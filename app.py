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

# Маршрут для регистрации
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logging.warning("Попытка регистрации без имени пользователя или пароля")
        return jsonify({'error': 'Username and password are required'}), 400

    if db.add_user(username, password):
        logging.info(f"Пользователь {username} успешно зарегистрирован")
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        logging.error(f"Ошибка при регистрации пользователя {username}")
        return jsonify({'error': 'Username already exists'}), 400

# Маршрут для входа
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logging.warning("Попытка входа без имени пользователя или пароля")
        return jsonify({'error': 'Username and password are required'}), 400

    user_data = db.get_user(username)
    if user_data:
        user = User(user_data['username'], user_data['password_hash'])
        if user.check_password(password):
            token = user.generate_token(app.config['SECRET_KEY'])
            logging.info(f"Пользователь {username} успешно вошел в систему")
            return jsonify({'message': 'Login successful', 'token': token}), 200

    logging.warning(f"Неудачная попытка входа для пользователя {username}")
    return jsonify({'error': 'Invalid username or password'}), 401

# Маршрут для создания персонажа
@app.route('/create_character', methods=['POST'])
def create_character():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')

    if not user_id or not name:
        logging.warning("Попытка создания персонажа без user_id или имени")
        return jsonify({'error': 'User ID and character name are required'}), 400

    if db.create_character(user_id, name):
        logging.info(f"Персонаж {name} успешно создан для пользователя {user_id}")
        return jsonify({'message': 'Character created successfully'}), 201
    else:
        logging.error(f"Ошибка при создании персонажа {name} для пользователя {user_id}")
        return jsonify({'error': 'Failed to create character. Invalid name or name already taken.'}), 400

# Маршрут для получения данных персонажа
@app.route('/get_character', methods=['GET'])
def get_character():
    user_id = request.args.get('user_id')
    if not user_id:
        logging.warning("Попытка получения персонажа без user_id")
        return jsonify({'error': 'User ID is required'}), 400

    character = db.get_character(user_id)
    if character:
        logging.info(f"Данные персонажа для пользователя {user_id} успешно получены")
        return jsonify(character), 200
    else:
        logging.warning(f"Персонаж для пользователя {user_id} не найден")
        return jsonify({'error': 'Character not found'}), 404

# Маршрут для обновления данных персонажа
@app.route('/update_character', methods=['POST'])
def update_character():
    data = request.json
    character_id = data.get('character_id')
    updates = data.get('updates', {})

    if not character_id:
        logging.warning("Попытка обновления персонажа без character_id")
        return jsonify({'error': 'Character ID is required'}), 400

    if db.update_character(character_id, **updates):
        logging.info(f"Персонаж {character_id} успешно обновлен")
        return jsonify({'message': 'Character updated successfully'}), 200
    else:
        logging.error(f"Ошибка при обновлении персонажа {character_id}")
        return jsonify({'error': 'Failed to update character. Invalid name or name already taken.'}), 400

if __name__ == '__main__':
    logging.info("Сервер запущен")
    app.run(debug=True)