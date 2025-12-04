# AI-Powered Synthetic Data Generator

This module provides a dynamic way to generate synthetic data. It includes a Streamlit UI for an interactive experience and a Python API for programmatic use.

## Running the Streamlit Application

The easiest way to use the generator is with the Streamlit UI. From the UI, you can visually build your file specification, including using the powerful **`contextual_text`** column type to generate meaningful, realistic text based on the content of other columns.

**1. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**2. Run the App:**
```bash
streamlit run app.py
```
This will open a new tab in your browser with the Synthetic Data Generator UI. From there, you can visually define your file specification, generate the data, and download it as a CSV.

---

## Programmatic Usage (Python API)

For more advanced use cases, you can use the Python API directly.

### How It Works

The `DynamicGenerator` uses a flexible, pattern-based `AIParser` to convert a natural language prompt into a structured specification. This specification is then fed to a core data generation engine to create the synthetic data.

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
