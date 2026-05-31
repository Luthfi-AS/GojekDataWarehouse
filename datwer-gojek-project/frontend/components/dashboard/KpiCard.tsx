import React from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string | number;
  trend: number;
  trendLabel: string;
  icon: React.ReactNode;
  iconColors?: string; // class Tailwind opsional untuk warna background ikon
}

export default function KpiCard({
  title,
  value,
  trend,
  trendLabel,
  icon,
  iconColors = "bg-success-bg text-success",
}: KpiCardProps) {
  const isPositive = trend >= 0;

  return (
    <div className="bg-theme-card p-6 rounded-xl border border-theme-border shadow-sm flex flex-col justify-between transition-colors duration-300">
      <div className="flex justify-between items-start">
        <p className="text-sm font-medium text-theme-muted whitespace-pre-line">
          {title}
        </p>
        <div
          className={`p-2 rounded-lg transition-colors duration-300 ${iconColors}`}
        >
          {icon}
        </div>
      </div>
      <div className="mt-4">
        <h3 className="text-3xl font-bold text-theme-main">{value}</h3>
        <div className="flex items-center mt-2 text-xs">
          <span
            className={`flex items-center px-1.5 py-0.5 rounded-md font-medium transition-colors duration-300 ${
              isPositive
                ? "bg-success-bg text-success"
                : "bg-error-bg text-error"
            }`}
          >
            {isPositive ? (
              <TrendingUp className="w-3 h-3 mr-1" />
            ) : (
              <TrendingDown className="w-3 h-3 mr-1" />
            )}
            {isPositive ? "+" : ""}
            {trend}%
          </span>
          <span className="text-theme-muted ml-2">{trendLabel}</span>
        </div>
      </div>
    </div>
  );
}
