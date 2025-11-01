import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',          # XAMPP default
            password='',          # set your MySQL password if any
            database='hackathon_mvp'
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
