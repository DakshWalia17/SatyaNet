"use client";

import { useState } from "react";
import { FileText, X, Download, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function TakedownNoticeModal({ isOpen, onClose, fileHash }: { isOpen: boolean, onClose: () => void, fileHash: string }) {
  const [loading, setLoading] = useState(false);
  const [noticeDraft, setNoticeDraft] = useState<string | null>(null);

  const generateNotice = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/notice/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: "FIR-2026-CH-992",
          officer_name: "Daksh Walia, Insp.",
          station_name: "Chandigarh",
          file_hash: fileHash || "N/A",
          platform: "Meta Platforms, Inc.",
          url: "https://facebook.com/suspicious-link-123"
        })
      });
      const data = await res.json();
      setNoticeDraft(data.notice_text);
    } catch (e) {
      console.error(e);
      setNoticeDraft("Error generating notice. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="w-full max-w-2xl bg-sidebar border border-border rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
          >
            <div className="flex items-center justify-between p-4 border-b border-border bg-background">
              <div className="flex items-center gap-2 text-foreground font-semibold">
                <FileText size={18} className="text-primary" />
                Section 91 Takedown Notice Generator
              </div>
              <button onClick={onClose} className="p-1 rounded-md hover:bg-muted text-muted-foreground transition-colors">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto flex-1">
              {!noticeDraft && !loading && (
                <div className="text-center py-12">
                  <FileText size={48} className="mx-auto text-muted-foreground mb-4 opacity-50" />
                  <h3 className="text-lg font-medium mb-2">Generate Legal Notice</h3>
                  <p className="text-sm text-muted-foreground mb-6">Automatically draft a Section 91 CrPC notice for the detected synthetic media.</p>
                  <button 
                    onClick={generateNotice}
                    className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-2.5 rounded-lg font-medium transition-colors"
                  >
                    Generate Draft
                  </button>
                </div>
              )}

              {loading && (
                <div className="text-center py-12 space-y-4">
                  <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
                  <p className="text-sm text-muted-foreground animate-pulse">Consulting legal templates...</p>
                </div>
              )}

              {noticeDraft && !loading && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className="flex items-center gap-2 text-success mb-2">
                    <CheckCircle2 size={16} />
                    <span className="text-sm font-medium">Draft Generated Successfully</span>
                  </div>
                  <div className="bg-background border border-border rounded-lg p-6 font-mono text-xs whitespace-pre-wrap text-muted-foreground leading-relaxed h-[400px] overflow-y-auto custom-scrollbar">
                    {noticeDraft}
                  </div>
                </motion.div>
              )}
            </div>

            {noticeDraft && !loading && (
              <div className="p-4 border-t border-border bg-background flex justify-end gap-3">
                <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm font-medium border border-border hover:bg-muted transition-colors">
                  Cancel
                </button>
                <button className="px-4 py-2 rounded-lg text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors flex items-center gap-2">
                  <Download size={16} />
                  Export PDF
                </button>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
