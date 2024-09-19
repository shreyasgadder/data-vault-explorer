import jaydebeapi
import cx_Oracle
import snowflake.connector
import sqlite3
import psycopg2
import pymysql
import json 
import sys
import os


class DatabaseConnector:
    def __init__(self):
        self.conn = None
        self.secrets = None
        self.db_type = None

    def get_db_type(self):
        return self.db_type
    
    def get_database(self):
        return self.secrets['database']

    def read_secret(self):
        filename = os.path.join('Utils', 'secrets.json')
        try:
            with open(filename, mode='r') as f: 
                return json.loads(f.read())
        except FileNotFoundError:
            print("404: Secrets File not found")
            sys.exit(1)

    def fetch_db_type(self, choice=None):        
        db_types = {
            1: "Hive",
            2: "Impala",
            3: "Oracle",
            4: "PostgreSQL",
            5: "Snowflake",
            6: "MySQL"
        }
        if choice is not None:
            self.db_type = db_types[int(choice)]
            self.secrets = self.read_secret()[self.db_type.lower()]
        else:
            print("Which Database?")
            while True:
                for key, value in db_types.items():
                    print(f" {key}. {value}")
                choice = input("Enter your choice: ")
                if choice.isdigit() and int(choice) in db_types:
                    self.db_type = db_types[int(choice)]
                    self.secrets = self.read_secret()[self.db_type.lower()]
                    break
                else:
                    print("Invalid input")

        if self.db_type in ["PostgreSQL", "Snowflake"]:
            self.secrets['database'] = input("Enter your database name:")
        else:
            self.secrets['database'] = None

    def connect(self):
        if self.conn is not None:   
            try:
                self.conn.close()
                print("Closed the existing connection...")
            except Exception as e:
                print(f"Connection error: {str(e)}")

        try:
            if self.db_type in ["Hive", "Impala"]:
                self.conn = jaydebeapi.connect(self.secrets['class'], self.secrets['host'],
                                               [self.secrets['user'], self.secrets['pass']], self.secrets['jar'])
            elif self.db_type == "Oracle":
                self.conn = cx_Oracle.connect(user=self.secrets['user'], password=self.secrets['pass'],
                                              dsn=self.secrets['dsn'])
            elif self.db_type == "PostgreSQL":
                self.conn = psycopg2.connect(host=self.secrets['host'], user=self.secrets['user'],
                                             password=self.secrets['pass'], database=self.secrets['database'])
            elif self.db_type == "Snowflake":
                self.conn = snowflake.connector.connect(account=self.secrets['account'],
                                                        user=self.secrets['user'],
                                                        password=self.secrets['pass'],
                                                        warehouse=self.secrets['warehouse'],
                                                        database=self.secrets['database'])
            elif self.db_type == "MySQL":
                self.conn = pymysql.connect(host=self.secrets['host'], user=self.secrets['user'],
                                            password=self.secrets['pass'])            
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            print(f"Connected to {self.db_type}...")
            return self.conn
        except Exception as e:
            print(f"Failed to connect to {self.db_type}. Error: {str(e)}")
            return None

    def close_connection(self):
        if self.conn is not None:
            try:
                self.conn.close()
                print("Disconnected...")
            except Exception as e:
                print(f"Connection error: {str(e)}")

# def main():
#     db_connector = DatabaseConnector()
#     db_connector.get_db_type()
#     connection = db_connector.connect()
    
#     if connection:
#         # Perform database operations here
#         pass
    
#     db_connector.close_connection()

# if __name__ == "__main__":
#     main()