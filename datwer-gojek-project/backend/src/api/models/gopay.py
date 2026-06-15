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

# --- Filter Options Models ---
# Catatan: tabel finance GoPay tidak punya dimensi kota, jadi tidak ada filter kota.
class DateRangeOption(BaseModel):
    label: str
    days: int

class NumericRange(BaseModel):
    min: float
    max: float

class FilterOptionsResponse(BaseModel):
    date_ranges: List[DateRangeOption]
    payment_methods: List[str]
    transaction_statuses: List[str]
    volume_range: NumericRange
    cashback_range: NumericRange
