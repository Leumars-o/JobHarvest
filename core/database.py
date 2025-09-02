# Scrapper Core
import sqlite3
import json
from typing import Dict, Any


class DatabaseManager:
    """Handles all database operations - platform agnostic
    """

    def __init__(self, db_name= 'job_scrapper.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.init_db()

    def init_db(self):
        """Initialize the SQLite database and create a table if table
            doesnt exist
        """
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Job table structure
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
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
        ''')
        self.conn.commit()
    
    
    def insert_job(self, job_info: Dict[str, Any]):
        """Insert job record into the database"""
        try:
            self.cursor.execute('''
                INSERT INTO jobs (platform, job_title, company, 
                                location, job_type, salary, description, 
                                requirements, post_date, url, company_logo, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_info['platform'],
                job_info['title'],
                job_info['company'],
                job_info['location'],
                job_info['job_type'],
                job_info['salary'],
                job_info['description'],
                job_info['requirements'],
                job_info['post_date'],
                job_info['url'],
                job_info['company_logo'],
                json.dumps(job_info.get('raw_data', {}))
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    

    def job_exists(self, url: str, platform: str) -> bool:
        """Check if job already exist in database"""
        self.cursor.execute(
            "SELECT 1 FROM jobs WHERE url = ? AND platform = ?",
            (url, platform)
        )
        return self.cursor.fetchone() is not None

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()