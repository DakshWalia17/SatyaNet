/**
 * Section 65B Indian Evidence Act PDF Certificate Hub — Chandigarh Police Cyber Cell
 * Developer: Daksh Walia, B.Tech AIML
 */

"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  FileText,
  Download,
  ShieldCheck,
  Award,
  Lock,
  UserCheck,
  CheckCircle2,
  ExternalLink,
  FileCheck,
  AlertCircle
} from "lucide-react";
import { buildSection65bPdfUrl } from "@/lib/api";

export default function Section65bCasesPage() {
  const [caseId, setCaseId] = useState("FIR-2026-CHD-042");
  const [officerBadgeId, setOfficerBadgeId] = useState("CHD-CYB-0042");
  const [officerName, setOfficerName] = useState("Insp. Daksh Walia");
  const [mediaJobId, setMediaJobId] = useState("");
  const [audioJobId, setAudioJobId] = useState("");
  const [notes, setNotes] = useState(
    "Certificate issued under Section 65B of Indian Evidence Act. Chain of custody SHA-256 integrity re-verified upon court draft generation."
  );

  const pdfUrl = buildSection65bPdfUrl({
    caseId,
    officerBadgeId,
    officerName,
    mediaJobId: mediaJobId.trim() || undefined,
    audioJobId: audioJobId.trim() || undefined,
    notes,
  });

  const handleDownload = () => {
    window.open(pdfUrl, "_blank");
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-[#14283D] via-[#1E3E62]/40 to-[#0B192C] p-5 rounded-2xl border border-[#334E68]/60 shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/30 uppercase">
              LEGAL CERTIFICATE ENGINE
            </span>
            <span className="text-[10px] font-mono text-[#94A3B8]">INDIAN EVIDENCE ACT</span>
          </div>
          <h1 className="text-xl font-extrabold text-[#F5F5F5] tracking-tight mt-1 flex items-center gap-2">
            Section 65B Court Certificate Generator
          </h1>
          <p className="text-xs text-[#94A3B8] mt-0.5">
            Generate court-admissible electronic record certificates with automated SHA-256 chain of custody verification.
          </p>
        </div>

        <button
          onClick={handleDownload}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#B8941F] text-[#0B192C] font-extrabold text-xs shadow-lg shadow-[#D4AF37]/20 transition-all hover:scale-[1.02]"
        >
          <Download size={16} />
          <span>Generate Court PDF</span>
        </button>
      </motion.div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Column (2 cols) */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 bg-[#14283D]/60 border border-[#334E68]/60 rounded-2xl p-6 shadow-xl space-y-5"
        >
          <div className="border-b border-[#334E68]/60 pb-3 flex items-center justify-between">
            <h3 className="font-bold text-sm text-[#F5F5F5] uppercase tracking-wider flex items-center gap-2">
              <FileCheck size={16} className="text-[#D4AF37]" />
              Case & Certifying Officer Details
            </h3>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              LEGAL STAMP READY
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-[#94A3B8] font-semibold block mb-1">
                FIR / Case Reference ID *
              </label>
              <input
                type="text"
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder="e.g. FIR-2026-CHD-042"
                className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl px-3.5 py-2 text-xs text-[#F5F5F5] font-mono focus:outline-none focus:border-[#D4AF37]"
              />
            </div>

            <div>
              <label className="text-xs text-[#94A3B8] font-semibold block mb-1">
                Certifying Officer Badge ID *
              </label>
              <input
                type="text"
                value={officerBadgeId}
                onChange={(e) => setOfficerBadgeId(e.target.value)}
                placeholder="e.g. CHD-CYB-0042"
                className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl px-3.5 py-2 text-xs text-[#F5F5F5] font-mono focus:outline-none focus:border-[#D4AF37]"
              />
            </div>

            <div>
              <label className="text-xs text-[#94A3B8] font-semibold block mb-1">
                Certifying Officer Full Name
              </label>
              <input
                type="text"
                value={officerName}
                onChange={(e) => setOfficerName(e.target.value)}
                placeholder="e.g. Insp. Daksh Walia"
                className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl px-3.5 py-2 text-xs text-[#F5F5F5] focus:outline-none focus:border-[#D4AF37]"
              />
            </div>

            <div>
              <label className="text-xs text-[#94A3B8] font-semibold block mb-1">
                Media Job ID (Optional)
              </label>
              <input
                type="text"
                value={mediaJobId}
                onChange={(e) => setMediaJobId(e.target.value)}
                placeholder="Paste media job_id from scan"
                className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl px-3.5 py-2 text-xs text-[#F5F5F5] font-mono focus:outline-none focus:border-[#D4AF37]"
              />
            </div>
          </div>

          <div>
            <label className="text-xs text-[#94A3B8] font-semibold block mb-1">
              Audio / Voice Job ID (Optional)
            </label>
            <input
              type="text"
              value={audioJobId}
              onChange={(e) => setAudioJobId(e.target.value)}
              placeholder="Paste audio job_id from scan"
              className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl px-3.5 py-2 text-xs text-[#F5F5F5] font-mono focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          <div>
            <label className="text-xs text-[#94A3B8] font-semibold block mb-1">
              Investigating Officer Remarks & Custody Notes
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-[#0B192C] border border-[#334E68] rounded-xl p-3 text-xs text-[#F5F5F5] focus:outline-none focus:border-[#D4AF37] leading-relaxed"
            />
          </div>

          <div className="pt-2 flex items-center justify-between">
            <span className="text-[11px] text-[#94A3B8]">
              Automated re-hashing algorithm: <strong className="text-[#D4AF37]">SHA-256 Bitwise</strong>
            </span>

            <button
              onClick={handleDownload}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#B8941F] text-[#0B192C] font-extrabold text-xs shadow-lg shadow-[#D4AF37]/20 flex items-center gap-1.5"
            >
              <Download size={15} />
              <span>Download Official PDF Certificate</span>
            </button>
          </div>
        </motion.div>

        {/* Info Column (1 col) */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="bg-[#14283D]/60 border border-[#334E68]/60 rounded-2xl p-5 shadow-lg space-y-3">
            <h3 className="font-bold text-xs text-[#F5F5F5] uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck size={16} className="text-[#D4AF37]" />
              Section 65B Compliance Summary
            </h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Under Section 65B of the Indian Evidence Act 1872 / Bharatiya Sakshya Adhiniyam 2023, electronic evidence requires a certified integrity statement signed by the system in-charge officer.
            </p>
            <ul className="space-[#334E68] text-xs text-[#F5F5F5] space-y-2 pt-2 border-t border-[#334E68]/40">
              <li className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-emerald-400 flex-shrink-0" />
                <span>SHA-256 Hash Verification</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-emerald-400 flex-shrink-0" />
                <span>Officer Badge & Station Seal</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-emerald-400 flex-shrink-0" />
                <span>Court-Admissible PDF Output</span>
              </li>
            </ul>
          </div>

          <div className="bg-[#0B192C]/80 border border-[#334E68]/60 rounded-2xl p-5 shadow-lg text-center space-y-2">
            <Award size={32} className="text-[#D4AF37] mx-auto" />
            <h4 className="font-bold text-xs text-[#F5F5F5] uppercase">Chandigarh Police Cyber Crime Cell</h4>
            <p className="text-[11px] text-[#94A3B8]">
              Engineered by Daksh Walia • AIMD Core Forensics
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
