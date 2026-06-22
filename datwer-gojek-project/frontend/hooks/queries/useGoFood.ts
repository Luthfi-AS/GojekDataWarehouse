import { useQuery } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";
import { GoFoodDashboardResponse, GoFoodFilterOptions } from "@/types/api";

export interface GoFoodFilters {
  days: number;
  city: string; // "" berarti semua kota
  merchant: string; // "" berarti semua merchant
  category: string; // "" berarti semua kategori
  promoMin: number | null; // null berarti tanpa batas bawah
  promoMax: number | null; // null berarti tanpa batas atas
}

export const useGoFoodSummary = (filters: GoFoodFilters) => {
  return useQuery<GoFoodDashboardResponse>({
    // Cache key menyertakan semua filter agar tiap kombinasi punya cache sendiri
    queryKey: [
      "gofood-summary",
      filters.days,
      filters.city,
      filters.merchant,
      filters.category,
      filters.promoMin,
      filters.promoMax,
    ],
    queryFn: () => {
      const params = new URLSearchParams({ days: String(filters.days) });
      if (filters.city) params.set("city", filters.city);
      if (filters.merchant) params.set("merchant", filters.merchant);
      if (filters.category) params.set("category", filters.category);
      if (filters.promoMin !== null) params.set("promo_min", String(filters.promoMin));
      if (filters.promoMax !== null) params.set("promo_max", String(filters.promoMax));
      return fetchAPI(`/gofood/dashboard-summary?${params.toString()}`);
    },
  });
};

export const useGoFoodFilters = () => {
  return useQuery<GoFoodFilterOptions>({
    queryKey: ["gofood-filters"],
    queryFn: () => fetchAPI("/gofood/filters"),
    staleTime: 1000 * 60 * 60, // opsi filter jarang berubah
  });
};
