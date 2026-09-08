/**
 * Command Center Overview — Chandigarh Police Cyber Cell AIMD Dashboard
 * Developer: Daksh Walia, B.Tech AIML
 */

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Activity,
  ShieldAlert,
  Fingerprint,
  Users,
  TrendingUp,
  AlertTriangle,
  FileAudio,
  FileVideo,
  Image as ImageIcon,
  Clock,
  ChevronRight,
  Download,
  FileText,
  Upload,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  Zap,
  ArrowRight,
  Copy,
  Check
} from "lucide-react";
import { listEvidence, EvidenceItem, buildSection65bPdfUrl } from "@/lib/api";

const fadeIn = {
  hidden: { opacity: 0, y: 16 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5 },
  }),
};

const stats = [
  {
    label: "Active Cyber Cases",
    value: "128",
    change: "+14%",
    changeType: "up" as const,
    icon: Activity,
    color: "text-[#FF6500]",
    bg: "bg-[#FF6500]/10 border-[#FF6500]/20",
  },
  {
    label: "Deepfakes Intercepted",
    value: "342",
    change: "Critical",
    changeType: "critical" as const,
    icon: Fingerprint,
    color: "text-rose-400",
    bg: "bg-rose-500/10 border-rose-500/20",
  },
  {
    label: "Secured Evidence Files",
    value: "89",
    change: "SHA-256 Immutable",
    changeType: "neutral" as const,
    icon: ShieldAlert,
    color: "text-[#D4AF37]",
    bg: "bg-[#D4AF37]/10 border-[#D4AF37]/20",
  },
  {
    label: "Certificates Issued",
    value: "64",
    change: "Sec 65B Act",
    changeType: "neutral" as const,
    icon: Users,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10 border-emerald-500/20",
  },
];

const mockThreatLogs = [
  {
    id: "CHD-EVI-9842",
    type: "Voice Clone Synthesis",
    source: "Telegram Audio Dispatch",
    risk: "CRITICAL",
    engine: "ElevenLabs v2 Synthesizer",
    score: 98.5,
    time: "2m ago",
    mediaType: "audio",
  },
  {
    id: "CHD-EVI-9841",
    type: "Deepfake Video Face Swap",
    source: "Web Investigation",
    risk: "HIGH",
    engine: "DeepFaceLab / Runway Gen-3",
    score: 94.0,
    time: "15m ago",
    mediaType: "video",
  },
  {
    id: "CHD-EVI-9840",
    type: "Generative Image Forgery",
    source: "Extension Live Scan",
    risk: "HIGH",
    engine: "Midjourney v6 / SDXL",
    score: 91.2,
    time: "42m ago",
    mediaType: "image",
  },
  {
    id: "CHD-EVI-9839",
    type: "Police Portal Impersonation",
    source: "Domain Reputation Engine",
    risk: "CRITICAL",
    engine: "Deceptive Phishing Domain",
    score: 99.1,
    time: "1h ago",
    mediaType: "web",
  },
];

export default function DashboardPage() {
  const [evidenceFiles, setEvidenceFiles] = useState<EvidenceItem[]>([]);
  const [loadingEvidence, setLoadingEvidence] = useState(true);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Section 65B Quick Modal state
  const [show65bModal, setShow65bModal] = useState(false);
  const [caseIdInput, setCaseIdInput] = useState("FIR-2026-CHD-042");
  const [badgeIdInput, setBadgeIdInput] = useState("CHD-CYB-0042");
  const [officerNameInput, setOfficerNameInput] = useState("Insp. Daksh Walia");

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        const files = await listEvidence();
        if (isMounted) setEvidenceFiles(files);
      } catch (err) {
        console.warn("Evidence API error, fallback active:", err);
      } finally {
        if (isMounted) setLoadingEvidence(false);
      }
    }
    loadData();
  }, []);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(text);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const handleDownload65b = () => {
    const pdfUrl = buildSection65bPdfUrl({
      caseId: caseIdInput,
      officerBadgeId: badgeIdInput,
      officerName: officerNameInput,
      notes: "Certified Section 65B Indian Evidence Act record generated via AIMD Forensic Engine.",
    });
    window.open(pdfUrl, "_blank");
    setShow65bModal(false);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-[#14283D] via-[#1E3E62]/60 to-[#0B192C] p-5 rounded-2xl border border-[#334E68]/60 shadow-xl"
      >
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/40 tracking-wider uppercase">
              LAW ENFORCEMENT PORTAL
            </span>
            <span className="text-[10px] font-mono text-[#94A3B8]">v2.4 FORENSICS</span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#F5F5F5] tracking-tight mt-1.5 flex items-center gap-2">
            Chandigarh Police Cyber Crime Cell Command Center
          </h1>
          <p className="text-xs text-[#94A3B8] mt-1">
            AI Media Forensics, Deepfake Origin Tracing & Section 65B Chain of Custody System
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/scan"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#FF6500] to-[#E55B00] hover:from-[#FF6500]/90 text-white font-semibold text-xs shadow-lg shadow-[#FF6500]/25 transition-all"
          >
            <Zap size={15} />
            <span>Launch Forensics Scanner</span>
          </Link>
          <button
            onClick={() => setShow65bModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#14283D] border border-[#D4AF37]/40 text-[#D4AF37] hover:bg-[#D4AF37]/10 font-semibold text-xs transition-all"
          >
            <FileText size={15} />
            <span>Quick Sec 65B PDF</span>
          </button>
        </div>
      </motion.div>

      {/* Cyber Alert Ticker */}
      <motion.div
        custom={0}
        variants={fadeIn}
        initial="hidden"
        animate="visible"
        className="bg-[#FF6500]/10 border border-[#FF6500]/30 rounded-xl p-4 flex items-start gap-4"
      >
        <div className="bg-[#FF6500]/20 p-2.5 rounded-lg text-[#FF6500] flex-shrink-0">
          <AlertTriangle size={20} />
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-[#FF6500] text-xs uppercase tracking-wider flex items-center gap-2">
            ⚠️ HIGH-PRIORITY DEEPFAKE CAMPAIGN DETECTED
          </h3>
          <p className="text-xs text-[#F5F5F5]/90 mt-1 leading-relaxed">
            Inter-station signal match: ElevenLabs synthetic audio clone detected across 3 active FIR investigations. Forensic SHA-256 chain verified and flagged for court certification.
          </p>
        </div>
        <Link
          href="/scan"
          className="text-xs text-[#FF6500] hover:underline flex items-center gap-1 font-semibold flex-shrink-0"
        >
          Inspect Signals <ChevronRight size={14} />
        </Link>
      </motion.div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            custom={i + 1}
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            className="bg-[#14283D]/60 border border-[#334E68]/50 rounded-2xl p-5 hover:border-[#FF6500]/30 transition-all duration-300 group shadow-md hover:shadow-xl"
          >
            <div className="flex items-center justify-between mb-3">
              <div className={`p-2.5 rounded-xl border ${stat.bg}`}>
                <stat.icon size={20} className={stat.color} />
              </div>
              {stat.changeType === "up" && (
                <div className="flex items-center gap-1 text-emerald-400 text-xs font-semibold">
                  <TrendingUp size={13} />
                  {stat.change}
                </div>
              )}
              {stat.changeType === "critical" && (
                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  {stat.change}
                </span>
              )}
              {stat.changeType === "neutral" && (
                <span className="text-[10px] font-mono font-medium text-[#94A3B8]">
                  {stat.change}
                </span>
              )}
            </div>
            <p className="text-2xl font-extrabold text-[#F5F5F5] tracking-tight">{stat.value}</p>
            <p className="text-xs text-[#94A3B8] mt-1 font-medium">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Main Grid: Threat Feed + Custody Log */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Feed (2 Cols) */}
        <motion.div
          custom={5}
          variants={fadeIn}
          initial="hidden"
          animate="visible"
          className="lg:col-span-2 bg-[#14283D]/60 border border-[#334E68]/60 rounded-2xl overflow-hidden shadow-lg"
        >
          <div className="px-6 py-4 border-b border-[#334E68]/60 flex items-center justify-between bg-[#14283D]">
            <div>
              <h3 className="font-bold text-sm text-[#F5F5F5] uppercase tracking-wider flex items-center gap-2">
                <ShieldAlert size={16} className="text-[#FF6500]" />
                Recent Cyber Cell Forensics Intelligence
              </h3>
              <p className="text-xs text-[#94A3B8] mt-0.5">Automated detection telemetry from media, audio, and web endpoints</p>
            </div>
            <Link href="/scan" className="text-xs text-[#FF6500] hover:underline font-semibold flex items-center gap-1">
              Full Forensics Lab <ArrowRight size={12} />
            </Link>
          </div>

          <div className="divide-y divide-[#334E68]/40">
            {mockThreatLogs.map((log) => (
              <div
                key={log.id}
                className="px-6 py-4 flex items-center justify-between hover:bg-[#1E3E62]/30 transition-colors group"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="p-2.5 rounded-xl bg-[#0B192C] border border-[#334E68]/60 text-[#D4AF37]">
                    {log.mediaType === "audio" ? (
                      <FileAudio size={18} />
                    ) : log.mediaType === "video" ? (
                      <FileVideo size={18} />
                    ) : (
                      <ImageIcon size={18} />
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-sm text-[#F5F5F5] truncate">{log.type}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-[#D4AF37] font-mono bg-[#D4AF37]/10 px-1.5 py-0.5 rounded border border-[#D4AF37]/20">
                        {log.id}
                      </span>
                      <span className="text-[10px] text-[#94A3B8]">• {log.source}</span>
                      <span className="text-[10px] text-[#FF6500] font-medium">• {log.engine}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 flex-shrink-0 ml-4">
                  <div className="hidden sm:flex items-center gap-2 w-32">
                    <div className="flex-1 h-2 rounded-full bg-[#0B192C] overflow-hidden border border-[#334E68]/40">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-[#FF6500] to-rose-500"
                        style={{ width: `${log.score}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono font-bold text-[#F5F5F5] w-9 text-right">
                      {log.score}%
                    </span>
                  </div>

                  <span
                    className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${
                      log.risk === "CRITICAL"
                        ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
                        : "bg-[#FF6500]/20 text-[#FF6500] border-[#FF6500]/30"
                    }`}
                  >
                    {log.risk}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Evidence Vault Direct Access (1 Col) */}
        <motion.div
          custom={6}
          variants={fadeIn}
          initial="hidden"
          animate="visible"
          className="space-y-4"
        >
          {/* Quick Upload Widget */}
          <div className="bg-[#14283D]/60 border border-[#334E68]/60 rounded-2xl p-5 shadow-lg">
            <h3 className="font-bold text-sm text-[#F5F5F5] uppercase tracking-wider mb-2 flex items-center gap-2">
              <Upload size={16} className="text-[#D4AF37]" />
              Immutable Evidence Upload
            </h3>
            <p className="text-xs text-[#94A3B8] mb-4">
              Upload evidence file directly to server custody with cryptographic SHA-256 locking.
            </p>

            <Link
              href="/evidence"
              className="w-full py-3 px-4 rounded-xl bg-[#0B192C] border-2 border-dashed border-[#334E68] hover:border-[#FF6500]/60 flex flex-col items-center justify-center gap-1 transition-all group cursor-pointer"
            >
              <Upload size={24} className="text-[#94A3B8] group-hover:text-[#FF6500] transition-colors" />
              <span className="text-xs font-semibold text-[#F5F5F5] group-hover:text-[#FF6500]">
                Open Immutable Evidence Vault
              </span>
              <span className="text-[10px] text-[#94A3B8]">Supports MP4, WAV, MP3, JPG, PNG</span>
            </Link>
          </div>

          {/* Immutable Evidence Live Table */}
          <div className="bg-[#14283D]/60 border border-[#334E68]/60 rounded-2xl p-5 shadow-lg">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-xs text-[#F5F5F5] uppercase tracking-wider flex items-center gap-1.5">
                <ShieldCheck size={14} className="text-emerald-400" />
                Custody Registry ({evidenceFiles.length})
              </h3>
              <Link href="/evidence" className="text-[10px] text-[#FF6500] hover:underline font-semibold">
                View All
              </Link>
            </div>

            {loadingEvidence ? (
              <div className="py-6 text-center text-xs text-[#94A3B8]">
                Loading server evidence registry...
              </div>
            ) : evidenceFiles.length === 0 ? (
              <div className="py-6 text-center text-xs text-[#94A3B8] bg-[#0B192C]/40 rounded-xl border border-[#334E68]/40">
                No active evidence files uploaded yet.
              </div>
            ) : (
              <div className="space-y-2">
                {evidenceFiles.slice(0, 3).map((item) => (
                  <div
                    key={item.job_id}
                    className="p-2.5 rounded-xl bg-[#0B192C]/60 border border-[#334E68]/40 flex items-center justify-between text-xs"
                  >
                    <div className="min-w-0 pr-2">
                      <p className="font-medium text-[#F5F5F5] truncate text-xs">{item.filename}</p>
                      <p className="text-[10px] font-mono text-[#D4AF37] truncate mt-0.5">
                        {item.sha256.substring(0, 16)}...
                      </p>
                    </div>
                    <button
                      onClick={() => copyToClipboard(item.sha256)}
                      className="p-1.5 rounded-lg text-[#94A3B8] hover:text-[#F5F5F5] hover:bg-[#1E3E62] transition-colors"
                      title="Copy SHA-256 Hash"
                    >
                      {copiedHash === item.sha256 ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Section 65B Quick PDF Modal */}
      {show65bModal && (
        <div className="fixed inset-0 z-50 bg-[#0B192C]/80 backdrop-blur-sm flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-[#14283D] border border-[#D4AF37]/40 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4"
          >
            <div className="flex items-center justify-between border-b border-[#334E68]/60 pb-3">
              <div className="flex items-center gap-2">
                <FileText className="text-[#D4AF37]" size={20} />
                <h3 className="font-bold text-sm text-[#F5F5F5] uppercase tracking-wider">
                  Issue Section 65B Certificate
                </h3>
              </div>
              <button
                onClick={() => setShow65bModal(false)}
                className="text-[#94A3B8] hover:text-white text-xs font-bold px-2 py-1 rounded bg-[#0B192C]"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-[#94A3B8] font-medium block mb-1">
                  FIR / Case Reference ID
                </label>
                <input
                  type="text"
                  value={caseIdInput}
                  onChange={(e) => setCaseIdInput(e.target.value)}
                  className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl px-3 py-2 text-xs text-[#F5F5F5] font-mono focus:outline-none focus:border-[#D4AF37]"
                />
              </div>

              <div>
                <label className="text-xs text-[#94A3B8] font-medium block mb-1">
                  Certifying Officer Badge ID
                </label>
                <input
                  type="text"
                  value={badgeIdInput}
                  onChange={(e) => setBadgeIdInput(e.target.value)}
                  className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl px-3 py-2 text-xs text-[#F5F5F5] font-mono focus:outline-none focus:border-[#D4AF37]"
                />
              </div>

              <div>
                <label className="text-xs text-[#94A3B8] font-medium block mb-1">
                  Certifying Officer Full Name
                </label>
                <input
                  type="text"
                  value={officerNameInput}
                  onChange={(e) => setOfficerNameInput(e.target.value)}
                  className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl px-3 py-2 text-xs text-[#F5F5F5] focus:outline-none focus:border-[#D4AF37]"
                />
              </div>
            </div>

            <div className="pt-2 flex items-center justify-end gap-3">
              <button
                onClick={() => setShow65bModal(false)}
                className="px-4 py-2 rounded-xl text-xs text-[#94A3B8] hover:text-white font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleDownload65b}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#B8941F] text-[#0B192C] font-bold text-xs shadow-lg shadow-[#D4AF37]/20 flex items-center gap-1.5"
              >
                <Download size={14} />
                <span>Generate PDF Certificate</span>
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
