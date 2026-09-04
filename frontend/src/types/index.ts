export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_guest: boolean;
  preferences: Record<string, any>;
  created_at: string;
}

export interface Quote {
  symbol: string;
  name: string;
  price: number;
  open: number;
  high: number;
  low: number;
  previous_close: number;
  change: number;
  change_pct: number;
  volume: number;
  avg_volume_20d: number;
  beta: number;
  sector: string;
  exchange: string;
  timestamp: string;
}

export interface WatchlistItem {
  id: string;
  watchlist_id: string;
  symbol: string;
  custom_tag?: string;
  alert_preferences: Record<string, any>;
  added_at: string;
  quote?: Quote;
}

export interface Watchlist {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  items: WatchlistItem[];
}

export interface MarketContext {
  benchmark_symbol: string;
  benchmark_name: string;
  benchmark_price: number;
  benchmark_change: number;
  benchmark_change_pct: number;
  market_status: string;
  sectors: Record<string, number>;
  timestamp: string;
}

export interface NewsItem {
  id: string;
  symbol?: string;
  sector?: string;
  headline: string;
  summary?: string;
  source_name: string;
  source_url?: string;
  event_type: string;
  sentiment_score: number;
  impact_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  published_at: string;
}

export interface OHLCV {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PulseItem {
  symbol: string;
  name: string;
  sector: string;
  current_price: number;
  checkpoint_price: number;
  price_change: number;
  price_change_pct: number;
  session_change_pct?: number;
  alpha_excess_pct: number;
  sector_divergence_pct: number;
  volume_z_score: number;
  current_volume: number;
  avg_volume_20d: number;
  attention_score: number;
  attention_level: "CRITICAL" | "ELEVATED" | "ROUTINE";
  confidence_score: number;
  confidence_tier?: "HIGH" | "MODERATE" | "ESTABLISHING";
  confidence_tier_description?: string;
  confidence_breakdown?: Record<string, any>;
  is_meaningful: boolean;
  primary_drivers: string[];
  summary: string;
  breakdown: {
    market_alpha_score?: number;
    sector_divergence_score?: number;
    volume_surge_score?: number;
    event_relevance_score?: number;
    persistence_score?: number;
  };
  related_events: Array<{
    id: string;
    headline: string;
    source: string;
    sentiment: number;
    impact: string;
    published_at: string;
  }>;
}

export interface PulseResponse {
  watchlist_id: string;
  watchlist_name: string;
  checkpoint_id: string;
  checkpoint_time: string;
  elapsed_seconds: number;
  human_elapsed: string;
  benchmark_status: {
    symbol: string;
    name: string;
    price: number;
    change_pct: number;
    status: string;
  };
  total_items: number;
  meaningful_count: number;
  critical_count: number;
  executive_summary: string;
  items: PulseItem[];
}

export interface Checkpoint {
  id: string;
  user_id: string;
  watchlist_id: string;
  device_id: string;
  checkpoint_time: string;
  snapshot_data: Record<string, any>;
  trigger_event: string;
  created_at: string;
  elapsed_seconds: number;
  human_elapsed: string;
}
