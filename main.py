import sys
from core.factory import ScrapperFactory
from core.orchestrator import JobScrapperOrchestrator


def scrape_singl_platform(platform: str, search_params: Dict[str, Any],
                          filter_params: Dict[str, Any] = None, max_pages: int = 5):
    """Scrape jobs from a single platform"""
    try:
        # Create platform scraper
        scraper = ScrapperFactory.create_scraper(platform)
        orchestrator = JobScrapperOrchestrator(scraper, f'{platform}_jobs.db')

        # Set filters if provided
        if filter_params:
            orchestrator.set_filter_criteria(**filter_params)

        # Start scraping
        return orchestrator.scrape_jobs(search_params, max_pages)
    
    except Exception as e:
        print(f"Failed to scrape {platform}: {e}")
        return 0
    
def scrape_multiple_platforms(platforms: list, search_params: Dict[str, Any],
                              filter_params: Dict[str, Any] = None, max_pages: int = 3):
    """Scrape jobs form multiple platforms"""
    total_scraped = 0

    for platform in platforms:
        print(f"\n{'='*20} SCRAPING {platform.upper()} {'='*20}")
        scraped = scrape_singl_platform(platform, search_params, filter_params, max_pages)
        total_scraped += scraped

    print(f"\n Total jobs scraped across all platforoms: {total_scraped}")
    return total_scraped


def list_available_platforms():
    """List all available platforms"""
    platforms = ScrapperFactory.get_available_platforms()
    print("Available platforms:")

    for platform in platforms:
        print(f" - {platform}")
    return platforms


def main():
    """Main application entry point"""
    # Example Usage
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            list_available_platforms()
            return
        
    # Define search parameters

    # Sample Parameters
    search_params = {
        'query': 'python developer',
        'location': 'remote',
        'company_url': 'https://company.workable.com' # specific to platform
    }

    # Define filter criteria

    # sample filter
    filter_params = {
        'keywords': ['python', 'developer', 'engineer'],
        'locations': ['remote', 'new york', 'san francisco'],
        'job_types': ['full-time'],
        'companies': ['tech', 'startup']
    }

    # Single platform scraping
    print("Scraping from workable...")
    scrape_singl_platform('workable', search_params, filter_params, max_pages=3)

    # Multiple platform scraping
    # platforms = ['workable', 'weworkremotely', 'indeed']
    # scrape_multiple_platforms(platforms, search_params, filter_params)

if __name__ == "__main__":
    main()

    