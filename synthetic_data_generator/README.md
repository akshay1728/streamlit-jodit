# AI-Powered Synthetic Data Generator

This module provides a dynamic way to generate synthetic data using natural language prompts. Instead of defining a detailed, structured specification, you can describe the file you need, and the system will interpret your request to generate the data.

## Usage

To use the synthetic data generator, describe the file you want to create in a natural language prompt. The system will parse your request and automatically generate a structured specification, which is then used to create the synthetic data.

### Extending the AI with Custom Patterns

The real power of this generator comes from its extensibility. If the built-in patterns do not meet your needs, you can easily "teach" the AI new concepts by creating your own custom patterns.

A pattern is a simple dictionary with three keys:
- `name`: The standardized, underscore_cased name for your column.
- `keywords`: A list of words or phrases that should trigger this pattern.
- `spec`: A valid specification dictionary for the `core.SyntheticDataGenerator`.

### Example

Here is an example of how to define custom patterns and use them to generate a synthetic inventory dataset:

```python
from synthetic_data_generator.dynamic_generator import DynamicGenerator

# Define a list of custom patterns for a new domain (e.g., inventory)
custom_patterns = [
    {
        "name": "product_sku",
        "keywords": ["product sku", "sku", "item code"],
        "spec": {"type": "text", "max_nb_chars": 10}
    },
    {
        "name": "price",
        "keywords": ["price", "cost", "value"],
        "spec": {"type": "text", "max_nb_chars": 6}
    }
]

# A new prompt that uses our custom keywords
prompt = "I need an inventory file. It should list the product sku and the price of each item. It also needs a user id for the person who logged the entry."

# Create an instance of the dynamic generator with our custom patterns
generator = DynamicGenerator(custom_patterns=custom_patterns)

# Generate 10 rows of synthetic data
try:
    synthetic_data = generator.generate(prompt=prompt, num_rows=10)

    # Print the generated data
    print(synthetic_data.head())

except ValueError as e:
    print(f"Error: {e}")
```

### How It Works

The `DynamicGenerator` uses a flexible, pattern-based `AIParser` to convert your natural language prompt into a structured specification. When you provide custom patterns, they are merged with the built-in ones, extending the AI's knowledge. This specification is then fed to a core data generation engine to create the synthetic data.
