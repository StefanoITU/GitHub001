{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 """\
Danish AI Job Scrapers for LinkedIn, Emagine, and eWorks Group\
"""\
\
import requests\
from bs4 import BeautifulSoup\
import time\
import sqlite3\
from datetime import datetime\
import json\
\
class DanishJobScraper:\
    def __init__(self, db_path="ai_jobs.db"):\
        self.db_path = db_path\
        self.headers = \{\
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'\
        \}\
        self.setup_database()\
    \
    def setup_database(self):\
        """Initialize database with proper schema"""\
        conn = sqlite3.connect(self.db_path)\
        cursor = conn.cursor()\
        \
        cursor.execute('''\
            CREATE TABLE IF NOT EXISTS jobs (\
                id INTEGER PRIMARY KEY AUTOINCREMENT,\
                title TEXT NOT NULL,\
                company TEXT NOT NULL,\
                location TEXT,\
                description TEXT,\
                url TEXT UNIQUE,\
                source TEXT NOT NULL,\
                date_posted TEXT,\
                job_type TEXT,\
                salary TEXT,\
                relevance_score INTEGER DEFAULT 0,\
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\
            )\
        ''')\
        \
        conn.commit()\
        conn.close()\
    \
    def save_job(self, job_data):\
        """Save job to database"""\
        conn = sqlite3.connect(self.db_path)\
        cursor = conn.cursor()\
        \
        try:\
            cursor.execute('''\
                INSERT OR REPLACE INTO jobs \
                (title, company, location, description, url, source, date_posted, job_type, salary, relevance_score)\
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\
            ''', (\
                job_data['title'],\
                job_data['company'],\
                job_data['location'],\
                job_data['description'],\
                job_data['url'],\
                job_data['source'],\
                job_data['date_posted'],\
                job_data['job_type'],\
                job_data.get('salary', ''),\
                job_data.get('relevance_score', 0)\
            ))\
            conn.commit()\
            return True\
        except Exception as e:\
            print(f"Error saving job: \{e\}")\
            return False\
        finally:\
            conn.close()\
    \
    def scrape_linkedin_jobs(self):\
        """Scrape LinkedIn jobs for AI positions in Denmark"""\
        # LinkedIn job search URLs for AI positions in Denmark\
        linkedin_urls = [\
            "https://www.linkedin.com/jobs/search/?keywords=artificial%20intelligence&location=Denmark&locationId=104514075",\
            "https://www.linkedin.com/jobs/search/?keywords=AI%20consultant&location=Denmark&locationId=104514075",\
            "https://www.linkedin.com/jobs/search/?keywords=machine%20learning&location=Denmark&locationId=104514075",\
            "https://www.linkedin.com/jobs/search/?keywords=data%20scientist&location=Denmark&locationId=104514075"\
        ]\
        \
        jobs_found = 0\
        \
        for url in linkedin_urls:\
            try:\
                response = requests.get(url, headers=self.headers)\
                if response.status_code == 200:\
                    soup = BeautifulSoup(response.content, 'html.parser')\
                    \
                    # LinkedIn job cards selector (may need adjustment)\
                    job_cards = soup.find_all('div', class_='base-card')\
                    \
                    for card in job_cards:\
                        try:\
                            title_elem = card.find('h3', class_='base-search-card__title')\
                            company_elem = card.find('h4', class_='base-search-card__subtitle')\
                            location_elem = card.find('span', class_='job-search-card__location')\
                            link_elem = card.find('a', class_='base-card__full-link')\
                            \
                            if title_elem and company_elem:\
                                job_data = \{\
                                    'title': title_elem.get_text(strip=True),\
                                    'company': company_elem.get_text(strip=True),\
                                    'location': location_elem.get_text(strip=True) if location_elem else 'Denmark',\
                                    'description': '',\
                                    'url': link_elem['href'] if link_elem else url,\
                                    'source': 'LinkedIn',\
                                    'date_posted': datetime.now().strftime('%Y-%m-%d'),\
                                    'job_type': 'Full-time',\
                                    'relevance_score': self.calculate_relevance(title_elem.get_text())\
                                \}\
                                \
                                if self.save_job(job_data):\
                                    jobs_found += 1\
                                    print(f"\uc0\u10003  Saved LinkedIn job: \{job_data['title']\}")\
                        \
                        except Exception as e:\
                            print(f"Error processing LinkedIn job card: \{e\}")\
                            continue\
                \
                time.sleep(2)  # Rate limiting\
                \
            except Exception as e:\
                print(f"Error scraping LinkedIn URL \{url\}: \{e\}")\
        \
        return jobs_found\
    \
    def scrape_emagine_jobs(self):\
        """Scrape Emagine jobs for AI positions"""\
        jobs_found = 0\
        \
        # Emagine Denmark job search URLs\
        emagine_urls = [\
            "https://www.emagine.dk/jobs?search=artificial+intelligence",\
            "https://www.emagine.dk/jobs?search=AI",\
            "https://www.emagine.dk/jobs?search=machine+learning",\
            "https://www.emagine.dk/jobs?search=data+scientist"\
        ]\
        \
        for url in emagine_urls:\
            try:\
                response = requests.get(url, headers=self.headers)\
                if response.status_code == 200:\
                    soup = BeautifulSoup(response.content, 'html.parser')\
                    \
                    # Emagine job listings selector (may need adjustment)\
                    job_cards = soup.find_all('div', class_='job-item') or soup.find_all('article', class_='job-card')\
                    \
                    for card in job_cards:\
                        try:\
                            title_elem = card.find('h2') or card.find('h3') or card.find('a', class_='job-title')\
                            company_elem = card.find('span', class_='company') or card.find('div', class_='company-name')\
                            location_elem = card.find('span', class_='location') or card.find('div', class_='location')\
                            link_elem = card.find('a')\
                            \
                            if title_elem:\
                                job_data = \{\
                                    'title': title_elem.get_text(strip=True),\
                                    'company': company_elem.get_text(strip=True) if company_elem else 'Emagine',\
                                    'location': location_elem.get_text(strip=True) if location_elem else 'Denmark',\
                                    'description': '',\
                                    'url': f"https://www.emagine.dk\{link_elem['href']\}" if link_elem and link_elem.get('href') else url,\
                                    'source': 'Emagine',\
                                    'date_posted': datetime.now().strftime('%Y-%m-%d'),\
                                    'job_type': 'Contract',\
                                    'relevance_score': self.calculate_relevance(title_elem.get_text())\
                                \}\
                                \
                                if self.save_job(job_data):\
                                    jobs_found += 1\
                                    print(f"\uc0\u10003  Saved Emagine job: \{job_data['title']\}")\
                        \
                        except Exception as e:\
                            print(f"Error processing Emagine job card: \{e\}")\
                            continue\
                \
                time.sleep(2)  # Rate limiting\
                \
            except Exception as e:\
                print(f"Error scraping Emagine URL \{url\}: \{e\}")\
        \
        return jobs_found\
    \
    def scrape_eworks_jobs(self):\
        """Scrape eWorks Group jobs for AI positions"""\
        jobs_found = 0\
        \
        # eWorks Group job search URLs\
        eworks_urls = [\
            "https://www.eworksgroup.com/jobs/?search=artificial+intelligence",\
            "https://www.eworksgroup.com/jobs/?search=AI",\
            "https://www.eworksgroup.com/jobs/?search=machine+learning",\
            "https://www.eworksgroup.com/jobs/?search=data+scientist"\
        ]\
        \
        for url in eworks_urls:\
            try:\
                response = requests.get(url, headers=self.headers)\
                if response.status_code == 200:\
                    soup = BeautifulSoup(response.content, 'html.parser')\
                    \
                    # eWorks job listings selector (may need adjustment)\
                    job_cards = soup.find_all('div', class_='job-listing') or soup.find_all('article', class_='job')\
                    \
                    for card in job_cards:\
                        try:\
                            title_elem = card.find('h2') or card.find('h3') or card.find('a', class_='job-title')\
                            company_elem = card.find('span', class_='company') or card.find('div', class_='company')\
                            location_elem = card.find('span', class_='location') or card.find('div', class_='location')\
                            link_elem = card.find('a')\
                            \
                            if title_elem:\
                                job_data = \{\
                                    'title': title_elem.get_text(strip=True),\
                                    'company': company_elem.get_text(strip=True) if company_elem else 'eWorks Group',\
                                    'location': location_elem.get_text(strip=True) if location_elem else 'Denmark',\
                                    'description': '',\
                                    'url': f"https://www.eworksgroup.com\{link_elem['href']\}" if link_elem and link_elem.get('href') else url,\
                                    'source': 'eWorks Group',\
                                    'date_posted': datetime.now().strftime('%Y-%m-%d'),\
                                    'job_type': 'Contract',\
                                    'relevance_score': self.calculate_relevance(title_elem.get_text())\
                                \}\
                                \
                                if self.save_job(job_data):\
                                    jobs_found += 1\
                                    print(f"\uc0\u10003  Saved eWorks job: \{job_data['title']\}")\
                        \
                        except Exception as e:\
                            print(f"Error processing eWorks job card: \{e\}")\
                            continue\
                \
                time.sleep(2)  # Rate limiting\
                \
            except Exception as e:\
                print(f"Error scraping eWorks URL \{url\}: \{e\}")\
        \
        return jobs_found\
    \
    def calculate_relevance(self, title):\
        """Calculate relevance score based on job title"""\
        ai_keywords = [\
            'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',\
            'data scientist', 'data science', 'neural network', 'nlp', 'computer vision',\
            'ai consultant', 'ai engineer', 'ai specialist', 'ai developer'\
        ]\
        \
        title_lower = title.lower()\
        score = 0\
        \
        for keyword in ai_keywords:\
            if keyword in title_lower:\
                score += 10\
        \
        return min(score, 100)  # Max score of 100\
    \
    def scrape_all_jobs(self):\
        """Scrape jobs from all sources"""\
        print("\uc0\u55357 \u56589  Starting job scraping from Danish AI job sources...")\
        \
        total_jobs = 0\
        \
        # LinkedIn\
        print("\\n\uc0\u55357 \u56536  Scraping LinkedIn jobs...")\
        linkedin_jobs = self.scrape_linkedin_jobs()\
        total_jobs += linkedin_jobs\
        print(f"Found \{linkedin_jobs\} LinkedIn jobs")\
        \
        # Emagine\
        print("\\n\uc0\u55356 \u57314  Scraping Emagine jobs...")\
        emagine_jobs = self.scrape_emagine_jobs()\
        total_jobs += emagine_jobs\
        print(f"Found \{emagine_jobs\} Emagine jobs")\
        \
        # eWorks Group\
        print("\\n\uc0\u55357 \u56508  Scraping eWorks Group jobs...")\
        eworks_jobs = self.scrape_eworks_jobs()\
        total_jobs += eworks_jobs\
        print(f"Found \{eworks_jobs\} eWorks Group jobs")\
        \
        print(f"\\n\uc0\u9989  Total jobs scraped: \{total_jobs\}")\
        return total_jobs\
\
# Usage example\
if __name__ == "__main__":\
    scraper = DanishJobScraper()\
    scraper.scrape_all_jobs()}