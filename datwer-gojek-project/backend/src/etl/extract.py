# src/etl/extract.py

import pandas as pd
from sqlalchemy import exc
import logging
# [UBAH] Gunakan fungsi singleton, bukan class
from src.shared.database import get_postgres_engine

# Konfigurasi Logger Standar Perusahaan
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SupabaseExtractor:
    """
    Modul Utilitas untuk mengekstraksi data dari PostgreSQL (Supabase).
    Mendukung penarikan data secara penuh (Full Load) maupun parsial (Incremental).
    """
    
    def __init__(self):
        try:
            # [UBAH] Memanggil fungsi secara langsung
            self.engine = get_postgres_engine()
        except Exception as e:
            logger.error(f"Gagal menginisialisasi koneksi database: {e}")
            raise e

        # Daftar tabel berdasarkan DDL Supabase Anda
        self.master_tables = [
            'merchants', 
            'users', 
            'drivers', 
            'locations', 
            'promos', 
            'payment_methods', 
            'statuses'
        ]
        
        self.transaction_tables = [
            'gofood_transactions', 
            'gosend_transactions', 
            'goride_transactions', 
            'gopay_transactions'
        ]

    def extract_table(self, table_name: str, custom_query: str = None) -> pd.DataFrame:
        """
        Menarik data dari satu tabel spesifik menjadi Pandas DataFrame.
        
        Args:
            table_name (str): Nama tabel tujuan.
            custom_query (str, optional): Query SQL kustom jika tidak ingin 'SELECT *'.
        """
        # Validasi nama tabel agar mencegah typo atau SQL Injection ringan
        all_tables = self.master_tables + self.transaction_tables
        if table_name not in all_tables and custom_query is None:
            logger.warning(f"Tabel '{table_name}' tidak ada dalam daftar standar DDL.")

        query = custom_query if custom_query else f"SELECT * FROM public.{table_name}"
        
        try:
            logger.info(f"Mengekstraksi data dari tabel: {table_name}...")
            df = pd.read_sql(query, self.engine)
            
            if df.empty:
                logger.warning(f"Tabel '{table_name}' kosong (0 baris).")
            else:
                logger.info(f"Sukses menarik {len(df)} baris dari '{table_name}'.")
                
            return df
            
        except exc.SQLAlchemyError as sql_err:
            logger.error(f"Kesalahan SQL saat mengekstraksi '{table_name}': {sql_err}")
            raise
        except Exception as e:
            logger.error(f"Terjadi kesalahan sistem saat mengekstraksi '{table_name}': {e}")
            raise

    def extract_all_masters(self) -> dict:
        """
        Fungsi utilitas untuk menarik seluruh 7 Tabel Master sekaligus.
        Sangat berguna untuk proses sinkronisasi Dimensi secara massal.
        
        Returns:
            dict: Dictionary dengan key nama tabel dan value Pandas DataFrame.
        """
        logger.info("=== MEMULAI EKSTRAKSI MASSAL TABEL MASTER ===")
        master_data = {}
        for table in self.master_tables:
            master_data[table] = self.extract_table(table)
        logger.info("=== EKSTRAKSI TABEL MASTER SELESAI ===")
        return master_data