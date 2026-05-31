import type { Metadata } from "next";
import Sidebar from "@/components/layout/Sidebar";
import TanstackProvider from "@/components/providers/TanstackProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gojek Enterprise Dashboard",
  description: "Analytical insights for Gojek operations and finance.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen bg-theme-base text-theme-main transition-colors duration-300">
        {/* Sisipkan Provider di sini */}
        <TanstackProvider>
          <Sidebar />
          <main className="flex-1 h-screen overflow-y-auto">{children}</main>
        </TanstackProvider>
      </body>
    </html>
  );
}
