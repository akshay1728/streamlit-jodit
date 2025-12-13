import streamlit as st
import pandas as pd
import json
from synthetic_data_generator.core.generator import SyntheticDataGenerator
import db_utils

# --- Constants ---
COLUMN_TYPES = [
    "text", "date", "choice", "person_id", "contextual_text",
    "integer", "currency", "scvid", "group"
]

def main():
    st.set_page_config(layout="wide")
    st.title("Database-Powered Synthetic Data Generator")

    # --- Database Connection Check ---
    conn = db_utils.get_db_connection()
    if not conn:
        st.error(
            "**Failed to connect to the database.**\n\n"
            "Please ensure the connection details in `config.py` are correct. "
            "If you don't have a database, you can run in mock mode by setting `DB_SERVER = \"mock_server\"` in the config file."
        )
        return # Stop the app from running further

    if conn != "mock_connection":
        # --- Database Setup ---
        # This will create the tables on the first run if they don't exist.
        db_utils.setup_database()
        conn.close() # Close the connection used for the check

    # --- Load all specifications from the database ---
    all_specs = db_utils.load_specifications_from_db()

    # --- Sidebar for Specification Management ---
    st.sidebar.title("Specification Manager")

    if 'current_spec_name' not in st.session_state and all_specs:
        st.session_state.current_spec_name = list(all_specs.keys())[0]
    elif not all_specs:
        st.session_state.current_spec_name = "New Specification"

    def on_spec_change():
        st.session_state.current_spec_name = st.session_state.spec_selector
        # When the selection changes, we must also update the columns in the session state
        st.session_state.columns = all_specs.get(st.session_state.current_spec_name, [])

    st.sidebar.selectbox("Select Specification", list(all_specs.keys()), key="spec_selector", on_change=on_spec_change)

    new_spec_name = st.sidebar.text_input("Or, Create New Specification", value="New Specification")
    if st.sidebar.button("Create and Edit New"):
        st.session_state.current_spec_name = new_spec_name
        st.session_state.columns = []

    # --- Main Area for Column Editing ---
    st.header(f"Editing Specification: '{st.session_state.current_spec_name}'")

    if 'columns' not in st.session_state:
        st.session_state.columns = all_specs.get(st.session_state.current_spec_name, [])

    for i, col in enumerate(st.session_state.columns):
        with st.expander(f"Column {i+1}: {col['name']} ({col['type']})", expanded=True):
            col['name'] = st.text_input("Column Name", col.get('name', ''), key=f"name_{i}")

            current_type_index = COLUMN_TYPES.index(col['type']) if col.get('type') in COLUMN_TYPES else 0
            col['type'] = st.selectbox("Column Type", COLUMN_TYPES, index=current_type_index, key=f"type_{i}")

            options = col.get('options', {})

            if col['type'] == 'date':
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

            elif col['type'] in ['integer', 'currency']:
                options['min'] = st.number_input("Min Value", value=options.get('min', 0), key=f"min_{i}")
                options['max'] = st.number_input("Max Value", value=options.get('max', 100), key=f"max_{i}")
            elif col['type'] in ['scvid', 'group']:
                tables = db_utils.get_table_names()
                options['table'] = st.selectbox("Source Table", tables, key=f"table_{i}")
                if options['table']:
                    columns = db_utils.get_column_names(options['table'])
                    options['column'] = st.selectbox("Source Column", columns, key=f"column_{i}")
                options['percentage'] = st.slider("Percentage of Values to Use", 1, 100, options.get('percentage', 100), key=f"perc_{i}")

            col['options'] = options

            if st.button("Remove Column", key=f"remove_{i}"):
                st.session_state.columns.pop(i)
                st.rerun()

    # --- Add Column Workflow ---
    st.subheader("Add a New Column")
    with st.form("new_col_form", clear_on_submit=True):
        new_name = st.text_input("New Column Name")
        new_type = st.selectbox("New Column Type", COLUMN_TYPES)
        if st.form_submit_button("Add to Specification"):
            st.session_state.columns.append({"name": new_name, "type": new_type, "options": {}})
            st.rerun()

    # --- Actions ---
    st.header("Actions")
    if st.button("Save Specification to DB"):
        success = db_utils.save_specification_to_db(st.session_state.current_spec_name, st.session_state.columns)
        if success:
            st.success(f"Specification '{st.session_state.current_spec_name}' saved to the database!")
        else:
            st.error("Failed to save the specification to the database. Check console for errors.")

    num_rows = st.number_input("Number of Rows to Generate", 1, 100000, 100)
    if st.button("Generate Data"):
        spec_for_gen = {col['name']: {'type': col['type'], 'options': col.get('options', {})} for col in st.session_state.columns}
        generator = SyntheticDataGenerator(spec_for_gen)
        st.session_state.generated_data = generator.generate(num_rows)

    if 'generated_data' in st.session_state and st.session_state.generated_data is not None:
        st.subheader("Data Preview")
        st.dataframe(st.session_state.generated_data.head())
        csv = st.session_state.generated_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"{st.session_state.current_spec_name}_synthetic_data.csv",
            mime='text/csv'
        )

if __name__ == "__main__":
    main()
