"use client";

import { Mic, Waves, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

export default function AudioForensicsPanel({ data }: { data: any }) {
  if (!data) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-gradient rounded-xl p-6 border border-border"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-primary/20 p-2 rounded-lg text-primary">
            <Mic size={24} />
          </div>
          <div>
            <h3 className="font-bold text-lg">Audio Forensics Analysis</h3>
            <p className="text-xs text-muted-foreground">ID: {data.analysis_id}</p>
          </div>
        </div>
        {data.digital_arrest_risk === "HIGH" && (
          <div className="flex items-center gap-2 bg-destructive/20 text-destructive px-4 py-2 rounded-full border border-destructive/50">
            <AlertTriangle size={16} />
            <span className="text-xs font-bold uppercase tracking-wider">{data.warning_tag}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-background/50 rounded-lg p-4 border border-border">
          <p className="text-sm text-muted-foreground mb-1">Detected Engine</p>
          <p className="font-semibold text-foreground">{data.engine}</p>
        </div>
        <div className="bg-background/50 rounded-lg p-4 border border-border">
          <p className="text-sm text-muted-foreground mb-1">Confidence Score</p>
          <div className="flex items-center gap-4">
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${data.confidence_score}%` }}
                className="h-full bg-destructive"
              />
            </div>
            <p className="font-bold text-destructive">{data.confidence_score}%</p>
          </div>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <h4 className="text-sm font-semibold flex items-center gap-2">
          <Waves size={16} className="text-primary" />
          Mel-Spectrogram Anomalies
        </h4>
        <div className="bg-background p-4 rounded-lg border border-border relative overflow-hidden h-32 flex items-end justify-center gap-1">
          {/* Dummy Spectrogram Visualization */}
          {Array.from({ length: 40 }).map((_, i) => (
            <motion.div
              key={i}
              initial={{ height: "10%" }}
              animate={{ height: `${Math.random() * 80 + 20}%` }}
              transition={{ repeat: Infinity, duration: 1.5, repeatType: "mirror", delay: i * 0.05 }}
              className={`w-2 rounded-t-sm ${i > 15 && i < 25 ? 'bg-destructive' : 'bg-primary/50'}`}
            />
          ))}
          <div className="absolute top-2 left-2 bg-background/80 px-2 py-1 rounded text-[10px] text-muted-foreground backdrop-blur-sm border border-border">
            Frequency (Hz) vs Time (s)
          </div>
          <div className="absolute bottom-2 right-2 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-destructive animate-ping"></span>
            <span className="text-[10px] text-destructive font-bold">SYNTHETIC SIGNATURE DETECTED</span>
          </div>
        </div>
      </div>

      <div>
        <h4 className="text-sm font-semibold mb-3">Identified Anomalies</h4>
        <ul className="space-y-2">
          {data.anomalies.map((anomaly: string, idx: number) => (
            <li key={idx} className="text-sm flex items-start gap-3 bg-muted/30 p-3 rounded-md border border-border/50">
              <span className="text-destructive mt-0.5">•</span>
              <span className="text-muted-foreground">{anomaly}</span>
            </li>
          ))}
        </ul>
      </div>

    </motion.div>
  );
}
