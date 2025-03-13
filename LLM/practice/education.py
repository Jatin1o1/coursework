

import os
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph
from langgraph.schema import Node
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()  # Load environment variables


class LLMAgentHandler:
    def __init__(self):
        os.environ[
            "OPENAI_API_KEY"] = "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"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

        self.llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)

    def generate_response(self, query: str) -> dict:
        prompt = PromptTemplate(
            input_variables=["input"],
            template="Answer this query in a concise and informative way: {input}"
        )

        return {"response": self.llm(prompt.format(input=query))}

    def get_agent_response(self, query: str) -> str:
        graph = Graph()
        graph.add_node("generate_response", self.generate_response)
        graph.set_entry_point("generate_response")
        graph.set_end_point("generate_response")

        try:
            result = graph.run({"input": query})
            return result['response'].strip()
        except Exception as e:
            return f"Agent Error: {str(e)}"


if __name__ == "__main__":
    agent_handler = LLMAgentHandler()
    response = agent_handler.get_agent_response("Tell me something interesting.")
    print(response)
