"use client";

import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Search, Bell, ChevronDown, User, Settings, LogOut } from "lucide-react";

const PAGE_TITLES: Record<string, { title: string; desc: string }> = {
  "/dashboard": { title: "Overview", desc: "System health & telemetry summary" },
  "/dashboard/monitoring": {
    title: "Website Monitors",
    desc: "Uptime checks, latency metrics & SSL status",
  },
  "/dashboard/instagram": {
    title: "Instagram Agent",
    desc: "Linked accounts, auto-reply rules & DM dispatch",
  },
  "/dashboard/audit": {
    title: "Security Audit",
    desc: "Request traces, auth events & operator actions",
  },
  "/dashboard/profile": {
    title: "My Profile",
    desc: "Account settings and session information",
  },
};

export default function DashboardHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [searchValue, setSearchValue] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const pageInfo = PAGE_TITLES[pathname] ?? {
    title: "Dashboard",
    desc: "NILA Control Panel",
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const initials = user?.full_name
    ? user.full_name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
    : user?.email?.slice(0, 2).toUpperCase() ?? "AD";

  return (
    <header
      className="flex items-center justify-between px-6 py-3 flex-shrink-0"
      style={{
        borderBottom: "1px solid rgba(99,102,241,0.1)",
        background: "rgba(6,9,16,0.7)",
        backdropFilter: "blur(16px)",
      }}
    >
      {/* Left — Page Title */}
      <div className="flex flex-col justify-center min-w-0">
        <h2 className="text-lg font-bold text-white leading-tight truncate">
          {pageInfo.title}
        </h2>
        <p
          className="text-xs leading-tight truncate hidden sm:block"
          style={{ color: "#64748b" }}
        >
          {pageInfo.desc}
        </p>
      </div>

      {/* Center — Search */}
      <div className="hidden md:flex flex-1 max-w-sm mx-8">
        <div className="search-input w-full">
          <Search className="w-4 h-4" style={{ color: "#4f46e5" }} />
          <input
            type="text"
            placeholder="Search monitors, logs, accounts..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
          />
        </div>
      </div>

      {/* Right — Actions */}
      <div className="flex items-center gap-2 z-50">
        {/* Notifications Bell */}
        <button
          className="btn-icon relative"
          title="Notifications"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span
            className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full"
            style={{ background: "#6366f1" }}
          />
        </button>

        {/* Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-xl transition-all"
            style={{
              background: dropdownOpen
                ? "rgba(99,102,241,0.12)"
                : "rgba(15,22,40,0.5)",
              border: "1px solid rgba(99,102,241,0.15)",
              cursor: "pointer",
            }}
          >
            {/* Avatar */}
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
              style={{
                background: "linear-gradient(135deg, #4f46e5, #06b6d4)",
              }}
            >
              {initials}
            </div>
            <div className="hidden sm:block text-left min-w-0">
              <p className="text-xs font-semibold text-white truncate max-w-[110px]">
                {user?.full_name || "Administrator"}
              </p>
              <p
                className="text-[10px] truncate max-w-[110px]"
                style={{ color: "#64748b" }}
              >
                {user?.is_superuser ? "Super Admin" : "Admin"}
              </p>
            </div>
            <ChevronDown
              className="w-3.5 h-3.5 transition-transform hidden sm:block"
              style={{
                color: "#64748b",
                transform: dropdownOpen ? "rotate(180deg)" : "rotate(0)",
              }}
            />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <>
              {/* Backdrop */}
              <div
                className="fixed inset-0 z-10"
                onClick={() => setDropdownOpen(false)}
              />
              <div
                className="absolute right-0 top-full mt-2 w-48 rounded-xl overflow-hidden z-20"
                style={{
                  background: "rgba(10,14,28,0.95)",
                  border: "1px solid rgba(99,102,241,0.2)",
                  boxShadow:
                    "0 16px 48px rgba(0,0,0,0.5), 0 0 0 1px rgba(99,102,241,0.05)",
                  backdropFilter: "blur(20px)",
                }}
              >
                {/* User info header */}
                <div
                  className="px-4 py-3"
                  style={{ borderBottom: "1px solid rgba(99,102,241,0.1)" }}
                >
                  <p className="text-xs font-semibold text-white">
                    {user?.full_name || "Administrator"}
                  </p>
                  <p
                    className="text-[11px] truncate mt-0.5"
                    style={{ color: "#64748b" }}
                  >
                    {user?.email}
                  </p>
                </div>

                <div className="py-1.5">
                  <Link
                    href="/dashboard/profile"
                    onClick={() => setDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors"
                    style={{ color: "#94a3b8" }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background =
                        "rgba(99,102,241,0.08)";
                      e.currentTarget.style.color = "#e2e8f0";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "transparent";
                      e.currentTarget.style.color = "#94a3b8";
                    }}
                  >
                    <User className="w-3.5 h-3.5" />
                    My Profile
                  </Link>
                  <Link
                    href="/dashboard/profile"
                    onClick={() => setDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors"
                    style={{ color: "#94a3b8" }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background =
                        "rgba(99,102,241,0.08)";
                      e.currentTarget.style.color = "#e2e8f0";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "transparent";
                      e.currentTarget.style.color = "#94a3b8";
                    }}
                  >
                    <Settings className="w-3.5 h-3.5" />
                    Settings
                  </Link>
                </div>

                <div
                  className="py-1.5"
                  style={{ borderTop: "1px solid rgba(99,102,241,0.1)" }}
                >
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors"
                    style={{ color: "#f87171", cursor: "pointer" }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "rgba(239,68,68,0.08)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "transparent";
                    }}
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    Sign Out
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
