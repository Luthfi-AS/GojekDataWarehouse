import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import clickhouse_connect
from clickhouse_connect.driver.client import Client
from dotenv import load_dotenv

# Muat variabel environment
load_dotenv()

# ==========================================
# Variabel Global (Singleton Cache)
# ==========================================
_postgres_engine: Engine | None = None
_clickhouse_client: Client | None = None

def get_postgres_engine() -> Engine:
    """
    Membuat dan mengembalikan koneksi ke Supabase PostgreSQL.
    Menggunakan pola Singleton agar engine hanya dibuat satu kali.
    """
    global _postgres_engine
    
    if _postgres_engine is None:
        db_url = os.getenv("SUPABASE_DB_URL")
        if not db_url:
            raise ValueError("SUPABASE_DB_URL tidak ditemukan di konfigurasi .env")
        
        _postgres_engine = create_engine(db_url, pool_pre_ping=True)
        logging.info("PostgreSQL engine berhasil diinisialisasi.")
        
    return _postgres_engine

def get_clickhouse_client() -> Client:
    """
    Membuat dan mengembalikan koneksi ke ClickHouse.
    Mencegah pembuatan HTTP Client baru di setiap request FastAPI.
    """
    global _clickhouse_client
    
    if _clickhouse_client is None:
        try:
            _clickhouse_client = clickhouse_connect.get_client(
                host=os.getenv("CLICKHOUSE_HOST", "localhost"),
                port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
                username=os.getenv("CLICKHOUSE_USER", "default"),
                password=os.getenv("CLICKHOUSE_PASSWORD", ""),
                # ClickHouse Cloud wajib TLS (port 8443). Default true; set false utk lokal.
                secure=os.getenv("CLICKHOUSE_SECURE", "true").lower() == "true"
            )
            logging.info("ClickHouse client berhasil diinisialisasi.")
        except Exception as e:
            logging.error(f"Koneksi ClickHouse gagal: {str(e)}")
            raise e
            
    return _clickhouse_client

