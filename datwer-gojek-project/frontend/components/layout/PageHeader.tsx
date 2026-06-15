"use client";

import React, { useState, useEffect } from "react";
import {
  Calendar,
  MapPin,
  Download,
  Sun,
  Moon,
  Tag,
  SlidersHorizontal,
  ChevronDown,
} from "lucide-react";

interface DateRangeOption {
  label: string;
  days: number;
}

// Konfigurasi dropdown filter generik (mis. merchant, kategori)
export interface SelectFilterConfig {
  key: string;
  label: string; // teks opsi "semua", mis. "All Merchants"
  value: string; // "" berarti semua
  options: string[];
  onChange: (value: string) => void;
  icon?: React.ReactNode;
}

// Konfigurasi filter rentang angka (mis. total diskon promo)
export interface RangeFilterConfig {
  key: string;
  label: string; // mis. "Promo"
  min: number; // batas bawah data
  max: number; // batas atas data
  valueMin: number | null;
  valueMax: number | null;
  onChange: (min: number | null, max: number | null) => void;
  icon?: React.ReactNode;
}

interface PageHeaderProps {
  title: string;
  description: string;
  // Filter (opsional). Jika tidak ada satupun filter, tombol statis lama tampil.
  days?: number;
  onDaysChange?: (days: number) => void;
  city?: string; // "" berarti semua kota
  onCityChange?: (city: string) => void;
  cities?: string[];
  selectFilters?: SelectFilterConfig[];
  rangeFilters?: RangeFilterConfig[];
}

const DATE_RANGE_OPTIONS: DateRangeOption[] = [
  { label: "Last 7 Days", days: 7 },
  { label: "Last 30 Days", days: 30 },
  { label: "Last 90 Days", days: 90 },
];

// Wrapper select bergaya senada dengan tombol filter lama
const selectClasses =
  "appearance-none bg-transparent text-sm font-medium text-theme-main focus:outline-none cursor-pointer pr-1 max-w-[12rem]";
const filterShellClasses =
  "flex items-center px-4 py-2 bg-theme-card border border-theme-border rounded-md shadow-sm hover:opacity-80 transition-opacity";

const formatCompact = (num: number) =>
  new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(num);

// Dropdown filter rentang angka dengan dua input (min & max)
function RangeFilterDropdown({ config }: { config: RangeFilterConfig }) {
  const [open, setOpen] = useState(false);
  const [localMin, setLocalMin] = useState("");
  const [localMax, setLocalMax] = useState("");

  // Sinkronkan input lokal saat nilai eksternal berubah (mis. setelah reset)
  useEffect(() => {
    setLocalMin(config.valueMin?.toString() ?? "");
    setLocalMax(config.valueMax?.toString() ?? "");
  }, [config.valueMin, config.valueMax]);

  const hasValue = config.valueMin !== null || config.valueMax !== null;
  const summary = hasValue
    ? `${formatCompact(config.valueMin ?? config.min)}–${formatCompact(
        config.valueMax ?? config.max,
      )}`
    : "All";

  const apply = () => {
    const min = localMin.trim() === "" ? null : Number(localMin);
    const max = localMax.trim() === "" ? null : Number(localMax);
    config.onChange(min, max);
    setOpen(false);
  };

  const reset = () => {
    setLocalMin("");
    setLocalMax("");
    config.onChange(null, null);
    setOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className={`${filterShellClasses} text-sm font-medium text-theme-main`}
      >
        {config.icon ?? (
          <SlidersHorizontal className="w-4 h-4 mr-2 text-theme-muted" />
        )}
        <span className="mr-1">{config.label}:</span>
        <span className="text-theme-muted">{summary}</span>
        <ChevronDown className="w-3.5 h-3.5 ml-2 text-theme-muted" />
      </button>

      {open && (
        <>
          {/* Backdrop untuk menutup saat klik di luar */}
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 w-64 bg-theme-card border border-theme-border rounded-md shadow-lg p-4 z-20">
            <p className="text-xs text-theme-muted mb-2">
              Range {formatCompact(config.min)} – {formatCompact(config.max)}
            </p>
            <div className="flex items-center gap-2 mb-3">
              <input
                type="number"
                value={localMin}
                placeholder={formatCompact(config.min)}
                onChange={(e) => setLocalMin(e.target.value)}
                className="w-full px-2 py-1.5 bg-theme-base border border-theme-border rounded text-sm text-theme-main focus:outline-none"
                aria-label={`${config.label} minimum`}
              />
              <span className="text-theme-muted">–</span>
              <input
                type="number"
                value={localMax}
                placeholder={formatCompact(config.max)}
                onChange={(e) => setLocalMax(e.target.value)}
                className="w-full px-2 py-1.5 bg-theme-base border border-theme-border rounded text-sm text-theme-main focus:outline-none"
                aria-label={`${config.label} maximum`}
              />
            </div>
            <div className="flex items-center justify-between">
              <button
                onClick={reset}
                className="text-sm text-theme-muted hover:text-theme-main"
              >
                Reset
              </button>
              <button
                onClick={apply}
                className="px-3 py-1.5 bg-theme-main text-theme-base rounded text-sm font-medium hover:opacity-90"
              >
                Apply
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default function PageHeader({
  title,
  description,
  days,
  onDaysChange,
  city,
  onCityChange,
  cities = [],
  selectFilters = [],
  rangeFilters = [],
}: PageHeaderProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (document.documentElement.classList.contains("dark")) {
      setIsDarkMode(true);
    }
  }, []);

  const toggleTheme = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove("dark");
      setIsDarkMode(false);
    } else {
      document.documentElement.classList.add("dark");
      setIsDarkMode(true);
    }
  };

  const showDateFilter = Boolean(onDaysChange);
  const showCityFilter = Boolean(onCityChange);
  const filtersEnabled =
    showDateFilter ||
    showCityFilter ||
    selectFilters.length > 0 ||
    rangeFilters.length > 0;

  return (
    <div className="flex flex-col md:flex-row md:items-start justify-between mb-8 gap-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-theme-main">
          {title}
        </h1>
        <p className="text-sm text-theme-muted mt-1">{description}</p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        {filtersEnabled ? (
          <>
            {/* DATE RANGE FILTER */}
            {showDateFilter && (
              <div className={filterShellClasses}>
                <Calendar className="w-4 h-4 mr-2 text-theme-muted" />
                <select
                  value={days ?? 30}
                  onChange={(e) => onDaysChange?.(Number(e.target.value))}
                  className={selectClasses}
                  aria-label="Date range filter"
                >
                  {DATE_RANGE_OPTIONS.map((opt) => (
                    <option key={opt.days} value={opt.days}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* CITY FILTER (hanya tampil bila halaman menyediakan onCityChange) */}
            {showCityFilter && (
              <div className={filterShellClasses}>
                <MapPin className="w-4 h-4 mr-2 text-theme-muted" />
                <select
                  value={city ?? ""}
                  onChange={(e) => onCityChange?.(e.target.value)}
                  className={selectClasses}
                  aria-label="City filter"
                >
                  <option value="">All Cities</option>
                  {cities.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* DROPDOWN FILTER GENERIK (merchant, kategori, dll.) */}
            {selectFilters.map((sf) => (
              <div key={sf.key} className={filterShellClasses}>
                {sf.icon ?? <Tag className="w-4 h-4 mr-2 text-theme-muted" />}
                <select
                  value={sf.value}
                  onChange={(e) => sf.onChange(e.target.value)}
                  className={selectClasses}
                  aria-label={sf.label}
                >
                  <option value="">{sf.label}</option>
                  {sf.options.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              </div>
            ))}

            {/* FILTER RENTANG ANGKA (mis. total diskon promo) */}
            {rangeFilters.map((rf) => (
              <RangeFilterDropdown key={rf.key} config={rf} />
            ))}
          </>
        ) : (
          <>
            <button className={`${filterShellClasses} text-sm font-medium text-theme-main`}>
              <Calendar className="w-4 h-4 mr-2 text-theme-muted" />
              Last 30 Days
            </button>
            <button className={`${filterShellClasses} text-sm font-medium text-theme-main`}>
              <MapPin className="w-4 h-4 mr-2 text-theme-muted" />
              All Cities
            </button>
          </>
        )}

        <button className="flex items-center px-4 py-2 bg-theme-main text-theme-base rounded-md text-sm font-medium shadow-sm hover:opacity-90 transition-opacity">
          <Download className="w-4 h-4 mr-2" />
          Export
        </button>

        <button
          onClick={toggleTheme}
          className="flex items-center justify-center p-2.5 bg-theme-card border border-theme-border rounded-md text-theme-muted hover:text-theme-main shadow-sm transition-all"
        >
          {isDarkMode ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
        </button>
      </div>
    </div>
  );
}
