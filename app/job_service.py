from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import json
import logging

from .database import get_db_session, Job
from .models import JobCreate, JobResponse, JobStats

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self):
        self.ai_keywords = [
            "artificial intelligence", "ai", "machine learning", "ml", "deep learning",
            "neural network", "nlp", "natural language processing", "computer vision",
            "generative ai", "gpt", "llm", "large language model", "prompt engineering",
            "ai trainer", "ai consultant", "ai mentor", "ai project lead", "ai curator",
            "data scientist", "ml engineer", "ai researcher", "chatbot", "automation",
            "tensorflow", "pytorch", "hugging face", "openai", "anthropic", "claude",
            "stable diffusion", "diffusion model", "transformer", "bert", "reinforcement learning"
        ]
        
        self.danish_locations = [
            "denmark", "danmark", "copenhagen", "københavn", "aarhus", "aalborg", 
            "odense", "esbjerg", "randers", "kolding", "horsens", "vejle", "roskilde",
            "helsingør", "herning", "silkeborg", "næstved", "fredericia", "viborg",
            "køge", "holstebro", "taastrup", "slagelse", "hillerød", "sønderborg",
            "danish", "dansk", "remote denmark", "hybrid denmark"
        ]
    
    def calculate_relevance_score(self, title: str, description: str, requirements: str) -> tuple[float, List[str]]:
        """Calculate AI relevance score and extract matching keywords"""
        text = f"{title} {description} {requirements}".lower()
        matched_keywords = []
        score = 0.0
        
        for keyword in self.ai_keywords:
            if keyword.lower() in text:
                matched_keywords.append(keyword)
                # Weight different keywords differently
                if keyword.lower() in ["ai trainer", "ai consultant", "ai mentor", "ai project lead", "ai curator"]:
                    score += 0.2
                elif keyword.lower() in ["artificial intelligence", "ai", "generative ai"]:
                    score += 0.15
                elif keyword.lower() in ["machine learning", "ml", "deep learning"]:
                    score += 0.1
                else:
                    score += 0.05
        
        # Bonus for title matches
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["ai", "artificial intelligence", "machine learning"]):
            score += 0.1
            
        return min(score, 1.0), matched_keywords
    
    def is_danish_job(self, location: str, company: str, description: str) -> bool:
        """Check if job is Danish/Denmark-based"""
        if not location:
            return False
            
        text = f"{location} {company} {description}".lower()
        return any(danish_loc in text for danish_loc in self.danish_locations)
    
    async def create_job(self, job_data: JobCreate) -> Optional[JobResponse]:
        """Create a new job with AI scoring"""
        db = get_db_session()
        try:
            # Check if job already exists
            existing_job = db.query(Job).filter(Job.url == job_data.url).first()
            if existing_job:
                logger.info(f"Job already exists: {job_data.url}")
                return None
            
            # Calculate AI relevance score
            description = job_data.description or ""
            requirements = job_data.requirements or ""
            
            relevance_score, matched_keywords = self.calculate_relevance_score(
                job_data.title, description, requirements
            )
            
            # Check if it's a Danish job
            is_danish = self.is_danish_job(
                job_data.location or "", 
                job_data.company, 
                description
            )
            
            # Only save jobs that are relevant and Danish
            if relevance_score < 0.1 or not is_danish:
                logger.info(f"Skipping job due to low relevance or non-Danish: {job_data.title}")
                return None
            
            # Create job instance
            job = Job(
                title=job_data.title,
                company=job_data.company,
                location=job_data.location,
                description=job_data.description,
                requirements=job_data.requirements,
                salary_min=job_data.salary_min,
                salary_max=job_data.salary_max,
                currency=job_data.currency,
                job_type=job_data.job_type,
                remote_ok=job_data.remote_ok,
                url=job_data.url,
                source=job_data.source,
                posted_date=job_data.posted_date,
                ai_keywords=json.dumps(matched_keywords),
                relevance_score=relevance_score
            )
            
            db.add(job)
            db.commit()
            db.refresh(job)
            
            logger.info(f"Created job: {job.title} at {job.company}")
            return JobResponse.from_orm(job)
            
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    async def get_jobs(
        self, 
        limit: int = 50, 
        offset: int = 0,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        days_ago: Optional[int] = 30
    ) -> List[JobResponse]:
        """Get paginated list of jobs with filters"""
        db = get_db_session()
        try:
            query = db.query(Job).filter(Job.is_active == True)
            
            # Date filter
            if days_ago:
                date_threshold = datetime.utcnow() - timedelta(days=days_ago)
                query = query.filter(Job.scraped_date >= date_threshold)
            
            # Location filter
            if location:
                query = query.filter(Job.location.ilike(f"%{location}%"))
            
            # Job type filter
            if job_type:
                query = query.filter(Job.job_type.ilike(f"%{job_type}%"))
            
            # Order by relevance score and date
            query = query.order_by(desc(Job.relevance_score), desc(Job.scraped_date))
            
            # Apply pagination
            jobs = query.offset(offset).limit(limit).all()
            
            return [JobResponse.from_orm(job) for job in jobs]
            
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            return []
        finally:
            db.close()
    
    async def get_job_stats(self) -> JobStats:
        """Get job statistics"""
        db = get_db_session()
        try:
            # Basic counts
            total_jobs = db.query(Job).count()
            active_jobs = db.query(Job).filter(Job.is_active == True).count()
            
            today = datetime.utcnow().date()
            jobs_today = db.query(Job).filter(
                func.date(Job.scraped_date) == today
            ).count()
            
            week_ago = datetime.utcnow() - timedelta(days=7)
            jobs_this_week = db.query(Job).filter(
                Job.scraped_date >= week_ago
            ).count()
            
            # Top companies
            top_companies = db.query(
                Job.company,
                func.count(Job.id).label('count')
            ).filter(Job.is_active == True).group_by(Job.company).order_by(
                desc('count')
            ).limit(10).all()
            
            # Top locations
            top_locations = db.query(
                Job.location,
                func.count(Job.id).label('count')
            ).filter(
                and_(Job.is_active == True, Job.location.isnot(None))
            ).group_by(Job.location).order_by(
                desc('count')
            ).limit(10).all()
            
            # Job types
            job_types = db.query(
                Job.job_type,
                func.count(Job.id).label('count')
            ).filter(
                and_(Job.is_active == True, Job.job_type.isnot(None))
            ).group_by(Job.job_type).order_by(
                desc('count')
            ).limit(10).all()
            
            # Sources
            sources = db.query(
                Job.source,
                func.count(Job.id).label('count')
            ).filter(Job.is_active == True).group_by(Job.source).order_by(
                desc('count')
            ).all()
            
            return JobStats(
                total_jobs=total_jobs,
                active_jobs=active_jobs,
                jobs_today=jobs_today,
                jobs_this_week=jobs_this_week,
                top_companies=[{"name": company, "count": count} for company, count in top_companies],
                top_locations=[{"name": location, "count": count} for location, count in top_locations],
                job_types=[{"name": job_type, "count": count} for job_type, count in job_types],
                sources=[{"name": source, "count": count} for source, count in sources]
            )
            
        except Exception as e:
            logger.error(f"Error fetching job stats: {e}")
            return JobStats(
                total_jobs=0, active_jobs=0, jobs_today=0, jobs_this_week=0,
                top_companies=[], top_locations=[], job_types=[], sources=[]
            )
        finally:
            db.close()
    
    async def delete_job(self, job_id: int) -> bool:
        """Delete a job"""
        db = get_db_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                db.delete(job)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting job: {e}")
            db.rollback()
            return False
        finally:
            db.close()