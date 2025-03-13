openai_api_key = "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"
serpapi_api_key = "fff4ef49c338ca20f7f70fee5cff4aa15e2fb06604b32f8067d2e8ad7a463f5a"
cohere= "H3NTwRI37jonYkIFvCIGr31lwtK0qAFj0msHZbo1"
tavily= "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"
import os
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langchain.tools import Tool
from fastapi.responses import JSONResponse
import nest_asyncio
import uvicorn
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = openai_api_key
serpapi_api_key = os.getenv("SERPAPI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Define the CourseRequest model
class CourseRequest(BaseModel):
    brief: str
    target_audience: str
    course_duration: str

# Define the state schema
class CourseState(BaseModel):
    brief: str
    research_data: str = None
    content_data: str = None
    structured_course: dict = None

# Initialize OpenAI model
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=500, n=1)

# Web Scraping Agent
class EnhancedResearchAgent:
    def __init__(self, serpapi_key):
        self.serpapi_key = serpapi_key

    def get_full_content(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            article = soup.find(['article', 'div'], class_='article-content')
            if not article:
                paragraphs = soup.find_all('p')
                content = " ".join([para.text for para in paragraphs])
            else:
                paragraphs = article.find_all('p')
                content = " ".join([para.text for para in paragraphs])
            return self.clean_content(content)
        except Exception as e:
            print(f"Error while scraping content from {url}: {e}")
            return ""

    def clean_content(self, content):
        return " ".join(content.replace("\n", " ").replace("\r", "").split())

    def web_scrape(self, query: str):
        params = {
            "q": query,
            "api_key": self.serpapi_key,
            "engine": "google",
            "num": 5,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        full_content = []
        for result in results.get("organic_results", []):
            if "link" in result:
                article_url = result["link"]
                print(f"Scraping article: {article_url}")
                content = self.get_full_content(article_url)
                if content:
                    full_content.append(content)
        return full_content

# Define Agent Functions
research_agent = EnhancedResearchAgent(serpapi_api_key)

def content_agent(research_data):
    response = llm.invoke(f"Generate detailed course content using: {research_data}")
    return response.content

def structure_agent(content_data):
    response = llm.invoke(f"Organize the course into modules and lessons: {content_data}")
    return response.content

# Create LangGraph Workflow
graph = StateGraph(state_schema=CourseState)
graph.add_node("research_agent", research_agent.web_scrape)
graph.add_node("content_agent", content_agent)
graph.add_node("structure_agent", structure_agent)

graph.add_edge("research_agent", "content_agent")
graph.add_edge("content_agent", "structure_agent")

graph.set_entry_point("research_agent")

def generate_course(brief, target_audience, course_duration):
    research = research_agent.web_scrape(brief)
    content = content_agent(research)
    structured_course = structure_agent(content)
    try:
        structured_course = json.loads(structured_course)
    except json.JSONDecodeError:
        structured_course = {"title": "Untitled Course", "description": "Invalid response", "modules": [], "references": []}
    return {
        "course_title": structured_course.get('title', 'Untitled Course'),
        "description": structured_course.get('description', 'No description provided'),
        "modules": structured_course.get('modules', []),
        "references": structured_course.get('references', [])
    }

@app.post("/generate_course")
async def create_course(request: CourseRequest):
    response = generate_course(request.brief, request.target_audience, request.course_duration)
    return JSONResponse(content=response)

# Run FastAPI in Notebook
if __name__ == "__main__":
    vals = {
        "brief": "A microfinance course for beginners who need to learn from basics",
        "target_audience": "College students with no financial background",
        "course_duration": "6 weeks"
    }
    print(generate_course(vals["brief"], vals["target_audience"], vals["course_duration"]))
