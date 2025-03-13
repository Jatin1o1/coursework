class ContentGenerator:
    """Generates structured course content based on research data."""

    def __init__(self, llm):
        self.llm = llm

    def generate_content(self, research_data: str, target_audience: str, duration: str) -> str:
        print("\033[94m generating Content for articles \033[0m")

        prompt = f"""
        Based on the following research, create structured JSON output for {duration} course:
        Research Data: {research_data}
        target audience : {target_audience}
        Output must be a JSON object with 'title', 'description', 'modules' (list of lessons), and 'references', Ensure the JSON follows proper indentation (4 spaces), no markdown formatting, no triple quotes, no escape characters
        on generation of opuput, make sure it is properly validated and formatted json
        """
        response = self.llm.invoke(prompt)
        return response.content
    
    