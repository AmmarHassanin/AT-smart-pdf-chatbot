"use client";

import { Sidebar } from "@/components/Sidebar";
import { Hero } from "@/components/Hero";
import { UploadDropzone } from "@/components/UploadDropzone";
import { Workspace } from "@/components/Workspace";
import { useChats } from "@/lib/useChats";
import { useI18n } from "@/lib/i18n";
import * as api from "@/lib/api";

const MODEL = "accurate";

export default function Home() {
  const { t } = useI18n();
  const { chats, loading, activeChat, activeChatId, newChat, selectChat, rename, remove, uploadFiles, ask } =
    useChats();

  if (loading || !activeChat) {
    return (
      <div className="flex h-screen overflow-hidden">
        <div className="hidden w-[280px] shrink-0 flex-col gap-3 border-e border-[var(--border)] bg-[var(--sidebar)] p-4 md:flex">
          <div className="skeleton h-9 rounded-[var(--radius-sm)]" />
          <div className="skeleton h-10 rounded-full" />
          <div className="skeleton h-9 rounded-[var(--radius-sm)]" />
          <div className="mt-2 space-y-2">
            {[0, 1, 2].map((i) => (
              <div key={i} className="skeleton h-12 rounded-[var(--radius-md)]" style={{ animationDelay: `${i * 0.1}s` }} />
            ))}
          </div>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="h-12 w-12 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--gold)]" />
            <span className="text-sm text-[var(--muted)]">Loading…</span>
          </div>
        </div>
      </div>
    );
  }

  const hasFiles = Object.keys(activeChat.file_digests).length > 0;
  const primaryFile = Object.keys(activeChat.file_digests)[0];

  const runTask = async (task: string) => {
    const prompt = await api.taskPrompt(task);
    if (prompt) ask(prompt, MODEL, 4);
  };

  const handleTranslate = (source: string, target: string) => {
    if (!activeChatId) return Promise.resolve({ text: "", engine: "none" });
    return api.translateDoc(activeChatId, source, target, MODEL);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onNewChat={newChat}
        onSelect={selectChat}
        onRename={rename}
        onDelete={remove}
      />
      <main className="min-w-0 flex-1 overflow-y-auto p-4">
        {!hasFiles ? (
          <div className="mx-auto max-w-5xl">
            <Hero onFeatureClick={(task) => (task === "ask" ? null : runTask(task))} />
            <UploadDropzone onFiles={uploadFiles} />
          </div>
        ) : (
          <div className="h-full">
            <Workspace
              chat={activeChat}
              primaryFile={primaryFile}
              fileUrl={activeChatId ? api.fileUrl(activeChatId, primaryFile) : ""}
              onAsk={(q) => ask(q, MODEL, 4)}
              onRunTask={runTask}
              onTranslate={handleTranslate}
              model={MODEL}
            />
          </div>
        )}
      </main>
    </div>
  );
}
