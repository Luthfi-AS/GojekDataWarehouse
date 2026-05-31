datwer-gojek-project/
│
├── src/                            # WILAYAH KODE UTAMA (Source Layout)
│   ├── __init__.py
│   ├── api/                        # --- 1. MICROSERVICE API (FastAPI) ---
│   │   ├── __init__.py
│   │   ├── endpoints/              # Pengganti folder 'api/' sebelumnya
│   │   │   ├── __init__.py
│   │   │   └── goride.py           # NEW: Endpoint API untuk dasbor GoRide
│   │   ├── models/                 # Pydantic schemas (Validasi)
│   │   │   ├── __init__.py
│   │   │   └── goride.py           # NEW: Skema respon data GoRide
│   │   └── main.py                 # Titik masuk FastAPI
│   │
│   ├── etl/                        # --- 2. DATA PIPELINE ENGINE ---
│   │   ├── __init__.py
│   │   ├── extract.py              # Koneksi & Tarik data dari Supabase (SQLAlchemy)
│   │   ├── transform.py            # Pembersihan & Type Casting (Pandas)
│   │   ├── load.py                 # Insert massal ke ClickHouse
│   │   └── orchestrator.py         # Sang Dirigen (Siap dihubungkan ke Apache Airflow)
│   │
│   └── shared/                     # --- 3. KOMPONEN BERSAMA (DRY Principle) ---
│       ├── __init__.py
│       ├── config.py               # Parsing .env menggunakan Pydantic BaseSettings
│       ├── database.py             # Setup Engine Supabase & ClickHouse Client
│       └── logger.py               # Format log seragam perusahaan (JSON logger)
│
├── sql/                            # WILAYAH DATABASE & ANALITIK
│   ├── ddl_clickhouse.sql          # Skema pembuatan tabel di ClickHouse
│   └── aggregate_views.sql         # Query kompleks (Materialized Views)
│
├── notebooks/                      # WILAYAH EKSPLORASI DATA & ML
│   └── 01_forecasting_eda.ipynb    # Eksplorasi data awal sebelum membangun model prediktif
│
├── tests/                          # WILAYAH QUALITY ASSURANCE (Pytest)
│   ├── __init__.py
│   ├── conftest.py                 # Setup Mock Database & Fixtures
│   ├── api/                        # Unit test khusus endpoint FastAPI
│   └── etl/                        # Unit test khusus fungsi Pandas (transform)
│
├── deploy/                         # WILAYAH INFRASTRUKTUR & DEVOPS
│   ├── Dockerfile                  # Resep containerisasi aplikasi
│   ├── docker-compose.yml          # Menjalankan ClickHouse & API lokal secara instan
│   └── .gitlab-ci.yml              # (Opsional) Skrip CI/CD pipeline
│
├── .env.example                    # Template environment variables (Tanpa password asli)
├── .gitignore
├── requirements.txt                # MANAJEMEN DEPENDENSI MODERN (Pengganti requirements.txt)
└── README.md                       # Dokumentasi Proyek