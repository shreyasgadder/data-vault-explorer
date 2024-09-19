import json
import sys
import pandas as pd
import re
import os
from Utils.DBConnection import DatabaseConnector
import logging
from typing import Dict, List, Tuple, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import re
from typing import Tuple, Optional, List

def extract_columns_and_table(query: str) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Extracts columns and table name from a SQL SELECT query.

    This function handles various SQL functions and aliases:
    1. Simple column names: 'column_name'
    2. Aliased columns: 'column_name AS alias'
    3. Functions without alias: 'FUNCTION(arg1, arg2)' -> 'expN'
    4. Functions with alias: 'FUNCTION(arg1, arg2) AS alias'
    5. Nested functions: 'FUNCTION1(FUNCTION2(arg))'

    Args:
    query (str): The SQL SELECT query.

    Returns:
    Tuple[Optional[List[str]], Optional[str]]: A tuple containing a list of column names (or None) and the table name (or None).
    """
    match = re.match(r'^SELECT\s+(.*?)\s+FROM\s+(\S+)', query, re.IGNORECASE | re.DOTALL)
    if not match:
        return None, None
    
    columns_raw = re.findall(r'(?:[^,()]|\([^)]*\))+', match.group(1))
    columns = []
    exp_count = 0

    for col in columns_raw:
        col = col.strip()
        
        # Check for alias
        alias_match = re.search(r'\s+AS\s+(\w+)\s*$', col, re.IGNORECASE)
        if alias_match:
            columns.append(alias_match.group(1))
        else:
            # Check if it's a function
            if '(' in col:
                # It's a function without an alias
                exp_count += 1
                columns.append(f'exp{exp_count}')
            else:
                # It's a simple column name
                columns.append(col)

    table = match.group(2)
    return columns, table

def get_column_names(table_name: str, cursor) -> List[str]:
    """
    Fetches column names of a given table from a database.

    Args:
    table_name (str): The name of the table.
    cursor: The database cursor.

    Returns:
    List[str]: A list of column names.
    """
    logging.info(f"Fetching column names for table: {table_name}")
    cursor.execute(f"DESCRIBE {table_name}")
    column_header = [x[0] for x in cursor.fetchall()]
    logging.info(f"Fetched column names for table: {table_name}")
    return column_header

def download_file(df: pd.DataFrame, output: str, file_format: int) -> None:
    """
    Downloads a DataFrame to a file in either Excel or CSV format.

    Args:
    df (pd.DataFrame): The DataFrame to download.
    output (str): The name of the output file.
    file_format (int): The format of the output file (1 for Excel, 2 for CSV).
    """
    os.makedirs('Output/TableFileExport', exist_ok=True)
    if file_format == 1:
        file = f'{output}.xlsx'
        filename = os.path.join('Output','TableFileExport',file)
        logging.info(f"Downloading {output} in xlsx format")
        df.to_excel(filename, index=False, engine='xlsxwriter')
    elif file_format == 2:
        file = f'{output}.csv'
        filename = os.path.join('Output','TableFileExport',file)
        logging.info(f"Downloading {output} in csv format")
        df.to_csv(filename, index=False)
    logging.info(f"File saved to {filename}")

def db_to_file(db_table_query, file_format, conn):
    """
    Fetches data from a database and saves it to files in either Excel or CSV format.

    Args:
    db_table_query (Dict[str, Optional[str]]): A dictionary mapping table file names to SQL SELECT queries.
    conn: The database connection.
    """
    logging.info("dbToFile execution started")
    cursor = conn.cursor()

    try:
        if file_format not in [1, 2]:
            raise ValueError("Invalid file format choice")

        for filename, query_cols in db_table_query.items():
            try:
                if len(query_cols) == 1:
                    query = query_cols[0]
                    cols, table = extract_columns_and_table(query)

                elif len(query_cols) == 2:
                    query = query_cols[0]
                    cols = query_cols[1]
                else:
                    raise ValueError("Invalid Input format in export_table.json")    
                    
                cursor.execute(query)
                result = cursor.fetchall()

                header = get_column_names(table, cursor) if cols[0] in ['*', 'DISTINCT *'] else cols

                df = pd.DataFrame(result, columns=header)
                logging.info(f"Data from {table} table fetched successfully.")
                logging.info(f"Sample data:\n{df.head()}")

                download_file(df, filename, file_format)
            except Exception as e:
                logging.error(f"Error processing table {filename}: {str(e)}")

    except ValueError as v:
        logging.error(f"Invalid input: {str(v)}")
    except Exception as e:
        logging.error(f"Error in db_to_file: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        filename = os.path.join('Input', 'export_table.json')
        with open(filename, mode='r') as f: 
            export_table_queries = json.loads(f.read())["Configuration"]

        db_choice = int(export_table_queries["database"])
        fileformat = int(export_table_queries["fileformat"])

        db_connector = DatabaseConnector()
        db_connector.fetch_db_type(db_choice)
        conn = db_connector.connect()

        db_table_query = export_table_queries["queries"]
        db_to_file(db_table_query, fileformat, conn)
    except FileNotFoundError:
            print("404: Input File not found")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")