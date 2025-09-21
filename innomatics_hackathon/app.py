from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil, os, json
from ResumeJDMatching import evaluate_multiple_resumes

app = FastAPI(title="Offline Resume-JD Matching API")

UPLOAD_FOLDER = "uploads"
RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
JD_FOLDER = os.path.join(UPLOAD_FOLDER, "jds")

os.makedirs(RESUME_FOLDER, exist_ok=True)
os.makedirs(JD_FOLDER, exist_ok=True)

# -----------------------------
# Upload Resume
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"message": "Resume must be PDF"})
    save_path = os.path.join(RESUME_FOLDER, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": f"Resume saved: {save_path}"}

# -----------------------------
# Upload JD
@app.post("/upload_jd")
async def upload_jd(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".json"):
        return JSONResponse(status_code=400, content={"message": "JD must be JSON"})
    save_path = os.path.join(JD_FOLDER, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": f"JD saved: {save_path}"}

# -----------------------------
# Evaluate all resumes against all JDs
@app.get("/evaluate_all")
def evaluate_all():
    resume_files = [os.path.join(RESUME_FOLDER, f) for f in os.listdir(RESUME_FOLDER) if f.lower().endswith(".pdf")]
    jd_files = [os.path.join(JD_FOLDER, f) for f in os.listdir(JD_FOLDER) if f.lower().endswith(".json")]

    if not resume_files or not jd_files:
        return JSONResponse(status_code=400, content={"message": "Upload both resumes and JDs first."})

    results = evaluate_multiple_resumes(resume_files, jd_files)

    # Save result offline
    result_file = os.path.join(UPLOAD_FOLDER, "evaluation_results.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    return {"results": results}
