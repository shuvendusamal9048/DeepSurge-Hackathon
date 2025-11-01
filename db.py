import mysql.connector
from mysql.connector import Error
import pandas as pd

# ------------------ Database connection ------------------
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',          # your XAMPP MySQL username
        password='',          # your XAMPP MySQL password
        database='hackathon_mvp'
    )

# ------------------ Admin Management ------------------
def create_admin(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
    except Error as e:
        print(f"Error creating admin: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def validate_admin(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Error validating admin: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ------------------ File Info ------------------
def save_file_info(filename, uploaded_by):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO file_info (filename, uploaded_by) VALUES (%s, %s)", (filename, uploaded_by))
        conn.commit()
    except Error as e:
        print(f"Error saving file info: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_user_files(username):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT filename, uploaded_at FROM file_info WHERE uploaded_by=%s ORDER BY uploaded_at DESC", (username,))
        rows = cursor.fetchall()
        return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["filename", "uploaded_at"])
    except Error as e:
        print(f"Error fetching user files: {e}")
        return pd.DataFrame(columns=["filename", "uploaded_at"])
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()