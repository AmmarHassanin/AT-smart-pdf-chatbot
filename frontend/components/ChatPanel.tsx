"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowUp, ChevronDown, MessageCircle, ScanText } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { useAppStore, type AiMode } from "@/lib/store";
import * as api from "@/lib/api";
import { Markdown } from "./Markdown";

const MODES: { key: AiMode; label: string }[] = [
  { key: "chat", label: "tab_chat" },
  { key: "summary", label: "tab_summary" },
  { key: "translate", label: "tab_translate" },
  { key: "key_points", label: "tab_key_points" },
  { key: "explain", label: "tab_explain" },
];

function SourceList({ sources }: { sources: api.Source[] }) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const jumpToPage = useAppStore((s) => s.jumpToPage);
  if (!sources.length) return null;

  return (
    <div className="mt-2 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--elevated)]">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-3 py-2 text-xs font-semibold text-[var(--muted)]"
      >
        <span>
          {t("sources")} · {sources.length}
        </span>
        <ChevronDown size={14} className={`transition ${open ? "rotate-180" : ""}`} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0 }} animate={{ height: "auto" }} exit={{ height: 0 }} className="overflow-hidden">
            <div className="space-y-1 px-3 pb-2">
              {sources.map((s, i) => (
                <div key={i} className="flex items-start justify-between gap-2 border-t border-[var(--border)] py-2 text-xs first:border-t-0">
                  <div>
                    <b>{s.source}</b> · {t("page_label")} {s.page}
                    {s.ocr && (
                      <span className="ms-1.5 rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-1.5 py-0.5 text-[10px] font-bold text-[var(--gold)]">
                        OCR
                      </span>
                    )}
                    <div className="mt-0.5 text-[var(--muted)]">{s.snippet}</div>
                  </div>
                  {typeof s.page === "number" && (
                    <button
                      onClick={() => jumpToPage(s.page as number)}
                      title={t("go_to_page")}
                      className="shrink-0 rounded-md border border-[var(--border)] bg-[var(--card)] p-1 text-[var(--gold)] hover:border-[var(--gold-border)]"
                    >
                      <ScanText size={13} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function ChatPanel({
  messages,
  hasFiles,
  onAsk,
  onRunTask,
  onTranslate,
}: {
  messages: api.ChatMessage[];
  hasFiles: boolean;
  onAsk: (question: string) => void;
  onRunTask: (task: string) => void;
  onTranslate: (source: string, target: string) => Promise<{ text: string; engine: string }>;
  model: string;
}) {
  const { t } = useI18n();
  const mode = useAppStore((s) => s.aiMode);
  const setMode = useAppStore((s) => s.setAiMode);
  const [draft, setDraft] = useState("");
  const [translateResult, setTranslateResult] = useState<string | null>(null);
  const [translating, setTranslating] = useState(false);
  const [src, setSrc] = useState("auto");
  const [tgt, setTgt] = useState("en");

  const send = () => {
    const text = draft.trim();
    if (!text) return;
    onAsk(text);
    setDraft("");
  };

  return (
    <div className="flex h-full flex-col">
      <div className="mb-3 flex items-center gap-2.5 border-b border-[var(--border)] pb-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-[10px] border border-[var(--gold-border)] bg-gradient-to-br from-[var(--gold-dim)] to-transparent text-xs font-bold text-[var(--gold)]">
          AT
        </div>
        <div>
          <div className="text-sm font-semibold">AI Assistant</div>
          <div className="text-xs text-[var(--muted)]">Answers use your uploaded PDFs only.</div>
        </div>
      </div>

      <div className="relative mb-3 flex gap-1 overflow-x-auto rounded-full border border-[var(--border)] bg-[var(--card)] p-1">
        {MODES.map((m) => (
          <button
            key={m.key}
            onClick={() => setMode(m.key)}
            className={`relative shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors duration-200 ${
              mode === m.key ? "text-[var(--gold)]" : "text-[var(--muted)] hover:text-[var(--text)]"
            }`}
          >
            {mode === m.key && (
              <motion.div
                layoutId="mode-pill"
                className="absolute inset-0 rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)]"
                transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
              />
            )}
            <span className="relative">{t(m.label)}</span>
          </button>
        ))}
      </div>

      {mode === "chat" && (
        <>
          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto pe-1">
            {messages.length === 0 && (
              <div className="flex h-full flex-col items-center justify-center gap-2 py-10 text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--elevated)] text-[var(--gold)]">
                  <MessageCircle size={18} />
                </div>
                <p className="max-w-[220px] text-sm text-[var(--muted)]">{t("empty_chat_hint")}</p>
              </div>
            )}
            {messages.map((m, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.25 }}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[88%] rounded-[var(--radius-lg)] px-3.5 py-2.5 text-sm shadow-premium ${
                    m.role === "user"
                      ? "rounded-ee-sm border border-[var(--gold-border)]/60 bg-gradient-to-br from-[var(--gold-dim)] to-[var(--elevated)]"
                      : "border border-[var(--border)] bg-[var(--card)]"
                  }`}
                >
                  {m.content ? (
                    m.role === "assistant" ? (
                      <Markdown>{m.content}</Markdown>
                    ) : (
                      <div className="whitespace-pre-wrap">{m.content}</div>
                    )
                  ) : (
                    <span className="inline-flex gap-1 py-0.5">
                      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--gold)] [animation-delay:-0.3s]" />
                      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--gold)] [animation-delay:-0.15s]" />
                      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--gold)]" />
                    </span>
                  )}
                  {m.role === "assistant" && <SourceList sources={m.sources} />}
                </div>
              </motion.div>
            ))}
          </div>
          <div className="mt-3 rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] p-2 transition-shadow focus-within:border-[var(--gold-border)] focus-within:shadow-[0_0_0_3px_var(--gold-glow)]">
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              placeholder={t("chat_input")}
              rows={2}
              className="w-full resize-none bg-transparent px-1 text-sm outline-none"
            />
            <div className="flex justify-end">
              <button
                onClick={send}
                className="btn-gold mt-1 flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-bold"
              >
                {t("send")} <ArrowUp size={13} />
              </button>
            </div>
          </div>
        </>
      )}

      {(mode === "summary" || mode === "key_points" || mode === "explain") && (
        <div className="flex-1">
          {!hasFiles ? (
            <p className="text-sm text-[var(--muted)]">{t("need_pdf")}</p>
          ) : (
            <button
              onClick={() => onRunTask(mode)}
              className="btn-gold rounded-full px-4 py-2 text-sm font-bold"
            >
              {t("run_action")}
            </button>
          )}
        </div>
      )}

      {mode === "translate" && (
        <div className="flex-1 space-y-3">
          {!hasFiles ? (
            <p className="text-sm text-[var(--muted)]">{t("need_pdf")}</p>
          ) : (
            <>
              <div className="flex gap-2">
                <select value={src} onChange={(e) => setSrc(e.target.value)} className="flex-1 rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--elevated)] p-2 text-sm">
                  <option value="auto">{t("translate_auto")}</option>
                  <option value="ar">{t("translate_ar")}</option>
                  <option value="en">{t("translate_en")}</option>
                </select>
                <select value={tgt} onChange={(e) => setTgt(e.target.value)} className="flex-1 rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--elevated)] p-2 text-sm">
                  <option value="ar">{t("translate_ar")}</option>
                  <option value="en">{t("translate_en")}</option>
                </select>
              </div>
              <button
                disabled={translating}
                onClick={async () => {
                  setTranslating(true);
                  const res = await onTranslate(src, tgt);
                  setTranslateResult(res.text);
                  setTranslating(false);
                }}
                className="btn-gold w-full rounded-full py-2 text-sm font-bold disabled:opacity-50"
              >
                {translating ? "…" : t("translate_run")}
              </button>
              {translateResult && (
                <div className="rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--card)] p-3">
                  <Markdown>{translateResult}</Markdown>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
