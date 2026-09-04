"use client";

import React, { useEffect, useState } from "react";
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip,
  BarChart,
  Bar
} from "recharts";
import { api } from "@/lib/api";
import { OHLCV } from "@/types";
import { formatINR } from "@/lib/utils";

interface StockDetailChartProps {
  symbol: string;
}

export const StockDetailChart: React.FC<StockDetailChartProps> = ({ symbol }) => {
  const [data, setData] = useState<OHLCV[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);

    api.getHistoricalOHLCV(symbol, 30)
      .then((bars) => {
        if (isMounted) {
          setData(bars);
          setIsLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [symbol]);

  if (isLoading) {
    return (
      <div className="h-64 w-full flex items-center justify-center bg-slate-900/50 rounded-xl border border-slate-800">
        <span className="text-xs text-slate-500 animate-pulse">Loading price history...</span>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="h-64 w-full flex items-center justify-center bg-slate-900/50 rounded-xl border border-slate-800">
        <span className="text-xs text-slate-500">Historical chart data unavailable</span>
      </div>
    );
  }

  const chartData = data.map((d) => ({
    date: new Date(d.timestamp).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
    price: d.close,
    volume: d.volume,
  }));

  const minPrice = Math.min(...chartData.map((d) => d.price)) * 0.98;
  const maxPrice = Math.max(...chartData.map((d) => d.price)) * 1.02;

  return (
    <div className="space-y-4">
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d09c" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00d09c" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="date" 
              stroke="#64748b" 
              fontSize={10} 
              tickLine={false} 
              axisLine={false} 
            />
            <YAxis 
              domain={[minPrice, maxPrice]} 
              stroke="#64748b" 
              fontSize={10} 
              tickLine={false} 
              axisLine={false}
              tickFormatter={(val) => `₹${val.toFixed(0)}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "8px",
                fontSize: "12px",
                color: "#f8fafc",
              }}
              formatter={(val: any) => [formatINR(val), "Close"]}
            />
            <Area 
              type="monotone" 
              dataKey="price" 
              stroke="#00d09c" 
              strokeWidth={2} 
              fillOpacity={1} 
              fill="url(#priceGradient)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
