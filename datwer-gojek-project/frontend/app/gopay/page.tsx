"use client";

import { useState } from "react";
import { Wallet, TrendingUp, Flame, CreditCard, ListChecks } from "lucide-react";

// Import Komponen Reusable
import PageHeader from "@/components/layout/PageHeader";
import KpiCard from "@/components/dashboard/KpiCard";
import DualLineChart from "@/components/dashboard/DualLineChart";
import DonutChart from "@/components/dashboard/DonutChart";

// Import Custom Hook TanStack Query
import { useGoPaySummary, useGoPayFilters } from "@/hooks/queries/useGoPay";

// Formatters
const formatCompact = (num: number) =>
  new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(num);

const formatCurrency = (num: number) => `Rp ${formatCompact(num)}`;

export default function GoPayDashboard() {
  // State 5 filter: rentang hari, metode pembayaran, status transaksi,
  // rentang volume transaksi, dan rentang cashback dibakar (GoPay tanpa dimensi kota)
  const [days, setDays] = useState(30);
  const [paymentMethod, setPaymentMethod] = useState("");
  const [status, setStatus] = useState("");
  const [volumeMin, setVolumeMin] = useState<number | null>(null);
  const [volumeMax, setVolumeMax] = useState<number | null>(null);
  const [cashbackMin, setCashbackMin] = useState<number | null>(null);
  const [cashbackMax, setCashbackMax] = useState<number | null>(null);

  // Mengambil data dinamis dari backend (re-fetch saat filter berubah)
  const { data, isLoading, isError } = useGoPaySummary({
    days,
    paymentMethod,
    status,
    volumeMin,
    volumeMax,
    cashbackMin,
    cashbackMax,
  });
  const { data: filterOptions } = useGoPayFilters();

  // Palet warna khusus GoPay
  const gopayBlue = "#00AED6";
  const gopayRed = "#F87171";
  const gopayGreen = "#10B981";

  const methodColors = [gopayBlue, "#4B5563", "#D1D5DB"];
  const typeColors = [gopayGreen, gopayBlue, gopayRed];

  const iconBgClass =
    "bg-[#E0F7FA] text-[#00AED6] dark:bg-[#00AED6]/20 dark:text-[#00AED6]";

  // Handle Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-theme-base p-8 flex items-center justify-center">
        <div className="text-theme-muted font-medium animate-pulse">
          Mengambil data GoPay dari server...
        </div>
      </div>
    );
  }

  // Handle Error State
  if (isError || !data) {
    return (
      <div className="min-h-screen bg-theme-base p-8 flex items-center justify-center">
        <div className="text-error font-medium">
          Gagal terhubung ke server API. Pastikan backend menyala.
        </div>
      </div>
    );
  }

  // Mencegah error menggunakan optional chaining (?.)
  const topMethod =
    data?.method_popularity?.length > 0
      ? data.method_popularity.reduce((prev, current) =>
          prev.value > current.value ? prev : current,
        )
      : { percentage: 0 };

  const topType =
    data?.transaction_type?.length > 0
      ? data.transaction_type.reduce((prev, current) =>
          prev.value > current.value ? prev : current,
        )
      : { percentage: 0 };

  return (
    <div className="min-h-screen bg-theme-base p-8 pb-20 transition-colors duration-300">
      {/* 1. HEADER */}
      <PageHeader
        title="GoPay Financial Ledger"
        description="Real-time financial reconciliation and transaction oversight."
        days={days}
        onDaysChange={setDays}
        selectFilters={[
          {
            key: "paymentMethod",
            label: "All Methods",
            value: paymentMethod,
            options: filterOptions?.payment_methods ?? [],
            onChange: setPaymentMethod,
            icon: <CreditCard className="w-4 h-4 mr-2 text-theme-muted" />,
          },
          {
            key: "status",
            label: "All Statuses",
            value: status,
            options: filterOptions?.transaction_statuses ?? [],
            onChange: setStatus,
            icon: <ListChecks className="w-4 h-4 mr-2 text-theme-muted" />,
          },
        ]}
        rangeFilters={[
          {
            key: "volume",
            label: "Volume",
            min: filterOptions?.volume_range.min ?? 0,
            max: filterOptions?.volume_range.max ?? 0,
            valueMin: volumeMin,
            valueMax: volumeMax,
            onChange: (min, max) => {
              setVolumeMin(min);
              setVolumeMax(max);
            },
          },
          {
            key: "cashback",
            label: "Cashback",
            min: filterOptions?.cashback_range.min ?? 0,
            max: filterOptions?.cashback_range.max ?? 0,
            valueMin: cashbackMin,
            valueMax: cashbackMax,
            onChange: (min, max) => {
              setCashbackMin(min);
              setCashbackMax(max);
            },
          },
        ]}
      />

      {/* 2. KPI SCORECARDS (3 Kolom) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <KpiCard
          title="GROSS TRANSACTION VALUE (GTV)"
          value={formatCurrency(data.kpis.gtv.value)}
          trend={data.kpis.gtv.trend}
          trendLabel="vs last period"
          icon={<Wallet className="w-5 h-5" />}
          iconColors={iconBgClass}
        />
        <KpiCard
          title="TOTAL ADMIN FEE REVENUE"
          value={formatCurrency(data.kpis.admin_fee.value)}
          trend={data.kpis.admin_fee.trend}
          trendLabel="vs last period"
          icon={<TrendingUp className="w-5 h-5" />}
          iconColors={iconBgClass}
        />
        <KpiCard
          title="TOTAL CASHBACK BURNED"
          value={formatCurrency(data.kpis.cashback_burned.value)}
          trend={data.kpis.cashback_burned.trend}
          trendLabel="vs last period"
          icon={<Flame className="w-5 h-5" />}
          iconColors={iconBgClass}
        />
      </div>

      {/* 3. CHARTS ROW (Menggunakan Grid 4 Kolom) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6 mb-6">
        {/* KIRI: DUAL LINE CHART (Mengambil 2 dari 4 kolom = 50%) */}
        <div className="xl:col-span-2 w-full min-w-0">
          <DualLineChart
            title="Daily Revenue vs Burn"
            data={data?.revenue_vs_burn || []}
            line1Key="revenue"
            line1Name="Admin Fee"
            line1Color={gopayBlue}
            line2Key="burn"
            line2Name="Cashback"
            line2Color={gopayRed}
          />
        </div>

        {/* TENGAH: DONUT 1 (Mengambil 1 dari 4 kolom = 25%) */}
        <div className="xl:col-span-1 w-full min-w-0">
          <DonutChart
            title="Transaction Types"
            description="Top Up vs Transfer vs Payment"
            data={data?.transaction_type || []}
            dataKey="value"
            centerValue={`${topType.percentage}%`}
            centerLabel="Top Type"
            colors={typeColors}
          />
        </div>

        {/* KANAN: DONUT 2 (Mengambil 1 dari 4 kolom = 25%) */}
        <div className="xl:col-span-1 w-full min-w-0">
          <DonutChart
            title="Method Popularity"
            description="Payment Sources"
            data={data?.method_popularity || []}
            dataKey="value"
            centerValue={`${topMethod.percentage}%`}
            centerLabel="Top Method"
            colors={methodColors}
          />
        </div>
      </div>
    </div>
  );
}
