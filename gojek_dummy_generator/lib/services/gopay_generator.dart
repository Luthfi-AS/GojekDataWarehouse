import 'dart:math';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../utils/randomizer.dart';

class GoPayGenerator {
  static final _supabase = Supabase.instance.client;
  static final _random = Random();

  static Future<void> run({
    required int count,
    required Function(String) onLog,
  }) async {
    try {
      List<Map<String, dynamic>> batchData = [];

      for (int i = 0; i < count; i++) {
        // 1. Menentukan Jenis Transaksi (Top Up, Transfer, atau Payment)
        int tipeChance = _random.nextInt(100);
        String tipeTransaksi;
        if (tipeChance < 30) {
          tipeTransaksi = 'Top Up';
        } else if (tipeChance < 60) {
          tipeTransaksi = 'Transfer';
        } else {
          tipeTransaksi = 'Payment';
        }

        // 2. Kalkulasi Nilai Transaksi dan Saldo
        // Nilai transaksi antara Rp 10.000 - Rp 500.000
        double nilaiTransaksi = Randomizer.nominal(10, 500, 1000);

        // Asumsi saldo sebelum selalu lebih besar dari nilai transaksi (agar tidak minus)
        double saldoSebelum =
            nilaiTransaksi + Randomizer.nominal(50, 1500, 1000);

        double biayaAdmin = 0.0;
        double biayaTransfer = 0.0;
        double pajakTransaksi = 0.0;
        double cashbackDiterima = 0.0;
        double saldoSesudah = saldoSebelum;

        // 3. Logika Finansial Berdasarkan Tipe
        if (tipeTransaksi == 'Top Up') {
          // Top up biasanya kena admin Rp 1.000
          biayaAdmin = 1000.0;
          saldoSesudah = saldoSebelum + nilaiTransaksi - biayaAdmin;
        } else if (tipeTransaksi == 'Transfer') {
          // Transfer ke bank lain kena Rp 2.500, ke sesama GoPay Rp 0
          biayaTransfer = (_random.nextBool()) ? 2500.0 : 0.0;
          saldoSesudah = saldoSebelum - nilaiTransaksi - biayaTransfer;
        } else {
          // Payment (Belanja)
          // Asumsi 20% transaksi kena PB1 (Pajak Resto 10% / 11%)
          if (_random.nextInt(5) == 0) {
            pajakTransaksi = (nilaiTransaksi * 0.11).roundToDouble();
          }
          // Asumsi 25% transaksi dapat cashback
          if (_random.nextInt(4) == 0) {
            cashbackDiterima = Randomizer.nominal(2, 15, 1000);
          }
          saldoSesudah =
              saldoSebelum - nilaiTransaksi - pajakTransaksi + cashbackDiterima;
        }

        String statusId = Randomizer.statusId;

        // 4. Handling Jika Transaksi Gagal/Batal
        // Jika statusnya bukan Selesai (STS-001), maka saldo sesudah = saldo sebelum
        if (statusId != 'STS-001') {
          saldoSesudah = saldoSebelum;
          biayaAdmin = 0.0;
          biayaTransfer = 0.0;
          pajakTransaksi = 0.0;
          cashbackDiterima = 0.0;
        }

        batchData.add({
          'transaction_id': 'GP-${Randomizer.generateTxId}',
          'user_id': Randomizer.userId,
          'status_id': statusId,
          'payment_method_id': Randomizer.paymentMethodId,
          'transaction_date': Randomizer.transactionDate,

          'nilai_transaksi': nilaiTransaksi,
          'biaya_admin': biayaAdmin,
          'cashback_diterima': cashbackDiterima,
          'saldo_sebelum': saldoSebelum,
          'saldo_sesudah': saldoSesudah,
          'status_transaksi': tipeTransaksi,
          'biaya_transfer': biayaTransfer,
          'pajak_transaksi': pajakTransaksi,
        });
      }

      // 5. Insert massal ke Supabase
      await _supabase.from('gopay_transactions').insert(batchData);
    } catch (e) {
      onLog('[ERROR] Gagal generate GoPay: $e');
      throw Exception(e);
    }
  }
}
