import unittest
from synthetic_data_generator.parser import AIParser

class TestAIParser(unittest.TestCase):
    def setUp(self):
        self.parser = AIParser()

    def test_basic_prompt(self):
        """
        Tests that a basic prompt with standard keywords is parsed correctly.
        """
        prompt = "Create a health file with a start date, end date, health condition, comment, and person id."
        spec = self.parser.parse(prompt)

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
        prompt = "I need a file for patient records. It should have a patient id, a diagnosis, a begin date, and a completion date. Also, add a column for notes."
        spec = self.parser.parse(prompt)

        self.assertIn("person_id", spec)
        self.assertIn("health_condition", spec)
        self.assertIn("start_date", spec)
        self.assertIn("end_date", spec)
        self.assertIn("comment", spec)

    def test_partial_prompt(self):
        """
        Tests that a prompt with only a subset of columns is parsed correctly.
        """
        prompt = "Generate a list of patient ids and their diagnosis."
        spec = self.parser.parse(prompt)

        self.assertIn("person_id", spec)
        self.assertIn("health_condition", spec)
        self.assertNotIn("start_date", spec)
        self.assertNotIn("end_date", spec)

    def test_empty_prompt(self):
        """
        Tests that an empty or irrelevant prompt results in an empty spec.
        """
        prompt = "Generate some data."
        spec = self.parser.parse(prompt)
        self.assertEqual(len(spec), 0)

if __name__ == '__main__':
    unittest.main()
