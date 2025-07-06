
"""
Danish AI Job Scrapers for various job boards
"""

import requests
from bs4 import BeautifulSoup
import time
import sqlite3
from datetime import datetime
import json

class DanishJobScraper:
    def __init__(self, db_path="ai_jobs.db"):
        self.db_path = db_path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.setup_database()

    def setup_database(self):
        """Initialize database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                description TEXT,
                url TEXT UNIQUE,
                source TEXT NOT NULL,
                date_posted TEXT,
                job_type TEXT,
                salary TEXT,
                relevance_score INTEGER DEFAULT 0,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_job(self, job_data):
        """Save job to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO jobs
                (title, company, location, description, url, source, date_posted, job_type, salary, relevance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data['title'],
                job_data['company'],
                job_data['location'],
                job_data['description'],
                job_data['url'],
                job_data['source'],
                job_data['date_posted'],
                job_data['job_type'],
                job_data.get('salary', ''),
                job_data.get('relevance_score', 0)
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving job: {e}")
            return False
        finally:
            conn.close()

    def calculate_relevance(self, title, description=""):
        """Calculate relevance score based on job title and description"""
        ai_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'ml',
            'deep learning', 'data scientist', 'data science', 'neural network',
            'nlp', 'computer vision', 'ai consultant', 'ai engineer',
            'ai specialist', 'ai developer', 'python', 'tensorflow', 'pytorch'
        ]
        
        text = f"{title} {description}".lower()
        score = 0
        
        for keyword in ai_keywords:
            if keyword in text:
                score += 10
        
        return min(score, 100)

    def scrape_jobindex(self):
        """Scrape JobIndex.dk for AI jobs"""
        print("🔍 Scraping JobIndex.dk...")
        jobs_found = 0
        
        # JobIndex search URLs for AI-related jobs
        search_terms = ['artificial+intelligence', 'machine+learning', 'data+scientist', 'ai+engineer']
        
        for term in search_terms:
            try:
                url = f"https://www.jobindex.dk/jobsoegning?q={term}&superjob=0"
                print(f"   Searching for: {term.replace('+', ' ')}")
                
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # JobIndex uses these selectors (may need adjustment)
                    job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')
                    
                    if not job_cards:
                        # Try alternative selectors
                        job_cards = soup.find_all('article') or soup.find_all('div', class_='job')
                    
                    for card in job_cards[:5]:  # Limit to first 5 results per search
                        try:
                            title_elem = card.find('h2') or card.find('h3') or card.find('a')
                            company_elem = card.find('span', class_='company') or card.find('div', class_='company')
                            
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                company = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
                                
                                # Get job URL
                                link = title_elem.get('href') if title_elem.name == 'a' else None
                                if not link:
                                    link_elem = card.find('a')
                                    link = link_elem.get('href') if link_elem else url
                                
                                # Make sure URL is absolute
                                if link and not link.startswith('http'):
                                    link = f"https://www.jobindex.dk{link}"
                                
                                job_data = {
                                    'title': title,
                                    'company': company,
                                    'location': 'Denmark',
                                    'description': '',
                                    'url': link or url,
                                    'source': 'JobIndex.dk',
                                    'date_posted': datetime.now().strftime('%Y-%m-%d'),
                                    'job_type': 'Full-time',
                                    'relevance_score': self.calculate_relevance(title)
                                }
                                
                                if self.save_job(job_data):
                                    jobs_found += 1
                                    print(f"   ✓ Saved: {title} at {company}")
                                
                        except Exception as e:
                            print(f"   ⚠️ Error processing job card: {e}")
                            continue
                    
                    time.sleep(2)  # Rate limiting
                else:
                    print(f"   ⚠️ Failed to fetch {url} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ Error scraping JobIndex for {term}: {e}")
        
        return jobs_found

    def scrape_thehub(self):
        """Scrape TheHub.dk for tech jobs"""
        print("🔍 Scraping TheHub.dk...")
        jobs_found = 0
        
        try:
            url = "https://thehub.dk/jobs"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job listings
                job_cards = soup.find_all('div', class_='job-card') or soup.find_all('article')
                
                for card in job_cards[:10]:  # Limit to first 10
                    try:
                        title_elem = card.find('h2') or card.find('h3') or card.find('a')
                        company_elem = card.find('span', class_='company') or card.find('div', class_='company')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            company = company_elem.get_text(strip=True) if company_elem else 'TheHub Company'
                            
                            # Only save if it's AI/ML related
                            if self.calculate_relevance(title) > 0:
                                job_data = {
                                    'title': title,
                                    'company': company,
                                    'location': 'Denmark',
                                    'description': '',
                                    'url': url,
                                    'source': 'TheHub.dk',
                                    'date_posted': datetime.now().strftime('%Y-%m-%d'),
                                    'job_type': 'Full-time',
                                    'relevance_score': self.calculate_relevance(title)
                                }
                                
                                if self.save_job(job_data):
                                    jobs_found += 1
                                    print(f"   ✓ Saved: {title} at {company}")
                    
                    except Exception as e:
                        print(f"   ⚠️ Error processing job card: {e}")
                        continue
                        
        except Exception as e:
            print(f"   ❌ Error scraping TheHub: {e}")
        
        return jobs_found

    def scrape_all_jobs(self):
        """Scrape jobs from all sources"""
        print("🚀 Starting real job scraping from Danish job boards...")
        
        total_jobs = 0
        
        # Scrape JobIndex
        jobindex_jobs = self.scrape_jobindex()
        total_jobs += jobindex_jobs
        print(f"📊 JobIndex jobs found: {jobindex_jobs}")
        
        # Scrape TheHub
        thehub_jobs = self.scrape_thehub()
        total_jobs += thehub_jobs
        print(f"📊 TheHub jobs found: {thehub_jobs}")
        
        print(f"\n✅ Total jobs scraped: {total_jobs}")
        
        # Show some stats
        self.show_stats()
        
        return total_jobs

    def show_stats(self):
        """Show database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT source, COUNT(*) FROM jobs GROUP BY source")
        source_counts = cursor.fetchall()
        
        print(f"\n📈 Database Statistics:")
        print(f"   Total jobs in database: {total_jobs}")
        for source, count in source_counts:
            print(f"   {source}: {count} jobs")
        
        conn.close()

# Usage example
if __name__ == "__main__":
    scraper = DanishJobScraper()
    scraper.scrape_all_jobs()
