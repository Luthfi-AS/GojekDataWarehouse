
-- Tabel Dimensi Merchant (SCD Type 2)
CREATE TABLE dim_merchant (
    merchant_key String,
    merchant_id_sumber String,
    nama_merchant String,
    kategori_bisnis String,
    alamat_merchant String,
    tanggal_bergabung Date,
    status_aktif String,
    rating_merchant Float32,
    -- Komponen SCD Type 2
    valid_from DateTime,
    valid_to DateTime,
    is_active UInt8
) ENGINE = MergeTree()
ORDER BY (merchant_key, valid_from);

-- Tabel Dimensi User (SCD Type 2)
CREATE TABLE dim_user (
    user_key String,
    user_id_sumber String,
    nama_lengkap String,
    nomor_telepon String,
    email String,
    tanggal_pendaftaran Date,
    tingkat_loyalitas String,
    status_akun String,
    jenis_kelamin String,
    -- Komponen SCD Type 2
    valid_from DateTime,
    valid_to DateTime,
    is_active UInt8
) ENGINE = MergeTree()
ORDER BY (user_key, valid_from);

-- Tabel Dimensi Driver (SCD Type 2)
CREATE TABLE dim_driver (
    driver_key String,
    driver_id_sumber String,
    nama_mitra String,
    jenis_kendaraan String,
    plat_nomor String,
    status_aktif String,
    -- Komponen SCD Type 2
    valid_from DateTime,
    valid_to DateTime,
    is_active UInt8
) ENGINE = MergeTree()
ORDER BY (driver_key, valid_from);

-- Tabel Dimensi Location (SCD Type 2)
CREATE TABLE dim_location (
    location_key String,
    location_id_sumber String,  
    nama_wilayah String,
    kota String,
    provinsi String,
    kode_pos String,
    latitude Float64,
    longitude Float64,
    -- Komponen SCD Type 2
    valid_from DateTime,
    valid_to DateTime,
    is_active UInt8
) ENGINE = MergeTree()
ORDER BY (location_key, valid_from);

-- Tabel Dimensi Promo (SCD Type 2)
CREATE TABLE dim_promo (
    promo_key String,
    promo_id_sumber String,     
    kode_promo String,
    nama_kampanye String,
    jenis_diskon String,
    nilai_maksimal Float32,
    -- Komponen SCD Type 2
    valid_from DateTime,
    valid_to DateTime,
    is_active UInt8
) ENGINE = MergeTree()
ORDER BY (promo_key, valid_from);

-- Tabel Dimensi PaymentMethod (SCD Type 2)
CREATE TABLE dim_payment_method (
    payment_method_key String,
    payment_method_id_sumber String,
    jenis_pembayaran String,
    penyedia_layanan String,
    kategori_pembayaran String,
    -- Komponen SCD Type 2
    valid_from DateTime,
    valid_to DateTime,
    is_active UInt8
) ENGINE = MergeTree()
ORDER BY (payment_method_key, valid_from);

-- Tabel Dimensi Date (Statis)
CREATE TABLE dim_date (
    date_key String,
    tanggal Date,
    hari Int8,
    bulan Int8,
    tahun Int16,
    kuartal Int8,
    nama_hari String,
    status_libur String
) ENGINE = MergeTree()
ORDER BY date_key;

-- Tabel Dimensi Status (Statis)
CREATE TABLE dim_status (
    status_key String,
    status_id_sumber String,    
    alasan_pembatalan String,
    kategori_status String
) ENGINE = MergeTree()
ORDER BY status_key;

-- ==========================================
-- WILAYAH TABEL FAKTA
-- ==========================================

-- Tabel Fakta GoFood
CREATE TABLE fact_gofood (
    gofood_fact_key String,
    transaction_id String,      -- [UPDATED] Kolom sumber ditambahkan (Anti-Duplikasi)
    user_key String,
    status_key String,
    merchant_key String,
    driver_key String,
    date_key String,
    location_delivery_key String,
    promo_key String,
    payment_method_key String,
    harga_makanan_total Float32,
    biaya_pengantaran Float32,
    biaya_layanan Float32,
    diskon_promo Float32,
    total_pembayaran Float32,
    komisi_merchant Float32,
    laba_kotor Float32,
    waktu_persiapan_menit Int32,
    -- Kolom Audit DW
    inserted_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(date_key)) 
ORDER BY (date_key, user_key, merchant_key);

-- Tabel Fakta GoSend
CREATE TABLE fact_gosend (
    gosend_fact_key String,
    transaction_id String,      -- [UPDATED] Kolom sumber ditambahkan (Anti-Duplikasi)
    user_key String,
    status_key String,
    driver_key String,
    date_key String,
    location_sender_key String,
    location_receiver_key String,
    promo_key String,
    ongkos_kirim Float32,
    biaya_asuransi Float32,
    potongan_promo Float32,
    total_biaya_kirim Float32,
    berat_paket_kg Float32,
    estimasi_waktu_sampai Int32,
    nilai_rating_pengiriman Int8,
    inserted_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(date_key))
ORDER BY (date_key, user_key, driver_key);

-- Tabel Fakta GoRide
CREATE TABLE fact_goride (
    goride_fact_key String,
    transaction_id String,      -- [UPDATED] Kolom sumber ditambahkan (Anti-Duplikasi)
    user_key String,
    status_key String,
    driver_key String,
    date_key String,
    location_pickup_key String,
    location_dropoff_key String,
    promo_key String,
    tarif_dasar Float32,
    biaya_tambahan_permintaan Float32,
    potongan_promo Float32,
    total_biaya_penumpang Float32,
    jarak_km Float32,
    durasi_menit Int32,
    nilai_rating_driver Int8,
    inserted_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(date_key))
ORDER BY (date_key, user_key, driver_key);

-- Tabel Fakta GoPay
CREATE TABLE fact_gopay (
    gopay_fact_key String,
    transaction_id String,      -- [UPDATED] Kolom sumber ditambahkan (Anti-Duplikasi)
    user_key String,
    status_key String,
    date_key String,
    payment_method_key String,
    nilai_transaksi Float32,
    biaya_admin Float32,
    cashback_diterima Float32,
    saldo_sebelum Float32,
    saldo_sesudah Float32,
    status_transaksi String,
    biaya_transfer Float32,
    pajak_transaksi Float32,
    inserted_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(date_key))
ORDER BY (date_key, user_key);