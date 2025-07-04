# AI Job Aggregator - Danish AI Consultancy Jobs

A comprehensive web application that aggregates AI consultancy jobs from multiple sources with a focus on the Danish market. The application automatically scrapes job postings from LinkedIn, JobNet, JobIndex, and other major job boards, filtering for AI-related positions in Denmark.

## Features

- 🤖 **AI-Powered Job Filtering**: Automatically identifies and scores AI-relevant jobs using keyword matching and relevance scoring
- 🇩🇰 **Danish Market Focus**: Specifically targets Danish job market with location filtering
- 📊 **Modern Dashboard**: Beautiful, responsive interface with job statistics and filtering
- 🔄 **Automated Scraping**: Runs daily at 9 AM and can be triggered manually
- 🔍 **Multiple Job Sources**: Scrapes LinkedIn, JobNet.dk, JobIndex.dk, and other major platforms
- 📈 **Relevance Scoring**: Each job gets a relevance score based on AI keywords and job requirements
- 🏷️ **Smart Categorization**: Automatically categorizes jobs by type (full-time, freelance, contract, etc.)
- 🎯 **Advanced Filtering**: Filter by location, job type, time period, and search terms

## Target Job Types

The application specifically looks for:
- AI Trainer
- AI Consultant  
- AI Mentor
- AI Project Lead
- AI Data Curator
- Machine Learning Engineer
- Data Scientist
- AI Researcher
- Prompt Engineer
- Generative AI roles

## Installation

### Prerequisites

- Python 3.8+
- Chrome browser (for web scraping)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-job-aggregator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Chrome WebDriver**
   The application will automatically download and set up Chrome WebDriver using `webdriver-manager`.

4. **Initialize the database**
   The SQLite database will be created automatically when you first run the application.

## Usage

### Running the Application

1. **Start the server**
   ```bash
   python -m app.main
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Access the dashboard**
   Open your browser and go to: `http://localhost:8000`

### Features Overview

#### Dashboard
- View job statistics (total jobs, jobs today, this week, high relevance)
- Monitor scraping status
- Access manual scraping trigger

#### Job Listings
- Browse AI jobs with relevance scores
- View job details, company, location, and requirements
- See matched AI keywords for each job
- Direct links to original job postings

#### Filtering
- **Location**: Filter by Danish cities (Copenhagen, Aarhus, Aalborg, etc.)
- **Job Type**: Full-time, part-time, contract, freelance
- **Time Period**: Last 7 days, 30 days, 90 days, or all time
- **Search**: Free text search across job titles and descriptions

#### Manual Scraping
- Click the "Scrape Jobs" button to trigger immediate job collection
- Progress indicator shows scraping status
- Results are automatically refreshed after completion

### API Endpoints

- `GET /api/jobs` - Get paginated job listings with filters
- `GET /api/jobs/stats` - Get job statistics
- `POST /api/jobs/scrape` - Trigger manual job scraping
- `GET /api/health` - Health check endpoint

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
DATABASE_URL=sqlite:///./ai_jobs.db
LOG_LEVEL=INFO
```

### Customization

#### AI Keywords
Edit the `ai_keywords` list in `app/job_service.py` to modify which keywords trigger AI job detection.

#### Danish Locations
Modify the `danish_locations` list in `app/job_service.py` to adjust location filtering.

#### Scraping Schedule
Change the cron trigger in `app/main.py` to modify the automatic scraping schedule:

```python
scheduler.add_job(
    scheduled_job_scraping,
    CronTrigger(hour=9, minute=0),  # Runs at 9 AM daily
    id="daily_job_scraping",
    replace_existing=True
)
```

## Architecture

### Backend Components

- **FastAPI Application** (`app/main.py`): Main web server and API endpoints
- **Job Scraper** (`app/scrapers.py`): Web scraping logic for multiple job sites
- **Job Service** (`app/job_service.py`): Business logic for job processing and filtering
- **Database Models** (`app/database.py`): SQLAlchemy models and database connection
- **Pydantic Models** (`app/models.py`): API request/response models

### Frontend
- **Modern HTML/CSS/JS**: Responsive dashboard with Tailwind CSS
- **Real-time Updates**: AJAX-based job loading and filtering
- **Interactive UI**: Toast notifications, loading states, and smooth transitions

### Database Schema

```sql
jobs (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500),
    company VARCHAR(200),
    location VARCHAR(200),
    description TEXT,
    requirements TEXT,
    salary_min FLOAT,
    salary_max FLOAT,
    currency VARCHAR(10),
    job_type VARCHAR(50),
    remote_ok BOOLEAN,
    url VARCHAR(500) UNIQUE,
    source VARCHAR(100),
    posted_date DATETIME,
    scraped_date DATETIME,
    is_active BOOLEAN,
    ai_keywords TEXT,
    relevance_score FLOAT
)
```

## Job Scraping Sources

### LinkedIn
- Uses Selenium for dynamic content scraping
- Searches for AI-related terms with Denmark location filter
- Extracts job details, descriptions, and posting dates
- Respects rate limits and uses random delays

### JobNet.dk
- Official Danish job portal
- HTTP-based scraping with BeautifulSoup
- Filters for IT category and Danish locations
- Extracts comprehensive job information

### JobIndex.dk
- Major Danish job board
- Focuses on IT/tech categories
- Location-based filtering for Danish cities

## Performance Considerations

- **Rate Limiting**: Built-in delays between requests to avoid being blocked
- **Caching**: Duplicate job detection prevents redundant entries
- **Pagination**: Efficient job loading with pagination support
- **Background Tasks**: Scraping runs in background to avoid blocking the UI

## Troubleshooting

### Common Issues

1. **Chrome WebDriver Issues**
   - Ensure Chrome browser is installed
   - The application automatically manages WebDriver installation
   - Check firewall settings if downloads fail

2. **Database Errors**
   - Ensure write permissions in the application directory
   - Check available disk space
   - Restart the application to recreate database if corrupted

3. **Scraping Issues**
   - Some job sites may implement anti-scraping measures
   - The application includes random delays and user-agent rotation
   - Check internet connectivity and site availability

### Logs

The application logs all activities to the console. Set `LOG_LEVEL=DEBUG` in your environment for detailed logging.

## Legal Considerations

This application is designed for personal use and respects the robots.txt and terms of service of job boards. Users should:

- Use the application responsibly
- Respect rate limits and website terms
- Not use scraped data for commercial purposes without permission
- Consider using official APIs where available

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue in the repository

## Roadmap

- [ ] Add more job sources
- [ ] Implement email notifications
- [ ] Add job bookmarking
- [ ] Create mobile app
- [ ] Add ML-based job recommendation
- [ ] Implement user authentication
- [ ] Add job application tracking
