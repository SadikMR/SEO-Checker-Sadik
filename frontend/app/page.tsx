"use client";

import { useEffect, useState } from "react";
import { useAudit } from "./components/useAudit";
import UrlForm from "./components/UrlForm";
import AuditDashboard from "./components/AuditSummary";

type BackendStatus = "checking" | "online" | "offline";

function BackendBadge({ status }: { status: BackendStatus }) {
  if (status === "checking") return null;
  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${
        status === "online"
          ? "bg-emerald-50 text-emerald-700"
          : "bg-red-50 text-red-700"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          status === "online" ? "bg-emerald-500" : "bg-red-500"
        }`}
      />
      {status === "online" ? "API Online" : "API Offline"}
    </div>
  );
}

export default function Home() {
  const { state, submit, reset } = useAudit();
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("checking");

  useEffect(() => {
    const API_BASE =
      process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${API_BASE}/health`)
      .then((r) => setBackendStatus(r.ok ? "online" : "offline"))
      .catch(() => setBackendStatus("offline"));
  }, []);

  const isLoading = state.status === "loading";

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50">
      {/* Nav */}
      <nav className="border-b border-slate-100 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold tracking-tight text-slate-900">
              SEO<span className="text-indigo-600">Checker</span>
            </span>
          </div>
          <BackendBadge status={backendStatus} />
        </div>
      </nav>

      <div className={`mx-auto px-6 py-12 transition-all duration-300 ${state.status === "success" ? "max-w-5xl" : "max-w-3xl"}`}>
        {/* Hero — shown when idle or on error */}
        {(state.status === "idle" ||
          state.status === "loading" ||
          state.status === "error") && (
          <div className="mb-10 text-center">
            <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-600 shadow-lg shadow-indigo-200">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth={1.5}
                className="h-8 w-8"
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              SEO Audit Tool
            </h1>
            <p className="mt-4 text-lg text-slate-500">
              Enter any website URL to get a comprehensive, instant SEO report.
            </p>
          </div>
        )}

        {/* URL Form — always visible unless showing results */}
        {state.status !== "success" && (
          <div
            className={`rounded-2xl border border-slate-200 bg-white p-6 shadow-sm ${
              state.status === "loading" ? "opacity-90" : ""
            }`}
          >
            <UrlForm onSubmit={submit} isLoading={isLoading} />

            {/* Loading state */}
            {state.status === "loading" && (
              <div
                className="mt-5 flex flex-col items-center gap-3 rounded-xl bg-indigo-50 px-4 py-5 text-center"
                role="status"
                aria-live="polite"
              >
                <div className="flex gap-1.5">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="h-2 w-2 rounded-full bg-indigo-500"
                      style={{
                        animation: `bounce 1s ease-in-out ${i * 0.15}s infinite`,
                      }}
                    />
                  ))}
                </div>
                <p className="text-sm font-medium text-indigo-700">
                  Rendering page and running SEO checks…
                </p>
                <p className="text-xs text-indigo-400">
                  This usually takes 10–30 seconds
                </p>
              </div>
            )}

            {/* Error state */}
            {state.status === "error" && (
              <div
                className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-4"
                role="alert"
                aria-live="assertive"
              >
                <div className="flex items-start gap-3">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.5}
                    className="mt-0.5 h-5 w-5 shrink-0 text-red-500"
                    aria-hidden="true"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  <div>
                    <p className="font-medium text-red-700">Audit failed</p>
                    <p className="mt-0.5 text-sm text-red-600">
                      {state.message}
                    </p>
                    {state.httpStatus === 504 && (
                      <p className="mt-1 text-xs text-red-400">
                        The page took too long to load. Try again or check the URL.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Success — show audit summary */}
        {state.status === "success" && (
          <AuditDashboard data={state.data} onReset={reset} />
        )}

        {/* Features row — shown only on idle */}
        {state.status === "idle" && (
          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {[
              {
                icon: "⚡",
                title: "10 Audit Checks",
                desc: "Title, meta, headings, images, links, OG, Twitter, robots, canonical & structured data.",
              },
              {
                icon: "🎯",
                title: "Weighted Scoring",
                desc: "Overall SEO score with category-level breakdowns and configurable weights.",
              },
              {
                icon: "💡",
                title: "Actionable Fixes",
                desc: "Deterministic, rules-based recommendations for every detected issue.",
              },
            ].map(({ icon, title, desc }) => (
              <div
                key={title}
                className="rounded-xl border border-slate-100 bg-white p-5 shadow-sm"
              >
                <div className="mb-2 text-2xl">{icon}</div>
                <h3 className="font-semibold text-slate-800">{title}</h3>
                <p className="mt-1 text-sm text-slate-500">{desc}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <style jsx global>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
      `}</style>
    </main>
  );
}
