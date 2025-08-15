import streamlit as st
import requests
import pdfplumber
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage

# API Keys
GROQ_API_KEY = "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"
SERP_API_KEY = "9f7f9cb9160b05cc41a86e4b129a00ac4800a551339ebc83a2b00b2cfa61efe0"

# Initialize Groq LLM
llm = ChatGroq(model_name="deepseek-r1-distill-llama-70b", groq_api_key=GROQ_API_KEY)

# Job Search Agent with Location
def job_search(job_title, job_location):
    search_query = f"{job_title} in {job_location}"  # Include location in the search
    search_url = f"https://serpapi.com/search.json?engine=google_jobs&q={search_query}&api_key={SERP_API_KEY}"
    
    response = requests.get(search_url).json()
    jobs = []
    
    for job in response.get("jobs_results", [])[:3]:  # Get top 3 jobs
        jobs.append({
            "title": job["title"],
            "company": job["company_name"],
            "location": job["location"],
            "description": job.get("description", "No description available"),
            "link": job["related_links"][0]["link"] if "related_links" in job else "No link available"
        })
    
    return jobs

# Job Summary Agent
def summarize_jobs(jobs):
    summaries = []
    for job in jobs:
        prompt = f"Summarize this job listing:\nTitle: {job['title']}\nCompany: {job['company']}\nLocation: {job['location']}\nDescription: {job['description']}"
        response = llm([SystemMessage(content="Summarize job descriptions concisely."), HumanMessage(content=prompt)])
        summaries.append(response.content)
    return summaries

# Resume Extraction
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Resume Improvement Agent
def improve_resume(resume_text, job_title):
    prompt = f"Review this resume and suggest improvements for a {job_title} position:\n\n{resume_text}"
    response = llm([SystemMessage(content="Provide resume improvement suggestions."), HumanMessage(content=prompt)])
    return response.content

# Streamlit UI
st.title("🚀 AI-Powered Job Search Assistant")

# User input for job search
job_title = st.text_input("Enter the job title you're looking for:")
job_location = st.text_input("Enter the location (e.g., Pune, India):")
uploaded_resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if st.button("Find Jobs"):
    if job_title and job_location:
        st.subheader("🔍 Searching for jobs...")
        jobs = job_search(job_title, job_location)
        
        if jobs:
            summarized_jobs = summarize_jobs(jobs)
            
            st.subheader("📌 Top Job Listings")
            for i, job in enumerate(jobs):
                st.write(f"**{job['title']}** at {job['company']} ({job['location']})")
                st.write(f"**Summary:** {summarized_jobs[i]}")
                st.write(f"[View Job Posting]({job['link']})")
                st.write("---")
        else:
            st.write("No jobs found. Try another search.")
    else:
        st.warning("Please enter both a job title and location.")

# Resume Improvement Section
if uploaded_resume:
    st.subheader("📄 Resume Improvement Suggestions")
    resume_text = extract_text_from_pdf(uploaded_resume)
    suggestions = improve_resume(resume_text, job_title)
    st.write(suggestions)
