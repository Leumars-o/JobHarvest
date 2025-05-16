import time
import random
from typing import Dict, Any
from .database import DatabaseManager
from .filters import JobFilter
from .base_scrapper import BasePlatformScrapper


class JobScrapperOrchestrator:
    """Main orchestrator that works with any platform scrapper"""

    def __init__(self, platform_scrapper: BasePlatformScrapper, db_name='job_scrapper.db'):
        self.platform_scrapper = platform_scrapper
        self.db_manager = DatabaseManager(db_name)
        self.job_filter = JobFilter()
        self.stats = {
            'total_found': 0,
            'filtered_out': 0,
            'duplicates': 0,
            'scraped': 0,
            'errors': 0
        }


    def set_filter_criteria(self, **filter_params):
        """set filtering criteria"""
        self.job_filter = JobFilter(**filter_params)

    
    def set_filter_criteria(self, **filter_params):
        """set filtering criteria"""
        self.job_filter = JobFilter(**filter_params)

    def scrape_jobs(self, search_params: Dict[str, Any], max_pages: int = 5):
        """main scrapping orchestration method"""
        try:
            self.platform_scrapper.setup_driver()
            self.platform_scrapper.get_job_listings_page(search_params)

            pages_scraped = 0

            while pages_scraped < max_pages:
                print(f"Scrapping page {pages_scraped + 1} from {self.platform_scrapper.platform_name}")

                job_elements = self.platform_scrapper.get_job_elements()
                self.stats['total_found'] += len(job_elements)

                for job_element in job_elements:
                    try:
                        self.process_job_element(job_element)
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        self.stats['errors'] += 1

                    # Respectful delay
                    time.sleep(random.uniform(1, 3))
                
                # Try to go to the next page
                if not self.platform_scrapper.has_next_page():
                    print("No more pages available")
                    break

                if not self.platform_scrapper.has_next_page():
                    print("Failed to navigate to next page")
                    break

                pages_scraped += 1
            
            self.print_stats()
            return self.stats['scraped']
        
        except Exception as e:
            print(f"Error during scraping: {e}")
            return 0
        
        finally:
            self.cleanup()

    
    def process_job_element(self, job_element):
        """Process a single job element"""

        # Extract basic info
        job_info = self.platform_scrapper.extract_basic_job_info(job_element)

        # check for duplicates
        if self.db_manager.job_exists(job_info.get('url', ''),
                                      self.platform_scrapper.platform_name):
            self.stats['duplicates'] += 1
            return
        
        # Apply filters
        if not self.job_filter.filter_job(job_info):
            self.stats['filtered_out'] += 1
            return
        
        # Get detailed info of job
        detailed_info = self.platform_scrapper.extract_detailed_job_info(job_info.get('url', ''))
        job_info.update(detailed_info)

        # Save to database
        if self.db_manager.insert_job(job_info):
            self.stats['scraped'] += 1

            print(f"✓ Scraped: {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}")

    
    def _print_stats(self):
        """print scraping statistics"""
        print("\n" + "="*50)
        print (f"SCRAPING STATISTICS - {self.platform_scrapper.platform_name}")
        print("="*50)
        for key, value in self.stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("="*50)


    def cleanup(self):
        """Clean up resources"""
        self.platform_scrapper.cleanup()
        self.db_manager.close()
        