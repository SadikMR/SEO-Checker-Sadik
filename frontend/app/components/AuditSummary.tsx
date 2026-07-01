"use client";

import { useState } from "react";
import type {
  AuditResponse,
  AuditIssue,
  CategoryScore,
} from "../lib/types";

// ─── helpers ──────────────────────────────────────────────────────────────

const SEV_BADGE: Record<AuditIssue["severity"], string> = {
  critical: "bg-red-100 text-red-700 border border-red-200",
  warning: "bg-amber-100 text-amber-700 border border-amber-200",
  info: "bg-blue-100 text-blue-700 border border-blue-200",
  pass: "bg-emerald-100 text-emerald-700 border border-emerald-200",
};

const SEV_ROW: Record<AuditIssue["severity"], string> = {
  critical: "bg-red-50 border-red-100",
  warning: "bg-amber-50 border-amber-100",
  info: "bg-blue-50 border-blue-100",
  pass: "bg-emerald-50 border-emerald-100",
};

const BAR_COLOR = (score: number) =>
  score >= 80
    ? "bg-emerald-500"
    : score >= 60
      ? "bg-amber-400"
      : score >= 40
        ? "bg-orange-400"
        : "bg-red-500";

const SCORE_COLOR = (score: number) =>
  score >= 80
    ? "#10b981"
    : score >= 60
      ? "#f59e0b"
      : score >= 40
        ? "#f97316"
        : "#ef4444";

function ScoreRing({ score }: { score: number }) {
  const r = 44;
  const circ = 2 * Math.PI * r;
  const progress = (score / 100) * circ;
  const color = SCORE_COLOR(score);
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="112" height="112" className="-rotate-90" aria-hidden="true">
        <circle cx="56" cy="56" r={r} fill="none" stroke="#e2e8f0" strokeWidth="10" />
        <circle
          cx="56" cy="56" r={r} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={`${progress} ${circ - progress}`}
          strokeLinecap="round"
          className="transition-all duration-700"
        />
      </svg>
      <span className="absolute text-3xl font-bold" style={{ color }}>
        {score}
      </span>
    </div>
  );
}

function CategoryBar({ cat }: { cat: CategoryScore }) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm">
        <span className="font-medium text-slate-700">{cat.label}</span>
        <span className="font-semibold" style={{ color: SCORE_COLOR(cat.score) }}>
          {cat.score}/100
        </span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full transition-all duration-700 ${BAR_COLOR(cat.score)}`}
          style={{ width: `${cat.score}%` }}
          role="progressbar"
          aria-valuenow={cat.score}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
      {children}
    </h2>
  );
}

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-2xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>
      {children}
    </div>
  );
}

function DataRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5 py-2.5 border-b border-slate-50 last:border-0">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</span>
      <span className="text-sm text-slate-800 break-all">{value ?? <span className="text-slate-300 italic">—</span>}</span>
    </div>
  );
}

function CollapsibleSection({
  title,
  defaultOpen = false,
  children,
}: {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <button
        className="flex w-full items-center justify-between px-5 py-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        {title}
        <svg
          className={`h-4 w-4 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`}
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="m19 9-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="border-t border-slate-100 px-5 pb-5 pt-3">{children}</div>}
    </div>
  );
}

// ─── main component ────────────────────────────────────────────────────────

interface AuditDashboardProps {
  data: AuditResponse;
  onReset: () => void;
}

export default function AuditDashboard({ data, onReset }: AuditDashboardProps) {
  const issues = data.results.filter((r) => r.severity !== "pass");
  const criticalCount = issues.filter((r) => r.severity === "critical").length;
  const warningCount = issues.filter((r) => r.severity === "warning").length;
  const infoCount = issues.filter((r) => r.severity === "info").length;

  const rd = data.raw_data;

  return (
    <div className="w-full space-y-6">

      {/* ── Top bar ── */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs text-slate-400">Audit complete</p>
          <a
            href={data.final_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block truncate text-sm font-semibold text-indigo-600 hover:underline"
          >
            {data.final_url}
          </a>
          {data.redirects.length > 0 && (
            <p className="mt-0.5 text-xs text-slate-400">
              ↳ {data.redirects.length} redirect{data.redirects.length > 1 ? "s" : ""} followed
            </p>
          )}
        </div>
        <button
          id="audit-reset-btn"
          onClick={onReset}
          className="shrink-0 inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 transition"
        >
          ← New Audit
        </button>
      </div>

      {/* ── Overall score + categories ── */}
      <Card>
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
          <div className="flex flex-col items-center gap-1 shrink-0">
            <ScoreRing score={data.scores.overall_score} />
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Overall Score</p>
          </div>
          <div className="flex-1 w-full space-y-3">
            {data.scores.categories.map((c) => (
              <CategoryBar key={c.category} cat={c} />
            ))}
          </div>
        </div>
      </Card>

      {/* ── Issue counters ── */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Critical", count: criticalCount, cls: "border-red-200 bg-red-50 text-red-600" },
          { label: "Warnings", count: warningCount, cls: "border-amber-200 bg-amber-50 text-amber-600" },
          { label: "Info", count: infoCount, cls: "border-blue-200 bg-blue-50 text-blue-600" },
          { label: "Fixes", count: data.recommendations.length, cls: "border-indigo-200 bg-indigo-50 text-indigo-600" },
        ].map(({ label, count, cls }) => (
          <div key={label} className={`rounded-xl border p-4 text-center ${cls}`}>
            <p className="text-2xl font-bold">{count}</p>
            <p className="mt-0.5 text-xs font-medium opacity-80">{label}</p>
          </div>
        ))}
      </div>

      {/* ── Redirects (if any) ── */}
      {data.redirects.length > 0 && (
        <CollapsibleSection title={`Redirect Chain (${data.redirects.length})`}>
          <ol className="space-y-1.5">
            {data.redirects.map((r, i) => (
              <li key={i} className="flex items-center gap-3 text-sm text-slate-600">
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
                  {r.status}
                </span>
                <span className="truncate">{r.url}</span>
              </li>
            ))}
            <li className="flex items-center gap-3 text-sm text-slate-600 pt-1">
              <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700">
                Final
              </span>
              <span className="truncate font-medium">{data.final_url}</span>
            </li>
          </ol>
        </CollapsibleSection>
      )}

      {/* ── Issues ── */}
      {issues.length > 0 && (
        <CollapsibleSection title={`Issues Found (${issues.length})`} defaultOpen>
          <ul className="space-y-2" aria-label="Audit issues">
            {issues.map((issue, i) => (
              <li
                key={`${issue.rule_id}-${i}`}
                className={`flex items-start gap-3 rounded-xl border p-3.5 text-sm ${SEV_ROW[issue.severity]}`}
              >
                <span className={`mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${SEV_BADGE[issue.severity]}`}>
                  {issue.severity}
                </span>
                <div className="min-w-0">
                  <p>{issue.message}</p>
                  {issue.value && (
                    <p className="mt-1 truncate text-xs opacity-60 font-mono">{issue.value}</p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}

      {/* ── Recommendations ── */}
      {data.recommendations.length > 0 && (
        <CollapsibleSection title={`Recommendations (${data.recommendations.length})`} defaultOpen>
          <ul className="space-y-2" aria-label="Recommendations">
            {data.recommendations.map((rec, i) => (
              <li
                key={`${rec.rule_id}-${i}`}
                className="flex items-start gap-3 rounded-xl border border-slate-200 p-3.5 text-sm text-slate-700"
              >
                <span className="mt-0.5 shrink-0 text-indigo-500 font-bold" aria-hidden="true">→</span>
                {rec.message}
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}

      {/* ── Raw SEO Data ── */}
      <CollapsibleSection title="Extracted SEO Data">
        <div className="space-y-5">

          {/* Meta Tags */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Meta Tags</p>
            <DataRow label="Title" value={rd.meta.title} />
            <DataRow label="Title Length" value={rd.meta.title_length != null ? `${rd.meta.title_length} chars` : null} />
            <DataRow label="Meta Description" value={rd.meta.description} />
            <DataRow label="Description Length" value={rd.meta.description_length != null ? `${rd.meta.description_length} chars` : null} />
            <DataRow label="Canonical" value={rd.meta.canonical} />
          </div>

          {/* Headings */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Headings</p>
            {[1, 2, 3, 4, 5, 6].map((n) => {
              const val = rd.headings[`h${n}` as keyof typeof rd.headings] as string[];
              return val?.length ? (
                <DataRow key={n} label={`H${n} (${val.length})`} value={val.join(" · ")} />
              ) : null;
            })}
            {!rd.headings.h1_count && <p className="text-sm text-slate-400 italic">No headings found.</p>}
          </div>

          {/* Open Graph */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Open Graph</p>
            <DataRow label="og:title" value={rd.open_graph.og_title} />
            <DataRow label="og:description" value={rd.open_graph.og_description} />
            <DataRow label="og:image" value={rd.open_graph.og_image} />
            <DataRow label="og:url" value={rd.open_graph.og_url} />
            <DataRow label="og:type" value={rd.open_graph.og_type} />
            <DataRow label="og:site_name" value={rd.open_graph.og_site_name} />
          </div>

          {/* Twitter Card */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Twitter Card</p>
            <DataRow label="twitter:card" value={rd.twitter_card.card} />
            <DataRow label="twitter:title" value={rd.twitter_card.title} />
            <DataRow label="twitter:description" value={rd.twitter_card.description} />
            <DataRow label="twitter:image" value={rd.twitter_card.image} />
            <DataRow label="twitter:site" value={rd.twitter_card.site} />
          </div>

          {/* Images */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Images</p>
            <DataRow label="Total Images" value={rd.images.total_images} />
            <DataRow label="With Alt" value={rd.images.images_with_alt} />
            <DataRow label="Missing Alt" value={rd.images.images_without_alt} />
          </div>

          {/* Links */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Links</p>
            <DataRow label="Total Links" value={rd.links.total_links} />
            <DataRow label="Internal" value={rd.links.internal_links} />
            <DataRow label="External" value={rd.links.external_links} />
            <DataRow label="Nofollow" value={rd.links.nofollow_links} />
          </div>

          {/* Robots */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Robots</p>
            <DataRow label="meta robots" value={rd.robots.meta_robots} />
            <DataRow label="X-Robots-Tag" value={rd.robots.x_robots_tag} />
            <DataRow
              label="robots.txt"
              value={
                rd.robots.robots_txt_disallowed ? (
                  <span className="text-red-600 font-medium">Disallowed</span>
                ) : (
                  <span className="text-emerald-600 font-medium">Allowed</span>
                )
              }
            />
          </div>

          {/* Structured Data */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Structured Data</p>
            <DataRow label="JSON-LD" value={rd.structured_data.has_json_ld ? rd.structured_data.json_ld_types.join(", ") || "Present" : "Not found"} />
            <DataRow label="Microdata" value={rd.structured_data.has_microdata ? rd.structured_data.microdata_types.join(", ") || "Present" : "Not found"} />
          </div>

        </div>
      </CollapsibleSection>

    </div>
  );
}
