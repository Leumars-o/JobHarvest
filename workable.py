from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import sqlite3
import time
import datetime
import json
import random
import sys

def init_db():
    """Initialize the SQLite database and create table if it doesn't exist"""
    conn = sqlite3.connect('workable_jobs.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            title TEXT,
            description TEXT,
            apply_url TEXT,
            workplace TEXT,
            employment_type TEXT,
            location TEXT,
            posted DATETIME,
            company_logo TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
    ''')

    conn.commit()
    return conn, cursor

def insert_job(cursor, job_info):
    """Insert job info into the database"""
    cursor.execute('''
        INSERT INTO jobs (company, title, description, apply_url, workplace, employment_type, location, posted, company_logo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_info['company'],
        job_info['title'],
        job_info['description'],
        job_info['apply_url'],
        job_info['workplace'],
        job_info['employment_type'],
        job_info['location'],
        job_info['post_date'],
        job_info['company_logo']
    ))


def job_filter(job_info):
    """Filter out invalid jobs based on the job information

    Args:
        job_info (dict): Dictionary containing job information

    Returns:
        Bool: returns True if the job is valid and should be processed, False otherwise
    """

    if job_info['posted'] != "Not found" or job_info['title'] != "Not found":
        if job_info['posted'].lower() == "posted today":
            return True
        
        # Check if the job is older than 15 days
        if job_info['post_data'][1] in ["day", "days"]:
            if int(job_info['post_data'][0]) < 15:
                return True
        else:
            return False
        print("Job is older than 15 days or has an invalid date format... Skipping")
    return False


def get_description(driver):
    """
    Scrapes the "Description" section of the job listing and returns as JSON

    Args:
        driver (WebDriver): The Selenium WebDriver instance

    Returns:
        JSON: The description section of the job listing or None if not found
    """

     # Wait for job breakdown div to load
    job_div = driver.find_element(By.XPATH, "//div[@class='jobBreakdown__job-breakdown--31MGR']")

    description_data = {
        'main_description': [],
        'requirements': [],
        'benefits': []
    }
    
    # Find all sections (Description, Requirements, Benefits)
    sections = job_div.find_elements(By.TAG_NAME, "section")
        
    for section in sections:
        try:
            # Get the section heading text
            heading_element = section.find_element(By.TAG_NAME, "h3")
            heading = heading_element.text.strip()
            
            # Get the content div for this section
            content_div = section.find_element(By.CLASS_NAME, "parsedHtml__content--OWD2W")
            
            # Process based on section type
            if "Description" in heading:
                # Get all text content elements (paragraphs, headings, lists)
                paragraphs = content_div.find_elements(By.TAG_NAME, "p")
                subheadings = content_div.find_elements(By.TAG_NAME, "h3")
                lists = content_div.find_elements(By.TAG_NAME, "ul")
                ordered_lists = content_div.find_elements(By.TAG_NAME, "ol")
                
                # Process paragraphs
                for p in paragraphs:
                    if p.find_elements(By.TAG_NAME, "strong"):
                        sub_title = p.find_elements(By.TAG_NAME, "strong")
                        for title in sub_title:
                            sub_title = title.text.strip()
                            if sub_title:
                                description_data['main_description'].append({
                                    'type': 'sub_title',
                                    'content': sub_title
                                })
                    else:
                        text = p.text.strip()
                        if text:  # Skip empty paragraphs
                            description_data['main_description'].append({
                                'type': 'paragraph',
                                'content': text
                            })
                
                # Process subheadings
                for h in subheadings:
                    text = h.text.strip()
                    if text:
                        description_data['main_description'].append({
                            'type': 'subheading',
                            'content': text
                        })
                
                # Process unordered lists
                for ul in lists:
                    items = ul.find_elements(By.TAG_NAME, "li")
                    list_items = []
                    for item in items:
                        list_items.append(item.text.strip())
                    
                    if list_items:
                        description_data['main_description'].append({
                            'type': 'unordered_list',
                            'items': list_items
                        })
                
                # Process ordered lists
                for ol in ordered_lists:
                    items = ol.find_elements(By.TAG_NAME, "li")
                    list_items = []
                    for item in items:
                        list_items.append(item.text.strip())
                    
                    if list_items:
                        description_data['main_description'].append({
                            'type': 'ordered_list',
                            'items': list_items
                        })
            
            elif "Requirements" in heading:
                # Same approach as description, but store in requirements
                paragraphs = content_div.find_elements(By.TAG_NAME, "p")
                subheadings = content_div.find_elements(By.TAG_NAME, "h3")
                lists = content_div.find_elements(By.TAG_NAME, "ul")
                ordered_lists = content_div.find_elements(By.TAG_NAME, "ol")
                
                for p in paragraphs:
                    if p.find_elements(By.TAG_NAME, "strong"):
                        sub_title = p.find_elements(By.TAG_NAME, "strong")
                        for title in sub_title:
                            sub_title = title.text.strip()
                            if sub_title:
                                description_data['main_description'].append({
                                    'type': 'sub_title',
                                    'content': sub_title
                                })
                    else:
                        text = p.text.strip()
                        if text:  # Skip empty paragraphs
                            description_data['main_description'].append({
                                'type': 'paragraph',
                                'content': text
                            })
                
                for h in subheadings:
                    text = h.text.strip()
                    if text:
                        description_data['requirements'].append({
                            'type': 'subheading',
                            'content': text
                        })
                
                for ul in lists:
                    items = ul.find_elements(By.TAG_NAME, "li")
                    list_items = []
                    for item in items:
                        list_items.append(item.text.strip())
                    
                    if list_items:
                        description_data['requirements'].append({
                            'type': 'unordered_list',
                            'items': list_items
                        })
                
                for ol in ordered_lists:
                    items = ol.find_elements(By.TAG_NAME, "li")
                    list_items = []
                    for item in items:
                        list_items.append(item.text.strip())
                    
                    if list_items:
                        description_data['requirements'].append({
                            'type': 'ordered_list',
                            'items': list_items
                        })
            
            elif "Benefits" in heading:
                # Same approach for benefits
                paragraphs = content_div.find_elements(By.TAG_NAME, "p")
                subheadings = content_div.find_elements(By.TAG_NAME, "h3")
                lists = content_div.find_elements(By.TAG_NAME, "ul")
                ordered_lists = content_div.find_elements(By.TAG_NAME, "ol")
                
                for p in paragraphs:
                    if p.find_elements(By.TAG_NAME, "strong"):
                        sub_title = p.find_elements(By.TAG_NAME, "strong")
                        for title in sub_title:
                            sub_title = title.text.strip()
                            if sub_title:
                                description_data['main_description'].append({
                                    'type': 'sub_title',
                                    'content': sub_title
                                })
                    else:
                        text = p.text.strip()
                        if text:  # Skip empty paragraphs
                            description_data['main_description'].append({
                                'type': 'paragraph',
                                'content': text
                            })
                
                for h in subheadings:
                    text = h.text.strip()
                    if text:
                        description_data['benefits'].append({
                            'type': 'subheading',
                            'content': text
                        })
                
                for ul in lists:
                    items = ul.find_elements(By.TAG_NAME, "li")
                    list_items = []
                    for item in items:
                        list_items.append(item.text.strip())
                    
                    if list_items:
                        description_data['benefits'].append({
                            'type': 'unordered_list',
                            'items': list_items
                        })
                
                for ol in ordered_lists:
                    items = ol.find_elements(By.TAG_NAME, "li")
                    list_items = []
                    for item in items:
                        list_items.append(item.text.strip())
                    
                    if list_items:
                        description_data['benefits'].append({
                            'type': 'ordered_list',
                            'items': list_items
                        })
            
        except Exception as e:
            print(f"Error processing section: {str(e)}")
    # Save the description data as JSON
    try:
        with open('scraped_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(description_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving description data: {str(e)}")
    
    # Convert to JSON string and return
    try:
        description_data = json.dumps(description_data, ensure_ascii=False)
        return description_data
    except Exception as e:
        print(f"Error converting description data to JSON: {str(e)}")
        return None


def get_post_date(job_info, element):
    """
    Parse the posting date and save the actual date of posting
    
    Args:
    job_info (dict): Dictionary to store job information
    element (element): HTML/XML element containing the posting date text
    
    Returns:
    None
    """

    # Get the text content of the element
    job_info["posted"] = element.text.strip()

    # Get today's date
    today = datetime.datetime.today()
    today_str = today.strftime('%d/%m/%Y')

    # Check if the posting date is today
    if "today" in job_info["posted"].lower():
        job_info["post_date"] = today_str
        job_info["post_data"] = ["today"]
        return
    
    try:
        # Split the text into parts
        parts = job_info["posted"].split()
        
        # Ensure the format is correct: "Posted X day/days/month/months/year/years ago"
        if (len(parts) >= 3 and 
            parts[0].lower() == "posted" and 
            parts[2] in ["day", "days", "month", "months", "year", "years"]):
            
            job_info["post_data"] = [parts[1], parts[2]]

            # Get the number of days, months or years
            time_value = int(parts[1])
            time_units = parts[2]
            
            # Get the posting time based on the time delta
            post_date = None
            if time_units in ["day", "days"]:
                post_date = today - datetime.timedelta(days=time_value)
            elif time_units in ["month", "months"]:
                post_date = today - datetime.timedelta(days=time_value*30)
            elif time_units in ["year", "years"]:
                post_date = today - datetime.timedelta(days=time_value*365)
            
            # Save the posting date in the correct format
            job_info["post_date"] = post_date.strftime('%d/%m/%Y')
        else:
            # fallback to today's date if the format is incorrect
            job_info["post_date"] = today.strftime('%d/%m/%Y')
    except (ValueError, IndexError):
        job_info["post_date"] = today.strftime('%d/%m/%Y')


def scrape_workable_jobs(last_count=None):
    try:
        conn, cursor = init_db()

        url = 'https://jobs.workable.com/search?location=Lagos%2C+Nigeria'
        # driver = webdriver.Chrome(options=chrome_options)
        driver = webdriver.Chrome()
        driver.maximize_window()

        driver.get(url)
        
        try:
            accept_cookie = driver.find_element(By.XPATH, "//button[@data-ui='cookie-consent-accept']")
            accept_cookie.click()
            print("cookie accepted")
            time.sleep(3)

        except Exception as e:
            print("cookie page not found")
            #continue with rest of script
            pass

        job_count_text = driver.find_element(By.XPATH, "//span[@data-ui='jobs-list-title']//strong[contains(@class, 'styles__strong')]").text
        job_count = int(job_count_text.split()[0])
        print(f"Total Job count: {job_count_text}")

        if last_count is not None:
            try:
                last_count = int(last_count)
                jobs_to_process = job_count - last_count
                if jobs_to_process <= 0:
                    print("No new jobs to process")
                    return False
                print(f"Processing {jobs_to_process} new jobs (from {job_count} total jobs.)")
            except ValueError:
                print("Invalid start count: {last_count}. Processing all jobs")
                jobs_to_process = job_count
        else:
            jobs_to_process = job_count
            print(f"Processing all {job_count} jobs")

        processed_count = 0

        while processed_count < jobs_to_process:
            listings = driver.find_elements(By.XPATH, "//li[@class='jobsList__list-item--3HLIF']")
            
            if listings:
                new_listings = listings[processed_count:] if processed_count < len(listings) else []
                print(f"Processing {len(new_listings)} new listings")
                print(f"Total processed: {processed_count}")
                print("=====================================\n")
            else:
                print("No listings found")
                new_listings = []

            for listing in new_listings:
                job_info = {}
                if processed_count >= jobs_to_process:
                    break
                try:
                    # click on the listing and wait for the job details to load
                    listing.click()
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//h2[contains(@class, 'jobOverview__job-title')]"))
                    )

                    # Extract job details with error handling for each field
                    extractors = {
                        'company': ("//h3[contains(@class, 'jobOverview__company')]//a", "text"),
                        'title': ("//h2[contains(@class, 'jobOverview__job-title')]//strong", "text"),
                        'apply_url': ("//h3[contains(@class, 'jobOverview__company')]//a", "href"),
                        'workplace': ("//span[@data-ui='overview-workplace']//strong", "text"),
                        'employment_type': ("//span[@data-ui='overview-employment-type']", "text"),
                        'location': ("//span[@data-ui='overview-location']", "text"),
                        'posted': ("//span[@data-ui='overview-date-posted']", "text"),
                        'company_logo': ("//div [@class='companyLogo__container--26Pxz' ] //img[contains(@class, 'companyLogo__logo')]", "src")
                    }

                    for field, (xpath, attr_type) in extractors.items():
                        try:
                            element = driver.find_element(By.XPATH, xpath)
                            if attr_type == "href":
                                job_info[field] = element.get_attribute("href")
                            elif attr_type == "src":
                                job_info[field] = element.get_attribute("src")
                            elif field == "posted":
                                get_post_date(job_info, element)
                            else:
                                job_info[field] = element.text.strip()
                                
                        except NoSuchElementException:
                            job_info[field] = "Not found"

                    # Get description
                    try:
                        job_info['description'] = get_description(driver)
                    except Exception as e:
                        print(f"Error fetching description: {e}")
                        job_info['description'] = None
                    
                    # validate and filter job data before inserting into database
                    if job_filter(job_info):
                        # Insert job into database
                        insert_job(cursor, job_info)
                        conn.commit()
                        processed_count += 1

                        print(f"Company: {job_info['company']}")
                        print(f"Job title: {job_info['title']}")
                        print(f"Workplace: {job_info['workplace']} - {job_info['employment_type']}")
                        print(f"Location: {job_info['location']}")
                        print(f"Posted: {job_info['posted']}")
                        print(f"posted: {job_info['post_date']}")
                        print("=====================================")
                    else:
                        print(f"Invalid Job data. Skipping job: {job_info['title']}")
                        print("=====================================")

                    # Add a random delay before processing the next listing
                    time.sleep(random.uniform(1.5, 3.0))
                    
                except Exception as e:
                    print(f"Error processing listing: {e}")
                    try:
                        driver.back()
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//li[@class='jobsList__list-item--3HLIF']"))
                        )
                    except Exception as back_error:
                        print(f"Error going back: {back_error}")
                    time.sleep(2)

            if processed_count < job_count:
                try:
                    show_more = driver.find_element(By.XPATH, "//button[@data-ui='load-more-button']")
                    show_more.click()
                    print("Clicked on show more")
                    time.sleep(3)
                except NoSuchElementException:
                    print("Show more not found")
                    break
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
        print("Data saved to database")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()
        if 'driver' in locals():
            driver.quit()


if __name__ == "__main__":
    last_count = sys.argv[1] if len(sys.argv) > 1 else None
    success = scrape_workable_jobs(last_count)