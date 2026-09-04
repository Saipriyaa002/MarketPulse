"use client";

import React from "react";
import { AlertTriangle, Compass, Flame, Sparkles, CheckCircle } from "lucide-react";
import { PulseResponse } from "@/types";

interface PulseHeroProps {
  pulse: PulseResponse | null;
  isLoading: boolean;
  onOpenDigest?: () => void;
}

export const PulseHero: React.FC<PulseHeroProps> = ({ pulse, isLoading, onOpenDigest }) => {
  if (isLoading) {
    return (
      <div className="w-full rounded-2xl bg-slate-900/60 border border-slate-800 p-6 animate-pulse">
        <div className="h-4 w-40 bg-slate-800 rounded mb-3"></div>
        <div className="h-7 w-3/4 bg-slate-800 rounded mb-4"></div>
        <div className="flex gap-4">
          <div className="h-10 w-28 bg-slate-800 rounded-lg"></div>
          <div className="h-10 w-28 bg-slate-800 rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (!pulse) return null;

  return (
    <div className="w-full rounded-2xl bg-gradient-to-b from-[#162031] to-[#101724] border border-slate-700/60 p-6 shadow-xl relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Top Tagline & Digest Button */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
            <Sparkles className="h-3.5 w-3.5" />
            Intelligence Briefing
          </span>
          <span className="text-xs text-slate-400">
            Since you last checked ({pulse.human_elapsed})
          </span>
        </div>

        {onOpenDigest && (
          <button
            onClick={onOpenDigest}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/30 text-indigo-300 text-xs font-semibold transition"
          >
            <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
            <span>What Did I Miss?</span>
          </button>
        )}
      </div>

      {/* Main Executive Summary Statement */}
      <h2 className="text-lg md:text-xl font-semibold text-slate-100 tracking-tight leading-relaxed max-w-4xl mb-5">
        {pulse.executive_summary}
      </h2>

      {/* Metric Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-slate-800/80">
        <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium">Watchlist Stocks</span>
          <p className="text-xl font-bold text-white mt-0.5">{pulse.total_items}</p>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
            <Compass className="h-3 w-3 text-cyan-400" /> Meaningful Shifts
          </span>
          <p className="text-xl font-bold text-cyan-400 mt-0.5">
            {pulse.meaningful_count} <span className="text-xs font-normal text-slate-400">detected</span>
          </p>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
            <Flame className="h-3 w-3 text-rose-400" /> Critical Attention
          </span>
          <p className={`text-xl font-bold mt-0.5 ${pulse.critical_count > 0 ? "text-rose-400" : "text-slate-400"}`}>
            {pulse.critical_count} <span className="text-xs font-normal text-slate-400">stocks</span>
          </p>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
            <CheckCircle className="h-3 w-3 text-emerald-400" /> Fact Certainty
          </span>
          <p className="text-xl font-bold text-emerald-400 mt-0.5">
            98% <span className="text-xs font-normal text-slate-400">grounded</span>
          </p>
        </div>
      </div>
    </div>
  );
};
