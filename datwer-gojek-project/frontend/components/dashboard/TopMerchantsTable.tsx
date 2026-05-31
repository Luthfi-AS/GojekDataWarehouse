"use client";

import React from "react";

interface MerchantItem {
  rank: number;
  name: string;
  category: string;
  revenue: string;
  performance: number;
}

interface TopMerchantsTableProps {
  title: string;
  data: MerchantItem[];
}

export default function TopMerchantsTable({
  title,
  data,
}: TopMerchantsTableProps) {
  return (
    <div className="bg-theme-card p-6 rounded-xl border border-theme-border shadow-sm transition-colors duration-300">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-theme-main">{title}</h2>
        <button className="text-sm font-semibold text-theme-main hover:text-theme-muted transition-colors">
          View All
        </button>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-12 gap-4 pb-3 border-b border-theme-border text-xs font-bold text-theme-muted uppercase tracking-wider">
        <div className="col-span-1">Rank</div>
        <div className="col-span-3">Merchant Name</div>
        <div className="col-span-1">Category</div>
        <div className="col-span-2 text-right">Revenue</div>
        <div className="col-span-5 text-center">Performance</div>
      </div>

      {/* Table Body */}
      <div className="mt-4 flex flex-col space-y-5">
        {data.map((merchant, idx) => (
          <div key={idx} className="grid grid-cols-12 gap-4 items-center">
            <div className="col-span-1 text-sm font-bold text-theme-main">
              {merchant.rank}
            </div>
            <div className="col-span-3 text-sm font-bold text-theme-main truncate pr-2">
              {merchant.name}
            </div>
            <div className="col-span-1 text-sm text-theme-muted truncate pr-2">
              {merchant.category}
            </div>
            <div className="col-span-2 text-sm font-bold text-theme-main text-right">
              {merchant.revenue}
            </div>

            {/* Progress Bar */}
            <div className="col-span-5 flex items-center pl-2 md:pl-4">
              <div className="w-full bg-theme-border h-2.5 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-theme-main transition-all duration-1000 ease-out"
                  style={{ width: `${merchant.performance}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
