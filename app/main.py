from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
import logging
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

from .database import create_tables, get_db
from .models import JobResponse, JobCreate
from .scrapers import JobScraper
from .job_service import JobService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()

async def scheduled_job_scraping():
    """Scheduled job scraping function"""
    logger.info("Starting scheduled job scraping...")
    scraper = JobScraper()
    job_service = JobService()
    
    try:
        # Scrape from multiple sources
        jobs = await scraper.scrape_all_sources()
        
        # Save jobs to database
        for job_data in jobs:
            await job_service.create_job(job_data)
            
        logger.info(f"Successfully scraped and saved {len(jobs)} jobs")
    except Exception as e:
        logger.error(f"Error during scheduled scraping: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AI Job Aggregator...")
    create_tables()
    
    # Schedule daily job scraping at 9 AM
    scheduler.add_job(
        scheduled_job_scraping,
        CronTrigger(hour=9, minute=0),
        id="daily_job_scraping",
        replace_existing=True
    )
    scheduler.start()
    
    # Run initial scraping
    asyncio.create_task(scheduled_job_scraping())
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("AI Job Aggregator shutting down...")

app = FastAPI(
    title="AI Job Aggregator",
    description="Aggregates AI consultancy jobs from multiple sources with focus on Danish market",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize services
job_service = JobService()
scraper = JobScraper()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(
    limit: int = 50,
    offset: int = 0,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    days_ago: Optional[int] = 30
):
    """Get paginated list of AI jobs"""
    try:
        jobs = await job_service.get_jobs(
            limit=limit,
            offset=offset,
            location=location,
            job_type=job_type,
            days_ago=days_ago
        )
        return jobs
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        return []

@app.post("/api/jobs/scrape")
async def manual_scrape(background_tasks: BackgroundTasks):
    """Manually trigger job scraping"""
    background_tasks.add_task(scheduled_job_scraping)
    return {"message": "Job scraping started in background"}

@app.get("/api/jobs/stats")
async def get_job_stats():
    """Get job statistics"""
    try:
        stats = await job_service.get_job_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching job stats: {e}")
        return {"error": "Failed to fetch statistics"}

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: int):
    """Delete a specific job"""
    try:
        success = await job_service.delete_job(job_id)
        if success:
            return {"message": "Job deleted successfully"}
        else:
            return {"error": "Job not found"}
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        return {"error": "Failed to delete job"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scheduler_running": scheduler.running
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)