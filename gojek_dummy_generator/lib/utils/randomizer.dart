import 'dart:math';
import 'package:uuid/uuid.dart';

class Randomizer {
  static final _random = Random();
  static const _uuid = Uuid();

  // Generate UUID (contoh: 8f7b3a...)
  static String get generateTxId => _uuid.v4().substring(0, 8);

  // Mengambil ID acak sesuai jumlah data yang kita seed sebelumnya
  static String get userId =>
      'USR-${(_random.nextInt(50) + 1).toString().padLeft(3, '0')}';
  static String get merchantId =>
      'MCH-${(_random.nextInt(20) + 1).toString().padLeft(3, '0')}';
  static String get driverId =>
      'DRV-${(_random.nextInt(30) + 1).toString().padLeft(3, '0')}';
  static String get locationId =>
      'LOC-${(_random.nextInt(5) + 1).toString().padLeft(3, '0')}';
  static String get promoId =>
      'PRM-${(_random.nextInt(3) + 1).toString().padLeft(3, '0')}';
  static String get paymentMethodId =>
      'PAY-${(_random.nextInt(3) + 1).toString().padLeft(3, '0')}';

  // Status: 80% Selesai (STS-001), 20% Dibatalkan (STS-002 / STS-003)
  static String get statusId {
    int chance = _random.nextInt(100);
    if (chance < 80) return 'STS-001';
    if (chance < 90) return 'STS-002';
    return 'STS-003';
  }

  // Membuat tanggal acak dalam 30 hari terakhir agar analitik ClickHouse terlihat hidup
  static String get transactionDate {
    final daysAgo = _random.nextInt(30);
    final hoursAgo = _random.nextInt(24);
    final minutesAgo = _random.nextInt(60);
    final date = DateTime.now().subtract(
      Duration(days: daysAgo, hours: hoursAgo, minutes: minutesAgo),
    );
    return date.toIso8601String();
  }

  // Angka acak dengan kelipatan tertentu (misal harga selalu kelipatan 1000)
  static double nominal(int min, int max, int multiplier) {
    return ((_random.nextInt(max - min + 1) + min) * multiplier).toDouble();
  }
}
