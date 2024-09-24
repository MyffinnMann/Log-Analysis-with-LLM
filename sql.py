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
    Bo_value = False # inicialicera den med false för att om den inte hamnar i try: den försöker returnera den ändå i slutet av funktionen
                    # och man för error att man använder en variable utan att declarera den först.
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

############################################
# den här funktionen är för att lägga till en test användare
# så man kan testa login sidan senare
# den kan användas för att bygga sign up sidan kanske
def insert_user(username, password):
    db = connect()
    cursor = db.cursor()

    # hash lösenordet
    hashed_password = hash_pas(password)

    sql_query = "INSERT INTO users (Username, pasw) VALUES (%s, %s)"
    values = (username, hashed_password)

    try:
        cursor.execute(sql_query, values)
        db.commit() # commit ändring till db
        print(f"User {username} inserted successfully.")
    except mysql.connector.Error as error:
        print("Error inserting user:", error)
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    # lägga till en användare för att testa login sidan
    test_username = "user2"
    test_password = "password2"

    insert_user(test_username, test_password)
################################################