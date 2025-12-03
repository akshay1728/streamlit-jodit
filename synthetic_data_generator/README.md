# AI-Powered Synthetic Data Generator

This module provides a dynamic way to generate synthetic data using natural language prompts. Instead of defining a detailed, structured specification, you can describe the file you need, and the system will interpret your request to generate the data.

## Usage

To use the synthetic data generator, describe the file you want to create in a natural language prompt. The system will parse your request and automatically generate a structured specification, which is then used to create the synthetic data.

### Example

Here is an example of how to generate a synthetic patient dataset using a simple prompt:

```python
from synthetic_data_generator.dynamic_generator import DynamicGenerator

# A prompt describing the desired file structure with varied keywords
prompt = "I need a file for patient records. It should have a patient id, a diagnosis, a begin date for the condition, and a completion date. Also, add a column for notes."

# Create an instance of the dynamic generator
generator = DynamicGenerator()

# Generate 15 rows of synthetic data
try:
    synthetic_data = generator.generate(prompt=prompt, num_rows=15)

    # Print the generated data
    print(synthetic_data.head())

except ValueError as e:
    print(f"Error: {e}")
```

### How It Works

The `DynamicGenerator` uses a flexible, pattern-based `AIParser` to convert your natural language prompt into a structured specification. This specification is then fed to a core data generation engine to create the synthetic data.

This pattern-based approach is designed to be a robust foundation that can be extended in the future with a more sophisticated AI model for even greater flexibility.
