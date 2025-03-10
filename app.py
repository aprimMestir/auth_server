from flask import Flask, request, jsonify
from models import Database, User
import jwt
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = Database()

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

@app.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is required'}), 400

    username = User.verify_token(token, app.config['SECRET_KEY'])
    if not username:
        return jsonify({'error': 'Invalid or expired token'}), 401

    return jsonify({'message': 'Logout successful'}), 200

@app.route('/check_auth', methods=['GET'])
def check_auth():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is required'}), 400

    username = User.verify_token(token, app.config['SECRET_KEY'])
    if username:
        return jsonify({'message': f'User {username} is authenticated'}), 200
    else:
        return jsonify({'error': 'Invalid or expired token'}), 401

if __name__ == '__main__':
    app.run(debug=True)