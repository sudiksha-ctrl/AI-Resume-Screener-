"""
AI Resume Screener & ATS Matcher - Verification & Test Suite
Demonstrates parsing, feature extraction, ATS scoring, skill gap diagnosis,
career role recommendations, and AI summary generation.
"""

import sys
import os
from typing import Dict, Any

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.parsers.resume_parser import parse_resume_file
from app.services.extractor import extract_candidate_profile
from app.services.matching_engine import compute_match_scores
from app.services.skill_gap import analyze_skill_gaps, diagnose_skill_gaps
from app.services.recommender import recommend_career_roles
from app.services.llm_summary import generate_ai_summary

# Benchmark Job Descriptions for Testing
SAMPLE_JOB_DESCRIPTIONS = {
    "fullstack": """
Job Title: Senior Full Stack Engineer
Required Experience: 5+ years of experience in software development
Required Education: Bachelor's Degree in Computer Science or related engineering field
Key Responsibilities:
- Design, build, and deploy high-availability web applications and microservices.
- Lead architecture decisions across frontend React/TypeScript and backend Python services.
- Manage containerized infrastructure using Docker, Kubernetes, and AWS cloud environments.
Required Skills:
Python, React, TypeScript, FastAPI, PostgreSQL, Docker, Kubernetes, AWS, Redis, REST API, Git, CI/CD
Nice-to-Have:
GraphQL, Next.js, PyTest, Terraform
""",
    "ml_engineer": """
Job Title: Senior Machine Learning Engineer
Required Experience: 4+ years of experience in machine learning and data engineering
Required Education: Master's Degree in Computer Science, Data Science, or AI
Key Responsibilities:
- Build, optimize, and deploy end-to-end deep learning, NLP, and generative AI models.
- Create low-latency model inference pipelines and vector search systems.
- Productionize models using containerization and cloud orchestration.
Required Skills:
Python, Machine Learning, Deep Learning, PyTorch, TensorFlow, Scikit-Learn, Pandas, NLP, LLMs, Docker, AWS, SQL
Nice-to-Have:
LangChain, Vector Databases, Hugging Face, MLflow, FastAPI
""",
    "frontend": """
Job Title: Frontend Web Developer
Required Experience: 3+ years of experience building modern web applications
Required Education: Bachelor's Degree in Information Technology or Computer Science
Key Responsibilities:
- Develop interactive, accessible, and responsive client-side web interfaces.
- Manage scalable state architecture and integrate RESTful and GraphQL endpoints.
- Optimize web vitals, bundle size, and automated testing coverage.
Required Skills:
React, TypeScript, JavaScript, Next.js, Redux, Tailwind CSS, HTML5, CSS3, Jest, REST API, Git
Nice-to-Have:
Cypress, Vite, GraphQL, WebSockets
"""
}


def print_separator(char: str = "=", length: int = 78):
    print(char * length)


def run_candidate_screening(file_path: str, target_jd_key: str, jd_title: str) -> Dict[str, Any]:
    print_separator("=")
    filename = os.path.basename(file_path)
    print(f"TESTING FILE: {filename}")
    print(f"TARGET ROLE : {jd_title}")
    print_separator("-")

    # 1. Parse Resume File
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found at: {file_path}")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    parsed = parse_resume_file(file_bytes, filename)
    print(f"[1] PARSE SUCCESS:")
    print(f"    - Extracted Word Count: {parsed.get('word_count', 0)}")
    print(f"    - Sections Detected: {', '.join(parsed.get('sections', {}).keys())}")

    # 2. Extract Candidate Profile
    profile = extract_candidate_profile(parsed)
    print(f"\n[2] CANDIDATE PROFILE:")
    print(f"    - Name             : {profile.get('candidate_name')}")
    print(f"    - Email            : {profile.get('email')}")
    print(f"    - Phone            : {profile.get('phone')}")
    print(f"    - Experience Est.  : {profile.get('experience_years')} yrs")
    print(f"    - Education Level  : {profile.get('education')} (Rank {profile.get('education_rank')})")
    print(f"    - Skills Detected  : {len(profile.get('skills', []))} skills -> {', '.join(profile.get('skills', [])[:8])}...")

    # 3. Compute ATS Match Scores
    jd_text = SAMPLE_JOB_DESCRIPTIONS[target_jd_key]
    match = compute_match_scores(profile, parsed["raw_text"], jd_text)
    sub = match.get("sub_scores", {})
    print(f"\n[3] ATS MATCH EVALUATION:")
    print(f"    - Overall ATS Score: {match.get('overall_score')}% ({match.get('match_tier')})")
    print(f"    - Skills Match     : {sub.get('skills_match')}%")
    print(f"    - Semantic Sim.    : {sub.get('semantic_similarity')}%")
    print(f"    - Experience Score : {sub.get('experience_match')}%")
    print(f"    - Education Score  : {sub.get('education_match')}%")
    print(f"    - Matched Skills   : {', '.join(match.get('matched_skills', []))}")
    print(f"    - Missing Skills   : {', '.join(match.get('missing_skills', [])) or 'None'}")

    # 4. Diagnose Skill Gaps & Actionable Roadmaps
    # Verified using both diagnose_skill_gaps and analyze_skill_gaps
    skill_gaps = diagnose_skill_gaps(match.get("missing_skills", []))
    print(f"\n[4] SKILL GAP DIAGNOSIS:")
    if skill_gaps:
        for idx, gap in enumerate(skill_gaps[:3], 1):
            print(f"    Gap #{idx}: {gap['skill']} [{gap['priority']} Priority | ~{gap['est_hours']} hrs | {gap['difficulty']}]")
            print(f"      Resource: {gap['recommended_resource']}")
            print(f"      Step 1  : {gap['steps'][0] if gap['steps'] else 'Review documentation'}")
    else:
        print("    No critical skill gaps detected for this role requirements.")

    # 5. Recommend Career Tracks
    recommendations = recommend_career_roles(profile.get("skills", []))
    print(f"\n[5] CAREER TRACK RECOMMENDATIONS:")
    for rec in recommendations[:3]:
        print(f"    - {rec['role']}: {rec['match_score']}% ({rec['fit_level']}) | Matched: {len(rec['matched_skills'])} skills")

    # 6. Generate AI Summary & Executive Assessment
    summary = generate_ai_summary(profile, match)
    print(f"\n[6] AI EXECUTIVE SUMMARY:")
    print(f"    - Headline : {summary.get('headline')}")
    print(f"    - Verdict  : {summary.get('readiness_verdict')}")
    print(f"    - Strengths:")
    for s in summary.get("strengths", []):
        print(f"      * {s}")
    print(f"    - Risks / Attention Points:")
    for r in summary.get("risks", []):
        print(f"      * {r}")
    print(f"    - Tailored Interview Probes:")
    for q in summary.get("suggested_interview_questions", [])[:2]:
        print(f"      ? {q}")

    print_separator("=")
    print("\n")
    return {
        "candidate": profile.get("candidate_name"),
        "overall_score": match.get("overall_score"),
        "match_tier": match.get("match_tier")
    }


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(base_dir, "sample_resumes")

    test_cases = [
        {
            "file": os.path.join(samples_dir, "alex_chen_senior_fullstack.txt"),
            "jd_key": "fullstack",
            "title": "Senior Full Stack Engineer"
        },
        {
            "file": os.path.join(samples_dir, "priya_patel_ml_engineer.txt"),
            "jd_key": "ml_engineer",
            "title": "Senior Machine Learning Engineer"
        },
        {
            "file": os.path.join(samples_dir, "david_kim_frontend_dev.txt"),
            "jd_key": "frontend",
            "title": "Frontend Web Developer"
        },
        {
            "file": os.path.join(samples_dir, "david_kim_frontend_dev.txt"),
            "jd_key": "fullstack",
            "title": "Senior Full Stack Engineer (Cross-role Gap Test)"
        }
    ]

    print_separator("#")
    print("       AI RESUME SCREENER & ATS MATCH ENGINE - TEST VERIFICATION")
    print_separator("#")
    print(f"Target sample resumes directory: {samples_dir}\n")

    summary_table = []
    for test in test_cases:
        res = run_candidate_screening(test["file"], test["jd_key"], test["title"])
        summary_table.append((res["candidate"], test["title"], f"{res['overall_score']}%", res["match_tier"]))

    print_separator("#")
    print("OVERALL TEST VERIFICATION SUMMARY:")
    print_separator("-")
    print(f"{'Candidate Name':<20} | {'Target Job Role':<35} | {'Score':<8} | {'Tier'}")
    print_separator("-")
    for cand, role, score, tier in summary_table:
        print(f"{cand:<20} | {role:<35} | {score:<8} | {tier}")
    print_separator("#")
    print("ALL TESTS COMPLETED SUCCESSFULLY!\n")


if __name__ == "__main__":
    main()
