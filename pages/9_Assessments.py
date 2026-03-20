import streamlit as st
from groq import Groq
import pandas as pd
import random

# Initialize Groq Client
client = Groq(api_key=st.secrets["PRAGYANAI_GROQ_API_KEY"])

st.set_page_config(page_title="Assessment & MCQ Generator", layout="wide")

st.header("📝 Smart Assessment Generator")
st.markdown("Generate balanced Question Papers, MCQs, and Coding Challenges mapped to Course Outcomes.")

# --- DATA CHECK ---
if 'master_curriculum' not in st.session_state or not st.session_state.master_curriculum:
    st.warning("Please upload a syllabus in '1_Extraction' first.")
    st.stop()

# --- SIDEBAR: ASSESSMENT PARAMETERS ---
with st.sidebar:
    st.header("Exam Settings")
    doc_names = list(st.session_state.master_curriculum.keys())
    selected_doc = st.selectbox("Source Syllabus", doc_names)
    
    test_type = st.radio("Assessment Type", ["Quiz (MCQs)", "Coding Lab Test", "Full Theory Paper"])
    
    difficulty_mix = st.multiselect(
        "Bloom's Taxonomy Levels",
        ["Remembering", "Understanding", "Applying", "Analyzing", "Evaluating"],
        default=["Understanding", "Applying"]
    )
    
    num_q = st.slider("Number of Questions", 5, 30, 10)

# --- GENERATION LOGIC ---
def generate_assessment(df, q_type, levels, count):
    concepts = df[['Module', 'Topic', 'Concepts']].to_string()
    # Pulling Course Outcomes if they exist in session state
    outcomes = st.session_state.master_curriculum[selected_doc].get('outcomes', 'General AI Proficiency')

    prompt = f"""
    You are an Academic Examiner. Generate a {q_type} based on the following:
    
    SYLLABUS: {concepts}
    TARGET OUTCOMES: {outcomes}
    BLOOM'S LEVELS: {', '.join(levels)}
    COUNT: {count}
    
    REQUIREMENTS:
    - For MCQs: Provide 4 options, the Correct Answer, and a 'Hint/Explanation'.
    - For Coding Tasks: Provide Problem Statement, Input/Output format, Constraints, and a 'Hidden Test Case' logic.
    - For Theory: Provide marks per question (Total 50) and a brief 'Marking Scheme'.
    
    Format the output in a clean, structured Markdown format.
    """
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content

# --- UI TABS ---
tab1, tab2 = st.tabs(["📄 Generated Assessment", "📊 Blueprint & Coverage"])

if f"expanded_{selected_doc}" in st.session_state:
    df = st.session_state[f"expanded_{selected_doc}"]

    with tab1:
        if st.button(f"Generate {test_type}"):
            with st.spinner("Compiling Questions..."):
                assessment_content = generate_assessment(df, test_type, difficulty_mix, num_q)
                st.markdown(assessment_content)
                
                # Export options
                st.download_button("Download Assessment (.md)", assessment_content, file_name="Syllabus_Exam.md")
    
    with tab2:
        st.subheader("Assessment Blueprint")
        st.write("This table shows the distribution of questions across modules based on the syllabus weights.")
        
        # Calculate theoretical distribution based on weights from Page 2
        blueprint = df[['Module', 'Topic', 'Weight']].copy()
        blueprint['Suggested Questions'] = (blueprint['Weight'] / 100 * num_q).round()
        st.table(blueprint)

else:
    st.info("Please expand the syllabus on Page 2 to map questions to specific modules.")

# --- INTERACTIVE QUIZ FEATURE (Optional) ---
st.divider()
if test_type == "Quiz (MCQs)":
    st.subheader("⚡ Quick Practice Mode")
    if st.button("Start 1-Question Blitz"):
        # Logic to generate just 1 question and use st.radio for interactivity
        st.session_state.quiz_started = True
        # In a full implementation, you'd handle the 'Check Answer' logic here
        st.info("Feature coming soon: Live Interactive Quiz scoring!")
