from fastapi import APIRouter, Depends
import logging
from typing import Dict, Any

from src.shared.database import get_clickhouse_client 

from src.api.models.goride import GoRideDashboardResponse

router = APIRouter(prefix="/api/goride", tags=["GoRide Operations"])

def calc_trend(curr, prev):
    """Menghitung persentase pertumbuhan (growth)."""
    if not prev or prev == 0: 
        return 0.0
    return round(((curr - prev) / prev) * 100, 1)

@router.get("/dashboard-summary", response_model=GoRideDashboardResponse)
async def get_goride_dashboard_summary():
    """
    Mengambil data operasional GoRide dari ClickHouse.
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

    try:
        # Inisiasi Client ClickHouse (Pastikan ini tidak di-comment!)
        client = get_clickhouse_client()
        
        # ==========================================
        # EKSEKUSI QUERY KE CLICKHOUSE
        # ==========================================
        
        # 1. KPIs
        kpi_query = '''
        SELECT 
            sumIf(total_perjalanan, tanggal >= today() - 30) AS trips_current,
            sumIf(total_perjalanan, tanggal >= today() - 60 AND tanggal < today() - 30) AS trips_prev,
            sumIf(total_jarak_km, tanggal >= today() - 30) AS distance_current,
            sumIf(total_jarak_km, tanggal >= today() - 60 AND tanggal < today() - 30) AS distance_prev,
            sumIf(total_biaya_tambahan, tanggal >= today() - 30) AS surge_current,
            sumIf(total_biaya_tambahan, tanggal >= today() - 60 AND tanggal < today() - 30) AS surge_prev,
            sumIf(total_rating_driver, tanggal >= today() - 30) / nullIf(sumIf(total_perjalanan, tanggal >= today() - 30), 0) AS rating_current,
            sumIf(total_rating_driver, tanggal >= today() - 60 AND tanggal < today() - 30) / nullIf(sumIf(total_perjalanan, tanggal >= today() - 60 AND tanggal < today() - 30), 0) AS rating_prev
        FROM olap_goride_ops_daily
        WHERE tanggal >= today() - 60
        '''
        kpi_result = client.query(kpi_query).result_rows
        
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
        trend_query = '''
        SELECT formatDateTime(tanggal, '%b %d') AS date, sum(total_perjalanan) AS volume
        FROM olap_goride_ops_daily
        WHERE tanggal >= today() - 30
        GROUP BY tanggal ORDER BY tanggal ASC
        '''
        trend_result = client.query(trend_query).result_rows
        for row in trend_result:
            response_data["daily_trend"].append({"date": row[0], "volume": row[1] or 0})

        # 3. Vehicle Split
        vehicle_query = '''
        WITH (SELECT sum(total_perjalanan) FROM olap_goride_ops_daily WHERE tanggal >= today() - 30) AS total_all
        SELECT jenis_kendaraan AS name, sum(total_perjalanan) AS value, 
               round((sum(total_perjalanan) / nullIf(total_all, 0)) * 100, 1) AS percentage
        FROM olap_goride_ops_daily
        WHERE tanggal >= today() - 30
        GROUP BY jenis_kendaraan ORDER BY value DESC
        '''
        vehicle_result = client.query(vehicle_query).result_rows
        for row in vehicle_result:
            response_data["vehicle_split"].append({"name": row[0], "value": row[1] or 0, "percentage": row[2] or 0.0})

        # 4. City Performance
        city_query = '''
        SELECT kota_jemputan AS city,
               sumIf(total_perjalanan, tanggal >= today() - 30) AS volume_current,
               sumIf(total_perjalanan, tanggal >= today() - 60 AND tanggal < today() - 30) AS volume_prev,
               round(((volume_current - volume_prev) / nullIf(volume_prev, 0)) * 100, 1) AS growth
        FROM olap_goride_ops_daily
        WHERE tanggal >= today() - 60
        GROUP BY kota_jemputan ORDER BY volume_current DESC LIMIT 5
        '''
        city_result = client.query(city_query).result_rows
        for row in city_result:
            response_data["city_performance"].append({"city": row[0], "volume": row[1] or 0, "growth": row[3] or 0.0})
        
    except Exception as e:
        logging.error(f"Gagal mengambil data dari ClickHouse: {str(e)}")

    return response_data