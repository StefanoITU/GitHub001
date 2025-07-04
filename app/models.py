from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List
from datetime import datetime
import json

class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str = "DKK"
    job_type: Optional[str] = None
    remote_ok: bool = False
    url: str
    source: str
    posted_date: Optional[datetime] = None
    ai_keywords: Optional[str] = None
    relevance_score: float = 0.0
    
    @validator('ai_keywords')
    def validate_ai_keywords(cls, v):
        if v is not None and isinstance(v, list):
            return json.dumps(v)
        return v

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    scraped_date: datetime
    is_active: bool
    
    @validator('ai_keywords')
    def parse_ai_keywords(cls, v):
        if v is not None and isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v or []
    
    class Config:
        from_attributes = True

class JobStats(BaseModel):
    total_jobs: int
    active_jobs: int
    jobs_today: int
    jobs_this_week: int
    top_companies: List[dict]
    top_locations: List[dict]
    job_types: List[dict]
    sources: List[dict]

class ScrapeRequest(BaseModel):
    sources: Optional[List[str]] = None  # Specific sources to scrape
    force_refresh: bool = False  # Force refresh even if recently scraped

class ScrapeResponse(BaseModel):
    message: str
    jobs_found: int
    sources_scraped: List[str]
    timestamp: datetime