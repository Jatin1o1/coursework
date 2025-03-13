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
from Course_maker.scraper import EnhancedResearchAgent

# Load environment variables
load_dotenv()

# Set up API keys for OpenAI and SerpAPI
serpapi_api_key = "fff4ef49c338ca20f7f70fee5cff4aa15e2fb06604b32f8067d2e8ad7a463f5a"
os.environ["OPENAI_API_KEY"] = "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"


# Define the state schema
class CourseState(BaseModel):
    brief: str
    research_data: str = None
    content_data: str = None
    structured_course: dict = None

# Initialize OpenAI model
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=500, n=1)


research_agent = EnhancedResearchAgent(serpapi_api_key)

def content_agent(research_data,target_audience, duration):
    prompt = f"""
    Based on the following research, create structured JSON output for {duration} course:
    Research Data: {research_data}
    target audience : {target_audience}
    Output must be a JSON object with 'title', 'description', 'modules' (list of lessons), and 'references', please verify the proper json as output, 
    """
    response = llm.invoke(prompt)
    return response.content

def structure_agent(content_data):
    prompt = f"""
    Organize the following content into a **fully valid JSON format**.
    
    **JSON Format:**
    {{
        "title": "Course Title",
        "description": "Brief description",
        "modules": [
            {{
                "title": "Module Title",
                "lessons": [
                    {{
                        "name": "Lesson Name",
                        "resources": ["Resource 1", "Resource 2"]
                    }}
                ]
            }}
        ],
        "references": ["Reference 1", "Reference 2"]
    }}

    **Instructions:**
    - Ensure **every JSON object and array is properly closed**.
    - **No extra text, explanations, or Markdown syntax** in the output.
    - **Do not include escape characters (`\n`, `\"`, `\\`)**.
    - **Generate at least 6 modules** with at least 3 lessons each.

    **Content to Structure:**
    {content_data}
    """
    
    response = llm.invoke(prompt)
    return response.content


# Create LangGraph Workflow
graph = StateGraph(state_schema=CourseState)
graph.add_node("research_agent", research_agent.web_scrape)
graph.add_node("content_agent", content_agent)
graph.add_node("structure_agent", structure_agent)

graph.add_edge("research_agent", "content_agent")
graph.add_edge("content_agent", "structure_agent")

graph.set_entry_point("research_agent")

def generate_course(brief, target_audience,duration):
    research_text = research_agent.web_scrape(brief)
    content = content_agent(research_text,target_audience,duration=duration)
    structured_course = structure_agent(content)
    return structured_course




# Run FastAPI in Notebook
if __name__ == "__main__":
    inputs = {
    "brief":"A robotics  course for beginners who need to learn from basics",
    "target_audience": "College students with no financial background",
    "course_duration": "6 weeks"
    }
    # print(generate_course(brief))
    print(generate_course(inputs["brief"],inputs["target_audience"],inputs["course_duration"]))
