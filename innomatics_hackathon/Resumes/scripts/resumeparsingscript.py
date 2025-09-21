import os
import fitz  # PyMuPDF
import docx2txt
import re
import json
import spacy

# ----------------------------
# 1. Paths
# ----------------------------
resume_folder = r"C:\JAGA\innomatics_hackathon\Resumes\dataresume"
output_file = r"C:\JAGA\innomatics_hackathon\Resumes\outcomes_resumes\parsed_resumes_smart.json"

# ----------------------------
# 2. Load spaCy model
# ----------------------------
nlp = spacy.load("en_core_web_sm")

# ----------------------------
# 3. Predefined skill list
# ----------------------------
SKILLS = [
    "python", "sql", "excel", "tableau", "power bi", "aws", "docker",
    "pandas", "numpy", "matplotlib", "seaborn", "spark", "pytorch",
    "tensorflow", "java", "c++", "machine learning", "data analysis",
    "powerpoint", "git", "kafka"
]

# ----------------------------
# 4. Helper functions
# ----------------------------
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

def clean_text(text):
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text.lower()

def extract_skills(text):
    found_skills = [skill.title() for skill in SKILLS if skill.lower() in text]
    return list(set(found_skills))

def extract_education(text):
    edu_patterns = [
        r"\b(b\.sc|bsc|b\.tech|be|m\.sc|msc|m\.tech|mba|phd)\b.*?(\d{4})",
        r"\b(university|college|institute)\b.*?(\d{4})"
    ]
    edu_matches = []
    for pattern in edu_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            edu_matches.append(" ".join(m).title())
    return list(set(edu_matches))

def extract_certifications(text):
    cert_keywords = ["certificate", "certified", "certification", "achieved"]
    certs = []
    lines = text.split("\n")
    for line in lines:
        if any(word in line.lower() for word in cert_keywords):
            certs.append(line.strip())
    return list(set(certs))

def extract_experience(text):
    exp_keywords = ["worked at", "experience", "internship", "role as", "responsible for"]
    lines = text.split("\n")
    exps = []
    for line in lines:
        if any(word in line.lower() for word in exp_keywords):
            exps.append(line.strip())
    return list(set(exps))

def extract_projects(text):
    proj_keywords = ["project", "capstone", "initiative"]
    lines = text.split("\n")
    projs = []
    for line in lines:
        if any(word in line.lower() for word in proj_keywords):
            projs.append(line.strip())
    return list(set(projs))

# ----------------------------
# 5. Main Parsing
# ----------------------------
parsed_resumes = []

for file_name in os.listdir(resume_folder):
    file_path = os.path.join(resume_folder, file_name)
    if file_name.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_name.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        continue

    cleaned_text = clean_text(text)

    resume_data = {
        "file_name": file_name,
        "full_text": cleaned_text,
        "skills": extract_skills(cleaned_text),
        "education": extract_education(cleaned_text),
        "experience": extract_experience(cleaned_text),
        "projects": extract_projects(cleaned_text),
        "certifications": extract_certifications(cleaned_text)
    }

    parsed_resumes.append(resume_data)

# ----------------------------
# 6. Save JSON
# ----------------------------
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed_resumes, f, indent=4, ensure_ascii=False)

print(f"Smart parsing complete. {len(parsed_resumes)} resumes saved to {output_file}")
