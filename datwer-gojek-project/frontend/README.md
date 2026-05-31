frontend/                   
    ├── app/                    # WILAYAH ROUTING & PAGES (App Router)
    │   ├── globals.css         # CSS Global & Konfigurasi Tailwind v4 (Theme-aware)
    │   ├── layout.tsx          
    │   ├── page.tsx            # Halaman Home (Otomatis redirect ke /goride)
    │   ├── gofood/
    │   │   └── page.tsx        # Halaman Dashboard GoFood (Sudah modular)
    │   ├── goride/
    │   │   └── page.tsx        # Halaman Dashboard GoRide (Sudah modular)
    │   └── gopay/
    │       └── page.tsx        # Halaman Dashboard GoPay (Menunggu dirakit)
    │
    ├── components/             # WILAYAH UI COMPONENTS
    │   ├── layout/             # Komponen Kerangka Halaman
    │   │   ├── Sidebar.tsx     # Menu navigasi samping kiri
    │   │   └── PageHeader.tsx  # Header atas (Judul, filter, tombol export, & toggle tema)
    │   │
    │   ├── dashboard/          # Komponen Visualisasi Data (Reusable)
    │   │   ├── KpiCard.tsx           # Kartu metrik dengan tren (+/-)
    │   │   ├── TrendAreaChart.tsx    # Grafik garis/area tunggal (tren harian)
    │   │   ├── DualLineChart.tsx     # NEW: Grafik garis ganda (Revenue vs Promo)
    │   │   ├── DonutChart.tsx        # Grafik donat untuk perbandingan proporsi
    │   │   ├── ProgressBarList.tsx   # Daftar bar horizontal (dengan toggle Volume/Growth)
    │   │   ├── TransactionStatusCard.tsx  
    │   │   └── TopMerchantsTable.tsx # NEW: Tabel ranking dengan bar performa
    │   │
    │   ├── providers/          # Wilayah untuk Context/Providers
    │   │   └── TanstackProvider.tsx  # Client Component untuk inisialisasi QueryClient
    │   │
    │   └── ui/                 # Komponen UI dasar murni (seperti Button, Input, Modal - opsional)
    │
    ├── hooks/                  # Wilayah Custom Hooks untuk TanStack
    │   ├── queries/            # Khusus untuk fetch data (GET)
    │   │   ├── useGoRide.ts    # Hook untuk narik data GoRide API
    │   │   ├── useGoFood.ts    
    │   │   └── useGoPay.ts     
    │   └── mutations/          # (Opsional) Khusus untuk ubah data (POST/PUT/DELETE)
    │
    ├── lib/                    # WILAYAH LOGIKA & UTILITY
    │   ├── api.ts              # Konfigurasi fetch ke backend API
    │   └── utils.ts            # Fungsi formatter (seperti formatCompact, formatCurrency)
    │
    ├── types/                  # WILAYAH TYPESCRIPT INTERFACES
    │   ├── index.ts            
    │   └── api.ts              
    │
    ├── package.json
    ├── tsconfig.json
    └── next.config.ts          # Konfigurasi Next.js