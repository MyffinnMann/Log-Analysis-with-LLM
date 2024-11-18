
import sqlite3
from argon2 import PasswordHasher
import random
import string

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
    sql_query2 = """INSERT INTO Session (Session_ID, user_ID) VALUES (?, (SELECT ID FROM user WHERE Username = ?))"""
    try:
        cursor.execute(sql_query, (username,))
        stored_pas = cursor.fetchone()
        Bo_value = verify_pas(stored_pas[0], pas)
        ## skapa session id om inloggningen lyckas
        if Bo_value:
            try:
                session_id = generate_session_id()
                cursor.execute(sql_query2, (session_id, username))
                db.commit()
            except:
                print("Error inserting session id")
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
        ## skapade en till tabell för att randomiza session id
        conn.execute('''
        CREATE TABLE Session (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Session_ID TEXT NOT NULL,
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
    

## funktion för att mapa en session id till en användare
def map_session_id_to_user(session_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT user_ID FROM Session WHERE Session_ID = ?;
        ''', (session_id,))
        user_id = cursor.fetchone()
        return user_id[0]
    except:
        print("Error mapping session id to user")
    finally:
        conn.close()

## funktion för att skapa 16 tecken+siffror lång session id
def generate_session_id():
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return session_id

## ta bort session id från databasen
def remove_session_id(session_phrase):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM Session WHERE session_ID = ?;
        ''', (session_phrase,))
        conn.commit()
    except:
        print("Error removing session id")
    finally:
        conn.close()
        