import { useQuery } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";
import { GoRideDashboardResponse, GoRideFilterOptions } from "@/types/api";

export interface GoRideFilters {
  days: number;
  city: string; // "" berarti semua kota
  vehicle: string; // "" berarti semua jenis kendaraan
  ratingMin: number | null; // null berarti tanpa batas bawah
  ratingMax: number | null; // null berarti tanpa batas atas
  surgeMin: number | null;
  surgeMax: number | null;
}

export const useGoRideSummary = (filters: GoRideFilters) => {
  return useQuery<GoRideDashboardResponse>({
    // Cache key menyertakan semua filter agar tiap kombinasi punya cache sendiri
    queryKey: [
      "goride-summary",
      filters.days,
      filters.city,
      filters.vehicle,
      filters.ratingMin,
      filters.ratingMax,
      filters.surgeMin,
      filters.surgeMax,
    ],
    queryFn: () => {
      const params = new URLSearchParams({ days: String(filters.days) });
      if (filters.city) params.set("city", filters.city);
      if (filters.vehicle) params.set("vehicle", filters.vehicle);
      if (filters.ratingMin !== null) params.set("rating_min", String(filters.ratingMin));
      if (filters.ratingMax !== null) params.set("rating_max", String(filters.ratingMax));
      if (filters.surgeMin !== null) params.set("surge_min", String(filters.surgeMin));
      if (filters.surgeMax !== null) params.set("surge_max", String(filters.surgeMax));
      return fetchAPI(`/goride/dashboard-summary?${params.toString()}`);
    },
  });
};

// Mengambil seluruh opsi filter (kota, jenis kendaraan, rentang rating & surge)
export const useGoRideFilters = () => {
  return useQuery<GoRideFilterOptions>({
    queryKey: ["goride-filters"],
    queryFn: () => fetchAPI("/goride/filters"),
    staleTime: 1000 * 60 * 60, // opsi filter jarang berubah
  });
};
