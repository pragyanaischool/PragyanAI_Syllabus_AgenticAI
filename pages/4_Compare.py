import streamlit as st
from groq import Groq
import pandas as pd
import plotly.graph_objects as go

# Initialize Groq Client from Secrets
client_4 = Groq(api_key=st.secrets["PRAGYANAI_GROQ_API_KEY"])

st.set_page_config(page_title="PragyanAI Curriculum Delta & Comparison", layout="wide")

st.header("⚖️ Curriculum Comparison & Delta Mapping")
st.markdown("Identify unique strengths, core commonalities, and the gap to industry alignment across different institutions.")

# --- DATA CHECK ---
if 'master_curriculum' not in st.session_state or len(st.session_state.master_curriculum) < 1:
    st.warning("Please upload at least one syllabus in '1_Extraction' to compare.")
    st.stop()

# --- SELECTION ---
all_docs = list(st.session_state.master_curriculum.keys())
selected_docs = st.multiselect("Select Syllabi to Compare", all_docs, default=all_docs[:2])

if len(selected_docs) < 1:
    st.info("Select at least one document to see the analysis.")
    st.stop()

# --- COMPARATIVE ANALYSIS LOGIC ---
def generate_comparison_matrix(doc_list):
    """Uses LLM to find Common, Unique, and Industry-Gap topics."""
    
    # Prepare context from session state
    context_data = ""
    for doc in doc_list:
        concepts = st.session_state.get(f"expanded_{doc}", pd.DataFrame())
        concept_list = concepts['Concepts'].tolist() if not concepts.empty else ["Data not expanded"]
        context_data += f"\nCOLLEGE: {doc}\nCONCEPTS: {', '.join(concept_list)}\n"

    jd_context = st.session_state.get('industry_input', "General AI Industry Standards")

    prompt = f"""
    You are a Senior Academic Auditor. Compare the following curricula and the Industry JD.
    
    DATA:
    {context_data}
    
    INDUSTRY REQUIREMENTS:
    {jd_context}
    
    TASK:
    1. Identify the 'CORE SYLLABUS': Topics present in ALL selected colleges.
    2. Identify 'UNIQUE MAPPING': For each college, what specific topics do they teach that others DON'T?
    3. Calculate 'INDUSTRY DELTA': What % of the Industry JD is covered by these combined? What is missing?
    
    Return the response in structured Markdown with clear headers.
    """
    
    response = client_4.chat.completions.create(
        model="meta-llama/llama-prompt-guard-2-86m",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# --- UI LAYOUT ---

tab1, tab2 = st.tabs(["📊 Comparison Dashboard", "🎯 Delta & Unique Mapping"])

with tab1:
    st.subheader("Curriculum Overlap & Coverage")
    
    # Visualizing Coverage (Example Logic)
    # In a real app, you'd calculate these scores via LLM or keyword matching
    categories = ['Foundations', 'Math/Logic', 'Modern AI (LLMs)', 'Practical Labs', 'Ethics']
    
    fig = go.Figure()

    for doc in selected_docs:
        # Dummy data for radar chart - in production, derive these from 'expanded_df' weights
        fig.add_trace(go.Scatterpolar(
            r=[80, 70, 40, 60, 50], # Example scores
            theta=categories,
            fill='toself',
            name=doc
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Curriculum Balance Radar"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    if st.button("Generate Detailed Delta Report"):
        with st.spinner("Analyzing differences..."):
            report = generate_comparison_matrix(selected_docs)
            st.markdown(report)
            
            # Allow user to download the comparison
            st.download_button(
                label="Download Delta Report",
                data=report,
                file_name="Curriculum_Comparison_Report.md",
                mime="text/markdown"
            )

# --- THE "UNIQUE" TABLE ---
st.divider()
st.subheader("Unique Concept Breakdown")
cols = st.columns(len(selected_docs))

for i, doc in enumerate(selected_docs):
    with cols[i]:
        st.info(f"**{doc}**")
        if f"expanded_{doc}" in st.session_state:
            df = st.session_state[f"expanded_{doc}"]
            # Display topics with weight > 20% or tagged as unique
            st.write("Primary Focus Areas:")
            st.dataframe(df[df['Weight'] >= 20][['Topic', 'Concepts']], hide_index=True)
        else:
            st.write("Please expand syllabus on Page 2 first.")
