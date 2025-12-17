import streamlit as st
import pandas as pd
import json
from sqlalchemy import create_engine
import pyodbc
import config as conf
import urllib

def get_db_connection(server, database, username):
    """Creates a SQLAlchemy engine for a given database type."""
    try:
        conn = pyodbc.connect(
            f"Driver={conf.DRIVER};SERVER={server};DATABASE={database};UID={username}; Authentication=ActiveDirectoryInteractive",
            autocommit=True)

        quoted = urllib.parse.quote_plus(
            f"Driver={conf.DRIVER};SERVER={server};DATABASE={database};UID={username};Authentication=ActiveDirectoryInteractive")
        engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted), fast_executemany=True)
        return conn, engine
    except Exception as e:
        st.error(f"Error creating connection: {e}")
        return None, None

def execute_query(query, server, db, params=None):
    conn, engine = get_db_connection(server, db)
    if not conn:
        return pd.DataFrame()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        if conn: conn.close()

def execute_non_query(query, server, db, params=None):
    conn, engine = get_db_connection(server, db)
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params) if params else cursor.execute(query)
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if conn: conn.close()

def load_specifications_from_db(server, db):
    df = execute_query("EXEC GetAllSpecifications", server, db)
    all_specs = {}
    if not df.empty:
        for spec_name, group in df.groupby('spec_name'):
            cols = []
            for _, row in group.sort_values('column_order').iterrows():
                cols.append({"name": row['col_name'], "type": row['type'], "options": json.loads(row.get('options', '{}') or '{}')})
            all_specs[spec_name] = cols
    return all_specs if all_specs else {}

def save_specification_to_db(spec_name, columns, server, db):
    for i, col in enumerate(columns): col['order'] = i
    columns_json = json.dumps(columns)
    return execute_non_query("EXEC SaveSpecification ?, ?", server, db, params=(spec_name, columns_json))

def get_table_names(server, db):
    df = execute_query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'", server, db)
    if not df.empty and 'TABLE_NAME' in df.columns:
        return df['TABLE_NAME'].tolist()
    return []

def get_column_names(table_name, server, db):
    df = execute_query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", server, db, params=(table_name,))
    if not df.empty and 'COLUMN_NAME' in df.columns:
        return df['COLUMN_NAME'].tolist()
    return []

def get_data_sample(table, column, percentage, server, db):
    df = execute_query(f"SELECT TOP {int(percentage)} PERCENT {column} FROM {table} ORDER BY NEWID()", server, db)
    return df[column].tolist() if not df.empty else []
