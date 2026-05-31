import pandas as pd
from datetime import datetime
import uuid
import logging
import hashlib

# Import Modul Utama ETL
from src.shared.database import get_clickhouse_client
from src.etl.extract import SupabaseExtractor
from src.etl.transform import DataTransformer
from src.etl.load import ClickHouseLoader

# Konfigurasi Logger
logger = logging.getLogger(__name__)

class DimensionSync:
    """
    Kelas Eksekutor SCD Type 2 Sempurna.
    Menggunakan teknik MD5 Hashing untuk mendeteksi perubahan data dan mencegah duplikasi mutlak.
    """

    def __init__(self):
        self.extractor = SupabaseExtractor()
        self.transformer = DataTransformer()
        self.loader = ClickHouseLoader()
        self.ch_client = get_clickhouse_client()

    def generate_hash(self, df: pd.DataFrame, exclude_cols: list) -> pd.Series:
        """Membuat sidik jari (hash) MD5 untuk mendeteksi perubahan pada baris data."""
        hash_cols = [col for col in df.columns if col not in exclude_cols]
        return df[hash_cols].astype(str).apply(
            lambda row: hashlib.md5(''.join(row).encode('utf-8')).hexdigest(), axis=1
        )

    def sync_all_dimensions(self):
        dimensions_config = [
            ('users', 'dim_user', 'user_id', 'user_key'),
            ('merchants', 'dim_merchant', 'merchant_id', 'merchant_key'),
            ('drivers', 'dim_driver', 'driver_id', 'driver_key'),
            ('locations', 'dim_location', 'location_id', 'location_key'),
            ('promos', 'dim_promo', 'promo_id', 'promo_key'),
            ('payment_methods', 'dim_payment_method', 'payment_method_id', 'payment_method_key'),
            ('statuses', 'dim_status', 'status_id', 'status_key')
        ]
        
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        logger.info("=== MEMULAI SINKRONISASI DIMENSI (SCD TYPE 2 SEMPURNA) ===")
        
        for pg_table, ch_table, source_id, target_key in dimensions_config:
            logger.info(f"[*] Memproses SCD2: {pg_table} -> {ch_table}")
            id_sumber_col = f"{target_key.replace('_key', '')}_id_sumber"
            
            # 1. EXTRACT & TRANSFORM
            df_source = self.extractor.extract_table(pg_table)
            if df_source.empty:
                continue
            df_source = self.transformer.clean_data(df_source, table_name=pg_table)
            df_source.rename(columns={source_id: id_sumber_col}, inplace=True)
            
            # Penanganan Tabel Statis (dim_status)
            if ch_table == 'dim_status':
                existing_status = self.ch_client.query_df(f"SELECT {id_sumber_col} FROM {ch_table}")
                if not existing_status.empty:
                    df_source = df_source[~df_source[id_sumber_col].isin(existing_status[id_sumber_col])]
                
                if not df_source.empty:
                    df_source[target_key] = [str(uuid.uuid4()) for _ in range(len(df_source))]
                    self.loader.insert_data(df_source, ch_table)
                continue

            # 2. LOGIKA SCD TYPE 2 (KOMPARASI HASH)
            query_target = f"SELECT * FROM {ch_table} WHERE is_active = 1"
            df_target = self.ch_client.query_df(query_target)
            
            exclude_for_hash = [target_key, id_sumber_col, 'valid_from', 'valid_to', 'is_active']
            df_source['row_hash'] = self.generate_hash(df_source, exclude_for_hash)
            
            df_to_insert = pd.DataFrame()
            keys_to_expire = []

            if df_target.empty:
                logger.info("    -> Data Warehouse kosong. Melakukan First Load.")
                df_to_insert = df_source.copy()
            else:
                df_target['row_hash'] = self.generate_hash(df_target, exclude_for_hash)
                
                # Identifikasi Data Baru
                new_records = df_source[~df_source[id_sumber_col].isin(df_target[id_sumber_col])].copy()
                
                # Identifikasi Data Berubah
                merged = df_source.merge(df_target, on=id_sumber_col, suffixes=('_src', '_tgt'))
                changed_records_src = merged[merged['row_hash_src'] != merged['row_hash_tgt']]
                changed_records = df_source[df_source[id_sumber_col].isin(changed_records_src[id_sumber_col])].copy()
                
                keys_to_expire = changed_records_src[target_key].tolist()
                df_to_insert = pd.concat([new_records, changed_records], ignore_index=True)
                
                logger.info(f"    -> Ditemukan: {len(new_records)} Data Baru, {len(changed_records)} Data Berubah.")

            # 3. UPDATE CLICKHOUSE (Matikan data lama)
            if keys_to_expire:
                logger.info(f"    -> Melakukan Expiration (is_active=0) pada {len(keys_to_expire)} baris lama...")
                keys_str = ", ".join([f"'{k}'" for k in keys_to_expire])
                expire_query = f"""
                    ALTER TABLE {ch_table} 
                    UPDATE is_active = 0, valid_to = '{now_str}' 
                    WHERE {target_key} IN ({keys_str})
                """
                self.loader.execute_query(expire_query)

            # 4. INSERT CLICKHOUSE (Data baru & Data revisi)
            if not df_to_insert.empty:
                df_to_insert.drop(columns=['row_hash'], inplace=True)
                df_to_insert[target_key] = [str(uuid.uuid4()) for _ in range(len(df_to_insert))]
                df_to_insert['valid_from'] = now
                df_to_insert['valid_to'] = pd.to_datetime('2099-12-31 23:59:59')
                df_to_insert['is_active'] = 1
                
                self.loader.insert_data(df_to_insert, ch_table)
            else:
                logger.info(f"    -> Tidak ada penambahan atau perubahan data untuk '{ch_table}'. (Skip)")
                
        logger.info("=== SINKRONISASI DIMENSI SCD 2 SELESAI ===")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    sync_job = DimensionSync()
    sync_job.sync_all_dimensions()