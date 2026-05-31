import 'package:supabase_flutter/supabase_flutter.dart';
import '../utils/randomizer.dart';

class GoFoodGenerator {
  static final _supabase = Supabase.instance.client;

  static Future<void> run({
    required int count,
    required Function(String) onLog,
  }) async {
    try {
      List<Map<String, dynamic>> batchData = [];

      for (int i = 0; i < count; i++) {
        // Kalkulasi Bisnis GoFood
        double hargaMakanan = Randomizer.nominal(20, 150, 1000); // 20rb - 150rb
        double biayaAntar = Randomizer.nominal(8, 25, 1000); // 8rb - 25rb
        double biayaLayanan = 3000.0;

        // Asumsi Diskon Promo Acak (0 sampai 15rb)
        double diskon =
            (Randomizer.statusId == 'STS-001' &&
                Randomizer.promoId != 'PRM-003')
            ? Randomizer.nominal(0, 15, 1000)
            : 0.0;

        double totalPembayaran =
            (hargaMakanan + biayaAntar + biayaLayanan) - diskon;
        double komisiMerchant =
            hargaMakanan * 0.20; // Gojek ambil 20% dari makanan
        double labaKotor =
            komisiMerchant + biayaLayanan; // Pendapatan kotor Gojek

        batchData.add({
          'transaction_id': 'GF-${Randomizer.generateTxId}',
          'user_id': Randomizer.userId,
          'status_id': Randomizer.statusId,
          'merchant_id': Randomizer.merchantId,
          'driver_id': Randomizer.driverId,
          'location_delivery_id': Randomizer.locationId,
          'promo_id': Randomizer.promoId,
          'payment_method_id': Randomizer.paymentMethodId,
          'transaction_date': Randomizer.transactionDate,

          'harga_makanan_total': hargaMakanan,
          'biaya_pengantaran': biayaAntar,
          'biaya_layanan': biayaLayanan,
          'diskon_promo': diskon,
          'total_pembayaran': totalPembayaran,
          'komisi_merchant': komisiMerchant,
          'laba_kotor': labaKotor,
          'waktu_persiapan_menit': Randomizer.nominal(
            10,
            45,
            1,
          ).toInt(), // 10 - 45 menit
        });
      }

      // Insert massal ke Supabase
      await _supabase.from('gofood_transactions').insert(batchData);
    } catch (e) {
      onLog('[ERROR] Gagal generate GoFood: $e');
      throw Exception(e);
    }
  }
}
