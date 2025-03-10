import jwt
from datetime import datetime, timedelta

class User:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, secret_key, expires_in=3600):
        # Генерация JWT-токена
        payload = {
            'username': self.username,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def verify_token(token, secret_key):
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload['username']
        except jwt.ExpiredSignatureError:
            return None  # Токен истек
        except jwt.InvalidTokenError:
            return None  # Невалидный токен


class Database:
    def __init__(self):
        self.users = {}

    def add_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = User(username, password)
        return True

    def get_user(self, username):
        return self.users.get(username)