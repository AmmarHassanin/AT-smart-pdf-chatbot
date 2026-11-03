"use client";

import { useState } from "react";
import { MessageSquare, Pencil, Plus, Search, Settings, Trash2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import type { Chat } from "@/lib/api";

function timeLabel(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const sameDay = date.toDateString() === now.toDateString();
  const time = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (sameDay) return `Today, ${time}`;
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) return `Yesterday, ${time}`;
  return date.toLocaleDateString();
}

export function Sidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelect,
  onRename,
  onDelete,
}: {
  chats: Chat[];
  activeChatId: string | null;
  onNewChat: () => void;
  onSelect: (id: string) => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string) => void;
}) {
  const { t, lang, setLang } = useI18n();
  const [query, setQuery] = useState("");
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");

  const filtered = chats.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()));

  return (
    <aside className="flex h-full w-[280px] shrink-0 flex-col border-e border-[var(--border)] bg-[var(--sidebar)]">
      <div className="shrink-0 p-4">
        <div className="mb-4 flex items-center gap-2.5 border-b border-[var(--border)] pb-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-sm)] border border-[var(--gold-border)] bg-gradient-to-br from-[var(--gold-dim)] to-transparent">
            <MessageSquare size={18} className="text-[var(--gold)]" />
          </div>
          <span className="text-lg font-bold">
            AT <span className="text-[var(--gold)]">PDF</span>
          </span>
        </div>

        <button
          onClick={onNewChat}
          className="btn-gold mb-3 flex w-full items-center justify-center gap-2 rounded-full py-2.5 text-sm font-bold"
        >
          <Plus size={16} /> {t("new_chat")}
        </button>

        <div className="relative">
          <Search size={15} className="pointer-events-none absolute start-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("search_chats")}
            className="w-full rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--card)] py-2 ps-9 pe-3 text-sm outline-none transition-colors focus:border-[var(--gold-border)] focus:shadow-[0_0_0_3px_var(--gold-glow)]"
          />
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4">
        <div className="mb-2 text-xs font-semibold text-[var(--muted)]">{t("recent")}</div>
        <div className="flex flex-col gap-1 pb-4">
          {filtered.map((chat) => {
            const isActive = chat.id === activeChatId;
            return (
              <div
                key={chat.id}
                className={`group relative rounded-[var(--radius-md)] border transition-colors duration-200 ${
                  isActive
                    ? "border-[var(--gold-border)] bg-[var(--gold-dim)] shadow-[inset_0_0_0_1px_rgba(212,184,122,0.08)]"
                    : "border-transparent hover:bg-white/[0.04]"
                }`}
              >
                {renamingId === chat.id ? (
                  <div className="flex gap-1 p-2">
                    <input
                      autoFocus
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          onRename(chat.id, renameValue);
                          setRenamingId(null);
                        }
                      }}
                      className="w-full rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--card)] px-2 py-1 text-sm outline-none"
                    />
                  </div>
                ) : (
                  <button onClick={() => onSelect(chat.id)} className="flex w-full items-start gap-2.5 px-3 py-2.5 text-start">
                    <MessageSquare size={16} className={`mt-0.5 shrink-0 ${isActive ? "text-[var(--gold)]" : "text-[var(--muted)]"}`} />
                    <div className="min-w-0 flex-1">
                      <div className={`truncate text-sm font-semibold ${isActive ? "text-[var(--gold)]" : "text-[var(--text)]"}`}>
                        {chat.title}
                      </div>
                      <div className="text-xs text-[var(--muted)]">{timeLabel(chat.updated_at)}</div>
                    </div>
                  </button>
                )}
                <div className="absolute end-1.5 top-1.5 hidden gap-1 group-hover:flex">
                  <button
                    onClick={() => {
                      setRenamingId(chat.id);
                      setRenameValue(chat.title);
                    }}
                    className="rounded-md border border-[var(--border)] bg-[var(--elevated)] p-1.5 text-[var(--muted)] hover:border-[var(--gold-border)]"
                  >
                    <Pencil size={12} />
                  </button>
                  <button
                    onClick={() => onDelete(chat.id)}
                    className="btn-danger rounded-md bg-[var(--elevated)] p-1.5"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-auto shrink-0 border-t border-[var(--border)] p-4">
        <button className="mb-3 flex w-full items-center gap-2 rounded-[var(--radius-md)] border border-[var(--border)] px-3 py-2 text-sm">
          <Settings size={14} /> {t("settings")}
        </button>
        <div className="mb-3 flex gap-1 text-xs">
          <button
            onClick={() => setLang("en")}
            className={`rounded-full px-2.5 py-1 ${lang === "en" ? "border border-[var(--gold-border)] text-[var(--gold)]" : "text-[var(--muted)]"}`}
          >
            EN
          </button>
          <button
            onClick={() => setLang("ar")}
            className={`rounded-full px-2.5 py-1 ${lang === "ar" ? "border border-[var(--gold-border)] text-[var(--gold)]" : "text-[var(--muted)]"}`}
          >
            AR
          </button>
        </div>
        <div className="flex items-center gap-2.5 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--card)] p-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-full border border-[var(--gold-border)] bg-gradient-to-br from-[var(--gold-dim)] to-transparent text-sm font-bold text-[var(--gold)]">
            A
          </div>
          <div>
            <div className="text-sm font-semibold">Ammar</div>
            <div className="text-xs text-[var(--muted)]">{t("free_plan")}</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
