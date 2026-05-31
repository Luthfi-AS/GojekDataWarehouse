import { useQuery } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";
import { GoRideDashboardResponse } from "@/types/api";

export const useGoRideSummary = () => {
  return useQuery<GoRideDashboardResponse>({
    queryKey: ["goride-summary"], // Kunci cache
    queryFn: () => fetchAPI("/goride/dashboard-summary"), // Memanggil http://localhost:8000/api/goride/dashboard-summary
  });
};
