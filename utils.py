import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import re

import re
def clean_syllabus_text(text):
    # Remove common PDF artifacts and page numbers
    text = re.sub(r'--- PAGE \d+ ---', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
  
# --- 1. Client Initialization ---
def get_groq_client():
    """Initializes the Groq client using Streamlit Secrets."""
    if "PRAGYANAI_GROQ_API_KEY" not in st.secrets:
        st.error("Missing GROQ_API_KEY in Streamlit Secrets! Please add it to .streamlit/secrets.toml")
        st.stop()
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. Text Processing & OCR ---
def extract_text_from_pdf(uploaded_file):
    """Extracts and cleans text from a PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                # Basic cleaning: remove multiple spaces and newlines
                content = re.sub(r'\s+', ' ', content)
                text += content + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# --- 3. Structured Extraction (The Agentic Part) ---
def parse_syllabus_with_ai(raw_text, filename):
    """Uses Llama-3 to convert raw text into a structured JSON-like format."""
    client = get_groq_client()
    
    # Specific prompt to find Course Code and Module boundaries
    prompt = f"""
    Analyze the following curriculum text from the file '{filename}'.
    Extract:
    1. Course Title and Code (e.g., BAI654D)
    2. Total Credits and Marks
    3. A Module-wise breakdown (Module 1 to 5) including Main Topic and key keywords.
    4. Course Outcomes (COs).

    RAW TEXT:
    {raw_text[:8000]}  # Limiting context window for efficiency
    
    Return the result as a structured dictionary.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "system", "content": "You are a precise academic data extractor."},
                      {"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error in AI parsing: {e}"

# --- 4. Shared UI Components ---
def init_session_state():
    """Ensures all required session keys exist across pages."""
    if 'master_curriculum' not in st.session_state:
        st.session_state.master_curriculum = {}
    if 'industry_input' not in st.session_state:
        st.session_state.industry_input = ""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def sidebar_status():
    """Displays a consistent status indicator in the sidebar."""
    st.sidebar.divider()
    st.sidebar.subheader("System Status")
    docs_loaded = len(st.session_state.master_curriculum)
    st.sidebar.success(f"📂 {docs_loaded} Syllabus Loaded")
    if st.session_state.industry_input:
        st.sidebar.success("🏢 Industry JD Linked")
    else:
        st.sidebar.warning("⚠️ No Industry JD Linked")
