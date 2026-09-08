/**
 * AIMD Dashboard Layout — Law Enforcement Police Cyber Cell Shell
 * Developer: Daksh Walia, B.Tech AIML
 * Chandigarh Police Cyber Crime Cell
 */

"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Shield,
  LayoutDashboard,
  FileSearch,
  Mic,
  FolderLock,
  FileText,
  Globe,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell,
  Search,
  Activity,
  PlusCircle,
  Award,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { useState, useEffect } from "react";
import { checkBackendHealth } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Overview Telemetry", icon: LayoutDashboard, category: "COMMAND" },
  { href: "/scan", label: "AI Media Scanner", icon: FileSearch, category: "FORENSICS" },
  { href: "/audio", label: "Synthetic Voice Lab", icon: Mic, category: "FORENSICS" },
  { href: "/evidence", label: "Evidence Vault", icon: FolderLock, category: "CHAIN OF CUSTODY" },
  { href: "/cases", label: "Section 65B Hub", icon: FileText, category: "COURT EVIDENCE" },
  { href: "/extension", label: "Web & Phishing Scanner", icon: Globe, category: "INTELLIGENCE" },
];

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "checking">("checking");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    let isMounted = true;
    const verifyHealth = async () => {
      try {
        await checkBackendHealth();
        if (isMounted) setBackendStatus("online");
      } catch {
        if (isMounted) setBackendStatus("offline");
      }
    };
    verifyHealth();
    const interval = setInterval(verifyHealth, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleLogout = () => {
    router.push("/login");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#0B192C] text-[#F5F5F5] font-sans">
      {/* ── Sidebar ─────────────────────────────────── */}
      <aside
        className={`${
          collapsed ? "w-[76px]" : "w-64"
        } bg-[#14283D] border-r border-[#334E68] flex flex-col transition-all duration-300 ease-in-out hidden md:flex relative z-20 shadow-xl`}
      >
        {/* Logo / Police Branding */}
        <div className="p-4 border-b border-[#334E68]/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-[#D4AF37] to-[#B8941F] p-2 rounded-xl flex-shrink-0 shadow-lg shadow-[#D4AF37]/20 border border-[#D4AF37]/40">
              <Shield size={22} className="text-[#0B192C]" />
            </div>
            {!collapsed && (
              <div className="overflow-hidden">
                <h1 className="font-bold text-sm leading-tight tracking-wider text-[#F5F5F5] uppercase">
                  AIMD <span className="text-[#D4AF37]">CYBER CELL</span>
                </h1>
                <p className="text-[9px] text-[#94A3B8] font-bold tracking-widest uppercase mt-0.5">
                  CHANDIGARH POLICE
                </p>
              </div>
            )}
          </div>
        </div>

        {/* System Connection Badge */}
        {!collapsed && (
          <div className="mx-3 mt-3 px-3 py-2 rounded-lg bg-[#0B192C]/60 border border-[#334E68]/50 flex items-center justify-between text-xs">
            <span className="text-[11px] text-[#94A3B8] font-medium flex items-center gap-1.5">
              <Activity size={13} className="text-[#FF6500]" />
              Engine Status:
            </span>
            <span
              className={`font-semibold text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1 ${
                backendStatus === "online"
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                  : backendStatus === "offline"
                  ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                  : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
              }`}
            >
              {backendStatus === "online" ? (
                <>
                  <CheckCircle2 size={10} /> FastAPI Live
                </>
              ) : backendStatus === "offline" ? (
                <>
                  <AlertCircle size={10} /> Local Fallback
                </>
              ) : (
                "Connecting..."
              )}
            </span>
          </div>
        )}

        {/* Navigation Menu */}
        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto custom-scrollbar">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname?.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                  isActive
                    ? "bg-[#FF6500]/15 text-[#FF6500] border border-[#FF6500]/30 shadow-md shadow-[#FF6500]/10 font-semibold"
                    : "text-[#94A3B8] hover:bg-[#1E3E62]/50 hover:text-[#F5F5F5] border border-transparent"
                }`}
                title={collapsed ? item.label : undefined}
              >
                <item.icon
                  size={19}
                  className={`flex-shrink-0 transition-colors ${
                    isActive ? "text-[#FF6500]" : "text-[#94A3B8] group-hover:text-[#F5F5F5]"
                  }`}
                />
                {!collapsed && (
                  <span className="flex-1 truncate tracking-tight">{item.label}</span>
                )}
                {!collapsed && isActive && (
                  <span className="w-1.5 h-1.5 rounded-full bg-[#FF6500] shadow-sm shadow-[#FF6500]" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-[#14283D] border border-[#334E68] flex items-center justify-center text-[#94A3B8] hover:text-[#F5F5F5] hover:bg-[#FF6500]/20 transition-all shadow-md z-30"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>

        {/* Officer Profile Footer */}
        <div className="p-3 border-t border-[#334E68]/60 bg-[#0B192C]/40">
          <div className={`flex items-center gap-3 ${collapsed ? "justify-center" : "px-2 py-1.5"}`}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#D4AF37]/20 to-[#FF6500]/20 border border-[#D4AF37]/40 flex items-center justify-center text-[#D4AF37] font-bold text-xs flex-shrink-0 shadow-inner">
              <Award size={18} />
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-xs text-[#F5F5F5] truncate">Daksh Walia</p>
                <p className="text-[10px] text-[#D4AF37] font-medium truncate">CHD-CYB-0042 • Officer</p>
              </div>
            )}
            {!collapsed && (
              <button
                onClick={handleLogout}
                title="Logout Session"
                className="p-1.5 text-[#94A3B8] hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
              >
                <LogOut size={16} />
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* ── Main Content Container ──────────────────────── */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-[#0B192C]">
        {/* Header Bar */}
        <header className="h-16 border-b border-[#334E68]/60 flex items-center justify-between px-6 bg-[#14283D]/60 backdrop-blur-md flex-shrink-0 z-10">
          {/* Left search & context */}
          <div className="flex items-center gap-4">
            <div className="relative hidden sm:block">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search FIR, Case ID, Evidence Hash, SHA-256..."
                className="bg-[#0B192C]/70 border border-[#334E68] rounded-xl pl-9 pr-4 py-1.5 text-xs text-[#F5F5F5] placeholder:text-[#94A3B8]/70 focus:outline-none focus:border-[#FF6500]/60 focus:ring-1 focus:ring-[#FF6500]/30 w-80 transition-all font-mono"
              />
            </div>
          </div>

          {/* Quick Actions & Department Badge */}
          <div className="flex items-center gap-3">
            <Link
              href="/scan"
              className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FF6500] hover:bg-[#FF6500]/90 text-white text-xs font-semibold shadow-md shadow-[#FF6500]/20 transition-all"
            >
              <PlusCircle size={14} />
              <span>New Evidence Analysis</span>
            </Link>

            <Link
              href="/cases"
              className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1E3E62] hover:bg-[#1E3E62]/80 text-[#D4AF37] border border-[#D4AF37]/30 text-xs font-semibold transition-all"
            >
              <FileText size={14} />
              <span>Issue Sec 65B PDF</span>
            </Link>

            <div className="h-4 w-px bg-[#334E68]" />

            <div className="flex items-center gap-2 bg-[#0B192C]/50 px-3 py-1.5 rounded-xl border border-[#334E68]/40">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[11px] font-mono text-[#94A3B8]">
                CHANDIGARH CYBER CELL
              </span>
            </div>
          </div>
        </header>

        {/* Viewport Content */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-gradient-to-b from-[#0B192C] to-[#0D1E36]">
          {children}
        </div>
      </main>
    </div>
  );
}
