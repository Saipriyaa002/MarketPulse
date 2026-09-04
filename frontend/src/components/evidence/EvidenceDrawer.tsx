"use client";

import React, { useState } from "react";
import { 
  X, 
  TrendingUp, 
  TrendingDown, 
  Layers, 
  BarChart3, 
  FileText, 
  ShieldCheck, 
  ExternalLink,
  Zap,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Clock,
  Info
} from "lucide-react";
import { PulseItem } from "@/types";
import { formatINR, formatPercent, formatCompact } from "@/lib/utils";
import { AttentionBadge } from "../watchlist/AttentionBadge";
import { StockDetailChart } from "../stock/StockDetailChart";
import { api } from "@/lib/api";

interface EvidenceDrawerProps {
  item: PulseItem | null;
  watchlistId?: string;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ 
  item, 
  watchlistId,
  onClose 
}) => {
  const [showConfidenceDetails, setShowConfidenceDetails] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<any>(null);
  const [isLoadingAi, setIsLoadingAi] = useState(false);

  if (!item) return null;

  const isPositive = item.price_change_pct >= 0;
  const isSessionPositive = (item.session_change_pct || 0) >= 0;

  const handleFetchAiExplanation = async () => {
    if (!watchlistId) return;
    setIsLoadingAi(true);
    try {
      const exp = await api.explainSymbol(item.symbol, watchlistId);
      setAiExplanation(exp);
    } catch (err) {
      console.error("AI explanation error:", err);
    } finally {
      setIsLoadingAi(false);
    }
  };

  const confidenceTierColor = 
    item.confidence_tier === "HIGH" ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" :
    item.confidence_tier === "MODERATE" ? "text-amber-400 bg-amber-500/10 border-amber-500/20" :
    "text-slate-400 bg-slate-500/10 border-slate-500/20";

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="w-full max-w-xl h-full bg-[#0e141f] border-l border-slate-800 shadow-2xl flex flex-col overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="sticky top-0 z-10 bg-[#0e141f]/95 backdrop-blur border-b border-slate-800 p-6 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold text-white tracking-tight">{item.symbol}</h2>
              <AttentionBadge score={item.attention_score} level={item.attention_level} />
            </div>
            <p className="text-sm text-slate-400 mt-0.5">{item.name} · {item.sector}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="p-6 space-y-6 flex-1">
          {/* Price & Checkpoint Delta Comparison Card */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 grid grid-cols-2 gap-4">
            <div>
              <span className="text-xs text-slate-400 font-medium">Current Price</span>
              <p className="text-2xl font-bold text-white mt-0.5 font-mono">{formatINR(item.current_price)}</p>
              
              <div className="mt-1 space-y-0.5">
                <span className={`text-xs font-semibold flex items-center gap-0.5 ${isPositive ? "text-emerald-400" : "text-rose-400"}`}>
                  {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  {formatPercent(item.price_change_pct)} since checkpoint
                </span>
                {item.session_change_pct !== undefined && (
                  <span className="text-[11px] text-slate-400 block font-mono">
                    Today: {formatPercent(item.session_change_pct)} (full day)
                  </span>
                )}
              </div>
            </div>
            <div>
              <span className="text-xs text-slate-400 font-medium">Checkpoint Baseline</span>
              <p className="text-xl font-semibold text-slate-300 mt-1 font-mono">{formatINR(item.checkpoint_price)}</p>
              <span className="text-xs text-slate-500 mt-1 block font-mono">
                Delta: {formatINR(item.price_change)}
              </span>
            </div>
          </div>

          {/* Interactive Chart */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Price Trajectory & Trend (30 Days)
              </h3>
              <span className="text-[10px] text-emerald-400 font-medium flex items-center gap-1">
                <Clock className="h-3 w-3" /> Checkpoint Indexed
              </span>
            </div>
            <StockDetailChart symbol={item.symbol} />
          </div>

          {/* Quantitative Evidence Grid */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <BarChart3 className="h-4 w-4 text-emerald-400" />
              Grounded Quantitative Metrics
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {/* Alpha Excess */}
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[11px] text-slate-400">Market-Rel Alpha</span>
                <p className={`text-base font-bold mt-0.5 font-mono ${item.alpha_excess_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                  {formatPercent(item.alpha_excess_pct)}
                </p>
                <span className="text-[10px] text-slate-500">vs Nifty 50</span>
              </div>

              {/* Sector Divergence */}
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[11px] text-slate-400">Sector Divergence</span>
                <p className={`text-base font-bold mt-0.5 font-mono ${item.sector_divergence_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                  {formatPercent(item.sector_divergence_pct)}
                </p>
                <span className="text-[10px] text-slate-500">vs {item.sector}</span>
              </div>

              {/* Volume Anomaly */}
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[11px] text-slate-400">Volume Surge</span>
                <p className="text-base font-bold text-cyan-400 mt-0.5 font-mono">
                  {item.volume_z_score.toFixed(1)}σ
                </p>
                <span className="text-[10px] text-slate-500">
                  {formatCompact(item.current_volume)} shares
                </span>
              </div>
            </div>
          </div>

          {/* Deterministic Explanation Card */}
          <div className="p-4 rounded-xl bg-gradient-to-br from-slate-900 to-[#121926] border border-slate-700/80">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-2 flex items-center gap-1.5">
              <Zap className="h-4 w-4" />
              Why this requires attention
            </h3>
            <p className="text-sm text-slate-200 leading-relaxed">
              {item.summary}
            </p>

            <div className="mt-4 pt-3 border-t border-slate-800">
              <span className="text-xs font-medium text-slate-400 block mb-2">Detected Drivers:</span>
              <ul className="space-y-1.5">
                {item.primary_drivers.map((driver, idx) => (
                  <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                    <span>{driver}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* On-Demand Grounded AI Briefing */}
          <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-400" />
                <span className="text-xs font-bold text-indigo-200 uppercase tracking-wider">
                  Grounded AI Analysis
                </span>
              </div>
              <button
                onClick={handleFetchAiExplanation}
                disabled={isLoadingAi || !watchlistId}
                className="px-3 py-1 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 border border-indigo-500/40 text-indigo-300 text-xs font-semibold transition disabled:opacity-50"
              >
                {isLoadingAi ? "Synthesizing..." : aiExplanation ? "Refresh AI" : "Run AI Analysis"}
              </button>
            </div>

            {aiExplanation ? (
              <div className="mt-3 space-y-2.5 text-xs text-slate-300 pt-3 border-t border-indigo-500/20">
                <p className="font-semibold text-slate-100">{aiExplanation.headline}</p>
                <p className="leading-relaxed text-slate-300">{aiExplanation.executive_summary}</p>
                {aiExplanation.key_takeaways && (
                  <div className="mt-2 space-y-1">
                    <span className="text-[11px] font-semibold text-indigo-300 block">Takeaways:</span>
                    {aiExplanation.key_takeaways.map((t: string, i: number) => (
                      <div key={i} className="flex items-start gap-1.5 text-slate-300">
                        <span className="text-indigo-400 font-bold">•</span>
                        <span>{t}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="text-[10px] text-slate-500 mt-2 italic">
                  Source: {aiExplanation.source || "deterministic_grounded_engine"} · Never invents unprovided market data.
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400 mt-2">
                Synthesize grounded analytical insights citing verified numbers and news from this session.
              </p>
            )}
          </div>

          {/* Correlated News / Events */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <FileText className="h-4 w-4 text-indigo-400" />
              Correlated Catalysts & News
            </h3>

            {item.related_events.length > 0 ? (
              <div className="space-y-3">
                {item.related_events.map((event) => (
                  <div key={event.id} className="p-3 rounded-lg bg-slate-900/90 border border-slate-800">
                    <p className="text-xs font-medium text-slate-100 leading-snug">{event.headline}</p>
                    <div className="flex items-center justify-between mt-2 text-[11px] text-slate-500">
                      <span className="font-semibold text-slate-400">Source: {event.source}</span>
                      <span className="px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] font-semibold">
                        {event.impact} IMPACT
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-slate-900/50 border border-dashed border-slate-800 text-center text-xs text-slate-500">
                No corporate news headline detected within this delta window. Movement driven primarily by quantitative order flow imbalance.
              </div>
            )}
          </div>

          {/* Defensible Evidence Confidence Section */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div 
              className="flex items-center justify-between cursor-pointer"
              onClick={() => setShowConfidenceDetails(!showConfidenceDetails)}
            >
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                <span className="text-xs font-semibold text-slate-200">Evidence Confidence:</span>
                <span className="text-sm font-bold text-white">{item.confidence_score}%</span>
                <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${confidenceTierColor}`}>
                  {item.confidence_tier || "HIGH"}
                </span>
              </div>
              <button className="text-slate-400 hover:text-white transition">
                {showConfidenceDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>
            </div>

            {item.confidence_tier_description && (
              <p className="text-[11px] text-slate-400 mt-1.5">
                {item.confidence_tier_description}
              </p>
            )}

            {/* Expandable 4-Pillar Breakdown */}
            {showConfidenceDetails && item.confidence_breakdown && (
              <div className="mt-3 pt-3 border-t border-slate-800 grid grid-cols-2 gap-2 text-xs">
                {Object.entries(item.confidence_breakdown).map(([key, val]: [string, any]) => (
                  <div key={key} className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <span className="text-[10px] text-slate-500 capitalize">{key.replace("_", " ")}</span>
                    <p className="font-semibold text-slate-200 mt-0.5">
                      {val.points}/{val.max} pts
                    </p>
                    <span className="text-[10px] text-slate-400 block truncate">{val.label}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
