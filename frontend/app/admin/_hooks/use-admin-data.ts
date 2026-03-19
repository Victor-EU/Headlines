"use client";

import { useEffect, useRef, useState, useCallback } from "react";

export function useAdminData<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
): { data: T | null; loading: boolean; reload: () => Promise<void> } {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const counterRef = useRef(0);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const load = useCallback(async (showLoading: boolean) => {
    const id = ++counterRef.current;
    if (showLoading) setLoading(true);
    try {
      const result = await fetcherRef.current();
      if (id === counterRef.current) {
        setData(result);
        setLoading(false);
      }
    } catch {
      if (id === counterRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    load(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  const reload = useCallback(() => load(false), [load]);

  return { data, loading, reload };
}
