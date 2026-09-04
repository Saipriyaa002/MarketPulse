import {
  User,
  Watchlist,
  MarketContext,
  PulseResponse,
  Checkpoint,
  OHLCV,
  Quote,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("marketpulse_token");
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("marketpulse_token", token);
      } else {
        localStorage.removeItem("marketpulse_token");
      }
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== "undefined") {
      this.token = localStorage.getItem("marketpulse_token");
    }
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Auto fallback to guest login if token expired/invalid
      if (typeof window !== "undefined" && !endpoint.includes("/auth/")) {
        try {
          const guestRes = await this.guestLogin();
          // Retry request once with new token
          headers["Authorization"] = `Bearer ${guestRes.access_token}`;
          const retryRes = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
          });
          if (!retryRes.ok) throw new Error(`HTTP ${retryRes.status}`);
          return retryRes.json();
        } catch {
          this.setToken(null);
        }
      }
    }

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errData.detail || `Request failed with status ${response.status}`);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth
  async guestLogin(): Promise<{ access_token: string; user: User }> {
    const res = await this.request<{ access_token: string; user: User }>("/auth/guest", {
      method: "POST",
    });
    this.setToken(res.access_token);
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  // Watchlists
  async getWatchlists(): Promise<Watchlist[]> {
    return this.request<Watchlist[]>("/watchlists");
  }

  async createWatchlist(name: string, symbols: string[] = []): Promise<Watchlist> {
    return this.request<Watchlist>("/watchlists", {
      method: "POST",
      body: JSON.stringify({ name, symbols }),
    });
  }

  async addWatchlistItem(watchlistId: string, symbol: string): Promise<any> {
    return this.request(`/watchlists/${watchlistId}/items`, {
      method: "POST",
      body: JSON.stringify({ symbol }),
    });
  }

  async removeWatchlistItem(watchlistId: string, symbol: string): Promise<void> {
    return this.request(`/watchlists/${watchlistId}/items/${symbol}`, {
      method: "DELETE",
    });
  }

  // Market & Context
  async getMarketContext(): Promise<MarketContext> {
    return this.request<MarketContext>("/market/context");
  }

  async getHistoricalOHLCV(symbol: string, days: number = 30): Promise<OHLCV[]> {
    return this.request<OHLCV[]>(`/market/history/${symbol}?days=${days}`);
  }

  async getQuote(symbol: string): Promise<Quote> {
    return this.request<Quote>(`/market/quote/${symbol}`);
  }

  async searchSymbols(q: string): Promise<Array<{ symbol: string; name: string; sector: string; price: string }>> {
    return this.request(`/market/search?q=${encodeURIComponent(q)}`);
  }

  // Checkpoints & Pulse
  async getCheckpoint(watchlistId: string): Promise<Checkpoint> {
    return this.request<Checkpoint>(`/checkpoints/current?watchlist_id=${watchlistId}`);
  }

  async advanceCheckpoint(watchlistId: string): Promise<Checkpoint> {
    return this.request<Checkpoint>("/checkpoints/advance", {
      method: "POST",
      body: JSON.stringify({ watchlist_id: watchlistId, trigger_event: "manual_ack" }),
    });
  }

  async getSinceLastSeen(watchlistId: string): Promise<PulseResponse> {
    return this.request<PulseResponse>(`/pulse/since-last-seen?watchlist_id=${watchlistId}`);
  }

  async getDigest(watchlistId: string): Promise<any> {
    return this.request(`/pulse/digest?watchlist_id=${watchlistId}`);
  }

  async explainSymbol(symbol: string, watchlistId: string): Promise<any> {
    return this.request(`/pulse/explain/${symbol}?watchlist_id=${watchlistId}`);
  }

  async simulateTimeLeap(watchlistId: string, hoursAgo: number = 4.0): Promise<PulseResponse> {
    return this.request<PulseResponse>("/pulse/simulate-time-leap", {
      method: "POST",
      body: JSON.stringify({
        watchlist_id: watchlistId,
        hours_ago: hoursAgo,
        simulate_volatility: true,
      }),
    });
  }
}

export const api = new ApiClient();
