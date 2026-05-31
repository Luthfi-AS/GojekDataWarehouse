# src/etl/transform.py

import pandas as pd
import logging

# Konfigurasi Logger
logger = logging.getLogger(__name__)

class DataTransformer:
    """
    Modul Utilitas untuk membersihkan, mengubah tipe data (Casting), 
    dan menangani nilai kosong (NaN/Null) sebelum data dikirim ke ClickHouse.
    """

    @staticmethod
    def clean_data(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Fungsi utama untuk transformasi DataFrame.
        
        Args:
            df (pd.DataFrame): Data mentah dari Supabase.
            table_name (str): Nama tabel untuk menentukan aturan pembersihan khusus.
            
        Returns:
            pd.DataFrame: Data yang sudah bersih dan siap di-load ke ClickHouse.
        """
        if df.empty:
            return df
            
        df = df.copy()
  
        cols_to_drop = ['created_at', 'updated_at']
        df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

        # Standardisasi kolom Waktu (Menghapus Timezone agar diterima ClickHouse)
        datetime_columns = ['transaction_date', 'tanggal_pendaftaran', 'tanggal_bergabung', 'valid_from', 'valid_to']
        for col in datetime_columns:
            if col in df.columns:
                # Ubah ke datetime pandas, hapus tz info jika ada
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].dt.tz is not None:
                    df[col] = df[col].dt.tz_localize(None)

        if table_name == 'locations':
            # Pastikan kode_pos tetap menjadi String (mencegah terpotongnya angka 0 di depan)
            df['kode_pos'] = df['kode_pos'].astype(str)

        elif table_name == 'merchants':
            # Pastikan rating adalah Float. Jika NaN, ubah jadi 0.0
            df['rating_merchant'] = pd.to_numeric(df['rating_merchant'], errors='coerce').fillna(0.0)

        elif table_name == 'statuses':
            # Alasan pembatalan bisa Null. Ganti dengan string kosong
            df['alasan_pembatalan'] = df['alasan_pembatalan'].fillna('-')

        elif table_name == 'goride_transactions':
            # Rating bisa Null jika trip dibatalkan. Ganti jadi 0 dan pastikan integer.
            df['nilai_rating_driver'] = df['nilai_rating_driver'].fillna(0).astype(int)

        elif table_name == 'gosend_transactions':
            df['nilai_rating_pengiriman'] = df['nilai_rating_pengiriman'].fillna(0).astype(int)
        
        for col in df.columns:
            if df[col].dtype == 'object':  # Kolom String
                df[col] = df[col].fillna("")
            elif pd.api.types.is_numeric_dtype(df[col]):  # Kolom Angka (Int/Float)
                df[col] = df[col].fillna(0)

        logger.info(f"[TRANSFORM] Berhasil membersihkan {len(df)} baris untuk tabel '{table_name}'.")
        return df

