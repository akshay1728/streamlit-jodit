import streamlit as st
import pandas as pd
import json
from synthetic_data_generator.core.generator import SyntheticDataGenerator
import file_storage

def main():
    st.set_page_config(layout="wide")
    st.title("File-Based Synthetic Data Generator")

    all_specs = file_storage.load_all_specs()

    # --- Sidebar for Specification Management ---
    st.sidebar.title("Specification Manager")

    if 'current_spec_name' not in st.session_state:
        st.session_state.current_spec_name = list(all_specs.keys())[0]

    def on_spec_change():
        st.session_state.current_spec_name = st.session_state.spec_selector

    st.sidebar.selectbox("Select a Specification", options=all_specs.keys(), key="spec_selector", on_change=on_spec_change)

    new_spec_name = st.sidebar.text_input("Or, Create a New Specification Name")
    if st.sidebar.button("Create and Edit New"):
        st.session_state.current_spec_name = new_spec_name
        st.session_state.columns = []

    # --- Main Area for Column Editing ---
    st.header(f"Editing Specification: '{st.session_state.current_spec_name}'")

    if 'columns' not in st.session_state:
        st.session_state.columns = all_specs.get(st.session_state.current_spec_name, [])

    for i, col in enumerate(st.session_state.columns):
        with st.expander(f"Column {i+1}: {col['name']} ({col['type']})", expanded=True):
            col['name'] = st.text_input("Column Name", col['name'], key=f"name_{i}")
            col['type'] = st.selectbox("Column Type", ["text", "date", "choice", "person_id", "contextual_text"],
                                       index=["text", "date", "choice", "person_id", "contextual_text"].index(col['type']),
                                       key=f"type_{i}")

            options = col.get('options', {})
            if col['type'] == 'date':
                # UI to choose between dynamic text reference or fixed date picker
                is_fixed_date = isinstance(options.get('start'), str) and options.get('start', '').count('-') == 2
                date_input_method = st.radio("Date Input Method", ["Dynamic Reference", "Fixed Date"],
                                             index=1 if is_fixed_date else 0,
                                             horizontal=True, key=f"date_method_{i}")

                if date_input_method == "Dynamic Reference":
                    options['start'] = st.text_input("Start Date Reference", options.get('start', '-1y'), key=f"start_ref_{i}")
                    options['end'] = st.text_input("End Date Reference", options.get('end', 'today'), key=f"end_ref_{i}")
                else: # Fixed Date
                    try:
                        start_date_val = pd.to_datetime(options.get('start')).date()
                    except (ValueError, pd._libs.tslibs.parsing.DateParseError):
                        start_date_val = pd.Timestamp.now().date()

                    try:
                        end_date_val = pd.to_datetime(options.get('end')).date()
                    except (ValueError, pd._libs.tslibs.parsing.DateParseError):
                        end_date_val = pd.Timestamp.now().date()

                    start_date = st.date_input("Start Date", value=start_date_val, key=f"start_date_{i}")
                    end_date = st.date_input("End Date", value=end_date_val, key=f"end_date_{i}")
                    options['start'] = start_date.strftime('%Y-%m-%d')
                    options['end'] = end_date.strftime('%Y-%m-%d')

            elif col['type'] == 'choice':
                choices_str = st.text_area("Choices (comma-separated)", ", ".join(options.get('choices', [])), key=f"choices_{i}")
                options['choices'] = [c.strip() for c in choices_str.split(',')]
            elif col['type'] == 'contextual_text':
                available_context_cols = [c['name'] for c in st.session_state.columns if c is not col]
                if not available_context_cols:
                    st.warning("You must define at least one other column to use as a context.")
                else:
                    options['context_column'] = st.selectbox("Context Column", available_context_cols, key=f"context_{i}")
                    templates_str = st.text_area("Templates (JSON format)", json.dumps(options.get('templates', {}), indent=2), height=150, key=f"templates_{i}")
                    try:
                        options['templates'] = json.loads(templates_str)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format in templates.")
            col['options'] = options

            if st.button("Remove Column", key=f"remove_{i}"):
                st.session_state.columns.pop(i)
                st.rerun()

    # --- Add Column Workflow ---
    st.subheader("Add a New Column")
    all_unique_cols = file_storage.get_all_unique_columns(all_specs)
    add_choice = st.radio("Add Method", ["Define New", "Reuse Existing"], horizontal=True)

    if add_choice == "Reuse Existing" and all_unique_cols:
        col_display = {f"{c['name']} ({c['type']})": c for c in all_unique_cols}
        selected_col_key = st.selectbox("Select an existing column", options=col_display.keys())
        if st.button("Add Selected Column"):
            st.session_state.columns.append(col_display[selected_col_key])
            st.rerun()
    else:
        with st.form("new_col_form", clear_on_submit=True):
            new_name = st.text_input("New Column Name")
            new_type = st.selectbox("New Column Type", ["text", "date", "choice", "person_id", "contextual_text"])
            if st.form_submit_button("Add to Specification"):
                st.session_state.columns.append({"name": new_name, "type": new_type, "options": {}})
                st.rerun()

    # --- Actions ---
    st.header("Actions")
    if st.button("Save Specification"):
        all_specs[st.session_state.current_spec_name] = st.session_state.columns
        file_storage.save_all_specs(all_specs)
        st.success(f"Specification '{st.session_state.current_spec_name}' saved successfully!")

    num_rows = st.number_input("Number of Rows", 1, 100000, 100)
    if st.button("Generate Data"):
        spec = {col['name']: {'type': col['type'], **col.get('options', {})} for col in st.session_state.columns}
        generator = SyntheticDataGenerator(spec)
        st.session_state.generated_data = generator.generate(num_rows)

    if 'generated_data' in st.session_state and st.session_state.generated_data is not None:
        st.subheader("Data Preview")
        st.dataframe(st.session_state.generated_data.head())
        csv = st.session_state.generated_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"{st.session_state.current_spec_name}.csv",
            mime='text/csv'
        )

if __name__ == "__main__":
    main()
