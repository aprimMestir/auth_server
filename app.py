import logging
from flask import Flask, request, jsonify
from models import Database, User
import jwt
from datetime import datetime, timedelta, timezone

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = Database()


def log_with_ip(message, level=logging.INFO):
    ip_address = request.remote_addr
    log_message = f"{message} [IP: {ip_address}]"
    logging.log(level, log_message)


# Регистрация пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        log_with_ip("Registration attempt without username/password", logging.WARNING)
        return jsonify({'error': 'Username and password required'}), 400

    if db.add_user(username, password):
        log_with_ip(f"User {username} registered")
        return jsonify({'message': 'User created'}), 201
    else:
        log_with_ip(f"Registration failed for {username}", logging.ERROR)
        return jsonify({'error': 'Username exists'}), 400


# Авторизация
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        log_with_ip("Login attempt without credentials", logging.WARNING)
        return jsonify({'error': 'Credentials required'}), 400

    user_data = db.get_user(username)
    if user_data and User(user_data['username'], user_data['password_hash']).check_password(password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)
        }, app.config['SECRET_KEY'])
        log_with_ip(f"User {username} logged in")
        return jsonify({'token': token}), 200

    log_with_ip(f"Failed login for {username}", logging.WARNING)
    return jsonify({'error': 'Invalid credentials'}), 401


# Создание персонажа
@app.route('/character', methods=['POST'])
def create_character():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    class_name = data.get('class')
    race = data.get('race')

    if not all([user_id, name, class_name, race]):
        log_with_ip("Invalid character creation request", logging.WARNING)
        return jsonify({'error': 'Missing parameters'}), 400

    if db.create_character(user_id, name, class_name, race):
        log_with_ip(f"Character {name} created for user {user_id}")
        return jsonify({'message': 'Character created'}), 201
    else:
        log_with_ip(f"Character creation failed for {name}", logging.ERROR)
        return jsonify({'error': 'Invalid name or exists'}), 400


# Управление экипировкой
@app.route('/equip', methods=['POST'])
def equip_item():
    data = request.json
    character_id = data.get('character_id')
    item_id = data.get('item_id')
    slot = data.get('slot')

    if not all([character_id, item_id, slot]):
        log_with_ip("Invalid equip request", logging.WARNING)
        return jsonify({'error': 'Missing parameters'}), 400

    success, message = db.equip_item(character_id, item_id, slot)

    if success:
        log_with_ip(f"Item {item_id} equipped to {slot}")
        return jsonify({'message': message}), 200
    else:
        log_with_ip(f"Equip failed: {message}", logging.WARNING)
        return jsonify({'error': message}), 400


# Получение экипировки
@app.route('/equipment/<int:character_id>', methods=['GET'])
def get_equipment(character_id):
    equipment = db.get_equipment(character_id)
    if equipment is not None:
        log_with_ip(f"Equipment fetched for {character_id}")
        return jsonify(equipment), 200
    else:
        log_with_ip(f"Equipment error for {character_id}", logging.ERROR)
        return jsonify({'error': 'Equipment not found'}), 404


# Управление инвентарём
@app.route('/inventory/add', methods=['POST'])
def add_to_inventory():
    data = request.json
    character_id = data.get('character_id')
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)

    if not all([character_id, item_id]):
        log_with_ip("Invalid inventory add request", logging.WARNING)
        return jsonify({'error': 'Missing parameters'}), 400

    if db.add_item_to_inventory(character_id, item_id, quantity):
        log_with_ip(f"Added {quantity}x{item_id} to inventory")
        return jsonify({'message': 'Items added'}), 200
    else:
        log_with_ip(f"Failed to add {item_id}", logging.ERROR)
        return jsonify({'error': 'Add failed'}), 400


if __name__ == '__main__':
    logging.info("Starting server")
    app.run(host='0.0.0.0', port=5000, debug=True)