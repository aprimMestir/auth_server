import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import re
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Логи в файл
        logging.StreamHandler()  # Логи в консоль
    ]
)

def validate_character_name(name):
    """
    Проверяет, соответствует ли имя персонажа правилам.
    :param name: Имя персонажа.
    :return: True, если имя валидно, иначе False.
    """
    if not name:
        return False  # Имя не может быть пустым
    if len(name) < 3 or len(name) > 50:
        return False  # Имя должно быть от 3 до 50 символов
    if not re.match(r'^[a-zA-Z0-9\s]+$', name):
        return False  # Имя может содержать только буквы, цифры и пробелы
    return True

class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="app_user",  # Имя пользователя
                password="secure_password",  # Пароль пользователя
                database="auth_server"  # Имя базы данных
            )
            self.cursor = self.connection.cursor()
            logging.info("Подключение к базе данных успешно установлено.")
        except mysql.connector.Error as err:
            logging.error(f"Ошибка подключения к базе данных: {err}")
            raise

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
            logging.error(f"Ошибка при добавлении пользователя {username}: {err}")
            return False

    def get_user(self, username):
        self.cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        result = self.cursor.fetchone()
        if result:
            return {"id": result[0], "username": result[1], "password_hash": result[2]}
        return None

    def is_character_name_unique(self, name):
        """
        Проверяет, уникально ли имя персонажа.
        :param name: Имя персонажа.
        :return: True, если имя уникально, иначе False.
        """
        self.cursor.execute("SELECT id FROM characters WHERE name = %s", (name,))
        result = self.cursor.fetchone()
        return result is None

    def create_character(self, user_id, name, level=1, health=100, mana=50, strength=10, agility=10, intelligence=10):
        if not validate_character_name(name):
            logging.warning(f"Невалидное имя персонажа: {name}")
            return False  # Имя не прошло валидацию

        if not self.is_character_name_unique(name):
            logging.warning(f"Имя персонажа уже занято: {name}")
            return False  # Имя уже занято

        try:
            self.cursor.execute(
                "INSERT INTO characters (user_id, name, level, health, mana, strength, agility, intelligence) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, name, level, health, mana, strength, agility, intelligence)
            )
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при создании персонажа {name}: {err}")
            return False

    def get_character(self, user_id):
        self.cursor.execute("SELECT * FROM characters WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "user_id": result[1],
                "name": result[2],
                "level": result[3],
                "health": result[4],
                "mana": result[5],
                "strength": result[6],
                "agility": result[7],
                "intelligence": result[8]
            }
        return None

    def update_character(self, character_id, name=None, level=None, health=None, mana=None, strength=None, agility=None, intelligence=None):
        try:
            updates = []
            params = []
            if name is not None:
                if not validate_character_name(name):
                    logging.warning(f"Невалидное имя персонажа: {name}")
                    return False  # Имя не прошло валидацию
                if not self.is_character_name_unique(name):
                    logging.warning(f"Имя персонажа уже занято: {name}")
                    return False  # Имя уже занято
                updates.append("name = %s")
                params.append(name)
            if level is not None:
                updates.append("level = %s")
                params.append(level)
            if health is not None:
                updates.append("health = %s")
                params.append(health)
            if mana is not None:
                updates.append("mana = %s")
                params.append(mana)
            if strength is not None:
                updates.append("strength = %s")
                params.append(strength)
            if agility is not None:
                updates.append("agility = %s")
                params.append(agility)
            if intelligence is not None:
                updates.append("intelligence = %s")
                params.append(intelligence)

            if updates:
                query = f"UPDATE characters SET {', '.join(updates)} WHERE id = %s"
                params.append(character_id)
                self.cursor.execute(query, tuple(params))
                self.connection.commit()
                return True
            return False
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при обновлении персонажа {character_id}: {err}")
            return False

    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            logging.info("Подключение к базе данных закрыто.")