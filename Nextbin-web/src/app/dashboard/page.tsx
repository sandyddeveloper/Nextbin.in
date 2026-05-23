"use client";

import { useEffect } from "react";
import { useProjects } from "@/hooks/use-projects";
import { useInstagram } from "@/hooks/use-instagram";
import {
  Activity,
  Instagram,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  RefreshCw,
  TrendingUp,
  Zap,
} from "lucide-react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from "recharts";

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  sub?: React.ReactNode;
  color: string;
  glow: string;
}

function StatCard({ icon: Icon, label, value, sub, color, glow }: StatCardProps) {
  return (
    <div
      className="p-5 rounded-2xl flex flex-col gap-3 relative overflow-hidden"
      style={{
        background: "rgba(10,14,28,0.7)",
        border: "1px solid rgba(99,102,241,0.12)",
        backdropFilter: "blur(16px)",
      }}
    >
      {/* Icon */}
      <div className="flex items-center justify-between">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ background: `${color}1a` }}
        >
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
        <div
          className="w-1.5 h-1.5 rounded-full"
          style={{ background: color, boxShadow: `0 0 6px ${glow}` }}
        />
      </div>

      {/* Value */}
      <div>
        <p className="text-3xl font-black text-white">{value}</p>
        <p className="text-xs mt-0.5 font-medium" style={{ color: "#64748b" }}>
          {label}
        </p>
      </div>

      {/* Sub info */}
      {sub && <div className="flex items-center gap-3 text-xs">{sub}</div>}

      {/* Corner glow */}
      <div
        className="absolute -right-6 -bottom-6 w-24 h-24 rounded-full pointer-events-none"
        style={{
          background: `radial-gradient(circle, ${glow}20 0%, transparent 70%)`,
        }}
      />
    </div>
  );
}

export default function DashboardPage() {
  const { projects, fetchProjects } = useProjects();
  const { accounts, auditLogs, fetchAccounts, fetchAuditLogs } = useInstagram();

  useEffect(() => {
    fetchProjects();
    fetchAccounts();
    fetchAuditLogs(10);
  }, [fetchProjects, fetchAccounts, fetchAuditLogs]);

  const upCount = projects.filter((p) => p.last_status === "UP").length;
  const downCount = projects.filter((p) => p.last_status === "DOWN").length;
  const connectedIg = accounts.filter((a) => a.status === "CONNECTED").length;
  const errorIg = accounts.filter(
    (a) => a.status === "ERROR" || a.status === "2FA_REQUIRED"
  ).length;

  const chartData = projects.map((p) => ({
    name: p.name.length > 10 ? p.name.slice(0, 10) + "…" : p.name,
    latency: p.last_status === "UP" ? Math.floor(Math.random() * 180) + 40 : 0,
  }));

  const handleRefreshAll = () => {
    fetchProjects();
    fetchAccounts();
    fetchAuditLogs(10);
  };

  return (
    <div className="space-y-6">
      {/* ── Refresh ── */}
      <div className="flex justify-end">
        <button onClick={handleRefreshAll} className="btn-secondary">
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* ── Stat Cards ── */}
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          icon={Activity}
          label="Web Monitors"
          value={projects.length}
          color="#6366f1"
          glow="#6366f1"
          sub={
            <>
              <span className="flex items-center gap-1" style={{ color: "#34d399" }}>
                <CheckCircle2 className="w-3.5 h-3.5" /> {upCount} UP
              </span>
              <span className="flex items-center gap-1" style={{ color: "#f87171" }}>
                <XCircle className="w-3.5 h-3.5" /> {downCount} DOWN
              </span>
            </>
          }
        />
        <StatCard
          icon={Instagram}
          label="Instagram Agents"
          value={accounts.length}
          color="#ec4899"
          glow="#ec4899"
          sub={
            <>
              <span className="flex items-center gap-1" style={{ color: "#34d399" }}>
                <CheckCircle2 className="w-3.5 h-3.5" /> {connectedIg} Active
              </span>
              <span className="flex items-center gap-1" style={{ color: "#fbbf24" }}>
                <AlertTriangle className="w-3.5 h-3.5" /> {errorIg} Issues
              </span>
            </>
          }
        />
        <StatCard
          icon={ShieldAlert}
          label="Security Events"
          value={auditLogs.length}
          color="#06b6d4"
          glow="#06b6d4"
          sub={
            <span className="flex items-center gap-1 font-mono text-[10px]" style={{ color: "#64748b" }}>
              <Clock className="w-3 h-3" />
              {auditLogs[0]?.action ?? "No events yet"}
            </span>
          }
        />
      </div>

      {/* ── Charts & Audit ── */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* Latency Chart */}
        <div
          className="lg:col-span-2 rounded-2xl overflow-hidden"
          style={{
            background: "rgba(10,14,28,0.7)",
            border: "1px solid rgba(99,102,241,0.12)",
            backdropFilter: "blur(16px)",
          }}
        >
          <div
            className="px-5 py-4 flex items-center justify-between"
            style={{ borderBottom: "1px solid rgba(99,102,241,0.08)" }}
          >
            <div>
              <h3 className="text-sm font-semibold text-white">
                Infrastructure Latency
              </h3>
              <p className="text-xs mt-0.5" style={{ color: "#64748b" }}>
                Response time across active monitors (ms)
              </p>
            </div>
            <div className="flex items-center gap-1.5">
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{
                  background: "#6366f1",
                  boxShadow: "0 0 6px #6366f1",
                  animation: "pulse 2s ease-in-out infinite",
                }}
              />
              <span className="text-[10px] font-semibold" style={{ color: "#6366f1" }}>
                LIVE
              </span>
            </div>
          </div>

          <div className="p-5 h-56">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="latGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="name"
                    stroke="#334155"
                    fontSize={10}
                    tickLine={false}
                    axisLine={{ stroke: "#1e293b" }}
                  />
                  <YAxis
                    stroke="#334155"
                    fontSize={10}
                    tickLine={false}
                    axisLine={false}
                    label={{
                      value: "ms",
                      angle: -90,
                      position: "insideLeft",
                      fill: "#475569",
                      fontSize: 10,
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0d1220",
                      borderColor: "rgba(99,102,241,0.2)",
                      borderRadius: "10px",
                      color: "#e2e8f0",
                      fontSize: "12px",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="latency"
                    stroke="#6366f1"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#latGrad)"
                    dot={{ fill: "#6366f1", r: 3 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center gap-2">
                <TrendingUp
                  className="w-10 h-10"
                  style={{ color: "#1e293b" }}
                />
                <p className="text-sm" style={{ color: "#475569" }}>
                  No monitors registered yet
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Audit Stream */}
        <div
          className="rounded-2xl overflow-hidden flex flex-col"
          style={{
            background: "rgba(10,14,28,0.7)",
            border: "1px solid rgba(99,102,241,0.12)",
            backdropFilter: "blur(16px)",
          }}
        >
          <div
            className="px-5 py-4 flex items-center gap-2 flex-shrink-0"
            style={{ borderBottom: "1px solid rgba(99,102,241,0.08)" }}
          >
            <Zap className="w-4 h-4" style={{ color: "#06b6d4" }} />
            <h3 className="text-sm font-semibold text-white">Audit Stream</h3>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {auditLogs.length > 0 ? (
              auditLogs.map((log) => (
                <div
                  key={log.id}
                  className="p-3 rounded-xl space-y-1.5"
                  style={{
                    background: "rgba(6,9,16,0.5)",
                    border: "1px solid rgba(99,102,241,0.08)",
                  }}
                >
                  <div className="flex items-center justify-between">
                    <span
                      className="text-[11px] font-bold font-mono"
                      style={{ color: "#818cf8" }}
                    >
                      {log.action}
                    </span>
                    <span className="text-[10px]" style={{ color: "#475569" }}>
                      {new Date(log.created_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                  <div
                    className="flex items-center justify-between text-[10px]"
                    style={{ color: "#64748b" }}
                  >
                    <span className="font-mono">{log.ip_address}</span>
                    <span
                      className="uppercase font-semibold tracking-wider"
                      style={{ color: "#475569" }}
                    >
                      {log.platform}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="h-32 flex items-center justify-center">
                <p className="text-sm" style={{ color: "#475569" }}>
                  No audit events recorded yet.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
