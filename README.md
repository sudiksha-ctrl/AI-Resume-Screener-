# AI Resume Screener & ATS Candidate Ranking Platform

An intelligent, full-stack **Applicant Tracking System (ATS)** and automated resume screener. Built with FastAPI, scikit-learn, and React, it analyzes resumes against job descriptions using **semantic token matching**, **TF-IDF cosine similarity**, **skill ontology boundary extraction**, and a **weighted composite scoring engine**.

---

## 🚀 Key Highlights & Features

- **Multi-Format Ingestion**: Parses `.pdf` (PyMuPDF / fitz), `.docx` (python-docx), and `.txt` files with automated text normalization and section segmentation.
- **Entity & Profile Extraction**: Extracts candidate name, email, phone number, estimated years of professional experience, and academic degree hierarchy.
- **Comprehensive Tech Skill Ontology**: Automated boundary detection for 70+ technical skills (languages, frameworks, databases, cloud, DevOps, AI/ML tools).
- **Composite ATS Matching Engine (0 - 100%)**:
  - **40% Skills Coverage**: Ratio of candidate skills satisfying job requirements.
  - **30% Semantic Similarity**: Hybrid TF-IDF vector cosine distance + sub-word character n-gram relevance.
  - **15% Experience Match**: Scaled tenure matching against minimum required years.
  - **15% Education Alignment**: Hierarchical degree rank matching (Ph.D., Master's, Bachelor's, Associate).
- **Actionable Skill Gap Roadmaps**: Identifies missing core technologies and generates custom learning paths with step-by-step topics, estimated hours, and curated resources.
- **Recruiter Batch Screener & Leaderboard**: Bulk-upload candidate resumes for a job opening to instantly generate an ATS-ranked leaderboard table.
- **Career Role Explorer**: Evaluates candidate competencies across standard industry career tracks (Python Backend, ML Engineer, DevOps, Full Stack, Frontend, Data Analyst).
- **Executive AI Evaluation Synthesis**: Generates hiring recommendations, key strengths, identified risks, and customized interview probing questions.
- **SQLite Persistence**: Automatically logs screening records, matched profiles, and breakdown sub-scores.

---

## 🏗️ Architecture

```
ai-resume-screener/
│
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── database.py              # SQLite session & engine setup
│       ├── models.py                # MatchRecord table model
│       ├── main.py                  # FastAPI REST API endpoints
│       ├── parsers/
│       │   ├── __init__.py
│       │   └── resume_parser.py     # PDF, DOCX, TXT parsers & section extractors
│       └── services/
│           ├── __init__.py
│           ├── extractor.py         # Contact, experience, degree & skill extraction
│           ├── matching_engine.py   # TF-IDF, semantic cosine similarity & composite scoring
│           ├── skill_gap.py         # Missing skill diagnosis & learning roadmaps
│           ├── recommender.py       # Career track compatibility calculator
│           └── llm_summary.py       # Executive match summary & interview questions
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── index.css                # Dark mode styles, badges & custom scrollbars
│       └── App.jsx                  # Single screener, batch leaderboard & role explorer
│
├── run_backend.bat                  # 1-click backend launcher
├── run_frontend.bat                 # 1-click frontend launcher
├── run_platform.bat                 # 1-click dual platform launcher
└── README.md
```

---

## 📊 Composite Scoring Formula

$$\text{Overall Score} = (0.40 \times \text{Skills Match}) + (0.30 \times \text{Semantic Sim}) + (0.15 \times \text{Exp Match}) + (0.15 \times \text{Edu Match})$$

- **Strong Match** $\ge 80\%$ (Emerald badge)
- **Good Match** $\ge 65\%$ (Teal badge)
- **Moderate Match** $\ge 50\%$ (Amber badge)
- **Low Match** $< 50\%$ (Rose badge)

---

## 🛠️ Quick Start Guide

### 1. Run via Batch Launchers (Windows)
Double-click `run_platform.bat` to launch both servers, or run individually:
- **Backend**: Double-click `run_backend.bat` (Runs on `http://127.0.0.1:8000`)
- **Frontend**: Double-click `run_frontend.bat` (Runs on `http://localhost:5173`)

### 2. Manual Terminal Commands

#### Backend:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 💼 Resume Bullet Points for Portfolios

- *Architected an automated AI Resume Screener & ATS platform using FastAPI, scikit-learn, and React, parsing PDF/DOCX resumes and scoring alignment via TF-IDF cosine similarity and regex skill extraction.*
- *Engineered a 4-tier composite evaluation algorithm weighting technical skills (40%), contextual semantic similarity (30%), tenure (15%), and degree hierarchy (15%).*
- *Designed a bulk candidate screening pipeline capable of processing multi-resume batches with sub-second ranking and candidate leaderboard generation.*
- *Implemented automated skill gap diagnostics delivering step-by-step learning roadmaps and executive hiring summaries for recruiters.*
