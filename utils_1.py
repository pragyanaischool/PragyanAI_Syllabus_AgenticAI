import re
import json
import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from typing import List, Dict

# =========================================
# 1. CONFIG / CLIENT
# =========================================

class LLMClient:
    def __init__(self):
        api_key = st.secrets.get("PRAGYANAI_GROQ_API_KEY")
        if not api_key:
            st.error("Missing PRAGYANAI_GROQ_API_KEY in secrets.toml")
            st.stop()

        self.client = Groq(api_key=api_key)

    def call(self, prompt: str, temperature=0) -> str:
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"ERROR: {str(e)}"


# =========================================
# 2. TEXT CLEANING
# =========================================

def clean_text(text: str) -> str:
    text = re.sub(r'--- PAGE \d+ ---', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# =========================================
# 3. PDF PROCESSOR
# =========================================

class PDFProcessor:

    @staticmethod
    def extract_text(file) -> str:
        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"

        return clean_text(text)

    @staticmethod
    def chunk_text(text: str, chunk_size=4000) -> List[str]:
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


# =========================================
# 4. AGENTIC PARSER
# =========================================

class SyllabusParserAgent:

    def __init__(self):
        self.llm = LLMClient()

    def parse_chunk(self, chunk: str) -> Dict:
        prompt = f"""
        Extract structured syllabus data.

        Return JSON:
        {{
          "course_code": "",
          "course_name": "",
          "modules": [
            {{"id": 1, "topic": "", "concepts": [], "hours": 0}}
          ],
          "outcomes": []
        }}

        TEXT:
        {chunk}
        """

        raw_output = self.llm.call(prompt)
        return self.safe_json(raw_output)

    def safe_json(self, text: str) -> Dict:
        try:
            return json.loads(text)
        except:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    return {}
        return {}


# =========================================
# 5. MERGER + VALIDATOR AGENT
# =========================================

class SyllabusValidator:

    @staticmethod
    def merge(results: List[Dict]) -> Dict:
        merged = {
            "course_code": "",
            "course_name": "",
            "modules": [],
            "outcomes": []
        }

        for r in results:
            if not r:
                continue

            merged["course_code"] = merged["course_code"] or r.get("course_code")
            merged["course_name"] = merged["course_name"] or r.get("course_name")

            merged["modules"].extend(r.get("modules", []))
            merged["outcomes"].extend(r.get("outcomes", []))

        return merged

    @staticmethod
    def deduplicate_modules(modules: List[Dict]) -> List[Dict]:
        seen = set()
        unique = []

        for m in modules:
            key = m.get("topic")
            if key and key not in seen:
                seen.add(key)
                unique.append(m)

        return unique

    @staticmethod
    def validate(data: Dict) -> Dict:
        if not data:
            return {}

        data["modules"] = SyllabusValidator.deduplicate_modules(
            data.get("modules", [])
        )

        return data


# =========================================
# 6. MAIN SERVICE PIPELINE
# =========================================

class SyllabusService:

    def __init__(self):
        self.parser = SyllabusParserAgent()
        self.validator = SyllabusValidator()

    def process(self, file) -> Dict:
        raw_text = PDFProcessor.extract_text(file)
        chunks = PDFProcessor.chunk_text(raw_text)

        parsed_results = []

        for chunk in chunks:
            parsed = self.parser.parse_chunk(chunk)
            parsed_results.append(parsed)

        merged = self.validator.merge(parsed_results)
        validated = self.validator.validate(merged)

        return validated


# =========================================
# 7. SESSION INIT (UI SHOULD IMPORT THIS)
# =========================================

def init_session():
    if "service" not in st.session_state:
        st.session_state.service = SyllabusService()

    if "curriculum" not in st.session_state:
        st.session_state.curriculum = {}
