"use client";

import { useState } from "react";
import { runAudit, AuditApiError } from "../lib/api";
import type { AuditResponse } from "../lib/types";

export type AuditState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: AuditResponse }
  | { status: "error"; message: string; httpStatus?: number };

export function useAudit() {
  const [state, setState] = useState<AuditState>({ status: "idle" });

  const submit = async (url: string) => {
    setState({ status: "loading" });
    try {
      const data = await runAudit(url);
      setState({ status: "success", data });
    } catch (err) {
      if (err instanceof AuditApiError) {
        setState({
          status: "error",
          message: err.detail,
          httpStatus: err.status,
        });
      } else if (err instanceof Error) {
        setState({ status: "error", message: err.message });
      } else {
        setState({ status: "error", message: "An unexpected error occurred." });
      }
    }
  };

  const reset = () => setState({ status: "idle" });

  return { state, submit, reset };
}
