"use client";

import { useEffect, useState } from "react";

type HealthStatus = "loading" | "connected" | "offline";

export default function Home() {
  const [status, setStatus] = useState<HealthStatus>("loading");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("http://localhost:8000/health");
        if (res.ok) {
          const data = await res.json();
          setStatus(data.status === "ok" ? "connected" : "offline");
        } else {
          setStatus("offline");
        }
      } catch {
        setStatus("offline");
      }
    };

    checkHealth();
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center px-6 py-16">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
          SEO Checker
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-600">
          Frontend scaffold initialized. Connect to the backend audit API to
          begin implementation.
        </p>

        {/* System Status Card */}
        <div className="mt-10 w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
            System Status
          </h2>

          <div className="mt-4 flex items-center gap-3">
            {status === "loading" && (
              <>
                <span className="relative flex h-3 w-3">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-slate-400 opacity-75" />
                  <span className="relative inline-flex h-3 w-3 rounded-full bg-slate-400" />
                </span>
                <span className="text-base font-medium text-slate-500">
                  Checking…
                </span>
              </>
            )}

            {status === "connected" && (
              <>
                <span className="relative flex h-3 w-3">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-500" />
                </span>
                <span className="text-base font-medium text-emerald-600">
                  Connected
                </span>
              </>
            )}

            {status === "offline" && (
              <>
                <span className="relative flex h-3 w-3">
                  <span className="relative inline-flex h-3 w-3 rounded-full bg-red-500" />
                </span>
                <span className="text-base font-medium text-red-600">
                  Offline / Error
                </span>
              </>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
