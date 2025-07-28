import streamlit as st
import google.generativeai as genai
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os
from dotenv import load_dotenv

# 🔹 Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-flash"  # ✅ Fastest model


# ── Gemini Query ──
def query_gemini_text(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini API Error: {e}"


# ── PDF Text Extraction ──
def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:5]:
                text += page.extract_text() or ""
    except:
        try:
            images = convert_from_bytes(file_bytes)
            for img in images[:3]:
                text += pytesseract.image_to_string(img)
        except:
            text = "⚠️ Could not extract text from PDF."
    return text[:4000] or "⚠️ No readable text found in PDF."


# ── Streamlit Config ──
st.set_page_config(page_title="Mini Copilot", page_icon="🤖")
st.title("🤖 Mini Copilot – AI File & Code Assistant")

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# Sidebar
if st.sidebar.button("🆕 New Chat"):
    st.session_state.messages.clear()
    st.session_state.file_processed = False

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── File Upload Handling ──
uploaded_file = st.file_uploader("Upload any file", type=None)
if uploaded_file and not st.session_state.file_processed:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name.lower()
    reply = ""

    # ✅ Handle Python/Text Files
    if file_name.endswith((".py", ".txt")):
        try:
            file_content = file_bytes.decode("utf-8", errors="ignore")[:4000]
            prompt = f"Explain this Python code:\n```python\n{file_content}\n```"
            reply = query_gemini_text(prompt)
        except Exception as e:
            reply = f"❌ Could not read this file: {e}"

    # ✅ Handle PDF Files
    elif file_name.endswith(".pdf"):
        pdf_text = extract_text_from_pdf(file_bytes)
        prompt = f"Summarize and explain this PDF:\n{pdf_text}"
        reply = query_gemini_text(prompt)

    # ✅ Handle Images (JPG/PNG)
    else:
        try:
            img = Image.open(io.BytesIO(file_bytes))
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(["Describe this image in detail.", img])
            reply = response.text.strip()
        except:
            reply = query_gemini_text("This is a binary file. Explain its possible contents.")

    # Display Uploaded File Info
    st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded: {uploaded_file.name}"})
    with st.chat_message("user"):
        st.markdown(f"📄 Uploaded: {uploaded_file.name}")

    # Show AI Reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # Mark file as processed
    st.session_state.file_processed = True


# ── User Prompt Handling ──
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
