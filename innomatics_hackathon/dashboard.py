import streamlit as st
import os
import shutil
from ResumeJDMatching import evaluate_single_resume, evaluate_bulk_resumes, bcolors
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# Setup folders
UPLOAD_FOLDER = "uploads"
BULK_FOLDER = os.path.join(UPLOAD_FOLDER, "bulk_resumes")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BULK_FOLDER, exist_ok=True)

# -----------------------------
# Page config
st.set_page_config(
    page_title="Offline Resume Relevance Check",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 Offline Resume Relevance Check System")
st.markdown("Evaluate resumes against a Job Description (JD) offline with rich visuals.")

# -----------------------------
# Upload JD (PDF)
st.header("1️⃣ Upload Job Description (PDF)")
jd_file = st.file_uploader(
    "Upload JD PDF",
    type=["pdf"],
    key="jd_upload"
)

jd_path = None
if jd_file:
    jd_path = os.path.join(UPLOAD_FOLDER, jd_file.name)
    with open(jd_path, "wb") as f:
        f.write(jd_file.getbuffer())
    st.success(f"✅ JD uploaded: {jd_file.name}")

# -----------------------------
# Upload Single Resume
st.header("2️⃣ Upload Single Resume (PDF)")
resume_file = st.file_uploader(
    "Upload Resume",
    type=["pdf"],
    key="resume_upload"
)

if resume_file and jd_path:
    resume_path = os.path.join(UPLOAD_FOLDER, resume_file.name)
    with open(resume_path, "wb") as f:
        f.write(resume_file.getbuffer())

    # Evaluate single resume
    st.subheader("Evaluation Result:")
    try:
        result = evaluate_single_resume(resume_path, jd_path)
        relevance = result["relevance_score"]
        feedback = result["feedback"]
        missing = result.get("missing_keywords", result.get("missing_skills", []))

        # Color-coded score
        if relevance > 70:
            color = "green"
        elif relevance > 40:
            color = "orange"
        else:
            color = "red"

        # Candidate card
        st.markdown(f"### Candidate: {result['candidate_name']}")
        st.markdown(f"**Feedback:** {feedback}")

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=relevance,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Relevance Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "green"}
                ],
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

        # Missing skills progress
        st.markdown("**Missing Skills / Keywords:**")
        for skill in missing:
            st.progress(0.5)  # Placeholder: can simulate missing skills visually
            st.write(f"- {skill}")

    except Exception as e:
        st.error(f"⚠️ Error during evaluation: {e}")

# -----------------------------
# Bulk Resume Evaluation
st.header("3️⃣ Upload Multiple Resumes for Bulk Evaluation")
bulk_files = st.file_uploader(
    "Upload multiple resumes",
    type=["pdf"],
    accept_multiple_files=True,
    key="bulk_upload"
)

if bulk_files and jd_path:
    # Clear bulk folder first
    for f in os.listdir(BULK_FOLDER):
        os.remove(os.path.join(BULK_FOLDER, f))

    # Save uploaded files
    resume_paths = []
    for file in bulk_files:
        path = os.path.join(BULK_FOLDER, file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        resume_paths.append(path)

    st.subheader("Bulk Evaluation Results:")
    try:
        bulk_results = evaluate_bulk_resumes(BULK_FOLDER, jd_path)
        table_data = []
        for res in bulk_results:
            table_data.append({
                "Candidate": res["candidate_name"],
                "Score": res["relevance_score"],
                "Missing Skills": ", ".join(res.get("missing_skills", [])),
                "Feedback": res.get("feedback", "")
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df)

        # Bulk bar chart
        fig_bulk = go.Figure()
        fig_bulk.add_trace(go.Bar(
            x=df["Candidate"],
            y=df["Score"],
            marker_color=['green' if s>70 else 'orange' if s>40 else 'red' for s in df["Score"]]
        ))
        fig_bulk.update_layout(title="Candidate Relevance Scores", yaxis_title="Score (%)")
        st.plotly_chart(fig_bulk, use_container_width=True)

        # Highlight top 3 visually
        top_candidates = df.sort_values("Score", ascending=False).head(3)
        st.markdown("**🏆 Top 3 Candidates:**")
        for idx, row in top_candidates.iterrows():
            st.markdown(f"- **{row['Candidate']}** → Score: {row['Score']}%, Missing Skills: {row['Missing Skills']}")

    except Exception as e:
        st.error(f"⚠️ Error during bulk evaluation: {e}")

st.markdown("---")
st.markdown("💡 Fully offline, visually enhanced, hackathon-ready dashboard.")
