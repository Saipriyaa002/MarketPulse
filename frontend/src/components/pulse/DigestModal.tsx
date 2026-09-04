"use client";

import React from "react";
import { X, Sparkles, AlertCircle, Compass, FileText, CheckCircle2 } from "lucide-react";

interface DigestModalProps {
  digest: any;
  onClose: () => void;
}

export const DigestModal: React.FC<DigestModalProps> = ({ digest, onClose }) => {
  if (!digest) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div 
        className="w-full max-w-2xl bg-[#0f1522] border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-800 bg-[#121a2a] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">What Did I Miss?</h2>
              <p className="text-xs text-slate-400">Executive Watchlist Intelligence Briefing</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-5 overflow-y-auto">
          {/* Executive Headline */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 via-slate-900 to-indigo-500/10 border border-emerald-500/20 text-slate-200 text-sm font-medium leading-relaxed">
            {digest.headline}
          </div>

          {/* Sections */}
          <div className="space-y-4">
            {digest.sections?.map((sec: any, idx: number) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2 flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  {sec.title}
                </h3>
                {sec.content && (
                  <p className="text-xs text-slate-300 leading-relaxed">{sec.content}</p>
                )}
                {sec.bullets && (
                  <ul className="space-y-1.5 mt-2">
                    {sec.bullets.map((b: string, bIdx: number) => (
                      <li key={bIdx} className="text-xs text-slate-300 flex items-start gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 mt-1.5 flex-shrink-0" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>

          {/* Conclusion */}
          <div className="p-3 rounded-lg bg-slate-900/40 border border-slate-800 text-xs text-slate-400 italic">
            {digest.conclusion}
          </div>
        </div>
      </div>
    </div>
  );
};
