"use client";

import React, { useState } from "react";
import { 
  ArrowUpDown, 
  ChevronRight, 
  TrendingUp, 
  TrendingDown, 
  Sparkles,
  Info
} from "lucide-react";
import { PulseItem } from "@/types";
import { formatINR, formatPercent, formatCompact } from "@/lib/utils";
import { AttentionBadge } from "./AttentionBadge";
import { MiniSparkline } from "../stock/MiniSparkline";

interface AttentionRankedTableProps {
  items: PulseItem[];
  onSelectItem: (item: PulseItem) => void;
  isLoading: boolean;
}

export const AttentionRankedTable: React.FC<AttentionRankedTableProps> = ({
  items,
  onSelectItem,
  isLoading,
}) => {
  const [filter, setFilter] = useState<"ALL" | "MEANINGFUL" | "CRITICAL">("ALL");

  const filteredItems = items.filter((item) => {
    if (filter === "CRITICAL") return item.attention_level === "CRITICAL";
    if (filter === "MEANINGFUL") return item.is_meaningful;
    return true;
  });

  return (
    <div className="w-full rounded-2xl bg-[#0f141f] border border-slate-800 shadow-xl overflow-hidden">
      {/* Table Controls & Filter Tabs */}
      <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-[#131924]/60">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-white text-sm">Watchlist Intelligence Feed</h3>
          <span className="text-xs text-slate-400">({filteredItems.length} stocks)</span>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <button
            onClick={() => setFilter("ALL")}
            className={`px-3 py-1 rounded-lg font-medium transition ${
              filter === "ALL" ? "bg-slate-700 text-white shadow" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            All Stocks
          </button>
          <button
            onClick={() => setFilter("MEANINGFUL")}
            className={`px-3 py-1 rounded-lg font-medium transition ${
              filter === "MEANINGFUL" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Meaningful Shifts
          </button>
          <button
            onClick={() => setFilter("CRITICAL")}
            className={`px-3 py-1 rounded-lg font-medium transition ${
              filter === "CRITICAL" ? "bg-rose-500/20 text-rose-300 border border-rose-500/30" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Critical Only
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#111722] text-slate-400 uppercase font-semibold text-[11px] tracking-wider border-b border-slate-800/80">
            <tr>
              <th className="py-3.5 px-4">Attention Level</th>
              <th className="py-3.5 px-4">Instrument</th>
              <th className="py-3.5 px-4 text-right">Price / Since Checkpoint</th>
              <th className="py-3.5 px-4 text-right">Market Alpha</th>
              <th className="py-3.5 px-4 text-right">Sector Div</th>
              <th className="py-3.5 px-4 text-right">Volume Z-Score</th>
              <th className="py-3.5 px-4 text-center">Trend</th>
              <th className="py-3.5 px-4">Key Driver</th>
              <th className="py-3.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredItems.map((item) => {
              const isPositive = item.price_change_pct >= 0;

              return (
                <tr
                  key={item.symbol}
                  onClick={() => onSelectItem(item)}
                  className="hover:bg-slate-800/40 cursor-pointer transition group"
                >
                  {/* Attention Badge */}
                  <td className="py-4 px-4 whitespace-nowrap">
                    <AttentionBadge score={item.attention_score} level={item.attention_level} />
                  </td>

                  {/* Symbol & Name */}
                  <td className="py-4 px-4 whitespace-nowrap">
                    <div className="font-bold text-sm text-white group-hover:text-emerald-400 transition">
                      {item.symbol}
                    </div>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                      <span>{item.name}</span>
                      <span>·</span>
                      <span className="text-slate-500">{item.sector}</span>
                    </div>
                  </td>

                  {/* Price & Delta */}
                  <td className="py-4 px-4 text-right whitespace-nowrap">
                    <div className="font-bold text-sm text-white font-mono">
                      {formatINR(item.current_price)}
                    </div>
                    {item.price_change_pct === 0.0 ? (
                      <div className="flex items-center justify-end gap-1 mt-0.5">
                        <span className="text-[10px] font-medium text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded border border-slate-700/50">
                          At Baseline
                        </span>
                      </div>
                    ) : (
                      <div
                        className={`text-xs font-semibold font-mono flex items-center justify-end gap-0.5 mt-0.5 ${
                          isPositive ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                        {formatPercent(item.price_change_pct)}
                      </div>
                    )}
                    {item.session_change_pct !== undefined && item.price_change_pct !== item.session_change_pct && (
                      <span className="text-[10px] text-slate-500 font-mono block mt-0.5">
                        Day: {formatPercent(item.session_change_pct)}
                      </span>
                    )}
                  </td>

                  {/* Market Alpha */}
                  <td className="py-4 px-4 text-right whitespace-nowrap font-mono">
                    <span
                      className={`font-semibold ${
                        item.alpha_excess_pct > 0.05 ? "text-emerald-400" :
                        item.alpha_excess_pct < -0.05 ? "text-rose-400" : "text-slate-400"
                      }`}
                    >
                      {formatPercent(item.alpha_excess_pct)}
                    </span>
                    <span className="text-[10px] text-slate-500 block">vs Nifty</span>
                  </td>

                  {/* Sector Divergence */}
                  <td className="py-4 px-4 text-right whitespace-nowrap font-mono">
                    <span
                      className={`font-semibold ${
                        item.sector_divergence_pct > 0.05 ? "text-emerald-400" :
                        item.sector_divergence_pct < -0.05 ? "text-rose-400" : "text-slate-400"
                      }`}
                    >
                      {formatPercent(item.sector_divergence_pct)}
                    </span>
                    <span className="text-[10px] text-slate-500 block">vs Sector</span>
                  </td>

                  {/* Volume Z-Score */}
                  <td className="py-4 px-4 text-right whitespace-nowrap font-mono">
                    <span
                      className={`font-bold ${
                        item.volume_z_score >= 2.0 ? "text-cyan-400" : "text-slate-300"
                      }`}
                    >
                      {item.volume_z_score.toFixed(1)}σ
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      {formatCompact(item.current_volume)}
                    </span>
                  </td>

                  {/* Sparkline */}
                  <td className="py-4 px-4 text-center whitespace-nowrap">
                    <div className="flex justify-center">
                      <MiniSparkline positive={isPositive} />
                    </div>
                  </td>

                  {/* Driver preview */}
                  <td className="py-4 px-4 max-w-xs truncate text-slate-300">
                    <span className="text-xs">
                      {item.primary_drivers[0] || "Routine market drift"}
                    </span>
                  </td>

                  {/* Action */}
                  <td className="py-4 px-4 text-right whitespace-nowrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectItem(item);
                      }}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
                    >
                      <span>Evidence</span>
                      <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
