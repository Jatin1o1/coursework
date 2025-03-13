
import os

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from Course_maker.scraper import EnhancedResearchAgent
from Course_maker.ContentGenerator import ContentGenerator
from Course_maker.CourseFormatter import CourseFormatter
from langgraph.graph import StateGraph


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


class CourseGenerator:
    def __init__(self ):
        self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7, max_tokens=1000, n=1)
        self.research_agent = EnhancedResearchAgent(serpapi_api_key)
        self.content_generator = ContentGenerator(self.llm)
        self.formatter = CourseFormatter(self.llm)
        # Create LangGraph Workflow
        graph = StateGraph(state_schema=CourseState)
        graph.add_node("research_agent", self.research_agent.web_scrape)
        graph.add_node("content_agent", self.content_generator.generate_content)
        graph.add_node("structure_agent", self.formatter.format_course)

        graph.add_edge("research_agent", "content_agent")
        graph.add_edge("content_agent", "structure_agent")

        graph.set_entry_point("research_agent")
        pass
    
    def generate_course(self,brief, target_audience,duration):
        research_text = self.research_agent.web_scrape(brief)
        content = self.content_generator.generate_content(research_text,target_audience,duration=duration)
        return content
        print("content",content)
        structured_course = self.formatter.format_course(content)
        
        return structured_course


if __name__ == "__main__":
    inputs = {
    "brief":"A robotics  course for beginners who need to learn from basics",
    "target_audience": "College students with no financial background",
    "course_duration": "6 weeks"
    }
    course_gen= CourseGenerator()
    # print(generate_course(brief))
    print(course_gen.generate_course(inputs["brief"],inputs["target_audience"],inputs["course_duration"]))
