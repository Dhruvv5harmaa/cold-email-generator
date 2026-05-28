from os import name

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from chains2 import Chain
from portfolio2 import Portfolio
from utils2 import clean_text

HEADERS = {
"User-Agent": (
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 (KHTML, like Gecko) "
"Chrome/125.0.0.0 Safari/537.36"
)
}

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and parsed.netloc

def fetch_job_page(url):
    response = requests.get(
    url,
    headers=HEADERS,
    timeout=10
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    return soup.get_text(separator=" ", strip=True)

def create_streamlit_app(llm, portfolio):
    st.title("📧 Cold Email Generator")

    st.markdown(
        "Generate personalized cold emails from job posting URLs using LLMs."
    )

    url_input = st.text_input(
        "Enter Job URL",
        value="https://careers.nike.com/software-engineer-iii-itc/job/R-70632"
    )

    submit_button = st.button("Generate Email")

    if submit_button:

        if not url_input:
            st.warning("Please enter a URL.")
            return

        if not is_valid_url(url_input):
            st.error("Please enter a valid URL.")
            return

        try:
            with st.spinner("Processing job posting..."):

                # Fetch webpage text
                raw_text = fetch_job_page(url_input)

                # Clean text
                cleaned_data = clean_text(raw_text)

                # Load portfolio into vector DB
                portfolio.load_portfolio()

                # Extract jobs
                jobs = llm.extract_jobs(cleaned_data)

                if not jobs:
                    st.warning("No jobs extracted from page.")
                    return

                st.success(f"Found {len(jobs)} job(s).")

                # Generate cold emails
                for index, job in enumerate(jobs, start=1):

                    skills = job.get("skills", [])

                    links = portfolio.query_links(skills)

                    email = llm.write_mail(job, links)

                    st.divider()

                    st.subheader(f"Cold Email #{index}")

                    st.code(email, language="markdown")

        except requests.exceptions.Timeout:
            st.error("Request timed out. Try again.")

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch webpage: {e}")

        except Exception as e:
            st.error(f"Unexpected Error: {e}")


if name == "main":

    st.set_page_config(
            page_title="Cold Email Generator",
            page_icon="📧",
            layout="wide"
    )
chain = Chain()
portfolio = Portfolio()
create_streamlit_app(chain, portfolio)