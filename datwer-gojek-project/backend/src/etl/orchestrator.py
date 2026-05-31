# src/etl/orchestrator.py

import logging
import sys
import time
from datetime import datetime

# Import Eksekutor Sinkronisasi
from src.etl.sync.sync_dimensions import DimensionSync
from src.etl.sync.sync_facts import FactSync

# Konfigurasi Logger Utama Pipeline
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ETL_ORCHESTRATOR")

class GojekETLOrchestrator:
    """
    Dirigen utama yang mengatur urutan eksekusi Data Pipeline.
    Aturan Emas DW: Tabel Dimensi HARUS diisi terlebih dahulu sebelum Tabel Fakta.
    """
    
    def __init__(self):
        self.dim_sync = DimensionSync()
        self.fact_sync = FactSync()

    def run_pipeline(self):
        start_time = time.time()
        logger.info(f"MEMULAI GOJEK DATA PIPELINE BATCH - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        
        try:
            # TAHAP 1: SINKRONISASI DIMENSI (SCD Type 2)

            logger.info(">> TAHAP 1: Mengeksekusi Sinkronisasi Tabel Dimensi...")
            self.dim_sync.sync_all_dimensions()
            logger.info(">> TAHAP 1 SELESAI.\n")

            # TAHAP 2: SINKRONISASI FAKTA (Merge Lookup)
            logger.info(">> TAHAP 2: Mengeksekusi Sinkronisasi Tabel Fakta...")
            self.fact_sync.run_all()
            logger.info(">> TAHAP 2 SELESAI.\n")
            
        except Exception as e:
            # Menangkap kegagalan di level manapun (Extract/Transform/Load)
            logger.error("PIPELINE GAGAL BERHENTI DENGAN ERROR!")
            logger.error(str(e))
            
            # Sangat penting untuk CI/CD atau Airflow agar mendeteksi kegagalan task
            sys.exit(1) 
            
        finally:
            # Menghitung durasi eksekusi
            end_time = time.time()
            duration = end_time - start_time
            minutes, seconds = divmod(duration, 60)
            
            logger.info("="*60)
            logger.info(f"PIPELINE SELESAI DENGAN SUKSES!")
            logger.info(f"Total Durasi Eksekusi: {int(minutes)} Menit {seconds:.2f} Detik")
            logger.info("="*60)


if __name__ == "__main__":
    # Eksekusi langsung jika file ini dijalankan via terminal
    orchestrator = GojekETLOrchestrator()
    orchestrator.run_pipeline()