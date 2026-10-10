import math
import re
from typing import Dict, Any, List, Tuple
from .extractor import extract_skills, extract_education_level, extract_experience_years

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def calculate_tfidf_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts using TF-IDF."""
    if not text1.strip() or not text2.strip():
        return 0.0
        
    if SKLEARN_AVAILABLE:
        try:
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words='english',
                token_pattern=r'(?u)\b\w+[\w\-+#]*\b'
            )
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(max(0.0, min(1.0, sim)))
        except Exception:
            pass

    # Fallback to Jaccard word similarity if TFIDF fails
    tokens1 = set(re.findall(r'\b[a-zA-Z0-9+#.-]+\b', text1.lower()))
    tokens2 = set(re.findall(r'\b[a-zA-Z0-9+#.-]+\b', text2.lower()))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    return float(intersection / union) if union > 0 else 0.0


def calculate_semantic_ngram_similarity(text1: str, text2: str) -> float:
    """
    Sub-word and token n-gram embedding similarity metric 
    for semantic relevance of technical requirements.
    """
    def get_char_ngrams(s: str, n: int = 3):
        s = re.sub(r'\s+', ' ', s.lower().strip())
        return {s[i:i+n] for i in range(len(s) - n + 1)}

    words1 = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower())]
    words2 = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower())]
    
    if not words1 or not words2:
        return 0.0

    # Soft matching for domain terms
    ngrams1 = get_char_ngrams(text1[:2000], 3)
    ngrams2 = get_char_ngrams(text2[:2000], 3)
    
    if not ngrams1 or not ngrams2:
        return 0.0

    overlap = len(ngrams1.intersection(ngrams2))
    semantic_score = (2.0 * overlap) / (len(ngrams1) + len(ngrams2))
    return float(max(0.0, min(1.0, semantic_score)))


def parse_job_requirements(job_description: str) -> Dict[str, Any]:
    """Extract required skills, expected years of exp, and min education from JD."""
    req_skills = extract_skills(job_description)
    exp_required = extract_experience_years(job_description)
    education_required = extract_education_level(job_description)
    
    return {
        "required_skills": req_skills,
        "required_experience_years": exp_required,
        "required_education": education_required["degree"],
        "required_education_rank": education_required["rank"]
    }


def compute_match_scores(
    resume_profile: Dict[str, Any],
    resume_text: str,
    job_description: str
) -> Dict[str, Any]:
    """
    Compute comprehensive match score breakdown:
    - Skills match (40%)
    - Semantic similarity (30%)
    - Experience match (15%)
    - Education match (15%)
    - Overall match score (0-100)
    """
    jd_reqs = parse_job_requirements(job_description)
    candidate_skills = set(resume_profile.get("skills", []))
    required_skills = set(jd_reqs["required_skills"])
    
    # 1. Skills match calculation
    if required_skills:
        matched_skills = sorted(list(candidate_skills.intersection(required_skills)))
        missing_skills = sorted(list(required_skills - candidate_skills))
        skills_score = len(matched_skills) / len(required_skills)
    else:
        # If no specific skills detected in JD, match based on general tech overlap
        matched_skills = sorted(list(candidate_skills))
        missing_skills = []
        skills_score = min(1.0, len(matched_skills) / 8.0)

    additional_skills = sorted(list(candidate_skills - required_skills))

    # 2. Semantic similarity calculation (hybrid TF-IDF + n-gram semantics)
    tfidf_sim = calculate_tfidf_similarity(resume_text, job_description)
    ngram_sim = calculate_semantic_ngram_similarity(resume_text, job_description)
    # Blend: 60% TF-IDF, 40% Semantic n-gram
    semantic_score = (tfidf_sim * 0.6) + (ngram_sim * 0.4)

    # 3. Experience match calculation
    req_exp = jd_reqs["required_experience_years"]
    cand_exp = resume_profile.get("experience_years", 1.0)
    if req_exp <= 1.0:
        exp_score = 1.0
    elif cand_exp >= req_exp:
        exp_score = 1.0
    else:
        exp_score = max(0.2, cand_exp / req_exp)

    # 4. Education match calculation
    req_edu_rank = jd_reqs["required_education_rank"]
    cand_edu_rank = resume_profile.get("education_rank", 2)
    if cand_edu_rank >= req_edu_rank:
        edu_score = 1.0
    elif cand_edu_rank == req_edu_rank - 1:
        edu_score = 0.8
    else:
        edu_score = 0.6

    # 5. Composite score calculation
    # Weights: Skills 40%, Semantic 30%, Experience 15%, Education 15%
    composite_raw = (
        (skills_score * 0.40) +
        (semantic_score * 0.30) +
        (exp_score * 0.15) +
        (edu_score * 0.15)
    )
    
    overall_percentage = round(composite_raw * 100, 1)
    # Clamp between 5 and 99
    overall_percentage = max(10.0, min(99.0, overall_percentage))

    # Match rating label
    if overall_percentage >= 80:
        verdict = "Strong Match"
        verdict_color = "emerald"
    elif overall_percentage >= 65:
        verdict = "Good Match"
        verdict_color = "teal"
    elif overall_percentage >= 50:
        verdict = "Moderate Match"
        verdict_color = "amber"
    else:
        verdict = "Low Match"
        verdict_color = "rose"

    return {
        "overall_score": overall_percentage,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "sub_scores": {
            "skills_match": round(skills_score * 100, 1),
            "semantic_similarity": round(semantic_score * 100, 1),
            "experience_match": round(exp_score * 100, 1),
            "education_match": round(edu_score * 100, 1)
        },
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "job_requirements": {
            "required_skills": jd_reqs["required_skills"],
            "required_experience_years": req_exp,
            "required_education": jd_reqs["required_education"]
        }
    }
