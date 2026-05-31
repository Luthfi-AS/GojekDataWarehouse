import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseConfig {
  // 1. Masukkan kredensial dari Dashboard Supabase Anda di sini
  // Use something like flutter_dotenv or pass via build args
  static const String _supabaseUrl = String.fromEnvironment('SUPABASE_URL');
  static const String _supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
  );

  // 2. Fungsi untuk menginisialisasi koneksi saat aplikasi pertama kali dibuka
  static Future<void> initialize() async {
    await Supabase.initialize(url: _supabaseUrl, anonKey: _supabaseAnonKey);
    print('[INFO] Koneksi Supabase Berhasil Diinisialisasi!');
  }

  // 3. Getter untuk mempermudah pemanggilan client di file generator nanti
  static SupabaseClient get client => Supabase.instance.client;
}
