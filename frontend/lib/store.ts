import { create } from "zustand";

export type AiMode = "chat" | "summary" | "translate" | "key_points" | "explain";

interface AppState {
  activeChatId: string | null;
  setActiveChatId: (id: string | null) => void;
  aiMode: AiMode;
  setAiMode: (mode: AiMode) => void;
  pdfPage: number;
  jumpToPage: (page: number) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeChatId: null,
  setActiveChatId: (id) => set({ activeChatId: id, aiMode: "chat" }),
  aiMode: "chat",
  setAiMode: (mode) => set({ aiMode: mode }),
  pdfPage: 1,
  jumpToPage: (page) => set({ pdfPage: page }),
}));
