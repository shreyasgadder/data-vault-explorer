import json
import os
import sys
import pandas as pd
from Utils.DBConnection import DatabaseConnector
import datetime
import logging
import traceback 

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def execute_query(cursor, entity):
    """
    Execute a SELECT query on the given entity and return its status.
    """
    logging.info(f"Executing query on {entity}")
    try:
        cursor.execute(f"SELECT * FROM {entity}")
        return {
            'Tables': entity,
            'Select Query': f'SELECT * FROM {entity};',
            'Error Description': 'Working'
        }
    except Exception as e:
        return {
            'Tables': entity,
            'Select Query': f'SELECT * FROM {entity};',
            'Error Description': str(e)
        }


def get_table_list(cursor, db_type, database, schema):
    if db_type == 'PostgreSQL':
        table_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"
    elif db_type == 'Oracle':
        table_query = f"SELECT table_name FROM all_tables WHERE owner = '{schema}';"
    elif db_type in ['Impala', 'Hive', 'MySQL']:
        table_query = f"SHOW TABLES IN {schema}"
    elif db_type == 'Snowflake':
        table_query = f"SHOW TABLES IN SCHEMA {database}.{schema}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    print(table_query)
    cursor.execute(table_query)
    res = cursor.fetchall()
    return [table[0] for table in res]


def test_tables(entities, cursor, include_schema, schema, db_connector):
    """
    Test specific entities (tables or views).
    """
    exec_status = []
    for entity in entities:
        full_entity = f"{schema}.{entity}" if include_schema else entity
        exec_status.append(execute_query(cursor, full_entity))
    # Reconnect after processing the batch
    conn = db_connector.connect()
    cursor = conn.cursor()
    return exec_status

def read_test_list(file_path):
    """
    Read the list of databases or tables to test from a file.
    """
    filename = os.path.join('Input', file_path)
    try:
        with open(filename, mode='r') as f: 
            return json.loads(f.read())["Configuration"]
    except FileNotFoundError:
        print("404: Input File not found")
        sys.exit(1)

def decode_configs(entityjson):
    """
    Get user input for test type, database name if needed, and batch sizes.
    """
    try:
        test_type = int(entityjson["test_type"])
        batch_size = int(entityjson["batch_size"]) if entityjson["batch_size"] else entityjson["batch_size"]
        if test_type == 1:
            return test_type, None, None, batch_size
        else:
            include_schema = entityjson["include_schema"]
            schema = entityjson["schema"]
            return test_type, include_schema, schema, batch_size
    
    except KeyError:
        print("Please correct the file format")

def save_results(exec_status):
    """
    Save the test results to an Excel file.
    """
    if exec_status:
        df_error_details = pd.DataFrame(exec_status)
        current_time = datetime.datetime.now().strftime("%d-%m-%Y_%H%M%S")
        file_name = f'Output/Entity_Test_Reports/table_with_errors_{current_time}.csv'
        df_error_details.to_csv(file_name, index=False)
        logging.info(f"File saved to {file_name}")
    else:
        logging.info("No Status information")

def automated_test(db_connector, entityjson):
    """
    Main function to perform automated testing of databases or tables.
    """
    conn = db_connector.connect()
    cursor = conn.cursor()

    try:
        test_list = entityjson["entities"]
        logging.info(f"Found {len(test_list)} items from the file")

        test_type, include_schema, schema, batch_size = decode_configs(entityjson)

        exec_status = []
        if test_type == 1:
            for schema in test_list:
                db_type = db_connector.get_db_type()
                database = db_connector.get_database()
                
                # Retrieve tables
                tables = get_table_list(cursor, db_type, database, schema)
                batch_size = batch_size if batch_size else len(tables)
                for i in range(0, len(tables), batch_size):
                    batch = tables[i:i+batch_size]
                    exec_status += test_tables(batch, cursor, True, schema, db_connector)

        else:
            batch_size = batch_size if batch_size else len(test_list)
            for i in range(0, len(test_list), batch_size):
                batch = test_list[i:i+batch_size]
                exec_status += test_tables(batch, cursor, include_schema, schema, db_connector)

        save_results(exec_status)

    except Exception as e:
        logging.error(f"Error during automated_test execution: {str(e)}")
        traceback.print_exc() 
    finally:
        cursor.close()
        db_connector.close_connection()

if __name__ == '__main__':
    entityjson = read_test_list('entity_list.json')
    db_choice = int(entityjson["database"])

    db_connector = DatabaseConnector()
    db_connector.fetch_db_type(db_choice)
    automated_test(db_connector, entityjson)
    