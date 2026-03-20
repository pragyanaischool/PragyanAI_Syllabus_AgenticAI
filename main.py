import streamlit as st
import json
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
    page_title="PragyanAI Intelligence Dashboard",
    layout="wide",
    page_icon="🧠"
)

# =========================================
# INIT
# =========================================
init_session_state()
init_agent()

# =========================================
# HEADER
# =========================================
st.title("🧠 PragyanAI - Curriculum Intelligence Platform")
st.caption("AI-Powered Syllabus Analysis | Industry Mapping | Curriculum Enhancement")

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("⚙️ Controls")

page = st.sidebar.radio(
    "Navigate",
    ["📂 Upload & Process", "📊 Dashboard", "🏢 Industry Mapping", "📘 Curriculum Explorer"]
)

sidebar_status()

# =========================================
# PAGE 1: UPLOAD
# =========================================
if page == "📂 Upload & Process":

    st.header("📂 Upload Syllabus PDFs")

    uploaded_files = st.file_uploader(
        "Upload one or more PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:

        if st.button("🚀 Process All Syllabi"):

            for file in uploaded_files:

                if file.name in st.session_state.master_curriculum:
                    st.warning(f"{file.name} already processed")
                    continue

                with st.spinner(f"Processing {file.name}..."):

                    text = extract_text_from_pdf(file)

                    if not text:
                        st.error(f"Failed to extract text: {file.name}")
                        continue

                    parsed = parse_syllabus_with_ai(text, file.name)

                    if parsed:
                        st.session_state.master_curriculum[file.name] = parsed

            st.success("✅ Processing Complete!")

# =========================================
# PAGE 2: DASHBOARD
# =========================================
elif page == "📊 Dashboard":

    st.header("📊 Curriculum Intelligence Dashboard")

    data = st.session_state.master_curriculum

    if not data:
        st.warning("No syllabus uploaded yet")
    else:
        total_courses = len(data)

        # Dummy scoring (you can replace with real logic later)
        ai_score = 70 + total_courses
        industry_score = 65 + total_courses
        practical_score = 50 + total_courses

        col1, col2, col3 = st.columns(3)

        col1.metric("📘 Courses", total_courses)
        col2.metric("🤖 AI Readiness", f"{ai_score}%")
        col3.metric("🏢 Industry Alignment", f"{industry_score}%")

        st.divider()

        # Modules Visualization
        st.subheader("📚 Module Distribution")

        module_counts = {}

        for course, content in data.items():
            modules = content.get("modules", [])
            module_counts[course] = len(modules)

        st.bar_chart(module_counts)

# =========================================
# PAGE 3: INDUSTRY MAPPING
# =========================================
elif page == "🏢 Industry Mapping":

    st.header("🏢 Industry Job Description Mapping")

    jd = st.text_area("Paste Job Description")

    if st.button("Analyze JD vs Curriculum"):

        if not jd:
            st.warning("Please enter job description")
        elif not st.session_state.master_curriculum:
            st.warning("Upload syllabus first")
        else:

            # Dummy logic (replace later with AI)
            missing_skills = ["LLMs", "Vector DB", "MLOps"]

            st.subheader("📉 Skill Gap Analysis")

            st.write("Missing Skills:")
            for skill in missing_skills:
                st.error(f"❌ {skill}")

            st.success("✔ Core Programming Covered")

# =========================================
# PAGE 4: CURRICULUM EXPLORER
# =========================================
elif page == "📘 Curriculum Explorer":

    st.header("📘 Explore Curriculum")

    data = st.session_state.master_curriculum

    if not data:
        st.warning("No syllabus available")
    else:

        selected_course = st.selectbox("Select Course", list(data.keys()))

        course_data = data[selected_course]

        st.subheader("📌 Course Info")
        st.json(course_data)

        st.subheader("📚 Modules")

        modules = course_data.get("modules", [])

        for m in modules:
            with st.expander(f"Module {m.get('id', '')}: {m.get('topic', '')}"):
                st.write("Concepts:", m.get("concepts", []))

        st.subheader("🎯 Outcomes")

        for o in course_data.get("outcomes", []):
            st.success(o)

# =========================================
# FOOTER
# =========================================
st.divider()
st.caption("🚀 PragyanAI | Building the Future of AI-Native Education Systems")
