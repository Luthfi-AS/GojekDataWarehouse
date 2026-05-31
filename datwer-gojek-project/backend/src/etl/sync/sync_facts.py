import pandas as pd
import uuid
import logging

# Import Modul Utama ETL
from src.shared.database import get_clickhouse_client
from src.etl.extract import SupabaseExtractor
from src.etl.transform import DataTransformer
from src.etl.load import ClickHouseLoader

# Konfigurasi Logger
logger = logging.getLogger(__name__)

class FactSync:
    """
    Kelas Eksekutor untuk menyinkronkan data transaksi dari Supabase 
    ke Tabel Fakta ClickHouse dengan Logika Incremental Load (Anti-Duplikasi).
    """

    def __init__(self):
        self.extractor = SupabaseExtractor()
        self.transformer = DataTransformer()
        self.loader = ClickHouseLoader()
        self.ch_client = get_clickhouse_client()

    def get_active_dimension(self, table_name: str, key_col: str, source_id_col: str) -> pd.DataFrame:
        if table_name == 'dim_status':
            query = f"SELECT {key_col}, {source_id_col} FROM {table_name}"
        else:
            query = f"SELECT {key_col}, {source_id_col} FROM {table_name} WHERE is_active = 1"
        return self.ch_client.query_df(query)

    def get_existing_transactions(self, ch_table: str) -> list:
        """Menarik daftar transaction_id yang SUDAH ADA di ClickHouse"""
        try:
            df = self.ch_client.query_df(f"SELECT transaction_id FROM {ch_table}")
            return df['transaction_id'].tolist()
        except Exception:
            return []

    def sync_fact_gofood(self):
        logger.info("[*] Sinkronisasi Fakta: fact_gofood")
        
        # 1. EXTRACT
        df_raw = self.extractor.extract_table('gofood_transactions')
        if df_raw.empty: return

        # --- LOGIKA INCREMENTAL LOAD ---
        existing_ids = self.get_existing_transactions('fact_gofood')
        if existing_ids:
            # Hanya ambil transaksi yang belum ada di ClickHouse
            df_raw = df_raw[~df_raw['transaction_id'].isin(existing_ids)]
            if df_raw.empty:
                logger.info("    -> Tidak ada transaksi GoFood baru. (Skip)")
                return
        
        logger.info(f"    -> Memproses {len(df_raw)} transaksi BARU.")
        # --------------------------------

        # 2. TRANSFORM
        df_clean = self.transformer.clean_data(df_raw, 'gofood_transactions')

        # 3. LOOKUP DIMENSI
        dim_user = self.get_active_dimension('dim_user', 'user_key', 'user_id_sumber')
        dim_status = self.get_active_dimension('dim_status', 'status_key', 'status_id_sumber')
        dim_merchant = self.get_active_dimension('dim_merchant', 'merchant_key', 'merchant_id_sumber')
        dim_driver = self.get_active_dimension('dim_driver', 'driver_key', 'driver_id_sumber')
        dim_promo = self.get_active_dimension('dim_promo', 'promo_key', 'promo_id_sumber')
        dim_payment = self.get_active_dimension('dim_payment_method', 'payment_method_key', 'payment_method_id_sumber')
        
        dim_loc_delivery = self.get_active_dimension('dim_location', 'location_key', 'location_id_sumber')
        dim_loc_delivery.rename(columns={'location_key': 'location_delivery_key', 'location_id_sumber': 'loc_del_src'}, inplace=True)

        # 4. MERGE
        df_fact = df_clean.merge(dim_user, left_on='user_id', right_on='user_id_sumber', how='left')
        df_fact = df_fact.merge(dim_status, left_on='status_id', right_on='status_id_sumber', how='left')
        df_fact = df_fact.merge(dim_merchant, left_on='merchant_id', right_on='merchant_id_sumber', how='left')
        df_fact = df_fact.merge(dim_driver, left_on='driver_id', right_on='driver_id_sumber', how='left')
        df_fact = df_fact.merge(dim_promo, left_on='promo_id', right_on='promo_id_sumber', how='left')
        df_fact = df_fact.merge(dim_payment, left_on='payment_method_id', right_on='payment_method_id_sumber', how='left')
        df_fact = df_fact.merge(dim_loc_delivery, left_on='location_delivery_id', right_on='loc_del_src', how='left')

        df_fact['gofood_fact_key'] = [str(uuid.uuid4()) for _ in range(len(df_fact))]
        df_fact['date_key'] = df_fact['transaction_date'].dt.strftime('%Y%m%d')

        final_columns = [
            'gofood_fact_key', 'transaction_id', 'user_key', 'status_key', 'merchant_key', 'driver_key', 
            'date_key', 'location_delivery_key', 'promo_key', 'payment_method_key', 
            'harga_makanan_total', 'biaya_pengantaran', 'biaya_layanan', 'diskon_promo', 
            'total_pembayaran', 'komisi_merchant', 'laba_kotor', 'waktu_persiapan_menit'
        ]
        
        self.loader.insert_data(df_fact[final_columns], 'fact_gofood')

    def sync_fact_gosend(self):
        logger.info("[*] Sinkronisasi Fakta: fact_gosend")
        
        df_raw = self.extractor.extract_table('gosend_transactions')
        if df_raw.empty: return

        # --- INCREMENTAL LOAD ---
        existing_ids = self.get_existing_transactions('fact_gosend')
        if existing_ids:
            df_raw = df_raw[~df_raw['transaction_id'].isin(existing_ids)]
            if df_raw.empty:
                logger.info("    -> Tidak ada transaksi GoSend baru. (Skip)")
                return
        
        df_clean = self.transformer.clean_data(df_raw, 'gosend_transactions')

        dim_user = self.get_active_dimension('dim_user', 'user_key', 'user_id_sumber')
        dim_status = self.get_active_dimension('dim_status', 'status_key', 'status_id_sumber')
        dim_driver = self.get_active_dimension('dim_driver', 'driver_key', 'driver_id_sumber')
        dim_promo = self.get_active_dimension('dim_promo', 'promo_key', 'promo_id_sumber')
        
        dim_loc_sender = self.get_active_dimension('dim_location', 'location_key', 'location_id_sumber')
        dim_loc_sender.rename(columns={'location_key': 'location_sender_key', 'location_id_sumber': 'loc_sender_src'}, inplace=True)
        
        dim_loc_receiver = self.get_active_dimension('dim_location', 'location_key', 'location_id_sumber')
        dim_loc_receiver.rename(columns={'location_key': 'location_receiver_key', 'location_id_sumber': 'loc_receiver_src'}, inplace=True)

        df_fact = df_clean.merge(dim_user, left_on='user_id', right_on='user_id_sumber', how='left')
        df_fact = df_fact.merge(dim_status, left_on='status_id', right_on='status_id_sumber', how='left')
        df_fact = df_fact.merge(dim_driver, left_on='driver_id', right_on='driver_id_sumber', how='left')
        df_fact = df_fact.merge(dim_promo, left_on='promo_id', right_on='promo_id_sumber', how='left')
        df_fact = df_fact.merge(dim_loc_sender, left_on='location_sender_id', right_on='loc_sender_src', how='left')
        df_fact = df_fact.merge(dim_loc_receiver, left_on='location_receiver_id', right_on='loc_receiver_src', how='left')

        df_fact['gosend_fact_key'] = [str(uuid.uuid4()) for _ in range(len(df_fact))]
        df_fact['date_key'] = df_fact['transaction_date'].dt.strftime('%Y%m%d')

        final_columns = [
            'gosend_fact_key', 'transaction_id', 'user_key', 'status_key', 'driver_key', 'date_key', 
            'location_sender_key', 'location_receiver_key', 'promo_key', 'ongkos_kirim', 
            'biaya_asuransi', 'potongan_promo', 'total_biaya_kirim', 'berat_paket_kg', 
            'estimasi_waktu_sampai', 'nilai_rating_pengiriman'
        ]
        
        self.loader.insert_data(df_fact[final_columns], 'fact_gosend')

    def sync_fact_goride(self):
        logger.info("[*] Sinkronisasi Fakta: fact_goride")
        
        df_raw = self.extractor.extract_table('goride_transactions')
        if df_raw.empty: return

        # --- INCREMENTAL LOAD ---
        existing_ids = self.get_existing_transactions('fact_goride')
        if existing_ids:
            df_raw = df_raw[~df_raw['transaction_id'].isin(existing_ids)]
            if df_raw.empty:
                logger.info("    -> Tidak ada transaksi GoRide baru. (Skip)")
                return

        df_clean = self.transformer.clean_data(df_raw, 'goride_transactions')

        dim_user = self.get_active_dimension('dim_user', 'user_key', 'user_id_sumber')
        dim_status = self.get_active_dimension('dim_status', 'status_key', 'status_id_sumber')
        dim_driver = self.get_active_dimension('dim_driver', 'driver_key', 'driver_id_sumber')
        dim_promo = self.get_active_dimension('dim_promo', 'promo_key', 'promo_id_sumber')
        
        dim_loc_pickup = self.get_active_dimension('dim_location', 'location_key', 'location_id_sumber')
        dim_loc_pickup.rename(columns={'location_key': 'location_pickup_key', 'location_id_sumber': 'loc_pickup_src'}, inplace=True)
        
        dim_loc_dropoff = self.get_active_dimension('dim_location', 'location_key', 'location_id_sumber')
        dim_loc_dropoff.rename(columns={'location_key': 'location_dropoff_key', 'location_id_sumber': 'loc_dropoff_src'}, inplace=True)

        df_fact = df_clean.merge(dim_user, left_on='user_id', right_on='user_id_sumber', how='left')
        df_fact = df_fact.merge(dim_status, left_on='status_id', right_on='status_id_sumber', how='left')
        df_fact = df_fact.merge(dim_driver, left_on='driver_id', right_on='driver_id_sumber', how='left')
        df_fact = df_fact.merge(dim_promo, left_on='promo_id', right_on='promo_id_sumber', how='left')
        df_fact = df_fact.merge(dim_loc_pickup, left_on='location_pickup_id', right_on='loc_pickup_src', how='left')
        df_fact = df_fact.merge(dim_loc_dropoff, left_on='location_dropoff_id', right_on='loc_dropoff_src', how='left')

        df_fact['goride_fact_key'] = [str(uuid.uuid4()) for _ in range(len(df_fact))]
        df_fact['date_key'] = df_fact['transaction_date'].dt.strftime('%Y%m%d')

        final_columns = [
            'goride_fact_key', 'transaction_id', 'user_key', 'status_key', 'driver_key', 'date_key', 
            'location_pickup_key', 'location_dropoff_key', 'promo_key', 'tarif_dasar', 
            'biaya_tambahan_permintaan', 'potongan_promo', 'total_biaya_penumpang', 
            'jarak_km', 'durasi_menit', 'nilai_rating_driver'
        ]
        
        self.loader.insert_data(df_fact[final_columns], 'fact_goride')

    def sync_fact_gopay(self):
        logger.info("[*] Sinkronisasi Fakta: fact_gopay")
        
        df_raw = self.extractor.extract_table('gopay_transactions')
        if df_raw.empty: return

        # --- INCREMENTAL LOAD ---
        existing_ids = self.get_existing_transactions('fact_gopay')
        if existing_ids:
            df_raw = df_raw[~df_raw['transaction_id'].isin(existing_ids)]
            if df_raw.empty:
                logger.info("    -> Tidak ada transaksi GoPay baru. (Skip)")
                return

        df_clean = self.transformer.clean_data(df_raw, 'gopay_transactions')

        dim_user = self.get_active_dimension('dim_user', 'user_key', 'user_id_sumber')
        dim_status = self.get_active_dimension('dim_status', 'status_key', 'status_id_sumber')
        dim_payment = self.get_active_dimension('dim_payment_method', 'payment_method_key', 'payment_method_id_sumber')

        df_fact = df_clean.merge(dim_user, left_on='user_id', right_on='user_id_sumber', how='left')
        df_fact = df_fact.merge(dim_status, left_on='status_id', right_on='status_id_sumber', how='left')
        df_fact = df_fact.merge(dim_payment, left_on='payment_method_id', right_on='payment_method_id_sumber', how='left')

        df_fact['gopay_fact_key'] = [str(uuid.uuid4()) for _ in range(len(df_fact))]
        df_fact['date_key'] = df_fact['transaction_date'].dt.strftime('%Y%m%d')

        final_columns = [
            'gopay_fact_key', 'transaction_id', 'user_key', 'status_key', 'date_key', 'payment_method_key', 
            'nilai_transaksi', 'biaya_admin', 'cashback_diterima', 'saldo_sebelum', 
            'saldo_sesudah', 'status_transaksi', 'biaya_transfer', 'pajak_transaksi'
        ]
        
        self.loader.insert_data(df_fact[final_columns], 'fact_gopay')

    def run_all(self):
        logger.info("=== MEMULAI SINKRONISASI TABEL FAKTA ===")
        self.sync_fact_gofood()
        self.sync_fact_gosend()
        self.sync_fact_goride()
        self.sync_fact_gopay()
        logger.info("=== SINKRONISASI FAKTA SELESAI ===")