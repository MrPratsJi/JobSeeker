# AI-Powered Job Search Assistant

## 🚀 Overview
The AI-Powered Job Search Assistant is a Streamlit-based application that helps users find relevant job opportunities, generate concise job summaries, and improve their resumes using Groq's open-source LLM and SerpAPI for job listings.

## ✨ Features
- Job Search Agent: Retrieves top job listings based on user input (job title & location) using SerpAPI.
- Job Summary Agent: Uses Groq LLM to generate concise summaries of job descriptions.
- Resume Extraction & Improvement: Extracts text from uploaded resumes (PDFs) and provides AI-powered suggestions for improvements.

## 📌 Tech Stack
- Python (Streamlit, Requests, pdfplumber)
- LangChain (Groq API for LLM capabilities)
- FAISS (for resume similarity comparison - optional enhancement)
- SerpAPI (for fetching job listings from Google Jobs search)

## 📢 How It WorksEnter Job 
- Title & Location → The app fetches relevant job listings using SerpAPI.
- Summarize Jobs → Uses Groq LLM to generate easy-to-read summaries.
- Upload Resume → Extracts text and provides improvement suggestions for a better job match.

## Deployed App Link:

- https://jobseeker-j8bdtqc6gveylo59tbuixm.streamlit.app/
