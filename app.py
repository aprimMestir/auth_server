from flask import Flask, request, jsonify
from models import Database, User
import jwt
from datetime import datetime, timedelta, timezone

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
        return jsonify({'error': 'Username and password are required'}), 400

    if db.add_user(username, password):
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'Username already exists'}), 400

# Маршрут для входа
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user_data = db.get_user(username)
    if user_data:
        user = User(user_data['username'], user_data['password_hash'])
        if user.check_password(password):
            token = user.generate_token(app.config['SECRET_KEY'])
            return jsonify({'message': 'Login successful', 'token': token}), 200

    return jsonify({'error': 'Invalid username or password'}), 401

# Маршрут для создания персонажа
@app.route('/create_character', methods=['POST'])
def create_character():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')

    if not user_id or not name:
        return jsonify({'error': 'User ID and character name are required'}), 400

    if db.create_character(user_id, name):
        return jsonify({'message': 'Character created successfully'}), 201
    else:
        return jsonify({'error': 'Failed to create character'}), 500

# Маршрут для получения данных персонажа
@app.route('/get_character', methods=['GET'])
def get_character():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    character = db.get_character(user_id)
    if character:
        return jsonify(character), 200
    else:
        return jsonify({'error': 'Character not found'}), 404

# Маршрут для обновления данных персонажа
@app.route('/update_character', methods=['POST'])
def update_character():
    data = request.json
    character_id = data.get('character_id')
    updates = data.get('updates', {})

    if not character_id:
        return jsonify({'error': 'Character ID is required'}), 400

    if db.update_character(character_id, **updates):
        return jsonify({'message': 'Character updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update character'}), 500

if __name__ == '__main__':
    app.run(debug=True)