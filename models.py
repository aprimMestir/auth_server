import jwt
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(user='app_user', password='P@$$w0rd',
                              host='localhost',
                              database='auth_server')
        self.cursor = self.connection.cursor()

    def add_user(self, username, password):
        password_hash = generate_password_hash(password)
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    def get_user(self, username):
        self.cursor.execute("SELECT username, password_hash FROM users WHERE username = %s", (username,))
        result = self.cursor.fetchone()
        if result:
            return {"username": result[0], "password_hash": result[1]}
        return None

    def close(self):
        self.cursor.close()
        self.connection.close()


class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, secret_key, expires_in=3600):
        payload = {
            'username': self.username,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def verify_token(token, secret_key):
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload['username']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None