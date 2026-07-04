# AI-Based Company Researcher
## An automated research assistant that performs real-time company intelligence gathering and generates concise, structured company briefs. Give it a company name or website URL, and it crawls the web for relevant information, extracts key data using a frontier AI model, and delivers a downloadable PDF report.
### Live URL of Webpage: https://ai-powered-company-researcher.onrender.com
# Overview
## This tool combines headless web scraping with large language model (LLM) extraction to turn scattered public information about a company into a clean, schema-valid summary. It's designed for quick due-diligence, sales research, competitive analysis, or general company profiling — all through a simple chat-style interface.
# How It Works
### 
1.	Input — You provide a company name or URL.
### 
2.	Crawling — Selenium WebDriver runs headlessly to concurrently fetch and render pages from relevant sources, bypassing common rendering restrictions on modern websites.
### 
3.	Extraction — The scraped content is cleaned and synthesized into structured text, then passed to a frontier LLM (via OpenRouter) to extract company data into a validated schema.
### 
4.	Delivery — The extracted data is compiled into a downloadable PDF report and presented back to you through the chat interface.
# Key Features
### 
•	Concurrent web crawling — Selenium WebDriver processes multiple target domains at once for faster research
### 
•	AI-powered data extraction — Uses OpenRouter to parse unstructured web content into structured, schema-valid data.
### 
•	Chat-inspired UI — A responsive front end built with plain HTML, CSS, and asynchronous JavaScript.
### 
•	Asynchronous backend — A FastAPI server schedules async workers and validates data with Pydantic.
### 
•	PDF report generation — Compiles the final research output into a clean, shareable PDF.

# Installation
1.	Clone the repository
2.	git clone <repository-url>
3.	cd ai-company-researcher
4.	Create and activate a virtual environment (recommended)
5.	python -m venv venv
6.	source venv/bin/activate   # On Windows: venv\Scripts\activate
7.	Install dependencies
8.	pip install -r requirements.txt
9.	Configure environment variables
Create a .env file in the project root and add your OpenRouter and Serper API key:
OPENROUTER_API_KEY=your_api_key_here
SERPER_API_KEY=your_api_key_here

# Steps to run the project
1.	Start the FastAPI server
2.	uvicorn main:app --reload
3.	Open the app in your browser at http://localhost:8000 (or the configured host or port where uvicorn is running).
4.	Enter a company name or URL into the chat interface.
5.	The app will crawl relevant sources, extract structured company data, and generate a downloadable PDF report summarizing its findings.

# Requirements
### Python 3.9+
### Google Chrome (or Chromium) installed, for Selenium WebDriver
### An OpenRouter API key

# Python Dependencies
### selenium==4.23.0
### webdriver-manager==4.0.2
### openai==2.44.0
### pydantic==2.9.2
### fpdf2==2.7.9
### fastapi==0.115.0
### uvicorn==0.30.6
### python-dotenv==1.0.1



