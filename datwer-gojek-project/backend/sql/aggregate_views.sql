-- 1. Tabel Penampung (Target)
CREATE TABLE olap_gofood_merchant_daily (
    tanggal Date,
    kota String,
    nama_merchant String,
    kategori_bisnis String,
    total_transaksi UInt32,
    total_pendapatan_kotor Float64,
    total_diskon_promo Float64,
    total_laba_kotor_gojek Float64,
    rata_rata_waktu_persiapan Float64
) ENGINE = SummingMergeTree()
ORDER BY (tanggal, kota, nama_merchant);

-- 2. Materialized View (Pipa Otomatis)
CREATE MATERIALIZED VIEW mv_gofood_merchant_daily 
TO olap_gofood_merchant_daily
AS
SELECT 
    d_date.tanggal AS tanggal,
    d_loc.kota AS kota,
    d_merch.nama_merchant AS nama_merchant,
    d_merch.kategori_bisnis AS kategori_bisnis,
    count(f.gofood_fact_key) AS total_transaksi,
    sum(f.total_pembayaran) AS total_pendapatan_kotor,
    sum(f.diskon_promo) AS total_diskon_promo,
    sum(f.laba_kotor) AS total_laba_kotor_gojek,
    avg(f.waktu_persiapan_menit) AS rata_rata_waktu_persiapan
FROM fact_gofood f
JOIN dim_date d_date ON f.date_key = d_date.date_key
JOIN dim_merchant d_merch ON f.merchant_key = d_merch.merchant_key
JOIN dim_location d_loc ON f.location_delivery_key = d_loc.location_key
WHERE d_merch.is_active = 1 AND d_loc.is_active = 1
GROUP BY tanggal, kota, nama_merchant, kategori_bisnis;

CREATE TABLE olap_goride_ops_daily (
    tanggal Date,
    kota_jemputan String,
    jenis_kendaraan String,
    total_perjalanan UInt32,         -- Hanya menghitung trip dengan status 'Sukses'
    total_jarak_km Float64,
    total_biaya_tambahan Float64,
    total_rating_driver UInt64       -- Menggantikan AVG menjadi akumulasi SUM untuk akurasi data
) ENGINE = SummingMergeTree()
ORDER BY (tanggal, kota_jemputan, jenis_kendaraan);

-- 2. Materialized View (Pipa Otomatis)
CREATE MATERIALIZED VIEW default.mv_goride_ops_daily TO default.olap_goride_ops_daily (
    `tanggal` Date,
    `kota_jemputan` String,
    `jenis_kendaraan` String,
    `total_perjalanan` UInt64,
    `total_jarak_km` Float64,
    `total_biaya_tambahan` Float64,
    `total_rating_driver` UInt64
) AS
SELECT
    d_date.tanggal AS tanggal,
    d_loc.kota AS kota_jemputan,
    d_drv.jenis_kendaraan AS jenis_kendaraan,
    count(f.goride_fact_key) AS total_perjalanan,
    sum(f.jarak_km) AS total_jarak_km,
    sum(f.biaya_tambahan_permintaan) AS total_biaya_tambahan,
    sum(CAST(f.nilai_rating_driver, 'UInt64')) AS total_rating_driver
FROM
    default.fact_goride AS f
    INNER JOIN default.dim_date AS d_date ON f.date_key = d_date.date_key
    INNER JOIN default.dim_location AS d_loc ON f.location_pickup_key = d_loc.location_key
    INNER JOIN default.dim_driver AS d_drv ON f.driver_key = d_drv.driver_key
    INNER JOIN default.dim_status AS d_stat ON f.status_key = d_stat.status_key
WHERE
    (d_loc.is_active = 1)
    AND (d_drv.is_active = 1)
    AND (d_stat.kategori_status = 'Selesai')
GROUP BY
    tanggal,
    kota_jemputan,
    jenis_kendaraan

    
-- 1. Tabel Penampung (Target)
CREATE TABLE olap_gopay_finance_daily (
    tanggal Date,
    status_transaksi String,
    metode_pembayaran String,
    total_volume_transaksi UInt32,
    nilai_transaksi_total Float64,
    total_biaya_admin Float64,
    total_cashback_dibakar Float64
) ENGINE = SummingMergeTree()
ORDER BY (tanggal, status_transaksi, metode_pembayaran);


CREATE MATERIALIZED VIEW mv_gopay_finance_daily 
TO olap_gopay_finance_daily
AS
SELECT 
    d_date.tanggal AS tanggal,
    f.status_transaksi AS status_transaksi,
    d_pay.jenis_pembayaran AS metode_pembayaran,
    count(f.gopay_fact_key) AS total_volume_transaksi,
    sum(f.nilai_transaksi) AS nilai_transaksi_total,
    sum(f.biaya_admin) AS total_biaya_admin,
    sum(f.cashback_diterima) AS total_cashback_dibakar
FROM fact_gopay f
JOIN dim_date d_date ON f.date_key = d_date.date_key
JOIN dim_payment_method d_pay ON f.payment_method_key = d_pay.payment_method_key
WHERE d_pay.is_active = 1
GROUP BY tanggal, status_transaksi, metode_pembayaran;

-- 1. Tabel Penampung (Target)
CREATE TABLE olap_demand_forecasting_daily (
    tanggal Date,
    nama_hari String,
    status_libur String,
    nama_wilayah String,
    total_order_gofood UInt32,
    total_order_goride UInt32,
    total_order_gosend UInt32
) ENGINE = SummingMergeTree()
ORDER BY (tanggal, nama_wilayah);

-- 2. Materialized View (Pipa Otomatis)
-- Karena ini menggabungkan beberapa fakta, kita menggunakan UNION ALL di dalam subquery
CREATE MATERIALIZED VIEW mv_demand_forecasting_daily 
TO olap_demand_forecasting_daily
AS
SELECT 
    d_date.tanggal AS tanggal,
    d_date.nama_hari AS nama_hari,
    d_date.status_libur AS status_libur,
    d_loc.nama_wilayah AS nama_wilayah,
    sum(if(layanan = 'GoFood', 1, 0)) AS total_order_gofood,
    sum(if(layanan = 'GoRide', 1, 0)) AS total_order_goride,
    sum(if(layanan = 'GoSend', 1, 0)) AS total_order_gosend
FROM (
    SELECT date_key, location_delivery_key AS loc_key, 'GoFood' AS layanan FROM fact_gofood
    UNION ALL
    SELECT date_key, location_pickup_key AS loc_key, 'GoRide' AS layanan FROM fact_goride
    UNION ALL
    SELECT date_key, location_sender_key AS loc_key, 'GoSend' AS layanan FROM fact_gosend
) gabungan
JOIN dim_date d_date ON gabungan.date_key = d_date.date_key
JOIN dim_location d_loc ON gabungan.loc_key = d_loc.location_key
WHERE d_loc.is_active = 1
GROUP BY tanggal, nama_hari, status_libur, nama_wilayah;