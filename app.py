import streamlit as st
import pandas as pd
import json
from synthetic_data_generator.core.generator import SyntheticDataGenerator

def get_default_templates():
    """Returns the default templates for health comments."""
    return {
        "diabetes": [
            "Patient reports stable blood sugar levels.",
            "Continue monitoring blood glucose. Adjust insulin as needed.",
            "Discussed diet and exercise plan."
        ],
        "BP": [
            "Blood pressure is high at 150/95. Advised patient to reduce sodium intake.",
            "Patient's blood pressure is within normal range.",
            "Medication for BP seems effective. No changes at this time."
        ],
        "heart condition": [
            "Patient reports occasional chest pain. EKG scheduled.",
            "No new symptoms. Continue current medication regimen.",
            "Follow-up appointment set for 3 months."
        ]
    }

def initialize_session_state():
    """
    Initializes the session state for the application.
    """
    if 'columns' not in st.session_state:
        # Start with a default health data example using the new contextual text
        st.session_state.columns = [
            {"id": 0, "name": "start_date", "type": "date", "options": {"start": "-2y", "end": "today"}},
            {"id": 1, "name": "end_date", "type": "date", "options": {"start": "start_date", "end": "+1y"}},
            {"id": 2, "name": "health_condition", "type": "choice", "options": {"choices": ["diabetes", "BP", "heart condition"]}},
            {"id": 3, "name": "comment", "type": "contextual_text", "options": {"context_column": "health_condition", "templates": get_default_templates()}},
            {"id": 4, "name": "person_id", "type": "person_id", "options": {}},
        ]
    if 'next_id' not in st.session_state:
        st.session_state.next_id = 5
    if 'generated_data' not in st.session_state:
        st.session_state.generated_data = None

def build_spec_from_ui():
    """
    Builds the specification dictionary from the UI state.
    """
    spec = {}
    for col in st.session_state.columns:
        spec[col['name']] = {"type": col['type'], **col['options']}
    return spec

def main():
    """
    Main function for the Streamlit application.
    """
    st.set_page_config(layout="wide")
    st.title("Synthetic Data Generator")

    initialize_session_state()

    st.header("1. Define Your File Specification")

    # --- Column Configuration UI ---
    for i, col in enumerate(st.session_state.columns):
        st.markdown(f"---")
        col_name, col_type, col_options = st.columns([2, 2, 4])

        with col_name:
            col['name'] = st.text_input("Column Name", value=col['name'], key=f"name_{col['id']}")

        with col_type:
            col['type'] = st.selectbox("Column Type",
                                       options=["person_id", "date", "choice", "text", "contextual_text"],
                                       index=["person_id", "date", "choice", "text", "contextual_text"].index(col['type']),
                                       key=f"type_{col['id']}")

        with col_options:
            if col['type'] == 'date':
                col['options']['start'] = st.text_input("Start Reference", value=col['options'].get('start', '-2y'), key=f"date_start_{col['id']}")
                col['options']['end'] = st.text_input("End Reference", value=col['options'].get('end', 'today'), key=f"date_end_{col['id']}")

            elif col['type'] == 'choice':
                choices_str = st.text_area("Choices (comma-separated)",
                                           value=",".join(col['options'].get('choices', ['option1', 'option2'])),
                                           key=f"choice_options_{col['id']}")
                col['options']['choices'] = [choice.strip() for choice in choices_str.split(',')]

            elif col['type'] == 'text':
                col['options']['max_nb_chars'] = st.number_input("Max Chars", value=col['options'].get('max_nb_chars', 100), key=f"text_max_chars_{col['id']}")

            elif col['type'] == 'contextual_text':
                available_context_cols = [c['name'] for c in st.session_state.columns if c['id'] != col['id']]

                if not available_context_cols:
                    st.warning("You must define at least one other column to use as context.")
                    # Disable the fields and clear any existing options
                    col['options'] = {}
                else:
                    # Set a default if the saved context column is no longer available
                    saved_context_col = col['options'].get('context_column')
                    current_context_col = saved_context_col if saved_context_col in available_context_cols else available_context_cols[0]

                    col['options']['context_column'] = st.selectbox("Context Column", options=available_context_cols,
                                                                    index=available_context_cols.index(current_context_col),
                                                                    key=f"context_col_{col['id']}")

                    templates_str = st.text_area("Templates (JSON format)",
                                                 value=json.dumps(col['options'].get('templates', {}), indent=2),
                                                 height=200,
                                                 key=f"context_templates_{col['id']}")
                    try:
                        col['options']['templates'] = json.loads(templates_str)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format for templates.")

            else:
                # Clear options for types that don't have them
                col['options'] = {}

        # --- Remove Column Button ---
        if st.button(f"Remove '{col['name']}'", key=f"remove_{col['id']}"):
            st.session_state.columns.pop(i)
            st.rerun()

    # --- Add Column Button ---
    if st.button("Add Another Column"):
        new_col = {"id": st.session_state.next_id, "name": f"new_column_{st.session_state.next_id}", "type": "text", "options": {"max_nb_chars": 50}}
        st.session_state.columns.append(new_col)
        st.session_state.next_id += 1
        st.rerun()

    st.markdown(f"---")
    st.header("2. Generate and Download Data")

    num_rows = st.number_input("Number of rows to generate", min_value=1, max_value=10000, value=100)

    if st.button("Generate Data"):
        try:
            spec = build_spec_from_ui()
            generator = SyntheticDataGenerator(specifications=spec)
            st.session_state.generated_data = generator.generate(num_rows=num_rows)
            st.success("Data generated successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.generated_data = None

    if st.session_state.generated_data is not None:
        st.subheader("Data Preview")
        st.dataframe(st.session_state.generated_data.head(20)) # Show more rows to see variety

        csv = st.session_state.generated_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='synthetic_data.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()
