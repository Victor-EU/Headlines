import { revalidatePath } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Validate admin token by forwarding to backend
  const baseUrl =
    process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL;
  if (!baseUrl) {
    return NextResponse.json({ error: "API not configured" }, { status: 500 });
  }
  try {
    const check = await fetch(`${baseUrl}/api/admin/categories`, {
      headers: { Authorization: authHeader },
    });
    if (check.status === 401 || check.status === 403) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
  } catch {
    return NextResponse.json(
      { error: "Backend unreachable" },
      { status: 502 },
    );
  }

  revalidatePath("/", "layout");
  return NextResponse.json({ revalidated: true });
}
