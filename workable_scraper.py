# platforms/workable_scraper_corrected.py
import json
import time
import datetime
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options

from core.base_scraper import BasePlatformScraper

class WorkableScraper(BasePlatformScraper):
    """oop optimized workable scraper"""

    def __init__(self):
        super().__init__("workable")
        self.base_url = "https://jobs.workable.com/search?location=Lagos%2C+Nigeria"
        self.wait = None
        self.current_page = 0

    
    def setup_driver(self) -> None:
        """Setup Chrome Webdriver"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    
    def get_job_listings_page(self, search_params: Dict[str, Any]) -> None:
        """Navigate to job listings page"""
        url = self._build_search_url(search_params)
        print(f"Navigating to: {url}")
        self.driver.get(url)
        self._handle_cookie_consent()
        time.sleep(2) # allowing page load 

    def get_job_elements(self) -> List[Any]:
        """Get all job elements currently visible on page"""
        try:
            # Wait for job listings to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//li[@class='jobsList__list-item--3HLIF']"))
            )
            
            # Return ALL job elements on current page
            listings = self.driver.find_elements(By.XPATH, "//li[@class='jobsList__list-item--3HLIF']")
            print(f"Found {len(listings)} job listings on page")
            return listings
            
        except TimeoutException:
            print("No job listings found")
            return []
        
    
    def extract_basic_job_info(self, job_element: Any) -> Dict[str, Any]:
        """Extract Only basic info visible in the job listing"""
        job_info = {
            'platform': self.platform_name,
            'title': 'Not found',
            'company': 'Not found',
            'location': 'Not found',
            'job_type': 'Not found',
            'salary': 'Not found',
            'url': 'Not found',
            'post_date': 'Not found',
            'raw_data': {}
        }

        try:
            pass
            # Extract whats visible without clicking
            # title_elem = 
            # job_info['title] = title_elem.text.strip() if title_elem else 'Not found'

            # job_link = 
            # job_info['url'] = job_link.get_attribute('href') if job_link else 'Not found'

        except NoSuchElementException as e:
            print(f"Error extracting basic info: {e}")
            job_info['raw_data']['error'] = str(e)

        return job_info
    

    def extract_detailed_job_info(self, job_url: str) -> Dict[str, Any]:
        """Navigate to job url and extract detailed information"""
        detailed_info = {
            'description': 'Not found',
            'requirements': 'Not found'
        }

        if not job_url or job_url == 'Not found':
            return detailed_info
        
        try:
            # navigate to the speecific page
            self.driver.get(job_url)

            # Wait for job details to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(@class, 'jobOverview__job-title')]"))
            )

            # Extract detailed information
            description_data = self._get_job_description()
            if description_data:
                detailed_info['description'] = description_data
                detailed_info['requirements'] = self._extract_requirements_from_description(description_data)

            
            # Extract other details like salary, benefits etc
            detailed_info.update(self._extract_job_metadata())

        except Exception as e:
            print(f"Error extracting detailed info from {job_url}: {e}")
            detailed_info['description'] = f"Error: {str(e)}"
        
        return detailed_info
    