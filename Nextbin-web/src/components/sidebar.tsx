"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import {
  LayoutDashboard,
  Activity,
  Instagram,
  ShieldCheck,
  Radio,
  User,
} from "lucide-react";
import { useEffect, useState } from "react";
import { getApiUrl } from "@/utils/api-helper";

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const res = await fetch(getApiUrl());
        setApiOnline(res.ok);
      } catch {
        setApiOnline(false);
      }
    };
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { name: "Website Monitors", href: "/dashboard/monitoring", icon: Activity },
    { name: "Instagram Agent", href: "/dashboard/instagram", icon: Instagram },
    {
      name: "Security Audit",
      href: "/dashboard/audit",
      icon: ShieldCheck,
      superuserOnly: true,
    },
    { name: "My Profile", href: "/dashboard/profile", icon: User },
  ];

  return (
    <aside
      className="w-60 flex flex-col h-screen select-none flex-shrink-0"
      style={{
        background: "rgba(6,9,16,0.95)",
        borderRight: "1px solid rgba(99,102,241,0.1)",
      }}
    >
      {/* ── Brand ── */}
      <div
        className="flex items-center gap-3 px-5 py-5 flex-shrink-0"
        style={{ borderBottom: "1px solid rgba(99,102,241,0.08)" }}
      >
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{
            background: "linear-gradient(135deg, #4f46e5, #6366f1)",
            boxShadow: "0 0 20px rgba(99,102,241,0.35)",
          }}
        >
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-black text-white text-base tracking-tight leading-none">
            NILA
          </h1>
          <p
            className="text-[10px] font-semibold tracking-[0.2em] uppercase mt-0.5"
            style={{ color: "#6366f1" }}
          >
            Control
          </p>
        </div>
      </div>

      {/* ── Navigation ── */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p
          className="px-3 pb-2 text-[10px] font-semibold tracking-[0.12em] uppercase"
          style={{ color: "#334155" }}
        >
          Navigation
        </p>
        {navItems.map((item) => {
          if (item.superuserOnly && !user?.is_superuser) return null;
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150"
              style={
                isActive
                  ? {
                      background:
                        "linear-gradient(90deg, rgba(99,102,241,0.18) 0%, rgba(99,102,241,0.04) 100%)",
                      borderLeft: "2px solid #6366f1",
                      color: "#c7d2fe",
                      paddingLeft: "10px",
                    }
                  : {
                      color: "#475569",
                      paddingLeft: "12px",
                    }
              }
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = "rgba(99,102,241,0.06)";
                  e.currentTarget.style.color = "#94a3b8";
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = "transparent";
                  e.currentTarget.style.color = "#475569";
                }
              }}
            >
              <Icon
                className="w-4 h-4 flex-shrink-0"
                style={{ color: isActive ? "#818cf8" : "#475569" }}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* ── Footer ── */}
      <div
        className="px-3 py-4 space-y-3 flex-shrink-0"
        style={{ borderTop: "1px solid rgba(99,102,241,0.08)" }}
      >
        {/* API Status */}
        <div
          className="flex items-center justify-between px-3 py-2.5 rounded-xl"
          style={{
            background: "rgba(15,22,40,0.5)",
            border: "1px solid rgba(99,102,241,0.1)",
          }}
        >
          <div
            className="flex items-center gap-2 text-xs"
            style={{ color: "#64748b" }}
          >
            <Radio className="w-3.5 h-3.5" />
            API Server
          </div>
          <div className="flex items-center gap-1.5">
            <div
              className="w-1.5 h-1.5 rounded-full"
              style={{
                background:
                  apiOnline === null
                    ? "#f59e0b"
                    : apiOnline
                    ? "#10b981"
                    : "#ef4444",
                boxShadow:
                  apiOnline === null
                    ? "0 0 6px #f59e0b"
                    : apiOnline
                    ? "0 0 6px #10b981"
                    : "0 0 6px #ef4444",
                animation: "pulse 2s ease-in-out infinite",
              }}
            />
            <span
              className="text-[10px] font-semibold"
              style={{
                color:
                  apiOnline === null
                    ? "#f59e0b"
                    : apiOnline
                    ? "#10b981"
                    : "#ef4444",
              }}
            >
              {apiOnline === null ? "CHECKING" : apiOnline ? "ONLINE" : "OFFLINE"}
            </span>
          </div>
        </div>

        {/* User Card */}
        <Link
          href="/dashboard/profile"
          className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition-all"
          style={{
            background: "rgba(15,22,40,0.5)",
            border: "1px solid rgba(99,102,241,0.1)",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "rgba(99,102,241,0.25)";
            e.currentTarget.style.background = "rgba(99,102,241,0.06)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "rgba(99,102,241,0.1)";
            e.currentTarget.style.background = "rgba(15,22,40,0.5)";
          }}
        >
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
            style={{ background: "linear-gradient(135deg, #4f46e5, #06b6d4)" }}
          >
            {user?.full_name
              ? user.full_name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase()
                  .slice(0, 2)
              : user?.email?.slice(0, 2).toUpperCase() ?? "AD"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-white truncate">
              {user?.full_name || "Administrator"}
            </p>
            <p
              className="text-[10px] truncate"
              style={{ color: "#64748b" }}
            >
              {user?.is_superuser ? "Super Admin" : "Admin"}
            </p>
          </div>
        </Link>
      </div>
    </aside>
  );
}
