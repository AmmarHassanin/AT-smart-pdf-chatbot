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
        <div className="relative mx-auto flex h-64 w-64 items-center justify-center">
          <div className="absolute inset-0 rounded-full bg-[var(--gold-glow)] opacity-40 blur-3xl" />

          <motion.div
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            className="relative flex h-40 w-40 items-center justify-center rounded-[28px] border border-[var(--gold-border)] bg-gradient-to-br from-[var(--card)] to-[var(--elevated)] shadow-premium"
          >
            <Bot size={64} className="relative text-[var(--gold)]" strokeWidth={1.3} />
          </motion.div>
        </div>

        <div>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-3 inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[var(--card)] px-3 py-1 text-xs font-medium text-[var(--muted)]">
              <Sparkles size={12} className="text-[var(--gold)]" /> AI-powered document intelligence
            </div>
            <h1 className="text-4xl font-extrabold leading-[1.1] tracking-tight md:text-5xl">
              <span className="block">{t("welcome_title")}</span>
              <span className="block text-[var(--gold)]">{t("welcome_accent")}</span>
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
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: 0.1 + i * 0.05 }}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="group rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] p-4 text-start transition-colors duration-200 hover:border-[var(--gold-border)]"
              >
                <div className="mb-2.5 flex h-9 w-9 items-center justify-center rounded-[10px] border border-[var(--border)] bg-[var(--elevated)] text-[var(--gold)] transition-colors duration-200 group-hover:border-[var(--gold-border)]">
                  <f.icon size={18} />
                </div>
                <div className="text-sm font-bold">{t(f.title)}</div>
                <div className="mt-1 text-xs leading-relaxed text-[var(--muted)]">{t(f.desc)}</div>
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
