import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import re
import os
import json
from flask import Flask, render_template, request, jsonify, send_file
import threading
import io
from datetime import datetime

app = Flask(__name__)

async def get_job_details(page, url):
    try:
        # Create a new page for job details to avoid context issues
        job_page = await page.context.new_page()
        await job_page.goto(url, wait_until="networkidle")
        # Wait for 1 second after page load
        await asyncio.sleep(1)
        
        # Get required skills
        skills = await job_page.query_selector_all("div.round_tabs_container span.round_tabs")
        required_skills = []
        for skill in skills:
            skill_text = await skill.text_content()
            if skill_text.strip():
                required_skills.append(skill_text.strip())
        
        # Close the job details page
        await job_page.close()
        return {
            "required_skills": required_skills
        }
    except Exception as e:
        print(f"Error fetching job details from {url}: {e}")
        # Make sure to close the page even if there's an error
        try:
            await job_page.close()
        except:
            pass
        return {
            "required_skills": []
        }

async def get_internships(position, experience, city, max_pages=0):
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
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
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
                    
                    # Navigate to page and wait for network idle
                    await page.goto(page_url, wait_until="networkidle")
                    # Wait for 1 second after page load
                    print("Waiting for page to load completely...")
                    await asyncio.sleep(1)
                    
                    # Check if we're on a valid page by looking for the main content
                    main_content = await page.query_selector("div.individual_internship")
                    if not main_content:
                        print(f"No internship data found on page {current_page}. Stopping search.")
                        break
                    
                    # Extract data
                    internships = await page.query_selector_all("div.individual_internship")
                    
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
                            position_tag = await internship.query_selector("a#job_title")
                            if not position_tag:
                                continue
                                
                            position = await position_tag.text_content()
                            position = position.strip()
                            job_url = base_url + await position_tag.get_attribute("href") if await position_tag.get_attribute("href") else None
                            
                            # Skip if no URL or if we've seen this URL before
                            if not job_url or job_url in seen_urls:
                                continue
                            
                            seen_urls.add(job_url)  # Mark URL as seen

                            # Company
                            company_tag = await internship.query_selector("p.company-name")
                            company = await company_tag.text_content() if company_tag else "N/A"
                            company = company.strip()

                            # Experience
                            experience_div = await internship.query_selector("div.row-1-item span")
                            experience_text = await experience_div.text_content() if experience_div else "N/A"
                            experience_text = experience_text.strip()
                            
                            # Extract number from experience text
                            experience_years = 0
                            if experience_text != "N/A":
                                match = re.search(r'(\d+)', experience_text)
                                if match:
                                    experience_years = int(match.group(1))

                            # Get additional job details
                            job_details = await get_job_details(page, job_url)

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
            
            # Keep browser open for one minute after data collection
            print("\nKeeping browser open for 1 minute to view results...")
            await asyncio.sleep(60)
            
        finally:
            # Make sure to close the browser even if there's an error
            await browser.close()
    
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
    position = request.args.get('position', '')
    experience = request.args.get('experience', '')
    city = request.args.get('city', '')
    max_pages = int(request.args.get('max_pages', '1'))
    
    # Run the search in a separate thread
    def run_search():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results, _ = loop.run_until_complete(get_internships(position, experience, city, max_pages))
        loop.close()
        return results
    
    # Run the search
    results = run_search()
    
    # Create Excel file in memory
    if results:
        df = pd.DataFrame(results)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"internships_{position}_{city}_{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    return jsonify({'results': results})

@app.route('/job-details')
def job_details():
    job_url = request.args.get('url', '')
    
    if not job_url:
        return jsonify({'error': 'Missing job URL'}), 400
    
    try:
        # Run the job details fetch in a separate thread
        def run_job_details():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            details = loop.run_until_complete(get_job_details(None, job_url))
            loop.close()
            return details
        
        details = run_job_details()
        
        return jsonify({
            'success': True,
            'required_skills': details.get('required_skills', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)
