import streamlit as st
import pandas as pd
from PIL import Image
import base64
import time
import re
import pdfplumber
from docx import Document
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Set page configuration
st.set_page_config(
    page_title="Career Compass - Resume Parser & Job Matcher",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance the UI
def add_custom_css():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 600;
        }
        .step-header {
            color: #0D47A1;
            margin-top: 0;
            margin-bottom: 1.5rem;
            font-weight: 600;
            border-bottom: 2px solid #1E88E5;
            padding-bottom: 10px;
        }
        .subheader {
            color: #1976D2;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 500;
        }
        .info-box {
            background-color: #E3F2FD;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #1E88E5;
            margin-bottom: 1rem;
        }
        .success-box {
            background-color: #E8F5E9;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #4CAF50;
            margin-bottom: 1rem;
        }
        .warning-box {
            background-color: #FFF8E1;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #FFC107;
            margin-bottom: 1rem;
        }
        .error-box {
            background-color: #FFEBEE;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #F44336;
            margin-bottom: 1rem;
        }
        .nav-button {
            text-align: center;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            background-color: #1E88E5;
            color: white;
            font-weight: 500;
            margin: 0.5rem;
            cursor: pointer;
            border: none;
        }
        .back-button {
            background-color: #78909C;
        }
        .card {
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            background-color: white;
        }
        .result-card {
            border-left: 5px solid #1E88E5;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #F5F7FA;
            border-radius: 5px;
        }
        .metric-container {
            text-align: center;
            padding: 1rem;
            background-color: #E3F2FD;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: #1976D2;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #546E7A;
        }
        .match-high {
            background-color: #E8F5E9;
            border-left: 5px solid #4CAF50;
        }
        .match-medium {
            background-color: #FFF8E1;
            border-left: 5px solid #FFC107;
        }
        .match-low {
            background-color: #FFEBEE;
            border-left: 5px solid #F44336;
        }
        .progress-container {
            margin-bottom: 2rem;
        }
        .stProgress > div > div > div > div {
            background-color: #1E88E5;
        }
        .resume-field {
            margin-bottom: 0.8rem;
        }
        .resume-field-label {
            font-weight: 500;
            color: #546E7A;
        }
        .resume-field-value {
            margin-left: 0.5rem;
        }
        .stExpander {
            border: 1px solid #E0E0E0;
            border-radius: 5px;
        }
        .skill-chip {
            display: inline-block;
            padding: 5px 10px;
            background-color: #E3F2FD;
            color: #1976D2;
            border-radius: 15px;
            margin: 3px;
            font-size: 0.85rem;
        }
        .motivation-slider {
            padding: 1rem;
            background-color: #F5F7FA;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .footer {
            text-align: center;
            padding: 1rem;
            color: #78909C;
            font-size: 0.9rem;
            margin-top: 3rem;
        }
        div[data-testid="stFileUploadDropzone"] {
            padding: 2rem;
            border: 2px dashed #1E88E5;
            border-radius: 5px;
            background-color: #E3F2FD;
        }
    </style>
    """, unsafe_allow_html=True)

# Add logo and app header function
def show_app_header():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-header">Career Compass</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; margin-top: -1.5rem; color: #546E7A; font-size: 1.1rem;">Resume Parser & Job Matching Assistant</p>', unsafe_allow_html=True)

# Show progress indicator
def show_progress():
    step_titles = ["Upload Resume", "Career Goals", "Motivation Matrix", "Job Matching", "Results"]
    progress_value = st.session_state.current_step / len(step_titles)
    
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.progress(progress_value)
    
    cols = st.columns(len(step_titles))
    for i, (col, title) in enumerate(zip(cols, step_titles)):
        with col:
            if i+1 < st.session_state.current_step:
                st.markdown(f'<div style="text-align: center; color: #1E88E5; font-weight: 600;">{title} ✓</div>', unsafe_allow_html=True)
            elif i+1 == st.session_state.current_step:
                st.markdown(f'<div style="text-align: center; color: #1E88E5; font-weight: 600; text-decoration: underline;">{title}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="text-align: center; color: #9E9E9E;">{title}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Resume Parsing Functions ----------------
def parse_resume(file):
    file_extension = file.name.split('.')[-1].lower()
    if file_extension == 'pdf':
        text = extract_text_from_pdf(file)
    elif file_extension == 'docx':
        text = extract_text_from_docx(file)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")
    
    parsed_data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": extract_location(text),
        "skills": extract_skills(text),
        "languages": extract_languages(text),
        "experience": extract_experience(text),
        "qualifications": extract_qualifications(text),
        "employment_history": extract_employment_history(text),
        "profile_summary": extract_profile_summary(text)
    }
    return parsed_data

def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

def extract_text_from_docx(file):
    try:
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from DOCX: {e}")

def extract_name(text):
    lines = text.split("\n")
    possible_names = [line for line in lines[:5] if len(line.split()) in [2, 3]]
    return possible_names[0] if possible_names else "Unknown"

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    return match.group(0) if match else "Not Found"

def extract_location(text):
    lines = text.split("\n")
    location_section_start = 0
    for i, line in enumerate(lines):
        if "Details" in line:
            location_section_start = i
            break
    for i in range(location_section_start, min(location_section_start + 10, len(lines))):
        if lines[i] in ["United States", "USA", "U.S.", "U.S.A."]:
            city_line = i - 1 if i > 0 else 0
            return f"{lines[city_line]}, {lines[i]}"
    city_state_pattern = re.search(r"([A-Za-z\s]+),?\s+([A-Za-z\s]+)", text[:500])
    if city_state_pattern:
        return city_state_pattern.group(0)
    return "Location Not Found"

def extract_skills(text):
    skill_keywords = [
        "Python", "Flask", "Django", "Machine Learning", "SQL", "Java", "React", "AWS",
        "JavaScript", "HTML", "CSS", "TensorFlow", "Pandas", "NumPy", "Docker", "Kubernetes",
        "Git", "Azure", "Linux", "Node.js", "C#", "C++", "Go", "PHP", "TypeScript", "Tableau", 
        "Power BI", "Jupyter", "Spark", "Hadoop", "Scala", "Cloud", "Vagrant", "LLMs", "GPT",
        "Re-enforcement", "Site Reliability", "DevOps", "Microservices", "NOSQL", 
        "Apache Kafka", "Apache Webserver", "Blockchain", "Performance engineering",
        "AI model Training", "Data Science", "Feature Engineering", "AI", "Shell Script", 
        "Intrusion Detection", "Matlab", "R", "Agile", "SDLC"
    ]
    skills_section_match = re.search(r"Skills\n(.*?)(?:\n\n|\nProfile|\nEmployment)", text, re.DOTALL)
    skills_text = skills_section_match.group(1) if skills_section_match else text
    found_skills = [skill for skill in skill_keywords if re.search(rf"\b{skill}\b", text, re.IGNORECASE)]
    additional_skills = [line.strip() for line in skills_text.split("\n") if line.strip() and len(line.strip()) > 2]
    all_skills = list(set(found_skills + additional_skills))
    return all_skills

def extract_languages(text):
    languages_section = re.search(r"Languages\n(.*?)(?:\n\n|\nEducation|\nEmployment)", text, re.DOTALL)
    if languages_section:
        languages_text = languages_section.group(1)
        languages = [lang.strip() for lang in languages_text.split("\n") if lang.strip()]
        return languages
    common_languages = ["English", "Spanish", "French", "German", "Chinese", "Japanese", 
                        "Arabic", "Hindi", "Bengali", "Russian", "Portuguese"]
    found_languages = [lang for lang in common_languages if re.search(rf"\b{lang}\b", text)]
    return found_languages if found_languages else ["Not Found"]

def extract_experience(text):
    years_of_experience = re.findall(r"(\d{1,2})\+?\s*years?(?:\s+of\s+experience)?", text)
    if years_of_experience:
        max_experience = max(map(int, years_of_experience))
        return f"{max_experience} years of experience"
    employment_pattern = re.findall(r"(\w+\s+\d{4})\s*[—–-]\s*(\w+\s+\d{4}|PRESENT)", text, re.IGNORECASE)
    if employment_pattern:
        return f"{len(employment_pattern)} employment periods found"
    return "Experience not found"

def extract_qualifications(text):
    qualification_keywords = [
        "Bachelor's", "Master's", "PhD", "Degree", "Certification", "Diploma", "BSc", "MSc", 
        "B.A.", "M.A.", "BTech", "MTech", "MBA", "Engineering", "Architecture", "Computer Science", 
        "Information Technology", "Data Science", "Machine Learning", "AI", "Software Engineering",
        "CSSA", "Certified", "Business", "MIS", "University"
    ]
    education_section = re.search(r"Education\n(.*?)(?:\n\n|$)", text, re.DOTALL)
    if education_section:
        edu_text = education_section.group(1)
        education_entries = [line.strip() for line in edu_text.split("\n") if line.strip() 
                            and any(keyword in line for keyword in ["Bachelor", "Master", "PhD", "Degree"])]
        if education_entries:
            return education_entries
    found_qualifications = [qual for qual in qualification_keywords if re.search(rf"\b{qual}\b", text, re.IGNORECASE)]
    return list(set(found_qualifications)) if found_qualifications else ["Not Found"]

def extract_employment_history(text):
    employment_section = re.search(r"Employment History\n(.*?)(?:\nEducation|\n\nEducation|$)", text, re.DOTALL | re.IGNORECASE)
    if not employment_section:
        return ["Employment history not found"]
    employment_text = employment_section.group(1)
    job_pattern = re.findall(r"(.*?),\s+(.*?),\s+(.*?)\n(\w+\s+\d{4})\s*[—–-]\s*(\w+\s+\d{4}|PRESENT)", 
                             employment_text, re.IGNORECASE | re.MULTILINE)
    if not job_pattern:
        job_pattern = re.findall(r"(.*?),\s+(.*?)\n(\w+\s+\d{4})\s*[—–-]\s*(\w+\s+\d{4}|PRESENT)", 
                                employment_text, re.IGNORECASE | re.MULTILINE)
    if not job_pattern:
        lines = employment_text.split("\n")
        jobs = []
        for i, line in enumerate(lines):
            if re.search(r"\b(architect|analyst|lead|principal|manager|director|engineer)\b", line, re.IGNORECASE):
                if i < len(lines) - 1 and re.search(r"\d{4}", lines[i+1]):
                    jobs.append(line)
        return jobs if jobs else ["Could not parse employment details"]
    
    formatted_jobs = []
    for job in job_pattern:
        if len(job) == 5:
            formatted_jobs.append(f"{job[0]} at {job[1]}, {job[2]} ({job[3]} - {job[4]})")
        elif len(job) == 4:
            formatted_jobs.append(f"{job[0]} at {job[1]} ({job[2]} - {job[3]})")
    return formatted_jobs

def extract_profile_summary(text):
    profile_section = re.search(r"Profile\n(.*?)(?:\nEmployment|\n\nEmployment)", text, re.DOTALL)
    if profile_section:
        profile_text = profile_section.group(1).strip()
        if len(profile_text) > 500:
            return profile_text[:497] + "..."
        return profile_text
    alt_section = re.search(r"(Summary|About)\n(.*?)(?:\n\n|\nSkills|\nExperience)", text, re.DOTALL)
    if alt_section:
        return alt_section.group(2).strip()
    return "Profile summary not found"

# Display parsed resume in a nice format
def display_parsed_resume(parsed_data):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<h3 style="text-align: center; color: #1976D2; margin-bottom: 1rem;">{parsed_data["name"]}</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="resume-field">', unsafe_allow_html=True)
        st.markdown('<span class="resume-field-label">📧 Email:</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="resume-field-value">{parsed_data["email"]}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="resume-field">', unsafe_allow_html=True)
        st.markdown('<span class="resume-field-label">📱 Phone:</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="resume-field-value">{parsed_data["phone"]}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="resume-field">', unsafe_allow_html=True)
        st.markdown('<span class="resume-field-label">📍 Location:</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="resume-field-value">{parsed_data["location"]}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="resume-field">', unsafe_allow_html=True)
        st.markdown('<span class="resume-field-label">⏱️ Experience:</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="resume-field-value">{parsed_data["experience"]}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="resume-field">', unsafe_allow_html=True)
        st.markdown('<span class="resume-field-label">🎓 Qualifications:</span>', unsafe_allow_html=True)
        qualifications_list = "".join([f"<li>{qual}</li>" for qual in parsed_data["qualifications"][:3]])
        st.markdown(f'<ul class="resume-field-value">{qualifications_list}</ul>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="resume-field">', unsafe_allow_html=True)
        st.markdown('<span class="resume-field-label">🗣️ Languages:</span>', unsafe_allow_html=True)
        languages_text = ", ".join(parsed_data["languages"][:3])
        st.markdown(f'<span class="resume-field-value">{languages_text}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="resume-field" style="margin-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<span class="resume-field-label">💼 Work History:</span>', unsafe_allow_html=True)
    employment_list = "".join([f"<li>{job}</li>" for job in parsed_data["employment_history"][:3]])
    st.markdown(f'<ul class="resume-field-value">{employment_list}</ul>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="resume-field">', unsafe_allow_html=True)
    st.markdown('<span class="resume-field-label">🧩 Skills:</span>', unsafe_allow_html=True)
    skills_html = ""
    for skill in parsed_data["skills"][:10]:
        skills_html += f'<div class="skill-chip">{skill}</div>'
    st.markdown(f'<div class="resume-field-value" style="margin-top: 0.5rem;">{skills_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if parsed_data["profile_summary"] and parsed_data["profile_summary"] != "Profile summary not found":
        st.markdown('<div class="resume-field">', unsafe_allow_html=True)
        st.markdown('<span class="resume-field-label">📄 Profile Summary:</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="resume-field-value" style="margin-top: 0.5rem; font-style: italic; color: #555;">{parsed_data["profile_summary"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("See Full Resume Details"):
        st.json(parsed_data)

# ---------------- Job Scraping and Matching Functions ----------------

def get_chrome_binary():
    possible_paths = [
        "/opt/google/chrome/chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def init_chrome_driver():
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    chrome_binary = get_chrome_binary()
    if not chrome_binary:
        raise Exception("No Chrome or Chromium binary found!")
    options.binary_location = chrome_binary
    if "google/chrome" in chrome_binary:
        driver_version = "133.0.6943.126"
    else:
        driver_version = "120.0.6099.224"
    driver_path = ChromeDriverManager(driver_version=driver_version).install()
    os.chmod(driver_path, 0o755)
    service = ChromeService(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def init_firefox_driver():
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver_path = GeckoDriverManager().install()
    service = FirefoxService(driver_path)
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def init_driver():
    try:
        driver = init_chrome_driver()
        print("Initialized Chrome/Chromium driver.")
        return driver
    except Exception as e:
        print("Chrome driver initialization failed, trying Firefox. Error:", e)
        driver = init_firefox_driver()
        print("Initialized Firefox driver.")
        return driver

def scrape_dice(job_role, driver, preferred_location="", preferred_salary=""):
    print(f"🔍 Scraping Dice for: {job_role}")
    formatted_role = job_role.replace(" ", "%20")
    # Use location and salary from user preferences if provided
    loc_param = preferred_location if preferred_location and preferred_location != "Select Location" else ""
    salary_param = preferred_salary if preferred_salary and preferred_salary != "Select Salary Range" else ""
    url = f"https://www.dice.com/jobs?q={formatted_role}&location={loc_param}&salary={salary_param}&countryCode=US&page=1&pageSize=20&language=en"
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_elements = soup.find_all("div", class_="card")
    jobs = []
    for job in job_elements:
        title_element = job.find("h5")
        link_element = job.find("a", href=True)
        location_element = job.find("span", attrs={"data-cy": "search-result-location"})
        company_name = job.find("a", attrs={"aria-label": lambda x: x and "company page for" in x})
        job_type_element = job.find("span", attrs={"data-cy": "search-result-employment-type"})
        posted_time_element = job.find("span", attrs={"data-cy": "card-posted-date"})
        updated_time_element = job.find("span", attrs={"data-cy": "card-modified-date"})
        description_element = job.find("div", attrs={"data-cy": "card-summary"})
        if title_element and link_element:
            jobs.append({
                "Job Role": job_role,
                "Title": title_element.text.strip(),
                "Apply Link": link_element["href"],
                "Location": location_element.text.strip() if location_element else "N/A",
                "Job Type": job_type_element.text.strip() if job_type_element else "N/A",
                "Posted Time": posted_time_element.text.strip() if posted_time_element else "N/A",
                "Updated Time": updated_time_element.text.strip() if updated_time_element else "N/A",
                "Description": description_element.text.strip() if description_element else "N/A",
                "Company Name": company_name.text.strip() if company_name else "N/A"
            })
    return jobs

def extract_career_goal_keywords(career_goals):
    if not career_goals:
        return {}
    goals_data = {
        "job_titles": [],
        "locations": [],
        "work_preferences": [],
        "industries": []
    }
    job_title_patterns = [
        r"(?:seeking|looking for|interested in)(?:\s+a)?\s+(?:role|position|job|career)?\s+(?:as|in)?\s+(?:an?)?\s+((?:senior|junior|lead|principal|staff)?\s*[a-z\s]+(?:engineer|developer|architect|manager|analyst|scientist|designer))",
        r"(?:senior|junior|lead|principal|staff)?\s*([a-z\s]+(?:engineer|developer|architect|manager|analyst|scientist|designer))\s+(?:role|position|job)",
        r"(?:become|be)\s+(?:a|an)\s+((?:senior|junior|lead|principal|staff)?\s*[a-z\s]+(?:engineer|developer|architect|manager|analyst|scientist|designer))"
    ]
    for pattern in job_title_patterns:
        matches = re.findall(pattern, career_goals.lower())
        if matches:
            goals_data["job_titles"].extend([title.strip().title() for title in matches])
    common_titles = [
        "software engineer", "data scientist", "machine learning engineer", 
        "devops engineer", "full stack developer", "frontend developer", 
        "backend developer", "site reliability engineer", "cloud engineer",
        "ai engineer", "web developer", "product manager", "project manager",
        "ux designer", "systems engineer", "solutions architect",
        "data engineer", "ml engineer", "research scientist"
    ]
    for title in common_titles:
        if title in career_goals.lower():
            goals_data["job_titles"].append(title.title())
    location_patterns = [
        r"(?:in|near|around|based in)\s+([a-z\s]+(?:area|city|region|county))",
        r"(?:in|near|around|based in)\s+([a-z]+,\s*[a-z]{2})",
        r"(?:in|near|around|based in)\s+([a-z\s]+)"
    ]
    for pattern in location_patterns:
        matches = re.findall(pattern, career_goals.lower())
        if matches:
            goals_data["locations"].extend([loc.strip().title() for loc in matches])
    common_cities = ["new york", "san francisco", "seattle", "boston", "austin", "chicago", 
                     "los angeles", "denver", "washington dc", "atlanta", "dallas"]
    for city in common_cities:
        if city in career_goals.lower():
            goals_data["locations"].append(city.title())
    preferences = ["remote", "hybrid", "onsite", "in-office", "work from home", "flexible", "part-time", "full-time"]
    for pref in preferences:
        if pref in career_goals.lower():
            goals_data["work_preferences"].append(pref.title())
    
    industries = ["tech", "finance", "healthcare", "education", "manufacturing", 
                 "retail", "startups", "enterprise", "government", "non-profit", 
                 "consulting", "e-commerce", "gaming", "entertainment"]
    for ind in industries:
        if ind in career_goals.lower():
            goals_data["industries"].append(ind.title())
    
    # Remove duplicates
    for key in goals_data:
        goals_data[key] = list(set(goals_data[key]))
    
    return goals_data

def calculate_job_match_score(job, resume_data, motivation_data):
    match_score = 0
    match_reasons = []
    
    # Check for skill matches
    job_description = job.get("Description", "").lower()
    resume_skills = [skill.lower() for skill in resume_data.get("skills", [])]
    matched_skills = []
    
    for skill in resume_skills:
        if skill.lower() in job_description.lower():
            match_score += 5
            matched_skills.append(skill)
    
    if matched_skills:
        match_reasons.append(f"Found {len(matched_skills)} matching skills including {', '.join(matched_skills[:3])}")
    
    # Check job title match
    job_title = job.get("Title", "").lower()
    resume_job_titles = extract_career_goal_keywords(resume_data.get("profile_summary", "")).get("job_titles", [])
    for title in resume_job_titles:
        if title.lower() in job_title:
            match_score += 10
            match_reasons.append(f"Job title '{title}' matches your career goals")
            break
    
    # Check location match
    job_location = job.get("Location", "").lower()
    if resume_data.get("location", "").lower() in job_location:
        match_score += 5
        match_reasons.append("Location matches your resume")
    
    # Consider motivation factors
    if motivation_data:
        if job.get("Job Type", "").lower() == "remote" and motivation_data.get("remote_preference", 0) > 7:
            match_score += 5
            match_reasons.append("Remote work aligns with your preferences")
        
        if "senior" in job_title and motivation_data.get("leadership", 0) > 7:
            match_score += 5
            match_reasons.append("Leadership opportunity aligns with your goals")
        
        if motivation_data.get("work_life_balance", 0) > 8 and "flexible" in job_description:
            match_score += 5
            match_reasons.append("Flexible schedule aligns with your work-life balance priority")
    
    # Max score is 100
    normalized_score = min(int((match_score / 30) * 100), 100)
    
    return {
        "score": normalized_score,
        "reasons": match_reasons
    }

# ---------------- Main App Functions ----------------

# Initialize session state variables
def init_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'parsed_resume' not in st.session_state:
        st.session_state.parsed_resume = None
    if 'career_goals' not in st.session_state:
        st.session_state.career_goals = ""
    if 'motivation_data' not in st.session_state:
        st.session_state.motivation_data = {}
    if 'job_matches' not in st.session_state:
        st.session_state.job_matches = []
    if 'match_complete' not in st.session_state:
        st.session_state.match_complete = False

def navigation_buttons():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.current_step > 1:
            if st.button("← Previous Step", key="prev_button"):
                st.session_state.current_step -= 1
                st.rerun()
    
    with col3:
        if st.session_state.current_step < 5 and ((st.session_state.current_step == 1 and st.session_state.parsed_resume) or
                                            (st.session_state.current_step == 2 and st.session_state.career_goals) or
                                            (st.session_state.current_step == 3 and st.session_state.motivation_data) or
                                            (st.session_state.current_step == 4 and st.session_state.job_matches)):
            if st.button("Next Step →", key="next_button"):
                st.session_state.current_step += 1
                st.rerun()

# Step 1: Resume Upload & Parsing
def resume_upload_step():
    st.markdown('<h2 class="step-header">Step 1: Upload Your Resume</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    To get started, please upload your resume in PDF or DOCX format. The system will automatically extract key information including:
    - Personal details (name, contact info)
    - Skills and qualifications
    - Work experience and education
    - Professional summary
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        with st.spinner("Analyzing your resume..."):
            try:
                parsed_data = parse_resume(uploaded_file)
                st.session_state.parsed_resume = parsed_data
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown("✅ Resume successfully parsed! Here's what we found:")
                st.markdown('</div>', unsafe_allow_html=True)
                display_parsed_resume(parsed_data)
            except Exception as e:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.markdown(f"❌ Error parsing resume: {str(e)}")
                st.markdown("Please make sure the file is not corrupted and try again.")
                st.markdown('</div>', unsafe_allow_html=True)

# Step 2: Career Goals
def career_goals_step():
    st.markdown('<h2 class="step-header">Step 2: Career Goals & Preferences</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    Tell us about your career aspirations and preferences. This information will help us find jobs that align with your goals.
    Please include details about:
    - Desired job roles or titles
    - Preferred locations or remote work preferences
    - Industry preferences
    - Career progression goals
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    career_goals = st.text_area("Describe your career goals and preferences", 
                             value=st.session_state.career_goals,
                             height=200,
                             placeholder="Example: I'm seeking a Senior Software Engineer role in a tech company, preferably in Seattle or remote. I'm interested in AI/ML and want to grow into a technical leadership position...")
    
    # Save career goals when user inputs them
    if career_goals != st.session_state.career_goals:
        st.session_state.career_goals = career_goals
    
    # Extract and display keywords
    if st.session_state.career_goals:
        extracted_keywords = extract_career_goal_keywords(st.session_state.career_goals)
        
        if any(extracted_keywords.values()):
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("✅ Here's what we understand about your career goals:")
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if extracted_keywords["job_titles"]:
                    st.markdown("**Desired Job Roles:**")
                    for title in extracted_keywords["job_titles"]:
                        st.markdown(f"- {title}")
                
                if extracted_keywords["locations"]:
                    st.markdown("**Preferred Locations:**")
                    for location in extracted_keywords["locations"]:
                        st.markdown(f"- {location}")
            
            with col2:
                if extracted_keywords["work_preferences"]:
                    st.markdown("**Work Preferences:**")
                    for pref in extracted_keywords["work_preferences"]:
                        st.markdown(f"- {pref}")
                
                if extracted_keywords["industries"]:
                    st.markdown("**Industries of Interest:**")
                    for industry in extracted_keywords["industries"]:
                        st.markdown(f"- {industry}")
        else:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown("""
            ⚠️ We couldn't extract specific details from your career goals.
            Try adding more concrete information about desired job titles, locations, or work preferences.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

# Step 3: Motivation Matrix
def motivation_matrix_step():
    st.markdown('<h2 class="step-header">Step 3: Motivation Matrix</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    Rate how important each factor is to you in your next job. This will help us prioritize job matches that align with your personal motivations.
    
    Scale: 1 (Not important) to 10 (Extremely important)
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    motivation_factors = {
        "salary": "Competitive Salary",
        "remote_preference": "Remote Work Options",
        "work_life_balance": "Work-Life Balance",
        "growth_opportunities": "Career Growth & Learning",
        "company_culture": "Company Culture & Values",
        "job_security": "Job Security & Stability",
        "leadership": "Leadership Opportunities",
        "challenge": "Challenging & Interesting Work",
        "industry": "Industry/Domain Interest",
        "impact": "Meaningful Impact & Purpose"
    }
    
    motivation_data = {}
    
    st.markdown('<div class="motivation-slider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    i = 0
    for key, label in motivation_factors.items():
        if i % 2 == 0:
            with col1:
                value = st.slider(
                    label, 
                    min_value=1, 
                    max_value=10, 
                    value=st.session_state.motivation_data.get(key, 5),
                    key=f"slider_{key}"
                )
                motivation_data[key] = value
        else:
            with col2:
                value = st.slider(
                    label, 
                    min_value=1, 
                    max_value=10, 
                    value=st.session_state.motivation_data.get(key, 5),
                    key=f"slider_{key}"
                )
                motivation_data[key] = value
        i += 1
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional job preferences
    st.markdown('<div class="subheader">Additional Job Preferences</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        experience_level = st.selectbox(
            "Experience Level", 
            ["Entry Level", "Mid Level", "Senior", "Management", "Executive"],
            index=2 if st.session_state.motivation_data.get("experience_level") == "Senior" else 
                 3 if st.session_state.motivation_data.get("experience_level") == "Management" else
                 4 if st.session_state.motivation_data.get("experience_level") == "Executive" else
                 1 if st.session_state.motivation_data.get("experience_level") == "Mid Level" else 0
        )
        motivation_data["experience_level"] = experience_level
        
        job_type = st.selectbox(
            "Job Type",
            ["Full-Time", "Part-Time", "Contract", "Freelance", "Internship"],
            index=["Full-Time", "Part-Time", "Contract", "Freelance", "Internship"].index(
                st.session_state.motivation_data.get("job_type", "Full-Time"))
        )
        motivation_data["job_type"] = job_type
    
    with col2:
        preferred_location = st.selectbox(
            "Preferred Location",
            ["Select Location", "Remote", "Hybrid", "On-site", "Any"],
            index=["Select Location", "Remote", "Hybrid", "On-site", "Any"].index(
                st.session_state.motivation_data.get("preferred_location", "Select Location"))
        )
        motivation_data["preferred_location"] = preferred_location
        
        preferred_salary = st.selectbox(
            "Desired Salary Range",
            ["Select Salary Range", "$50-75K", "$75-100K", "$100-125K", "$125-150K", "$150-200K", "$200K+"],
            index=["Select Salary Range", "$50-75K", "$75-100K", "$100-125K", "$125-150K", "$150-200K", "$200K+"].index(
                st.session_state.motivation_data.get("preferred_salary", "Select Salary Range"))
        )
        motivation_data["preferred_salary"] = preferred_salary
    
    # Save motivation data
    st.session_state.motivation_data = motivation_data
    
    # Display top motivators
    if motivation_data:
        top_motivators = sorted(
            [(key, value) for key, value in motivation_data.items() if key in motivation_factors], 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("✅ Your top 3 motivators:")
        for key, value in top_motivators:
            st.markdown(f"- **{motivation_factors[key]}** (Importance: {value}/10)")
        st.markdown('</div>', unsafe_allow_html=True)

# Step 4: Job Matching
def job_matching_step():
    st.markdown('<h2 class="step-header">Step 4: Job Matching</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    Now let's find jobs that match your profile and preferences. We'll search for relevant positions based on your skills, 
    experience, and the career goals you've shared with us.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not st.session_state.match_complete:
        job_roles_to_search = []
        
        # Extract job titles from career goals
        career_keywords = extract_career_goal_keywords(st.session_state.career_goals)
        if career_keywords.get("job_titles"):
            job_roles_to_search.extend(career_keywords.get("job_titles"))
        
        # Add roles based on skills
        if st.session_state.parsed_resume and st.session_state.parsed_resume.get("skills"):
            skills = st.session_state.parsed_resume.get("skills")
            if any(skill in ["Python", "Java", "JavaScript", "C++", "C#"] for skill in skills):
                job_roles_to_search.append("Software Engineer")
            if any(skill in ["Machine Learning", "TensorFlow", "PyTorch", "Deep Learning"] for skill in skills):
                job_roles_to_search.append("Machine Learning Engineer")
            if any(skill in ["AWS", "Azure", "GCP", "Cloud"] for skill in skills):
                job_roles_to_search.append("Cloud Engineer")
        
        # Ensure we have at least one job role to search
        if not job_roles_to_search:
            job_roles_to_search = ["Software Engineer", "Data Scientist", "Full Stack Developer"]
        
        # Remove duplicates and limit to top 3
        job_roles_to_search = list(set(job_roles_to_search))[:3]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_roles = st.multiselect(
                "Select job roles to search for:",
                job_roles_to_search + ["DevOps Engineer", "Data Engineer", "Frontend Developer", "Backend Developer"],
                default=job_roles_to_search
            )
        
        with col2:
            max_jobs = st.number_input("Maximum number of jobs per role:", min_value=1, max_value=10, value=3)
        
        if st.button("Find Matching Jobs", key="find_jobs_button"):
            if selected_roles:
                with st.spinner("Searching for matching jobs... This may take a few moments"):
                    try:
                        driver = init_driver()
                        all_jobs = []
                        
                        for role in selected_roles:
                            jobs = scrape_dice(
                                role, 
                                driver,
                                preferred_location=st.session_state.motivation_data.get("preferred_location", ""),
                                preferred_salary=st.session_state.motivation_data.get("preferred_salary", "")
                            )
                            jobs_with_scores = []
                            
                            for job in jobs:
                                match_info = calculate_job_match_score(
                                    job, 
                                    st.session_state.parsed_resume, 
                                    st.session_state.motivation_data
                                )
                                job["match_score"] = match_info["score"]
                                job["match_reasons"] = match_info["reasons"]
                                jobs_with_scores.append(job)
                            
                            # Sort by match score and take top N
                            sorted_jobs = sorted(jobs_with_scores, key=lambda x: x["match_score"], reverse=True)
                            all_jobs.extend(sorted_jobs[:max_jobs])
                        
                        driver.quit()
                        st.session_state.job_matches = all_jobs
                        st.session_state.match_complete = True
                        st.rerun()
                    except Exception as e:
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.markdown(f"❌ Error searching for jobs: {str(e)}")
                        st.markdown("Please try again later or contact support if the issue persists.")
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.markdown("⚠️ Please select at least one job role to search for.")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        if st.session_state.job_matches:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown(f"✅ Found {len(st.session_state.job_matches)} matching jobs based on your profile and preferences!")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Start a new job search", key="new_search_button"):
                st.session_state.match_complete = False
                st.session_state.job_matches = []
                st.rerun()
        else:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown("⚠️ No matching jobs found. Please try different search criteria.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Try again with different criteria", key="try_again_button"):
                st.session_state.match_complete = False
                st.rerun()

# Step 5: Results & Recommendations
def results_step():
    st.markdown('<h2 class="step-header">Step 5: Results & Recommendations</h2>', unsafe_allow_html=True)
    
    if not st.session_state.job_matches:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("⚠️ No job matches found. Please go back to the previous step and search for jobs.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Calculate aggregate statistics
    avg_match_score = sum(job["match_score"] for job in st.session_state.job_matches) / len(st.session_state.job_matches)
    top_match = max(st.session_state.job_matches, key=lambda x: x["match_score"])
    job_roles = set(job["Job Role"] for job in st.session_state.job_matches)
    locations = set(job["Location"] for job in st.session_state.job_matches)
    
    # Display match metrics
    st.markdown('<div class="subheader">Match Summary</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(st.session_state.job_matches)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Matching Jobs Found</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{int(avg_match_score)}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Average Match Score</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{top_match["match_score"]}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Highest Match Score</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter options
    st.markdown('<div class="subheader">Filter Results</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_role = st.selectbox("Job Role", ["All"] + list(job_roles))
    
    with col2:
        selected_location = st.selectbox("Location", ["All"] + list(locations))
    
    with col3:
        match_threshold = st.slider("Minimum Match Score", 0, 100, 50)
    
    # Filter jobs based on selections
    filtered_jobs = st.session_state.job_matches
    
    if selected_role != "All":
        filtered_jobs = [job for job in filtered_jobs if job["Job Role"] == selected_role]
    
    if selected_location != "All":
        filtered_jobs = [job for job in filtered_jobs if job["Location"] == selected_location]
    
    filtered_jobs = [job for job in filtered_jobs if job["match_score"] >= match_threshold]
    
    # Sort jobs by match score
    sorted_jobs = sorted(filtered_jobs, key=lambda x: x["match_score"], reverse=True)
    
    # Display filtered results count
    st.markdown(f"Showing {len(sorted_jobs)} jobs matching your criteria")
    
    # Display job matches
    if sorted_jobs:
        for job in sorted_jobs:
            match_class = "match-high" if job["match_score"] >= 80 else "match-medium" if job["match_score"] >= 60 else "match-low"
            
            st.markdown(f'<div class="result-card {match_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {job['Title']}")
                st.markdown(f"**Company:** {job['Company Name']} | **Location:** {job['Location']}")
                st.markdown(f"**Job Type:** {job['Job Type']} | **Posted:** {job['Posted Time']}")
            
            with col2:
                st.markdown(f'<div style="text-align: center; margin-top: 10px;">', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 2rem; font-weight: 600; color: #1976D2;">{job["match_score"]}%</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 0.9rem; color: #546E7A;">Match Score</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("#### Why this matches your profile:")
            for reason in job["match_reasons"]:
                st.markdown(f"- {reason}")
            
            st.markdown("#### Job Description:")
            with st.expander("View Description"):
                st.markdown(job["Description"])
            
            st.markdown(f"[Apply Now]({job['Apply Link']})")
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("⚠️ No jobs match your current filter criteria. Try adjusting the filters.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Career insights based on matched jobs
    if st.session_state.job_matches:
        st.markdown('<div class="subheader">Career Insights</div>', unsafe_allow_html=True)
        
        # Extract all skills mentioned across job descriptions
        all_skills = []
        common_skills = ["python", "java", "javascript", "sql", "aws", "azure", "react", 
                         "node.js", "docker", "kubernetes", "agile", "scrum", "ci/cd",
                         "machine learning", "data science", "artificial intelligence"]
        
        for job in st.session_state.job_matches:
            for skill in common_skills:
                if skill in job["Description"].lower() and skill not in all_skills:
                    all_skills.append(skill)
        
        # Find skills gap
        user_skills = [skill.lower() for skill in st.session_state.parsed_resume.get("skills", [])]
        missing_skills = [skill for skill in all_skills if skill not in user_skills]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**In-Demand Skills in These Jobs:**")
            skills_html = ""
            for skill in all_skills[:10]:
                skills_html += f'<div class="skill-chip">{skill.title()}</div>'
            st.markdown(f'<div style="margin-top: 0.5rem;">{skills_html}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Skills to Consider Adding to Your Profile:**")
            if missing_skills:
                missing_skills_html = ""
                for skill in missing_skills[:5]:
                    missing_skills_html += f'<div class="skill-chip">{skill.title()}</div>'
                st.markdown(f'<div style="margin-top: 0.5rem;">{missing_skills_html}</div>', unsafe_allow_html=True)
            else:
                st.markdown("You have all the commonly required skills for these positions!")
        
        # Career growth suggestions
        st.markdown("**Career Growth Suggestions:**")
        st.markdown("""
        1. **Skill Development**: Focus on adding the missing skills identified above to your profile.
        2. **Networking**: Connect with professionals at the companies you're interested in.
        3. **Portfolio Building**: Create projects that showcase your abilities in your target domain.
        4. **Continued Learning**: Consider certifications relevant to your desired roles.
        """)

# Main app
def main():
    add_custom_css()
    init_session_state()
    
    show_app_header()
    show_progress()
    
    if st.session_state.current_step == 1:
        resume_upload_step()
    elif st.session_state.current_step == 2:
        career_goals_step()
    elif st.session_state.current_step == 3:
        motivation_matrix_step()
    elif st.session_state.current_step == 4:
        job_matching_step()
    elif st.session_state.current_step == 5:
        results_step()
    
    navigation_buttons()
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("Career Compass | Resume Parser & Job Matching Assistant | © 2023")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()