"use client";

import type { AuditResponse } from "../lib/types";

interface AuditSummaryProps {
  data: AuditResponse;
  onReset: () => void;
}

const SEVERITY_STYLES = {
  critical: "bg-red-50 border-red-200 text-red-700",
  warning: "bg-amber-50 border-amber-200 text-amber-700",
  info: "bg-blue-50 border-blue-200 text-blue-700",
  pass: "bg-emerald-50 border-emerald-200 text-emerald-700",
} as const;

const SEVERITY_BADGE = {
  critical: "bg-red-100 text-red-700",
  warning: "bg-amber-100 text-amber-700",
  info: "bg-blue-100 text-blue-700",
  pass: "bg-emerald-100 text-emerald-700",
} as const;

function ScoreRing({ score }: { score: number }) {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const progress = (score / 100) * circ;
  const color =
    score >= 80
      ? "#10b981"
      : score >= 60
        ? "#f59e0b"
        : score >= 40
          ? "#f97316"
          : "#ef4444";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="96" height="96" className="-rotate-90">
        <circle
          cx="48"
          cy="48"
          r={r}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="8"
        />
        <circle
          cx="48"
          cy="48"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={`${progress} ${circ - progress}`}
          strokeLinecap="round"
          className="transition-all duration-700"
        />
      </svg>
      <span
        className="absolute text-2xl font-bold"
        style={{ color }}
        aria-label={`Overall SEO score: ${score}`}
      >
        {score}
      </span>
    </div>
  );
}

export default function AuditSummary({ data, onReset }: AuditSummaryProps) {
  const issues = data.results.filter((r) => r.severity !== "pass");
  const criticalCount = issues.filter((r) => r.severity === "critical").length;
  const warningCount = issues.filter((r) => r.severity === "warning").length;

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">Audit complete for</p>
          <a
            href={data.final_url}
            target="_blank"
            rel="noopener noreferrer"
            className="truncate text-base font-medium text-indigo-600 hover:underline"
          >
            {data.final_url}
          </a>
        </div>
        <button
          id="audit-reset-btn"
          onClick={onReset}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm transition hover:bg-slate-50"
        >
          ← New Audit
        </button>
      </div>

      {/* Score + category grid */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col items-center gap-6 sm:flex-row">
          {/* Ring */}
          <div className="flex flex-col items-center gap-2">
            <ScoreRing score={data.scores.overall_score} />
            <p className="text-sm font-medium text-slate-500">Overall Score</p>
          </div>

          {/* Category bars */}
          <div className="flex-1 space-y-3 w-full">
            {data.scores.categories.map((cat) => {
              const pct = cat.score;
              const barColor =
                pct >= 80
                  ? "bg-emerald-500"
                  : pct >= 60
                    ? "bg-amber-400"
                    : pct >= 40
                      ? "bg-orange-400"
                      : "bg-red-500";
              return (
                <div key={cat.category}>
                  <div className="mb-1 flex justify-between text-sm">
                    <span className="font-medium text-slate-700">
                      {cat.label}
                    </span>
                    <span className="text-slate-500">{pct}/100</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-slate-100">
                    <div
                      className={`h-2 rounded-full transition-all duration-700 ${barColor}`}
                      style={{ width: `${pct}%` }}
                      role="progressbar"
                      aria-valuenow={pct}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={`${cat.label}: ${pct}/100`}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Issue counters */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-center">
          <p className="text-3xl font-bold text-red-600">{criticalCount}</p>
          <p className="mt-1 text-sm text-red-500">Critical</p>
        </div>
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-center">
          <p className="text-3xl font-bold text-amber-600">{warningCount}</p>
          <p className="mt-1 text-sm text-amber-500">Warnings</p>
        </div>
        <div className="col-span-2 rounded-xl border border-indigo-200 bg-indigo-50 p-4 text-center sm:col-span-1">
          <p className="text-3xl font-bold text-indigo-600">
            {data.recommendations.length}
          </p>
          <p className="mt-1 text-sm text-indigo-500">Recommendations</p>
        </div>
      </div>

      {/* Issues list */}
      {issues.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Issues Found
          </h2>
          <ul className="space-y-2" aria-label="Audit issues">
            {issues.map((issue, i) => (
              <li
                key={`${issue.rule_id}-${i}`}
                className={`flex items-start gap-3 rounded-xl border p-4 text-sm ${SEVERITY_STYLES[issue.severity]}`}
              >
                <span
                  className={`mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${SEVERITY_BADGE[issue.severity]}`}
                >
                  {issue.severity}
                </span>
                <span>{issue.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations list */}
      {data.recommendations.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Recommendations
          </h2>
          <ul className="space-y-2" aria-label="Recommendations">
            {data.recommendations.map((rec, i) => (
              <li
                key={`${rec.rule_id}-${i}`}
                className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-sm"
              >
                <span className="mt-0.5 text-indigo-500" aria-hidden="true">
                  →
                </span>
                {rec.message}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
