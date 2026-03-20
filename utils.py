import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import re
import json

# =========================================
# CLEAN TEXT
# =========================================

def clean_syllabus_text(text):
    text = re.sub(r'--- PAGE \d+ ---', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# =========================================
# GROQ CLIENT
# =========================================

def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("PRAGYANAI_GROQ_API_KEY")

    if not api_key:
        st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
        st.stop()

    return Groq(api_key=api_key)


# =========================================
# PDF EXTRACTION
# =========================================

def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            content = page.extract_text()

            if content:
                content = re.sub(r'\s+', ' ', content)
                text += content + "\n"

        if not text.strip():
            st.warning("⚠️ No text extracted from PDF (possibly scanned PDF)")

        return clean_syllabus_text(text)

    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""


# =========================================
# SAFE JSON PARSER
# =========================================

def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
        return None


# =========================================
# AI PARSER
# =========================================

def parse_syllabus_with_ai(raw_text, filename):
    client = get_groq_client()

    # 👉 chunking (fix)
    chunks = [raw_text[i:i+4000] for i in range(0, len(raw_text), 4000)]
    results = []

    for chunk in chunks:
        prompt = f"""
        Analyze syllabus text from '{filename}'.

        Extract:
        - Course Title & Code
        - Credits
        - Modules (1–5 with topics & keywords)
        - Course Outcomes

        Return ONLY JSON.
        
        TEXT:
        {chunk}
        """

        # 👉 retry logic (fix)
        for attempt in range(2):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Return ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                )

                content = completion.choices[0].message.content
                parsed = safe_json_load(content)

                if parsed:
                    results.append(parsed)
                    break

            except Exception as e:
                if attempt == 1:
                    st.error(f"AI parsing failed: {e}")

    # 👉 merge results
    final_output = {
        "course_title": "",
        "course_code": "",
        "modules": [],
        "outcomes": []
    }

    for r in results:
        if not r:
            continue

        final_output["course_title"] = final_output["course_title"] or r.get("course_title")
        final_output["course_code"] = final_output["course_code"] or r.get("course_code")

        final_output["modules"].extend(r.get("modules", []))
        final_output["outcomes"].extend(r.get("outcomes", []))

    return final_output


# =========================================
# SESSION INIT
# =========================================

def init_session_state():
    if 'master_curriculum' not in st.session_state:
        st.session_state.master_curriculum = {}

    if 'industry_input' not in st.session_state:
        st.session_state.industry_input = ""

    if 'messages' not in st.session_state:
        st.session_state.messages = []


# =========================================
# SIDEBAR STATUS
# =========================================

def sidebar_status():
    st.sidebar.divider()
    st.sidebar.subheader("System Status")

    docs_loaded = len(st.session_state.get("master_curriculum", {}))
    st.sidebar.success(f"📂 {docs_loaded} Syllabus Loaded")

    if st.session_state.get("industry_input"):
        st.sidebar.success("🏢 Industry JD Linked")
    else:
        st.sidebar.warning("⚠️ No Industry JD Linked")


# =========================================
# AGENT CLASS (FIXED)
# =========================================

class SyllabusAgent:
    def __init__(self):
        self.client = get_groq_client()

    def extract_and_clean(self, file):
        try:
            reader = PdfReader(file)
            full_text = ""

            for page in reader.pages:
                raw = page.extract_text()
                if not raw:
                    continue

                lines = raw.split('\n')
                clean_lines = [
                    l for l in lines
                    if not re.match(r'^\d+\s*\|\s*P\s*a\s*g\s*e', l)
                ]

                full_text += "\n".join(clean_lines)

            return clean_syllabus_text(full_text)

        except Exception as e:
            st.error(f"Extraction error: {e}")
            return ""

    def agentic_parser(self, text):
        prompt = f"""
        Convert syllabus into structured JSON.

        Schema:
        {{
          "course_code": "",
          "course_name": "",
          "credits": "",
          "modules": [],
          "outcomes": []
        }}

        TEXT:
        {text[:6000]}
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            return safe_json_load(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Agent parsing error: {e}")
            return None


# =========================================
# GLOBAL INIT
# =========================================

def init_agent():
    if 'agent' not in st.session_state:
        st.session_state.agent = SyllabusAgent()

    if 'master_curriculum' not in st.session_state:
        st.session_state.master_curriculum = {}
