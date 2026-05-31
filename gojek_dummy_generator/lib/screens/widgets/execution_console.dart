import 'package:flutter/material.dart';
import '../../core/app_colors.dart';
import '../../models/panel_models.dart';

class ExecutionConsole extends StatelessWidget {
  final List<LogEntry> logs;
  final ScrollController scrollController;
  final VoidCallback onClear;

  const ExecutionConsole({
    super.key,
    required this.logs,
    required this.scrollController,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.terminalBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2D2D2D)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.25),
            blurRadius: 20,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Column(
          children: [
            Container(
              height: 36,
              color: AppColors.terminalBar,
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Row(
                children: [
                  const TerminalTrafficLight(color: Color(0xFFFF5F57)),
                  const SizedBox(width: 6),
                  const TerminalTrafficLight(color: Color(0xFFFFBD2E)),
                  const SizedBox(width: 6),
                  const TerminalTrafficLight(color: Color(0xFF28CA41)),
                  const SizedBox(width: 12),
                  const Text(
                    'execution_console  —  bash',
                    style: TextStyle(
                      fontSize: 11,
                      color: Color(0xFF9CA3AF),
                      fontFamily: 'monospace',
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 1,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFF374151),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${logs.length} lines',
                      style: const TextStyle(
                        fontSize: 9.5,
                        color: Color(0xFF9CA3AF),
                        fontFamily: 'monospace',
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  GestureDetector(
                    onTap: onClear,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      child: const Icon(
                        Icons.delete_sweep_rounded,
                        size: 15,
                        color: Color(0xFF6B7280),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(
              height: 150,
              child: ListView.builder(
                controller: scrollController,
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 10,
                ),
                itemCount: logs.length,
                itemBuilder: (_, i) => ConsoleLine(entry: logs[i]),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class TerminalTrafficLight extends StatelessWidget {
  final Color color;
  const TerminalTrafficLight({super.key, required this.color});
  @override
  Widget build(BuildContext context) => Container(
    width: 11,
    height: 11,
    decoration: BoxDecoration(color: color, shape: BoxShape.circle),
  );
}

class ConsoleLine extends StatelessWidget {
  final LogEntry entry;
  const ConsoleLine({super.key, required this.entry});

  Color get _c {
    switch (entry.type) {
      case LogType.success:
        return AppColors.terminalGreen;
      case LogType.error:
        return AppColors.terminalRed;
      case LogType.warning:
        return AppColors.terminalYellow;
      case LogType.info:
        return AppColors.terminalText;
    }
  }

  Color get _p {
    switch (entry.type) {
      case LogType.success:
        return AppColors.terminalGreen;
      case LogType.error:
        return AppColors.terminalRed;
      case LogType.warning:
        return AppColors.terminalYellow;
      case LogType.info:
        return const Color(0xFF6B7280);
    }
  }

  @override
  Widget build(BuildContext context) {
    final hh = entry.timestamp.hour.toString().padLeft(2, '0');
    final mm = entry.timestamp.minute.toString().padLeft(2, '0');
    final ss = entry.timestamp.second.toString().padLeft(2, '0');
    return Padding(
      padding: const EdgeInsets.only(bottom: 3),
      child: RichText(
        text: TextSpan(
          style: const TextStyle(
            fontFamily: 'monospace',
            fontSize: 11,
            height: 1.55,
          ),
          children: [
            TextSpan(
              text: '$hh:$mm:$ss ',
              style: const TextStyle(color: Color(0xFF4B5563)),
            ),
            TextSpan(
              text: '> ',
              style: TextStyle(color: _p, fontWeight: FontWeight.bold),
            ),
            TextSpan(
              text: entry.message,
              style: TextStyle(color: _c),
            ),
          ],
        ),
      ),
    );
  }
}
