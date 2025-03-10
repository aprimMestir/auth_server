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
        logging.FileHandler("app.log"),  # Логи в файл
        logging.StreamHandler()  # Логи в консоль
    ]
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = Database()

def log_with_ip(message, level=logging.INFO):
    """
    Добавляет IP-адрес пользователя в лог.
    :param message: Сообщение для лога.
    :param level: Уровень логирования (по умолчанию INFO).
    """
    ip_address = request.remote_addr
    log_message = f"{message} [IP: {ip_address}]"
    logging.log(level, log_message)

# Маршрут для регистрации
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        log_with_ip("Попытка регистрации без имени пользователя или пароля", logging.WARNING)
        return jsonify({'error': 'Username and password are required'}), 400

    if db.add_user(username, password):
        log_with_ip(f"Пользователь {username} успешно зарегистрирован")
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        log_with_ip(f"Ошибка при регистрации пользователя {username}", logging.ERROR)
        return jsonify({'error': 'Username already exists'}), 400

# Маршрут для входа
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        log_with_ip("Попытка входа без имени пользователя или пароля", logging.WARNING)
        return jsonify({'error': 'Username and password are required'}), 400

    user_data = db.get_user(username)
    if user_data:
        user = User(user_data['username'], user_data['password_hash'])
        if user.check_password(password):
            token = user.generate_token(app.config['SECRET_KEY'])
            log_with_ip(f"Пользователь {username} успешно вошел в систему")
            return jsonify({'message': 'Login successful', 'token': token}), 200

    log_with_ip(f"Неудачная попытка входа для пользователя {username}", logging.WARNING)
    return jsonify({'error': 'Invalid username or password'}), 401

# Маршрут для создания персонажа
@app.route('/create_character', methods=['POST'])
def create_character():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    class_name = data.get('class')
    race = data.get('race')

    if not user_id or not name or not class_name or not race:
        log_with_ip("Попытка создания персонажа без обязательных данных", logging.WARNING)
        return jsonify({'error': 'User ID, name, class, and race are required'}), 400

    if db.create_character(user_id, name, class_name, race):
        log_with_ip(f"Персонаж {name} успешно создан для пользователя {user_id}")
        return jsonify({'message': 'Character created successfully'}), 201
    else:
        log_with_ip(f"Ошибка при создании персонажа {name} для пользователя {user_id}", logging.ERROR)
        return jsonify({'error': 'Failed to create character. Invalid name or name already taken.'}), 400

# Маршрут для получения данных персонажа
@app.route('/get_character', methods=['GET'])
def get_character():
    user_id = request.args.get('user_id')
    if not user_id:
        log_with_ip("Попытка получения персонажа без user_id", logging.WARNING)
        return jsonify({'error': 'User ID is required'}), 400

    character = db.get_character(user_id)
    if character:
        log_with_ip(f"Данные персонажа для пользователя {user_id} успешно получены")
        return jsonify(character), 200
    else:
        log_with_ip(f"Персонаж для пользователя {user_id} не найден", logging.WARNING)
        return jsonify({'error': 'Character not found'}), 404

# Маршрут для обновления данных персонажа
@app.route('/update_character', methods=['POST'])
def update_character():
    data = request.json
    character_id = data.get('character_id')
    updates = data.get('updates', {})

    if not character_id:
        log_with_ip("Попытка обновления персонажа без character_id", logging.WARNING)
        return jsonify({'error': 'Character ID is required'}), 400

    if db.update_character(character_id, **updates):
        log_with_ip(f"Персонаж {character_id} успешно обновлен")
        return jsonify({'message': 'Character updated successfully'}), 200
    else:
        log_with_ip(f"Ошибка при обновлении персонажа {character_id}", logging.ERROR)
        return jsonify({'error': 'Failed to update character. Invalid name or name already taken.'}), 400

if __name__ == '__main__':
    logging.info("Сервер запущен")
    app.run(debug=True)