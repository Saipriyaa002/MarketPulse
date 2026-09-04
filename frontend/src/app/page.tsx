"use client";

import React, { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { Watchlist, Checkpoint, MarketContext, PulseResponse, PulseItem } from "@/types";
import { Header } from "@/components/layout/Header";
import { MarketContextBar } from "@/components/layout/MarketContextBar";
import { PulseHero } from "@/components/pulse/PulseHero";
import { AttentionRankedTable } from "@/components/watchlist/AttentionRankedTable";
import { EvidenceDrawer } from "@/components/evidence/EvidenceDrawer";
import { DigestModal } from "@/components/pulse/DigestModal";
import { RefreshCw, Plus, TrendingUp } from "lucide-react";

export default function DashboardPage() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [activeWatchlist, setActiveWatchlist] = useState<Watchlist | null>(null);
  const [checkpoint, setCheckpoint] = useState<Checkpoint | null>(null);
  const [context, setContext] = useState<MarketContext | null>(null);
  const [pulse, setPulse] = useState<PulseResponse | null>(null);
  const [selectedItem, setSelectedItem] = useState<PulseItem | null>(null);
  const [digestData, setDigestData] = useState<any | null>(null);
  const [showDigestModal, setShowDigestModal] = useState(false);

  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleOpenDigest = async () => {
    if (!activeWatchlist) return;
    try {
      const data = await api.getDigest(activeWatchlist.id);
      setDigestData(data);
      setShowDigestModal(true);
    } catch (err) {
      console.error("Failed to load digest:", err);
    }
  };

  // Initialize data
  const loadInitialData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // 1. Ensure authenticated (guest fallback)
      let currentToken = api.getToken();
      if (!currentToken) {
        await api.guestLogin();
      }

      // 2. Fetch market context
      const mContext = await api.getMarketContext().catch(() => null);
      if (mContext) setContext(mContext);

      // 3. Fetch user watchlists
      let wlList = await api.getWatchlists();
      if (wlList.length === 0) {
        // Fallback: create default watchlist
        const defaultWl = await api.createWatchlist("Main Watchlist", ["INFY", "TCS", "HDFCBANK", "TATAMOTORS", "RELIANCE"]);
        wlList = [defaultWl];
      }
      setWatchlists(wlList);

      const currentWl = wlList.find((w) => w.is_default) || wlList[0];
      setActiveWatchlist(currentWl);

      // 4. Fetch Checkpoint and Pulse Feed for active watchlist
      if (currentWl) {
        const [cp, pFeed] = await Promise.all([
          api.getCheckpoint(currentWl.id),
          api.getSinceLastSeen(currentWl.id),
        ]);
        setCheckpoint(cp);
        setPulse(pFeed);
      }
    } catch (err: any) {
      console.error("Dashboard load error:", err);
      setError(err.message || "Failed to load watchlist data. Ensure backend is running on port 8000.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Handle selecting another watchlist
  const handleSelectWatchlist = async (wl: Watchlist) => {
    setActiveWatchlist(wl);
    setIsRefreshing(true);
    try {
      const [cp, pFeed] = await Promise.all([
        api.getCheckpoint(wl.id),
        api.getSinceLastSeen(wl.id),
      ]);
      setCheckpoint(cp);
      setPulse(pFeed);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Handle "Catch Me Up" (Advance checkpoint to now)
  const handleAdvanceCheckpoint = async () => {
    if (!activeWatchlist) return;
    setIsRefreshing(true);
    try {
      const newCp = await api.advanceCheckpoint(activeWatchlist.id);
      const updatedPulse = await api.getSinceLastSeen(activeWatchlist.id);
      setCheckpoint(newCp);
      setPulse(updatedPulse);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Handle Demo "Simulate Time Leap"
  const handleSimulateLeap = async (hours: number) => {
    if (!activeWatchlist) return;
    setIsRefreshing(true);
    try {
      const leapPulse = await api.simulateTimeLeap(activeWatchlist.id, hours);
      const updatedCp = await api.getCheckpoint(activeWatchlist.id);
      setPulse(leapPulse);
      setCheckpoint(updatedCp);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0a0e17] text-slate-100">
      {/* Top Navigation */}
      <Header
        watchlists={watchlists}
        activeWatchlist={activeWatchlist}
        onSelectWatchlist={handleSelectWatchlist}
        checkpoint={checkpoint}
        onAdvanceCheckpoint={handleAdvanceCheckpoint}
        onSimulateLeap={handleSimulateLeap}
        isLoading={isRefreshing}
      />

      {/* Market Context Ticker Strip */}
      <MarketContextBar context={context} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6 space-y-6">
        {/* Error notification if backend unavailable */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={loadInitialData}
              className="px-3 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 font-semibold"
            >
              Retry
            </button>
          </div>
        )}

        {/* Pulse Executive Hero Banner */}
        <PulseHero 
          pulse={pulse} 
          isLoading={isLoading} 
          onOpenDigest={handleOpenDigest} 
        />

        {/* Watchlist Intelligence Table */}
        <div className="space-y-3">
          <AttentionRankedTable
            items={pulse?.items || []}
            onSelectItem={(item) => setSelectedItem(item)}
            isLoading={isLoading || isRefreshing}
          />
        </div>
      </main>

      {/* Slide-Over Evidence Drawer */}
      <EvidenceDrawer
        item={selectedItem}
        watchlistId={activeWatchlist?.id}
        onClose={() => setSelectedItem(null)}
      />

      {/* What Did I Miss Digest Modal */}
      {showDigestModal && (
        <DigestModal
          digest={digestData}
          onClose={() => setShowDigestModal(false)}
        />
      )}
    </div>
  );
}
