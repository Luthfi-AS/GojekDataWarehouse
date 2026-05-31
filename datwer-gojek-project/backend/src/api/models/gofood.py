from pydantic import BaseModel
from typing import List

# --- Sub-Models ---
class KpiDetail(BaseModel):
    value: float
    trend: float

class GoFoodKpis(BaseModel):
    total_revenue: KpiDetail
    gross_profit: KpiDetail
    total_promo: KpiDetail
    avg_prep_time: KpiDetail

class RevenueVsPromo(BaseModel):
    date: str
    revenue: float
    promo: float

class CategorySplit(BaseModel):
    name: str
    value: int
    percentage: float

class TopMerchant(BaseModel):
    rank: int
    name: str
    category: str
    revenue: float
    performance: int

# --- Root Response Model ---
class GoFoodDashboardResponse(BaseModel):
    kpis: GoFoodKpis
    revenue_vs_promo: List[RevenueVsPromo]
    category_split: List[CategorySplit]
    top_merchants: List[TopMerchant]