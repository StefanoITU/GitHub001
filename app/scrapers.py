import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import json
import asyncio
import httpx

from .models import JobCreate

logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random
        })
        
        # Chrome options for headless browsing
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument(f'--user-agent={self.ua.random}')
        
        # AI-related search terms
        self.ai_search_terms = [
            "AI trainer", "AI consultant", "AI mentor", "AI project lead", "AI curator",
            "machine learning engineer", "data scientist", "AI researcher", 
            "artificial intelligence", "generative AI", "prompt engineer"
        ]
        
        # Danish job sites
        self.job_sites = {
            'jobnet': 'https://job.jobnet.dk',
            'jobindex': 'https://www.jobindex.dk',
            'glassdoor': 'https://www.glassdoor.dk',
            'indeed': 'https://dk.indeed.com',
            'linkedin': 'https://www.linkedin.com/jobs'
        }
    
    def get_driver(self):
        """Get Chrome WebDriver instance"""
        try:
            driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=self.chrome_options
            )
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            return None
    
    def extract_salary(self, text: str) -> tuple[Optional[float], Optional[float]]:
        """Extract salary range from text"""
        if not text:
            return None, None
            
        # Common Danish salary patterns
        patterns = [
            r'(\d+)\.?(\d*)\s*-\s*(\d+)\.?(\d*)\s*(?:kr|dkk|kroner)',
            r'(\d+)\.?(\d*)\s*(?:kr|dkk|kroner)',
            r'(\d+)\.?(\d*)\s*(?:k|thousand)\s*(?:kr|dkk|kroner)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if len(match.groups()) == 4:  # Range
                    min_sal = float(f"{match.group(1)}{match.group(2) or '000'}")
                    max_sal = float(f"{match.group(3)}{match.group(4) or '000'}")
                    return min_sal, max_sal
                else:  # Single value
                    sal = float(f"{match.group(1)}{match.group(2) or '000'}")
                    return sal, sal
        
        return None, None
    
    def extract_job_type(self, text: str) -> Optional[str]:
        """Extract job type from text"""
        if not text:
            return None
            
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['freelance', 'consultant', 'contractor']):
            return 'freelance'
        elif any(term in text_lower for term in ['part-time', 'part time', 'deltid']):
            return 'part-time'
        elif any(term in text_lower for term in ['full-time', 'full time', 'fuldtid']):
            return 'full-time'
        elif any(term in text_lower for term in ['contract', 'kontrakt']):
            return 'contract'
        
        return 'full-time'  # Default
    
    async def scrape_linkedin_jobs(self, search_term: str, location: str = "Denmark") -> List[Dict]:
        """Scrape LinkedIn jobs using Selenium"""
        jobs = []
        driver = self.get_driver()
        
        if not driver:
            logger.error("Failed to get Chrome driver")
            return jobs
        
        try:
            # Build LinkedIn search URL
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                'keywords': search_term,
                'location': location,
                'f_TPR': 'r86400',  # Last 24 hours
                'f_JT': 'F,P,C',    # Full-time, Part-time, Contract
                'sortBy': 'DD'      # Date descending
            }
            
            search_url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            logger.info(f"Scraping LinkedIn: {search_url}")
            driver.get(search_url)
            
            # Wait for page to load
            time.sleep(random.uniform(3, 6))
            
            # Accept cookies if present
            try:
                accept_cookies = driver.find_element(By.CSS_SELECTOR, 'button[data-consent-decision="accept"]')
                if accept_cookies:
                    accept_cookies.click()
                    time.sleep(2)
            except:
                pass
            
            # Get job cards
            job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-search-card')
            
            for card in job_cards[:20]:  # Limit to first 20 results
                try:
                    # Extract basic info
                    title_elem = card.find_element(By.CSS_SELECTOR, '.base-search-card__title')
                    company_elem = card.find_element(By.CSS_SELECTOR, '.base-search-card__subtitle')
                    location_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__location')
                    
                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    job_location = location_elem.text.strip()
                    
                    # Get job URL
                    job_url = title_elem.get_attribute('href')
                    
                    # Extract posted date
                    posted_date = None
                    try:
                        date_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__listdate')
                        posted_date = self.parse_posted_date(date_elem.text.strip())
                    except:
                        pass
                    
                    # Click to get more details
                    try:
                        title_elem.click()
                        time.sleep(random.uniform(2, 4))
                        
                        # Get job description
                        description = ""
                        try:
                            desc_elem = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '.show-more-less-html__markup'))
                            )
                            description = desc_elem.text.strip()
                        except:
                            pass
                        
                        # Extract salary and job type
                        salary_min, salary_max = self.extract_salary(description)
                        job_type = self.extract_job_type(description)
                        
                        # Check if remote
                        remote_ok = any(term in description.lower() for term in ['remote', 'hjemme', 'hybrid'])
                        
                        job_data = {
                            'title': title,
                            'company': company,
                            'location': job_location,
                            'description': description,
                            'requirements': '',  # LinkedIn doesn't separate requirements
                            'salary_min': salary_min,
                            'salary_max': salary_max,
                            'job_type': job_type,
                            'remote_ok': remote_ok,
                            'url': job_url,
                            'source': 'linkedin',
                            'posted_date': posted_date
                        }
                        
                        jobs.append(job_data)
                        
                    except Exception as e:
                        logger.error(f"Error extracting job details: {e}")
                        continue
                    
                except Exception as e:
                    logger.error(f"Error processing job card: {e}")
                    continue
                
                # Random delay between jobs
                time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        
        finally:
            driver.quit()
        
        logger.info(f"Found {len(jobs)} jobs on LinkedIn")
        return jobs
    
    async def scrape_jobnet(self, search_term: str) -> List[Dict]:
        """Scrape JobNet.dk"""
        jobs = []
        
        try:
            # JobNet API endpoint
            base_url = "https://job.jobnet.dk/CV/FindWork/Search"
            params = {
                'SearchString': search_term,
                'Area': '100',  # Denmark
                'Country': 'DK',
                'SortBy': 'CreatedDate',
                'SortOrder': 'Descending',
                'PageSize': '20'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, params=params)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find job listings
                    job_listings = soup.find_all('div', class_='job-listing-item')
                    
                    for listing in job_listings:
                        try:
                            # Extract job details
                            title_elem = listing.find('h2', class_='job-title')
                            company_elem = listing.find('span', class_='company-name')
                            location_elem = listing.find('span', class_='location')
                            
                            if not all([title_elem, company_elem]):
                                continue
                            
                            title = title_elem.text.strip()
                            company = company_elem.text.strip()
                            location = location_elem.text.strip() if location_elem else ''
                            
                            # Get job URL
                            job_url = title_elem.find('a')['href']
                            if not job_url.startswith('http'):
                                job_url = f"https://job.jobnet.dk{job_url}"
                            
                            # Get description (requires separate request)
                            description = ""
                            try:
                                desc_response = await client.get(job_url)
                                if desc_response.status_code == 200:
                                    desc_soup = BeautifulSoup(desc_response.text, 'html.parser')
                                    desc_elem = desc_soup.find('div', class_='job-description')
                                    if desc_elem:
                                        description = desc_elem.text.strip()
                            except:
                                pass
                            
                            # Extract posted date
                            posted_date = None
                            try:
                                date_elem = listing.find('span', class_='posted-date')
                                if date_elem:
                                    posted_date = self.parse_posted_date(date_elem.text.strip())
                            except:
                                pass
                            
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': location,
                                'description': description,
                                'requirements': '',
                                'salary_min': None,
                                'salary_max': None,
                                'job_type': self.extract_job_type(description),
                                'remote_ok': 'remote' in description.lower(),
                                'url': job_url,
                                'source': 'jobnet',
                                'posted_date': posted_date
                            }
                            
                            jobs.append(job_data)
                            
                        except Exception as e:
                            logger.error(f"Error processing JobNet listing: {e}")
                            continue
                
        except Exception as e:
            logger.error(f"Error scraping JobNet: {e}")
        
        logger.info(f"Found {len(jobs)} jobs on JobNet")
        return jobs
    
    async def scrape_jobindex(self, search_term: str) -> List[Dict]:
        """Scrape JobIndex.dk"""
        jobs = []
        
        try:
            base_url = "https://www.jobindex.dk/jobsoegning"
            params = {
                'q': search_term,
                'supcat': '11',  # IT category
                'area': '1',     # Capital region
                'sortby': '1'    # Newest first
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, params=params)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find job listings
                    job_listings = soup.find_all('div', class_='jobsearch-result')
                    
                    for listing in job_listings:
                        try:
                            # Extract job details
                            title_elem = listing.find('h4', class_='jobsearch-title')
                            company_elem = listing.find('a', class_='company-name')
                            location_elem = listing.find('span', class_='location')
                            
                            if not all([title_elem, company_elem]):
                                continue
                            
                            title = title_elem.text.strip()
                            company = company_elem.text.strip()
                            location = location_elem.text.strip() if location_elem else ''
                            
                            # Get job URL
                            job_url = title_elem.find('a')['href']
                            if not job_url.startswith('http'):
                                job_url = f"https://www.jobindex.dk{job_url}"
                            
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': location,
                                'description': '',
                                'requirements': '',
                                'salary_min': None,
                                'salary_max': None,
                                'job_type': 'full-time',
                                'remote_ok': False,
                                'url': job_url,
                                'source': 'jobindex',
                                'posted_date': None
                            }
                            
                            jobs.append(job_data)
                            
                        except Exception as e:
                            logger.error(f"Error processing JobIndex listing: {e}")
                            continue
                
        except Exception as e:
            logger.error(f"Error scraping JobIndex: {e}")
        
        logger.info(f"Found {len(jobs)} jobs on JobIndex")
        return jobs
    
    def parse_posted_date(self, date_text: str) -> Optional[datetime]:
        """Parse posted date from various formats"""
        try:
            date_text = date_text.lower().strip()
            
            if 'i dag' in date_text or 'today' in date_text:
                return datetime.now()
            elif 'i går' in date_text or 'yesterday' in date_text:
                return datetime.now() - timedelta(days=1)
            elif 'dage siden' in date_text:
                days = int(re.search(r'(\d+)', date_text).group(1))
                return datetime.now() - timedelta(days=days)
            elif 'hours ago' in date_text:
                hours = int(re.search(r'(\d+)', date_text).group(1))
                return datetime.now() - timedelta(hours=hours)
            elif 'timer siden' in date_text:
                hours = int(re.search(r'(\d+)', date_text).group(1))
                return datetime.now() - timedelta(hours=hours)
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing date: {date_text} - {e}")
            return None
    
    async def scrape_all_sources(self) -> List[JobCreate]:
        """Scrape all job sources"""
        all_jobs = []
        
        # Scrape each search term
        for search_term in self.ai_search_terms:
            logger.info(f"Scraping jobs for: {search_term}")
            
            # Scrape LinkedIn
            try:
                linkedin_jobs = await self.scrape_linkedin_jobs(search_term)
                all_jobs.extend(linkedin_jobs)
            except Exception as e:
                logger.error(f"Error scraping LinkedIn for {search_term}: {e}")
            
            # Scrape JobNet
            try:
                jobnet_jobs = await self.scrape_jobnet(search_term)
                all_jobs.extend(jobnet_jobs)
            except Exception as e:
                logger.error(f"Error scraping JobNet for {search_term}: {e}")
            
            # Scrape JobIndex
            try:
                jobindex_jobs = await self.scrape_jobindex(search_term)
                all_jobs.extend(jobindex_jobs)
            except Exception as e:
                logger.error(f"Error scraping JobIndex for {search_term}: {e}")
            
            # Delay between search terms
            await asyncio.sleep(random.uniform(5, 10))
        
        # Remove duplicates based on URL
        unique_jobs = []
        seen_urls = set()
        
        for job in all_jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(JobCreate(**job))
        
        logger.info(f"Found {len(unique_jobs)} unique jobs from all sources")
        return unique_jobs