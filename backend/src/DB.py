"""This is the file for the user-credential database (sqlite)"""
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
    sql_query2 = """INSERT INTO Session (Session_ID, username) VALUES (?, ?);"""
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
            except sqlite3.Error as error:
                print("Error creating session id:", error)
                
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
        ## skapade en till tabell för att randomiza session id med användarenamn
        conn.execute('''
        CREATE TABLE Session (
            Session_ID TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES user(Username)
        );
        ''')

        conn.commit()
        print("User table created successfully")
    except sqlite3.OperationalError as e:
        print("Error creating user table:", e)
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


## funktion för att mapa en session id till en användare, detta används när man vill ha tilbbaka användarnamnet
def map_session_id_to_user(session_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT username FROM Session WHERE Session_ID = ?;
        ''', (session_id,))
        username = cursor.fetchone()
        return username[0]
    except sqlite3.Error as e:
        print("Error mapping session id to user:", e)
        return None
    finally:
        conn.close()

## funktion för att mapa användare till session id, detta används när man vill ha tillbaka session id
def map_user_to_session_id(username):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT Session_ID FROM Session WHERE username = ?;
        ''', (username,))
        session_id = cursor.fetchone()
        return session_id[0]
    except sqlite3.Error as e:
        print("Error mapping user to session id:", e)
        return None
    finally:
        conn.close


## funktion för att skapa 32 tecken+siffror lång session id
def generate_session_id():
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
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

## funktion för att ta bort användarens namn 