"use client";

import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { UploadCloud } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function UploadDropzone({ onFiles }: { onFiles: (files: File[]) => void }) {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.5 }}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const files = Array.from(e.dataTransfer.files).filter((f) => f.type === "application/pdf");
        if (files.length) onFiles(files);
      }}
      whileHover={{ scale: 1.005 }}
      className={`relative mx-auto mt-10 max-w-6xl cursor-pointer overflow-hidden rounded-[24px] border border-dashed p-10 text-center shadow-premium transition-colors duration-300 ${
        dragging ? "border-[var(--gold)] bg-[var(--gold-dim)]" : "border-[var(--border)] bg-[var(--card)] hover:border-[var(--gold-border)]"
      }`}
    >
      <div className="gradient-mesh pointer-events-none absolute inset-0 opacity-50" />
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        multiple
        className="hidden"
        onChange={(e) => {
          const files = Array.from(e.target.files || []);
          if (files.length) onFiles(files);
          e.target.value = "";
        }}
      />
      <motion.div
        animate={dragging ? { y: [-2, 2, -2] } : {}}
        transition={{ duration: 0.8, repeat: Infinity }}
        className="relative mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full border border-[var(--gold-border)] bg-gradient-to-br from-[var(--gold-dim)] to-transparent text-[var(--gold)] shadow-[0_0_30px_var(--gold-glow)]"
      >
        <UploadCloud size={28} />
      </motion.div>
      <div className="relative mb-1.5 text-lg font-bold">{t("upload_title")}</div>
      <div className="relative text-sm text-[var(--muted)]">{t("upload_hint")}</div>
      <div className="relative mt-3 inline-flex items-center gap-1.5 rounded-full border border-[var(--gold-border)]/60 bg-[var(--gold-dim)]/50 px-3 py-1 text-xs font-medium text-[var(--gold)]">
        {t("upload_limit")}
      </div>
    </motion.div>
  );
}
