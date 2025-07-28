import streamlit as st
import google.generativeai as genai
import pdfplumber
import mimetypes
from PIL import Image
import io

# 🔹 Configure Gemini API
API_KEY = "AIzaSyAG9aiAXuZ7ULYe3KeaMLvKXVrGyj3ji5A"
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash"

# ── Query Gemini for Text ──
def query_gemini_text(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

# ── Query Gemini for Image ──
def query_gemini_image(image: Image.Image, prompt="Describe this image in detail.") -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"❌ Gemini Image Analysis Error: {e}"

# ── Extract Text from PDF ──
def extract_text_from_pdf(file_bytes):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        return ""
    return text

# ── Streamlit Setup ──
st.set_page_config(page_title="AI File Analyzer (Gemini)", page_icon="🤖")

st.sidebar.title("⚙️ Options")
if st.sidebar.button("🆕 New Chat"):
    st.session_state.clear()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# ── Display Previous Chat ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── File Upload ──
uploaded_file = st.file_uploader("Upload any file (Python, PDF, Image, Text)...", type=None)

if uploaded_file and not st.session_state.file_processed:
    file_type, _ = mimetypes.guess_type(uploaded_file.name)
    file_bytes = uploaded_file.read()

    # ✅ Handle Images
    if file_type and file_type.startswith("image"):
        with st.chat_message("user"):
            st.markdown(f"📷 **Uploaded Image:** {uploaded_file.name}")
            st.image(file_bytes)

        st.session_state.messages.append({"role": "user", "content": f"📷 Uploaded Image: {uploaded_file.name}"})
        image = Image.open(io.BytesIO(file_bytes))

        with st.spinner("💭 Analyzing image with Gemini..."):
            reply = query_gemini_image(image, "Describe and analyze this image.")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ✅ Handle PDFs
    elif file_type == "application/pdf":
        pdf_text = extract_text_from_pdf(file_bytes)
        if not pdf_text.strip():
            pdf_text = "❌ This PDF has no extractable text (might be scanned). OCR is required."
        
        with st.chat_message("user"):
            st.markdown(f"📄 **Uploaded PDF:** {uploaded_file.name}")
            if pdf_text.startswith("❌"):
                st.warning(pdf_text)
            else:
                st.code(pdf_text[:800] + "..." if len(pdf_text) > 800 else pdf_text)

        st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded PDF: {uploaded_file.name}"})

        if not pdf_text.startswith("❌"):
            with st.spinner("💭 Analyzing PDF with Gemini..."):
                reply = query_gemini_text(f"Explain this PDF content:\n{pdf_text[:4000]}")
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)

    # ✅ Handle Python/Text Files
    elif file_type and ("text" in file_type or uploaded_file.name.endswith((".py", ".txt", ".json", ".csv", ".md"))):
        text = file_bytes.decode("utf-8", errors="ignore")
        with st.chat_message("user"):
            st.markdown(f"📄 **Uploaded File:** {uploaded_file.name}")
            st.code(text[:800] + "..." if len(text) > 800 else text, language="python" if uploaded_file.name.endswith(".py") else None)
        st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded File: {uploaded_file.name}"})

        with st.spinner("💭 Analyzing file content with Gemini..."):
            reply = query_gemini_text(f"Explain this file content:\n{text[:4000]}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ❌ Unsupported Files
    else:
        with st.chat_message("assistant"):
            st.warning("❌ This file type is not supported yet. Try uploading Python, text, PDF, or image.")
        st.session_state.messages.append({"role": "assistant", "content": "❌ Unsupported file type."})

    st.session_state.file_processed = True

# ── Chat Input ──
user_input = st.chat_input("Ask something about your file or anything else...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("💭 Thinking..."):
        reply = query_gemini_text(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
