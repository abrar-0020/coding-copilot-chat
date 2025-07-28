# 🤖 Mini Copilot – AI File Analyzer (Gemini Powered)

### 📌 **Overview**
**Mini Copilot** is an **AI-powered coding assistant** built with **Streamlit** and **Google Gemini API**.  
It allows users to upload **any file (Python, text, images, PDFs, etc.)** and interact with it intelligently.  
You can ask it questions, get explanations, and analyze files with ease.

🌐 **Live Demo:**  
👉 [https://mini-copilot.streamlit.app/](https://mini-copilot.streamlit.app/)

---

## 🚀 **Features**
- 🧠 **AI-Powered by Gemini** – Understands and explains content smartly.  
- 📂 **Multi-File Support** – Supports `.py`, `.txt`, `.pdf`, `.jpg`, `.png`, and more.  
- 🔍 **OCR for Scanned PDFs** – Extracts text using Tesseract.  
- ⚡ **Fast & Simple** – Minimal UI with quick responses.  
- 🔒 **Secure** – Uses `.env` for API key protection.  

---

## 🛠 **Tech Stack**
- **Framework:** Streamlit  
- **AI Model:** Google Gemini  
- **OCR:** Tesseract + pdf2image  
- **PDF Parsing:** pdfplumber  
- **Image Processing:** Pillow  

---

## 📦 **Installation**

``bash
# 1. Clone the repository
git clone https://github.com/abrar-0020/coding-copilot-chat.git
cd coding-copilot-chat

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key to .env
echo "GEMINI_API_KEY=your_key_here" > .env

# 5. Run the app
streamlit run app.py
``

---

## 📄 **Usage**
1. Upload a file (Python, image, PDF, etc.).  
2. Mini Copilot analyzes and explains it.  
3. Ask follow-up questions in the chat.  

---

## ✅ **Requirements**
``
streamlit
google-generativeai
pdfplumber
pillow
pytesseract
pdf2image
python-dotenv
``
Also install:
- **Tesseract OCR** ([Guide](https://github.com/UB-Mannheim/tesseract/wiki))  
- **Poppler** (for pdf2image)

---

## 🧑‍💻 **Example Usage**
- Upload a **Python script** → get a human-readable explanation.  
- Upload an **image** → AI describes and interprets it.  
- Upload a **scanned PDF** → OCR extracts text → AI explains it.  

---

## ✅ **Project Structure**
``
📂 coding-copilot-chat
 ├── app.py              # Main Streamlit App
 ├── requirements.txt    # Dependencies
 ├── .env                # API Key (ignored in Git)
 └── README.md           # Documentation
``

---

## 📝 **Future Enhancements**
- [ ] Support for audio and video files.  
- [ ] Multi-page PDF summaries with chunking.  
- [ ] Real-time streaming responses.

---

## 📜 **License & Copyright**
``
© 2025 Abrar. All rights reserved.

This project is protected by copyright law.  
You may use and modify it for personal and educational purposes.  
Commercial use requires prior written permission from the author.
```
