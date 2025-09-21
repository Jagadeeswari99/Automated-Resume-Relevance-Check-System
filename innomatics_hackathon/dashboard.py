import streamlit as st
import os
import shutil
from ResumeJDMatching import evaluate_single_resume, evaluate_bulk_resumes
import pandas as pd
import plotly.graph_objects as go
import sqlite3

# -----------------------------
# Setup folders
UPLOAD_FOLDER = "uploads"
BULK_FOLDER = os.path.join(UPLOAD_FOLDER, "bulk_resumes")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BULK_FOLDER, exist_ok=True)

# -----------------------------
# Setup database
DB_FILE = "evaluations.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_name TEXT,
    jd_name TEXT,
    relevance_score REAL,
    missing_skills TEXT,
    feedback TEXT,
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# -----------------------------
# Page config
st.set_page_config(page_title="Offline Resume Relevance Check", layout="wide")
st.title("📄 Offline Resume Relevance Check System")
st.markdown("Evaluate resumes offline with rich visuals and stored history.")

# -----------------------------
# Upload JD
st.header("1️⃣ Upload Job Description (PDF)")
jd_file = st.file_uploader("Upload JD PDF", type=["pdf"])
jd_path = None
if jd_file:
    jd_path = os.path.join(UPLOAD_FOLDER, jd_file.name)
    with open(jd_path, "wb") as f:
        f.write(jd_file.getbuffer())
    st.success(f"✅ JD uploaded: {jd_file.name}")

# -----------------------------
# Upload Single Resume
st.header("2️⃣ Upload Single Resume (PDF)")
resume_file = st.file_uploader("Upload Resume", type=["pdf"], key="resume_upload")

if resume_file and jd_path:
    resume_path = os.path.join(UPLOAD_FOLDER, resume_file.name)
    with open(resume_path, "wb") as f:
        f.write(resume_file.getbuffer())

    st.subheader("Evaluation Result:")
    try:
        result = evaluate_single_resume(resume_path, jd_path)
        relevance = result["relevance_score"]
        feedback = result["feedback"]
        missing = result.get("missing_keywords", result.get("missing_skills", []))

        color = "green" if relevance > 70 else "orange" if relevance > 40 else "red"

        # Candidate card
        st.markdown(f"### Candidate: {result['candidate_name']}")
        st.markdown(f"**Feedback:** {feedback}")

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=relevance,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Relevance Score"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': color},
                   'steps':[{'range':[0,40],'color':'red'},{'range':[40,70],'color':'orange'},{'range':[70,100],'color':'green'}]}
        ))
        st.plotly_chart(fig, use_container_width=True)

        # Animated missing skills
        st.markdown("**Missing Skills / Keywords:**")
        for skill in missing:
            st.progress(0.5)
            st.write(f"- {skill}")

        # Save to DB
        c.execute("""
        INSERT INTO evaluations(candidate_name, jd_name, relevance_score, missing_skills, feedback)
        VALUES (?, ?, ?, ?, ?)
        """, (result['candidate_name'], jd_file.name, relevance, ", ".join(missing), feedback))
        conn.commit()

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# -----------------------------
# Bulk evaluation
st.header("3️⃣ Upload Multiple Resumes for Bulk Evaluation")
bulk_files = st.file_uploader("Upload multiple resumes", type=["pdf"], accept_multiple_files=True)

if bulk_files and jd_path:
    # clear folder
    for f in os.listdir(BULK_FOLDER):
        os.remove(os.path.join(BULK_FOLDER, f))

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
            # Save to DB
            c.execute("""
            INSERT INTO evaluations(candidate_name, jd_name, relevance_score, missing_skills, feedback)
            VALUES (?, ?, ?, ?, ?)
            """, (res['candidate_name'], jd_file.name, res['relevance_score'], ", ".join(res.get("missing_skills", [])), res.get("feedback","")))
        conn.commit()

        df = pd.DataFrame(table_data)
        st.dataframe(df)

        # Bulk bar chart with top 3 highlight
        fig_bulk = go.Figure()
        colors = []
        for idx, row in df.iterrows():
            colors.append('gold' if idx < 3 else 'green' if row['Score']>70 else 'orange' if row['Score']>40 else 'red')
        fig_bulk.add_trace(go.Bar(x=df["Candidate"], y=df["Score"], marker_color=colors, text=df["Missing Skills"], hoverinfo='x+y+text'))
        fig_bulk.update_layout(title="Candidate Relevance Scores", yaxis_title="Score (%)")
        st.plotly_chart(fig_bulk, use_container_width=True)

        st.markdown("**🏆 Top 3 Candidates:**")
        for idx, row in df.sort_values("Score", ascending=False).head(3).iterrows():
            st.markdown(f"- **{row['Candidate']}** → Score: {row['Score']}%, Missing Skills: {row['Missing Skills']}")

        # Export option
        st.download_button("📥 Download Evaluation Results CSV", df.to_csv(index=False), "evaluation_results.csv")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# -----------------------------
# History / Audit Logs
st.header("4️⃣ Past Evaluations (History & Audit Logs)")
try:
    df_logs = pd.read_sql_query("SELECT * FROM evaluations ORDER BY evaluation_date DESC", conn)
    st.dataframe(df_logs)
except Exception as e:
    st.error(f"⚠️ Could not fetch logs: {e}")

st.markdown("---")
st.markdown("💡 Fully offline, SQLite-powered, visually enhanced, recruiter-friendly dashboard 🚀")
