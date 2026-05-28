import os

from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from langchain_groq import ChatGroq

load_dotenv()

class Chain:


    def __init__(self):

        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile"
        )

        self.job_extraction_prompt = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT:
            {page_data}

            ### TASK:
            Extract job posting information from the text.

            Return ONLY valid JSON.

            Expected JSON format:

            [
                {{
                    "role": "Job Role",
                    "experience": "Experience Required",
                    "skills": ["skill1", "skill2"],
                    "description": "Short job description"
                }}
            ]

            ### IMPORTANT RULES:
            - Return ONLY JSON
            - No markdown
            - No explanation
            - No preamble
            - If no jobs found, return []

            ### JSON:
            """
        )

        self.email_prompt = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### RELEVANT PORTFOLIO LINKS:
            {link_list}

            ### TASK:
            Write a professional cold email.

            You are XYZ, a Business Development Executive at ABC Solutions,
            an AI & Software Consulting company.

            The email should:
            - be concise
            - sound personalized
            - mention relevant skills
            - explain how ABC Solutions can help
            - include relevant portfolio links naturally
            - end with a call to action

            ### IMPORTANT:
            - No preamble
            - No placeholders
            - Keep it professional
            - Keep it under 250 words

            ### EMAIL:
            """
        )

    def extract_jobs(self, cleaned_text):

        try:

            # Prevent extremely large context
            cleaned_text = cleaned_text[:12000]

            chain_extract = self.job_extraction_prompt | self.llm

            response = chain_extract.invoke({
                "page_data": cleaned_text
            })

            json_parser = JsonOutputParser()

            parsed_response = json_parser.parse(response.content)

            if isinstance(parsed_response, dict):
                return [parsed_response]

            if isinstance(parsed_response, list):
                return parsed_response

            return []

        except OutputParserException:
            raise OutputParserException(
                "Failed to parse LLM response into valid JSON."
            )

        except Exception as e:
            raise Exception(f"Job extraction failed: {str(e)}")

    def write_mail(self, job, links):

        try:

            chain_email = self.email_prompt | self.llm

            response = chain_email.invoke({
                "job_description": str(job),
                "link_list": links
            })

            return response.content

        except Exception as e:
            raise Exception(f"Email generation failed: {str(e)}")


if os.name == "main":

    print(os.getenv("GROQ_API_KEY"))

