from fastapi import APIRouter, Query
import logging
from typing import Dict, Any, List, Optional, Tuple

from src.shared.database import get_clickhouse_client
from src.api.models.gopay import GoPayDashboardResponse, FilterOptionsResponse

router = APIRouter(prefix="/api/gopay", tags=["GoPay Financial Ledger"])

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
    """Ambil daftar nilai unik (non-kosong) dari satu kolom tabel GoPay."""
    result = client.query(
        f"SELECT DISTINCT {column} FROM olap_gopay_finance_daily ORDER BY {column} ASC"
    ).result_rows
    return [row[0] for row in result if row[0]]


def _fetch_range(client, column: str) -> Tuple[float, float]:
    """Ambil nilai min & max satu kolom untuk batas slider filter."""
    result = client.query(
        f"SELECT min({column}), max({column}) FROM olap_gopay_finance_daily"
    ).result_rows
    if result and result[0]:
        return float(result[0][0] or 0), float(result[0][1] or 0)
    return 0.0, 0.0


def _build_filter_clause(
    params: Dict[str, Any],
    payment_method: Optional[str],
    status: Optional[str],
    volume_min: Optional[float],
    volume_max: Optional[float],
    cashback_min: Optional[float],
    cashback_max: Optional[float],
) -> str:
    """
    Bangun potongan klausa WHERE (selain rentang tanggal) berdasarkan filter aktif,
    sekaligus mengisi `params` untuk binding aman (mencegah SQL injection).
    """
    clauses: List[str] = []
    if payment_method:
        params["payment_method"] = payment_method
        clauses.append("AND metode_pembayaran = {payment_method:String}")
    if status:
        params["status"] = status
        clauses.append("AND status_transaksi = {status:String}")
    if volume_min is not None:
        params["volume_min"] = volume_min
        clauses.append("AND total_volume_transaksi >= {volume_min:Float64}")
    if volume_max is not None:
        params["volume_max"] = volume_max
        clauses.append("AND total_volume_transaksi <= {volume_max:Float64}")
    if cashback_min is not None:
        params["cashback_min"] = cashback_min
        clauses.append("AND total_cashback_dibakar >= {cashback_min:Float64}")
    if cashback_max is not None:
        params["cashback_max"] = cashback_max
        clauses.append("AND total_cashback_dibakar <= {cashback_max:Float64}")
    return " ".join(clauses)


@router.get("/filters", response_model=FilterOptionsResponse)
async def get_gopay_filters():
    """
    Opsi filter untuk dashboard GoPay dalam satu endpoint: preset rentang tanggal
    (date_ranges), daftar metode pembayaran (payment_methods) & status transaksi
    (transaction_statuses), serta batas rentang volume transaksi (volume_range)
    dan cashback dibakar (cashback_range). GoPay tidak punya dimensi kota.
    """
    payment_methods: List[str] = []
    transaction_statuses: List[str] = []
    volume_range = {"min": 0.0, "max": 0.0}
    cashback_range = {"min": 0.0, "max": 0.0}
    try:
        client = get_clickhouse_client()
        payment_methods = _fetch_distinct(client, "metode_pembayaran")
        transaction_statuses = _fetch_distinct(client, "status_transaksi")
        v_min, v_max = _fetch_range(client, "total_volume_transaksi")
        volume_range = {"min": v_min, "max": v_max}
        c_min, c_max = _fetch_range(client, "total_cashback_dibakar")
        cashback_range = {"min": c_min, "max": c_max}
    except Exception as e:
        logging.error(f"Gagal mengambil opsi filter GoPay: {str(e)}")

    return {
        "date_ranges": DATE_RANGE_OPTIONS,
        "payment_methods": payment_methods,
        "transaction_statuses": transaction_statuses,
        "volume_range": volume_range,
        "cashback_range": cashback_range,
    }


@router.get("/dashboard-summary", response_model=GoPayDashboardResponse)
async def get_gopay_dashboard_summary(
    days: int = Query(
        30, ge=1, le=365, description="Rentang hari ke belakang (mis. 7, 30, 90)"
    ),
    payment_method: Optional[str] = Query(
        None, description="Filter metode pembayaran. Kosongkan untuk semua."
    ),
    status: Optional[str] = Query(
        None, description="Filter status transaksi. Kosongkan untuk semua."
    ),
    volume_min: Optional[float] = Query(
        None, description="Batas bawah total volume transaksi (harian per baris)."
    ),
    volume_max: Optional[float] = Query(
        None, description="Batas atas total volume transaksi (harian per baris)."
    ),
    cashback_min: Optional[float] = Query(
        None, description="Batas bawah total cashback dibakar."
    ),
    cashback_max: Optional[float] = Query(
        None, description="Batas atas total cashback dibakar."
    ),
):
    """
    Mengambil data analitik finansial GoPay dari ClickHouse.
    Difilter berdasarkan rentang `days` terakhir, serta opsional metode pembayaran,
    status transaksi, rentang volume transaksi, dan rentang cashback dibakar.
    Mengembalikan default 0 jika data kosong atau terjadi error.
    """

    # 1. Fallback Aman (transaction_status diganti menjadi transaction_type list kosong)
    response_data = {
        "kpis": {
            "gtv": {"value": 0, "trend": 0.0},
            "admin_fee": {"value": 0, "trend": 0.0},
            "cashback_burned": {"value": 0, "trend": 0.0},
        },
        "revenue_vs_burn": [],
        "transaction_type": [],  # <-- DIUBAH DARI transaction_status
        "method_popularity": [],
    }

    # Parameter aman untuk query + klausa filter dinamis
    params: Dict[str, Any] = {"days": days, "days2": days * 2}
    filter_clause = _build_filter_clause(
        params,
        payment_method,
        status,
        volume_min,
        volume_max,
        cashback_min,
        cashback_max,
    )

    try:
        client = get_clickhouse_client()

        # ==========================================
        # 1. QUERY KPIs (Periode Terakhir vs Sebelumnya)
        # ==========================================
        kpi_query = f"""
        SELECT
            sumIf(nilai_transaksi_total, tanggal >= today() - {{days:UInt32}}) AS gtv_curr,
            sumIf(nilai_transaksi_total, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS gtv_prev,

            sumIf(total_biaya_admin, tanggal >= today() - {{days:UInt32}}) AS admin_curr,
            sumIf(total_biaya_admin, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS admin_prev,

            sumIf(total_cashback_dibakar, tanggal >= today() - {{days:UInt32}}) AS cb_curr,
            sumIf(total_cashback_dibakar, tanggal >= today() - {{days2:UInt32}} AND tanggal < today() - {{days:UInt32}}) AS cb_prev
        FROM olap_gopay_finance_daily
        WHERE tanggal >= today() - {{days2:UInt32}} {filter_clause}
        """
        kpi_result = client.query(kpi_query, parameters=params).result_rows

        if kpi_result and kpi_result[0]:
            row = kpi_result[0]
            gtv_c, gtv_p = row[0] or 0, row[1] or 0
            adm_c, adm_p = row[2] or 0, row[3] or 0
            cb_c, cb_p = row[4] or 0, row[5] or 0

            response_data["kpis"]["gtv"] = {
                "value": gtv_c,
                "trend": calc_trend(gtv_c, gtv_p),
            }
            response_data["kpis"]["admin_fee"] = {
                "value": adm_c,
                "trend": calc_trend(adm_c, adm_p),
            }
            response_data["kpis"]["cashback_burned"] = {
                "value": cb_c,
                "trend": calc_trend(cb_c, cb_p),
            }

        # ==========================================
        # 2. QUERY DUAL LINE CHART (Revenue vs Burn)
        # ==========================================
        trend_query = f"""
        SELECT formatDateTime(tanggal, '%b %d') AS date,
               sum(total_biaya_admin) AS revenue,
               sum(total_cashback_dibakar) AS burn
        FROM olap_gopay_finance_daily
        WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}
        GROUP BY tanggal ORDER BY tanggal ASC
        """
        trend_result = client.query(trend_query, parameters=params).result_rows
        for row in trend_result:
            response_data["revenue_vs_burn"].append(
                {"date": row[0], "revenue": row[1] or 0, "burn": row[2] or 0}
            )

        # ==========================================
        # 3. QUERY TRANSACTION TYPE SPLIT (Dulu Transaction Status)
        # ==========================================
        # Mengelompokkan berdasarkan kolom status_transaksi (Top Up, Transfer, Payment)
        type_query = f"""
        WITH (SELECT sum(total_volume_transaksi) FROM olap_gopay_finance_daily WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}) AS total_all
        SELECT status_transaksi AS name,
               sum(total_volume_transaksi) AS value,
               round((sum(total_volume_transaksi) / nullIf(total_all, 0)) * 100, 1) AS percentage
        FROM olap_gopay_finance_daily
        WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}
        GROUP BY status_transaksi ORDER BY value DESC
        """
        type_result = client.query(type_query, parameters=params).result_rows
        for row in type_result:
            response_data["transaction_type"].append(
                {"name": row[0], "value": row[1] or 0, "percentage": row[2] or 0.0}
            )

        # ==========================================
        # 4. QUERY METHOD POPULARITY (Donut Chart)
        # ==========================================
        # Filter "status_transaksi = 'Selesai'" dihapus karena kolom ini berisi jenis transaksi
        method_query = f"""
        WITH (SELECT sum(total_volume_transaksi) FROM olap_gopay_finance_daily WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}) AS total_all
        SELECT metode_pembayaran AS name,
               sum(total_volume_transaksi) AS value,
               round((sum(total_volume_transaksi) / nullIf(total_all, 0)) * 100, 1) AS percentage
        FROM olap_gopay_finance_daily
        WHERE tanggal >= today() - {{days:UInt32}} {filter_clause}
        GROUP BY metode_pembayaran ORDER BY value DESC
        """
        method_result = client.query(method_query, parameters=params).result_rows
        for row in method_result:
            response_data["method_popularity"].append(
                {"name": row[0], "value": row[1] or 0, "percentage": row[2] or 0.0}
            )

    except Exception as e:
        logging.error(f"Gagal mengambil data GoPay dari ClickHouse: {str(e)}")

    return response_data
