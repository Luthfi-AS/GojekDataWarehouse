from fastapi import APIRouter
import logging
from typing import Dict, Any

from src.shared.database import get_clickhouse_client
from src.api.models.gopay import GoPayDashboardResponse

router = APIRouter(prefix="/api/gopay", tags=["GoPay Financial Ledger"])

def calc_trend(curr, prev):
    if not prev or prev == 0: 
        return 0.0
    return round(((curr - prev) / prev) * 100, 1)

@router.get("/dashboard-summary", response_model=GoPayDashboardResponse)
async def get_gopay_dashboard_summary():
    """
    Mengambil data analitik finansial GoPay dari ClickHouse.
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
        "method_popularity": []
    }

    try:
        client = get_clickhouse_client()
        
        # ==========================================
        # 1. QUERY KPIs (30 Hari Terakhir vs Sebelumnya)
        # ==========================================
        kpi_query = '''
        SELECT 
            sumIf(nilai_transaksi_total, tanggal >= today() - 30) AS gtv_curr,
            sumIf(nilai_transaksi_total, tanggal >= today() - 60 AND tanggal < today() - 30) AS gtv_prev,
            
            sumIf(total_biaya_admin, tanggal >= today() - 30) AS admin_curr,
            sumIf(total_biaya_admin, tanggal >= today() - 60 AND tanggal < today() - 30) AS admin_prev,
            
            sumIf(total_cashback_dibakar, tanggal >= today() - 30) AS cb_curr,
            sumIf(total_cashback_dibakar, tanggal >= today() - 60 AND tanggal < today() - 30) AS cb_prev
        FROM olap_gopay_finance_daily
        WHERE tanggal >= today() - 60
        '''
        kpi_result = client.query(kpi_query).result_rows
        
        if kpi_result and kpi_result[0]:
            row = kpi_result[0]
            gtv_c, gtv_p = row[0] or 0, row[1] or 0
            adm_c, adm_p = row[2] or 0, row[3] or 0
            cb_c, cb_p = row[4] or 0, row[5] or 0
            
            response_data["kpis"]["gtv"] = {"value": gtv_c, "trend": calc_trend(gtv_c, gtv_p)}
            response_data["kpis"]["admin_fee"] = {"value": adm_c, "trend": calc_trend(adm_c, adm_p)}
            response_data["kpis"]["cashback_burned"] = {"value": cb_c, "trend": calc_trend(cb_c, cb_p)}

        # ==========================================
        # 2. QUERY DUAL LINE CHART (Revenue vs Burn)
        # ==========================================
        trend_query = '''
        SELECT formatDateTime(tanggal, '%b %d') AS date, 
               sum(total_biaya_admin) AS revenue, 
               sum(total_cashback_dibakar) AS burn
        FROM olap_gopay_finance_daily
        WHERE tanggal >= today() - 30
        GROUP BY tanggal ORDER BY tanggal ASC
        '''
        trend_result = client.query(trend_query).result_rows
        for row in trend_result:
            response_data["revenue_vs_burn"].append({
                "date": row[0], 
                "revenue": row[1] or 0, 
                "burn": row[2] or 0
            })

        # ==========================================
        # 3. QUERY TRANSACTION TYPE SPLIT (Dulu Transaction Status)
        # ==========================================
        # Mengelompokkan berdasarkan kolom status_transaksi (Top Up, Transfer, Payment)
        type_query = '''
        WITH (SELECT sum(total_volume_transaksi) FROM olap_gopay_finance_daily WHERE tanggal >= today() - 30) AS total_all
        SELECT status_transaksi AS name, 
               sum(total_volume_transaksi) AS value, 
               round((sum(total_volume_transaksi) / nullIf(total_all, 0)) * 100, 1) AS percentage
        FROM olap_gopay_finance_daily
        WHERE tanggal >= today() - 30
        GROUP BY status_transaksi ORDER BY value DESC
        '''
        type_result = client.query(type_query).result_rows
        for row in type_result:
            response_data["transaction_type"].append({
                "name": row[0], 
                "value": row[1] or 0, 
                "percentage": row[2] or 0.0
            })

        # ==========================================
        # 4. QUERY METHOD POPULARITY (Donut Chart)
        # ==========================================
        # Filter "status_transaksi = 'Selesai'" dihapus karena kolom ini berisi jenis transaksi
        method_query = '''
        WITH (SELECT sum(total_volume_transaksi) FROM olap_gopay_finance_daily WHERE tanggal >= today() - 30) AS total_all
        SELECT metode_pembayaran AS name, 
               sum(total_volume_transaksi) AS value, 
               round((sum(total_volume_transaksi) / nullIf(total_all, 0)) * 100, 1) AS percentage
        FROM olap_gopay_finance_daily
        WHERE tanggal >= today() - 30
        GROUP BY metode_pembayaran ORDER BY value DESC
        '''
        method_result = client.query(method_query).result_rows
        for row in method_result:
            response_data["method_popularity"].append({
                "name": row[0], 
                "value": row[1] or 0, 
                "percentage": row[2] or 0.0
            })

    except Exception as e:
        logging.error(f"Gagal mengambil data GoPay dari ClickHouse: {str(e)}")

    return response_data