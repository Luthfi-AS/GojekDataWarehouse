import 'package:flutter/material.dart';

enum LogType { info, success, error, warning }

class LogEntry {
  final LogType type;
  final String message;
  final DateTime timestamp;

  LogEntry({required this.type, required this.message})
    : timestamp = DateTime.now();
}

class GeneratorConfig {
  final String serviceKey;
  final String title;
  final String subtitle;
  final IconData icon;
  final Color accentColor;

  const GeneratorConfig({
    required this.serviceKey,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.accentColor,
  });
}
