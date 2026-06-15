"use client";

import { useState } from "react";
import { CheckCircle2, Route, Star, Banknote, Car } from "lucide-react";

// Import Komponen Reusable
import PageHeader from "@/components/layout/PageHeader";
import KpiCard from "@/components/dashboard/KpiCard";
import TrendAreaChart from "@/components/dashboard/TrendAreaChart";
import DonutChart from "@/components/dashboard/DonutChart";
import ProgressBarList from "@/components/dashboard/ProgressBarList";

// Import Custom Hook TanStack Query
import { useGoRideSummary, useGoRideFilters } from "@/hooks/queries/useGoRide";

// Formatters
const formatCompact = (num: number) =>
  new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(num);

export default function GoRideDashboard() {
  // State 5 filter: rentang hari, kota, jenis kendaraan, rentang rating & surge
  const [days, setDays] = useState(30);
  const [city, setCity] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [ratingMin, setRatingMin] = useState<number | null>(null);
  const [ratingMax, setRatingMax] = useState<number | null>(null);
  const [surgeMin, setSurgeMin] = useState<number | null>(null);
  const [surgeMax, setSurgeMax] = useState<number | null>(null);

  // Mengambil data dari Backend menggunakan TanStack Query (re-fetch saat filter berubah)
  const { data, isLoading, isError } = useGoRideSummary({
    days,
    city,
    vehicle,
    ratingMin,
    ratingMax,
    surgeMin,
    surgeMax,
  });
  const { data: filterOptions } = useGoRideFilters();

  // Handle Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-theme-base p-8 flex items-center justify-center">
        <div className="text-theme-muted font-medium animate-pulse">
          Mengambil data dari server...
        </div>
      </div>
    );
  }

  // Handle Error State
  if (isError || !data) {
    return (
      <div className="min-h-screen bg-theme-base p-8 flex items-center justify-center">
        <div className="text-error font-medium">
          Gagal terhubung ke server. Pastikan API FastAPI di port 8000 sudah
          berjalan.
        </div>
      </div>
    );
  }

  // Transformasi array agar sesuai dengan props komponen yang generik
  const cityDataForList = data.city_performance.map((c) => ({
    name: c.city,
    volume: c.volume,
    growth: c.growth,
  }));

  return (
    <div className="min-h-screen bg-theme-base p-8 pb-20">
      {/* 1. HEADER */}
      <PageHeader
        title="GoRide Operations Performance"
        description="Real-time analytical overview of transportation logistics."
        days={days}
        onDaysChange={setDays}
        city={city}
        onCityChange={setCity}
        cities={filterOptions?.cities ?? []}
        selectFilters={[
          {
            key: "vehicle",
            label: "All Vehicles",
            value: vehicle,
            options: filterOptions?.vehicle_types ?? [],
            onChange: setVehicle,
            icon: <Car className="w-4 h-4 mr-2 text-theme-muted" />,
          },
        ]}
        rangeFilters={[
          {
            key: "rating",
            label: "Rating",
            min: filterOptions?.rating_range.min ?? 0,
            max: filterOptions?.rating_range.max ?? 0,
            valueMin: ratingMin,
            valueMax: ratingMax,
            onChange: (min, max) => {
              setRatingMin(min);
              setRatingMax(max);
            },
          },
          {
            key: "surge",
            label: "Surge",
            min: filterOptions?.surge_range.min ?? 0,
            max: filterOptions?.surge_range.max ?? 0,
            valueMin: surgeMin,
            valueMax: surgeMax,
            onChange: (min, max) => {
              setSurgeMin(min);
              setSurgeMax(max);
            },
          },
        ]}
      />

      {/* 2. KPI SCORECARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <KpiCard
          title={"Total Successful\nTrips"}
          value={formatCompact(data.kpis.total_trips.value)}
          trend={data.kpis.total_trips.trend}
          trendLabel="vs. last 30d"
          icon={<CheckCircle2 className="w-5 h-5" />}
        />
        <KpiCard
          title="Total Distance"
          value={`${formatCompact(data.kpis.total_distance.value)} KM`}
          trend={data.kpis.total_distance.trend}
          trendLabel="vs. last 30d"
          icon={<Route className="w-5 h-5" />}
        />
        <KpiCard
          title="Avg Driver Rating"
          value={data.kpis.avg_rating.value}
          trend={data.kpis.avg_rating.trend}
          trendLabel="Target: 4.70"
          icon={<Star className="w-5 h-5" />}
        />
        <KpiCard
          title="Total Surge Pricing"
          value={`Rp ${formatCompact(data.kpis.total_surge.value)}`}
          trend={data.kpis.total_surge.trend}
          trendLabel="Optimization impact"
          icon={<Banknote className="w-5 h-5" />}
        />
      </div>

      {/* 3. CHARTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <TrendAreaChart
          title="Daily Trip Volume Trend"
          description="30-day transactional cycle"
          data={data.daily_trend}
          dataKey="volume"
          valueSuffix="Trips"
        />

        <DonutChart
          title="Vehicle Type Comparison"
          description="Active fleet distribution"
          data={data.vehicle_split}
          dataKey="value"
          centerValue={formatCompact(data.kpis.total_trips.value)}
          centerLabel="Trips"
        />
      </div>

      {/* 4. CITY PROGRESS LIST */}
      <ProgressBarList
        title="Total Trips by Pickup City"
        description="Regional performance benchmarks"
        data={cityDataForList}
      />
    </div>
  );
}
