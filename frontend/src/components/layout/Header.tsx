"use client";

import React, { useState } from "react";
import { 
  Activity, 
  Clock, 
  CheckCircle2, 
  FastForward, 
  RefreshCw, 
  ChevronDown, 
  Sparkles,
  ShieldCheck
} from "lucide-react";
import { Watchlist, Checkpoint } from "@/types";

interface HeaderProps {
  watchlists: Watchlist[];
  activeWatchlist: Watchlist | null;
  onSelectWatchlist: (wl: Watchlist) => void;
  checkpoint: Checkpoint | null;
  onAdvanceCheckpoint: () => void;
  onSimulateLeap: (hours: number) => void;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  watchlists,
  activeWatchlist,
  onSelectWatchlist,
  checkpoint,
  onAdvanceCheckpoint,
  onSimulateLeap,
  isLoading,
}) => {
  const [showWlMenu, setShowWlMenu] = useState(false);
  const [showDemoMenu, setShowDemoMenu] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-[#0c1017]/95 backdrop-blur px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Logo & Product Title */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Activity className="h-5 w-5 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white">MarketPulse</span>
              <span className="text-[10px] uppercase font-semibold tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Groww 2026
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Intelligent Market Watchlist</p>
          </div>
        </div>

        {/* Center: Watchlist Selector & Checkpoint Status */}
        <div className="flex items-center gap-3">
          {/* Watchlist Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowWlMenu(!showWlMenu)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-sm font-medium text-slate-200 border border-slate-700/60 transition"
            >
              <span>{activeWatchlist ? activeWatchlist.name : "Select Watchlist"}</span>
              <ChevronDown className="h-4 w-4 text-slate-400" />
            </button>

            {showWlMenu && (
              <div className="absolute top-full mt-1 left-0 w-48 rounded-lg bg-slate-900 border border-slate-700 shadow-xl py-1 z-50">
                {watchlists.map((wl) => (
                  <button
                    key={wl.id}
                    onClick={() => {
                      onSelectWatchlist(wl);
                      setShowWlMenu(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-sm hover:bg-slate-800 transition ${
                      activeWatchlist?.id === wl.id ? "text-emerald-400 font-semibold" : "text-slate-300"
                    }`}
                  >
                    {wl.name} ({wl.items.length})
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Checkpoint Badge */}
          {checkpoint && (
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
              <Clock className="h-3.5 w-3.5 text-amber-400" />
              <span>Last checked:</span>
              <span className="font-semibold text-white">{checkpoint.human_elapsed}</span>
            </div>
          )}
        </div>

        {/* Right Actions: Catch Me Up + Demo Controls */}
        <div className="flex items-center gap-2.5">
          {/* Catch Me Up (Advance Checkpoint) */}
          <button
            onClick={onAdvanceCheckpoint}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs transition shadow-md shadow-emerald-500/20 disabled:opacity-50"
            title="Acknowledge changes and reset checkpoint to now"
          >
            <CheckCircle2 className="h-4 w-4 stroke-[2.5]" />
            <span className="hidden sm:inline">Catch Me Up</span>
          </button>

          {/* Time Leap Demo Button for Judges */}
          <div className="relative">
            <button
              onClick={() => setShowDemoMenu(!showDemoMenu)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-medium transition"
              title="Simulate time lapse for evaluation"
            >
              <FastForward className="h-3.5 w-3.5 text-indigo-400" />
              <span className="hidden lg:inline">Simulate Time Leap</span>
              <ChevronDown className="h-3 w-3 text-indigo-400" />
            </button>

            {showDemoMenu && (
              <div className="absolute top-full mt-1 right-0 w-56 rounded-lg bg-slate-900 border border-indigo-500/30 shadow-2xl p-2 z-50 text-xs">
                <p className="font-semibold text-indigo-300 px-2 py-1 mb-1 border-b border-slate-800">
                  Judge Demo Mode
                </p>
                <button
                  onClick={() => {
                    onSimulateLeap(2);
                    setShowDemoMenu(false);
                  }}
                  className="w-full text-left px-2 py-1.5 rounded hover:bg-slate-800 text-slate-200 transition"
                >
                  ⚡ Simulate 2 Hours Ago
                </button>
                <button
                  onClick={() => {
                    onSimulateLeap(4);
                    setShowDemoMenu(false);
                  }}
                  className="w-full text-left px-2 py-1.5 rounded hover:bg-slate-800 text-slate-200 transition"
                >
                  ⚡ Simulate 4 Hours Ago (Recommended)
                </button>
                <button
                  onClick={() => {
                    onSimulateLeap(24);
                    setShowDemoMenu(false);
                  }}
                  className="w-full text-left px-2 py-1.5 rounded hover:bg-slate-800 text-slate-200 transition"
                >
                  ⚡ Simulate Yesterday Close (24h)
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
