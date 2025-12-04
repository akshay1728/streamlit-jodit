import unittest
from synthetic_data_generator.parser import AIParser

class TestAIParser(unittest.TestCase):
    def setUp(self):
        # We will initialize a new parser for each test to ensure isolation
        pass

    def test_basic_prompt(self):
        """
        Tests that a basic prompt with standard keywords is parsed correctly.
        """
        parser = AIParser()
        prompt = "Create a health file with a start date, end date, health condition, comment, and person id."
        spec = parser.parse(prompt)

        self.assertIn("start_date", spec)
        self.assertIn("end_date", spec)
        self.assertIn("health_condition", spec)
        self.assertIn("comment", spec)
        self.assertIn("person_id", spec)
        self.assertEqual(spec["end_date"]["start"], "start_date")

    def test_flexible_prompt(self):
        """
        Tests that a prompt with varied keywords is parsed correctly.
        """
        parser = AIParser()
        prompt = "I need a file for patient records. It should have a patient id, a diagnosis, a begin date, and a completion date. Also, add a column for notes."
        spec = parser.parse(prompt)

        self.assertIn("person_id", spec)
        self.assertIn("health_condition", spec)
        self.assertIn("start_date", spec)
        self.assertIn("end_date", spec)
        self.assertIn("comment", spec)

    def test_partial_prompt(self):
        """
        Tests that a prompt with only a subset of columns is parsed correctly.
        """
        parser = AIParser()
        prompt = "Generate a list of patient ids and their diagnosis."
        spec = parser.parse(prompt)

        self.assertIn("person_id", spec)
        self.assertIn("health_condition", spec)
        self.assertNotIn("start_date", spec)
        self.assertNotIn("end_date", spec)

    def test_empty_prompt(self):
        """
        Tests that an empty or irrelevant prompt results in an empty spec.
        """
        parser = AIParser()
        prompt = "Generate some data."
        spec = parser.parse(prompt)
        self.assertEqual(len(spec), 0)

    def test_custom_patterns(self):
        """
        Tests that the parser can be extended with custom patterns.
        """
        custom_patterns = [
            {
                "name": "product_sku",
                "keywords": ["product sku", "sku", "item code"],
                "spec": {"type": "text", "max_nb_chars": 10}
            }
        ]
        parser = AIParser(custom_patterns=custom_patterns)
        prompt = "I need an inventory file with a product sku and a patient id."
        spec = parser.parse(prompt)

        self.assertIn("product_sku", spec)
        self.assertIn("person_id", spec)
        self.assertEqual(spec["product_sku"]["type"], "text")

if __name__ == '__main__':
    unittest.main()
