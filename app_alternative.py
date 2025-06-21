import pandas as pd
import re
import os
import json
from flask import Flask, render_template, request, jsonify, send_file
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

def setup_driver():
    """Setup Chrome driver with headless options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        # Try to use webdriver-manager to get Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error with webdriver-manager: {e}")
        # Fallback to system Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def get_job_details(driver, url):
    """Get detailed job information from a specific job URL"""
    try:
        # Create a new driver instance for job details
        job_driver = setup_driver()
        job_driver.get(url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Get required skills
        try:
            skills_elements = job_driver.find_elements(By.CSS_SELECTOR, "div.round_tabs_container span.round_tabs")
            required_skills = [skill.text.strip() for skill in skills_elements if skill.text.strip()]
        except:
            required_skills = []
        
        job_driver.quit()
        return {
            "required_skills": required_skills
        }
    except Exception as e:
        print(f"Error fetching job details from {url}: {e}")
        try:
            job_driver.quit()
        except:
            pass
        return {
            "required_skills": []
        }

def get_internships(position, experience, city, max_pages=0):
    """Get internships data using Selenium"""
    # Format the URL with user inputs
    base_url = "https://internshala.com"
    
    # Build URL based on available parameters
    if position and city:
        url = f"{base_url}/internships/{position}-internship-in-{city}/"
    elif position:
        url = f"{base_url}/internships/{position}-internship/"
    elif city:
        url = f"{base_url}/internships/internship-in-{city}/"
    else:
        # If no parameters, search all internships
        url = f"{base_url}/internships/"
    
    all_data = []
    seen_urls = set()  # Track seen URLs to avoid duplicates
    current_page = 1
    consecutive_empty_pages = 0  # Track consecutive empty pages
    max_consecutive_empty = 3  # Stop after 3 consecutive empty pages
    
    print(f"Searching for internships at: {url}")
    print(f"Max pages to search: {'All available' if max_pages == 0 else max_pages}")
    
    driver = setup_driver()
    
    try:
        while consecutive_empty_pages < max_consecutive_empty:
            # Check if we've reached the max pages limit
            if max_pages > 0 and current_page > max_pages:
                print(f"Reached maximum pages limit ({max_pages})")
                break
                
            try:
                # Add page parameter to URL only if max_pages is specified
                if max_pages > 0 and current_page > 1:
                    page_url = f"{url}page-{current_page}/"
                else:
                    page_url = url
                    
                print(f"Fetching page {current_page}...")
                
                # Navigate to page
                driver.get(page_url)
                
                # Wait for page to load
                time.sleep(3)
                
                # Check if we're on a valid page by looking for the main content
                try:
                    main_content = driver.find_element(By.CSS_SELECTOR, "div.individual_internship")
                except:
                    print(f"No internship data found on page {current_page}. Stopping search.")
                    break
                
                # Extract data
                internships = driver.find_elements(By.CSS_SELECTOR, "div.individual_internship")
                
                if not internships:  # No more jobs found on this page
                    consecutive_empty_pages += 1
                    print(f"No internships found on page {current_page}")
                    current_page += 1
                    continue
                else:
                    consecutive_empty_pages = 0  # Reset counter if we found jobs
                    print(f"Found {len(internships)} internships on page {current_page}")
                    
                page_jobs_count = 0  # Track jobs added from this page
                
                for internship in internships:
                    try:
                        # Position
                        position_tag = internship.find_element(By.CSS_SELECTOR, "a#job_title")
                        position = position_tag.text.strip()
                        job_url = base_url + position_tag.get_attribute("href") if position_tag.get_attribute("href") else None
                        
                        # Skip if no URL or if we've seen this URL before
                        if not job_url or job_url in seen_urls:
                            continue
                        
                        seen_urls.add(job_url)  # Mark URL as seen

                        # Company
                        try:
                            company_tag = internship.find_element(By.CSS_SELECTOR, "p.company-name")
                            company = company_tag.text.strip()
                        except:
                            company = "N/A"

                        # Experience
                        try:
                            experience_div = internship.find_element(By.CSS_SELECTOR, "div.row-1-item span")
                            experience_text = experience_div.text.strip()
                        except:
                            experience_text = "N/A"
                        
                        # Extract number from experience text
                        experience_years = 0
                        if experience_text != "N/A":
                            match = re.search(r'(\d+)', experience_text)
                            if match:
                                experience_years = int(match.group(1))

                        # Get additional job details
                        job_details = get_job_details(driver, job_url)

                        job_data = {
                            "position": position,
                            "company": company,
                            "url": job_url,
                            "experience": experience_years,
                            "required_skills": job_details.get("required_skills", [])
                        }
                        
                        # Only add if we have valid data
                        if position != "N/A" and company != "N/A":
                            all_data.append(job_data)
                            page_jobs_count += 1
                            print(f"Added: {position} at {company}")
                        
                    except Exception as e:
                        print(f"Skipping job due to error: {e}")
                        continue
                
                print(f"Added {page_jobs_count} jobs from page {current_page}")
                
                # If we didn't add any jobs from this page, increment empty counter
                if page_jobs_count == 0:
                    consecutive_empty_pages += 1
                    print(f"No valid jobs found on page {current_page}. Stopping search.")
                    break
                
                # If max_pages is 0, only fetch first page
                if max_pages == 0:
                    print("No page count specified. Only fetching first page.")
                    break
                    
                current_page += 1
                
            except Exception as e:
                print(f"Error fetching page {current_page}: {e}")
                consecutive_empty_pages += 1
                current_page += 1
        
    finally:
        # Make sure to close the driver even if there's an error
        driver.quit()
    
    pages_processed = current_page - 1
    print(f"\nTotal internships found: {len(all_data)}")
    print(f"Total pages processed: {pages_processed}")
    print(f"Unique URLs processed: {len(seen_urls)}")
    
    return all_data, pages_processed

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    # Get parameters from request
    position = request.args.get('position', '').strip()
    experience = request.args.get('experience', '').strip()
    city = request.args.get('city', '').strip()
    max_pages = int(request.args.get('max_pages', 1))
    
    def run_search():
        try:
            # Get internships data
            internships_data, pages_processed = get_internships(position, experience, city, max_pages)
            
            if internships_data:
                # Create DataFrame
                df = pd.DataFrame(internships_data)
                
                # Create filename with timestamp
                timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                filename = f"internships_{position or 'all'}_{timestamp}.xlsx"
                filepath = os.path.join('downloads', filename)
                
                # Ensure downloads directory exists
                os.makedirs('downloads', exist_ok=True)
                
                # Save to Excel
                df.to_excel(filepath, index=False)
                print(f"Data saved to {filepath}")
                
                # Store results in a simple way (you might want to use a database in production)
                with open('downloads/latest_results.json', 'w') as f:
                    json.dump({
                        'data': internships_data,
                        'filename': filename,
                        'pages_processed': pages_processed
                    }, f)
            else:
                print("No internships found")
                
        except Exception as e:
            print(f"Error in search: {e}")
    
    # Run search in a separate thread
    thread = threading.Thread(target=run_search)
    thread.start()
    
    return jsonify({"message": "Search started. Check back in a few minutes for results."})

@app.route('/job-details')
def job_details():
    url = request.args.get('url', '')
    
    def run_job_details():
        try:
            job_details_data = get_job_details(setup_driver(), url)
            # Store job details
            with open('downloads/job_details.json', 'w') as f:
                json.dump(job_details_data, f)
        except Exception as e:
            print(f"Error getting job details: {e}")
    
    # Run in a separate thread
    thread = threading.Thread(target=run_job_details)
    thread.start()
    
    return jsonify({"message": "Job details fetch started."})

@app.route('/download')
def download():
    # Get the latest Excel file from downloads directory
    downloads_dir = 'downloads'
    if not os.path.exists(downloads_dir):
        return jsonify({"error": "No downloads available"})
    
    # Find the most recent Excel file
    excel_files = [f for f in os.listdir(downloads_dir) if f.endswith('.xlsx')]
    if not excel_files:
        return jsonify({"error": "No Excel files found"})
    
    latest_file = max(excel_files, key=lambda x: os.path.getctime(os.path.join(downloads_dir, x)))
    file_path = os.path.join(downloads_dir, latest_file)
    
    return send_file(file_path, as_attachment=True, download_name=latest_file)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Create downloads directory if it doesn't exist
    os.makedirs('downloads', exist_ok=True)
    
    # For production, use gunicorn
    if os.environ.get('FLASK_ENV') == 'production':
        from gunicorn.app.base import BaseApplication
        
        class StandaloneApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key, value)

            def load(self):
                return self.application

        options = {
            'bind': f"0.0.0.0:{os.environ.get('PORT', 8000)}",
            'workers': 1,
            'worker_class': 'sync',
            'timeout': 120
        }
        
        StandaloneApplication(app, options).run()
    else:
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000))) 