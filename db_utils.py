# db_utils.py
import pyodbc
import pandas as pd
import json
from config import DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD, DB_DRIVER

# --- Mock Data ---
MOCK_SPECS = {
    "Health_Data_Spec": [
        {"name": "start_date", "type": "date", "options": {"start": "-2y", "end": "-1y"}},
        {"name": "health_condition", "type": "choice", "options": {"choices": ["Diabetes", "Asthma", "Heart Condition"]}}
    ]
}
MOCK_TABLES = ["patients", "admissions", "treatments"]
MOCK_COLUMNS = {"patients": ["patient_id", "first_name", "last_name"], "admissions": ["admission_id", "patient_id", "admission_date"]}

# --- Connection ---
def get_db_connection():
    if DB_SERVER == "mock_server":
        return "mock_connection"
    try:
        conn_str = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD};"
        return pyodbc.connect(conn_str)
    except pyodbc.Error:
        return None

# --- Query Execution ---
def execute_query(query, params=None):
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    if conn == "mock_connection":
        if "GetAllSpecifications" in query:
            return pd.DataFrame([
                {"spec_name": "Health_Data_Spec", "col_name": "start_date", "type": "date", "options": json.dumps({"start": "-2y", "end": "-1y"}), "column_order": 0},
                {"spec_name": "Health_Data_Spec", "col_name": "health_condition", "type": "choice", "options": json.dumps({"choices": ["Diabetes", "Asthma"]}), "column_order": 1}
            ])
        if "INFORMATION_SCHEMA.TABLES" in query:
            return pd.DataFrame({"TABLE_NAME": MOCK_TABLES})
        if "INFORMATION_SCHEMA.COLUMNS" in query:
            table_name = params[0] if isinstance(params, tuple) else "patients"
            return pd.DataFrame({"COLUMN_NAME": MOCK_COLUMNS.get(table_name, [])})
        if "SELECT TOP" in query:
            # For get_data_sample
            return pd.DataFrame({"mock_column": [f"mock_data_{i}" for i in range(5)]})
        return pd.DataFrame()

    try:
        return pd.read_sql(query, conn, params=params)
    except Exception:
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def execute_non_query(query, params=None):
    conn = get_db_connection()
    if not conn: return False
    if conn == "mock_connection": return True
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params) if params else cursor.execute(query)
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if conn: conn.close()

# --- Setup ---
def setup_database():
    if DB_SERVER == "mock_server": return
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
    _create_stored_procedures()

def _create_stored_procedures():
    if DB_SERVER == "mock_server": return
    # Drop existing procedures if they exist, to ensure they are up-to-date
    execute_non_query("DROP PROCEDURE IF EXISTS GetAllSpecifications")
    execute_non_query("DROP PROCEDURE IF EXISTS SaveSpecification")

    get_all_proc = """
    CREATE PROCEDURE GetAllSpecifications
    AS
    BEGIN
        SELECT s.name as spec_name, sc.name as col_name, sc.type, sc.options, sc.column_order
        FROM specifications s
        JOIN specification_columns sc ON s.id = sc.specification_id
        ORDER BY s.name, sc.column_order;
    END
    """

    save_spec_proc = """
    CREATE PROCEDURE SaveSpecification
        @SpecName NVARCHAR(255),
        @ColumnsJson NVARCHAR(MAX)
    AS
    BEGIN
        BEGIN TRANSACTION;

        DECLARE @SpecId INT;
        SELECT @SpecId = id FROM specifications WHERE name = @SpecName;

        IF @SpecId IS NULL
        BEGIN
            INSERT INTO specifications (name) VALUES (@SpecName);
            SET @SpecId = SCOPE_IDENTITY();
        END
        ELSE
        BEGIN
            DELETE FROM specification_columns WHERE specification_id = @SpecId;
        END

        INSERT INTO specification_columns (specification_id, column_order, name, type, options)
        SELECT @SpecId, JSON_VALUE(c.value, '$.order'), JSON_VALUE(c.value, '$.name'), JSON_VALUE(c.value, '$.type'), JSON_QUERY(c.value, '$.options')
        FROM OPENJSON(@ColumnsJson) AS c;

        COMMIT TRANSACTION;
    END
    """
    execute_non_query(get_all_proc)
    execute_non_query(save_spec_proc)

# --- Data Access ---
def load_specifications_from_db():
    df = execute_query("EXEC GetAllSpecifications")
    all_specs = {}
    if not df.empty:
        for spec_name, group in df.groupby('spec_name'):
            cols = []
            for _, row in group.sort_values('column_order').iterrows():
                cols.append({"name": row['col_name'], "type": row['type'], "options": json.loads(row.get('options', '{}') or '{}')})
            all_specs[spec_name] = cols
    return all_specs if all_specs else (MOCK_SPECS if DB_SERVER == "mock_server" else {})


def save_specification_to_db(spec_name, columns):
    for i, col in enumerate(columns): col['order'] = i
    columns_json = json.dumps(columns)
    return execute_non_query("EXEC SaveSpecification ?, ?", params=(spec_name, columns_json))

def get_table_names():
    df = execute_query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    if not df.empty and 'TABLE_NAME' in df.columns:
        return df['TABLE_NAME'].tolist()
    return []

def get_column_names(table_name):
    df = execute_query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", params=(table_name,))
    if not df.empty and 'COLUMN_NAME' in df.columns:
        return df['COLUMN_NAME'].tolist()
    return []

def get_data_sample(table, column, percentage):
    # This is simplified for the mock. A real implementation would be more robust.
    df = execute_query(f"SELECT TOP {int(percentage)} PERCENT {column} FROM {table} ORDER BY NEWID()")
    return df[column].tolist() if not df.empty else []
