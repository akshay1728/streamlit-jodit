from synthetic_data_generator.generator import SyntheticDataGenerator
import unittest

class TestSyntheticDataGenerator(unittest.TestCase):
    def test_invalid_column_order(self):
        """
        Tests that a ValueError is raised when a column is referenced before it is defined.
        """
        invalid_specifications = {
            'end_date': {'type': 'date', 'start': 'Start_date', 'end': '+1y'},
            'Start_date': {'type': 'date', 'start': '-2y', 'end': 'today'},
            'health_condition': {'type': 'choice', 'choices': ['diabetes', 'BP', 'heart condition']},
            'comment': {'type': 'text', 'max_nb_chars': 150},
            'person_id': {'type': 'person_id'}
        }
        generator = SyntheticDataGenerator(specifications=invalid_specifications)
        with self.assertRaises(ValueError):
            generator.generate(num_rows=10)

    def test_unknown_column_type(self):
        """
        Tests that a NotImplementedError is raised when an unknown column type is used.
        """
        invalid_specifications = {
            'name': {'type': 'full_name'},
            'age': {'type': 'number', 'min': 18, 'max': 99}
        }
        generator = SyntheticDataGenerator(specifications=invalid_specifications)
        with self.assertRaises(NotImplementedError):
            generator.generate(num_rows=10)

if __name__ == '__main__':
    unittest.main()
