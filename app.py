import streamlit as st
import google.generativeai as genai
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os
from dotenv import load_dotenv

# 🔹 Load API Key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-flash"  # ✅ Fastest Gemini Model

# ── Gemini Query Function (Streaming Enabled) ──
def query_gemini_text(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt, stream=True)
        result = ""
        for chunk in response:
            if chunk.text:
                result += chunk.text
        return result.strip()
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

# ── Extract Text from PDF ──
def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:5]:  # Limit to first 5 pages for speed
                text += page.extract_text() or ""
    except:
        # OCR for scanned PDFs
        images = convert_from_bytes(file_bytes)
        for img in images[:3]:
            text += pytesseract.image_to_string(img)
    return text[:4000]  # Limit size for faster response

# ── Streamlit Page Config ──
st.set_page_config(page_title="Mini Copilot", page_icon="🤖")
st.title("🤖 Mini Copilot – AI File & Code Assistant")

# ── Chat State ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# ── Sidebar Options ──
if st.sidebar.button("🆕 New Chat"):
    st.session_state.messages = []
    st.session_state.file_processed = False

# ── Display Previous Messages ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── File Upload ──
uploaded_file = st.file_uploader("Upload any file", type=None)
if uploaded_file and not st.session_state.file_processed:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name.lower()

    # Determine file type
    if file_name.endswith(".py") or file_name.endswith(".txt"):
        file_content = file_bytes.decode("utf-8", errors="ignore")[:4000]
        prompt = f"Explain this file:\n```\n{file_content}\n```"
    elif file_name.endswith(".pdf"):
        file_content = extract_text_from_pdf(file_bytes)
        prompt = f"Summarize this PDF content:\n{file_content}"
    else:  # Assume image or other file
        try:
            img = Image.open(io.BytesIO(file_bytes))
            prompt = "Describe this image in detail."
            # Send as multimodal input
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content([prompt, img])
            reply = response.text
        except:
            prompt = "This is a binary file. Explain its possible contents."
    
    if "reply" not in locals():  # Only call Gemini if not handled by image branch
        reply = query_gemini_text(prompt)

    st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded: {uploaded_file.name}"})
    with st.chat_message("user"):
        st.markdown(f"📄 Uploaded: {uploaded_file.name}")
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.file_processed = True

# ── User Chat Input ──
user_input = st.chat_input("Ask something about your file or code...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ✅ Show progressive response (No spinner delay)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("💭 Thinking...")
        reply = query_gemini_text(user_input)
        placeholder.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
