"use client";

import React from "react";
import { Flame, AlertCircle, CheckCircle2 } from "lucide-react";

interface AttentionBadgeProps {
  score: number;
  level: "CRITICAL" | "ELEVATED" | "ROUTINE";
}

export const AttentionBadge: React.FC<AttentionBadgeProps> = ({ score, level }) => {
  if (level === "CRITICAL") {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-300">
        <Flame className="h-3.5 w-3.5 text-rose-400 fill-rose-400/30" />
        <span className="text-xs font-bold">{score}</span>
        <span className="text-[10px] uppercase font-semibold tracking-wider text-rose-400">Critical</span>
      </div>
    );
  }

  if (level === "ELEVATED") {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300">
        <AlertCircle className="h-3.5 w-3.5 text-amber-400" />
        <span className="text-xs font-bold">{score}</span>
        <span className="text-[10px] uppercase font-semibold tracking-wider text-amber-400">Elevated</span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-400">
      <CheckCircle2 className="h-3.5 w-3.5 text-slate-500" />
      <span className="text-xs font-semibold text-slate-300">{score}</span>
      <span className="text-[10px] uppercase font-medium tracking-wider text-slate-400">Routine</span>
    </div>
  );
};
