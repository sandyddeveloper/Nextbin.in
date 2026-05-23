"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";
import {
  ShieldCheck,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Loader2,
  Zap,
  Activity,
  Globe,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, loading, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isAuthenticated) router.push("/dashboard");
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Please enter your credentials.");
      return;
    }
    const success = await login(email, password);
    if (success) {
      toast.success("Access granted — Welcome back.");
      router.push("/dashboard");
    } else {
      toast.error("Authentication failed. Check your credentials.");
    }
  };

  return (
    <div
      className="min-h-screen flex overflow-hidden"
      style={{ background: "#060910" }}
    >
      {/* ── Left Panel — Brand & Visual ── */}
      <div className="hidden lg:flex lg:w-[52%] relative flex-col items-center justify-center p-12 overflow-hidden">
        {/* Ambient background */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse 60% 70% at 30% 40%, rgba(99,102,241,0.12) 0%, transparent 70%), radial-gradient(ellipse 50% 60% at 70% 70%, rgba(6,182,212,0.08) 0%, transparent 70%)",
          }}
        />
        {/* Grid lines */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(99,102,241,1) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,1) 1px, transparent 1px)",
            backgroundSize: "50px 50px",
          }}
        />

        {/* Content */}
        <div className="relative z-10 max-w-lg text-center">
          {/* Logo Mark */}
          <div className="flex items-center justify-center mb-10">
            <div
              className="w-20 h-20 rounded-3xl flex items-center justify-center"
              style={{
                background:
                  "linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #06b6d4 100%)",
                boxShadow:
                  "0 0 60px rgba(99,102,241,0.4), 0 0 100px rgba(6,182,212,0.15)",
              }}
            >
              <ShieldCheck className="w-10 h-10 text-white" />
            </div>
          </div>

          <h1
            className="text-5xl font-black mb-4 tracking-tight"
            style={{
              background:
                "linear-gradient(135deg, #ffffff 0%, #c7d2fe 50%, #67e8f9 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            NILA
          </h1>
          <p
            className="text-sm font-semibold tracking-[0.3em] uppercase mb-6"
            style={{ color: "#6366f1" }}
          >
            Nextbin Automation Suite
          </p>
          <p className="text-base leading-relaxed" style={{ color: "#64748b" }}>
            Enterprise-grade monitoring, Instagram automation, and security
            auditing — all in one secure control plane.
          </p>

          {/* Feature pills */}
          <div className="flex flex-col gap-3 mt-10">
            {[
              { icon: Activity, label: "Real-time website uptime monitoring" },
              { icon: Zap, label: "Instagram DM automation & reply rules" },
              { icon: Globe, label: "Fintech-grade audit logs & request tracing" },
            ].map(({ icon: Icon, label }, i) => (
              <div
                key={i}
                className="flex items-center gap-3 p-3 rounded-xl text-left"
                style={{
                  background: "rgba(99,102,241,0.06)",
                  border: "1px solid rgba(99,102,241,0.12)",
                }}
              >
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: "rgba(99,102,241,0.15)" }}
                >
                  <Icon className="w-4 h-4" style={{ color: "#818cf8" }} />
                </div>
                <span className="text-sm" style={{ color: "#94a3b8" }}>
                  {label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right Panel — Login Form ── */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 relative">
        {/* Subtle ambient */}
        <div
          className="absolute inset-0 opacity-50"
          style={{
            background:
              "radial-gradient(ellipse 60% 50% at 50% 30%, rgba(99,102,241,0.05) 0%, transparent 70%)",
          }}
        />

        <div
          className={`relative w-full max-w-md transition-all duration-500 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-3 mb-8">
            <div
              className="w-10 h-10 rounded-2xl flex items-center justify-center"
              style={{
                background: "linear-gradient(135deg, #4f46e5, #06b6d4)",
                boxShadow: "0 0 20px rgba(99,102,241,0.4)",
              }}
            >
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-white text-lg">NILA</h1>
              <p
                className="text-[10px] font-semibold tracking-widest uppercase"
                style={{ color: "#6366f1" }}
              >
                Control
              </p>
            </div>
          </div>

          {/* Card */}
          <div
            className="rounded-2xl overflow-hidden"
            style={{
              background: "rgba(10,14,28,0.8)",
              border: "1px solid rgba(99,102,241,0.2)",
              boxShadow:
                "0 24px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(99,102,241,0.08)",
              backdropFilter: "blur(24px)",
            }}
          >
            {/* Card top accent */}
            <div
              className="h-[2px]"
              style={{
                background:
                  "linear-gradient(90deg, #4f46e5, #6366f1, #06b6d4)",
              }}
            />

            <div className="p-8">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-white mb-1">
                  Sign In
                </h2>
                <p className="text-sm" style={{ color: "#64748b" }}>
                  Enter your administrative credentials
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Email */}
                <div className="space-y-1.5">
                  <label
                    className="text-xs font-semibold"
                    style={{ color: "#94a3b8" }}
                  >
                    Email Address
                  </label>
                  <div className="nila-input-icon">
                    <Mail className="icon w-4 h-4" />
                    <input
                      id="login-email"
                      type="email"
                      className="nila-input"
                      placeholder="admin@nextbin.in"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={loading}
                      autoComplete="email"
                    />
                  </div>
                </div>

                {/* Password */}
                <div className="space-y-1.5">
                  <label
                    className="text-xs font-semibold"
                    style={{ color: "#94a3b8" }}
                  >
                    Password
                  </label>
                  <div className="nila-input-icon">
                    <Lock className="icon w-4 h-4" />
                    <input
                      id="login-password"
                      type={showPassword ? "text" : "password"}
                      className="nila-input"
                      placeholder="••••••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={loading}
                      autoComplete="current-password"
                      style={{ paddingRight: "44px" }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2"
                      style={{ color: "#475569", cursor: "pointer" }}
                      tabIndex={-1}
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Submit */}
                <button
                  id="login-submit"
                  type="submit"
                  disabled={loading}
                  className="w-full mt-6 flex items-center justify-center gap-2.5 py-3 px-6 rounded-xl font-semibold text-sm text-white transition-all"
                  style={{
                    background: loading
                      ? "rgba(99,102,241,0.5)"
                      : "linear-gradient(135deg, #4f46e5 0%, #6366f1 60%, #06b6d4 100%)",
                    border: "1px solid rgba(139,140,255,0.3)",
                    boxShadow: loading
                      ? "none"
                      : "0 0 30px rgba(99,102,241,0.35), 0 4px 12px rgba(0,0,0,0.3)",
                    cursor: loading ? "not-allowed" : "pointer",
                    transform: "translateY(0)",
                  }}
                  onMouseEnter={(e) => {
                    if (!loading)
                      e.currentTarget.style.transform = "translateY(-1px)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Verifying...
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4" />
                      Sign In to NILA
                    </>
                  )}
                </button>
              </form>

              {/* Footer */}
              <div
                className="mt-6 pt-5 flex items-center justify-center gap-1.5"
                style={{ borderTop: "1px solid rgba(99,102,241,0.1)" }}
              >
                <div className="pulse-dot green w-2 h-2" />
                <span className="text-[11px]" style={{ color: "#64748b" }}>
                  Secured with AES-256 · Audit Logged · Request Traced
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
