import re

class AIParser:
    """
    An AI-powered parser that converts a natural language prompt into a structured data generation specification.
    This version uses a flexible pattern-matching approach.
    """
    def __init__(self):
        # A more flexible list of patterns. Each pattern has a standard name,
        # a list of keywords to match (including plurals), and the spec details.
        self.patterns = [
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

        # Dependency resolution is now implicitly handled because the 'start' key
        # in the spec already refers to the standardized column name.
        # We just need to make sure the referenced column is also in the final spec.

        columns_in_spec = list(final_spec.keys())
        for col_name, spec_details in final_spec.items():
            if 'start' in spec_details:
                dependency = spec_details['start']
                if dependency in self.patterns[0]["keywords"] and dependency not in columns_in_spec:
                    # This check is now more for ensuring the dependency was also requested in the prompt
                    # The core generator already validates the order.
                    pass

        return final_spec
