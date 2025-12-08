# file_storage.py

import json
import os

SPECS_FILE = 'specifications.json'

def load_all_specs():
    """
    Loads all specifications from the JSON file.
    If the file doesn't exist, it returns a default structure.
    """
    if not os.path.exists(SPECS_FILE):
        # Create a default file if it doesn't exist
        default_specs = {
            "Sample Health Spec": [
                {"name": "start_date", "type": "date", "options": {"start": "-2y", "end": "today"}},
                {"name": "end_date", "type": "date", "options": {"start": "start_date", "end": "+1y"}},
                {"name": "health_condition", "type": "choice", "options": {"choices": ["diabetes", "BP", "heart condition"]}},
                {"name": "comment", "type": "contextual_text", "options": {
                    "context_column": "health_condition",
                    "templates": {
                        "diabetes": ["Patient reports stable blood sugar levels.", "Continue monitoring glucose."],
                        "BP": ["Blood pressure is high. Advised patient to reduce sodium.", "BP is within normal range."],
                        "heart condition": ["Patient reports occasional chest pain.", "No new symptoms reported."]
                    }
                }},
                {"name": "person_id", "type": "person_id", "options": {}},
            ]
        }
        save_all_specs(default_specs)
        return default_specs

    with open(SPECS_FILE, 'r') as f:
        return json.load(f)

def save_all_specs(specs):
    """
    Saves the entire specifications dictionary to the JSON file.
    """
    with open(SPECS_FILE, 'w') as f:
        json.dump(specs, f, indent=4)

def get_all_unique_columns(specs):
    """
    Extracts a list of all unique column definitions from the specs.
    """
    unique_columns = {}
    for spec_name, columns in specs.items():
        for col in columns:
            # Create a unique key for each column based on its properties
            col_key = (col['name'], col['type'], json.dumps(col.get('options', {}), sort_keys=True))
            if col_key not in unique_columns:
                unique_columns[col_key] = col
    return list(unique_columns.values())
