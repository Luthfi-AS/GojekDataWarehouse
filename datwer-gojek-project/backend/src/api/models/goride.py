from pydantic import BaseModel
from typing import List, Optional

# --- Sub-Models ---
class KpiDetail(BaseModel):
    value: float
    trend: float

class Kpis(BaseModel):
    total_trips: KpiDetail
    total_distance: KpiDetail
    avg_rating: KpiDetail
    total_surge: KpiDetail

class DailyTrend(BaseModel):
    date: str
    volume: int

class VehicleSplit(BaseModel):
    name: str
    value: int
    percentage: float

class CityPerformance(BaseModel):
    city: str
    volume: int
    growth: float

# --- Root Response Model ---
class GoRideDashboardResponse(BaseModel):
    kpis: Kpis
    daily_trend: List[DailyTrend]
    vehicle_split: List[VehicleSplit]
    city_performance: List[CityPerformance]