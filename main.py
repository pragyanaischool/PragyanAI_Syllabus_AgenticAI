import streamlit as st
from utils import (
    extract_text_from_pdf,
    parse_syllabus_with_ai,
    init_session_state,
    sidebar_status,
    init_agent
)

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="PragyanAI Syllabus Engine",
    layout="wide"
)

st.title("📘 PragyanAI - Agentic Syllabus Intelligence")

# =========================================
# INIT
# =========================================

init_session_state()
init_agent()
sidebar_status()

# =========================================
# FILE UPLOAD
# =========================================

uploaded_file = st.file_uploader(
    "Upload Syllabus PDF",
    type=["pdf"]
)

# =========================================
# PROCESS BUTTON
# =========================================

if uploaded_file:

    st.success(f"📄 Uploaded: {uploaded_file.name}")

    if st.button("🚀 Process Syllabus"):

        # Prevent re-processing same file
        if uploaded_file.name in st.session_state.master_curriculum:
            st.warning("⚠️ This file is already processed.")
        else:
            with st.spinner("🤖 AI is analyzing syllabus..."):

                # Step 1: Extract text
                text = extract_text_from_pdf(uploaded_file)

                if not text:
                    st.error("❌ Failed to extract text from PDF.")
                else:
                    # Step 2: Parse with AI
                    parsed = parse_syllabus_with_ai(text, uploaded_file.name)

                    if not parsed:
                        st.error("❌ AI parsing failed.")
                    else:
                        # Save result
                        st.session_state.master_curriculum[uploaded_file.name] = parsed

                        st.success("✅ Syllabus processed successfully!")

# =========================================
# DISPLAY RESULTS
# =========================================

if st.session_state.master_curriculum:

    st.subheader("📊 Processed Curriculums")

    for filename, data in st.session_state.master_curriculum.items():

        with st.expander(f"📘 {filename}", expanded=False):
            st.json(data)

# =========================================
# CLEAR BUTTON
# =========================================

if st.button("🧹 Clear All Data"):
    st.session_state.master_curriculum = {}
    st.success("Cleared all processed data!")
