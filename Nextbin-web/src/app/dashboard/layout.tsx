"use client";

import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Sidebar from "@/components/sidebar";
import DashboardHeader from "@/components/dashboard-header";
import { Loader2 } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [loading, isAuthenticated, router]);

  if (loading) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-3"
        style={{ background: "#060910" }}
      >
        <div
          className="w-12 h-12 rounded-2xl flex items-center justify-center"
          style={{ background: "linear-gradient(135deg, #4f46e5, #6366f1)" }}
        >
          <Loader2 className="w-6 h-6 text-white animate-spin" />
        </div>
        <p className="text-sm font-medium" style={{ color: "#64748b" }}>
          Verifying session...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ background: "#060910" }}
    >
      {/* Sidebar */}
      <Sidebar />

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <DashboardHeader />

        {/* Page Content */}
        <main
          className="flex-1 overflow-y-auto p-6 lg:p-8"
          style={{
            background:
              "radial-gradient(ellipse 80% 50% at 50% 0%, rgba(99,102,241,0.04) 0%, transparent 60%), #060910",
          }}
        >
          <div className="max-w-[1400px] mx-auto animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
