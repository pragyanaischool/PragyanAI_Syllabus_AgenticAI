import streamlit as st
from groq import Groq
import pandas as pd

# Initialize Groq Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Practical Learning & Project Hub", layout="wide")

st.header("🛠️ Practical Implementation & Industry Project Factory")
st.markdown("Generate targeted coding exercises and industrial-grade project blueprints based on your curriculum.")

# --- DATA CHECK ---
if 'master_curriculum' not in st.session_state or not st.session_state.master_curriculum:
    st.warning("Please upload a syllabus in '1_Extraction' first.")
    st.stop()

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("Exercise Configuration")
    doc_names = list(st.session_state.master_curriculum.keys())
    selected_doc = st.selectbox("Source Syllabus", doc_names)
    
    prog_count = st.select_slider("Number of Lab Programs", options=[10, 20, 50])
    
    tool_focus = st.multiselect(
        "Focus Tools/Libs", 
        ["Python (Core)", "Scikit-Learn", "NLTK/Spacy", "TensorFlow/PyTorch", "OpenAI/Groq API", "Pandas/NumPy"],
        default=["Python (Core)", "Scikit-Learn"]
    )
    
    st.divider()
    st.header("Project Configuration")
    num_projects = st.number_input("Number of Industry Projects", min_value=1, max_value=5, value=2)

# --- HELPER: SYSTEM PROMPTS ---
def get_lab_prompt(df, count, tools):
    concepts = ", ".join(df['Concepts'].tolist())
    return f"""
    You are a Technical Lab Instructor. Create a list of {count} Lab Programs based on:
    CONCEPTS: {concepts}
    TOOLS: {', '.join(tools)}
    
    For each program, provide:
    1. Program ID & Title
    2. Key Concept Covered (from the syllabus)
    3. Tool/Library Used
    4. Implementation Hint (Logic flow)
    
    Format: A Markdown Table.
    """

def get_project_prompt(df, count):
    concepts = ", ".join(df['Topic'].tolist())
    gap = st.session_state.get(f"gap_analysis_{selected_doc}", "General AI Engineering")
    return f"""
    Create {count} Detailed Industry Project Blueprints.
    SYLLABUS FOCUS: {concepts}
    INDUSTRY GAP: {gap}
    
    For each project, include:
    - Project Title & Industry Domain
    - Problem Statement
    - Detailed Tech Stack (Frontend, Backend, AI Model, Infrastructure)
    - Module Integration (Which syllabus modules are used?)
    - Evaluation Matrix: Provide a table with criteria (e.g., Accuracy, Latency, Code Quality) and weightage (%).
    """

# --- UI TABS ---
tab1, tab2 = st.tabs(["🧪 Targeted Lab Exercises", "🚀 Detailed Industry Blueprints"])

if f"expanded_{selected_doc}" in st.session_state:
    df = st.session_state[f"expanded_{selected_doc}"]

    with tab1:
        st.subheader(f"List of {prog_count} Practice Programs")
        if st.button(f"Generate {prog_count} Programs"):
            with st.spinner("Generating exercise list..."):
                lab_content = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": get_lab_prompt(df, prog_count, tool_focus)}],
                ).choices[0].message.content
                st.markdown(lab_content)
                st.download_button("Download Lab List", lab_content, file_name="Lab_Programs.md")

    with tab2:
        st.subheader("Industry-Ready Project Blueprints")
        if st.button(f"Generate {num_projects} Projects"):
            with st.spinner("Designing industrial solutions..."):
                project_content = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": get_project_prompt(df, num_projects)}],
                ).choices[0].message.content
                st.markdown(project_content)
                st.download_button("Download Project Blueprints", project_content, file_name="Industry_Projects.md")
else:
    st.info("Please expand the syllabus on Page 2 first.")
