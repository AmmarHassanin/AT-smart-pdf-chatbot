"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type Lang = "en" | "ar";

const STRINGS: Record<Lang, Record<string, string>> = {
  en: {
    brand: "AT PDF",
    new_chat: "New chat",
    search_chats: "Search conversations…",
    recent: "Recent",
    settings: "Settings",
    free_plan: "Free Plan",
    welcome_title: "Your documents.",
    welcome_accent: "Your AI assistant.",
    welcome_sub: "Understand documents, translate content, and discover insights instantly.",
    feat_ask: "Ask PDF",
    feat_ask_desc: "Chat with your document using grounded answers.",
    feat_sum: "Summarize",
    feat_sum_desc: "Concise and detailed summaries from your PDF.",
    feat_tr: "Translate",
    feat_tr_desc: "Arabic ↔ English translation from extracted text.",
    feat_keys: "Key points",
    feat_keys_desc: "Important ideas as readable bullets.",
    feat_explain: "Explain simply",
    feat_explain_desc: "Beginner-friendly explanations of difficult passages.",
    upload_title: "Upload PDF",
    upload_hint: "Drag and drop or browse — multiple files supported",
    upload_limit: "PDF only · up to 200MB per file",
    chat_input: "Ask about your documents…",
    send: "Send",
    tab_chat: "Chat",
    tab_summary: "Summary",
    tab_translate: "Translate",
    tab_key_points: "Key points",
    tab_explain: "Explain",
    sources: "Sources",
    go_to_page: "Go to this page",
    thinking: "AT is thinking…",
    empty_chat_hint: "Ask a question about your document to start.",
    remove: "Remove",
    page_label: "Page",
    translate_source: "From",
    translate_target: "To",
    translate_auto: "Auto-detect",
    translate_ar: "Arabic",
    translate_en: "English",
    translate_run: "Translate",
    run_action: "Generate",
    need_pdf: "Upload a PDF first to use this feature.",
  },
  ar: {
    brand: "AT PDF",
    new_chat: "محادثة جديدة",
    search_chats: "ابحث في المحادثات…",
    recent: "الأخيرة",
    settings: "الإعدادات",
    free_plan: "الخطة المجانية",
    welcome_title: "مستنداتك.",
    welcome_accent: "مساعدك الذكي.",
    welcome_sub: "افهم مستنداتك، ترجم المحتوى، واستكشف الرؤى فورًا.",
    feat_ask: "اسأل PDF",
    feat_ask_desc: "محادثة مبنية على محتوى المستند.",
    feat_sum: "تلخيص",
    feat_sum_desc: "ملخص مختصر ومفصل من ملفك.",
    feat_tr: "ترجمة",
    feat_tr_desc: "ترجمة عربي ↔ إنجليزي من النص المستخرج.",
    feat_keys: "نقاط رئيسية",
    feat_keys_desc: "أفكار مهمة على شكل نقاط.",
    feat_explain: "شرح مبسّط",
    feat_explain_desc: "شرح للأجزاء الصعبة بلغة سهلة.",
    upload_title: "رفع PDF",
    upload_hint: "اسحب الملف أو اختر من جهازك — يدعم عدة ملفات",
    upload_limit: "PDF فقط · حتى 200 م.ب لكل ملف",
    chat_input: "اسأل عن مستنداتك…",
    send: "إرسال",
    tab_chat: "محادثة",
    tab_summary: "ملخص",
    tab_translate: "ترجمة",
    tab_key_points: "نقاط",
    tab_explain: "شرح",
    sources: "المصادر",
    go_to_page: "روح لهذه الصفحة",
    thinking: "AT يفكر…",
    empty_chat_hint: "اسأل عن مستندك عشان تبدأ.",
    remove: "إزالة",
    page_label: "صفحة",
    translate_source: "من",
    translate_target: "إلى",
    translate_auto: "اكتشاف تلقائي",
    translate_ar: "العربية",
    translate_en: "English",
    translate_run: "ترجم",
    run_action: "توليد",
    need_pdf: "ارفع PDF أولاً لاستخدام هذه الميزة.",
  },
};

interface I18nContextValue {
  lang: Lang;
  dir: "ltr" | "rtl";
  t: (key: string) => string;
  setLang: (lang: Lang) => void;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    const saved = localStorage.getItem("atpdf_lang") as Lang | null;
    if (saved === "ar" || saved === "en") setLangState(saved);
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  }, [lang]);

  const setLang = (next: Lang) => {
    setLangState(next);
    localStorage.setItem("atpdf_lang", next);
  };

  const t = (key: string) => STRINGS[lang][key] || STRINGS.en[key] || key;

  return (
    <I18nContext.Provider value={{ lang, dir: lang === "ar" ? "rtl" : "ltr", t, setLang }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
