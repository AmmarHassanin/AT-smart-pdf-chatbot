"use client";

import { useEffect, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import { ChevronLeft, ChevronRight, Download, Minus, Plus } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { getUserId } from "@/lib/api";

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.mjs`;

export function PdfViewer({ fileUrl, filename }: { fileUrl: string; filename: string }) {
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(1.1);
  const page = useAppStore((s) => s.pdfPage);
  const jumpToPage = useAppStore((s) => s.jumpToPage);

  useEffect(() => {
    jumpToPage(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileUrl]);

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-[var(--radius-md)] border border-[var(--border)]">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--border)] bg-[var(--elevated)] px-3 py-2">
        <span className="truncate text-sm font-semibold">{filename}</span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => jumpToPage(Math.max(1, page - 1))}
            className="rounded-md border border-[var(--border)] bg-[var(--card)] p-1.5 hover:border-[var(--gold-border)]"
          >
            <ChevronLeft size={14} />
          </button>
          <span className="w-16 text-center text-xs text-[var(--muted)]">
            {page} / {numPages || "?"}
          </span>
          <button
            onClick={() => jumpToPage(Math.min(numPages, page + 1))}
            className="rounded-md border border-[var(--border)] bg-[var(--card)] p-1.5 hover:border-[var(--gold-border)]"
          >
            <ChevronRight size={14} />
          </button>
          <span className="mx-1 h-4 w-px bg-[var(--border)]" />
          <button
            onClick={() => setScale((s) => Math.max(0.5, s - 0.1))}
            className="rounded-md border border-[var(--border)] bg-[var(--card)] p-1.5 hover:border-[var(--gold-border)]"
          >
            <Minus size={14} />
          </button>
          <span className="w-10 text-center text-xs text-[var(--muted)]">{Math.round(scale * 100)}%</span>
          <button
            onClick={() => setScale((s) => Math.min(2, s + 0.1))}
            className="rounded-md border border-[var(--border)] bg-[var(--card)] p-1.5 hover:border-[var(--gold-border)]"
          >
            <Plus size={14} />
          </button>
          <button
            onClick={async () => {
              const res = await fetch(fileUrl, { headers: { "X-User-Id": getUserId() } });
              const blob = await res.blob();
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = filename;
              a.click();
              URL.revokeObjectURL(url);
            }}
            className="rounded-md border border-[var(--border)] bg-[var(--card)] p-1.5 hover:border-[var(--gold-border)]"
          >
            <Download size={14} />
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-auto bg-[#0d0f12] p-3">
        <Document
          file={{ url: fileUrl, httpHeaders: { "X-User-Id": getUserId() } }}
          onLoadSuccess={({ numPages: n }) => setNumPages(n)}
          loading={<div className="p-6 text-center text-sm text-[var(--muted)]">Loading…</div>}
        >
          <Page pageNumber={page} scale={scale} renderAnnotationLayer renderTextLayer className="mx-auto shadow-lg" />
        </Document>
      </div>
    </div>
  );
}
