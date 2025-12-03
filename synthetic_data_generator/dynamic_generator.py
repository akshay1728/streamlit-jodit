from .parser import AIParser
from .core.generator import SyntheticDataGenerator

class DynamicGenerator:
    """
    A dynamic, AI-powered synthetic data generator.
    """
    def __init__(self):
        self.parser = AIParser()

    def generate(self, prompt, num_rows):
        """
        Generates synthetic data based on a natural language prompt.

        :param prompt: A natural language string describing the desired file.
        :param num_rows: The number of rows to generate.
        :return: A pandas DataFrame with the synthetic data.
        """
        # Step 1: Use the AI parser to get a structured specification
        specifications = self.parser.parse(prompt)

        if not specifications:
            raise ValueError("Could not parse the prompt to generate a file specification. Please be more descriptive.")

        # Step 2: Use the core generator to create the data
        core_generator = SyntheticDataGenerator(specifications=specifications)
        synthetic_data = core_generator.generate(num_rows=num_rows)

        return synthetic_data
