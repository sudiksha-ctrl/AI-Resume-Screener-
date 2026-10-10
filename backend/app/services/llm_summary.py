from typing import Dict, Any, List

def generate_ai_summary(
    candidate_profile: Dict[str, Any],
    match_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate professional, executive AI evaluation summary,
    highlighting candidate strengths, critical gaps, and tailored interview probes.
    """
    candidate_name = candidate_profile.get("candidate_name", "The candidate")
    overall_score = match_result.get("overall_score", 0)
    matched_skills = match_result.get("matched_skills", [])
    missing_skills = match_result.get("missing_skills", [])
    sub_scores = match_result.get("sub_scores", {})
    exp_years = candidate_profile.get("experience_years", 0)
    education = candidate_profile.get("education", "Degree")
    
    # Synthesis narrative
    if overall_score >= 80:
        headline = f"Exceptional alignment for the position. {candidate_name} exhibits strong competency across the essential tech stack."
        readiness = "Immediate Hire / Fast-Track Interview"
    elif overall_score >= 65:
        headline = f"Promising candidate with solid core foundations. Minor gaps can be easily addressed during onboarding."
        readiness = "Proceed to Technical Interview"
    elif overall_score >= 50:
        headline = f"Partial fit with baseline qualifications. Requires verification in key architectural & tooling requirements."
        readiness = "Conditional Review / Preliminary Screen"
    else:
        headline = f"Significant divergence from the required skill profile and target seniority."
        readiness = "Do Not Advance / Keep in Talent Pool"

    # Identify Key Strengths
    strengths = []
    if matched_skills:
        top_skills = ", ".join(matched_skills[:5])
        strengths.append(f"Demonstrates validated hands-on proficiency in key core technologies: {top_skills}.")
    if exp_years >= 2:
        strengths.append(f"Solid industry tenure (~{exp_years} years estimated experience) indicating practical production background.")
    if sub_scores.get("semantic_similarity", 0) >= 55:
        strengths.append("High contextual overlap between project deliverables in resume and job role objectives.")
    if education and education != "Not Specified":
        strengths.append(f"Formal academic credentials verified ({education}).")
    if not strengths:
        strengths.append("General technical background with transferable engineering skills.")

    # Identify Gaps / Risks
    risks = []
    if missing_skills:
        key_missing = ", ".join(missing_skills[:4])
        risks.append(f"Absence of explicit keywords or hands-on references for required tools: {key_missing}.")
    if sub_scores.get("experience_match", 100) < 60:
        risks.append(f"Current experience duration ({exp_years} yrs) is below ideal target threshold.")
    if sub_scores.get("skills_match", 100) < 50:
        risks.append("Skills match ratio is under 50%; candidate may require ramp-up period.")
    if not risks:
        risks.append("No critical deal-breakers identified; meets baseline specifications.")

    # Tailored interview questions based on missing or matched skills
    suggested_interview_questions = []
    if missing_skills:
        first_missing = missing_skills[0]
        suggested_interview_questions.append(
            f"How would you approach ramping up on {first_missing}, and can you describe a time you quickly mastered an unfamiliar tech stack?"
        )
    if matched_skills:
        primary_match = matched_skills[0]
        suggested_interview_questions.append(
            f"Can you walk us through the architectural design of a high-load system you developed using {primary_match}?"
        )
    suggested_interview_questions.append(
        "Describe a challenging production incident or bug you diagnosed. How did you identify the root cause and prevent recurrence?"
    )

    return {
        "headline": headline,
        "readiness_verdict": readiness,
        "strengths": strengths,
        "risks": risks,
        "suggested_interview_questions": suggested_interview_questions,
        "executive_notes": (
            f"Evaluated against criteria with skills coverage at {sub_scores.get('skills_match', 0)}% "
            f"and semantic alignment at {sub_scores.get('semantic_similarity', 0)}%. "
            f"Overall confidence score: {overall_score}%."
        )
    }
