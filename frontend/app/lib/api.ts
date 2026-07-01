/**
 * Audit API client.
 * Sends POST /audit to the backend and returns the typed response.
 */

import type { AuditResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class AuditApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(detail);
    this.name = "AuditApiError";
  }
}

export async function runAudit(url: string): Promise<AuditResponse> {
  const res = await fetch(`${API_BASE}/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore parse error
    }
    throw new AuditApiError(res.status, detail);
  }

  return res.json() as Promise<AuditResponse>;
}
