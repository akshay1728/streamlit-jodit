import streamlit as st
import pandas as pd
import json
from synthetic_data_generator.core.generator import SyntheticDataGenerator
import db_utils
import config as conf

# --- Constants ---
COLUMN_TYPES = [
    "text", "date", "choice", "person_id", "contextual_text",
    "integer", "currency", "scvid", "group"
]

def set_sessionState():
    if 'user_conn' not in st.session_state:
        st.session_state.user_conn = None
    if 'user_engine' not in st.session_state:
        st.session_state.user_engine = 'None'
    if 'source_conn' not in st.session_state:
        st.session_state.source_conn = None
    if 'source_engine' not in st.session_state:
        st.session_state.source_engine = 'None'
    if 'source_server' not in st.session_state:
        st.session_state.source_server = 'None'
    if 'source_database' not in st.session_state:
        st.session_state.source_database = 'None'
    if 'is_clicked' not in st.session_state:
        st.session_state.is_clicked = 0

def fnSubmit():
    st.session_state.is_clicked = 1

def render_options_for_new_column(server, db):
    """Renders the correct UI inputs for the new column based on its type."""
    col_type = st.session_state.new_column['type']
    options = st.session_state.new_column['options']
    if col_type == 'date':
        options['start'] = st.text_input("Start Date Ref", "-1y", key="new_date_start")
        options['end'] = st.text_input("End Date Ref", "today", key="new_date_end")
    elif col_type == 'choice':
        choices_str = st.text_area("Choices (comma-separated)", key="new_choice_str")
        options['choices'] = [c.strip() for c in choices_str.split(',') if c.strip()]
    elif col_type in ['integer', 'currency']:
        options['min'] = st.number_input("Min Value", 0, key="new_min")
        options['max'] = st.number_input("Max Value", 100, key="new_max")
    elif col_type == 'contextual_text':
        available_context_cols = [c['name'] for c in st.session_state.columns]
        if not available_context_cols:
            st.warning("You must define at least one other column to use as a context.")
        else:
            options['context_column'] = st.selectbox("Context Column", available_context_cols, key="new_context_col")
            templates_str = st.text_area("Templates (JSON format)", "{}", height=150, key="new_templates_str")
            try:
                options['templates'] = json.loads(templates_str)
            except json.JSONDecodeError:
                st.error("Invalid JSON format in templates.")
    elif col_type in ['scvid', 'group']:
        if 'sources' not in options:
            options['sources'] = []

        st.write("Data Sources")

        for j, source in enumerate(options['sources']):
            c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
            tables = db_utils.get_table_names(server, db, st.session_state.username)
            table_index = tables.index(source['table']) if source.get('table') in tables else 0
            source['table'] = c1.selectbox("Table", tables, index=table_index, key=f"new_table_{j}")

            if source['table']:
                columns = db_utils.get_column_names(source['table'], server, db, st.session_state.username)
                column_index = columns.index(source['column']) if source.get('column') in columns else 0
                source['column'] = c2.selectbox("Column", columns, index=column_index, key=f"new_col_{j}")

            source['percentage'] = c3.number_input("Percentage", 1, 100, source.get('percentage', 100), key=f"new_perc_{j}")

            if c4.button("X", key=f"new_remove_source_{j}"):
                options['sources'].pop(j)
                st.rerun()

        if st.button("Add Source", key="new_add_source"):
            options['sources'].append({'table': '', 'column': '', 'percentage': 100})
            st.rerun()

        total_percentage = sum(s['percentage'] for s in options['sources'])
        if total_percentage != 100:
            st.warning(f"Percentages must sum to 100. Current total: {total_percentage}%")

def main():
    st.set_page_config(layout="wide")
    st.title("Database-Powered Synthetic Data Generator")
    set_sessionState()
    # Adding a placeholder for the username, as it's now a required argument
    st.session_state.username = "your_email@domain.com"
    st.session_state.user_conn, st.session_state.user_engine = db_utils.get_db_connection(conf.BASE_SERVER, conf.BASE_DATABASE, st.session_state.username)

    st.sidebar.title("Specification Manager")
    server_query = " ovm.get_autDBServer"
    server_df = pd.read_sql(server_query, con=st.session_state.user_conn)
    db_query = " ovm.get_autDB"
    db_df = pd.read_sql(db_query, con=st.session_state.user_conn)
    src_server = st.sidebar.selectbox('Server', options=server_df, key="source_server")
    src_database = st.sidebar.selectbox("Database", options=db_df, key="source_database")
    st.sidebar.button('Connect', on_click=fnSubmit, key='a')

    source_server = st.session_state.source_server
    source_database = st.session_state.source_database

    if st.session_state.is_clicked == 1:
        all_specs = db_utils.load_specifications_from_db(conf.BASE_SERVER, conf.BASE_DATABASE, st.session_state.username)

        if 'current_spec_name' not in st.session_state and all_specs:
            st.session_state.current_spec_name = list(all_specs.keys())[0]
        elif not all_specs:
            st.session_state.current_spec_name = "New Spec"

        def on_spec_change():
            st.session_state.current_spec_name = st.session_state.spec_selector
            st.session_state.columns = all_specs.get(st.session_state.current_spec_name, [])

        st.sidebar.selectbox("Select Specification", list(all_specs.keys()), key="spec_selector", on_change=on_spec_change)

        st.header(f"Editing: '{st.session_state.current_spec_name}'")
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
                    options['choices'] = [c.strip() for c in choices_str.split(',') if c.strip()]
                elif col['type'] == 'contextual_text':
                    available_context_cols = [c['name'] for c in st.session_state.columns if c is not col]
                    if not available_context_cols:
                        st.warning("You must define at least one other column to use as a context.")
                    else:
                        context_col_index = available_context_cols.index(options['context_column']) if options.get('context_column') in available_context_cols else 0
                        options['context_column'] = st.selectbox("Context Column", available_context_cols, index=context_col_index, key=f"context_{i}")
                        templates_str = st.text_area("Templates (JSON format)", json.dumps(options.get('templates', {}), indent=2), height=150, key=f"templates_{i}")
                        try:
                            options['templates'] = json.loads(templates_str)
                        except json.JSONDecodeError:
                            st.error("Invalid JSON format in templates.")
                elif col['type'] in ['integer', 'currency']:
                    options['min'] = st.number_input("Min Value", value=options.get('min', 0), key=f"min_{i}")
                    options['max'] = st.number_input("Max Value", value=options.get('max', 100), key=f"max_{i}")
                elif col['type'] in ['scvid', 'group']:
                    if 'sources' not in options:
                        options['sources'] = []

                    st.write("Data Sources")

                    for j, source in enumerate(options['sources']):
                        c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
                        tables = db_utils.get_table_names(source_server, source_database, st.session_state.username)
                        table_index = tables.index(source['table']) if source.get('table') in tables else 0
                        source['table'] = c1.selectbox("Table", tables, index=table_index, key=f"table_{i}_{j}")

                        if source['table']:
                            columns = db_utils.get_column_names(source['table'], source_server, source_database, st.session_state.username)
                            column_index = columns.index(source['column']) if source.get('column') in columns else 0
                            source['column'] = c2.selectbox("Column", columns, index=column_index, key=f"col_{i}_{j}")

                        source['percentage'] = c3.number_input("Percentage", 1, 100, source.get('percentage', 100), key=f"perc_{i}_{j}")

                        if c4.button("X", key=f"remove_source_{i}_{j}"):
                            options['sources'].pop(j)
                            st.rerun()

                    if st.button("Add Source", key=f"add_source_{i}"):
                        options['sources'].append({'table': '', 'column': '', 'percentage': 100})
                        st.rerun()

                    total_percentage = sum(s['percentage'] for s in options['sources'])
                    if total_percentage != 100:
                        st.warning(f"Percentages must sum to 100. Current total: {total_percentage}%")

                col['options'] = options

                if st.button("Remove Column", key=f"remove_{i}"):
                    st.session_state.columns.pop(i)
                    st.rerun()

        st.subheader("Add a New Column")
        if 'new_column' not in st.session_state:
            st.session_state.new_column = {"name": "", "type": "text", "options": {}}
        if 'new_col_type_selector' not in st.session_state:
            st.session_state.new_col_type_selector = st.session_state.new_column['type']

        st.session_state.new_column['name'] = st.text_input("Name", st.session_state.new_column['name'])

        def on_type_change():
            st.session_state.new_column['type'] = st.session_state.new_col_type_selector
            st.session_state.new_column['options'] = {}

        st.selectbox("Type", COLUMN_TYPES,
            key='new_col_type_selector',
            on_change=on_type_change
        )
        st.session_state.new_column['type'] = st.session_state.new_col_type_selector

        render_options_for_new_column(source_server, source_database)

        if st.button("Add Column to Specification"):
            if st.session_state.new_column['name']:
                st.session_state.columns.append(st.session_state.new_column.copy())
                st.session_state.new_column = {"name": "", "type": "text", "options": {}}
                st.rerun()
            else:
                st.warning("Column name cannot be empty.")

        st.header("Actions")
        if st.button("Save Specification to DB"):
            success = db_utils.save_specification_to_db(st.session_state.current_spec_name, st.session_state.columns, conf.BASE_SERVER, conf.BASE_DATABASE, st.session_state.username)
            if success:
                st.success(f"Specification '{st.session_state.current_spec_name}' saved to the database!")
            else:
                st.error("Failed to save the specification to the database. Check console for errors.")

        num_rows = st.number_input("Number of Rows to Generate", 1, 100000, 100)
        if st.button("Generate Data"):
            spec_for_gen = {col['name']: {'type': col['type'], 'options': col.get('options', {})} for col in st.session_state.columns}
            generator = SyntheticDataGenerator(spec_for_gen, source_server, source_database, st.session_state.username)
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
