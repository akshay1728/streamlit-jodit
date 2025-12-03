# Synthetic Data Generator

This module provides a flexible way to generate synthetic data based on a given specification. It is useful for creating realistic-looking datasets for testing, demonstrations, or any other purpose where real data is not available or suitable.

## Installation

To use this module, you need to install the required dependencies. You can do this by running the following command:

```bash
pip install -r requirements.txt
```

## Usage

To use the synthetic data generator, you need to define a specification dictionary that describes the columns of the dataset you want to create. Each key in the dictionary is a column name, and the value is another dictionary that defines the properties of that column.

### Column Types

The following column types are supported:

- `date`: Generates a random date. You can specify a `start` and `end` date for the range. These can be relative dates (e.g., `'-1y'`, `'+30d'`) or a reference to another date column.
- `choice`: Selects a random value from a list of choices.
- `text`: Generates a random text string. You can specify the `max_nb_chars`.
- `person_id`: Generates a unique identifier for a person.

### Error Handling

The generator will raise a `ValueError` if you try to reference a column that has not yet been defined in the specification. For example, if you define `end_date` before `Start_date`, the generator will raise an error because it needs `Start_date` to calculate `end_date`.

If you use an unsupported column type in your specification, the generator will raise a `NotImplementedError`.

### Example

Here is an example of how to generate a synthetic health dataset:

```python
from synthetic_data_generator.generator import SyntheticDataGenerator

# Define the specifications for the health data file
health_specifications = {
    'Start_date': {'type': 'date', 'start': '-2y', 'end': 'today'},
    'end_date': {'type': 'date', 'start': 'Start_date', 'end': '+1y'},
    'health_condition': {'type': 'choice', 'choices': ['diabetes', 'BP', 'heart condition', 'asthma', 'migraine']},
    'comment': {'type': 'text', 'max_nb_chars': 150},
    'person_id': {'type': 'person_id'}
}

# Create an instance of the generator
generator = SyntheticDataGenerator(specifications=health_specifications)

# Generate 100 rows of synthetic data with a 50% unique person ratio
synthetic_data = generator.generate(num_rows=100, unique_person_ratio=0.5)

# Print the generated data
print(synthetic_data.head())
```
