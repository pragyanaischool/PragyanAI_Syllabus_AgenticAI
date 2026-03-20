import streamlit as st

st.set_page_config(page_title="PragyanAI Curriculum Intelligence AI", layout="wide")

st.sidebar.title("Navigation")
st.sidebar.info("Select a module to begin Curriculum Analysis.")

if 'master_curriculum' not in st.session_state:
    st.session_state.master_curriculum = {}
if 'industry_input' not in st.session_state:
    st.session_state.industry_input = ""

st.title(" PragyanAI Curriculum Intelligence Platform")
st.markdown("""
Welcome to the AI-powered academic-to-industry alignment tool. 
1. **Upload** college syllabi.
2. **Expand** and edit concepts.
3. **Align** with Industry Job Descriptions.
4. **Generate** Labs, Projects, and Assessments.
""")
