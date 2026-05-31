from fastapi import APIRouter
import logging
from typing import Dict, Any

from src.shared.database import get_clickhouse_client
from src.api.models.gofood import GoFoodDashboardResponse

router = APIRouter(prefix="/api/gofood", tags=["GoFood & Merchant Operations"])

def calc_trend(curr, prev):
    if not prev or prev == 0: 
        return 0.0
    return round(((curr - prev) / prev) * 100, 1)

@router.get("/dashboard-summary", response_model=GoFoodDashboardResponse)
async def get_gofood_dashboard_summary():
    """
    Mengambil data analitik GoFood dari ClickHouse.
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

    try:
        client = get_clickhouse_client()
        
        # ==========================================
        # 1. QUERY KPIs
        # ==========================================
        kpi_query = '''
        SELECT 
            sumIf(total_pendapatan_kotor, tanggal >= today() - 30) AS rev_curr,
            sumIf(total_pendapatan_kotor, tanggal >= today() - 60 AND tanggal < today() - 30) AS rev_prev,
            sumIf(total_laba_kotor_gojek, tanggal >= today() - 30) AS prof_curr,
            sumIf(total_laba_kotor_gojek, tanggal >= today() - 60 AND tanggal < today() - 30) AS prof_prev,
            sumIf(total_diskon_promo, tanggal >= today() - 30) AS promo_curr,
            sumIf(total_diskon_promo, tanggal >= today() - 60 AND tanggal < today() - 30) AS promo_prev,
            avgIf(rata_rata_waktu_persiapan, tanggal >= today() - 30) AS prep_curr,
            avgIf(rata_rata_waktu_persiapan, tanggal >= today() - 60 AND tanggal < today() - 30) AS prep_prev
        FROM olap_gofood_merchant_daily
        WHERE tanggal >= today() - 60
        '''
        kpi_result = client.query(kpi_query).result_rows
        
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
        trend_query = '''
        SELECT formatDateTime(tanggal, '%b %d') AS date, 
               sum(total_pendapatan_kotor) AS revenue, 
               sum(total_diskon_promo) AS promo
        FROM olap_gofood_merchant_daily
        WHERE tanggal >= today() - 30
        GROUP BY tanggal ORDER BY tanggal ASC
        '''
        trend_result = client.query(trend_query).result_rows
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
        cat_query = '''
        WITH (SELECT uniqExact(nama_merchant) FROM olap_gofood_merchant_daily WHERE tanggal >= today() - 30) AS total_merchants
        SELECT kategori_bisnis AS name, 
               uniqExact(nama_merchant) AS value, 
               round((uniqExact(nama_merchant) / nullIf(total_merchants, 0)) * 100, 1) AS percentage
        FROM olap_gofood_merchant_daily
        WHERE tanggal >= today() - 30
        GROUP BY kategori_bisnis ORDER BY value DESC
        '''
        cat_result = client.query(cat_query).result_rows
        for row in cat_result:
            response_data["category_split"].append({
                "name": row[0], 
                "value": row[1] or 0, 
                "percentage": row[2] or 0.0
            })

        # ==========================================
        # 4. QUERY TOP MERCHANTS TABLE
        # ==========================================
        top_query = '''
        SELECT concat(nama_merchant, ', ', kota) AS name, 
               kategori_bisnis AS category, 
               sum(total_pendapatan_kotor) AS revenue
        FROM olap_gofood_merchant_daily
        WHERE tanggal >= today() - 30
        GROUP BY nama_merchant, kota, kategori_bisnis 
        ORDER BY revenue DESC 
        LIMIT 5
        '''
        top_result = client.query(top_query).result_rows
        
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