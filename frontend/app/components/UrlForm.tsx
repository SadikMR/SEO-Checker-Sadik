"use client";

import { useState, type FormEvent } from "react";

interface UrlFormProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

function isValidUrl(value: string): boolean {
  try {
    const u = new URL(value);
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
}

export default function UrlForm({ onSubmit, isLoading }: UrlFormProps) {
  const [url, setUrl] = useState("");
  const [touched, setTouched] = useState(false);

  const valid = isValidUrl(url);
  const showError = touched && url.length > 0 && !valid;

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!valid) return;
    onSubmit(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full" noValidate>
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          {/* Globe icon */}
          <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
              className="h-5 w-5"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
          </span>

          <input
            id="url-input"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onBlur={() => setTouched(true)}
            placeholder="https://example.com"
            autoComplete="url"
            disabled={isLoading}
            aria-label="Website URL to audit"
            aria-invalid={showError}
            aria-describedby={showError ? "url-error" : undefined}
            className={[
              "h-14 w-full rounded-xl border bg-white pl-11 pr-4 text-base shadow-sm transition-all",
              "placeholder:text-slate-400 focus:outline-none focus:ring-2",
              showError
                ? "border-red-400 focus:ring-red-300"
                : "border-slate-200 focus:border-indigo-400 focus:ring-indigo-200",
              isLoading ? "cursor-not-allowed opacity-60" : "",
            ]
              .filter(Boolean)
              .join(" ")}
          />
        </div>

        <button
          id="audit-submit-btn"
          type="submit"
          disabled={isLoading}
          className={[
            "inline-flex h-14 items-center justify-center gap-2 rounded-xl px-7 text-base font-semibold",
            "bg-indigo-600 text-white shadow-sm transition-all hover:bg-indigo-500",
            "focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-60",
          ].join(" ")}
        >
          {isLoading ? (
            <>
              <svg
                className="h-4 w-4 animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8H4z"
                />
              </svg>
              Analysing…
            </>
          ) : (
            "Analyse"
          )}
        </button>
      </div>

      {showError && (
        <p id="url-error" role="alert" className="mt-2 text-sm text-red-600">
          Please enter a valid URL starting with http:// or https://
        </p>
      )}
    </form>
  );
}
