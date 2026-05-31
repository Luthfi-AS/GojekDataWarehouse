import 'package:flutter/material.dart';
import '../../core/app_colors.dart';

class MasterDataCard extends StatelessWidget {
  final bool isSeeding;
  final VoidCallback onSeed;

  const MasterDataCard({
    super.key,
    required this.isSeeding,
    required this.onSeed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.border,
        ), // Menggunakan border standar
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04), // Shadow standar
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header Kritis telah dihapus ──
          const Padding(
            padding: EdgeInsets.fromLTRB(14, 14, 14, 0),
            child: Column(
              children: [
                MasterDataRow(
                  icon: Icons.person_rounded,
                  label: 'Users',
                  description: '50 akun pengguna — nama & lokasi',
                  count: '50',
                ),
                SizedBox(height: 2),
                Divider(height: 1, color: AppColors.border),
                SizedBox(height: 2),
                MasterDataRow(
                  icon: Icons.storefront_rounded,
                  label: 'Merchants',
                  description: '20 outlet (Mie Gacoan, dll.)',
                  count: '20',
                ),
                SizedBox(height: 2),
                Divider(height: 1, color: AppColors.border),
                SizedBox(height: 2),
                MasterDataRow(
                  icon: Icons.two_wheeler_rounded,
                  label: 'Drivers',
                  description: '30 mitra GoRide + GoSend aktif',
                  count: '30',
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(14),
            child: SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: isSeeding ? null : onSeed,
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.gojekGreen,
                  disabledBackgroundColor: AppColors.gojekGreen.withOpacity(
                    0.38,
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 13),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  elevation: 0,
                ),
                icon: isSeeding
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.rocket_launch_rounded, size: 17),
                label: Text(
                  isSeeding
                      ? 'Menyiapkan Data Master...'
                      : 'Seed Master Data (Users, Merchants, Drivers)',
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    letterSpacing: -0.2,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class MasterDataRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String description;
  final String count;

  const MasterDataRow({
    super.key,
    required this.icon,
    required this.label,
    required this.description,
    required this.count,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(7),
            decoration: BoxDecoration(
              color: AppColors.gojekGreenLight,
              borderRadius: BorderRadius.circular(7),
            ),
            child: Icon(icon, size: 15, color: AppColors.gojekGreen),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  description,
                  style: const TextStyle(
                    fontSize: 10.5,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: AppColors.gojekGreenLight,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              count,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: AppColors.gojekGreen,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
