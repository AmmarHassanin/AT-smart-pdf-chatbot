"use client";

import { motion } from "framer-motion";
import { Bot, FileText, HelpCircle, Languages, List, MessageCircle, Sparkles } from "lucide-react";
import { useI18n } from "@/lib/i18n";

const FEATURES = [
  { key: "ask", icon: MessageCircle, title: "feat_ask", desc: "feat_ask_desc" },
  { key: "summary", icon: FileText, title: "feat_sum", desc: "feat_sum_desc" },
  { key: "translate", icon: Languages, title: "feat_tr", desc: "feat_tr_desc" },
  { key: "key_points", icon: List, title: "feat_keys", desc: "feat_keys_desc" },
  { key: "explain", icon: HelpCircle, title: "feat_explain", desc: "feat_explain_desc" },
];

export function Hero({ onFeatureClick }: { onFeatureClick: (task: string) => void }) {
  const { t } = useI18n();

  return (
    <div className="mx-auto max-w-6xl px-4 py-14">
      <div className="grid grid-cols-1 items-center gap-14 md:grid-cols-[1fr_1.25fr]">
        <div className="relative mx-auto flex h-72 w-72 items-center justify-center">
          <div className="gradient-mesh animate-drift absolute inset-0 rounded-full blur-3xl" />

          {/* orbit rings */}
          <motion.div
            className="absolute inset-0 rounded-full border border-dashed border-[var(--gold-border)]/40"
            animate={{ rotate: 360 }}
            transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
          />
          <motion.div
            className="absolute inset-6 rounded-full border border-[var(--gold-border)]/25"
            animate={{ rotate: -360 }}
            transition={{ duration: 28, repeat: Infinity, ease: "linear" }}
          />
          <motion.div
            className="absolute h-2.5 w-2.5 rounded-full bg-[var(--gold)] shadow-[0_0_12px_var(--gold)]"
            animate={{ rotate: 360 }}
            transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
            style={{ top: "0%", left: "50%", transformOrigin: "0 144px" }}
          />

          <motion.div
            animate={{ y: [0, -12, 0] }}
            transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
            className="relative flex h-44 w-44 items-center justify-center rounded-[32px] border border-[var(--gold-border)] bg-gradient-to-br from-[#1b1710] via-[var(--card)] to-[var(--elevated)] shadow-premium"
            style={{ boxShadow: "0 0 80px -10px var(--gold-glow), inset 0 1px 0 rgba(255,255,255,0.06)" }}
          >
            <div className="absolute inset-0 rounded-[32px] bg-gradient-to-br from-[var(--gold-dim)] to-transparent opacity-60" />
            <Bot size={76} className="relative text-[var(--gold)] drop-shadow-[0_0_20px_var(--gold-glow)]" strokeWidth={1.3} />
            <motion.div
              className="absolute -right-2 -top-2 flex h-7 w-7 items-center justify-center rounded-full border border-[var(--gold-border)] bg-[var(--card)]"
              animate={{ scale: [1, 1.15, 1], opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 2.4, repeat: Infinity }}
            >
              <Sparkles size={13} className="text-[var(--gold)]" />
            </motion.div>
          </motion.div>
        </div>

        <div>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-3 inline-flex items-center gap-1.5 rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-xs font-semibold text-[var(--gold)]">
              <Sparkles size={12} /> AI-powered document intelligence
            </div>
            <h1 className="text-4xl font-extrabold leading-[1.1] tracking-tight md:text-6xl">
              <span className="block">{t("welcome_title")}</span>
              <span className="text-gradient-gold block">{t("welcome_accent")}</span>
            </h1>
          </motion.div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15, duration: 0.5 }}
            className="mt-4 max-w-md text-base leading-relaxed text-[var(--muted)]"
          >
            {t("welcome_sub")}
          </motion.p>

          <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-3">
            {FEATURES.map((f, i) => (
              <motion.button
                key={f.key}
                onClick={() => onFeatureClick(f.key)}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.1 + i * 0.06 }}
                whileHover={{ y: -3 }}
                whileTap={{ scale: 0.98 }}
                className="group relative overflow-hidden rounded-[var(--radius-lg)] border border-[var(--border)] bg-gradient-to-br from-[var(--card)] to-[var(--elevated)] p-4 text-start shadow-premium transition-[border-color,box-shadow] duration-300 hover:border-[var(--gold-border)] hover:shadow-[0_12px_32px_-8px_var(--gold-glow)]"
              >
                <div className="pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full bg-[var(--gold-glow)] opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-60" />
                <div className="relative mb-2.5 flex h-9 w-9 items-center justify-center rounded-[10px] border border-[var(--gold-border)] bg-gradient-to-br from-[var(--gold-dim)] to-transparent text-[var(--gold)] transition-transform duration-300 group-hover:scale-110">
                  <f.icon size={18} />
                </div>
                <div className="relative text-sm font-bold">{t(f.title)}</div>
                <div className="relative mt-1 text-xs leading-relaxed text-[var(--muted)]">{t(f.desc)}</div>
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
