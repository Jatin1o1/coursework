class CourseFormatter:
    """Formats and structures the course content into modules and lessons."""

    def __init__(self, llm):
        self.llm = llm

    def format_course(self, content_data: str) -> str:
        print("\033[93m Formatting course \033[0m")
        prompt = f"""
        Organize the following content into structured JSON format with:
        - 'title': Course title
        - 'description': Brief description
        - 'modules': List of modules with lessons, make sure to add resouces for each lesson, each module should have atleast 2-3 lessons
        - 'references': Additional reading materials
        Content: {content_data}
        Ensure JSON output only and  JSON follows proper indentation (4 spaces), no markdown formatting, no triple quotes, no escape characters, also make sure json is properly validated 
        """
        response = self.llm.invoke(prompt)
        return response.content
    

    