import pandas as pd
from src.shared.database import DatabaseManager

def generate_dim_date(start_date='2020-01-01', end_date='2030-12-31'):
    print(f"Generating dim_date dari {start_date} hingga {end_date}...")
    
    # [DIPERBAIKI] Menggunakan start_date dan end_date
    df_dates = pd.DataFrame({'tanggal': pd.date_range(start=start_date, end=end_date)})
    
    # Ekstraksi komponen tanggal
    df_dates['date_key'] = df_dates['tanggal'].dt.strftime('%Y%m%d')
    df_dates['hari'] = df_dates['tanggal'].dt.day
    df_dates['bulan'] = df_dates['tanggal'].dt.month
    df_dates['tahun'] = df_dates['tanggal'].dt.year
    df_dates['kuartal'] = df_dates['tanggal'].dt.quarter
    df_dates['nama_hari'] = df_dates['tanggal'].dt.day_name()
    
    # Logika sederhana untuk status libur
    df_dates['status_libur'] = df_dates['nama_hari'].apply(
        lambda x: 'Libur Akhir Pekan' if x in ['Saturday', 'Sunday'] else 'Hari Kerja'
    )
    
    # Konversi tipe data agar sesuai dengan DDL ClickHouse
    df_dates['tanggal'] = df_dates['tanggal'].dt.date
    
    # Insert ke ClickHouse
    client = DatabaseManager.get_clickhouse_client()
    
    print("Inserting ke ClickHouse...")
    client.insert_df('dim_date', df_dates)
    print(f"Berhasil insert {len(df_dates)} baris ke dim_date.")

if __name__ == "__main__":
    generate_dim_date()