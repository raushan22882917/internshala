import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import json
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, FileResponse, Response
import time
import random
import uvicorn
from typing import Optional
import io
from fastapi.middleware.cors import CORSMiddleware
import urllib.parse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins universally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_job_details(url):
    """Fetch job details using BeautifulSoup"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        required_skills = []

        # Method 1: Find by id 'skills-container'
        skills_container = soup.find(id="skills-container")
        if skills_container:
            skill_tags = skills_container.find_all(class_="skill") # Or other tag
            if not skill_tags:
                 skill_tags = skills_container.find_all("span") # fallback
            for skill in skill_tags:
                skill_text = skill.get_text(strip=True)
                if skill_text:
                    required_skills.append(skill_text)
        
        # Method 2: Find by heading
        if not required_skills:
            skills_heading = soup.find("h4", string=re.compile(r"Skill\(s\)\srequired", re.I))
            if skills_heading:
                skills_div = skills_heading.find_next_sibling("div")
                if skills_div:
                    skill_tags = skills_div.find_all("span", class_="round_tabs")
                    for skill in skill_tags:
                        skill_text = skill.get_text(strip=True)
                        if skill_text:
                            required_skills.append(skill_text)

        # Method 3: Original implementation as fallback
        if not required_skills:
            skills_container = soup.find("div", class_="round_tabs_container")
            if skills_container:
                skill_tags = skills_container.find_all("span", class_="round_tabs")
                for skill in skill_tags:
                    skill_text = skill.get_text(strip=True)
                    if skill_text:
                        required_skills.append(skill_text)
        
        return {
            "required_skills": list(set(required_skills)) # Remove duplicates
        }
    except Exception as e:
        print(f"Error fetching job details from {url}: {e}")
        return {
            "required_skills": []
        }

def get_listings(search_type, position, experience, city, start_page=1, end_page=1):
    """Fetch jobs or internships using BeautifulSoup"""
    base_url = "https://internshala.com"

    if search_type == 'job':
        path_segment = "jobs"
        position_suffix = "jobs"
    else:
        path_segment = "internships"
        position_suffix = "internship"

    if position and city:
        url = f"{base_url}/{path_segment}/{position}-{position_suffix}-in-{city}/"
    elif position:
        url = f"{base_url}/{path_segment}/{position}-{position_suffix}/"
    elif city:
        if search_type == 'job':
            url = f"{base_url}/{path_segment}/jobs-in-{city}/"
        else:
            url = f"{base_url}/{path_segment}/internship-in-{city}/"
    else:
        url = f"{base_url}/{path_segment}/"
    
    all_data = []
    seen_urls = set()
    consecutive_empty_pages = 0
    max_consecutive_empty = 3
    skipped_pages = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    current_page = start_page
    while consecutive_empty_pages < max_consecutive_empty and current_page <= end_page:
        try:
            page_url = url if current_page == 1 else f"{url}page-{current_page}/"
            if current_page > 1:
                time.sleep(random.uniform(1, 3))
            response = requests.get(page_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            listings = soup.select('.individual_internship, .internship_meta, .job_listing, .individual_job, .job-card')

            if not listings:
                consecutive_empty_pages += 1
                current_page += 1
                continue
            else:
                consecutive_empty_pages = 0

            for item in listings:
                try:
                    position_tag = item.find("h3", class_="profile") or item.find("div", class_="heading_4_5")
                    if position_tag:
                        position_tag = position_tag.find("a")
                    
                    if not position_tag:
                        position_tag = item.find("a") or item.find("h3") or item.find("h2") or item.find("div", class_="title")

                    if not position_tag:
                        continue
                    
                    position_text = position_tag.get_text(strip=True)
                    if not position_text:
                        continue
                        
                    href = position_tag.get("href")
                    job_url = None
                    if href:
                        if href.startswith("http"):
                            job_url = href
                        else:
                            job_url = urllib.parse.urljoin(base_url, href)
                    
                    if not job_url:
                        link_tag = item.find("a")
                        if link_tag and link_tag.get("href"):
                            href = link_tag.get("href")
                            if href.startswith("http"):
                                job_url = href
                            else:
                                job_url = urllib.parse.urljoin(base_url, href)

                    if not job_url or job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)

                    company_tag = item.find("p", class_="company-name") or item.find("div", class_="company") or item.find("span", class_="company") or item.find("p", class_="company")
                    company = company_tag.get_text(strip=True) if company_tag else "N/A"
                    
                    experience_div = item.find("div", class_="row-1-item")
                    experience_span = experience_div.find("span") if experience_div else None
                    experience_text = experience_span.get_text(strip=True) if experience_span else "N/A"
                    
                    if experience_text == "N/A":
                        experience_tag = item.find("div", class_="experience") or item.find("span", class_="experience") or item.find("div", class_=lambda x: x and "experience" in x.lower())
                        experience_text = experience_tag.get_text(strip=True) if experience_tag else "N/A"

                    experience_years = 0
                    if experience_text != "N/A":
                        match = re.search(r'(\d+)', experience_text)
                        if match:
                            experience_years = int(match.group(1))

                    job_details = get_job_details(job_url)

                    job_data = {
                        "position": position_text,
                        "company": company,
                        "url": job_url,
                        "experience": experience_years,
                        "required_skills": job_details.get("required_skills", [])
                    }

                    if search_type == 'job':
                        salary_tag = item.find("div", class_="salary") or item.find("span", class_="salary") or item.find("div", class_=lambda x: x and "salary" in x.lower())
                        salary = salary_tag.get_text(strip=True) if salary_tag else "Not specified"
                        job_data["salary"] = salary

                    if position_text != "N/A" and company != "N/A":
                        all_data.append(job_data)
                except Exception as e:
                    continue
            current_page += 1
        except Exception as e:
            skipped_pages.append(current_page)
            current_page += 1
            
    pages_processed = current_page - start_page
    return all_data, pages_processed, skipped_pages

@app.get('/search')
def search(
    position: Optional[str] = Query(None),
    experience: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    start_page: int = Query(1),
    end_page: int = Query(1),
    search_type: str = Query('internship', enum=['internship', 'job'])
):
    results, pages_processed, skipped_pages = get_listings(search_type, position, experience, city, start_page, end_page)
    return {
        'results': results,
        'pages_processed': pages_processed,
        'skipped_pages': skipped_pages,
        'search_params': {
            'position': position,
            'experience': experience,
            'city': city,
            'start_page': start_page,
            'end_page': end_page,
            'search_type': search_type
        }
    }

@app.get('/job-details')
def job_details(url: str = Query(...)):
    if not url:
        return JSONResponse(content={'error': 'Missing job URL'}, status_code=400)
    
    try:
        details = get_job_details(url)
        
        return {
            'success': True,
            'required_skills': details.get('required_skills', [])
        }
    except Exception as e:
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get('/download_csv')
def download_csv(
    position: Optional[str] = Query(None),
    experience: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    start_page: int = Query(1),
    end_page: int = Query(1),
    search_type: str = Query('internship', enum=['internship', 'job'])
):
    results, _, skipped_pages = get_listings(search_type, position, experience, city, start_page, end_page)
    if not results:
        return JSONResponse(content={'error': 'No results to download for the given criteria'}, status_code=404)
    df = pd.DataFrame(results)
    filename_parts = []
    if position:
        filename_parts.append(position)
    if city:
        filename_parts.append(city)
    if not filename_parts:
        filename_parts.append("all")
    csv_filename = f"{search_type}_{'_'.join(filename_parts)}.csv"
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    headers = {
        'Content-Disposition': f'attachment; filename="{csv_filename}"'
    }
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers=headers
    )

@app.get('/health')
def health():
    return {'status': 'healthy', 'message': 'Internshala Scraper is running'}

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run("app:app", host='0.0.0.0', port=port, reload=True)
