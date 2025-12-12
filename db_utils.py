# db_utils.py

import pyodbc
import pandas as pd
from config import DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD, DB_DRIVER

def get_db_connection():
    """
    Establishes and returns a connection to the database.
    Returns None if the connection fails.
    """
    conn_str = (
        f"DRIVER={DB_DRIVER};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD};"
    )
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database Connection Error: {sqlstate}")
        # In a real app, you'd want to log this error more formally.
        return None

def execute_query(query, params=None):
    """
    Executes a SQL query and returns the results as a pandas DataFrame.
    """
    conn = get_db_connection()
    if conn:
        try:
            if params:
                df = pd.read_sql(query, conn, params=params)
            else:
                df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            print(f"Query Execution Error: {e}")
            return pd.DataFrame() # Return empty DataFrame on error
        finally:
            conn.close()
    return pd.DataFrame() # Return empty DataFrame if connection fails

def execute_non_query(query, params=None):
    """
    Executes a non-query SQL command (INSERT, UPDATE, DELETE, CREATE).
    Returns True on success, False on failure.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return True
        except Exception as e:
            print(f"Non-query Execution Error: {e}")
            return False
        finally:
            conn.close()
    return False

def setup_database():
    """
    Creates the necessary tables if they don't exist.
    """
    spec_table_query = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='specifications' and xtype='U')
    CREATE TABLE specifications (
        id INT PRIMARY KEY IDENTITY(1,1),
        name NVARCHAR(255) UNIQUE NOT NULL
    )
    """
    cols_table_query = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='specification_columns' and xtype='U')
    CREATE TABLE specification_columns (
        id INT PRIMARY KEY IDENTITY(1,1),
        specification_id INT NOT NULL,
        column_order INT NOT NULL,
        name NVARCHAR(255) NOT NULL,
        type NVARCHAR(50) NOT NULL,
        options NVARCHAR(MAX),
        FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE CASCADE
    )
    """
    execute_non_query(spec_table_query)
    execute_non_query(cols_table_query)

def load_specifications_from_db():
    """
    Loads all specifications and their columns from the database.
    """
    query = """
    SELECT s.name as spec_name, sc.*
    FROM specifications s
    JOIN specification_columns sc ON s.id = sc.specification_id
    ORDER BY s.name, sc.column_order
    """
    df = execute_query(query)
    all_specs = {}
    if not df.empty:
        for spec_name, group in df.groupby('spec_name'):
            cols = []
            for _, row in group.iterrows():
                cols.append({
                    "name": row['name'],
                    "type": row['type'],
                    "options": json.loads(row['options']) if row['options'] else {}
                })
            all_specs[spec_name] = cols
    return all_specs

def save_specification_to_db(spec_name, columns):
    """
    Saves a full specification to the database, overwriting the old one.
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        # Find spec ID or create a new one
        cursor.execute("SELECT id FROM specifications WHERE name = ?", (spec_name,))
        spec_id_row = cursor.fetchone()
        if spec_id_row:
            spec_id = spec_id_row[0]
            # Delete old columns for this spec
            cursor.execute("DELETE FROM specification_columns WHERE specification_id = ?", (spec_id,))
        else:
            cursor.execute("INSERT INTO specifications (name) VALUES (?)", (spec_name,))
            spec_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

        # Insert new columns
        for i, col in enumerate(columns):
            cursor.execute("""
                INSERT INTO specification_columns (specification_id, column_order, name, type, options)
                VALUES (?, ?, ?, ?, ?)
            """, (spec_id, i, col['name'], col['type'], json.dumps(col.get('options', {}))))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving specification: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_table_names():
    """
    Retrieves a list of all user table names from the database.
    """
    query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    df = execute_query(query)
    return df['TABLE_NAME'].tolist() if not df.empty else []

def get_column_names(table_name):
    """
    Retrieves a list of column names for a given table.
    """
    query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?"
    df = execute_query(query, params=(table_name,))
    return df['COLUMN_NAME'].tolist() if not df.empty else []

def get_data_sample(table, column, percentage):
    """
    Gets a random sample of data from a specified table and column.
    """
    # Note: TABLESAMPLE is SQL Server specific and might not be supported on all editions.
    # Using a simple ORDER BY NEWID() for broader compatibility.
    query = f"SELECT TOP {int(percentage)} PERCENT {column} FROM {table} ORDER BY NEWID()"
    df = execute_query(query)
    return df[column].tolist() if not df.empty else []
