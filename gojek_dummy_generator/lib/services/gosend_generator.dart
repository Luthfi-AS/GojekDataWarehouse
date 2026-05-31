import 'dart:math';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../utils/randomizer.dart';

class GoSendGenerator {
  static final _supabase = Supabase.instance.client;
  static final _random = Random();

  static Future<void> run({
    required int count,
    required Function(String) onLog,
  }) async {
    try {
      List<Map<String, dynamic>> batchData = [];

      for (int i = 0; i < count; i++) {
        // 1. Kalkulasi Karakteristik Paket
        // Berat paket acak antara 0.5 kg hingga 20.0 kg (kapasitas wajar motor)
        double beratPaket = double.parse(
          (_random.nextDouble() * 19.5 + 0.5).toStringAsFixed(1),
        );

        // Estimasi waktu sampai antara 15 hingga 120 menit
        int estimasiWaktu = _random.nextInt(106) + 15;

        // 2. Kalkulasi Biaya (Logika Bisnis GoSend)
        // Ongkos kirim dasar (simulasi jarak acak): Rp 15.000 - Rp 60.000
        double ongkosKirim = Randomizer.nominal(15, 60, 1000);

        // Tambahan biaya jika paket berat (> 10 kg)
        if (beratPaket > 10.0) {
          ongkosKirim += 10000.0;
        }

        // 30% kemungkinan pengguna menggunakan fitur asuransi barang (berkisar 2rb - 5rb)
        double biayaAsuransi = (_random.nextInt(3) == 0)
            ? Randomizer.nominal(2, 5, 1000)
            : 0.0;

        String statusId = Randomizer.statusId;
        String promoId = Randomizer.promoId;

        // 3. Kalkulasi Promo
        double potonganPromo = (statusId == 'STS-001' && promoId != 'PRM-003')
            ? Randomizer.nominal(5, 15, 1000)
            : 0.0;

        // Cegah diskon melebihi ongkos kirim dasar
        if (potonganPromo > ongkosKirim) potonganPromo = ongkosKirim;

        double totalBiayaKirim = (ongkosKirim + biayaAsuransi) - potonganPromo;

        // 4. Rating Driver (hanya jika sukses)
        int? ratingPengiriman = (statusId == 'STS-001')
            ? (_random.nextInt(2) + 4)
            : null;

        // Lokasi pengirim dan penerima harus diacak secara independen
        String senderLocation = Randomizer.locationId;
        String receiverLocation = Randomizer.locationId;
        // Pastikan lokasi pengirim dan penerima tidak sama persis (logika opsional agar realistis)
        while (receiverLocation == senderLocation) {
          receiverLocation = Randomizer.locationId;
        }

        batchData.add({
          'transaction_id': 'GS-${Randomizer.generateTxId}',
          'user_id': Randomizer.userId,
          'status_id': statusId,
          'driver_id': Randomizer.driverId,
          'location_sender_id': senderLocation,
          'location_receiver_id': receiverLocation,
          'promo_id': promoId,
          'transaction_date': Randomizer.transactionDate,

          'ongkos_kirim': ongkosKirim,
          'biaya_asuransi': biayaAsuransi,
          'potongan_promo': potonganPromo,
          'total_biaya_kirim': totalBiayaKirim,
          'berat_paket_kg': beratPaket,
          'estimasi_waktu_sampai': estimasiWaktu,
          'nilai_rating_pengiriman': ratingPengiriman,
        });
      }

      // 5. Insert massal ke Supabase
      await _supabase.from('gosend_transactions').insert(batchData);
    } catch (e) {
      onLog('[ERROR] Gagal generate GoSend: $e');
      throw Exception(e);
    }
  }
}
