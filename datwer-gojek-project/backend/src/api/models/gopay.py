from pydantic import BaseModel
from typing import List

# --- Sub-Models ---
class KpiDetail(BaseModel):
    value: float
    trend: float

class GoPayKpis(BaseModel):
    gtv: KpiDetail
    admin_fee: KpiDetail
    cashback_burned: KpiDetail

class RevenueVsBurn(BaseModel):
    date: str
    revenue: float
    burn: float

# MENGGANTIKAN TransactionStatus
class TransactionTypeSplit(BaseModel):
    name: str
    value: int
    percentage: float

class MethodPopularity(BaseModel):
    name: str
    value: int
    percentage: float

# --- Root Response Model ---
class GoPayDashboardResponse(BaseModel):
    kpis: GoPayKpis
    revenue_vs_burn: List[RevenueVsBurn]
    transaction_type: List[TransactionTypeSplit] # <-- DIUBAH
    method_popularity: List[MethodPopularity]