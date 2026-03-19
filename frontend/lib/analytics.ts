const MAX_QUEUE_SIZE = 50;
const FLUSH_INTERVAL_MS = 3000;

type AnalyticsEvent = {
  event_type: string;
  session_id: string;
  referrer: string | null;
  article_id?: string;
  category_slug?: string;
  source_slug?: string;
  surface?: string;
};

let queue: AnalyticsEvent[] = [];
let flushTimer: ReturnType<typeof setInterval> | null = null;
let listenersAttached = false;

function getSessionId(): string {
  if (typeof window === "undefined") return "";
  const COOKIE_NAME = "headlines_sid";
  const MAX_AGE = 1800; // 30 minutes
  const match = document.cookie.match(new RegExp(`(?:^|; )${COOKIE_NAME}=([^;]*)`));
  const sid = match ? decodeURIComponent(match[1]) : crypto.randomUUID();
  // Set/refresh cookie with rolling expiry
  document.cookie = `${COOKIE_NAME}=${sid}; max-age=${MAX_AGE}; path=/; SameSite=Strict`;
  return sid;
}

function getBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "";
}

function ensureFlushTimer() {
  if (flushTimer !== null) return;
  flushTimer = setInterval(() => flush(false), FLUSH_INTERVAL_MS);
}

function ensureUnloadListeners() {
  if (listenersAttached || typeof window === "undefined") return;
  listenersAttached = true;

  const onUnload = () => flush(true);

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") onUnload();
  });
  window.addEventListener("pagehide", onUnload);
}

async function flush(useBeacon: boolean) {
  if (queue.length === 0) return;

  const events = queue.splice(0);
  const url = `${getBaseUrl()}/api/events`;

  if (useBeacon) {
    for (const event of events) {
      const sent = navigator.sendBeacon(
        url,
        new Blob([JSON.stringify(event)], { type: "application/json" }),
      );
      // If sendBeacon fails, accept the loss — page is unloading
      if (!sent) break;
    }
    return;
  }

  const results = await Promise.allSettled(
    events.map((event) =>
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(event),
      }),
    ),
  );

  // Re-queue failed events (capped at MAX_QUEUE_SIZE)
  const failed: AnalyticsEvent[] = [];
  results.forEach((result, i) => {
    if (result.status === "rejected") {
      failed.push(events[i]);
    }
  });

  if (failed.length > 0) {
    queue.push(...failed);
    if (queue.length > MAX_QUEUE_SIZE) {
      queue.splice(0, queue.length - MAX_QUEUE_SIZE);
    }
  }

  // Stop timer if queue is empty and no more events expected
  if (queue.length === 0 && flushTimer !== null) {
    clearInterval(flushTimer);
    flushTimer = null;
  }
}

export async function trackEvent(
  eventType: string,
  data?: { article_id?: string; category_slug?: string; source_slug?: string; surface?: string },
) {
  if (typeof window === "undefined") return;

  const event: AnalyticsEvent = {
    event_type: eventType,
    session_id: getSessionId(),
    referrer: document.referrer || null,
    ...data,
  };

  queue.push(event);
  if (queue.length > MAX_QUEUE_SIZE) {
    queue.splice(0, queue.length - MAX_QUEUE_SIZE);
  }

  ensureFlushTimer();
  ensureUnloadListeners();
}
