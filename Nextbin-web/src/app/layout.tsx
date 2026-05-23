import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "NILA Control Suite",
  description: "Fintech-Grade Automation & Monitoring Dashboard by Nextbin",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark h-full" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} min-h-full flex flex-col`}
        style={{ background: "#060910", color: "#e8eaf0", fontFamily: "var(--font-inter), system-ui, sans-serif" }}
      >
        {children}
        <Toaster theme="dark" closeButton richColors />
      </body>
    </html>
  );
}
