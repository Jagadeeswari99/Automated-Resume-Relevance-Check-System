import os
import fitz  # PyMuPDF
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Console colors
class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# -----------------------------
# Helper: extract text from PDF
def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"{bcolors.FAIL}⚠️ File not found: {pdf_path}{bcolors.ENDC}")
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# -----------------------------
# Helper: clean keywords (remove duplicates & lowercase)
def clean_keywords(keywords):
    return list({kw.strip().lower() for kw in keywords if kw.strip()})

# -----------------------------
# Load JD PDF and extract keywords (must-have + good-to-have)
def load_jd(jd_path):
    jd_text = extract_text_from_pdf(jd_path)
    # Split by line, comma, or semicolon
    raw_keywords = []
    for line in jd_text.splitlines():
        raw_keywords.extend(line.replace(';', ',').split(','))
    return clean_keywords(raw_keywords)

# -----------------------------
# Evaluate single resume
def evaluate_single_resume(resume_path, jd_path):
    resume_text = extract_text_from_pdf(resume_path)
    jd_keywords = load_jd(jd_path)

    if not jd_keywords:
        raise ValueError(f"{bcolors.FAIL}⚠️ No keywords found in JD{bcolors.ENDC}")

    # TF-IDF Vectorizer with JD keywords as vocabulary
    vectorizer = TfidfVectorizer(vocabulary=jd_keywords)
    tfidf_matrix = vectorizer.fit_transform([resume_text])
    scores = tfidf_matrix.toarray()[0]

    relevance_score = sum(scores) / len(jd_keywords) * 100

    # Determine fit
    if relevance_score > 70:
        fit = "High fit"
        color = bcolors.OKGREEN
    elif relevance_score > 40:
        fit = "Medium fit"
        color = bcolors.WARNING
    else:
        fit = "Low fit"
        color = bcolors.FAIL

    # Missing keywords
    missing_keywords = [jd_keywords[i] for i, val in enumerate(scores) if val == 0]

    feedback = f"Candidate is {fit}. Missing keywords: {', '.join(missing_keywords) if missing_keywords else 'None'}"

    result = {
        "candidate_name": os.path.basename(resume_path),
        "relevance_score": round(relevance_score),
        "missing_keywords": missing_keywords,
        "feedback": feedback
    }

    # Console output
    print("\n---------------------------------")
    print(f"Resume: {bcolors.BOLD}{os.path.basename(resume_path)}{bcolors.ENDC}")
    print(f"Score: {color}{round(relevance_score)}% ({fit}){bcolors.ENDC}")
    print(f"Missing Keywords: {missing_keywords}")
    print(f"Feedback: {feedback}")

    return result

# -----------------------------
# Evaluate multiple resumes in bulk
def evaluate_bulk_resumes(resume_folder, jd_path):
    if not os.path.exists(resume_folder):
        raise FileNotFoundError(f"{bcolors.FAIL}⚠️ Resume folder not found: {resume_folder}{bcolors.ENDC}")
    
    resumes = [os.path.join(resume_folder, f) for f in os.listdir(resume_folder) if f.lower().endswith(".pdf")]
    if not resumes:
        raise FileNotFoundError(f"{bcolors.FAIL}⚠️ No PDF resumes found in {resume_folder}{bcolors.ENDC}")

    results = []
    for resume_file in resumes:
        res = evaluate_single_resume(resume_file, jd_path)
        results.append(res)

    # Save results
    output_file = os.path.join(resume_folder, "evaluation_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"\n{bcolors.OKGREEN}✅ Bulk evaluation complete. Results saved to {output_file}{bcolors.ENDC}")
    return results

# -----------------------------
# Example usage (uncomment to test standalone)
# JD_PATH = "JD/sample_jd.pdf"
# RESUME_PATH = "Resumes/sample_resume.pdf"
# evaluate_single_resume(RESUME_PATH, JD_PATH)
# evaluate_bulk_resumes("Resumes", JD_PATH)
