import streamlit as st
from groq import Groq
import pandas as pd

# Initialize Groq Client from Secrets
client = Groq(api_key=st.secrets["PRAGYANAI_GROQ_API_KEY"])

st.set_page_config(page_title="Industry Gap Analysis", layout="wide")

st.header("🏢 Industry Alignment & Gap Analysis")
st.markdown("Compare your academic curriculum against real-world Job Descriptions to find 'The Delta'.")

# --- DATA CHECK ---
if 'master_curriculum' not in st.session_state or not st.session_state.master_curriculum:
    st.warning("Please upload and expand a syllabus in the previous pages first.")
    st.stop()

# --- SIDEBAR: INPUT ---
st.sidebar.subheader("Target Industry Input")
jd_text = st.sidebar.text_area(
    "Paste Job Description (JD) here:", 
    placeholder="e.g., We are looking for an AI Engineer proficient in PyTorch, LLMs, and MLOps...",
    height=300
)

target_role = st.sidebar.selectbox("Target Role", ["AI Engineer", "Data Scientist", "MLOps Engineer", "NLP Researcher"])

# --- MAIN UI ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Current Academic Focus")
    doc_names = list(st.session_state.master_curriculum.keys())
    selected_doc = st.selectbox("Select Syllabus to Analyze", doc_names)
    
    # Get the expanded data from Page 2
    if f"expanded_{selected_doc}" in st.session_state:
        current_syllabus_df = st.session_state[f"expanded_{selected_doc}"]
        st.dataframe(current_syllabus_df[['Module', 'Topic', 'Concepts']], use_container_width=True)
    else:
        st.info("No expanded data found. Using raw extraction.")
        st.write(st.session_state.master_curriculum[selected_doc]['data'])

with col2:
    st.subheader("Industry Requirements")
    if st.button("Analyze JD & Find Gaps") and jd_text:
        with st.spinner("Llama-3 is performing Gap Analysis..."):
            
            # Combine current concepts into a string for the prompt
            academic_concepts = ", ".join(current_syllabus_df['Concepts'].tolist()) if f"expanded_{selected_doc}" in st.session_state else "General AI"
            
            gap_prompt = f"""
            SYSTEM: You are an Industry-Academic Consultant.
            
            INPUT 1 (Academic Syllabus Concepts): {academic_concepts}
            INPUT 2 (Job Description): {jd_text}
            
            TASK:
            1. Extract 'Must-Have' technical skills from the JD.
            2. Compare them with the Academic Syllabus.
            3. Identify 'THE GAP' (Industry skills NOT in the syllabus).
            4. Suggest 3 specific practical projects to bridge this gap.
            
            FORMAT: Return a structured analysis.
            """
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": gap_prompt}],
                temperature=0.2
            )
            
            analysis_result = response.choices[0].message.content
            st.session_state[f"gap_analysis_{selected_doc}"] = analysis_result
            st.markdown(analysis_result)
    else:
        st.info("Paste a JD in the sidebar and click 'Analyze' to see the results.")

# --- THE DELTA VISUALIZATION ---
if f"gap_analysis_{selected_doc}" in st.session_state:
    st.divider()
    st.subheader("🚀 Practical Enhancement Strategy")
    
    # UI Component to "Inject" Industry topics back into the curriculum
    st.write("Would you like to add these missing industry skills to your Master Curriculum?")
    new_skill = st.text_input("Add Industry Skill to Curriculum (e.g., 'Deployment with Docker')")
    
    if st.button("Add to Master Syllabus"):
        # Logic to append to the dataframe in session_state
        new_row = {"Module": "Industry Add-on", "Topic": "Applied AI", "Sub-Topics": "Practical", "Concepts": new_skill, "Weight": 5}
        st.session_state[f"expanded_{selected_doc}"] = pd.concat([st.session_state[f"expanded_{selected_doc}"], pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"'{new_skill}' has been added to the syllabus on Page 2!")
