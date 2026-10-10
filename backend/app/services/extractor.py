import re
from typing import List, Dict, Any, Optional

# Comprehensive tech skills dictionary categorized
TECH_SKILLS = [
    # Programming Languages
    "Python", "Java", "C++", "C#", "C", "Go", "Golang", "Rust", "TypeScript", 
    "JavaScript", "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "Dart", "Bash", "Shell",
    
    # Web & Frontend
    "React", "React.js", "Next.js", "Vue", "Vue.js", "Angular", "Svelte", 
    "HTML5", "HTML", "CSS3", "CSS", "Tailwind CSS", "Bootstrap", "Redux", "Webpack", "Vite",
    
    # Backend & Frameworks
    "Node.js", "Express", "Express.js", "FastAPI", "Flask", "Django", "Spring Boot", 
    "Spring", "ASP.NET", ".NET", "Ruby on Rails", "NestJS", "REST API", "RESTful APIs", "GraphQL", "gRPC", "WebSockets",
    
    # Databases & Caching
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle", 
    "Elasticsearch", "Cassandra", "DynamoDB", "Firebase", "Supabase", "Prisma",
    
    # Cloud & DevOps
    "Docker", "Kubernetes", "AWS", "Amazon Web Services", "Azure", "GCP", 
    "Google Cloud", "Git", "GitHub", "GitLab", "CI/CD", "Jenkins", "Terraform", 
    "Ansible", "Linux", "Nginx", "Apache", "Kafka", "RabbitMQ", "Microservices",
    
    # AI / ML & Data Science
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing", 
    "Computer Vision", "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", "Pandas", 
    "NumPy", "OpenCV", "Hugging Face", "LLMs", "LangChain", "Vector Databases", 
    "Matplotlib", "Seaborn", "Data Analysis", "Tableau", "Power BI",
    
    # Testing & Tools
    "Jest", "PyTest", "Cypress", "Selenium", "Postman", "Swagger", "Jira", "Agile", "Scrum"
]

# Canonical mapping to normalize skill aliases
SKILL_CANONICAL = {
    "react.js": "React",
    "vue.js": "Vue",
    "express.js": "Express",
    "golang": "Go",
    "amazon web services": "AWS",
    "google cloud": "GCP",
    "natural language processing": "NLP",
    "llms": "Large Language Models",
    "restful apis": "REST API",
}


def build_skill_patterns():
    patterns = []
    for skill in TECH_SKILLS:
        # Escape special regex characters in skill name (like C++, C#, .NET, CI/CD)
        escaped = re.escape(skill)
        # Handle word boundaries safely for symbols like ++ or #
        pattern = rf"(?<!\w){escaped}(?!\w)"
        patterns.append((re.compile(pattern, re.IGNORECASE), skill))
    return patterns

SKILL_PATTERNS = build_skill_patterns()


def extract_email(text: str) -> Optional[str]:
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    # Matches international and standard US/India phone formats
    phone_pattern = r'(?:\+?\d{1,3}[\s-]?)?\(?\d{3,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,5}'
    matches = re.finditer(phone_pattern, text)
    for match in matches:
        cand = match.group(0).strip()
        # Filter out common false positives like years or numbers
        digits_only = re.sub(r'\D', '', cand)
        if 10 <= len(digits_only) <= 13:
            return cand
    return None


def extract_name(text: str, filename: Optional[str] = None) -> str:
    """Extract candidate name from top lines or filename."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # Check top 5 non-empty lines for candidate name
    for line in lines[:5]:
        # Exclude lines that look like emails, URLs, or headers
        if "@" in line or "http" in line or "linkedin" in line or "github" in line:
            continue
        if len(line.split()) in [2, 3, 4] and not any(char.isdigit() for char in line):
            # Exclude lines containing common section headers
            lower = line.lower()
            if any(w in lower for w in ["resume", "curriculum", "vitae", "summary", "profile", "developer", "engineer"]):
                continue
            return line
            
    # Fallback to filename if available
    if filename:
        clean_name = re.sub(r'(\.pdf|\.docx|\.txt|_resume|-resume|resume)', '', filename, flags=re.IGNORECASE)
        clean_name = re.sub(r'[-_]', ' ', clean_name).strip()
        if clean_name:
            return clean_name.title()

    return "Candidate"


def extract_education_level(text: str) -> Dict[str, Any]:
    """Detect highest education qualification."""
    text_lower = text.lower()
    
    degrees = [
        {"level": "Doctorate / Ph.D.", "regex": r"\b(ph\.?d\.?|doctorate|doctoral)\b", "weight": 5},
        {"level": "Master's Degree", "regex": r"\b(master'?s?|m\.?s\.?|m\.?tech|m\.?e\.?|mca|mba)\b", "weight": 4},
        {"level": "Bachelor's Degree", "regex": r"\b(bachelor'?s?|b\.?s\.?|b\.?tech|b\.?e\.?|bca|b\.?sc|undergraduate)\b", "weight": 3},
        {"level": "Associate Degree", "regex": r"\b(associate'?s?|diploma)\b", "weight": 2},
        {"level": "High School", "regex": r"\b(high school|secondary|12th)\b", "weight": 1}
    ]
    
    for deg in degrees:
        if re.search(deg["regex"], text_lower):
            return {"degree": deg["level"], "rank": deg["weight"]}
            
    return {"degree": "Not Specified", "rank": 2}


def extract_experience_years(text: str) -> float:
    """Estimate total years of professional experience."""
    text_lower = text.lower()
    
    # Pattern 1: explicit mention "X years of experience"
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', text_lower)
    if exp_matches:
        try:
            return float(exp_matches[0])
        except ValueError:
            pass

    # Pattern 2: Year ranges like 2018 - 2023, 2020 - Present
    year_ranges = re.findall(r'(20\d\d|19\d\d)\s*(?:-|–|to)\s*(20\d\d|present|current)', text_lower)
    total_span = 0
    import datetime
    current_year = datetime.datetime.now().year
    
    for start, end in year_ranges:
        try:
            s = int(start)
            e = current_year if end in ["present", "current"] else int(end)
            if 1990 <= s <= e <= current_year + 1:
                diff = e - s
                if diff > 0 and diff < 30:
                    total_span = max(total_span, diff)
        except ValueError:
            continue
            
    if total_span > 0:
        return float(total_span)
        
    return 1.0  # default entry baseline


def extract_skills(text: str) -> List[str]:
    """Extract list of technical skills present in text."""
    found_skills = set()
    for pattern, skill in SKILL_PATTERNS:
        if pattern.search(text):
            canonical = SKILL_CANONICAL.get(skill.lower(), skill)
            found_skills.add(canonical)
            
    return sorted(list(found_skills))


def extract_candidate_profile(parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
    """Complete candidate profile extraction."""
    text = parsed_resume.get("raw_text", "")
    filename = parsed_resume.get("filename", "")
    
    name = extract_name(text, filename)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    education = extract_education_level(text)
    experience_years = extract_experience_years(text)
    
    return {
        "candidate_name": name,
        "email": email or "Not Found",
        "phone": phone or "Not Found",
        "skills": skills,
        "skills_count": len(skills),
        "education": education["degree"],
        "education_rank": education["rank"],
        "experience_years": experience_years,
        "word_count": parsed_resume.get("word_count", 0),
        "sections_detected": list(parsed_resume.get("sections", {}).keys())
    }
