
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

def hash_pas(password):
    return ph.hash(password)

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
            Username TEXT NOT NULL
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

def insert_test_values():
    try:
        conn = connect()

        hash = ph.hash("test")
        conn.execute('''
        INSERT INTO user (Username) VALUES ('test_user');
        ''')
        conn.execute('''
        INSERT INTO Password (Hash_PWD, user_ID) VALUES (?, 1);
        ''', (hash,))

        conn.commit()
        print("Test values inserted successfully")

    except:
        print("Test values already exists or error inserting test values")
    finally:
        conn.close()



def get_user_id_DB(username):
    db = connect()
    cursor = db.cursor()
    sql_query = """SELECT ID FROM user WHERE Username = ?"""
    try:
        cursor.execute(sql_query, (username,))
        user_id = cursor.fetchone()[0]
    except:
        return False
    return user_id