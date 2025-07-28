import streamlit as st
import google.generativeai as genai
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os
from dotenv import load_dotenv

# 🔹 Load Gemini API Key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-flash"

# ── Gemini Query (Text) ──
def query_gemini_text(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([prompt])
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

# ── Gemini Query (Image) ──
def query_gemini_image(pil_image: Image.Image) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([ "Describe this image in detail.", pil_image ])
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini Vision Error: {e}"

# ── Extract Text from PDF ──
def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:5]:
                text += page.extract_text() or ""
        if text.strip():
            return text[:4000]
    except:
        pass
    # OCR fallback
    try:
        images = convert_from_bytes(file_bytes)
        extracted = ""
        for img in images[:3]:
            extracted += pytesseract.image_to_string(img)
        return extracted[:4000] if extracted.strip() else "⚠️ No readable text found."
    except:
        return "⚠️ Could not extract text from this PDF."

# ── Detect Language ──
def detect_language(filename: str) -> str:
    ext = filename.split(".")[-1]
    return {
        "py": "python",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "html": "html",
        "css": "css",
        "js": "javascript"
    }.get(ext, "")

# ── Streamlit App ──
st.set_page_config(page_title="Mini Copilot", page_icon="🤖")
st.title("🤖 Mini Copilot – AI File & Code Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔹 New Chat Button
if st.sidebar.button("🆕 New Chat"):
    st.session_state.messages.clear()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── File Upload (Dynamic Key to allow re-upload) ──
uploaded_file = st.file_uploader("📂 Upload any file", type=None, key=str(len(st.session_state.messages)))

if uploaded_file:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name.lower()
    reply = ""

    # Log user action
    st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded: {uploaded_file.name}"})
    with st.chat_message("user"):
        st.markdown(f"📄 Uploaded: **{uploaded_file.name}**")

    # ✅ Handle Code Files
    if file_name.endswith((".py", ".java", ".c", ".cpp", ".html", ".css", ".js")):
        content = file_bytes.decode("utf-8", errors="ignore")[:4000]
        lang = detect_language(file_name)
        st.code(content, language=lang)
        reply = query_gemini_text(f"Explain this {lang} code:\n```{lang}\n{content}\n```")

    # ✅ Handle PDF
    elif file_name.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_bytes)
        st.text_area("📄 Extracted PDF Text", extracted_text, height=200)
        reply = query_gemini_text(f"Summarize and explain this PDF content:\n{extracted_text}")

    # ✅ Handle Images
    elif file_name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        img = Image.open(io.BytesIO(file_bytes))
        st.image(img, caption="📸 Uploaded Image", use_column_width=True)
        reply = query_gemini_image(img)

    # ✅ Handle Other Files
    else:
        preview = file_bytes[:2000].decode("utf-8", errors="ignore")
        st.text_area("📄 Raw File Preview", preview, height=200)
        reply = query_gemini_text(f"Analyze and explain this file content:\n{preview}")

    # Show AI response
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# ── User Chat Input ──
user_input = st.chat_input("Ask something about your file or code...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("💭 Thinking...")
        reply = query_gemini_text(user_input)
        placeholder.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
