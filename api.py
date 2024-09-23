from flask import Flask, request, jsonify
from flask_cors import CORS  # Lägg till denna rad
import sql

api = Flask(__name__)
CORS(api)  # Aktivera CORS för hela appen

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f"Data mottagen från frontend: {data}")  # Debug

    username = data.get('username')
    password = data.get('password')

    print(f"Kontrollerar användarnamn: {username} och lösenord: {password}")  # Debug
    Bo_value = sql.check_login(username, password)
    # Kontrollera om användarnamn och lösenord matchar
    if Bo_value == True:
        print("Inloggning lyckades!")  # Debug
        return jsonify({"success": True}), 200
    else:
        print("Inloggning misslyckades!")  # Debug
        return jsonify({"success": False}), 401

if __name__ == '__main__':
    #FIXA TILL FÖR HTTPS SENARE api.run(debug=True, ssl_context=('Z:/SKOLA/Säkerhets Projekt/UI_design/cert/server.pfx', 'SecureLangsss'))
    api.run(debug=True)