import streamlit as st
import google.generativeai as genai
import pdfplumber
import mimetypes
from PIL import Image
import io

# 🔹 Configure Gemini API
API_KEY = "your_gemini_api_key_here"
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash"

# ── Gemini Query Functions ──
def query_gemini_text(prompt: str) -> str:
    """Send plain text to Gemini."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

def query_gemini_image(image_bytes, prompt="Describe this image.") -> str:
    """Send an image with an optional prompt to Gemini."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        image = Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"❌ Gemini Image Analysis Error: {e}"

# ── PDF Text Extraction ──
def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
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
uploaded_file = st.file_uploader("Upload any file (text, Python, PDF, image)...", type=None)

if uploaded_file and not st.session_state.file_processed:
    file_type, _ = mimetypes.guess_type(uploaded_file.name)
    file_bytes = uploaded_file.read()

    # ✅ Images
    if file_type and file_type.startswith("image"):
        with st.chat_message("user"):
            st.markdown(f"📷 **Uploaded Image:** {uploaded_file.name}")
            st.image(file_bytes)
        st.session_state.messages.append({"role": "user", "content": f"📷 Uploaded Image: {uploaded_file.name}"})

        with st.spinner("💭 Analyzing image with Gemini..."):
            reply = query_gemini_image(file_bytes, "Explain this image.")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ✅ PDFs
    elif file_type == "application/pdf":
        text = extract_text_from_pdf(file_bytes)
        if not text:
            text = "No extractable text found in this PDF."
        with st.chat_message("user"):
            st.markdown(f"📄 **Uploaded PDF:** {uploaded_file.name}")
            st.code(text[:800] + "..." if len(text) > 800 else text)
        st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded PDF: {uploaded_file.name}"})

        with st.spinner("💭 Analyzing PDF content..."):
            reply = query_gemini_text(f"Explain this document:\n{text[:4000]}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ✅ Text & Code Files (.py, .txt, .json, etc.)
    elif file_type and ("text" in file_type or uploaded_file.name.endswith((".py", ".txt", ".json", ".csv", ".md"))):
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except:
            text = str(file_bytes)

        with st.chat_message("user"):
            st.markdown(f"📄 **Uploaded File:** {uploaded_file.name}")
            st.code(text[:800] + "..." if len(text) > 800 else text, language="python" if uploaded_file.name.endswith(".py") else None)
        st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded File: {uploaded_file.name}"})

        with st.spinner("💭 Analyzing file content..."):
            reply = query_gemini_text(f"Explain this file content:\n{text[:4000]}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ❌ Unsupported files
    else:
        with st.chat_message("assistant"):
            st.warning("❌ This file type is not supported yet. Try uploading a text, code, PDF, or image.")
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
