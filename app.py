import os
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="AT - Smart PDF Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تحميل المتغيرات البيئية
load_dotenv()

# 3. تصميم CSS احترافي (Cyberpunk / Neon Purple & 3D Styling)
custom_css = """
<style>
    /* الخلفية العامة باللون الأسود والبنفسجي العميق */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #2e1065 0%, #090514 60%, #030008 100%);
        color: #f3e8ff;
    }

    /* الشريط الجانبي بتأثير زجاجي بنفسجي */
    [data-testid="stSidebar"] {
        background: rgba(15, 7, 32, 0.7) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(168, 85, 247, 0.2);
    }

    /* العنوان الرئيسي بتأثير نيون بنفسجي متوهج */
    .main-title {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #c084fc, #a855f7, #e879f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        text-shadow: 0 0 35px rgba(168, 85, 247, 0.5);
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        color: #c084fc;
        font-size: 1.1rem;
        margin-bottom: 35px;
        letter-spacing: 0.5px;
    }

    /* بطاقة رفع الملفات ثلاثية الأبعاد بنيون بنفسجي */
    [data-testid="stFileUploader"] {
        background: rgba(88, 28, 135, 0.15);
        border: 2px dashed #a855f7;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(168, 85, 247, 0.15);
        transition: all 0.4s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #f0abfc;
        box-shadow: 0 0 25px rgba(232, 121, 249, 0.4);
        transform: translateY(-2px);
    }

    /* الفوتر الزجاجي */
    .footer-container {
        background: rgba(24, 9, 43, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(168, 85, 247, 0.25);
        border-radius: 20px;
        padding: 22px;
        text-align: center;
        margin-top: 50px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(168, 85, 247, 0.2);
    }

    .developer-name {
        background: linear-gradient(90deg, #f0abfc, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 20px;
    }

    /* عنصر 3D عائم في المنتصف */
    .3d-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
    }
    .3d-avatar {
        width: 120px;
        filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.8));
        animation: float 4s ease-in-out infinite;
    }

    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(3deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 4. الشريط الجانبي (Sidebar)
with st.sidebar:
    st.markdown('''
        <div style="text-align: center; margin-bottom: 15px;">
            <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Writing%20Hand.png" width="70" style="filter: drop-shadow(0 0 15px #a855f7);">
        </div>
    ''', unsafe_allow_html=True)
    st.title("🤖 AT Bot Info")
    st.markdown("""
    **AT - Smart PDF Chatbot**  
    An advanced AI workspace using **RAG Architecture** to query and extract insights from documents instantly.
    
    👨‍💻 **Developed by:**  
    <span class="developer-name">Ammar Yasser</span>
    
    ---
    ### 🛠️ Tech Stack:
    * **Python** 🐍
    * **Streamlit** (Purple UI)
    * **LangChain** Framework
    * **Groq API** (Llama-3 70B)
    * **FAISS** Vector DB
    * **HuggingFace** Embeddings
    """, unsafe_allow_html=True)

# 5. الواجهة الرئيسية مع مجسم 3D متحرك للروبوت AT
st.markdown('''
    <div class="3d-container">
        <img class="3d-avatar" src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Robot/Robot.png">
    </div>
''', unsafe_allow_html=True)

st.markdown('<div class="main-title">AT Smart PDF Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">تحدث مع مستنداتك واستخرج المعلومات بدقة الذكاء الاصطناعي مع الروبوت AT</div>', unsafe_allow_html=True)

# 6. قسم رفع الملفات
pdf = st.file_uploader("📂 قم برفع ملف الـ PDF هنا لفتح المحادثة مع AT", type="pdf")

if pdf is not None:
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)

    with st.spinner("⚡ جاري معالجة الملف بواسطة AT..."):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    
    st.success("✅ تم تحليل الملف بنجاح! يمكنك الآن طرح أي سؤال على الروبوت AT.")

    user_question = st.text_input("💬 اكتب سؤالك هنا لـ AT:")

    if user_question:
    with st.spinner("🤖 AT يفكر ويولد الإجابة..."):
        llm = ChatGroq(model="llama3-70b-8192", temperature=0)

        # إعداد الـ Prompt بشكل معزول وآمن تماماً
        system_prompt = (
            "أنت المساعد الذكي AT. أجب على السؤال بناءً على السياق الموفر فقط. "
            "إذا لم تجد الإجابة في النص، قل بكل بساطة: المعلومة غير متوفرة في الملف.\n\n"
            "السياق:\n{context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # بناء السلسلة والاستعلام
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)

        # الحصول على النتيجة
        response = retrieval_chain.invoke({"input": user_question})
        st.write(response["answer"])