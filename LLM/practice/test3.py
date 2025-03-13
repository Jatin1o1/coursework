import os
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
# from crewai import Agent, Task, Crew  # ✅ CrewAI for multi-agent workflow

# Load environment variables
load_dotenv()
serpapi_api_key = "fff4ef49c338ca20f7f70fee5cff4aa15e2fb06604b32f8067d2e8ad7a463f5a"
os.environ["OPENAI_API_KEY"] = "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"


# Initialize FastAPI app
app = FastAPI()

class CourseRequest(BaseModel):
    brief: str
    target_audience: str
    course_duration: str

# Initialize OpenAI model
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7, max_tokens=500, n=1)

# ✅ Web Scraping Agent
class EnhancedResearchAgent:
    def __init__(self, serpapi_key):
        self.serpapi_key = serpapi_key

    def get_full_content(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            content = " ".join([para.text for para in paragraphs])
            return " ".join(content.replace("\n", " ").replace("\r", "").split())
        except Exception as e:
            print(f"Error while scraping content from {url}: {e}")
            return ""

    def web_scrape(self, query: str):
        params = {
            "q": query, "api_key": self.serpapi_key, "engine": "google", "num": 5,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        full_content = []
        for result in results.get("organic_results", []):
            if "link" in result:
                article_url = result["link"]
                print(f"Scraping: {article_url}")
                content = self.get_full_content(article_url)
                if content:
                    full_content.append(content)
        return "\n".join(full_content) if full_content else "No relevant data found"

# ✅ Define Agents
research_agent = Agent(
    role="Researcher",
    goal="Find and summarize online content about the given topic.",
    backstory="An expert in online research and data extraction.",
    tools=[EnhancedResearchAgent(serpapi_api_key).web_scrape],
    verbose=True
)

content_agent = Agent(
    role="Content Generator",
    goal="Generate structured course content based on research.",
    backstory="A knowledgeable professor in course design.",
    tools=[llm],
    verbose=True
)

structure_agent = Agent(
    role="Course Organizer",
    goal="Format and structure the generated content into a course outline.",
    backstory="An experienced curriculum designer who organizes content into modules.",
    tools=[llm],
    verbose=True
)

# ✅ Define Tasks
research_task = Task(
    description="Scrape and summarize research data for course generation.",
    agent=research_agent
)

content_task = Task(
    description="Use the research data to generate structured course content.",
    agent=content_agent,
    context=research_task
)

structure_task = Task(
    description="Format the generated course content into a structured curriculum.",
    agent=structure_agent,
    context=content_task
)

# ✅ CrewAI - Define the workflow
crew = Crew(
    agents=[research_agent, content_agent, structure_agent],
    tasks=[research_task, content_task, structure_task]
)

def generate_course(brief):
    research_text = research_agent.web_scrape(brief)
    content = content_agent(research_text)
    structured_course = structure_agent(content)
    return json.loads(structured_course) if structured_course else {"title": "Untitled Course"}

# ✅ Course Generation Function
# def generate_course(brief, target_audience, course_duration):
#     research_text = crew.kickoff(inputs={"brief": brief})
#     print("🔍 Scraped Research Data:", research_text[:500])

#     content = content_agent.tools[0].invoke(f"Generate detailed course content using: {research_text}")
#     print("📚 Generated Course Content:", content[:500])

#     structured_course = structure_agent.tools[0].invoke(f"Organize the course into structured modules: {content}")
#     print("📖 Structured Course:", structured_course[:500])

#     try:
#         structured_course = json.loads(structured_course)
#     except json.JSONDecodeError:
#         print("❌ Invalid JSON response from AI")
#         structured_course = {"title": "Untitled Course", "description": "Invalid response", "modules": [], "references": []}

#     return {
#         "course_title": structured_course.get('title', 'Untitled Course'),
#         "description": structured_course.get('description', 'No description provided'),
#         "modules": structured_course.get('modules', []),
#         "references": structured_course.get('references', [])
#     }

@app.post("/generate_course")
async def create_course(request: CourseRequest):
    response = generate_course(request.brief, request.target_audience, request.course_duration)
    return JSONResponse(content=response)

if __name__ == "__main__":
    vals = {
        "brief": "A microfinance course for beginners",
        "target_audience": "College students",
        "course_duration": "6 weeks"
    }
    print(generate_course(vals["brief"], vals["target_audience"], vals["course_duration"]))
