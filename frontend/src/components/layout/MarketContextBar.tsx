"use client";

import React from "react";
import { TrendingUp, TrendingDown, Layers } from "lucide-react";
import { MarketContext } from "@/types";
import { formatPercent } from "@/lib/utils";

interface MarketContextBarProps {
  context: MarketContext | null;
}

export const MarketContextBar: React.FC<MarketContextBarProps> = ({ context }) => {
  if (!context) return null;

  return (
    <div className="w-full bg-[#131924] border-b border-slate-800/80 px-4 lg:px-8 py-2 overflow-x-auto text-xs scrollbar-none">
      <div className="max-w-7xl mx-auto flex items-center gap-6 min-w-max">
        {/* Benchmark Pill */}
        <div className="flex items-center gap-2 pr-4 border-r border-slate-700/60">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-semibold text-white">{context.benchmark_name}:</span>
          <span className="font-mono font-medium text-slate-200">
            {context.benchmark_price.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
          </span>
          <span
            className={`font-mono font-medium flex items-center gap-0.5 ${
              context.benchmark_change_pct >= 0 ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {context.benchmark_change_pct >= 0 ? (
              <TrendingUp className="h-3 w-3" />
            ) : (
              <TrendingDown className="h-3 w-3" />
            )}
            {formatPercent(context.benchmark_change_pct)}
          </span>
        </div>

        {/* Sectors Horizontal Feed */}
        <div className="flex items-center gap-4 text-slate-300">
          <span className="text-slate-500 font-medium flex items-center gap-1">
            <Layers className="h-3 w-3" /> Sectors:
          </span>
          {Object.entries(context.sectors).map(([sector, change]) => (
            <div key={sector} className="flex items-center gap-1.5">
              <span className="text-slate-400">{sector}</span>
              <span
                className={`font-mono font-medium ${
                  change >= 0 ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {formatPercent(change)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
