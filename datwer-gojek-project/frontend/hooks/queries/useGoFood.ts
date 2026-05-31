import { useQuery } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";
import { GoFoodDashboardResponse } from "@/types/api";

export const useGoFoodSummary = () => {
  return useQuery<GoFoodDashboardResponse>({
    queryKey: ["gofood-summary"], // Cache key unik untuk GoFood
    queryFn: () => fetchAPI("/gofood/dashboard-summary"),
  });
};
