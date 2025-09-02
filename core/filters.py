from typing import Dict, Any, List


class JobFilter:
    """Job filtering logic"""

    def __init__(self, keywords=None, locations=None, job_types=None,
                 salary_min=None, companies=None):
        self.keywords = [k.lower() for k in (keywords or [])]
        self.locations = [l.lower() for l in (locations or [])]
        self.job_types = [jt.lower() for jt in (job_types or [])]
        self.salary_min = salary_min
        self.companies = [c.lower() for c in (companies or [])]

    def filter_job(self, job_info: Dict[str, Any]) -> bool:
        """Filter job based on criteria"""

        # Keyword filtering
        if self.keywords:
            title = job_info.get('title', '').lower()
            description = job_info.get('description', '').lower()
            if not any(keyword in title or keyword in description for keyword in self.keywords):
                return False
            
        # Location Filter
        if self.locations:
            job_location = job_info.get('location', '').lower()
            if not any(location in job_location for location in self.locations):
                return False
        
        # Job type filter
        if self.job_types:
            job_type = job_info.get('job_type', '').lower()
            if not any(jtype in job_type for jtype in self.job_types):
                return False
            
        # Company filtering
        if self.companies:
            company_name = job_info.get('company', '').lower()
            if not any(company in company_name for company in self.companies):
                return False
        
        return True