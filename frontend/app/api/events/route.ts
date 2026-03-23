import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.INTERNAL_API_URL || "http://api:8000";

export async function POST(request: NextRequest) {
  const body = await request.text();

  const res = await fetch(`${BACKEND_URL}/api/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });

  if (!res.ok) {
    return NextResponse.json(null, { status: res.status });
  }

  return new NextResponse(null, { status: 204 });
}
