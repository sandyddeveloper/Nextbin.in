"use client";

import { useAuth } from "@/hooks/use-auth";
import {
  User,
  Mail,
  ShieldCheck,
  Clock,
  Key,
  LogOut,
  Copy,
  CheckCircle2,
  Fingerprint,
  Globe,
} from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

function InfoRow({
  icon: Icon,
  label,
  value,
  mono = false,
  badge,
}: {
  icon: React.ElementType;
  label: string;
  value: React.ReactNode;
  mono?: boolean;
  badge?: React.ReactNode;
}) {
  return (
    <div
      className="flex items-center justify-between py-3.5 px-4"
      style={{ borderBottom: "1px solid rgba(99,102,241,0.07)" }}
    >
      <div className="flex items-center gap-3 min-w-0">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ background: "rgba(99,102,241,0.1)" }}
        >
          <Icon className="w-4 h-4" style={{ color: "#818cf8" }} />
        </div>
        <span className="text-xs font-medium" style={{ color: "#64748b" }}>
          {label}
        </span>
      </div>
      <div className="flex items-center gap-2">
        {badge}
        <span
          className={`text-sm font-medium text-right max-w-[220px] truncate ${
            mono ? "font-mono" : ""
          }`}
          style={{ color: "#e2e8f0" }}
        >
          {value}
        </span>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div
      className="p-5 rounded-2xl"
      style={{
        background: "rgba(10,14,28,0.6)",
        border: "1px solid rgba(99,102,241,0.1)",
      }}
    >
      <div
        className="w-9 h-9 rounded-xl flex items-center justify-center mb-3"
        style={{ background: `${color}18` }}
      >
        <Icon className="w-5 h-5" style={{ color }} />
      </div>
      <p className="text-2xl font-bold text-white mb-0.5">{value}</p>
      <p className="text-xs" style={{ color: "#64748b" }}>
        {label}
      </p>
    </div>
  );
}

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [copied, setCopied] = useState(false);

  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("nila_token") ?? ""
      : "";

  const handleCopyToken = () => {
    if (token) {
      navigator.clipboard.writeText(token);
      setCopied(true);
      toast.success("Session token copied to clipboard.");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleLogout = () => {
    logout();
    toast.info("Session terminated.");
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

  const createdDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "long",
        year: "numeric",
      })
    : "—";

  return (
    <div className="max-w-3xl space-y-6">
      {/* ── Profile Hero ── */}
      <div
        className="rounded-2xl p-6 relative overflow-hidden"
        style={{
          background: "rgba(10,14,28,0.7)",
          border: "1px solid rgba(99,102,241,0.15)",
          backdropFilter: "blur(20px)",
        }}
      >
        {/* Ambient glow */}
        <div
          className="absolute top-0 right-0 w-64 h-64 opacity-20 pointer-events-none"
          style={{
            background:
              "radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%)",
          }}
        />

        <div className="relative flex items-center gap-5">
          {/* Avatar */}
          <div
            className="w-20 h-20 rounded-2xl flex items-center justify-center text-white text-2xl font-black flex-shrink-0"
            style={{
              background: "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
              boxShadow: "0 0 30px rgba(99,102,241,0.3)",
            }}
          >
            {initials}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h2 className="text-2xl font-bold text-white">
                {user?.full_name || "Administrator"}
              </h2>
              {user?.is_superuser && (
                <span
                  className="px-2.5 py-1 rounded-lg text-[11px] font-semibold"
                  style={{
                    background: "rgba(99,102,241,0.15)",
                    border: "1px solid rgba(99,102,241,0.3)",
                    color: "#818cf8",
                  }}
                >
                  SUPER ADMIN
                </span>
              )}
              {user?.is_active && (
                <span
                  className="px-2.5 py-1 rounded-lg text-[11px] font-semibold flex items-center gap-1"
                  style={{
                    background: "rgba(16,185,129,0.1)",
                    border: "1px solid rgba(16,185,129,0.2)",
                    color: "#34d399",
                  }}
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{
                      background: "#10b981",
                      boxShadow: "0 0 6px #10b981",
                    }}
                  />
                  ACTIVE
                </span>
              )}
            </div>
            <p className="text-sm mt-1" style={{ color: "#64748b" }}>
              {user?.email}
            </p>
            <p className="text-xs mt-2" style={{ color: "#475569" }}>
              Member since {createdDate}
            </p>
          </div>

          {/* Sign out */}
          <button
            onClick={handleLogout}
            className="btn-danger hidden sm:flex"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
        </div>
      </div>

      {/* ── Stats ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard
          icon={User}
          label="Account ID"
          value={`#${user?.id ?? "—"}`}
          color="#6366f1"
        />
        <StatCard
          icon={ShieldCheck}
          label="Role Level"
          value={user?.is_superuser ? "L2" : "L1"}
          color="#06b6d4"
        />
        <StatCard
          icon={CheckCircle2}
          label="Status"
          value={user?.is_active ? "Active" : "Inactive"}
          color="#10b981"
        />
        <StatCard
          icon={Globe}
          label="Platform"
          value="Web"
          color="#f59e0b"
        />
      </div>

      {/* ── Account Details ── */}
      <div
        className="rounded-2xl overflow-hidden"
        style={{
          background: "rgba(10,14,28,0.6)",
          border: "1px solid rgba(99,102,241,0.12)",
        }}
      >
        <div
          className="px-4 py-3.5 flex items-center gap-2"
          style={{ borderBottom: "1px solid rgba(99,102,241,0.1)" }}
        >
          <Fingerprint className="w-4 h-4" style={{ color: "#6366f1" }} />
          <h3 className="text-sm font-semibold text-white">
            Account Details
          </h3>
        </div>

        <InfoRow icon={User} label="Display Name" value={user?.full_name || "—"} />
        <InfoRow icon={Mail} label="Email Address" value={user?.email || "—"} />
        <InfoRow
          icon={ShieldCheck}
          label="Permission Level"
          value={user?.is_superuser ? "Superuser" : "Administrator"}
          badge={
            <span
              className="px-2 py-0.5 rounded-md text-[10px] font-semibold"
              style={{
                background: user?.is_superuser
                  ? "rgba(99,102,241,0.15)"
                  : "rgba(6,182,212,0.1)",
                border: `1px solid ${
                  user?.is_superuser
                    ? "rgba(99,102,241,0.3)"
                    : "rgba(6,182,212,0.2)"
                }`,
                color: user?.is_superuser ? "#818cf8" : "#22d3ee",
              }}
            >
              {user?.is_superuser ? "L2" : "L1"}
            </span>
          }
        />
        <InfoRow
          icon={Clock}
          label="Account Created"
          value={createdDate}
          mono
        />
        <div style={{ paddingBottom: "0" }}>
          <InfoRow
            icon={CheckCircle2}
            label="Account Status"
            value={user?.is_active ? "Active" : "Deactivated"}
            badge={
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{
                  background: user?.is_active ? "#10b981" : "#ef4444",
                  boxShadow: `0 0 6px ${user?.is_active ? "#10b981" : "#ef4444"}`,
                }}
              />
            }
          />
        </div>
      </div>

      {/* ── Session Token ── */}
      <div
        className="rounded-2xl overflow-hidden"
        style={{
          background: "rgba(10,14,28,0.6)",
          border: "1px solid rgba(99,102,241,0.12)",
        }}
      >
        <div
          className="px-4 py-3.5 flex items-center gap-2"
          style={{ borderBottom: "1px solid rgba(99,102,241,0.1)" }}
        >
          <Key className="w-4 h-4" style={{ color: "#6366f1" }} />
          <h3 className="text-sm font-semibold text-white">
            Active Session Token
          </h3>
          <span
            className="ml-auto px-2 py-0.5 rounded-md text-[10px] font-semibold"
            style={{
              background: "rgba(16,185,129,0.1)",
              border: "1px solid rgba(16,185,129,0.2)",
              color: "#34d399",
            }}
          >
            LIVE
          </span>
        </div>

        <div className="p-4">
          <div
            className="flex items-center gap-3 p-3 rounded-xl"
            style={{
              background: "rgba(6,9,16,0.6)",
              border: "1px solid rgba(99,102,241,0.1)",
            }}
          >
            <code
              className="flex-1 text-[11px] truncate font-mono"
              style={{ color: "#64748b" }}
            >
              {token ? `${token.slice(0, 40)}...` : "No active token"}
            </code>
            <button
              onClick={handleCopyToken}
              className="btn-icon flex-shrink-0"
              title="Copy token"
            >
              {copied ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
          <p className="text-[11px] mt-2.5" style={{ color: "#475569" }}>
            JWT Bearer token — used for all API requests. Do not share this with
            anyone. Expires on logout or session timeout.
          </p>
        </div>
      </div>

      {/* ── Danger Zone ── */}
      <div
        className="rounded-2xl overflow-hidden"
        style={{
          background: "rgba(239,68,68,0.03)",
          border: "1px solid rgba(239,68,68,0.12)",
        }}
      >
        <div
          className="px-4 py-3.5 flex items-center gap-2"
          style={{ borderBottom: "1px solid rgba(239,68,68,0.1)" }}
        >
          <LogOut className="w-4 h-4" style={{ color: "#f87171" }} />
          <h3 className="text-sm font-semibold" style={{ color: "#f87171" }}>
            Session Control
          </h3>
        </div>

        <div className="p-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-white">Terminate Session</p>
            <p className="text-xs mt-0.5" style={{ color: "#64748b" }}>
              Revoke your current JWT token and sign out from all active tabs.
            </p>
          </div>
          <button onClick={handleLogout} className="btn-danger flex-shrink-0">
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
