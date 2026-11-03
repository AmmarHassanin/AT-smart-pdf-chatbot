"use client";

import dynamic from "next/dynamic";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { ChatPanel } from "./ChatPanel";
import type { Chat, Source } from "@/lib/api";

const PdfViewer = dynamic(() => import("./PdfViewer").then((m) => m.PdfViewer), {
  ssr: false,
  loading: () => <div className="p-6 text-center text-sm text-[var(--muted)]">Loading viewer…</div>,
});

export function Workspace({
  chat,
  primaryFile,
  fileUrl,
  onAsk,
  onRunTask,
  onTranslate,
  model,
}: {
  chat: Chat;
  primaryFile: string;
  fileUrl: string;
  onAsk: (q: string) => void;
  onRunTask: (task: string) => void;
  onTranslate: (source: string, target: string) => Promise<{ text: string; engine: string }>;
  model: string;
}) {
  return (
    <PanelGroup direction="horizontal" className="h-full gap-2">
      <Panel defaultSize={58} minSize={30} className="glass shadow-premium rounded-[var(--radius-lg)] border border-[var(--border)] p-2">
        <PdfViewer fileUrl={fileUrl} filename={primaryFile} />
      </Panel>
      <PanelResizeHandle className="group relative mx-1 w-1 rounded-full bg-[var(--border)] transition-colors hover:bg-[var(--gold-border)] data-[resize-handle-active]:bg-[var(--gold)]">
        <span className="absolute left-1/2 top-1/2 h-10 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--elevated)] opacity-0 transition-opacity group-hover:opacity-100" />
      </PanelResizeHandle>
      <Panel defaultSize={42} minSize={25} className="glass shadow-premium flex min-h-[32rem] flex-col rounded-[var(--radius-lg)] border border-[var(--border)] p-3">
        <ChatPanel
          messages={chat.messages}
          hasFiles={Object.keys(chat.file_digests).length > 0}
          onAsk={onAsk}
          onRunTask={onRunTask}
          onTranslate={onTranslate}
          model={model}
        />
      </Panel>
    </PanelGroup>
  );
}

export type { Source };
