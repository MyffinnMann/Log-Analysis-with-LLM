"""This is the file for the user-credential database (sqlite)"""
import sqlite3
from argon2 import PasswordHasher
ph = PasswordHasher()

def connect():
    try:
        db = sqlite3.connect('backend/db/securelang.db')
        print("Anslutning till SQLite-databasen lyckades.")
        return db
    except sqlite3.Error as error:
        print("Kunde inte ansluta till databasen:", error)

def hash_pas(passwor):
    return ph.hash(passwor)

def verify_pas(stored_pas, given_pas):
    try:
        return ph.verify(stored_pas, given_pas)
    except:
        return False

def check_login(username, pas):
    db = connect()
    cursor = db.cursor()
    sql_query = """SELECT Hash_PWD FROM Password
                    WHERE user_ID = (SELECT ID FROM user WHERE Username = ?)"""
    try:
        cursor.execute(sql_query, (username,))
        stored_pas = cursor.fetchone()
        Bo_value = verify_pas(stored_pas[0], pas)
    except:
        return False
    return Bo_value

def create_tables():
    try:
        conn = connect()
        conn.execute('''
        CREATE TABLE user (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE
        );
        ''')
        conn.execute('''
        CREATE TABLE Password (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Hash_PWD TEXT NOT NULL,
            user_ID INTEGER,
            FOREIGN KEY(user_ID) REFERENCES user(ID)
        );
        ''')

        conn.commit()
        print("User table created successfully")
    except:
        print("User table already exists")
    finally:
        conn.close()

def insert_test_values(username, password):
    try:
        conn = connect()

        # kolla om användar namn redan finns
        result = conn.execute('SELECT ID FROM user WHERE Username = ?', (username,))
        if result.fetchone() is not None:
            print(f"Username '{username}' already exists.")
            return

        # Insert the username
        conn.execute('INSERT INTO user (Username) VALUES (?);', (username,))
        user_id = conn.execute('SELECT last_insert_rowid();').fetchone()[0]  # user_id av sista insertad användar namn

        # Hash lösenordet och insert
        hash = ph.hash(password)
        conn.execute('INSERT INTO Password (Hash_PWD, user_ID) VALUES (?, ?);', (hash, user_id))

        conn.commit()
        print(f"User '{username}' inserted successfully.")

    except Exception as e:
        print(f"Error inserting user '{username}': {e}")
    finally:
        conn.close()

def get_all_answer(username, token):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT Question, ans FROM Question_Answers WHERE user_ID = (SELECT ID FROM user WHERE Username = ?);
        ''', (username,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        print("error fetching answers")
    finally:
        conn.close()

def get_all_files(username):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT file_name, file_hash FROM Files WHERE user_ID = (SELECT ID FROM user WHERE Username = ?);
        ''', (username,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        print("error fetching files")
    finally:
        conn.close()
