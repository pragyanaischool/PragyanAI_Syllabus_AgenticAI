import streamlit as st
from PyPDF2 import PdfReader
from groq import Groq

client = Groq(api_key="PRAGYNAAI_GROQ_API_KEY")

def extract_syllabus(text, filename):
    prompt = f"Extract the structured syllabus from this text for file {filename}. Identify Course Code, Modules 1-5, and Marks."
    # API Call logic here...
    return {"filename": filename, "data": "Structured Content"}

uploaded_files = st.file_uploader("Upload Syllabi (PDF)", accept_multiple_files=True)

if st.button("Process Documents"):
    for file in uploaded_files:
        text = "".join([p.extract_text() for p in PdfReader(file).pages])
        result = extract_syllabus(text, file.name)
        st.session_state.master_curriculum[file.name] = result
    st.success("All documents processed!")
