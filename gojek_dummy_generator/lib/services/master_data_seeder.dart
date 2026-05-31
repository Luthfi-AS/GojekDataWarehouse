import 'dart:math';
import 'package:supabase_flutter/supabase_flutter.dart';

class MasterDataSeeder {
  static final _supabase = Supabase.instance.client;
  static final _random = Random();

  // Fungsi utama untuk menjalankan semua seeder
  static Future<void> run({required Function(String) onLog}) async {
    try {
      await _seedLocations(onLog);
      await _seedPromos(onLog);
      await _seedPaymentMethods(onLog);
      await _seedStatuses(onLog);
      await _seedMerchants(onLog);
      await _seedUsers(onLog);
      await _seedDrivers(onLog);
      onLog('[SUCCESS] Seluruh Master Data berhasil di-upsert ke Supabase!');
    } catch (e) {
      onLog('[ERROR] Gagal melakukan seeding: $e');
      throw Exception(e);
    }
  }

  static Future<void> _seedLocations(Function(String) onLog) async {
    final locations = [
      {
        'location_id': 'LOC-001',
        'nama_wilayah': 'Jatinangor',
        'kota': 'Sumedang',
        'provinsi': 'Jawa Barat',
        'kode_pos': '45363',
        'latitude': -6.930,
        'longitude': 107.774,
      },
      {
        'location_id': 'LOC-002',
        'nama_wilayah': 'Bojongsoang',
        'kota': 'Bandung',
        'provinsi': 'Jawa Barat',
        'kode_pos': '40288',
        'latitude': -6.974,
        'longitude': 107.630,
      },
      {
        'location_id': 'LOC-003',
        'nama_wilayah': 'Buah Batu',
        'kota': 'Bandung',
        'provinsi': 'Jawa Barat',
        'kode_pos': '40286',
        'latitude': -6.953,
        'longitude': 107.628,
      },
      {
        'location_id': 'LOC-004',
        'nama_wilayah': 'Dipatiukur',
        'kota': 'Bandung',
        'provinsi': 'Jawa Barat',
        'kode_pos': '40132',
        'latitude': -6.890,
        'longitude': 107.615,
      },
      {
        'location_id': 'LOC-005',
        'nama_wilayah': 'Dago',
        'kota': 'Bandung',
        'provinsi': 'Jawa Barat',
        'kode_pos': '40135',
        'latitude': -6.874,
        'longitude': 107.618,
      },
    ];
    await _supabase.from('locations').upsert(locations);
    onLog(' > [OK] Tabel locations (5 baris)');
  }

  static Future<void> _seedPromos(Function(String) onLog) async {
    final promos = [
      {
        'promo_id': 'PRM-001',
        'kode_promo': 'GOFOODAJA',
        'nama_kampanye': 'Diskon Makanan',
        'jenis_diskon': 'Persentase',
        'nilai_maksimal': 20000,
      },
      {
        'promo_id': 'PRM-002',
        'kode_promo': 'GORIDEMURAH',
        'nama_kampanye': 'Potongan Transport',
        'jenis_diskon': 'Nominal',
        'nilai_maksimal': 10000,
      },
      {
        'promo_id': 'PRM-003',
        'kode_promo': 'NOPROMO',
        'nama_kampanye': 'Tidak Ada Promo',
        'jenis_diskon': 'None',
        'nilai_maksimal': 0,
      },
    ];
    await _supabase.from('promos').upsert(promos);
    onLog(' > [OK] Tabel promos (3 baris)');
  }

  static Future<void> _seedPaymentMethods(Function(String) onLog) async {
    final payments = [
      {
        'payment_method_id': 'PAY-001',
        'jenis_pembayaran': 'E-Wallet',
        'penyedia_layanan': 'GoPay',
        'kategori_pembayaran': 'Digital',
      },
      {
        'payment_method_id': 'PAY-002',
        'jenis_pembayaran': 'Tunai',
        'penyedia_layanan': 'Cash',
        'kategori_pembayaran': 'Fisik',
      },
      {
        'payment_method_id': 'PAY-003',
        'jenis_pembayaran': 'Kartu Debit',
        'penyedia_layanan': 'Bank Jago',
        'kategori_pembayaran': 'Bank',
      },
    ];
    await _supabase.from('payment_methods').upsert(payments);
    onLog(' > [OK] Tabel payment_methods (3 baris)');
  }

  static Future<void> _seedStatuses(Function(String) onLog) async {
    final statuses = [
      {
        'status_id': 'STS-001',
        'alasan_pembatalan': null,
        'kategori_status': 'Selesai',
      },
      {
        'status_id': 'STS-002',
        'alasan_pembatalan': 'Toko Tutup',
        'kategori_status': 'Dibatalkan',
      },
      {
        'status_id': 'STS-003',
        'alasan_pembatalan': 'Driver Tidak Ditemukan',
        'kategori_status': 'Dibatalkan',
      },
    ];
    await _supabase.from('statuses').upsert(statuses);
    onLog(' > [OK] Tabel statuses (3 baris)');
  }

  static Future<void> _seedMerchants(Function(String) onLog) async {
    final merchants = List.generate(20, (index) {
      final id = index + 1;
      // Menyelipkan beberapa data spesifik agar realistis
      String nama = 'Merchant $id';
      if (id == 1) nama = 'Mie Gacoan Jatinangor';
      if (id == 2) nama = 'Geprek Bensu Buah Batu';
      if (id == 3) nama = 'Kopi Kenangan Dago';

      return {
        'merchant_id': 'MCH-${id.toString().padLeft(3, '0')}',
        'nama_merchant': nama,
        'kategori_bisnis': (id % 2 == 0) ? 'Restoran' : 'Minuman',
        'alamat_merchant': 'Jl. Raya No. $id, Bandung',
        'tanggal_bergabung': '2024-01-15',
        'status_aktif': 'Aktif',
        'rating_merchant': (_random.nextDouble() * 1.5 + 3.5).toStringAsFixed(
          1,
        ), // Rating 3.5 - 5.0
      };
    });
    await _supabase.from('merchants').upsert(merchants);
    onLog(' > [OK] Tabel merchants (20 baris)');
  }

  static Future<void> _seedUsers(Function(String) onLog) async {
    final names = [
      'Luthfi',
      'Athallah',
      'Bunga',
      'Danish',
      'Ainur',
      'Azhari',
      'Budi',
      'Siti',
      'Andi',
      'Rina',
    ];
    final users = List.generate(50, (index) {
      final id = index + 1;
      return {
        'user_id': 'USR-${id.toString().padLeft(3, '0')}',
        'nama_lengkap': '${names[index % names.length]} Pengguna $id',
        'nomor_telepon': '08123456${id.toString().padLeft(4, '0')}',
        'email': 'user$id@example.com',
        'tanggal_pendaftaran': '2023-05-20',
        'tingkat_loyalitas': (id % 5 == 0)
            ? 'Platinum'
            : (id % 2 == 0 ? 'Gold' : 'Basic'),
        'status_akun': 'Aktif',
        'jenis_kelamin': (id % 2 == 0) ? 'Laki-laki' : 'Perempuan',
      };
    });
    await _supabase.from('users').upsert(users);
    onLog(' > [OK] Tabel users (50 baris)');
  }

  static Future<void> _seedDrivers(Function(String) onLog) async {
    final drivers = List.generate(30, (index) {
      final id = index + 1;
      return {
        'driver_id': 'DRV-${id.toString().padLeft(3, '0')}',
        'nama_mitra': 'Mitra Driver $id',
        'jenis_kendaraan': (id % 5 == 0) ? 'Mobil' : 'Motor',
        'plat_nomor': 'D ${1000 + id} XYZ',
        'status_aktif': 'Aktif',
      };
    });
    await _supabase.from('drivers').upsert(drivers);
    onLog(' > [OK] Tabel drivers (30 baris)');
  }
}
