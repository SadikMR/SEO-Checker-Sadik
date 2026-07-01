"use client";

import { useState } from "react";
import type {
  AuditResponse,
  AuditIssue,
  AuditRecommendation,
  CategoryScore,
  RawSEOData,
} from "../lib/types";

// ─── Design tokens ────────────────────────────────────────────────────────────

const SCORE_GRADE = (s: number) =>
  s >= 90 ? "A" : s >= 80 ? "B" : s >= 65 ? "C" : s >= 50 ? "D" : "F";

const SCORE_COLOR = (s: number) =>
  s >= 80 ? "#10b981" : s >= 60 ? "#f59e0b" : s >= 40 ? "#f97316" : "#ef4444";

const SCORE_BG = (s: number) =>
  s >= 80
    ? "from-emerald-500 to-teal-400"
    : s >= 60
      ? "from-amber-500 to-yellow-400"
      : s >= 40
        ? "from-orange-500 to-amber-400"
        : "from-red-500 to-rose-400";

const SEV_CONFIG: Record<
  AuditIssue["severity"],
  { label: string; dot: string; row: string; badge: string; icon: string }
> = {
  critical: {
    label: "Critical",
    dot: "bg-red-500",
    row: "border-l-4 border-l-red-400 bg-red-50",
    badge: "bg-red-100 text-red-700 ring-1 ring-red-200",
    icon: "⛔",
  },
  warning: {
    label: "Warning",
    dot: "bg-amber-500",
    row: "border-l-4 border-l-amber-400 bg-amber-50",
    badge: "bg-amber-100 text-amber-700 ring-1 ring-amber-200",
    icon: "⚠️",
  },
  info: {
    label: "Info",
    dot: "bg-blue-400",
    row: "border-l-4 border-l-blue-300 bg-blue-50",
    badge: "bg-blue-100 text-blue-700 ring-1 ring-blue-200",
    icon: "ℹ️",
  },
  pass: {
    label: "Pass",
    dot: "bg-emerald-500",
    row: "border-l-4 border-l-emerald-400 bg-emerald-50",
    badge: "bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200",
    icon: "✅",
  },
};

const CATEGORY_ICONS: Record<string, string> = {
  meta: "🏷️",
  headings: "📝",
  images: "🖼️",
  links: "🔗",
  social: "📣",
  robots: "🤖",
  structured_data: "🔧",
};

// ─── Sub-components ───────────────────────────────────────────────────────────

function ScoreRing({
  score,
  size = 140,
  strokeWidth = 12,
}: {
  score: number;
  size?: number;
  strokeWidth?: number;
}) {
  const r = (size - strokeWidth) / 2;
  const circ = 2 * Math.PI * r;
  const progress = (score / 100) * circ;
  const color = SCORE_COLOR(score);
  const grade = SCORE_GRADE(score);

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg
        width={size}
        height={size}
        className="-rotate-90"
        aria-hidden="true"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.15)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="white"
          strokeWidth={strokeWidth}
          strokeDasharray={`${progress} ${circ - progress}`}
          strokeLinecap="round"
          className="transition-all duration-1000"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-4xl font-black text-white leading-none">
          {score}
        </span>
        <span
          className="mt-0.5 text-xs font-bold uppercase tracking-widest"
          style={{ color: "rgba(255,255,255,0.7)" }}
        >
          Grade {grade}
        </span>
      </div>
    </div>
  );
}

function MiniDonut({ score }: { score: number }) {
  const r = 18;
  const circ = 2 * Math.PI * r;
  const progress = (score / 100) * circ;
  const color = SCORE_COLOR(score);
  return (
    <svg width="44" height="44" className="-rotate-90" aria-hidden="true">
      <circle cx="22" cy="22" r={r} fill="none" stroke="#f1f5f9" strokeWidth="5" />
      <circle
        cx="22"
        cy="22"
        r={r}
        fill="none"
        stroke={color}
        strokeWidth="5"
        strokeDasharray={`${progress} ${circ - progress}`}
        strokeLinecap="round"
        className="transition-all duration-700"
      />
    </svg>
  );
}

function CategoryCard({ cat }: { cat: CategoryScore }) {
  const color = SCORE_COLOR(cat.score);
  const icon = CATEGORY_ICONS[cat.category] ?? "📊";
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="relative shrink-0">
        <MiniDonut score={cat.score} />
        <span className="absolute inset-0 flex items-center justify-center text-base rotate-90">
          {icon}
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium text-slate-500 truncate">{cat.label}</p>
        <p className="text-xl font-bold leading-tight" style={{ color }}>
          {cat.score}
          <span className="text-xs font-normal text-slate-400">/100</span>
        </p>
      </div>
    </div>
  );
}

function IssueRow({ issue }: { issue: AuditIssue }) {
  const cfg = SEV_CONFIG[issue.severity];
  return (
    <li className={`flex items-start gap-3 rounded-xl p-3.5 text-sm ${cfg.row}`}>
      <span
        className={`mt-0.5 shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${cfg.badge}`}
      >
        {cfg.label}
      </span>
      <div className="min-w-0">
        <p className="text-slate-700">{issue.message}</p>
        {issue.value && (
          <p className="mt-1 truncate font-mono text-xs text-slate-400">
            {issue.value}
          </p>
        )}
      </div>
    </li>
  );
}

function RecommendationRow({
  rec,
  index,
}: {
  rec: AuditRecommendation;
  index: number;
}) {
  const priorityColor =
    rec.severity === "critical"
      ? "bg-red-500"
      : rec.severity === "warning"
        ? "bg-amber-500"
        : "bg-blue-400";

  return (
    <li className="flex items-start gap-4 rounded-xl border border-slate-100 bg-white p-4 shadow-sm">
      <span
        className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${priorityColor}`}
      >
        {index + 1}
      </span>
      <p className="text-sm text-slate-700 leading-relaxed">{rec.message}</p>
    </li>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
        active
          ? "bg-indigo-600 text-white shadow-sm"
          : "text-slate-500 hover:text-slate-800 hover:bg-slate-100"
      }`}
    >
      {children}
    </button>
  );
}

function DataLabel({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
      {children}
    </span>
  );
}

function DataValue({ children }: { children: React.ReactNode }) {
  if (children === null || children === undefined || children === "") {
    return <span className="text-sm italic text-slate-300">Not set</span>;
  }
  return <span className="text-sm text-slate-800 break-all">{children}</span>;
}

function DataRow({
  label,
  value,
  status,
}: {
  label: string;
  value: React.ReactNode;
  status?: "ok" | "warn" | "error";
}) {
  const dot =
    status === "ok"
      ? "bg-emerald-400"
      : status === "warn"
        ? "bg-amber-400"
        : status === "error"
          ? "bg-red-400"
          : "bg-transparent";
  return (
    <div className="grid grid-cols-[auto_1fr] items-start gap-x-4 gap-y-0.5 border-b border-slate-50 py-2.5 last:border-0">
      <div className="flex items-center gap-2 pt-0.5">
        {status && (
          <span className={`mt-1 h-1.5 w-1.5 shrink-0 rounded-full ${dot}`} />
        )}
        <DataLabel>{label}</DataLabel>
      </div>
      <DataValue>{value}</DataValue>
    </div>
  );
}

function StatusPill({
  ok,
  okLabel,
  failLabel,
}: {
  ok: boolean;
  okLabel: string;
  failLabel: string;
}) {
  return ok ? (
    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-200">
      ✓ {okLabel}
    </span>
  ) : (
    <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700 ring-1 ring-red-200">
      ✗ {failLabel}
    </span>
  );
}

// ─── Raw Data Tabs ─────────────────────────────────────────────────────────────

type TabKey =
  | "meta"
  | "headings"
  | "social"
  | "images"
  | "links"
  | "robots"
  | "structured";

const TABS: { key: TabKey; label: string }[] = [
  { key: "meta", label: "Meta" },
  { key: "headings", label: "Headings" },
  { key: "social", label: "Social" },
  { key: "images", label: "Images" },
  { key: "links", label: "Links" },
  { key: "robots", label: "Robots" },
  { key: "structured", label: "Schema" },
];

function RawDataPanel({ rd }: { rd: RawSEOData }) {
  const [tab, setTab] = useState<TabKey>("meta");

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      {/* Tab bar */}
      <div className="flex items-center gap-1 border-b border-slate-100 bg-slate-50 px-4 py-2 overflow-x-auto">
        {TABS.map((t) => (
          <TabButton key={t.key} active={tab === t.key} onClick={() => setTab(t.key)}>
            {t.label}
          </TabButton>
        ))}
      </div>

      {/* Panel content */}
      <div className="p-5">
        {tab === "meta" && (
          <div>
            <DataRow
              label="Title"
              value={rd.meta.title}
              status={rd.meta.title ? (rd.meta.title_length! >= 30 && rd.meta.title_length! <= 60 ? "ok" : "warn") : "error"}
            />
            <DataRow
              label="Title Length"
              value={rd.meta.title_length != null ? `${rd.meta.title_length} characters` : null}
            />
            <DataRow
              label="Meta Description"
              value={rd.meta.description}
              status={rd.meta.description ? (rd.meta.description_length! >= 120 && rd.meta.description_length! <= 160 ? "ok" : "warn") : "error"}
            />
            <DataRow
              label="Description Length"
              value={rd.meta.description_length != null ? `${rd.meta.description_length} characters` : null}
            />
            <DataRow
              label="Canonical URL"
              value={rd.meta.canonical}
              status={rd.meta.canonical ? "ok" : "warn"}
            />
          </div>
        )}

        {tab === "headings" && (
          <div>
            {[1, 2, 3, 4, 5, 6].map((n) => {
              const val = rd.headings[`h${n}` as keyof typeof rd.headings] as string[];
              if (!val?.length) return null;
              return (
                <div key={n} className="mb-3">
                  <DataLabel>H{n} ({val.length})</DataLabel>
                  <ul className="mt-1 space-y-1">
                    {val.map((h, i) => (
                      <li key={i} className="rounded-lg bg-slate-50 px-3 py-1.5 text-sm text-slate-700">
                        {h}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
            {!rd.headings.h1_count && (
              <p className="text-sm italic text-slate-400">No headings found on this page.</p>
            )}
          </div>
        )}

        {tab === "social" && (
          <div className="space-y-5">
            <div>
              <p className="mb-2 text-sm font-semibold text-slate-500">Open Graph</p>
              <DataRow label="og:title" value={rd.open_graph.og_title} status={rd.open_graph.og_title ? "ok" : "error"} />
              <DataRow label="og:description" value={rd.open_graph.og_description} status={rd.open_graph.og_description ? "ok" : "error"} />
              <DataRow label="og:image" value={rd.open_graph.og_image} status={rd.open_graph.og_image ? "ok" : "warn"} />
              <DataRow label="og:url" value={rd.open_graph.og_url} />
              <DataRow label="og:type" value={rd.open_graph.og_type} />
              <DataRow label="og:site_name" value={rd.open_graph.og_site_name} />
            </div>
            <hr className="border-slate-100" />
            <div>
              <p className="mb-2 text-sm font-semibold text-slate-500">Twitter Card</p>
              <DataRow label="twitter:card" value={rd.twitter_card.card} status={rd.twitter_card.card ? "ok" : "error"} />
              <DataRow label="twitter:title" value={rd.twitter_card.title} status={rd.twitter_card.title ? "ok" : "warn"} />
              <DataRow label="twitter:description" value={rd.twitter_card.description} />
              <DataRow label="twitter:image" value={rd.twitter_card.image} />
              <DataRow label="twitter:site" value={rd.twitter_card.site} />
            </div>
          </div>
        )}

        {tab === "images" && (
          <div>
            {/* Visual stat row */}
            <div className="mb-4 grid grid-cols-3 gap-3">
              {[
                { label: "Total", count: rd.images.total_images, color: "text-slate-700 bg-slate-50" },
                { label: "With Alt", count: rd.images.images_with_alt, color: "text-emerald-700 bg-emerald-50" },
                { label: "Missing Alt", count: rd.images.images_without_alt, color: "text-red-700 bg-red-50" },
              ].map(({ label, count, color }) => (
                <div key={label} className={`rounded-xl p-3 text-center ${color}`}>
                  <p className="text-2xl font-bold">{count}</p>
                  <p className="text-xs font-medium opacity-70">{label}</p>
                </div>
              ))}
            </div>
            {rd.images.total_images > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Alt Coverage
                </p>
                <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-emerald-500 transition-all duration-700"
                    style={{
                      width: `${(rd.images.images_with_alt / rd.images.total_images) * 100}%`,
                    }}
                  />
                </div>
                <p className="mt-1 text-right text-xs text-slate-400">
                  {rd.images.total_images > 0
                    ? `${Math.round((rd.images.images_with_alt / rd.images.total_images) * 100)}% coverage`
                    : "–"}
                </p>
              </div>
            )}
          </div>
        )}

        {tab === "links" && (
          <div>
            {/* Visual stat row */}
            <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                { label: "Total", count: rd.links.total_links, color: "text-slate-700 bg-slate-50" },
                { label: "Internal", count: rd.links.internal_links, color: "text-indigo-700 bg-indigo-50" },
                { label: "External", count: rd.links.external_links, color: "text-sky-700 bg-sky-50" },
                { label: "Nofollow", count: rd.links.nofollow_links, color: "text-amber-700 bg-amber-50" },
              ].map(({ label, count, color }) => (
                <div key={label} className={`rounded-xl p-3 text-center ${color}`}>
                  <p className="text-2xl font-bold">{count}</p>
                  <p className="text-xs font-medium opacity-70">{label}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === "robots" && (
          <div>
            <DataRow
              label="meta robots"
              value={rd.robots.meta_robots ?? "Not set (defaults to index, follow)"}
              status={!rd.robots.meta_robots ? "ok" : rd.robots.meta_robots.includes("noindex") ? "error" : "ok"}
            />
            <DataRow
              label="X-Robots-Tag"
              value={rd.robots.x_robots_tag}
            />
            <DataRow
              label="robots.txt"
              value={
                <StatusPill
                  ok={!rd.robots.robots_txt_disallowed}
                  okLabel="Googlebot allowed"
                  failLabel="Googlebot blocked"
                />
              }
              status={rd.robots.robots_txt_disallowed ? "error" : "ok"}
            />
          </div>
        )}

        {tab === "structured" && (
          <div>
            <div className="mb-4 grid grid-cols-2 gap-3">
              <div className={`rounded-xl p-3 text-center ${rd.structured_data.has_json_ld ? "bg-emerald-50 text-emerald-700" : "bg-slate-50 text-slate-400"}`}>
                <p className="text-lg font-bold">JSON-LD</p>
                <p className="text-xs font-medium">
                  {rd.structured_data.has_json_ld ? "✓ Present" : "Not found"}
                </p>
              </div>
              <div className={`rounded-xl p-3 text-center ${rd.structured_data.has_microdata ? "bg-emerald-50 text-emerald-700" : "bg-slate-50 text-slate-400"}`}>
                <p className="text-lg font-bold">Microdata</p>
                <p className="text-xs font-medium">
                  {rd.structured_data.has_microdata ? "✓ Present" : "Not found"}
                </p>
              </div>
            </div>
            {rd.structured_data.json_ld_types.length > 0 && (
              <div className="mb-3">
                <DataLabel>JSON-LD Types</DataLabel>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {rd.structured_data.json_ld_types.map((t) => (
                    <span key={t} className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {rd.structured_data.microdata_types.length > 0 && (
              <div>
                <DataLabel>Microdata Types</DataLabel>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {rd.structured_data.microdata_types.map((t) => (
                    <span key={t} className="rounded-full bg-purple-50 px-2.5 py-0.5 text-xs font-medium text-purple-700">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {!rd.structured_data.has_json_ld && !rd.structured_data.has_microdata && (
              <p className="text-sm italic text-slate-400">No structured data detected.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────

interface AuditDashboardProps {
  data: AuditResponse;
  onReset: () => void;
}

export default function AuditDashboard({ data, onReset }: AuditDashboardProps) {
  const issues = data.results.filter((r) => r.severity !== "pass");
  const criticalIssues = issues.filter((r) => r.severity === "critical");
  const warningIssues = issues.filter((r) => r.severity === "warning");
  const infoIssues = issues.filter((r) => r.severity === "info");

  const score = data.scores.overall_score;
  const scoreBg = SCORE_BG(score);

  return (
    <div className="w-full space-y-6 pb-12">

      {/* ── Hero score banner ── */}
      <div className={`relative overflow-hidden rounded-3xl bg-gradient-to-br ${scoreBg} p-8 text-white shadow-xl`}>
        {/* Background decoration */}
        <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-white/10" />
        <div className="pointer-events-none absolute -bottom-8 -left-8 h-40 w-40 rounded-full bg-white/5" />

        <div className="relative flex flex-col items-center gap-6 sm:flex-row sm:items-start">
          {/* Score ring */}
          <ScoreRing score={score} />

          {/* Info block */}
          <div className="flex-1 text-center sm:text-left">
            <h1 className="text-2xl font-bold tracking-tight">SEO Audit Report</h1>
            <a
              href={data.final_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 block truncate text-sm font-medium opacity-80 hover:opacity-100 hover:underline"
            >
              {data.final_url}
            </a>

            {data.redirects.length > 0 && (
              <p className="mt-1 text-xs opacity-60">
                {data.redirects.length} redirect{data.redirects.length > 1 ? "s" : ""} followed
              </p>
            )}

            {/* Quick stats */}
            <div className="mt-4 flex flex-wrap justify-center gap-3 sm:justify-start">
              {[
                { label: "Critical", count: criticalIssues.length, bg: "bg-white/20" },
                { label: "Warnings", count: warningIssues.length, bg: "bg-white/15" },
                { label: "Fixes", count: data.recommendations.length, bg: "bg-white/10" },
              ].map(({ label, count, bg }) => (
                <div key={label} className={`rounded-xl ${bg} px-4 py-2 text-center backdrop-blur-sm`}>
                  <p className="text-xl font-bold">{count}</p>
                  <p className="text-xs opacity-75">{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* New Audit button */}
          <button
            id="audit-reset-btn"
            onClick={onReset}
            className="shrink-0 rounded-xl bg-white/20 px-5 py-2.5 text-sm font-semibold text-white backdrop-blur-sm hover:bg-white/30 transition-all"
          >
            ← New Audit
          </button>
        </div>
      </div>

      {/* ── Category score cards ── */}
      <section aria-labelledby="categories-heading">
        <h2
          id="categories-heading"
          className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400"
        >
          Category Scores
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {data.scores.categories.map((cat) => (
            <CategoryCard key={cat.category} cat={cat} />
          ))}
        </div>
      </section>

      {/* ── Redirects ── */}
      {data.redirects.length > 0 && (
        <section>
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
            Redirect Chain
          </h2>
          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <ol className="space-y-2">
              {data.redirects.map((r, i) => (
                <li key={i} className="flex items-center gap-3 text-sm">
                  <span className="shrink-0 rounded-full bg-amber-200 px-2 py-0.5 text-xs font-bold text-amber-800">
                    {r.status}
                  </span>
                  <span className="truncate text-amber-800">{r.url}</span>
                </li>
              ))}
              <li className="flex items-center gap-3 text-sm">
                <span className="shrink-0 rounded-full bg-emerald-200 px-2 py-0.5 text-xs font-bold text-emerald-800">
                  200
                </span>
                <span className="truncate font-medium text-emerald-800">
                  {data.final_url}
                </span>
              </li>
            </ol>
          </div>
        </section>
      )}

      {/* ── Issues grouped by severity ── */}
      {issues.length > 0 && (
        <section aria-labelledby="issues-heading">
          <h2
            id="issues-heading"
            className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400"
          >
            Issues Found ({issues.length})
          </h2>
          <div className="space-y-3">
            {criticalIssues.length > 0 && (
              <ul className="space-y-2" aria-label="Critical issues">
                {criticalIssues.map((issue, i) => (
                  <IssueRow key={`crit-${i}`} issue={issue} />
                ))}
              </ul>
            )}
            {warningIssues.length > 0 && (
              <ul className="space-y-2" aria-label="Warnings">
                {warningIssues.map((issue, i) => (
                  <IssueRow key={`warn-${i}`} issue={issue} />
                ))}
              </ul>
            )}
            {infoIssues.length > 0 && (
              <ul className="space-y-2" aria-label="Info">
                {infoIssues.map((issue, i) => (
                  <IssueRow key={`info-${i}`} issue={issue} />
                ))}
              </ul>
            )}
          </div>
        </section>
      )}

      {/* ── Recommendations ── */}
      {data.recommendations.length > 0 && (
        <section aria-labelledby="recs-heading">
          <h2
            id="recs-heading"
            className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400"
          >
            Recommendations ({data.recommendations.length})
          </h2>
          <ul className="space-y-2" aria-label="Recommendations">
            {data.recommendations.map((rec, i) => (
              <RecommendationRow key={`${rec.rule_id}-${i}`} rec={rec} index={i} />
            ))}
          </ul>
        </section>
      )}

      {/* ── Extracted SEO Data ── */}
      <section aria-labelledby="data-heading">
        <h2
          id="data-heading"
          className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400"
        >
          Extracted SEO Data
        </h2>
        <RawDataPanel rd={data.raw_data} />
      </section>

    </div>
  );
}
