import 'dart:async';
import 'package:flutter/material.dart';

import '../core/app_colors.dart';
import '../models/panel_models.dart';
import 'widgets/components.dart';

import '../services/master_data_seeder.dart';
import '../services/gofood_generator.dart';
import '../services/goride_generator.dart';
import '../services/gosend_generator.dart';
import '../services/gopay_generator.dart';

class ControlPanelScreen extends StatefulWidget {
  const ControlPanelScreen({super.key});

  @override
  State<ControlPanelScreen> createState() => _ControlPanelScreenState();
}

class _ControlPanelScreenState extends State<ControlPanelScreen> {
  // State
  final Map<String, double> _counts = {
    'gofood': 50,
    'goride': 50,
    'gosend': 50,
    'gopay': 50,
  };
  bool _isSeedingMaster = false;
  final Map<String, bool> _isGenerating = {
    'gofood': false,
    'goride': false,
    'gosend': false,
    'gopay': false,
  };

  final List<LogEntry> _logs = [];
  final ScrollController _consoleScroll = ScrollController();

  // Config
  final List<GeneratorConfig> _generators = const [
    GeneratorConfig(
      serviceKey: 'gofood',
      title: 'GoFood',
      subtitle: 'Order Makanan',
      icon: Icons.fastfood_rounded,
      accentColor: Color(0xFFEA580C),
    ),
    GeneratorConfig(
      serviceKey: 'goride',
      title: 'GoRide',
      subtitle: 'Ojek Online',
      icon: Icons.two_wheeler_rounded,
      accentColor: Color(0xFF2563EB),
    ),
    GeneratorConfig(
      serviceKey: 'gosend',
      title: 'GoSend',
      subtitle: 'Kurir Instan',
      icon: Icons.local_shipping_rounded,
      accentColor: Color(0xFF7C3AED),
    ),
    GeneratorConfig(
      serviceKey: 'gopay',
      title: 'GoPay',
      subtitle: 'Dompet Digital',
      icon: Icons.account_balance_wallet_rounded,
      accentColor: Color(0xFF0891B2),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _initLogs();
  }

  @override
  void dispose() {
    _consoleScroll.dispose();
    super.dispose();
  }

  void _initLogs() {
    _addLog(LogType.info, 'Gojek Data Engine v2.1.0 dimuat...');
    Future.delayed(
      const Duration(milliseconds: 900),
      () => _addLog(
        LogType.success,
        '[CONNECTED] Supabase PostgreSQL 15.4 aktif.',
      ),
    );
  }

  void _addLog(LogType type, String message) {
    if (!mounted) return;
    setState(() => _logs.add(LogEntry(type: type, message: message)));
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_consoleScroll.hasClients) {
        _consoleScroll.animateTo(
          _consoleScroll.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  // Actions
  Future<void> _onSeedMasterData() async {
    if (_isSeedingMaster) return;
    setState(() => _isSeedingMaster = true);
    _addLog(LogType.info, 'Memulai proses seed master data ke Supabase...');

    try {
      await MasterDataSeeder.run(
        onLog: (msg) => _addLog(
          msg.contains('[ERROR]')
              ? LogType.error
              : msg.contains('[SUCCESS]')
              ? LogType.success
              : LogType.info,
          msg,
        ),
      );
    } catch (e) {
      _addLog(LogType.error, 'Proses terhenti karena error.');
    }
    if (mounted) setState(() => _isSeedingMaster = false);
  }

  Future<void> _onGenerate(String serviceKey) async {
    if (_isGenerating[serviceKey] == true) return;
    final count = _counts[serviceKey]!.toInt();
    final config = _generators.firstWhere((g) => g.serviceKey == serviceKey);

    setState(() => _isGenerating[serviceKey] = true);
    _addLog(
      LogType.info,
      'Memulai generasi $count transaksi ${config.title}...',
    );

    try {
      if (serviceKey == 'gofood') {
        await GoFoodGenerator.run(
          count: count,
          onLog: (msg) => _addLog(
            msg.contains('[ERROR]') ? LogType.error : LogType.success,
            msg,
          ),
        );
      } else if (serviceKey == 'goride') {
        await GoRideGenerator.run(
          count: count,
          onLog: (msg) => _addLog(
            msg.contains('[ERROR]') ? LogType.error : LogType.success,
            msg,
          ),
        );
      } else if (serviceKey == 'gosend') {
        await GoSendGenerator.run(
          count: count,
          onLog: (msg) => _addLog(
            msg.contains('[ERROR]') ? LogType.error : LogType.success,
            msg,
          ),
        );
      } else if (serviceKey == 'gopay') {
        await GoPayGenerator.run(
          count: count,
          onLog: (msg) => _addLog(
            msg.contains('[ERROR]') ? LogType.error : LogType.success,
            msg,
          ),
        );
      }

      _addLog(
        LogType.success,
        '[SUCCESS] $count transaksi ${config.title} berhasil dikirim ke database.',
      );
    } catch (e) {
      _addLog(LogType.error, '[FAILED] Transaksi gagal: $e');
    }
    if (mounted) setState(() => _isGenerating[serviceKey] = false);
  }

  void _clearConsole() {
    setState(() {
      _logs.clear();
      _logs.add(
        LogEntry(
          type: LogType.warning,
          message: 'Console dibersihkan oleh user.',
        ),
      );
    });
  }

  // ─── BUILDER ──────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: _buildAppBar(),
      body: ListView(
        padding: const EdgeInsets.only(bottom: 40),
        children: [
          const SizedBox(height: 24), // Memberi sedikit jarak dari atas
          const SectionLabel(number: '01', title: 'Master Data Initialization'),
          const SizedBox(height: 10),
          MasterDataCard(
            isSeeding: _isSeedingMaster,
            onSeed: _onSeedMasterData,
          ),
          const SizedBox(height: 28),
          const SectionLabel(number: '02', title: 'Transaction Generators'),
          const SizedBox(height: 10),
          _buildGeneratorGrid(),
          const SizedBox(height: 28),
          const SectionLabel(number: '03', title: 'Execution Console'),
          const SizedBox(height: 10),
          ExecutionConsole(
            logs: _logs,
            scrollController: _consoleScroll,
            onClear: _clearConsole,
          ),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: AppColors.surface,
      elevation: 0,
      scrolledUnderElevation: 0,
      titleSpacing: 16,
      title: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.gojekGreen,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.bolt_rounded,
              color: Colors.white,
              size: 20,
            ),
          ),
          const SizedBox(width: 10),
          const Text(
            'Gojek Data Engine',
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w800,
              color: AppColors.textPrimary,
              letterSpacing: -0.6,
            ),
          ),
        ],
      ),
      actions: const [
        AppBarBadge(label: 'DEV', color: Color(0xFF7C3AED)),
        SizedBox(width: 10),
        AppBarBadge(label: 'v2.1', color: AppColors.textSecondary),
        SizedBox(width: 16),
      ],
      bottom: PreferredSize(
        preferredSize: const Size.fromHeight(1),
        child: Container(height: 1, color: AppColors.border),
      ),
    );
  }

  Widget _buildGeneratorGrid() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 0.82,
        ),
        itemCount: _generators.length,
        itemBuilder: (_, index) {
          final config = _generators[index];
          return GeneratorCard(
            config: config,
            count: _counts[config.serviceKey]!,
            isLoading: _isGenerating[config.serviceKey] ?? false,
            onCountChanged: (v) =>
                setState(() => _counts[config.serviceKey] = v),
            onGenerate: () => _onGenerate(config.serviceKey),
          );
        },
      ),
    );
  }
}
