"use client";

import React from "react";
import { Banknote, TrendingUp, Tag, Clock, Info } from "lucide-react";

// Import Komponen Reusable
import PageHeader from "@/components/layout/PageHeader";
import KpiCard from "@/components/dashboard/KpiCard";
import DonutChart from "@/components/dashboard/DonutChart";
import DualLineChart from "@/components/dashboard/DualLineChart";
import TopMerchantsTable from "@/components/dashboard/TopMerchantsTable";

// Import Custom Hook
import { useGoFoodSummary } from "@/hooks/queries/useGoFood";

// Formatters
const formatCompact = (num: number) =>
  new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(num);

const formatCurrency = (num: number) => `Rp ${formatCompact(num)}`;

export default function GoFoodDashboard() {
  // Fetch data asli dari Backend
  const { data, isLoading, isError } = useGoFoodSummary();

  const donutColors = [
    "var(--text-main)",
    "var(--error-text)",
    "var(--text-muted)",
  ];

  // Handle Loading
  if (isLoading) {
    return (
      <div className="min-h-screen bg-theme-base p-8 flex items-center justify-center">
        <div className="text-theme-muted font-medium animate-pulse">
          Mengambil data GoFood dari server...
        </div>
      </div>
    );
  }

  // Handle Error
  if (isError || !data) {
    return (
      <div className="min-h-screen bg-theme-base p-8 flex items-center justify-center">
        <div className="text-error font-medium">
          Gagal terhubung ke server API. Pastikan backend menyala.
        </div>
      </div>
    );
  }

  // Kalkulasi total merchant untuk teks di tengah Donut Chart
  const totalMerchants = data.category_split.reduce(
    (acc, curr) => acc + curr.value,
    0,
  );

  // Map ulang data top_merchants agar nilai revenue menjadi string format ("Rp 1.2B")
  // karena komponen tabel kita di frontend menerima format teks untuk properti ini
  const formattedTopMerchants = data.top_merchants.map((merchant) => ({
    ...merchant,
    revenue: formatCurrency(merchant.revenue),
  }));

  return (
    <div className="min-h-screen bg-theme-base p-8 pb-20 transition-colors duration-300">
      {/* 1. HEADER */}
      <PageHeader
        title="GoFood & Merchant Operations"
        description="Real-time analytics for food delivery and merchant performance"
      />

      {/* 2. KPI SCORECARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <KpiCard
          title="TOTAL GROSS REVENUE"
          value={formatCurrency(data.kpis.total_revenue.value)}
          trend={data.kpis.total_revenue.trend}
          trendLabel="vs last period"
          icon={<Banknote className="w-5 h-5" />}
          iconColors="bg-error-bg text-error"
        />
        <KpiCard
          title="GOJEK GROSS PROFIT"
          value={formatCurrency(data.kpis.gross_profit.value)}
          trend={data.kpis.gross_profit.trend}
          trendLabel="vs last period"
          icon={<TrendingUp className="w-5 h-5" />}
          iconColors="bg-error-bg text-error"
        />
        <KpiCard
          title="TOTAL PROMO DISCOUNT"
          value={formatCurrency(data.kpis.total_promo.value)}
          trend={data.kpis.total_promo.trend}
          trendLabel="vs last period"
          icon={<Tag className="w-5 h-5" />}
          iconColors="bg-error-bg text-error"
        />
        <KpiCard
          title="AVG PREP TIME"
          value={`${data.kpis.avg_prep_time.value}m`}
          trend={data.kpis.avg_prep_time.trend}
          trendLabel="vs last period"
          icon={<Clock className="w-5 h-5" />}
          iconColors="bg-error-bg text-error"
        />
      </div>

      {/* 3. CHARTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* DUAL LINE CHART */}
        <DualLineChart
          title="Daily Revenue vs Promo Discount"
          data={data.revenue_vs_promo}
          line1Key="revenue"
          line1Name="Revenue (Rp)"
          line1Color="var(--text-main)"
          line2Key="promo"
          line2Name="Promo (Rp)"
          line2Color="var(--error-text)"
        />

        {/* DONUT CHART */}
        <div className="relative">
          <Info className="absolute top-6 right-6 w-5 h-5 text-theme-muted cursor-pointer z-10" />
          <DonutChart
            title="Category Split"
            description=""
            data={data.category_split}
            dataKey="value"
            centerValue={formatCompact(totalMerchants)}
            centerLabel="Merchants"
            colors={donutColors}
          />
        </div>
      </div>

      {/* 4. TOP MERCHANTS TABLE */}
      <TopMerchantsTable
        title="Top Merchants by Revenue"
        data={formattedTopMerchants}
      />
    </div>
  );
}
