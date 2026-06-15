import { useQuery } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";
import { GoPayDashboardResponse, GoPayFilterOptions } from "@/types/api";

export interface GoPayFilters {
  days: number;
  paymentMethod: string; // "" berarti semua metode
  status: string; // "" berarti semua status
  volumeMin: number | null;
  volumeMax: number | null;
  cashbackMin: number | null;
  cashbackMax: number | null;
}

export const useGoPaySummary = (filters: GoPayFilters) => {
  return useQuery<GoPayDashboardResponse>({
    // Cache key menyertakan semua filter agar tiap kombinasi punya cache sendiri
    queryKey: [
      "gopay-summary",
      filters.days,
      filters.paymentMethod,
      filters.status,
      filters.volumeMin,
      filters.volumeMax,
      filters.cashbackMin,
      filters.cashbackMax,
    ],
    queryFn: () => {
      const params = new URLSearchParams({ days: String(filters.days) });
      if (filters.paymentMethod) params.set("payment_method", filters.paymentMethod);
      if (filters.status) params.set("status", filters.status);
      if (filters.volumeMin !== null) params.set("volume_min", String(filters.volumeMin));
      if (filters.volumeMax !== null) params.set("volume_max", String(filters.volumeMax));
      if (filters.cashbackMin !== null) params.set("cashback_min", String(filters.cashbackMin));
      if (filters.cashbackMax !== null) params.set("cashback_max", String(filters.cashbackMax));
      return fetchAPI(`/gopay/dashboard-summary?${params.toString()}`);
    },
  });
};

// Mengambil seluruh opsi filter (metode, status, rentang volume & cashback)
export const useGoPayFilters = () => {
  return useQuery<GoPayFilterOptions>({
    queryKey: ["gopay-filters"],
    queryFn: () => fetchAPI("/gopay/filters"),
    staleTime: 1000 * 60 * 60, // opsi filter jarang berubah
  });
};
