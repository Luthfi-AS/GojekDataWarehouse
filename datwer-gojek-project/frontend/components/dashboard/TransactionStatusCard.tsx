"use client";

import React from "react";

interface TransactionStatusCardProps {
  title: string;
  description: string;
  successPercentage: number;
  failedPercentage: number;
  primaryColor?: string;
}

export default function TransactionStatusCard({
  title,
  description,
  successPercentage,
  failedPercentage,
  primaryColor = "var(--color-primary)",
}: TransactionStatusCardProps) {
  return (
    <div className="bg-theme-card p-6 rounded-xl border border-theme-border shadow-sm flex flex-col justify-center transition-colors duration-300">
      <h2 className="text-lg font-semibold text-theme-main">{title}</h2>
      <p className="text-sm text-theme-muted mb-6">{description}</p>

      <div className="border-t border-theme-border pt-6 mt-2 flex items-center space-x-6">
        <div className="flex items-center text-sm font-medium text-theme-main">
          <div
            className="w-3 h-3 rounded-full mr-2"
            style={{ backgroundColor: primaryColor }}
          ></div>
          Success ({successPercentage}%)
        </div>
        <div className="flex items-center text-sm font-medium text-theme-muted">
          <div className="w-3 h-3 rounded-full mr-2 bg-gray-300 dark:bg-gray-600"></div>
          Failed ({failedPercentage}%)
        </div>
      </div>
    </div>
  );
}