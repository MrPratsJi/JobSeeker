import streamlit as st
import requests
import pdfplumber
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage  # <- fixed import

# API Keys (move these to env vars in production)
GROQ_API_KEY = "your-groq-key"
SERP_API_KEY = "your-serp-key"

# Initialize Groq LLM
llm = ChatGroq(model_name="deepseek-r1-distill-llama-70b", groq_api_key=GROQ_API_KEY)


def _unwrap_response(resp):
    """
    Robustly get text from whatever shape ChatGroq returns:
      - if object has .content -> return that
      - if list/iterable -> try first element's .content or str
      - otherwise str(resp)
    """
    try:
        # common langchain-like message response
        if hasattr(resp, "content"):
            return resp.content
        # sometimes it's a list of message objects or strings
        if isinstance(resp, (list, tuple)) and len(resp) > 0:
            first = resp[0]
            if hasattr(first, "content"):
                return first.content
            return str(first)
        # fallback
        return str(resp)
    except Exception:
        return str(resp)


# Job Search Agent with Location
def job_search(job_title, job_location):
    search_query = f"{job_title} in {job_location}"
    search_url = f"https://serpapi.com/search.json?engine=google_jobs&q={requests.utils.quote(search_query)}&api_key={SERP_API_KEY}"

    try:
        response = requests.get(search_url, timeout=10).json()
    except Exception:
        return []

    jobs = []
    for job in response.get("jobs_results", [])[:3]:
        jobs.append({
            "title": job.get("title", "No title"),
            "company": job.get("company_name", "Unknown"),
            "location": job.get("location", "Unknown"),
            "description": job.get("description", "No description available"),
            "link": job.get("related_links", [{"link": "No link available"}])[0].get("link", "No link available"),
        })

    return jobs


# Job Summary Agent
def summarize_jobs(jobs):
    summaries = []
    for job in jobs:
        prompt = (
            f"Summarize this job listing in 2-3 short sentences.\n\n"
            f"Title: {job['title']}\nCompany: {job['company']}\nLocation: {job['location']}\n\n"
            f"Description: {job['description']}"
        )

        try:
            resp = llm([SystemMessage(content="Summarize job descriptions concisely."), HumanMessage(content=prompt)])
            summaries.append(_unwrap_response(resp))
        except Exception as e:
            summaries.append(f"Error summarizing: {e}")

    return summaries


# Resume Extraction
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text or "No text found in PDF."


# Resume Improvement Agent
def improve_resume(resume_text, job_title):
    prompt = (
        f"Review this resume and suggest clear, actionable improvements tailored for a {job_title} role.\n\n"
        f"Resume:\n{resume_text}"
    )
    try:
        resp = llm([SystemMessage(content="Provide resume improvement suggestions."), HumanMessage(content=prompt)])
        return _unwrap_response(resp)
    except Exception as e:
        return f"Error improving resume: {e}"


# Streamlit UI
st.title("🚀 AI-Powered Job Search Assistant")

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

if uploaded_resume:
    st.subheader("📄 Resume Improvement Suggestions")
    resume_text = extract_text_from_pdf(uploaded_resume)
    suggestions = improve_resume(resume_text, job_title or "the target role")
    st.write(suggestions)
