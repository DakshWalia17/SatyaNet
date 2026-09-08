/**
 * CyberShield — Pure CSS/SVG animated security shield for the login right panel.
 * Uses layered SVG with CSS animations for a premium 3D-like glow effect.
 * Developer: Daksh Walia, B.Tech AIML, CGC Mohali
 */

"use client";

import { motion } from "framer-motion";

export default function CyberShield() {
  return (
    <div className="cyber-shield-container">
      {/* Ambient background glow layers */}
      <div className="shield-ambient-glow" />
      <div className="shield-ambient-glow-secondary" />

      {/* Orbiting rings */}
      <div className="orbit-ring orbit-ring-1">
        <div className="orbit-dot" />
      </div>
      <div className="orbit-ring orbit-ring-2">
        <div className="orbit-dot orbit-dot-gold" />
      </div>
      <div className="orbit-ring orbit-ring-3">
        <div className="orbit-dot" />
      </div>

      {/* Central shield SVG */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
        className="shield-core"
      >
        <svg
          viewBox="0 0 200 230"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="shield-svg"
        >
          {/* Shield outer glow filter */}
          <defs>
            <filter id="shieldGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <linearGradient id="shieldGrad" x1="100" y1="0" x2="100" y2="230" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#1E40AF" stopOpacity="0.7" />
              <stop offset="100%" stopColor="#0A192F" stopOpacity="0.5" />
            </linearGradient>
            <linearGradient id="shieldStroke" x1="100" y1="0" x2="100" y2="230" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#60A5FA" />
              <stop offset="50%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#D4AF37" />
            </linearGradient>
            <linearGradient id="innerGlow" x1="100" y1="30" x2="100" y2="200" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#0A192F" stopOpacity="0.1" />
            </linearGradient>
          </defs>

          {/* Shield body */}
          <path
            d="M100 10 L185 50 L185 120 C185 170 145 210 100 225 C55 210 15 170 15 120 L15 50 Z"
            fill="url(#shieldGrad)"
            stroke="url(#shieldStroke)"
            strokeWidth="2"
            filter="url(#shieldGlow)"
            className="shield-body"
          />

          {/* Inner shield line */}
          <path
            d="M100 30 L170 60 L170 120 C170 162 138 195 100 208 C62 195 30 162 30 120 L30 60 Z"
            fill="url(#innerGlow)"
            stroke="#3B82F6"
            strokeWidth="0.8"
            strokeOpacity="0.4"
          />

          {/* Lock / checkmark icon in center */}
          <g transform="translate(70, 85)">
            {/* Lock body */}
            <rect
              x="6"
              y="22"
              width="48"
              height="38"
              rx="4"
              fill="none"
              stroke="#D4AF37"
              strokeWidth="2.5"
              className="lock-body"
            />
            {/* Lock shackle */}
            <path
              d="M18 22 V14 C18 6 24 0 30 0 C36 0 42 6 42 14 V22"
              fill="none"
              stroke="#D4AF37"
              strokeWidth="2.5"
              strokeLinecap="round"
              className="lock-shackle"
            />
            {/* Keyhole */}
            <circle cx="30" cy="37" r="4" fill="#D4AF37" className="keyhole-dot" />
            <path d="M30 41 L30 50" stroke="#D4AF37" strokeWidth="2.5" strokeLinecap="round" />
          </g>

          {/* Scan line effect */}
          <rect
            x="15"
            y="0"
            width="170"
            height="2"
            fill="#3B82F6"
            opacity="0.6"
            className="scan-line"
          />
        </svg>
      </motion.div>

      {/* Floating data particles */}
      <div className="particle particle-1" />
      <div className="particle particle-2" />
      <div className="particle particle-3" />
      <div className="particle particle-4" />
      <div className="particle particle-5" />
      <div className="particle particle-6" />

      {/* Grid overlay */}
      <div className="grid-overlay" />

      {/* Status text below shield */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5, duration: 0.8 }}
        className="shield-status"
      >
        <div className="status-indicator">
          <span className="status-dot" />
          <span className="status-text">ENCRYPTION ACTIVE • AES-256</span>
        </div>
        <p className="shield-tagline">
          AI-Powered Media Forensics
        </p>
      </motion.div>
    </div>
  );
}
