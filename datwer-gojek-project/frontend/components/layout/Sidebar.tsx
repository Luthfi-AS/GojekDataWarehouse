"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Utensils, Bike, Landmark } from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  // Daftar menu navigasi
  const navItems = [
    {
      name: "GOFOOD & MERCHANT",
      href: "/gofood",
      icon: Utensils,
    },
    {
      name: "GORIDE OPERATIONS",
      href: "/goride",
      icon: Bike,
    },
    {
      name: "GOPAY FINANCIAL LEDGER",
      href: "/gopay",
      icon: Landmark,
    },
  ];

  return (
    <aside className="w-64 min-h-screen bg-theme-base border-r border-theme-border flex flex-col flex-shrink-0 transition-colors duration-300">
      {/* --- LOGO & HEADER --- */}
      <div className="p-6 mb-2 mt-2">
        <h1 className="text-xl font-extrabold text-theme-main leading-tight">
          Gojek Enterprise
          <br />
          Dashboard
        </h1>
        <p className="text-[10px] font-bold text-theme-muted tracking-wider mt-2 uppercase">
          ANALYTICAL INSIGHTS
        </p>
      </div>

      {/* --- MENU NAVIGASI --- */}
      <nav className="flex flex-col w-full">
        {navItems.map((item) => {
          // Cek apakah URL saat ini cocok dengan href menu
          const isActive = pathname?.startsWith(item.href);
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-6 py-4 text-sm font-bold transition-all relative ${
                isActive
                  ? "text-theme-main bg-theme-border/30" // Latar belakang abu-abu transparan saat aktif
                  : "text-theme-muted hover:bg-theme-border/10 hover:text-theme-main"
              }`}
            >
              {/* Indikator Garis Kiri (Hanya muncul jika aktif) */}
              {isActive && (
                <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-theme-main" />
              )}

              <Icon className="w-5 h-5 mr-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
