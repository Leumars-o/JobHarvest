import importlib
import os
from typing import Dict, Type
from .base_scrapper import BasePlatformScrapper

class ScrapperFactory:
    """Dynamic factory for creating platform-specific scrapers"""
    _scrapers: Dict[str, Type[BasePlatformScrapper]] = {}

    @classmethod
    def register_scraper(cls, platform_name: str, scraper_class: Type[BasePlatformScrapper]):
        """Resgister a new scraper class"""
        cls._scrapers[platform_name.lower()] = scraper_class

    @classmethod
    def create_scraper(cls, platform: str) -> BasePlatformScrapper:
        """Create a platform-specific scrapers"""

        platform_lower = platform.lower()

        # Try to load from registered scrapers first
        if platform_lower in cls._scrapers:
            return cls._scrapers[platform_lower]()
        
        # Try to dynamically import from platform directory
        try:
            module = importlib.import_module(f'platforms.{platform_lower}_scraper')
            scraper_class = getattr(module, f'{platform.title()}Scraper')

            # Register for future use
            cls.register_scraper(platform_lower, scraper_class)
            return scraper_class()
        
        except (ImportError, AttributeError) as e:
            available_platforms = cls.get_available_platforms()
            raise ValueError(f"Unsupported platform: {platform}. Available platforms: {available_platforms}")
        

    @classmethod
    def get_available_platforms(cls) -> list:
        """Get list of available platforms"""
        platforms = list(cls._scrapers.keys())

        # Also check platforms directory
        platforms_dir = 'platforms'
        if os.path.exists(platforms_dir):
            for file in os.listdir(platforms_dir):
                if file.endswith('_scraper.py') and file != '__init__.py':
                    platform = file.replace('_scraper.py', '')
                    if platform not in platforms:
                        platforms.append(platform)

        return sorted(platforms)
        