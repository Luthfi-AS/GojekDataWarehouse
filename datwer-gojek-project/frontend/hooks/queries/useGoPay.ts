import { useQuery } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";
import { GoPayDashboardResponse } from "@/types/api";

export const useGoPaySummary = () => {
  return useQuery<GoPayDashboardResponse>({
    queryKey: ["gopay-summary"], // Cache key unik untuk GoPay
    queryFn: () => fetchAPI("/gopay/dashboard-summary"),
  });
};
