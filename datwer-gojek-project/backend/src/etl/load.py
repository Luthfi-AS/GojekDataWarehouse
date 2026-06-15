# src/etl/load.py

import pandas as pd
import logging

# [UBAH] Gunakan fungsi singleton client
from src.shared.database import get_clickhouse_client

# Konfigurasi Logger
logger = logging.getLogger(__name__)


class ClickHouseLoader:
    """
    Modul Utilitas untuk memuat (Load) data Pandas DataFrame secara massal
    ke dalam ClickHouse Data Warehouse.
    """

    def __init__(self):
        try:
            # [UBAH] Memanggil fungsi secara langsung
            self.client = get_clickhouse_client()
        except Exception as e:
            logger.error(f"Gagal menginisialisasi koneksi ClickHouse: {e}")
            raise e

    def insert_data(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Mengirim Pandas DataFrame ke tabel spesifik di ClickHouse.

        Args:
            df (pd.DataFrame): Data yang sudah bersih.
            table_name (str): Nama tabel tujuan di ClickHouse (contoh: 'dim_merchant').
        """
        if df.empty:
            logger.warning(
                f"[LOAD] DataFrame kosong. Melewati proses insert untuk tabel '{table_name}'."
            )
            return

        try:
            logger.info(
                f"[LOAD] Memulai proses pengiriman {len(df)} baris ke tabel '{table_name}'..."
            )

            # Memasukkan DataFrame secara langsung.
            # Pustaka clickhouse-connect sangat optimal untuk bulk insert menggunakan Arrow/Native format.
            self.client.insert_df(table_name, df)

            logger.info(f"[LOAD - SUCCESS] Berhasil memuat data ke '{table_name}'.")

        except Exception as e:
            logger.error(f"[LOAD - ERROR] Gagal mengirim data ke '{table_name}': {e}")
            # Lemparkan error agar orkestrator tahu pipeline gagal di tahap ini
            raise e

    def execute_query(self, query: str) -> None:
        """
        Fungsi utilitas tambahan jika ingin menjalankan perintah non-insert,
        seperti TRUNCATE atau OPTIMIZE TABLE.
        """
        try:
            self.client.command(query)
            logger.info(f"[LOAD] Eksekusi query sukses: {query[:50]}...")
        except Exception as e:
            logger.error(f"[LOAD - ERROR] Gagal mengeksekusi query: {e}")
            raise e
