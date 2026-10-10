import datetime
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .database import Base

class MatchRecord(Base):
    __tablename__ = "match_records"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    candidate_name = Column(String(120), default="Unknown")
    email = Column(String(120), nullable=True)
    phone = Column(String(60), nullable=True)
    filename = Column(String(255), nullable=True)
    job_title = Column(String(255), default="General Job Description")
    overall_score = Column(Float, default=0.0)
    verdict = Column(String(60), default="Moderate Match")
    verdict_color = Column(String(30), default="teal")
    
    # Serialized JSON fields
    sub_scores_json = Column(Text, default="{}")
    matched_skills_json = Column(Text, default="[]")
    missing_skills_json = Column(Text, default="[]")
    ai_summary_json = Column(Text, default="{}")

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "candidate_name": self.candidate_name,
            "email": self.email,
            "phone": self.phone,
            "filename": self.filename,
            "job_title": self.job_title,
            "overall_score": self.overall_score,
            "verdict": self.verdict,
            "verdict_color": self.verdict_color,
            "sub_scores": json.loads(self.sub_scores_json) if self.sub_scores_json else {},
            "matched_skills": json.loads(self.matched_skills_json) if self.matched_skills_json else [],
            "missing_skills": json.loads(self.missing_skills_json) if self.missing_skills_json else [],
            "ai_summary": json.loads(self.ai_summary_json) if self.ai_summary_json else {}
        }
