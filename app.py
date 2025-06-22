import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import json
from flask import Flask, render_template, request, jsonify, send_file
import time
import random

app = Flask(__name__)

def get_job_details(url):
    """Fetch job details using BeautifulSoup"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get required skills
        skills_container = soup.find("div", class_="round_tabs_container")
        required_skills = []
        
        if skills_container:
            skill_tags = skills_container.find_all("span", class_="round_tabs")
            for skill in skill_tags:
                skill_text = skill.get_text(strip=True)
                if skill_text:
                    required_skills.append(skill_text)
        
        return {
            "required_skills": required_skills
        }
    except Exception as e:
        print(f"Error fetching job details from {url}: {e}")
        return {
            "required_skills": []
        }

def get_internships(position, experience, city, max_pages=1):
    """Fetch internships using BeautifulSoup"""
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
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
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
            
            # Add random delay to be respectful to the server
            if current_page > 1:
                time.sleep(random.uniform(1, 3))
            
            # Make request
            response = requests.get(page_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if we're on a valid page by looking for the main content
            main_content = soup.find("div", class_="individual_internship")
            if not main_content:
                print(f"No internship data found on page {current_page}. Stopping search.")
                break
            
            # Extract data
            internships = soup.find_all("div", class_="individual_internship")
            
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
                    position_tag = internship.find("a", id="job_title")
                    if not position_tag:
                        continue
                        
                    position_text = position_tag.get_text(strip=True)
                    job_url = base_url + position_tag.get("href") if position_tag.get("href") else None
                    
                    # Skip if no URL or if we've seen this URL before
                    if not job_url or job_url in seen_urls:
                        continue
                    
                    seen_urls.add(job_url)  # Mark URL as seen

                    # Company
                    company_tag = internship.find("p", class_="company-name")
                    company = company_tag.get_text(strip=True) if company_tag else "N/A"

                    # Experience
                    experience_div = internship.find("div", class_="row-1-item")
                    experience_span = experience_div.find("span") if experience_div else None
                    experience_text = experience_span.get_text(strip=True) if experience_span else "N/A"
                    
                    # Extract number from experience text
                    experience_years = 0
                    if experience_text != "N/A":
                        match = re.search(r'(\d+)', experience_text)
                        if match:
                            experience_years = int(match.group(1))

                    # Get additional job details
                    job_details = get_job_details(job_url)

                    job_data = {
                        "position": position_text,
                        "company": company,
                        "url": job_url,
                        "experience": experience_years,
                        "required_skills": job_details.get("required_skills", [])
                    }
                    
                    # Only add if we have valid data
                    if position_text != "N/A" and company != "N/A":
                        all_data.append(job_data)
                        page_jobs_count += 1
                        print(f"Added: {position_text} at {company}")
                    
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
    
    pages_processed = current_page - 1
    print(f"\nTotal internships found: {len(all_data)}")
    print(f"Total pages processed: {pages_processed}")
    print(f"Unique URLs processed: {len(seen_urls)}")
    
    return all_data, pages_processed

def get_jobs(position, experience, city, max_pages=1):
    """Fetch jobs using BeautifulSoup"""
    # Format the URL with user inputs
    base_url = "https://internshala.com"
    
    # Build URL based on available parameters
    if position and city:
        url = f"{base_url}/jobs/{position}-jobs-in-{city}/"
    elif position:
        url = f"{base_url}/jobs/{position}-jobs/"
    elif city:
        url = f"{base_url}/jobs/jobs-in-{city}/"
    else:
        # If no parameters, search all jobs
        url = f"{base_url}/jobs/"
    
    all_data = []
    seen_urls = set()  # Track seen URLs to avoid duplicates
    current_page = 1
    consecutive_empty_pages = 0  # Track consecutive empty pages
    max_consecutive_empty = 3  # Stop after 3 consecutive empty pages
    
    print(f"Searching for jobs at: {url}")
    print(f"Max pages to search: {'All available' if max_pages == 0 else max_pages}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
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
            
            # Add random delay to be respectful to the server
            if current_page > 1:
                time.sleep(random.uniform(1, 3))
            
            # Make request
            response = requests.get(page_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # For jobs, look for job listings - the structure might be different
            # Try different selectors that might contain job listings
            job_selectors = [
                "div.job_listing",  # Common job listing selector
                "div.individual_job",  # Alternative selector
                "div.job-card",  # Another possible selector
                "div[class*='job']",  # Any div with 'job' in class name
                "div[class*='listing']"  # Any div with 'listing' in class name
            ]
            
            jobs = []
            for selector in job_selectors:
                jobs = soup.find_all("div", class_=selector.replace("div.", ""))
                if jobs:
                    print(f"Found jobs using selector: {selector}")
                    break
            
            # If no jobs found with specific selectors, try a more generic approach
            if not jobs:
                # Look for any div that might contain job information
                potential_jobs = soup.find_all("div", class_=lambda x: x and any(word in x.lower() for word in ['job', 'listing', 'card', 'item']))
                if potential_jobs:
                    jobs = potential_jobs
                    print(f"Found {len(jobs)} potential job listings using generic selector")
            
            if not jobs:  # No more jobs found on this page
                consecutive_empty_pages += 1
                print(f"No jobs found on page {current_page}")
                current_page += 1
                continue
            else:
                consecutive_empty_pages = 0  # Reset counter if we found jobs
                print(f"Found {len(jobs)} jobs on page {current_page}")
                
            page_jobs_count = 0  # Track jobs added from this page
            
            for job in jobs:
                try:
                    # Try to extract job information
                    # Position/Title
                    position_tag = job.find("a") or job.find("h3") or job.find("h2") or job.find("div", class_="title")
                    if not position_tag:
                        continue
                        
                    position_text = position_tag.get_text(strip=True)
                    if not position_text:
                        continue
                    
                    # Get job URL
                    job_url = None
                    if position_tag.name == "a" and position_tag.get("href"):
                        job_url = base_url + position_tag.get("href") if not position_tag.get("href").startswith("http") else position_tag.get("href")
                    else:
                        # Try to find a link within the job card
                        link_tag = job.find("a")
                        if link_tag and link_tag.get("href"):
                            job_url = base_url + link_tag.get("href") if not link_tag.get("href").startswith("http") else link_tag.get("href")
                    
                    # Skip if no URL or if we've seen this URL before
                    if not job_url or job_url in seen_urls:
                        continue
                    
                    seen_urls.add(job_url)  # Mark URL as seen

                    # Company
                    company_tag = job.find("div", class_="company") or job.find("span", class_="company") or job.find("p", class_="company")
                    company = company_tag.get_text(strip=True) if company_tag else "N/A"

                    # Salary (for jobs)
                    salary_tag = job.find("div", class_="salary") or job.find("span", class_="salary") or job.find("div", class_=lambda x: x and "salary" in x.lower())
                    salary = salary_tag.get_text(strip=True) if salary_tag else "Not specified"

                    # Experience
                    experience_tag = job.find("div", class_="experience") or job.find("span", class_="experience") or job.find("div", class_=lambda x: x and "experience" in x.lower())
                    experience_text = experience_tag.get_text(strip=True) if experience_tag else "N/A"
                    
                    # Extract number from experience text
                    experience_years = 0
                    if experience_text != "N/A":
                        match = re.search(r'(\d+)', experience_text)
                        if match:
                            experience_years = int(match.group(1))

                    # Get additional job details
                    job_details = get_job_details(job_url)

                    job_data = {
                        "position": position_text,
                        "company": company,
                        "url": job_url,
                        "experience": experience_years,
                        "salary": salary,
                        "required_skills": job_details.get("required_skills", [])
                    }
                    
                    # Only add if we have valid data
                    if position_text != "N/A" and company != "N/A":
                        all_data.append(job_data)
                        page_jobs_count += 1
                        print(f"Added: {position_text} at {company}")
                    
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
    
    pages_processed = current_page - 1
    print(f"\nTotal jobs found: {len(all_data)}")
    print(f"Total pages processed: {pages_processed}")
    print(f"Unique URLs processed: {len(seen_urls)}")
    
    return all_data, pages_processed

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    try:
        # Get parameters from request
        position = request.args.get('position', '')
        experience = request.args.get('experience', '')
        city = request.args.get('city', '')
        max_pages = int(request.args.get('max_pages', '1'))
        search_type = request.args.get('searchType', 'internship')
        
        # Run the appropriate search based on type
        if search_type == 'job':
            results, pages_processed = get_jobs(position, experience, city, max_pages)
        else:
            results, pages_processed = get_internships(position, experience, city, max_pages)
        
        # Save results to Excel
        if results:
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            df = pd.DataFrame(results)
            
            # Create filename with search parameters
            filename_parts = []
            if position:
                filename_parts.append(position)
            if city:
                filename_parts.append(city)
            if not filename_parts:
                filename_parts.append("all")
            
            excel_filename = os.path.join(downloads_dir, f"{search_type}_{'_'.join(filename_parts)}.xlsx")
            df.to_excel(excel_filename, index=False)
        
        return jsonify({
            'results': results,
            'pages_processed': pages_processed,
            'search_params': {
                'position': position,
                'experience': experience,
                'city': city,
                'max_pages': max_pages,
                'search_type': search_type
            }
        })
    except Exception as e:
        print(f"An error occurred during search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/job-details')
def job_details():
    job_url = request.args.get('url', '')
    
    if not job_url:
        return jsonify({'error': 'Missing job URL'}), 400
    
    try:
        details = get_job_details(job_url)
        
        return jsonify({
            'success': True,
            'required_skills': details.get('required_skills', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download():
    # Get the latest Excel file from downloads directory
    downloads_dir = "downloads"
    excel_files = [f for f in os.listdir(downloads_dir) if f.endswith('.xlsx')]
    if excel_files:
        latest_file = max([os.path.join(downloads_dir, f) for f in excel_files], key=os.path.getctime)
        return send_file(latest_file, as_attachment=True, download_name='results.xlsx')
    return jsonify({'error': 'No Excel file found'}), 404

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Internshala Scraper is running'})

if __name__ == "__main__":
    # Get port from environment variable (for Render) or use default
    port = int(os.environ.get('PORT', 8000))
    
    # Use production server in production environment
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
            'bind': f'0.0.0.0:{port}',
            'workers': 1,
            'worker_class': 'sync',
            'timeout': 300,
            'keepalive': 2,
        }
        
        StandaloneApplication(app, options).run()
    else:
        # Development server
        app.run(debug=True, host='0.0.0.0', port=port)
