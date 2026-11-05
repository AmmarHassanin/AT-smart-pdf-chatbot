// In production (Docker/Coolify) this is left empty so requests go to the
// same origin as the page, and Next.js's server-side rewrite (next.config.ts)
// proxies /api/* to the backend container over the internal Docker network.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getUserId(): string {
  if (typeof window === "undefined") return "";
  let id = localStorage.getItem("atpdf_user_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("atpdf_user_id", id);
  }
  return id;
}

function headers(json = true): HeadersInit {
  const h: Record<string, string> = { "X-User-Id": getUserId() };
  if (json) h["Content-Type"] = "application/json";
  return h;
}

export interface Source {
  source: string;
  page: number | string;
  snippet: string;
  ocr: boolean;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources: Source[];
}

export interface Chat {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
  file_digests: Record<string, string>;
  pages: number;
  index_warnings: { type: string; name?: string; count?: number }[];
}

export async function listChats(): Promise<Chat[]> {
  const res = await fetch(`${API_URL}/api/chats`, { headers: headers() });
  if (!res.ok) throw new Error("Failed to list chats");
  return res.json();
}

export async function createChat(): Promise<Chat> {
  const res = await fetch(`${API_URL}/api/chats`, { method: "POST", headers: headers() });
  if (!res.ok) throw new Error("Failed to create chat");
  return res.json();
}

export async function renameChat(id: string, title: string): Promise<Chat> {
  const res = await fetch(`${API_URL}/api/chats/${id}`, {
    method: "PATCH",
    headers: headers(),
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Failed to rename chat");
  return res.json();
}

export async function deleteChat(id: string): Promise<void> {
  await fetch(`${API_URL}/api/chats/${id}`, { method: "DELETE", headers: headers() });
}

export async function uploadFiles(chatId: string, files: File[]) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  const res = await fetch(`${API_URL}/api/chats/${chatId}/files`, {
    method: "POST",
    headers: headers(false),
    body: form,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json() as Promise<{ changed: boolean; warnings: unknown[]; pages: number }>;
}

export async function removeFile(chatId: string, filename: string) {
  await fetch(`${API_URL}/api/chats/${chatId}/files/${encodeURIComponent(filename)}`, {
    method: "DELETE",
    headers: headers(),
  });
}

export function fileUrl(chatId: string, filename: string): string {
  return `${API_URL}/api/chats/${chatId}/files/${encodeURIComponent(filename)}`;
}

export async function translateDoc(chatId: string, source: string, target: string, model: string) {
  const res = await fetch(`${API_URL}/api/chats/${chatId}/translate`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ source, target, model }),
  });
  if (!res.ok) throw new Error("Translate failed");
  return res.json() as Promise<{ text: string; engine: string }>;
}

export async function taskPrompt(task: string): Promise<string> {
  const res = await fetch(`${API_URL}/api/tasks/${task}`);
  if (!res.ok) return "";
  const data = await res.json();
  return data.prompt as string;
}

export async function askStream(
  chatId: string,
  question: string,
  model: string,
  k: number,
  onToken: (text: string) => void,
  onDone: (reply: string, sources: Source[]) => void,
  onError: (message: string) => void
) {
  const res = await fetch(`${API_URL}/api/chats/${chatId}/ask`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ question, model, k }),
  });
  if (!res.ok || !res.body) {
    onError("Request failed");
    return;
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";
    for (const raw of events) {
      const lines = raw.split("\n");
      let event = "message";
      let data = "";
      for (const line of lines) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (event === "token") onToken(data);
      else if (event === "error") onError(data);
      else if (event === "done") {
        try {
          const parsed = JSON.parse(data);
          onDone(parsed.reply || "", parsed.sources || []);
        } catch {
          onDone("", []);
        }
      }
    }
  }
}
