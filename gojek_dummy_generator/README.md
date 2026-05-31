# ⚙️ Gojek Data Engine (OLTP Data Generator)

Aplikasi **Control Panel / Developer Dashboard** berbasis Flutter yang dirancang khusus untuk keperluan _Data Engineering_. Alat ini berfungsi sebagai mesin generator (simulator) untuk menyuntikkan ribuan data transaksi tiruan yang realistis secara langsung ke dalam _database_ relasional PostgreSQL (Supabase).

Data operasional (OLTP) yang dihasilkan oleh mesin ini nantinya akan digunakan sebagai sumber data mentah untuk diekstraksi (ETL) menuju sistem _Data Warehouse_ (ClickHouse) untuk keperluan analitik tingkat lanjut.

## 🚀 Fitur Utama

- **Master Data Seeder**: Menyuntikkan data fondasi yang saling berelasi dengan aman (Users, Merchants, Drivers, Locations, Promos, Payment Methods, Statuses) tanpa melanggar aturan _Foreign Key_.
- **GoFood Generator**: Membuat transaksi pesanan makanan lengkap dengan kalkulasi jarak, biaya antar, pajak, dan diskon promo.
- **GoRide Generator**: Mensimulasikan perjalanan ojek _online_ dengan perhitungan _surge pricing_ (biaya tambahan dinamis) berdasarkan probabilitas.
- **GoSend Generator**: Mensimulasikan pengiriman paket dengan variasi berat barang dan opsi asuransi pengiriman.
- **GoPay Generator**: Memproduksi riwayat finansial dompet digital (Top Up, Transfer, dan Payment) dengan mutasi saldo yang akurat.
- **Execution Console**: Dasbor log internal menyerupai terminal _bash_ untuk memantau proses _insert_ data secara _real-time_.

## 📂 Struktur Direktori (Modular Architecture)

Proyek ini menggunakan arsitektur modular yang memisahkan antara antarmuka (UI), konfigurasi dasar, dan logika bisnis mesin generator.

```text
gojek_dummy_generator/
│
├── lib/
│   ├── core/                       # ➔ KONFIGURASI UMUM
│   │   ├── app_colors.dart         # Konstanta warna tema aplikasi (Material 3)
│   │   └── supabase_config.dart    # Setup client Supabase & kredensial
│   │
│   ├── models/                     # ➔ STRUKTUR DATA
│   │   └── panel_models.dart       # Model log console dan konfigurasi generator
│   │
│   ├── screens/                    # ➔ ANTARMUKA (UI)
│   │   ├── control_panel.dart      # Layar utama (State Management & Logika Eksekusi)
│   │   └── widgets/
│   │       └── panel_components.dart # Potongan UI terpisah (Card, Console, Banner)
│   │
│   ├── services/                   # ➔ MESIN GENERATOR (Supabase INSERTS)
│   │   ├── master_data_seeder.dart # Mengisi data fondasi (Users, Merchants, dll.)
│   │   ├── gofood_generator.dart   # Logika bisnis transaksi GoFood
│   │   ├── goride_generator.dart   # Logika bisnis transaksi GoRide
│   │   ├── gosend_generator.dart   # Logika bisnis transaksi GoSend
│   │   └── gopay_generator.dart    # Logika bisnis transaksi GoPay
│   │
│   ├── utils/                      # ➔ ALAT BANTU (Helpers)
│   │   └── randomizer.dart         # Engine acak untuk UUID, tanggal, status, dan nominal
│   │
│   └── main.dart                   # ➔ ENTRY POINT
```

POSTGRE

-- Tabel Master Merchant
CREATE TABLE merchants (
merchant_id VARCHAR(50) PRIMARY KEY, -- Ini akan menjadi merchant_id_sumber di ClickHouse
nama_merchant VARCHAR(255) NOT NULL,
kategori_bisnis VARCHAR(100),
alamat_merchant TEXT,
tanggal_bergabung DATE,
status_aktif VARCHAR(20) DEFAULT 'Aktif',
rating_merchant DECIMAL(3, 2),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Master User
CREATE TABLE users (
user_id VARCHAR(50) PRIMARY KEY, -- Ini akan menjadi user_id_sumber di ClickHouse
nama_lengkap VARCHAR(255) NOT NULL,
nomor_telepon VARCHAR(50),
email VARCHAR(255),
tanggal_pendaftaran DATE,
tingkat_loyalitas VARCHAR(50),
status_akun VARCHAR(20) DEFAULT 'Aktif',
jenis_kelamin VARCHAR(20),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Master Driver
CREATE TABLE drivers (
driver_id VARCHAR(50) PRIMARY KEY,
nama_mitra VARCHAR(255) NOT NULL,
jenis_kendaraan VARCHAR(50),
plat_nomor VARCHAR(20),
status_aktif VARCHAR(20) DEFAULT 'Aktif',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Master Location
CREATE TABLE locations (
location_id VARCHAR(50) PRIMARY KEY,
nama_wilayah VARCHAR(255),
kota VARCHAR(100),
provinsi VARCHAR(100),
kode_pos VARCHAR(10),
latitude DOUBLE PRECISION,
longitude DOUBLE PRECISION
);

-- Tabel Master Promo
CREATE TABLE promos (
promo_id VARCHAR(50) PRIMARY KEY,
kode_promo VARCHAR(50) UNIQUE NOT NULL,
nama_kampanye VARCHAR(255),
jenis_diskon VARCHAR(50),
nilai_maksimal DECIMAL(10, 2)
);

-- Tabel Master Payment Method
CREATE TABLE payment_methods (
payment_method_id VARCHAR(50) PRIMARY KEY,
jenis_pembayaran VARCHAR(50),
penyedia_layanan VARCHAR(100),
kategori_pembayaran VARCHAR(50)
);

-- Tabel Master Status (Lookup)
CREATE TABLE statuses (
status_id VARCHAR(50) PRIMARY KEY,
alasan_pembatalan VARCHAR(255),
kategori_status VARCHAR(50)
);

-- Tabel Transaksi GoFood
CREATE TABLE gofood_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    status_id VARCHAR(50) REFERENCES statuses(status_id),
    merchant_id VARCHAR(50) REFERENCES merchants(merchant_id),
    driver_id VARCHAR(50) REFERENCES drivers(driver_id),
    location_delivery_id VARCHAR(50) REFERENCES locations(location_id),
    promo_id VARCHAR(50) REFERENCES promos(promo_id),
    payment_method_id VARCHAR(50) REFERENCES payment_methods(payment_method_id),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    harga_makanan_total DECIMAL(12, 2),
    biaya_pengantaran DECIMAL(12, 2),
    biaya_layanan DECIMAL(12, 2),
    diskon_promo DECIMAL(12, 2),
    total_pembayaran DECIMAL(12, 2),
    komisi_merchant DECIMAL(12, 2),
    laba_kotor DECIMAL(12, 2),
    waktu_persiapan_menit INTEGER
);

-- Tabel Transaksi GoSend
CREATE TABLE gosend_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    status_id VARCHAR(50) REFERENCES statuses(status_id),
    driver_id VARCHAR(50) REFERENCES drivers(driver_id),
    location_sender_id VARCHAR(50) REFERENCES locations(location_id),
    location_receiver_id VARCHAR(50) REFERENCES locations(location_id),
    promo_id VARCHAR(50) REFERENCES promos(promo_id),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ongkos_kirim DECIMAL(12, 2),
    biaya_asuransi DECIMAL(12, 2),
    potongan_promo DECIMAL(12, 2),
    total_biaya_kirim DECIMAL(12, 2),
    berat_paket_kg DECIMAL(5, 2),
    estimasi_waktu_sampai INTEGER,
    nilai_rating_pengiriman INTEGER
);

-- Tabel Transaksi GoRide
CREATE TABLE goride_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    status_id VARCHAR(50) REFERENCES statuses(status_id),
    driver_id VARCHAR(50) REFERENCES drivers(driver_id),
    location_pickup_id VARCHAR(50) REFERENCES locations(location_id),
    location_dropoff_id VARCHAR(50) REFERENCES locations(location_id),
    promo_id VARCHAR(50) REFERENCES promos(promo_id),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tarif_dasar DECIMAL(12, 2),
    biaya_tambahan_permintaan DECIMAL(12, 2),
    potongan_promo DECIMAL(12, 2),
    total_biaya_penumpang DECIMAL(12, 2),
    jarak_km DECIMAL(6, 2),
    durasi_menit INTEGER,
    nilai_rating_driver INTEGER
);

-- Tabel Transaksi GoPay
CREATE TABLE gopay_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    status_id VARCHAR(50) REFERENCES statuses(status_id),
    payment_method_id VARCHAR(50) REFERENCES payment_methods(payment_method_id),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nilai_transaksi DECIMAL(12, 2),
    biaya_admin DECIMAL(12, 2),
    cashback_diterima DECIMAL(12, 2),
    saldo_sebelum DECIMAL(12, 2),
    saldo_sesudah DECIMAL(12, 2),
    status_transaksi VARCHAR(50),
    biaya_transfer DECIMAL(12, 2),
    pajak_transaksi DECIMAL(12, 2)
);