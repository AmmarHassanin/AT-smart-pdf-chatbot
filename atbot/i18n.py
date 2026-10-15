"""UI language (English / Arabic) and layout direction."""

from __future__ import annotations

import html
import json

import streamlit as st

LANG_KEY = "ui_lang"
THEME_KEY = "ui_theme"

_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "brand": "AT PDF",
        "new_chat": "New chat",
        "conversations": "Recent",
        "search_chats": "Search conversations…",
        "new_conversation": "New chat",
        "delete_chat_help": "Delete chat",
        "rename_chat_help": "Rename",
        "confirm_delete_title": "Delete this chat?",
        "confirm_delete_body": "This removes the conversation and its uploaded files from this session.",
        "confirm_yes": "Delete",
        "confirm_no": "Cancel",
        "rename_prompt": "Chat title",
        "save_rename": "Save",
        "settings": "Settings",
        "model": "Model",
        "chunks": "Retrieved chunks",
        "theme_label": "Theme",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "language_label": "Language",
        "upload_title": "Upload PDF",
        "upload_hint": "Drag and drop or browse — multiple files supported",
        "upload_limit": "PDF only · up to {mb}MB per file",
        "remove_file": "Remove",
        "replace_file": "Replace",
        "clear_all": "Clear chat & files",
        "welcome_title": "Your documents. Your AI assistant.",
        "welcome_sub": "Understand documents, translate content, and discover insights instantly.",
        "feat_ask": "Ask PDF",
        "feat_ask_desc": "Chat with your document using grounded answers.",
        "feat_sum": "Summarize",
        "feat_sum_desc": "Concise and detailed summaries from your PDF.",
        "feat_tr": "Translate",
        "feat_tr_desc": "Arabic ↔ English translation from extracted text.",
        "feat_keys": "Key points",
        "feat_keys_desc": "Important ideas as readable bullets.",
        "feat_explain": "Explain simply",
        "feat_explain_desc": "Beginner-friendly explanations of difficult passages.",
        "hub_hint": "Upload a PDF to unlock document tools and chat.",
        "need_pdf": "Upload a PDF first to use this feature.",
        "processing": "Processing document…",
        "doc_ready": "Indexed",
        "doc_pages": "{pages} pages · {files} file(s)",
        "doc_no_index": "Waiting for text extraction…",
        "workspace_title": "Document workspace",
        "workspace_sub": "Preview your PDF, run tools, and chat with context.",
        "pdf_page": "Page",
        "pdf_zoom": "Zoom",
        "prompts_label": "Quick actions",
        "chat_title": "Chat",
        "chat_sub": "Answers use your uploaded PDFs only.",
        "copy": "Copy",
        "copied": "Copied",
        "retry": "Retry",
        "chat_input": "Ask about your documents…",
        "chat_input_hint": "Enter to send · attach PDFs with the clip icon",
        "groq_missing": "Add GROQ_API_KEY to your .env file and restart the app.",
        "robot_missing": "Brand asset missing at assets/Layer 1.png",
        "model_accurate": "Accurate — GPT-OSS 120B",
        "model_fast": "Fast — GPT-OSS 20B",
        "sources": "Sources",
        "translate_panel_title": "Translate document",
        "translate_source": "From",
        "translate_target": "To",
        "translate_auto": "Auto-detect",
        "translate_ar": "Arabic",
        "translate_en": "English",
        "translate_run": "Translate",
        "translate_empty": "No extractable text in this PDF.",
        "translate_result": "Translation",
        "file_too_large": "{name} exceeds the {mb}MB limit.",
        "prompt_summary": "Provide a concise summary and a short detailed summary of this document using only the PDF context.",
        "prompt_ask": "What are the most important things I should know from this document?",
        "prompt_key_points": "Extract the key points as clear bullet lists grouped by topic. Use only the document.",
        "prompt_explain": "Explain the most difficult parts of this document in simple language for a beginner.",
        "prompt_translate_chat": "List important passages from the document and give their meaning (stay within document facts only).",
        "no_index": "Upload a PDF with selectable text first.",
        "typing": "AT is thinking…",
        "tab_chat": "Chat",
        "tab_summary": "Summary",
        "tab_translate": "Translate",
        "tab_key_points": "Key points",
        "tab_explain": "Explain",
        "panel_assistant": "AI Assistant",
        "empty_chat": "Ask a question about your document to start.",
        "btn_edit": "Edit",
        "btn_delete": "Del",
        "run_action": "Generate",
        "fullscreen": "Fullscreen",
        "page_label": "Page",
        "error_answer": "Something went wrong while generating the reply: {error}",
        "empty_answer": "No response was returned. Please try again.",
        "long_message": "Long message",
        "send": "Send",
        "encrypted_pdf": "{name} is password-protected and could not be opened.",
        "corrupt_pdf": "Could not open {name}. Try an unencrypted copy.",
        "no_text_pdf": "{name} has no extractable text (likely scanned images only).",
        "free_plan": "Free Plan",
    },
    "ar": {
        "brand": "AT PDF",
        "new_chat": "محادثة جديدة",
        "conversations": "الأخيرة",
        "search_chats": "ابحث في المحادثات…",
        "new_conversation": "محادثة جديدة",
        "delete_chat_help": "حذف",
        "rename_chat_help": "إعادة تسمية",
        "confirm_delete_title": "حذف هذه المحادثة؟",
        "confirm_delete_body": "سيتم حذف المحادثة والملفات المرتبطة بها من هذه الجلسة.",
        "confirm_yes": "حذف",
        "confirm_no": "إلغاء",
        "rename_prompt": "عنوان المحادثة",
        "save_rename": "حفظ",
        "settings": "الإعدادات",
        "model": "النموذج",
        "chunks": "مقاطع الاسترجاع",
        "theme_label": "السمة",
        "theme_dark": "داكن",
        "theme_light": "فاتح",
        "language_label": "اللغة",
        "upload_title": "رفع PDF",
        "upload_hint": "اسحب الملف أو اختر من جهازك — يدعم عدة ملفات",
        "upload_limit": "PDF فقط · حتى {mb} م.ب لكل ملف",
        "remove_file": "إزالة",
        "replace_file": "استبدال",
        "clear_all": "مسح المحادثة والملفات",
        "welcome_title": "مستنداتك. مساعدك الذكي.",
        "welcome_sub": "افهم المستندات، ترجم المحتوى، واستخرج الم insights فوراً.",
        "feat_ask": "اسأل PDF",
        "feat_ask_desc": "محادثة مبنية على محتوى المستند.",
        "feat_sum": "تلخيص",
        "feat_sum_desc": "ملخص مختصر ومفصل من ملفك.",
        "feat_tr": "ترجمة",
        "feat_tr_desc": "ترجمة عربي ↔ إنجليزي من النص المستخرج.",
        "feat_keys": "نقاط رئيسية",
        "feat_keys_desc": "أفكار مهمة على شكل نقاط.",
        "feat_explain": "شرح مبسّط",
        "feat_explain_desc": "شرح للأجزاء الصعبة بلغة سهلة.",
        "hub_hint": "ارفع PDF لتفعيل أدوات المستند والمحادثة.",
        "need_pdf": "ارفع PDF أولاً لاستخدام هذه الميزة.",
        "processing": "جاري معالجة المستند…",
        "doc_ready": "جاهز",
        "doc_pages": "{pages} صفحة · {files} ملف",
        "doc_no_index": "بانتظار استخراج النص…",
        "workspace_title": "مساحة المستند",
        "workspace_sub": "معاينة PDF، أدوات، ومحادثة بالسياق.",
        "pdf_page": "صفحة",
        "pdf_zoom": "تكبير",
        "prompts_label": "إجراءات سريعة",
        "chat_title": "المحادثة",
        "chat_sub": "الإجابات من ملفاتك فقط.",
        "copy": "نسخ",
        "copied": "تم النسخ",
        "retry": "إعادة",
        "chat_input": "اسأل عن مستنداتك…",
        "chat_input_hint": "Enter للإرسال · مرفق PDF من أيقونة المشبك",
        "groq_missing": "أضف GROQ_API_KEY في ملف .env ثم أعد التشغيل.",
        "robot_missing": "ملف الهوية غير موجود في assets/Layer 1.png",
        "model_accurate": "دقيق — GPT-OSS 120B",
        "model_fast": "سريع — GPT-OSS 20B",
        "sources": "المصادر",
        "translate_panel_title": "ترجمة المستند",
        "translate_source": "من",
        "translate_target": "إلى",
        "translate_auto": "اكتشاف تلقائي",
        "translate_ar": "العربية",
        "translate_en": "English",
        "translate_run": "ترجم",
        "translate_empty": "لا يوجد نص قابل للاستخراج.",
        "translate_result": "الترجمة",
        "file_too_large": "{name} يتجاوز حد {mb} م.ب.",
        "prompt_summary": "قدّم ملخصاً مختصراً وملخصاً مفصلاً قصيراً للمستند اعتماداً على سياق PDF فقط.",
        "prompt_ask": "ما أهم ما يجب أن أعرفه من هذا المستند؟",
        "prompt_key_points": "استخرج النقاط الرئيسية كقوائم نقطية واضحة حسب الموضوع. من المستند فقط.",
        "prompt_explain": "اشرح أصعب أجزاء المستند بلغة بسيطة لمبتدئ.",
        "prompt_translate_chat": "اذكر مقاطع مهمة من المستند ومعناها (بدون خروج عن المستند).",
        "no_index": "ارفع PDF يحتوي نصاً قابلاً للتحديد أولاً.",
        "typing": "AT يفكر…",
        "tab_chat": "محادثة",
        "tab_summary": "ملخص",
        "tab_translate": "ترجمة",
        "tab_key_points": "نقاط",
        "tab_explain": "شرح",
        "panel_assistant": "المساعد",
        "empty_chat": "اسأل عن المستند لتبدأ المحادثة.",
        "btn_edit": "تعديل",
        "btn_delete": "حذف",
        "run_action": "توليد",
        "fullscreen": "ملء الشاشة",
        "page_label": "صفحة",
        "error_answer": "حدث خطأ أثناء توليد الرد: {error}",
        "empty_answer": "لم يصل رد. جرّب مرة أخرى.",
        "long_message": "رسالة طويلة",
        "send": "إرسال",
        "encrypted_pdf": "{name} محمي بكلمة مرور ولم يُفتح.",
        "corrupt_pdf": "تعذّر فتح {name}. جرّب نسخة غير مشفرة.",
        "no_text_pdf": "{name} لا يحتوي نصاً قابلاً للاستخراج (غالباً صور).",
        "free_plan": "الخطة المجانية",
    },
}

_STRINGS["ar"]["welcome_sub"] = "افهم مستنداتك، ترجم المحتوى، واستكشف الرؤى فوراً."
_STRINGS["ar"]["feat_explain_desc"] = "شرح للأجزاء الصعبة بلغة سهلة."


def get_lang() -> str:
    lang = st.session_state.get(LANG_KEY, "en")
    return lang if lang in _STRINGS else "en"


def get_theme() -> str:
    theme = st.session_state.get(THEME_KEY, "dark")
    return theme if theme in ("dark", "light") else "dark"


def set_lang(lang: str) -> None:
    if lang in _STRINGS:
        st.session_state[LANG_KEY] = lang


def set_theme(theme: str) -> None:
    if theme in ("dark", "light"):
        st.session_state[THEME_KEY] = theme


def t(key: str, **kwargs: object) -> str:
    bucket = _STRINGS.get(get_lang(), _STRINGS["en"])
    text = bucket.get(key, _STRINGS["en"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text


def suggestions_for_lang() -> list[str]:
    return [
        t("prompt_summary"),
        t("prompt_key_points"),
        t("prompt_explain"),
        t("prompt_ask"),
    ]


def model_display(model_key: str) -> str:
    from atbot.constants import MODELS

    keys = list(MODELS.keys())
    if model_key not in keys:
        return model_key
    idx = keys.index(model_key)
    return t("model_accurate") if idx == 0 else t("model_fast")


def inject_layout() -> None:
    lang = get_lang()
    theme = get_theme()
    direction = "rtl" if lang == "ar" else "ltr"
    st.markdown(
        f"""
<script>
document.documentElement.setAttribute("data-theme", {json.dumps(theme)});
document.documentElement.setAttribute("dir", {json.dumps(direction)});
document.documentElement.setAttribute("lang", {json.dumps(lang)});
</script>
""",
        unsafe_allow_html=True,
    )


def render_lang_switch_navbar() -> None:
    lang = get_lang()
    with st.container(key="lang_nav_toggle"):
        choice = st.segmented_control(
            t("language_label"),
            options=["en", "ar"],
            default=lang,
            format_func=lambda x: t("translate_en") if x == "en" else t("translate_ar"),
            key="lang_select_navbar",
            label_visibility="collapsed",
        )
    if choice and choice != lang:
        set_lang(choice)
        _persist_prefs()
        st.rerun()


def _persist_prefs() -> None:
    try:
        from atbot.persistence import persist_user_state

        persist_user_state()
    except Exception:
        pass
