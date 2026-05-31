import 'package:flutter/material.dart';
import 'core/supabase_config.dart';
import 'screens/control_panel.dart'; // Nanti kita buat file ini

void main() async {
  // Wajib ditambahkan jika main() menggunakan async
  // Ini memastikan mesin Flutter sudah siap sebelum kita menghubungi Supabase
  WidgetsFlutterBinding.ensureInitialized();

  // Memulai koneksi ke Supabase
  await SupabaseConfig.initialize();

  runApp(const GojekDummyApp());
}

class GojekDummyApp extends StatelessWidget {
  const GojekDummyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Gojek Data Generator',
      debugShowCheckedModeBanner: false, // Menghilangkan pita "DEBUG" di pojok
      theme: ThemeData(
        // Menggunakan hijau khas Gojek sebagai warna dasar aplikasi
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF00AA13)),
        useMaterial3: true,
      ),
      // Aplikasi langsung diarahkan ke layar Control Panel
      home: const ControlPanelScreen(),
    );
  }
}
