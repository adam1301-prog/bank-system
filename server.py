# server.py
import time, datetime
from flask import Flask, request, jsonify
import csv

def load_users():
    users = {}
    with open('users.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users[row['username']] = {
                'password': row['password'],
                'balance': float(row['balance'])
            }
    return users

users = load_users()

def save_users():
    with open('users.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'password', 'balance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for username, data in users.items():
            writer.writerow({
                'username': username,
                'password': data['password'],
                'balance': data['balance']
            })

def print_balance(user):
    if user in users:
        print(users[user]["balance"])
    else:
        print(f"Brak użytkownika o nazwie: {user}")

def deposit(username, amount):
    if username in users:
        if amount > 0:
            users[username]['balance'] += amount
            save_users()
            print(f"Wpłacono {amount} na konto {username}. Nowy stan: {users[username]['balance']}")
        else:
            print("Kwota musi być większa niż 0")
    else:
        print(f"Użytkownik {username} nie istnieje")


def withdraw(username, amount):
    if username in users:
        if amount > 0:
            if users[username]['balance'] >= amount:
                users[username]['balance'] -= amount
                save_users()
                print(f"Wypłacono {amount} z konta {username}. Nowy stan: {users[username]['balance']}")
            else:
                print("Niewystarczające środki")
        else:
            print("Kwota musi być większa niż 0")
    else:
        print(f"Użytkownik {username} nie istnieje")

print_balance("adam")

app = Flask(__name__)

@app.route('/')
def home():
    return "Serwer działa!2 👋"



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username]["password"] == password:
        return jsonify({"status": "success", "message": f"Zalogowano jako {username}"})
    else:
        return jsonify({"status": "error", "message": "Błędna nazwa użytkownika lub hasło"}), 401

def special_login():
    pass
    #TODO: Zastąpić to logowaniem administratora by nie korzystał z normalnego.

@app.route('/balance', methods=['POST'])
def balance():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username]["password"] == password:
        return jsonify({"balance": users[username]["balance"]})
    else:
        return jsonify({"status": "error", "message": "Nieautoryzowany dostęp"}), 401


@app.route("/users", methods=["POST"])
def check_users():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username]["password"] == password:
        to_return = ""
        for user, info in users.items():
            line = f"{user.ljust(16, "_")}{info["balance"]}\n"
            to_return += line
        return jsonify({"status": "success", "list": to_return})
    else:
        return jsonify({"status": "error", "message": "Nieautoryzowany dostęp"}), 401


@app.route('/deposit', methods=['POST'])
def deposit_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    amount = data.get("amount")

    if username in users and users[username]["password"] == password:
        if amount > 0:
            users[username]["balance"] += amount
            save_users()
            return jsonify({"status": "success", "message": f"Wpłacono {amount} zł\nDostępne środki: {users[username]["balance"]}"})
        else:
            return jsonify({"status": "error", "message": "Kwota musi być większa niż 0"}), 400
    else:
        return jsonify({"status": "error", "message": "Nieautoryzowany dostęp"}), 401

@app.route("/special_deposit", methods=["POST"])
def special_deposit_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    amount = data.get("amount")
    username2 = data.get("username2")

    if username in users and users[username]["password"] == password:
        if amount > 0:
            users[username2]["balance"] += amount
            save_users()
            return jsonify({"status": "success", "message": f"Wpłacono {amount} zł\nDostępne środki klienta: {users[username2]["balance"]}"})
        else:
            return jsonify({"status": "error", "message": "Kwota musi być większa niż 0"}), 400
    else:
        return jsonify({"status": "error", "message": "Nieautoryzowany dostęp"}), 401


@app.route('/withdraw', methods=['POST'])
def withdraw_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    amount = data.get("amount")

    if username in users and users[username]["password"] == password:
        if amount > 0:
            if users[username]["balance"] >= amount:
                users[username]["balance"] -= amount
                save_users()
                return jsonify({"status": "success", "message": f"Wypłacono {amount} zł\nDostępne środki: {users[username]["balance"]}"})
            else:
                return jsonify({"status": "error", "message": "Niewystarczające środki"}), 400
        else:
            return jsonify({"status": "error", "message": "Kwota musi być większa niż 0"}), 400
    else:
        return jsonify({"status": "error", "message": "Nieautoryzowany dostęp"}), 401

@app.route("/special_withdraw", methods=["POST"])
def special_withdraw_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    amount = data.get("amount")
    username2 = data.get("username2")

    if username in users and users[username]["password"] == password:
        if amount > 0:
            if users[username2]["balance"] >= amount:
                users[username2]["balance"] -= amount
                save_users()
                return jsonify({"status": "success",
                                "message": f"Wypłacono {amount} zł\nDostępne środki: {users[username2]["balance"]}"})
            else:
                return jsonify({"status": "error", "message": "Niewystarczające środki"}), 400
        else:
            return jsonify({"status": "error", "message": "Kwota musi być większa niż 0"}), 400
    else:
        return jsonify({"status": "error", "message": "Nieautoryzowany dostęp"}), 401

@app.route("/transfer", methods=["POST"])
def transfer_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    amount = data.get("amount")
    from_ = data.get("from_")
    to = data.get("to")

    if username in users and users[username]["password"] == password:
        if amount > 0:
            if users[from_]["balance"] >= amount:
                users[from_]["balance"] -= amount
                users[to]["balance"] += amount
                save_users()
                return jsonify({"status": "success",
                                "message": f"Wykonano przelew na {amount} zł, z konta użytkownika {from_} na {to}\nDostępne środki (odpowiednio): {users[from_]["balance"]} i {users[to]["balance"]}"})
            else:
                return jsonify({"status": "error", "message": "Niewystarczające środki"}), 400

        else:
            return jsonify({"status": "error", "message": "Kwota musi być większa niż 0"}), 400
    else:
        return jsonify({"status": "error", "message": "Nieautoryzowany dostęp"}), 401

def going_on():
    print("Serwer uruchomiony!")
    while True:
        time.sleep(120)
        print(f"Program działa!\nStan na: {datetime.now()}\n")

if __name__ == '__main__':
    print("Serwer uruchomiony!")   #TODO: Zastąpić to funkcją going_on() i zrobić coś by nie blokowała programu
    app.run(host='0.0.0.0', port=5000, debug=True)
