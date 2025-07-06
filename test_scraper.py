#!/usr/bin/env python3
"""
Test scraper to add sample AI jobs for demonstration
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
import random

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.job_service import JobService
from app.models import JobCreate

# Sample AI job data for Danish companies
sample_jobs = [
    {
        "title": "AI Consultant - Machine Learning Engineer",
        "company": "NNIT",
        "location": "Copenhagen, Denmark",
        "description": "We are looking for an AI Consultant to join our team in Copenhagen. You will work with machine learning models, develop AI solutions for clients, and help implement artificial intelligence strategies. Experience with Python, TensorFlow, and cloud platforms is required. This is a unique opportunity to work with some of Denmark's largest enterprises.",
        "requirements": "Master's degree in Computer Science, AI, or related field. 3+ years experience with machine learning, deep learning, and AI project implementation. Strong Python skills, experience with TensorFlow/PyTorch. Knowledge of Danish market preferred.",
        "salary_min": 650000,
        "salary_max": 850000,
        "currency": "DKK",
        "job_type": "full-time",
        "remote_ok": True,
        "url": "https://www.nnit.com/careers/ai-consultant-ml-engineer-123",
        "source": "nnit_careers",
        "posted_date": datetime.now() - timedelta(days=1)
    },
    {
        "title": "Senior AI Trainer & Prompt Engineer",
        "company": "Deloitte Denmark",
        "location": "Aarhus, Denmark",
        "description": "Join Deloitte's AI practice as a Senior AI Trainer and Prompt Engineer. You'll train large language models, develop prompt engineering strategies, and work with generative AI solutions. This role involves working with clients across various industries to implement cutting-edge AI technologies.",
        "requirements": "5+ years in AI/ML, experience with LLMs, prompt engineering, and generative AI. Strong background in NLP, transformer models. Experience training teams on AI technologies. Fluent in Danish and English.",
        "salary_min": 750000,
        "salary_max": 950000,
        "currency": "DKK",
        "job_type": "full-time",
        "remote_ok": False,
        "url": "https://www.deloitte.dk/careers/senior-ai-trainer-prompt-engineer-456",
        "source": "deloitte_careers",
        "posted_date": datetime.now() - timedelta(hours=8)
    },
    {
        "title": "AI Project Lead - Nordic AI Center",
        "company": "Accenture Nordic",
        "location": "Copenhagen, Denmark",
        "description": "Lead AI projects at Accenture's Nordic AI Center. Drive artificial intelligence initiatives, manage AI project portfolios, and work with cross-functional teams to deliver innovative solutions. You'll mentor junior AI practitioners and interface with C-level executives.",
        "requirements": "7+ years in AI/ML project leadership. Strong business acumen combined with technical AI expertise. Experience managing large-scale AI implementations. PMP or similar project management certification preferred.",
        "salary_min": 800000,
        "salary_max": 1100000,
        "currency": "DKK",
        "job_type": "full-time",
        "remote_ok": True,
        "url": "https://www.accenture.com/dk/careers/ai-project-lead-nordic-789",
        "source": "accenture_careers",
        "posted_date": datetime.now() - timedelta(days=2)
    },
    {
        "title": "Machine Learning Engineer - Computer Vision",
        "company": "TietoEVRY",
        "location": "Odense, Denmark",
        "description": "We're seeking a Machine Learning Engineer specializing in computer vision to join our AI team. You'll develop computer vision models, work with image processing algorithms, and create AI solutions for industrial applications. Experience with OpenCV, deep learning frameworks, and edge AI deployment required.",
        "requirements": "Bachelor's/Master's in Computer Science or Engineering. 4+ years in computer vision and machine learning. Proficiency with OpenCV, PyTorch/TensorFlow, and edge AI deployment. Experience with industrial AI applications is a plus.",
        "salary_min": 600000,
        "salary_max": 780000,
        "currency": "DKK",
        "job_type": "full-time",
        "remote_ok": True,
        "url": "https://www.tietoevry.com/careers/ml-engineer-computer-vision-101",
        "source": "tietoevry_careers",
        "posted_date": datetime.now() - timedelta(days=3)
    },
    {
        "title": "AI Curator - Data Science Platform",
        "company": "Netcompany",
        "location": "Copenhagen, Denmark",
        "description": "Join Netcompany as an AI Curator for our data science platform. You'll curate AI models, manage model lifecycle, ensure AI governance, and work on building trustworthy AI systems. This role involves both technical implementation and strategic AI initiatives.",
        "requirements": "Strong background in AI/ML model management, MLOps, and AI governance. Experience with model versioning, monitoring, and deployment pipelines. Knowledge of AI ethics and responsible AI practices. 5+ years in data science or AI roles.",
        "salary_min": 700000,
        "salary_max": 900000,
        "currency": "DKK",
        "job_type": "full-time",
        "remote_ok": False,
        "url": "https://www.netcompany.com/careers/ai-curator-data-science-platform-202",
        "source": "netcompany_careers",
        "posted_date": datetime.now() - timedelta(hours=12)
    },
    {
        "title": "AI Research Scientist - NLP",
        "company": "IBM Denmark",
        "location": "Copenhagen, Denmark",
        "description": "IBM Research is looking for an AI Research Scientist focusing on Natural Language Processing. You'll conduct cutting-edge research in NLP, develop novel AI algorithms, and contribute to IBM's AI portfolio. This role involves publishing research papers and collaborating with international teams.",
        "requirements": "PhD in Computer Science, AI, or related field. Strong publication record in NLP/AI conferences. Experience with transformer models, large language models, and advanced NLP techniques. Research mindset with practical implementation skills.",
        "salary_min": 850000,
        "salary_max": 1200000,
        "currency": "DKK",
        "job_type": "full-time",
        "remote_ok": True,
        "url": "https://www.ibm.com/dk/careers/ai-research-scientist-nlp-303",
        "source": "ibm_careers",
        "posted_date": datetime.now() - timedelta(days=1)
    },
    {
        "title": "AI Mentor - Enterprise AI Adoption",
        "company": "Microsoft Denmark",
        "location": "Remote, Denmark",
        "description": "Help enterprises adopt AI technologies as an AI Mentor at Microsoft Denmark. You'll guide organizations through their AI journey, provide strategic AI consulting, and mentor internal teams on AI best practices. Strong communication and mentoring skills required.",
        "requirements": "Extensive experience in AI strategy and implementation. Strong mentoring and coaching abilities. Experience working with enterprise clients on AI transformation. Knowledge of Microsoft AI stack (Azure ML, Cognitive Services) preferred.",
        "salary_min": 750000,
        "salary_max": 1000000,
        "currency": "DKK",
        "job_type": "full-time",
        "remote_ok": True,
        "url": "https://www.microsoft.com/dk/careers/ai-mentor-enterprise-adoption-404",
        "source": "microsoft_careers",
        "posted_date": datetime.now() - timedelta(hours=6)
    },
    {
        "title": "Generative AI Specialist",
        "company": "Danske Bank",
        "location": "Copenhagen, Denmark",
        "description": "Danske Bank is seeking a Generative AI Specialist to drive our AI innovation initiatives. You'll work with GPT models, develop generative AI applications for banking, and ensure responsible AI deployment. Experience with financial services and regulatory compliance in AI is valuable.",
        "requirements": "Strong background in generative AI, large language models, and prompt engineering. Understanding of financial services and regulatory requirements. Experience with AI governance and risk management. 4+ years in AI/ML roles.",
        "salary_min": 700000,
        "salary_max": 920000,
        "currency": "DKK",
        "job_type": "full-time",
        "remote_ok": False,
        "url": "https://www.danskebank.com/careers/generative-ai-specialist-505",
        "source": "danskebank_careers",
        "posted_date": datetime.now() - timedelta(days=2)
    }
]

async def add_sample_jobs():
    """Add sample jobs to the database"""
    job_service = JobService()
    
    print("🤖 Adding sample AI jobs to the database...")
    
    added_count = 0
    for job_data in sample_jobs:
        try:
            job_create = JobCreate(**job_data)
            result = await job_service.create_job(job_create)
            if result:
                added_count += 1
                print(f"✅ Added: {job_data['title']} at {job_data['company']}")
            else:
                print(f"⚠️  Skipped: {job_data['title']} (already exists or filtered out)")
        except Exception as e:
            print(f"❌ Error adding {job_data['title']}: {e}")
    
    print(f"\n🎉 Successfully added {added_count} sample jobs!")
    
    # Get and display stats
    stats = await job_service.get_job_stats()
    print(f"\n📊 Current Database Stats:")
    print(f"   Total Jobs: {stats.total_jobs}")
    print(f"   Active Jobs: {stats.active_jobs}")
    print(f"   Jobs Today: {stats.jobs_today}")
    print(f"   Jobs This Week: {stats.jobs_this_week}")

if __name__ == "__main__":
    asyncio.run(add_sample_jobs())