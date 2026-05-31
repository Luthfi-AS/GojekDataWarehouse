// ==========================================
// SHARED TYPES (Digunakan bersama)
// ==========================================
export interface KpiDetail {
  value: number;
  trend: number;
}

// ==========================================
// GO RIDE TYPES
// ==========================================
export interface GoRideKpis {
  total_trips: KpiDetail;
  total_distance: KpiDetail;
  avg_rating: KpiDetail;
  total_surge: KpiDetail;
}

export interface DailyTrend {
  date: string;
  volume: number;
}

export interface VehicleSplit {
  name: string;
  value: number;
  percentage: number;
}

export interface CityPerformance {
  city: string;
  volume: number;
  growth: number;
}

export interface GoRideDashboardResponse {
  kpis: GoRideKpis;
  daily_trend: DailyTrend[];
  vehicle_split: VehicleSplit[];
  city_performance: CityPerformance[];
}

// ==========================================
// GO FOOD TYPES
// ==========================================
export interface GoFoodKpis {
  total_revenue: KpiDetail;
  gross_profit: KpiDetail;
  total_promo: KpiDetail;
  avg_prep_time: KpiDetail;
}

export interface RevenueVsPromo {
  date: string;
  revenue: number;
  promo: number;
}

export interface CategorySplit {
  name: string;
  value: number;
  percentage: number;
}

export interface TopMerchant {
  rank: number;
  name: string;
  category: string;
  revenue: number;
  performance: number;
}

export interface GoFoodDashboardResponse {
  kpis: GoFoodKpis;
  revenue_vs_promo: RevenueVsPromo[];
  category_split: CategorySplit[];
  top_merchants: TopMerchant[];
}

// ==========================================
// GO PAY TYPES
// ==========================================
export interface GoPayKpis {
  gtv: KpiDetail;
  admin_fee: KpiDetail;
  cashback_burned: KpiDetail;
}

export interface RevenueVsBurn {
  date: string;
  revenue: number;
  burn: number;
}

// BARU: Menggantikan TransactionStatus
export interface TransactionTypeSplit {
  name: string;
  value: number;
  percentage: number;
}

export interface MethodPopularity {
  name: string;
  value: number;
  percentage: number;
}

export interface GoPayDashboardResponse {
  kpis: GoPayKpis;
  revenue_vs_burn: RevenueVsBurn[];
  transaction_type: TransactionTypeSplit[]; // <-- DIUBAH
  method_popularity: MethodPopularity[];
}
