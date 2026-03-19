"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/admin-api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export default function AdminLoginPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      if (!res.ok) {
        setError("Invalid password");
        return;
      }

      const data = await res.json();
      setToken(data.token);
      router.push("/admin");
    } catch {
      setError("Connection error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm p-8 rounded-lg border border-rule bg-surface-alt"
      >
        <h1 className="text-xl font-semibold text-primary mb-6">
          Headlines Admin
        </h1>
        <label className="block text-sm text-secondary mb-2">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 rounded border border-rule bg-surface text-primary text-sm focus:outline-none focus:border-accent"
          autoFocus
        />
        {error && <p className="text-status-error text-sm mt-2">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-4 px-4 py-2 rounded bg-accent text-white text-sm font-medium hover:bg-accent-hover disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </div>
  );
}
