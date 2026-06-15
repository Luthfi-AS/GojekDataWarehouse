from fastapi import APIRouter, Query
import logging
from typing import Dict, Any, List, Optional, Tuple

from src.shared.database import get_clickhouse_client
from src.api.models.gofood import GoFoodDashboardResponse, FilterOptionsResponse

router = APIRouter(prefix="/api/gofood", tags=["GoFood & Merchant Operations"])

# Preset rentang tanggal yang tersedia untuk dropdown filter
DATE_RANGE_OPTIONS = [
    {"label": "Last 7 Days", "days": 7},
    {"label": "Last 30 Days", "days": 30},
    {"label": "Last 90 Days", "days": 90},
]

def calc_trend(curr, prev):
    if not prev or prev == 0:
        return 0.0
    return round(((curr - prev) / prev) * 100, 1)

def _fetch_distinct(client, column: str) -> List[str]:
    """Ambil daftar nilai unik (non-kosong) dari satu kolom tabel GoFood."""
    result = client.query(
        f"SELECT DISTINCT {column} FROM olap_gofood_merchant_daily ORDER BY {column} ASC"
    ).result_rows
    return [row[0] for row in result if row[0]]

def _fetch_promo_range(client) -> Tuple[float, float]:
    """Ambil nilai min & max total_diskon_promo untuk batas slider filter."""
    result = client.query(
        "SELECT min(total_diskon_promo), max(total_diskon_promo) FROM olap_gofood_merchant_daily"
    ).result_rows
    if result and result[0]:
        return float(result[0][0] or 0), float(result[0][1] or 0)
    return 0.0, 0.0

def _fetch_cities(client) -> List[str]:
    """Ambil daftar kota unik dari tabel GoFood."""
    return _fetch_distinct(client, "kota")

def _build_filter_clause(
    params: Dict[str, Any],
    city: Optional[str],
    merchant: Optional[str],
    category: Optional[str],
    promo_min: Optional[float],
    promo_max: Optional[float],
) -> str:
    """
    Bangun potongan klausa WHERE (selain rentang tanggal) berdasarkan filter aktif,
    sekaligus mengisi `params` untuk binding aman (mencegah SQL injection).
    """
    clauses: List[str] = []
    if city:
        params["city"] = city
        clauses.append("AND kota = {city:String}")
    if merchant:
        params["merchant"] = merchant
        clauses.append("AND nama_merchant = {merchant:String}")
    if category:
        params["category"] = category
        clauses.append("AND kategori_bisnis = {category:String}")
    if promo_min is not None:
        params["promo_min"] = promo_min
        clauses.append("AND total_diskon_promo >= {promo_min:Float64}")
    if promo_max is not None:
        params["promo_max"] = promo_max
        clauses.append("AND total_diskon_promo <= {promo_max:Float64}")
    return " ".join(clauses)

@router.get("/cities", response_model=List[str])
async def get_gofood_cities():
    """Daftar kota unik untuk dropdown filter dashboard GoFood."""
    try:
        client = get_clickhouse_client()
        return _fetch_cities(client)
    except Exception as e:
        logging.error(f"Gagal mengambil daftar kota GoFood: {str(e)}")
        return []

@router.get("/filters", response_model=FilterOptionsResponse)
async def get_gofood_filters():
    """
    Opsi filter untuk dashboard GoFood dalam satu endpoint:
    preset rentang tanggal (date_ranges), daftar kota (cities), daftar merchant
    (merchants), daftar kategori bisnis (categories), dan batas rentang diskon
    promo (promo_range). Dipakai frontend untuk mengisi semua dropdown filter.
    """
    cities: List[str] = []
    merchants: List[str] = []
    categories: List[str] = []
    promo_range = {"min": 0.0, "max": 0.0}
    try:
        client = get_clickhouse_client()
        cities = _fetch_cities(client)
        merchants = _fetch_distinct(client, "nama_merchant")
        categories = _fetch_distinct(client, "kategori_bisnis")
        p_min, p_max = _fetch_promo_range(client)
        promo_range = {"min": p_min, "max": p_max}
    except Exception as e:
        logging.error(f"Gagal mengambil opsi filter GoFood: {str(e)}")

    return {
        "date_ranges": DATE_RANGE_OPTIONS,
        "cities": cities,
        "merchants": merchants,
        "categories": categories,
        "promo_range": promo_range,
    }

@router.get("/dashboard-summary", response_model=GoFoodDashboardResponse)
async def get_gofood_dashboard_summary(
    days: int = Query(30, ge=1, le=365, description="Rentang hari ke belakang (mis. 7, 30, 90)"),
    city: Optional[str] = Query(None, description="Filter kota. Kosongkan untuk semua kota."),
    merchant: Optional[str] = Query(None, description="Filter nama merchant. Kosongkan untuk semua."),
    category: Optional[str] = Query(None, description="Filter kategori bisnis. Kosongkan untuk semua."),
    promo_min: Optional[float] = Query(None, description="Batas bawah total diskon promo (harian per merchant)."),
    promo_max: Optional[float] = Query(None, description="Batas atas total diskon promo (harian per merchant)."),
):
    """
    Mengambil data analitik GoFood dari ClickHouse.
    Difilter berdasarkan rentang `days` terakhir, serta opsional `city`,
    `merchant`, `category`, dan rentang `promo_min`..`promo_max`.
    Mengembalikan nilai 0 jika tabel kosong atau koneksi gagal.
    """

    # 1. Fallback Aman (Semua bernilai 0)
    response_data = {
        "kpis": {
            "total_revenue": {"value": 0, "trend": 0.0},
            "gross_profit": {"value": 0, "trend": 0.0},
            "total_promo": {"value": 0, "trend": 0.0},
            "avg_prep_time": {"value": 0, "trend": 0.0},
        },
        "revenue_vs_promo": [],
        "category_split": [],
        "top_merchants": []
    }

    # Parameter aman untuk query + klausa filter dinamis (city/merchant/category/promo)
    params: Dict[str, Any] = {"days": days, "days2": days * 2}
    filter_clause = _build_filter_clause(params, city, merchant, category, promo_min, promo_max)

    try:
        client = get_clickhouse_client()

        # ==========================================
        # 1. QUERY KPIs
        # ==========================================
        kpi_query = f'''
        SELECT
            sumIf(total_pendapatan_kotor, tanggal >= today() - {{days:UInt32}}) AS rev_curr,
            sumIf(total_pendapatan_kotor, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS rev_prev,
            sumIf(total_laba_kotor_gojek, tanggal >= today() - {{days:UInt32}}) AS prof_curr,
            sumIf(total_laba_kotor_gojek, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS prof_prev,
            sumIf(total_diskon_promo, tanggal >= today() - {{days:UInt32}}) AS promo_curr,
            sumIf(total_diskon_promo, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS promo_prev,
            avgIf(rata_rata_waktu_persiapan, tanggal >= today() - {{days:UInt32}}) AS prep_curr,
            avgIf(rata_rata_waktu_persiapan, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS prep_prev
        FROM olap_gofood_merchant_daily
        WHERE tanggal >= today() - {{days2:UInt32}} {filter_clause}
        '''
        kpi_result = client.query(kpi_query, parameters=params).result_rows

        if kpi_result and kpi_result[0]:
            row = kpi_result[0]
            rev_curr, rev_prev = row[0] or 0, row[1] or 0
            prof_curr, prof_prev = row[2] or 0, row[3] or 0
            promo_curr, promo_prev = row[4] or 0, row[5] or 0
            prep_curr, prep_prev = row[6] or 0, row[7] or 0

            response_data["kpis"]["total_revenue"] = {"value": rev_curr, "trend": calc_trend(rev_curr, rev_prev)}
            response_data["kpis"]["gross_profit"] = {"value": prof_curr, "trend": calc_trend(prof_curr, prof_prev)}
            response_data["kpis"]["total_promo"] = {"value": promo_curr, "trend": calc_trend(promo_curr, promo_prev)}
            response_data["kpis"]["avg_prep_time"] = {"value": round(prep_curr, 1), "trend": round(prep_curr - prep_prev, 1)}

        # ==========================================
        # 2. QUERY DUAL LINE CHART (Revenue vs Promo)
        # ==========================================
        trend_query = f'''
        SELECT formatDateTime(tanggal, '%b %d') AS date,
               sum(total_pendapatan_kotor) AS revenue,
               sum(total_diskon_promo) AS promo
        FROM olap_gofood_merchant_daily
        WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}
        GROUP BY tanggal ORDER BY tanggal ASC
        '''
        trend_result = client.query(trend_query, parameters=params).result_rows
        for row in trend_result:
            response_data["revenue_vs_promo"].append({
                "date": row[0],
                "revenue": row[1] or 0,
                "promo": row[2] or 0
            })

        # ==========================================
        # 3. QUERY CATEGORY SPLIT (Donut Chart)
        # ==========================================
        # Menggunakan uniqExact untuk menghitung jumlah merchant unik per kategori
        cat_query = f'''
        WITH (SELECT uniqExact(nama_merchant) FROM olap_gofood_merchant_daily WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}) AS total_merchants
        SELECT kategori_bisnis AS name,
               uniqExact(nama_merchant) AS value,
               round((uniqExact(nama_merchant) / nullIf(total_merchants, 0)) * 100, 1) AS percentage
        FROM olap_gofood_merchant_daily
        WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}
        GROUP BY kategori_bisnis ORDER BY value DESC
        '''
        cat_result = client.query(cat_query, parameters=params).result_rows
        for row in cat_result:
            response_data["category_split"].append({
                "name": row[0],
                "value": row[1] or 0,
                "percentage": row[2] or 0.0
            })

        # ==========================================
        # 4. QUERY TOP MERCHANTS TABLE
        # ==========================================
        top_query = f'''
        SELECT concat(nama_merchant, ', ', kota) AS name,
               kategori_bisnis AS category,
               sum(total_pendapatan_kotor) AS revenue
        FROM olap_gofood_merchant_daily
        WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}
        GROUP BY nama_merchant, kota, kategori_bisnis
        ORDER BY revenue DESC
        LIMIT 5
        '''
        top_result = client.query(top_query, parameters=params).result_rows

        # Kalkulasi performance secara dinamis berdasarkan pendapatan tertinggi (Rank 1 = 100%)
        max_rev = top_result[0][2] if top_result and top_result[0][2] else 1

        for idx, row in enumerate(top_result):
            current_rev = row[2] or 0
            performance = int((current_rev / max_rev) * 100) if max_rev > 0 else 0

            response_data["top_merchants"].append({
                "rank": idx + 1,
                "name": row[0],
                "category": row[1],
                "revenue": current_rev, # Frontend akan memformat ini menggunakan formatCompact/formatCurrency
                "performance": performance
            })

    except Exception as e:
        logging.error(f"Gagal mengambil data GoFood dari ClickHouse: {str(e)}")

    return response_data
