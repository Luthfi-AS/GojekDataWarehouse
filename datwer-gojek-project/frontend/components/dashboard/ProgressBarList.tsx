"use client";

import React, { useState } from "react";

interface ProgressBarItem {
  name: string;
  volume: number;
  growth: number;
}

interface ProgressBarListProps {
  title: string;
  description: string;
  data: ProgressBarItem[];
  color?: string;
}

export default function ProgressBarList({
  title,
  description,
  data,
  color = "var(--color-primary)",
}: ProgressBarListProps) {
  // State Toggle dipindahkan ke dalam komponen
  const [metric, setMetric] = useState<"volume" | "growth">("volume");

  return (
    <div className="bg-theme-card p-6 rounded-xl border border-theme-border shadow-sm transition-colors duration-300">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
        <div>
          <h2 className="text-lg font-semibold text-theme-main">{title}</h2>
          <p className="text-sm text-theme-muted">{description}</p>
        </div>
        <div className="flex bg-theme-base p-1 rounded-lg mt-4 sm:mt-0 border border-theme-border transition-colors duration-300">
          <button
            onClick={() => setMetric("volume")}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
              metric === "volume"
                ? "bg-theme-card shadow-sm text-theme-main"
                : "text-theme-muted hover:text-theme-main"
            }`}
          >
            By Volume
          </button>
          <button
            onClick={() => setMetric("growth")}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
              metric === "growth"
                ? "bg-theme-card shadow-sm text-theme-main"
                : "text-theme-muted hover:text-theme-main"
            }`}
          >
            By Growth
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {data.map((item: any, idx: number) => {
          const maxVal = Math.max(
            ...data.map((c: any) =>
              metric === "volume" ? c.volume : Math.abs(c.growth),
            ),
          );
          const currentVal = metric === "volume" ? item.volume : item.growth;
          const barWidth =
            maxVal === 0 ? 0 : (Math.abs(currentVal) / maxVal) * 100;

          return (
            <div key={idx} className="relative">
              <div className="flex justify-between items-end mb-2">
                <span className="text-sm font-medium text-theme-main">
                  {item.name}
                </span>
                <span className="text-sm font-bold text-theme-main">
                  {metric === "volume"
                    ? new Intl.NumberFormat("id-ID").format(item.volume)
                    : `${item.growth > 0 ? "+" : ""}${item.growth}%`}
                </span>
              </div>
              <div className="w-full bg-theme-base h-2.5 rounded-full overflow-hidden border border-theme-border/50 transition-colors duration-300">
                <div
                  className={`h-full rounded-full transition-all duration-500`}
                  style={{
                    width: `${barWidth}%`,
                    backgroundColor:
                      metric === "growth" && currentVal < 0
                        ? "var(--error-text)"
                        : color,
                  }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
