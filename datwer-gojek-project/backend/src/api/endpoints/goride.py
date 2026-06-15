from fastapi import APIRouter, Query
import logging
from typing import Dict, Any, List, Optional, Tuple

from src.shared.database import get_clickhouse_client

from src.api.models.goride import GoRideDashboardResponse, FilterOptionsResponse

router = APIRouter(prefix="/api/goride", tags=["GoRide Operations"])

# Preset rentang tanggal yang tersedia untuk dropdown filter
DATE_RANGE_OPTIONS = [
    {"label": "Last 7 Days", "days": 7},
    {"label": "Last 30 Days", "days": 30},
    {"label": "Last 90 Days", "days": 90},
]

def calc_trend(curr, prev):
    """Menghitung persentase pertumbuhan (growth)."""
    if not prev or prev == 0:
        return 0.0
    return round(((curr - prev) / prev) * 100, 1)

def _fetch_distinct(client, column: str) -> List[str]:
    """Ambil daftar nilai unik (non-kosong) dari satu kolom tabel GoRide."""
    result = client.query(
        f"SELECT DISTINCT {column} FROM olap_goride_ops_daily ORDER BY {column} ASC"
    ).result_rows
    return [row[0] for row in result if row[0]]

def _fetch_range(client, column: str) -> Tuple[float, float]:
    """Ambil nilai min & max satu kolom untuk batas slider filter."""
    result = client.query(
        f"SELECT min({column}), max({column}) FROM olap_goride_ops_daily"
    ).result_rows
    if result and result[0]:
        return float(result[0][0] or 0), float(result[0][1] or 0)
    return 0.0, 0.0

def _fetch_cities(client) -> List[str]:
    """Ambil daftar kota (jemputan) unik dari tabel GoRide."""
    return _fetch_distinct(client, "kota_jemputan")

def _build_filter_clause(
    params: Dict[str, Any],
    city: Optional[str],
    vehicle: Optional[str],
    rating_min: Optional[float],
    rating_max: Optional[float],
    surge_min: Optional[float],
    surge_max: Optional[float],
) -> str:
    """
    Bangun potongan klausa WHERE (selain rentang tanggal) berdasarkan filter aktif,
    sekaligus mengisi `params` untuk binding aman (mencegah SQL injection).
    """
    clauses: List[str] = []
    if city:
        params["city"] = city
        clauses.append("AND kota_jemputan = {city:String}")
    if vehicle:
        params["vehicle"] = vehicle
        clauses.append("AND jenis_kendaraan = {vehicle:String}")
    if rating_min is not None:
        params["rating_min"] = rating_min
        clauses.append("AND total_rating_driver >= {rating_min:Float64}")
    if rating_max is not None:
        params["rating_max"] = rating_max
        clauses.append("AND total_rating_driver <= {rating_max:Float64}")
    if surge_min is not None:
        params["surge_min"] = surge_min
        clauses.append("AND total_biaya_tambahan >= {surge_min:Float64}")
    if surge_max is not None:
        params["surge_max"] = surge_max
        clauses.append("AND total_biaya_tambahan <= {surge_max:Float64}")
    return " ".join(clauses)

@router.get("/cities", response_model=List[str])
async def get_goride_cities():
    """Daftar kota unik untuk dropdown filter dashboard GoRide."""
    try:
        client = get_clickhouse_client()
        return _fetch_cities(client)
    except Exception as e:
        logging.error(f"Gagal mengambil daftar kota GoRide: {str(e)}")
        return []

@router.get("/filters", response_model=FilterOptionsResponse)
async def get_goride_filters():
    """
    Opsi filter untuk dashboard GoRide dalam satu endpoint:
    preset rentang tanggal (date_ranges), daftar kota (cities), daftar jenis
    kendaraan (vehicle_types), serta batas rentang rating driver (rating_range)
    dan biaya tambahan/surge (surge_range).
    """
    cities: List[str] = []
    vehicle_types: List[str] = []
    rating_range = {"min": 0.0, "max": 0.0}
    surge_range = {"min": 0.0, "max": 0.0}
    try:
        client = get_clickhouse_client()
        cities = _fetch_cities(client)
        vehicle_types = _fetch_distinct(client, "jenis_kendaraan")
        r_min, r_max = _fetch_range(client, "total_rating_driver")
        rating_range = {"min": r_min, "max": r_max}
        s_min, s_max = _fetch_range(client, "total_biaya_tambahan")
        surge_range = {"min": s_min, "max": s_max}
    except Exception as e:
        logging.error(f"Gagal mengambil opsi filter GoRide: {str(e)}")

    return {
        "date_ranges": DATE_RANGE_OPTIONS,
        "cities": cities,
        "vehicle_types": vehicle_types,
        "rating_range": rating_range,
        "surge_range": surge_range,
    }

@router.get("/dashboard-summary", response_model=GoRideDashboardResponse)
async def get_goride_dashboard_summary(
    days: int = Query(30, ge=1, le=365, description="Rentang hari ke belakang (mis. 7, 30, 90)"),
    city: Optional[str] = Query(None, description="Filter kota jemputan. Kosongkan untuk semua kota."),
    vehicle: Optional[str] = Query(None, description="Filter jenis kendaraan. Kosongkan untuk semua."),
    rating_min: Optional[float] = Query(None, description="Batas bawah total rating driver (harian per baris)."),
    rating_max: Optional[float] = Query(None, description="Batas atas total rating driver (harian per baris)."),
    surge_min: Optional[float] = Query(None, description="Batas bawah total biaya tambahan/surge."),
    surge_max: Optional[float] = Query(None, description="Batas atas total biaya tambahan/surge."),
):
    """
    Mengambil data operasional GoRide dari ClickHouse.
    Difilter berdasarkan rentang `days` terakhir dan opsional `city`.
    Jika data tidak ditemukan atau terjadi error, mengembalikan nilai 0.
    """

    # 1. Siapkan Struktur Fallback (Default 0)
    response_data = {
        "kpis": {
            "total_trips": {"value": 0, "trend": 0.0},
            "total_distance": {"value": 0, "trend": 0.0},
            "avg_rating": {"value": 0, "trend": 0.0},
            "total_surge": {"value": 0, "trend": 0.0},
        },
        "daily_trend": [],
        "vehicle_split": [],
        "city_performance": []
    }

    # Parameter aman untuk query + klausa filter dinamis (city/vehicle/rating/surge)
    params: Dict[str, Any] = {"days": days, "days2": days * 2}
    filter_clause = _build_filter_clause(
        params, city, vehicle, rating_min, rating_max, surge_min, surge_max
    )

    try:
        # Inisiasi Client ClickHouse (Pastikan ini tidak di-comment!)
        client = get_clickhouse_client()

        # ==========================================
        # EKSEKUSI QUERY KE CLICKHOUSE
        # ==========================================

        # 1. KPIs
        kpi_query = f'''
        SELECT
            sumIf(total_perjalanan, tanggal >= today() - {{days:UInt32}}) AS trips_current,
            sumIf(total_perjalanan, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS trips_prev,
            sumIf(total_jarak_km, tanggal >= today() - {{days:UInt32}}) AS distance_current,
            sumIf(total_jarak_km, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS distance_prev,
            sumIf(total_biaya_tambahan, tanggal >= today() - {{days:UInt32}}) AS surge_current,
            sumIf(total_biaya_tambahan, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS surge_prev,
            sumIf(total_rating_driver, tanggal >= today() - {{days:UInt32}}) / nullIf(sumIf(total_perjalanan, tanggal >= today() - {{days:UInt32}}), 0) AS rating_current,
            sumIf(total_rating_driver, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) / nullIf(sumIf(total_perjalanan, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}), 0) AS rating_prev
        FROM olap_goride_ops_daily
        WHERE tanggal >= today() - {{days2:UInt32}} {filter_clause}
        '''
        kpi_result = client.query(kpi_query, parameters=params).result_rows

        if kpi_result and kpi_result[0]:
            row = kpi_result[0]
            t_curr, t_prev = row[0] or 0, row[1] or 0
            d_curr, d_prev = row[2] or 0, row[3] or 0
            s_curr, s_prev = row[4] or 0, row[5] or 0
            r_curr, r_prev = row[6] or 0, row[7] or 0

            response_data["kpis"]["total_trips"] = {"value": t_curr, "trend": calc_trend(t_curr, t_prev)}
            response_data["kpis"]["total_distance"] = {"value": d_curr, "trend": calc_trend(d_curr, d_prev)}
            response_data["kpis"]["total_surge"] = {"value": s_curr, "trend": calc_trend(s_curr, s_prev)}
            response_data["kpis"]["avg_rating"] = {"value": round(r_curr, 2), "trend": round(r_curr - r_prev, 2)}

        # 2. Daily Trend
        trend_query = f'''
        SELECT formatDateTime(tanggal, '%b %d') AS date, sum(total_perjalanan) AS volume
        FROM olap_goride_ops_daily
        WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}
        GROUP BY tanggal ORDER BY tanggal ASC
        '''
        trend_result = client.query(trend_query, parameters=params).result_rows
        for row in trend_result:
            response_data["daily_trend"].append({"date": row[0], "volume": row[1] or 0})

        # 3. Vehicle Split
        vehicle_query = f'''
        WITH (SELECT sum(total_perjalanan) FROM olap_goride_ops_daily WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}) AS total_all
        SELECT jenis_kendaraan AS name, sum(total_perjalanan) AS value,
               round((sum(total_perjalanan) / nullIf(total_all, 0)) * 100, 1) AS percentage
        FROM olap_goride_ops_daily
        WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}
        GROUP BY jenis_kendaraan ORDER BY value DESC
        '''
        vehicle_result = client.query(vehicle_query, parameters=params).result_rows
        for row in vehicle_result:
            response_data["vehicle_split"].append({"name": row[0], "value": row[1] or 0, "percentage": row[2] or 0.0})

        # 4. City Performance
        city_query = f'''
        SELECT kota_jemputan AS city,
               sumIf(total_perjalanan, tanggal >= today() - {{days:UInt32}}) AS volume_current,
               sumIf(total_perjalanan, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS volume_prev,
               round(((volume_current - volume_prev) / nullIf(volume_prev, 0)) * 100, 1) AS growth
        FROM olap_goride_ops_daily
        WHERE tanggal >= today() - {{days2:UInt32}} {filter_clause}
        GROUP BY kota_jemputan ORDER BY volume_current DESC LIMIT 5
        '''
        city_result = client.query(city_query, parameters=params).result_rows
        for row in city_result:
            response_data["city_performance"].append({"city": row[0], "volume": row[1] or 0, "growth": row[3] or 0.0})

    except Exception as e:
        logging.error(f"Gagal mengambil data dari ClickHouse: {str(e)}")

    return response_data
