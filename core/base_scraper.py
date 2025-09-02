from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BasePlatformScraper(ABC):
    """Abstract base class for platform-specific scrapers"""

    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.driver = None
    
    @abstractmethod
    def setup_driver(self) -> None:
        """setup web driver - platform specific"""
        pass

    @abstractmethod
    def get_job_listings_page(self, search_params: Dict[str, Any]) -> None:
        """Navigate to job listings page"""
        pass

    @abstractmethod
    def get_job_elements(self) -> List[Any]:
        """Get all job elements from current page"""
        pass

    @abstractmethod
    def extract_basic_job_info(self, job_element: Any) -> Dict[str, Any]:
        """Extract basic job info from job listing element"""
        pass

    @abstractmethod
    def extract_detailed_job_info(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed job info by visiting job page"""
        pass

    @abstractmethod
    def has_next_page(self) -> bool:
        """check if there's a next page"""
        pass

    @abstractmethod
    def go_to_next_page(self) -> bool:
        """Navigate to the next page"""
        pass

    def cleanup(self):
        """clean up resources"""
        if self.driver:
            self.driver.quit()
