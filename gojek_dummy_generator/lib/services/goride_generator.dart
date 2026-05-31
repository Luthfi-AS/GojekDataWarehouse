import 'dart:math';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../utils/randomizer.dart';

class GoRideGenerator {
  static final _supabase = Supabase.instance.client;
  static final _random = Random();

  static Future<void> run({
    required int count,
    required Function(String) onLog,
  }) async {
    try {
      List<Map<String, dynamic>> batchData = [];

      for (int i = 0; i < count; i++) {
        // 1. Kalkulasi Jarak & Waktu
        // Jarak acak antara 1.0 km hingga 25.0 km
        double jarakKm = double.parse(
          (_random.nextDouble() * 24 + 1).toStringAsFixed(1),
        );
        // Asumsi kecepatan rata-rata motor di kota: 1 km butuh 3-5 menit
        int durasiMenit = (jarakKm * (3 + _random.nextInt(3))).toInt();

        // 2. Kalkulasi Tarif (Logika Bisnis GoRide)
        // Tarif dasar: Rp 10.000 untuk 3 km pertama, Rp 2.500 untuk tiap km berikutnya
        double tarifDasar = 10000.0;
        if (jarakKm > 3) {
          tarifDasar += (jarakKm - 3) * 2500.0;
        }
        // Membulatkan tarif ke kelipatan 500 terdekat agar realistis (misal 14.500)
        tarifDasar = (tarifDasar / 500).round() * 500.0;

        // 33% kemungkinan terkena biaya tambahan (Surge Pricing saat jam sibuk/hujan)
        double biayaTambahan = (_random.nextInt(3) == 0)
            ? Randomizer.nominal(2, 10, 1000)
            : 0.0;

        String statusId = Randomizer.statusId;
        String promoId = Randomizer.promoId;

        // 3. Kalkulasi Promo
        double potonganPromo = (statusId == 'STS-001' && promoId != 'PRM-003')
            ? Randomizer.nominal(5, 15, 1000)
            : 0.0;

        // Pastikan diskon tidak membuat Gojek rugi (tidak melebihi tarif dasar)
        if (potonganPromo > tarifDasar) potonganPromo = tarifDasar;

        double totalBiaya = (tarifDasar + biayaTambahan) - potonganPromo;

        // 4. Rating (Hanya berikan rating jika perjalanan selesai)
        // Rating acak antara 4 atau 5 (karena mayoritas driver mendapat bintang tinggi)
        int? ratingDriver = (statusId == 'STS-001')
            ? (_random.nextInt(2) + 4)
            : null;

        // Pastikan lokasi jemput dan antar diambil acak
        String pickupLocation = Randomizer.locationId;
        String dropoffLocation = Randomizer.locationId;

        batchData.add({
          'transaction_id': 'GR-${Randomizer.generateTxId}',
          'user_id': Randomizer.userId,
          'status_id': statusId,
          'driver_id': Randomizer.driverId,
          'location_pickup_id': pickupLocation,
          'location_dropoff_id': dropoffLocation,
          'promo_id': promoId,
          'transaction_date': Randomizer.transactionDate,

          'tarif_dasar': tarifDasar,
          'biaya_tambahan_permintaan': biayaTambahan,
          'potongan_promo': potonganPromo,
          'total_biaya_penumpang': totalBiaya,
          'jarak_km': jarakKm,
          'durasi_menit': durasiMenit,
          'nilai_rating_driver': ratingDriver,
        });
      }

      // 5. Insert massal ke Supabase
      await _supabase.from('goride_transactions').insert(batchData);
    } catch (e) {
      onLog('[ERROR] Gagal generate GoRide: $e');
      throw Exception(e);
    }
  }
}
