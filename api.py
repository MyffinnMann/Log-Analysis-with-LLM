from flask import Flask, request, jsonify
from flask_cors import CORS  # Lägg till denna rad

app = Flask(__name__)
CORS(app)  # Aktivera CORS för hela appen

# Simulerad databas av användare (för demoändamål)
users = {
    "user1": "p",
    "user2": "securepassword",
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f"Data mottagen från frontend: {data}")  # Debug

    username = data.get('username')
    password = data.get('password')

    print(f"Kontrollerar användarnamn: {username} och lösenord: {password}")  # Debug

    # Kontrollera om användarnamn och lösenord matchar
    if username in users and users[username] == password:
        print("Inloggning lyckades!")  # Debug
        return jsonify({"success": True}), 200
    else:
        print("Inloggning misslyckades!")  # Debug
        return jsonify({"success": False}), 401

if __name__ == '__main__':
    app.run(debug=True)
