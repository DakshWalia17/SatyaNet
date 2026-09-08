/**
 * AIMD Login Page — Cinematic split-screen authentication interface.
 * Chandigarh Police Cyber Cell • AI Media Investigation Platform
 * Developer: Daksh Walia, B.Tech AIML, CGC Mohali
 */

"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Shield,
  Eye,
  EyeOff,
  AlertTriangle,
  Loader2,
  Fingerprint,
  Lock,
} from "lucide-react";
import CyberShield from "@/components/CyberShield";

/* ── Animation Variants ───────────────────────────── */
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6 },
  },
};

const fadeInScale = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.8 },
  },
};

export default function LoginPage() {
  const router = useRouter();
  const [badgeId, setBadgeId] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isFocused, setIsFocused] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError("");

      if (!badgeId.trim() || !password.trim()) {
        setError("All fields are mandatory for authentication.");
        return;
      }

      setIsLoading(true);

      // Simulate authentication delay
      await new Promise((resolve) => setTimeout(resolve, 2200));

      // Simulate successful auth → route to dashboard
      setIsLoading(false);
      router.push("/dashboard");
    },
    [badgeId, password, router]
  );

  return (
    <div className="login-page">
      {/* ── Background ambient effects ─────────────── */}
      <div className="login-bg-noise" />
      <div className="login-bg-gradient" />

      <div className="login-split-container">
        {/* ═══════════════════════════════════════════ */}
        {/* LEFT PANEL — Authentication Form           */}
        {/* ═══════════════════════════════════════════ */}
        <motion.div
          className="login-left-panel"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Top branding */}
          <motion.div variants={itemVariants} className="login-branding">
            <div className="branding-badge">
              <Shield className="branding-icon" />
            </div>
            <div>
              <p className="branding-dept">CHANDIGARH POLICE</p>
              <p className="branding-unit">CYBER CELL</p>
            </div>
          </motion.div>

          {/* Form card */}
          <motion.div variants={fadeInScale} className="login-card">
            {/* Title */}
            <motion.div variants={itemVariants} className="login-title-block">
              <h1 className="login-title">
                <span className="title-gradient">AIMD</span>
              </h1>
              <p className="login-subtitle">
                AI Media Investigation, Detection
                <br />& Origin Tracing Platform
              </p>
            </motion.div>

            {/* Separator */}
            <motion.div variants={itemVariants} className="login-separator">
              <div className="separator-line" />
              <span className="separator-text">SECURE ACCESS</span>
              <div className="separator-line" />
            </motion.div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="login-form">
              {/* Badge ID Field */}
              <motion.div variants={itemVariants} className="input-group">
                <label htmlFor="badgeId" className="input-label">
                  <Fingerprint size={14} />
                  Police Badge ID / Officer Email
                </label>
                <div
                  className={`input-wrapper ${
                    isFocused === "badge" ? "input-focused" : ""
                  }`}
                >
                  <input
                    id="badgeId"
                    type="text"
                    value={badgeId}
                    onChange={(e) => setBadgeId(e.target.value)}
                    onFocus={() => setIsFocused("badge")}
                    onBlur={() => setIsFocused(null)}
                    placeholder="e.g. CHD-CYB-0042 or officer@chd.police.in"
                    className="login-input"
                    autoComplete="username"
                    disabled={isLoading}
                  />
                </div>
              </motion.div>

              {/* Password Field */}
              <motion.div variants={itemVariants} className="input-group">
                <label htmlFor="password" className="input-label">
                  <Lock size={14} />
                  Secure Access Password
                </label>
                <div
                  className={`input-wrapper ${
                    isFocused === "password" ? "input-focused" : ""
                  }`}
                >
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setIsFocused("password")}
                    onBlur={() => setIsFocused(null)}
                    placeholder="••••••••••••"
                    className="login-input"
                    autoComplete="current-password"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="password-toggle"
                    tabIndex={-1}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </motion.div>

              {/* Error */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="login-error"
                >
                  <AlertTriangle size={14} />
                  {error}
                </motion.div>
              )}

              {/* Submit button */}
              <motion.div variants={itemVariants}>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="login-submit-btn"
                >
                  {isLoading ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>Verifying Credentials…</span>
                    </>
                  ) : (
                    <>
                      <Shield size={18} />
                      <span>Authenticate Session</span>
                    </>
                  )}
                </button>
              </motion.div>
            </form>

            {/* Security notice */}
            <motion.div variants={itemVariants} className="security-notice">
              <AlertTriangle size={12} className="notice-icon" />
              <p>
                Restricted System: Authorized Law Enforcement Personnel Only.
                Unauthorized access and data extraction are subject to strict
                prosecution under the IT Act 2000.
              </p>
            </motion.div>
          </motion.div>

          {/* Footer */}
          <motion.p variants={itemVariants} className="login-footer">
            © {new Date().getFullYear()} Chandigarh Police — Cyber Crime Cell
            <br />
            <span className="footer-dev">
              Developed by Daksh Walia • B.Tech AIML, CGC Mohali
            </span>
          </motion.p>
        </motion.div>

        {/* ═══════════════════════════════════════════ */}
        {/* RIGHT PANEL — Animated Cyber Shield        */}
        {/* ═══════════════════════════════════════════ */}
        <motion.div
          className="login-right-panel"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.2, delay: 0.4 }}
        >
          <CyberShield />
        </motion.div>
      </div>
    </div>
  );
}
