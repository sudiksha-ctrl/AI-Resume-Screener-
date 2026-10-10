from typing import List, Dict, Any

CAREER_ROLES = [
    {
        "role": "Python Backend Developer",
        "description": "Architects high-performance server-side APIs, microservices, and database layers.",
        "core_skills": ["Python", "FastAPI", "Flask", "Django", "SQL", "PostgreSQL", "Docker", "REST API", "Redis"],
        "min_skills_needed": 3
    },
    {
        "role": "Full Stack Developer",
        "description": "Bridges responsive client user interfaces with scalable backend microservices and databases.",
        "core_skills": ["React", "JavaScript", "TypeScript", "Node.js", "Express", "Python", "SQL", "MongoDB", "REST API", "Git"],
        "min_skills_needed": 3
    },
    {
        "role": "Machine Learning Engineer",
        "description": "Develops, tunes, and deploys predictive ML/DL models into production environments.",
        "core_skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas", "NumPy", "Docker"],
        "min_skills_needed": 3
    },
    {
        "role": "Cloud & DevOps Engineer",
        "description": "Automates CI/CD deployment pipelines, container orchestration, and cloud infrastructure.",
        "core_skills": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Git", "Linux", "Terraform"],
        "min_skills_needed": 2
    },
    {
        "role": "Frontend Web Developer",
        "description": "Specializes in modern reactive UI architecture, state management, and web performance.",
        "core_skills": ["React", "JavaScript", "TypeScript", "HTML5", "CSS3", "Tailwind CSS", "Next.js", "Redux", "Git"],
        "min_skills_needed": 3
    },
    {
        "role": "Data Analyst / BI Specialist",
        "description": "Transforms business data into actionable dashboards, KPIs, and statistical insights.",
        "core_skills": ["Python", "SQL", "Pandas", "NumPy", "Tableau", "Power BI", "Data Analysis", "MySQL", "PostgreSQL"],
        "min_skills_needed": 2
    },
    {
        "role": "AI / NLP Engineer",
        "description": "Implements modern NLP architectures, LLM fine-tuning, retrieval systems, and vector search.",
        "core_skills": ["Python", "NLP", "LLMs", "LangChain", "PyTorch", "Hugging Face", "Vector Databases", "Deep Learning"],
        "min_skills_needed": 2
    }
]


def recommend_career_roles(candidate_skills: List[str]) -> List[Dict[str, Any]]:
    """Recommend best fitting tech career tracks based on candidate skill set."""
    cand_skill_set = set(candidate_skills)
    recommendations = []
    
    for role_def in CAREER_ROLES:
        role_skills = set(role_def["core_skills"])
        matched = cand_skill_set.intersection(role_skills)
        missing = role_skills - cand_skill_set
        
        # Calculate role compatibility percentage
        match_percentage = round((len(matched) / len(role_skills)) * 100, 1)
        
        # Compatibility level badge
        if match_percentage >= 70:
            fit_level = "High Fit"
            color = "emerald"
        elif match_percentage >= 40:
            fit_level = "Moderate Fit"
            color = "amber"
        else:
            fit_level = "Growth Track"
            color = "slate"
            
        recommendations.append({
            "role": role_def["role"],
            "description": role_def["description"],
            "match_score": match_percentage,
            "fit_level": fit_level,
            "color": color,
            "matched_skills": sorted(list(matched)),
            "missing_skills": sorted(list(missing)),
            "core_skills": role_def["core_skills"]
        })
        
    # Sort descending by match score
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations
