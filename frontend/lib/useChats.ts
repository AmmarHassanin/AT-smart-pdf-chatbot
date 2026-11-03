"use client";

import { useCallback, useEffect, useState } from "react";
import * as api from "./api";
import { useAppStore } from "./store";

export function useChats() {
  const [chats, setChats] = useState<api.Chat[]>([]);
  const [loading, setLoading] = useState(true);
  const activeChatId = useAppStore((s) => s.activeChatId);
  const setActiveChatId = useAppStore((s) => s.setActiveChatId);

  const refresh = useCallback(async () => {
    const list = await api.listChats();
    setChats(list);
    return list;
  }, []);

  useEffect(() => {
    (async () => {
      setLoading(true);
      const list = await refresh();
      if (list.length > 0) {
        setActiveChatId(list[0].id);
      } else {
        const chat = await api.createChat();
        setChats([chat]);
        setActiveChatId(chat.id);
      }
      setLoading(false);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeChat = chats.find((c) => c.id === activeChatId) || null;

  const newChat = useCallback(async () => {
    const chat = await api.createChat();
    setChats((prev) => [chat, ...prev]);
    setActiveChatId(chat.id);
  }, [setActiveChatId]);

  const selectChat = useCallback(
    (id: string) => {
      setActiveChatId(id);
    },
    [setActiveChatId]
  );

  const rename = useCallback(async (id: string, title: string) => {
    const updated = await api.renameChat(id, title);
    setChats((prev) => prev.map((c) => (c.id === id ? updated : c)));
  }, []);

  const remove = useCallback(
    async (id: string) => {
      await api.deleteChat(id);
      const list = await refresh();
      if (activeChatId === id) {
        if (list.length > 0) setActiveChatId(list[0].id);
        else {
          const chat = await api.createChat();
          setChats([chat]);
          setActiveChatId(chat.id);
        }
      }
    },
    [activeChatId, refresh, setActiveChatId]
  );

  const patchActiveChat = useCallback(
    (patch: Partial<api.Chat>) => {
      setChats((prev) => prev.map((c) => (c.id === activeChatId ? { ...c, ...patch } : c)));
    },
    [activeChatId]
  );

  const appendMessage = useCallback(
    (message: api.ChatMessage) => {
      setChats((prev) =>
        prev.map((c) => (c.id === activeChatId ? { ...c, messages: [...c.messages, message] } : c))
      );
    },
    [activeChatId]
  );

  const updateLastMessage = useCallback(
    (content: string) => {
      setChats((prev) =>
        prev.map((c) => {
          if (c.id !== activeChatId) return c;
          const messages = [...c.messages];
          const last = messages[messages.length - 1];
          if (last && last.role === "assistant") {
            messages[messages.length - 1] = { ...last, content };
          }
          return { ...c, messages };
        })
      );
    },
    [activeChatId]
  );

  const setLastMessageSources = useCallback(
    (sources: api.Source[]) => {
      setChats((prev) =>
        prev.map((c) => {
          if (c.id !== activeChatId) return c;
          const messages = [...c.messages];
          const last = messages[messages.length - 1];
          if (last && last.role === "assistant") {
            messages[messages.length - 1] = { ...last, sources };
          }
          return { ...c, messages };
        })
      );
    },
    [activeChatId]
  );

  const uploadFiles = useCallback(
    async (files: File[]) => {
      if (!activeChatId) return;
      const result = await api.uploadFiles(activeChatId, files);
      const updated = await api.listChats();
      setChats(updated);
      return result;
    },
    [activeChatId]
  );

  const removeFile = useCallback(
    async (filename: string) => {
      if (!activeChatId) return;
      await api.removeFile(activeChatId, filename);
      const updated = await api.listChats();
      setChats(updated);
    },
    [activeChatId]
  );

  const ask = useCallback(
    async (question: string, model: string, k: number) => {
      if (!activeChatId) return;
      appendMessage({ role: "user", content: question, sources: [] });
      appendMessage({ role: "assistant", content: "", sources: [] });
      let acc = "";
      await api.askStream(
        activeChatId,
        question,
        model,
        k,
        (token) => {
          acc += token;
          updateLastMessage(acc);
        },
        (reply, sources) => {
          updateLastMessage(reply || acc);
          setLastMessageSources(sources);
        },
        (message) => {
          updateLastMessage(`⚠ ${message}`);
        }
      );
    },
    [activeChatId, appendMessage, updateLastMessage, setLastMessageSources]
  );

  return {
    chats,
    loading,
    activeChat,
    activeChatId,
    newChat,
    selectChat,
    rename,
    remove,
    uploadFiles,
    removeFile,
    ask,
    patchActiveChat,
  };
}
