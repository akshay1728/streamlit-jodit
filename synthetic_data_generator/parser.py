import re

class AIParser:
    """
    An AI-powered parser that converts a natural language prompt into a structured data generation specification.
    This version is extensible with custom patterns.
    """
    def __init__(self, custom_patterns=None):
        # A more flexible list of patterns. Each pattern has a standard name,
        # a list of keywords to match (including plurals), and the spec details.
        self.default_patterns = [
            {
                "name": "start_date",
                "keywords": ["start date", "start dates", "begin date", "begin dates", "commencement date"],
                "spec": {"type": "date", "start": "-2y", "end": "today"}
            },
            {
                "name": "end_date",
                "keywords": ["end date", "end dates", "finish date", "finish dates", "completion date", "completion dates"],
                "spec": {"type": "date", "start": "start_date", "end": "+1y"} # Dependency on the standard name
            },
            {
                "name": "health_condition",
                "keywords": ["health condition", "health conditions", "medical issue", "diagnosis", "diagnoses"],
                "spec": {"type": "choice", "choices": ["diabetes", "BP", "heart condition", "asthma"]}
            },
            {
                "name": "comment",
                "keywords": ["comment", "comments", "notes", "note", "description"],
                "spec": {"type": "text", "max_nb_chars": 150}
            },
            {
                "name": "person_id",
                "keywords": ["person id", "person ids", "patient id", "patient ids", "user id", "user ids"],
                "spec": {"type": "person_id"}
            }
        ]

        # Merge custom patterns with default ones
        self.patterns = self.default_patterns
        if custom_patterns:
            # A simple merge: custom patterns are added. More sophisticated merging could be implemented if needed.
            self.patterns.extend(custom_patterns)


    def parse(self, prompt):
        """
        Parses a natural language prompt and returns a structured specification.

        :param prompt: A natural language string describing the desired file.
        :return: A dictionary representing the structured specification.
        """
        prompt = prompt.lower()

        final_spec = {}

        # Find all columns that match keywords in the prompt
        for pattern in self.patterns:
            for keyword in pattern["keywords"]:
                # Use word boundaries to avoid matching parts of words (e.g., 'end' in 'send')
                if re.search(r'\b' + re.escape(keyword) + r'\b', prompt):
                    final_spec[pattern["name"]] = pattern["spec"].copy()
                    # Move to the next pattern once a match is found for the current one
                    break

        # Dependency resolution is handled by the core generator, which validates that
        # any referenced columns are present in the final specification.
        return final_spec
