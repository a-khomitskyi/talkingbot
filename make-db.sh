#!/bin/bash
# Get the current directory
current_dir=$(pwd)
# Use the Python interpreter from the current directory
python_path="$current_dir/env/bin/python"

$python_path << END
import sqlite3
from datetime import datetime

# Database connection function
def db_connection(dbname: str) -> sqlite3.Connection:
    conn = sqlite3.connect(dbname)
    return conn

# Function to create users table
def make_table_users(db_obj: sqlite3.Connection) -> bool:
    try:
        cursor = db_obj.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY NOT NULL,
            nick TEXT NOT NULL,
            is_blocked INTEGER NOT NULL,
            joined TEXT NOT NULL)"""
        )
        db_obj.commit()
        print("Table 'users' has created successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        return False
    finally:
        cursor.close()

# Function to create messages table
def make_table_messages(db_obj: sqlite3.Connection) -> bool:
    try:
        cursor = db_obj.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS messages (
            original_id INTEGER PRIMARY KEY,
            bot_id INTEGER NOT NULL,
            sender INTEGER NOT NULL,
            receiver INTEGER NOT NULL)"""
        )
        db_obj.commit()
        print("Table 'messages' has created successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        return False
    finally:
        cursor.close()

# Database name
dbname = 'bot.db'

# Create tables
make_table_users(conn)
make_table_messages(conn)
END
