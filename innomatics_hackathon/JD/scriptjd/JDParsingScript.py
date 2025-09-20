import os
import json
import re
import spacy

# ----------------------------
# 1. Paths
# ----------------------------
jd_folder = r"C:\JAGA\innomatics_hackathon\JD\dataJD" # Update if your JDs are elsewhere
output_file = r"C:\JAGA\innomatics_hackathon\JD\outcomes\parsed_jds.json"

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
    "communication", "leadership", "problem solving"
]

# ----------------------------
# 4. Helper functions
# ----------------------------
def clean_text(text):
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

def extract_title(text):
    # Try to find the first line as job title
    lines = text.split("\n")
    if lines:
        return lines[0].strip().title()
    return "Not Found"

def extract_skills(text):
    found_skills = [skill.title() for skill in SKILLS if skill.lower() in text]
    return list(set(found_skills))

def extract_must_have(text):
    # Look for lines with 'must have', 'required', 'mandatory'
    must_have = []
    lines = text.split("\n")
    for line in lines:
        if any(word in line.lower() for word in ["must have", "required", "mandatory"]):
            skills = extract_skills(line)
            must_have.extend(skills)
    return list(set(must_have))

def extract_nice_to_have(text):
    # Look for lines with 'nice to have', 'good to have', 'preferred'
    nice_to_have = []
    lines = text.split("\n")
    for line in lines:
        if any(word in line.lower() for word in ["nice to have", "good to have", "preferred"]):
            skills = extract_skills(line)
            nice_to_have.extend(skills)
    return list(set(nice_to_have))

# ----------------------------
# 5. Main Parsing
# ----------------------------
parsed_jds = []

for file_name in os.listdir(jd_folder):
    if not file_name.lower().endswith((".pdf", ".txt", ".docx")):
        continue
    
    file_path = os.path.join(jd_folder, file_name)
    
    # Extract text based on file type
    text = ""
    if file_name.lower().endswith(".pdf"):
        import fitz
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    elif file_name.lower().endswith(".docx"):
        import docx2txt
        text = docx2txt.process(file_path)
    else:  # txt file
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    
    cleaned_text = clean_text(text)
    
    jd_data = {
        "file_name": file_name,
        "job_title": extract_title(cleaned_text),
        "must_have_skills": extract_must_have(cleaned_text),
        "nice_to_have_skills": extract_nice_to_have(cleaned_text),
        "full_text": cleaned_text
    }
    
    parsed_jds.append(jd_data)

# ----------------------------
# 6. Save JSON
# ----------------------------
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed_jds, f, indent=4, ensure_ascii=False)

print(f"Job Description Parsing complete. {len(parsed_jds)} JDs saved to {output_file}")
