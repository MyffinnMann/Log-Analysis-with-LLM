import mysql.connector
from argon2 import PasswordHasher
ph = PasswordHasher()

def connect():
    try:
        #____FÖR DEV DATOR____
        db = mysql.connector.connect(
            host="localhost",            #
            user="root",
            password="!azEDrfTG%",
            database="securelang",
        )
        if db.is_connected():
            print("Anslutning till MySQL-databasen lyckades.")
            return db

    except mysql.connector.Error as error:
        print("Kunde inte ansluta till databasen:", error)

#_______________PASSWORD MANAGMENT_______________
def hash_pas(passwor):      #SPARA ALLA PARAMETRAR i DB DÅ DETTA ANVÄNDS FÖR ATT KUNNA VERIFIERA DÅ SALTET ÄR RANDOM VARJE GÅNG
    return ph.hash(passwor)

def verify_pas(stored_pas, given_pas):      #VERFIERA LÖSENORDET SOM ÄR GIVET MED DET SOM ÄR SPARAT PÅ DB
    try:
        return ph.verify(stored_pas,given_pas)  #Returns true or false
    except:
        return False

#_______LOGIN  
def check_login(username, pas):
    db = connect()
    cursor = db.cursor()
    sql_query = """SELECT pasw FROM users
                    WHERE Username = %s"""
    try:
        cursor.execute(sql_query, (username,))  #Fetch the stored hash and key values from the stored password. 
        stored_pas = cursor.fetchone()
        #print(stored_pas[0])
        Bo_value = verify_pas(stored_pas[0], pas)  #Check the password and return true or false
    except:
        pass

    return Bo_value
