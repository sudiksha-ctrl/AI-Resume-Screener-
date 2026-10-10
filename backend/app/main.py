import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import MatchRecord
from .parsers.resume_parser import parse_resume_file, clean_text
from .services.extractor import extract_candidate_profile
from .services.matching_engine import compute_match_scores
from .services.skill_gap import analyze_skill_gaps
from .services.recommender import recommend_career_roles
from .services.llm_summary import generate_ai_summary

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Screener API",
    description="Intelligent ATS Resume Parsing, Semantic Skill Matching, and Candidate Scoring Engine",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextMatchRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: Optional[str] = "Software Engineer"
    candidate_name: Optional[str] = None


@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "AI Resume Screener & ATS Matcher",
        "version": "1.0.0",
        "endpoints": [
            "/api/match/single",
            "/api/match/text",
            "/api/match/batch",
            "/api/sample",
            "/api/history"
        ]
    }


def process_screening(
    resume_text: str,
    job_description: str,
    filename: Optional[str] = None,
    job_title: Optional[str] = None,
    db: Optional[Session] = None
) -> dict:
    """Core screening pipeline function."""
    cleaned_resume = clean_text(resume_text)
    
    # 1. Profile & skill extraction
    parsed_meta = {
        "filename": filename or "Uploaded Resume",
        "raw_text": cleaned_resume,
        "word_count": len(cleaned_resume.split()),
        "sections": {}
    }
    profile = extract_candidate_profile(parsed_meta)
    
    # 2. Match calculation
    match_result = compute_match_scores(profile, cleaned_resume, job_description)
    
    # 3. Skill gap analysis
    skill_gaps = analyze_skill_gaps(match_result["missing_skills"])
    
    # 4. Career recommendations
    recommended_roles = recommend_career_roles(profile["skills"])
    
    # 5. Executive AI Evaluation summary
    ai_summary = generate_ai_summary(profile, match_result)
    
    # 6. Save record to DB if session provided
    record_id = None
    if db:
        record = MatchRecord(
            candidate_name=profile["candidate_name"],
            email=profile["email"],
            phone=profile["phone"],
            filename=filename or "Text Input",
            job_title=job_title or "Job Description Match",
            overall_score=match_result["overall_score"],
            verdict=match_result["verdict"],
            verdict_color=match_result["verdict_color"],
            sub_scores_json=json.dumps(match_result["sub_scores"]),
            matched_skills_json=json.dumps(match_result["matched_skills"]),
            missing_skills_json=json.dumps(match_result["missing_skills"]),
            ai_summary_json=json.dumps(ai_summary)
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id

    return {
        "record_id": record_id,
        "candidate_profile": profile,
        "match_result": match_result,
        "skill_gaps": skill_gaps,
        "recommended_roles": recommended_roles,
        "ai_summary": ai_summary
    }


@app.post("/api/match/single")
async def match_single_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_description: str = Form(...),
    job_title: Optional[str] = Form("Software Engineering Role"),
    db: Session = Depends(get_db)
):
    """
    Screen a single resume file (PDF, DOCX, TXT) or raw text against a job description.
    """
    text_to_process = ""
    filename = "Text Resume"
    
    if file:
        filename = file.filename
        content = await file.read()
        parsed = parse_resume_file(content, filename)
        text_to_process = parsed["raw_text"]
    elif resume_text:
        text_to_process = resume_text
    else:
        raise HTTPException(status_code=400, detail="Either a resume file or resume_text must be provided.")
        
    if not text_to_process.strip():
        raise HTTPException(status_code=400, detail="No readable text extracted from the provided resume.")

    return process_screening(
        resume_text=text_to_process,
        job_description=job_description,
        filename=filename,
        job_title=job_title,
        db=db
    )


@app.post("/api/match/text")
def match_text_json(
    request: TextMatchRequest,
    db: Session = Depends(get_db)
):
    """Screen raw text resume against a job description via JSON."""
    return process_screening(
        resume_text=request.resume_text,
        job_description=request.job_description,
        filename=request.candidate_name or "Direct Input",
        job_title=request.job_title,
        db=db
    )


@app.post("/api/match/batch")
async def match_batch_resumes(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...),
    job_title: Optional[str] = Form("Bulk Screening Position"),
    db: Session = Depends(get_db)
):
    """
    Screen multiple resumes simultaneously, returning an ATS Leaderboard ranking.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for batch screening.")
        
    results = []
    
    for f in files:
        try:
            content = await f.read()
            parsed = parse_resume_file(content, f.filename)
            text = parsed["raw_text"]
            if not text.strip():
                continue
                
            report = process_screening(
                resume_text=text,
                job_description=job_description,
                filename=f.filename,
                job_title=job_title,
                db=db
            )
            
            # Leaderboard card summary
            results.append({
                "record_id": report["record_id"],
                "filename": f.filename,
                "candidate_name": report["candidate_profile"]["candidate_name"],
                "email": report["candidate_profile"]["email"],
                "phone": report["candidate_profile"]["phone"],
                "experience_years": report["candidate_profile"]["experience_years"],
                "education": report["candidate_profile"]["education"],
                "overall_score": report["match_result"]["overall_score"],
                "verdict": report["match_result"]["verdict"],
                "verdict_color": report["match_result"]["verdict_color"],
                "sub_scores": report["match_result"]["sub_scores"],
                "matched_skills": report["match_result"]["matched_skills"],
                "missing_skills": report["match_result"]["missing_skills"],
                "headline": report["ai_summary"]["headline"],
                "full_report": report
            })
        except Exception as e:
            results.append({
                "filename": f.filename,
                "candidate_name": "Parsing Error",
                "overall_score": 0,
                "verdict": f"Error: {str(e)}",
                "verdict_color": "rose",
                "error": True
            })
            
    # Rank candidates by overall score descending
    results.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
    
    for rank_idx, item in enumerate(results, start=1):
        item["rank"] = rank_idx
        
    return {
        "job_title": job_title,
        "total_screened": len(files),
        "leaderboard": results
    }


@app.get("/api/sample")
def get_sample_data():
    """Returns curated ready-to-test sample resumes and industry job descriptions."""
    return {
        "sample_resumes": [
            {
                "id": "fullstack",
                "title": "Alex Morgan - Full Stack & Cloud Developer",
                "candidate_name": "Alex Morgan",
                "experience_years": 4,
                "education": "Bachelor's Degree in Computer Science",
                "text": """Alex Morgan
Email: alex.morgan.dev@gmail.com | Phone: +1 (555) 234-5678 | San Francisco, CA
LinkedIn: linkedin.com/in/alexmorgan-dev | GitHub: github.com/alexm-code

PROFESSIONAL SUMMARY
Dynamic Full-Stack Software Engineer with 4+ years of experience architecting resilient web applications, REST APIs, and microservices. Expert in React, Node.js, Python, PostgreSQL, and Docker container deployments with CI/CD.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3
Frameworks & Libraries: React, Node.js, Express, FastAPI, Tailwind CSS, Redux
Databases & Cloud: PostgreSQL, MongoDB, Redis, Docker, AWS (S3, EC2), Git, GitHub Actions, CI/CD
Methodologies: Agile, Scrum, REST API design, Microservices architecture

PROFESSIONAL EXPERIENCE
Senior Full Stack Engineer | CloudScale Systems | 2022 - Present
- Architected enterprise SaaS dashboard serving 150k+ monthly active users using React, TypeScript, and FastAPI.
- Migrated legacy monolith to Docker containerized microservices orchestrated via CI/CD, boosting deployment velocity by 40%.
- Designed optimized PostgreSQL schemas and integrated Redis caching, cutting average query latency by 55%.

Software Engineer | NexaTech Solutions | 2020 - 2022
- Built customer-facing e-commerce portals using React, Node.js, and MongoDB.
- Implemented JWT-based OAuth2 authentication and automated test suites with Jest and PyTest.
- Streamlined GitHub Actions pipelines for automated staging and production releases.

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley | 2016 - 2020
"""
            },
            {
                "id": "ml_engineer",
                "title": "Dr. Elena Rostova - Senior AI / Machine Learning Engineer",
                "candidate_name": "Dr. Elena Rostova",
                "experience_years": 5,
                "education": "Master's Degree in Artificial Intelligence",
                "text": """Dr. Elena Rostova
Email: elena.rostova.ai@outlook.com | Phone: +1 (415) 890-1234 | Boston, MA
GitHub: github.com/elena-ai-research

SUMMARY
Senior Machine Learning & NLP Specialist with 5 years of industry experience deploying deep learning models into production. Proficient in PyTorch, Scikit-Learn, Hugging Face transformers, Vector Databases, and Python microservices.

TECHNICAL SKILLS
Languages: Python, C++, SQL, R
AI / ML: PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, Deep Learning, NLP, Computer Vision, OpenCV, Hugging Face, LLMs
Data & Infrastructure: PostgreSQL, Docker, AWS, Git, Linux, REST API, Vector Databases

WORK EXPERIENCE
Lead Machine Learning Engineer | DeepData Labs | 2021 - Present
- Developed domain-specific LLM retrieval systems (RAG) using PyTorch, LangChain, and Vector Databases, improving answer relevance by 38%.
- Led engineering of Computer Vision inspection pipeline with OpenCV and PyTorch, achieving 98.4% detection accuracy.
- Containerized model inference endpoints using FastAPI and Docker, serving 2M daily inference requests on AWS.

Data Scientist & ML Developer | Cognitive Systems Corp | 2019 - 2021
- Built predictive customer churn classifiers using Scikit-Learn, Pandas, and XGBoost with AUC of 0.92.
- Cleaned and engineered multi-terabyte datasets using Python and SQL.

EDUCATION
Master of Science in Artificial Intelligence | Carnegie Mellon University | 2017 - 2019
Bachelor of Science in Data Science | Boston University | 2013 - 2017
"""
            },
            {
                "id": "devops_cloud",
                "title": "Marcus Chen - Cloud DevOps & Infrastructure Engineer",
                "candidate_name": "Marcus Chen",
                "experience_years": 6,
                "education": "Bachelor's Degree in Software Engineering",
                "text": """Marcus Chen
Email: marcus.chen.devops@proton.me | Phone: +1 (206) 456-7890 | Seattle, WA
LinkedIn: linkedin.com/in/marcus-clouddevops

PROFESSIONAL SUMMARY
DevOps & Cloud Infrastructure Architect with 6 years experience implementing automated infrastructure as code (IaC), container orchestration with Kubernetes & Docker, and multi-cloud AWS / GCP reliability engineering.

TECHNICAL SKILLS
Cloud & DevOps: Docker, Kubernetes, AWS, GCP, Terraform, Ansible, CI/CD, Jenkins, GitHub Actions, Linux, Nginx
Programming & Scripting: Python, Bash, Shell, Go, SQL
Observability & Databases: Prometheus, Grafana, PostgreSQL, Redis, Git

PROFESSIONAL EXPERIENCE
Staff DevOps Engineer | HighVelocity Cloud | 2021 - Present
- Architected multi-region Kubernetes clusters on AWS using Terraform and Helm, achieving 99.99% uptime SLA.
- Automated end-to-end CI/CD workflows using GitHub Actions and ArgoCD, slashing deployment rollback rates by 60%.
- Integrated centralized logging and alerts with Prometheus and Grafana for 100+ microservices.

Cloud Operations Engineer | Apex Cloud Solutions | 2018 - 2021
- Provisioned secure VPC networking, EC2, S3, RDS, and IAM policies adhering to SOC2 compliance standards.
- Scripted automated backup and disaster recovery mechanisms using Python and Bash.

EDUCATION
Bachelor of Science in Software Engineering | University of Washington | 2014 - 2018
"""
            }
        ],
        "sample_job_descriptions": [
            {
                "id": "senior_fullstack",
                "title": "Senior Full Stack Python & React Engineer",
                "company": "Fintech Global Innovations",
                "text": """Job Title: Senior Full Stack Software Engineer
Location: Remote / San Francisco, CA
Experience Required: 3+ years

Job Description:
We are seeking an experienced Full Stack Engineer to lead the development of our high-volume financial transaction platform.

Key Responsibilities:
- Design and implement scalable REST APIs and microservices using Python and FastAPI or Django.
- Build clean, reactive, and responsive frontend applications using React, TypeScript, and modern CSS (Tailwind CSS).
- Design and optimize relational database models in PostgreSQL and caching layers using Redis.
- Package and deploy applications inside Docker containers with continuous integration (CI/CD) pipelines on AWS.
- Collaborate in an Agile team with peer code reviews and automated testing (PyTest, Jest).

Required Technical Qualifications:
- 3+ years experience with Python and React (or modern JavaScript/TypeScript).
- Strong knowledge of SQL and relational databases like PostgreSQL.
- Hands-on experience with Docker, Git, and CI/CD automated deployment.
- Familiarity with cloud platforms (AWS or GCP).
- Bachelor's Degree in Computer Science or equivalent practical experience.
"""
            },
            {
                "id": "ai_ml_specialist",
                "title": "Senior AI / Machine Learning Engineer",
                "company": "NeuroTech AI Research",
                "text": """Job Title: Senior Machine Learning & AI Engineer
Location: Boston, MA / Hybrid
Experience Required: 4+ years

About the Role:
NeuroTech AI is looking for an exceptional Machine Learning Engineer to design and deploy generative AI, NLP, and computer vision models.

Key Requirements:
- 4+ years of hands-on Machine Learning and Deep Learning development in Python.
- Proven expertise in PyTorch or TensorFlow, Scikit-Learn, Pandas, and NumPy.
- Experience with Natural Language Processing (NLP), LLMs, Hugging Face, or Computer Vision.
- Containerization experience with Docker and model serving via REST APIs or FastAPI.
- Familiarity with Vector Databases and AWS cloud infrastructure.
- Master's or Bachelor's Degree in Computer Science, Data Science, or related field.
"""
            },
            {
                "id": "cloud_devops_lead",
                "title": "Cloud & DevOps Infrastructure Engineer",
                "company": "ScalePlatform Inc.",
                "text": """Job Title: Cloud & DevOps Infrastructure Engineer
Location: Seattle, WA / Remote
Experience Required: 4+ years

Responsibilities:
- Build and maintain multi-region Kubernetes clusters and container workloads.
- Automate cloud infrastructure using Terraform, Ansible, and AWS or GCP.
- Implement robust CI/CD deployment pipelines using GitHub Actions or Jenkins.
- Manage Linux server configuration, Nginx proxies, and Docker environments.
- Ensure security best practices, IAM roles, and disaster recovery.
"""
            }
        ]
    }


@app.get("/api/history")
def get_match_history(limit: int = Query(20, le=100), db: Session = Depends(get_db)):
    """Fetch recent resume screening records from SQLite."""
    records = db.query(MatchRecord).order_by(MatchRecord.created_at.desc()).limit(limit).all()
    return {
        "count": len(records),
        "history": [r.to_dict() for r in records]
    }


@app.delete("/api/history")
def clear_match_history(db: Session = Depends(get_db)):
    """Clear screening history records."""
    db.query(MatchRecord).delete()
    db.commit()
    return {"message": "Screening history cleared successfully."}
