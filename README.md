# Job Board Data Scraper

A flexible, extensible job scraping framework built with Python that can scrape job listings from multiple job boards. Currently supports Workable platform with an architecture designed for easy extension to other job platforms.

## Features

- **Multi-Platform Support**: Extensible architecture for adding new job board scrapers
- **Smart Filtering**: Configurable job filtering by keywords, location, job type, and company
- **Database Storage**: SQLite database for persistent job data storage
- **Duplicate Detection**: Automatic detection and prevention of duplicate job entries
- **Respectful Scraping**: Built-in delays and respectful scraping practices
- **Factory Pattern**: Dynamic scraper creation and registration system
- **Orchestrated Scraping**: Centralized job scraping orchestration with statistics

## Project Structure

```
job-board-data/
├── core/                    # Core framework components
│   ├── __init__.py
│   ├── base_scraper.py      # Abstract base class for platform scrapers
│   ├── database.py          # Database operations and management
│   ├── factory.py           # Dynamic scraper factory
│   ├── filters.py           # Job filtering logic
│   └── orchestrator.py      # Main scraping orchestration
├── main.py                  # Main application entry point
├── workable_scraper.py      # Workable platform scraper implementation
├── workable.py              # Legacy Workable scraper
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd job-board-data
```

2. Install required dependencies:
```bash
pip install selenium sqlite3
```

3. Install ChromeDriver for Selenium (required for web scraping):
   - Download from [ChromeDriver](https://chromedriver.chromium.org/)
   - Add to your system PATH

## Usage

### Quick Start

```python
from main import scrape_singl_platform

# Basic scraping example
search_params = {
    'query': 'python developer',
    'location': 'remote',
    'company_url': 'https://company.workable.com'
}

# Scrape jobs from Workable
scrape_singl_platform('workable', search_params, max_pages=3)
```

### Command Line Usage

List available platforms:
```bash
python main.py list
```

Run with default parameters:
```bash
python main.py
```

### Advanced Usage

#### Custom Filtering
```python
# Define filter criteria
filter_params = {
    'keywords': ['python', 'developer', 'engineer'],
    'locations': ['remote', 'new york', 'san francisco'],
    'job_types': ['full-time'],
    'companies': ['tech', 'startup']
}

# Scrape with filters
scrape_singl_platform('workable', search_params, filter_params, max_pages=5)
```

#### Multiple Platform Scraping
```python
from main import scrape_multiple_platforms

platforms = ['workable']  # Add more platforms as they become available
scrape_multiple_platforms(platforms, search_params, filter_params)
```

## Architecture

### Core Components

1. **BasePlatformScraper** (`core/base_scraper.py`):
   - Abstract base class defining the scraper interface
   - Methods for driver setup, page navigation, data extraction

2. **JobScrapperOrchestrator** (`core/orchestrator.py`):
   - Coordinates the scraping process
   - Handles filtering, duplicate detection, and database operations
   - Provides scraping statistics and error handling

3. **DatabaseManager** (`core/database.py`):
   - SQLite database operations
   - Job storage and duplicate detection
   - Database schema management

4. **JobFilter** (`core/filters.py`):
   - Configurable job filtering system
   - Filter by keywords, location, job type, salary, company

5. **ScrapperFactory** (`core/factory.py`):
   - Dynamic scraper creation and registration
   - Plugin-style architecture for adding new platforms

### Database Schema

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT,
    job_title TEXT,
    company TEXT,
    location TEXT,
    job_type TEXT,
    salary TEXT,
    description TEXT,
    requirements TEXT,
    post_date TEXT,
    url TEXT,
    company_logo TEXT,
    scrapped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data TEXT
)
```

## Supported Platforms

### Workable
- Scrapes job listings from Workable-powered career pages
- Supports detailed job information extraction
- Handles pagination and dynamic content loading

## Adding New Platforms

To add a new job board scraper:

1. Create a new scraper class inheriting from `BasePlatformScraper`:

```python
from core.base_scraper import BasePlatformScraper

class NewPlatformScraper(BasePlatformScraper):
    def __init__(self):
        super().__init__("new_platform")
    
    def setup_driver(self):
        # Implementation for driver setup
        pass
    
    def get_job_listings_page(self, search_params):
        # Implementation for navigation
        pass
    
    # Implement other required methods...
```

2. Register the scraper with the factory:

```python
from core.factory import ScrapperFactory
ScrapperFactory.register_scraper("new_platform", NewPlatformScraper)
```

## Configuration

### Search Parameters
- `query`: Job search query/keywords
- `location`: Job location filter
- `company_url`: Platform-specific company URL (for Workable)

### Filter Parameters
- `keywords`: List of required keywords in title/description
- `locations`: List of acceptable job locations
- `job_types`: List of acceptable job types (full-time, part-time, etc.)
- `companies`: List of acceptable company names
- `salary_min`: Minimum salary requirement

## Statistics and Monitoring

The scraper provides detailed statistics:
- Total jobs found
- Jobs filtered out
- Duplicate jobs detected
- Successfully scraped jobs
- Errors encountered

## Best Practices

- **Respectful Scraping**: Built-in delays prevent overwhelming target servers
- **Error Handling**: Comprehensive error handling and logging
- **Data Validation**: Input validation and data sanitization
- **Modular Design**: Easy to extend and maintain

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes following the existing architecture
4. Add tests for new functionality
5. Submit a pull request

## License

This project is for educational and legitimate job search purposes only. Please respect the terms of service of job board websites and use responsibly.

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**:
   - Ensure ChromeDriver is installed and in your PATH
   - Check ChromeDriver version compatibility with your Chrome browser

2. **Database errors**:
   - Check file permissions for database creation
   - Ensure SQLite is properly installed

3. **Scraping failures**:
   - Website structure may have changed
   - Check for CAPTCHA or anti-bot measures
   - Verify network connectivity

### Debug Mode

Enable debug output by modifying the scraper to include more verbose logging for troubleshooting specific issues.