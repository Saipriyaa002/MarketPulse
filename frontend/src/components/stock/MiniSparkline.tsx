"use client";

import React from "react";

interface MiniSparklineProps {
  positive?: boolean;
  width?: number;
  height?: number;
}

export const MiniSparkline: React.FC<MiniSparklineProps> = ({
  positive = true,
  width = 72,
  height = 24,
}) => {
  // Deterministic SVG wave path for responsive sparkline
  const points = positive
    ? "2,20 16,18 28,21 42,12 56,14 70,4"
    : "2,4 16,7 28,5 42,16 56,12 70,20";

  const strokeColor = positive ? "#00d09c" : "#eb5b3c";

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        fill="none"
        stroke={strokeColor}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
};
