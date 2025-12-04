import streamlit as st
import pandas as pd
from synthetic_data_generator.core.generator import SyntheticDataGenerator

def initialize_session_state():
    """
    Initializes the session state for the application.
    """
    if 'columns' not in st.session_state:
        # Start with a default health data example
        st.session_state.columns = [
            {"id": 0, "name": "start_date", "type": "date", "options": {"start": "-2y", "end": "today"}},
            {"id": 1, "name": "end_date", "type": "date", "options": {"start": "start_date", "end": "+1y"}},
            {"id": 2, "name": "health_condition", "type": "choice", "options": {"choices": ["diabetes", "BP", "heart condition"]}},
            {"id": 3, "name": "comment", "type": "text", "options": {"max_nb_chars": 150}},
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
        col_name, col_type, col_options = st.columns([2, 2, 3])

        with col_name:
            col['name'] = st.text_input("Column Name", value=col['name'], key=f"name_{col['id']}")

        with col_type:
            col['type'] = st.selectbox("Column Type",
                                       options=["person_id", "date", "choice", "text"],
                                       index=["person_id", "date", "choice", "text"].index(col['type']),
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
        st.dataframe(st.session_state.generated_data.head())

        csv = st.session_state.generated_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='synthetic_data.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()
