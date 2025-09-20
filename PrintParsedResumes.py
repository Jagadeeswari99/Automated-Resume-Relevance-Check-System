import json
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# ----------------------------
# 1. Load parsed resumes JSON
# ----------------------------
parsed_file = r"C:\JAGA\innomatics hackathon\parsed_resumes_smart.json"

with open(parsed_file, "r", encoding="utf-8") as f:
    parsed_resumes = json.load(f)

# ----------------------------
# 2. Print each resume nicely
# ----------------------------
for resume in parsed_resumes:
    print(Fore.CYAN + "="*60)
    print(Fore.YELLOW + f"Resume: {resume['file_name']}")
    print(Fore.CYAN + "-"*60)
    
    # Sections to display
    sections = ["skills", "experience", "education", "projects", "certifications"]
    
    for section in sections:
        content = resume.get(section, [])
        if not content:
            print(Fore.RED + f"{section.capitalize()}: Not Found")
        else:
            print(Fore.GREEN + f"{section.capitalize()}:")
            for item in content:
                print(Fore.WHITE + f"  • {item}")
        print(Fore.CYAN + "-"*60)
    
print(Fore.CYAN + "="*60)
print(Fore.MAGENTA + f"Printed {len(parsed_resumes)} resumes successfully! Ready for hackathon demo!")
