import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import re
import logging
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

class User:
    """
    Класс для работы с пользователями.
    """
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        """
        Проверяет, совпадает ли пароль с хэшем.
        :param password: Пароль для проверки.
        :return: True, если пароль верный, иначе False.
        """
        return check_password_hash(self.password_hash, password)

    def generate_token(self, secret_key, expires_in=3600):
        """
        Генерирует JWT-токен для пользователя.
        :param secret_key: Секретный ключ для подписи токена.
        :param expires_in: Время жизни токена в секундах.
        :return: JWT-токен.
        """
        payload = {
            'username': self.username,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')

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

    def add_user(self, username, password, ip_address=None):
        password_hash = generate_password_hash(password)
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            self.connection.commit()
            if ip_address:
                logging.info(f"Пользователь {username} успешно зарегистрирован [IP: {ip_address}]")
            else:
                logging.info(f"Пользователь {username} успешно зарегистрирован")
            return True
        except mysql.connector.Error as err:
            if ip_address:
                logging.error(f"Ошибка при регистрации пользователя {username} [IP: {ip_address}]: {err}")
            else:
                logging.error(f"Ошибка при регистрации пользователя {username}: {err}")
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

    def create_character(self, user_id, name, class_name, race, level=1, health=100, mana=50, strength=10, agility=10, intelligence=10, xp=0, gold=0):
        if not validate_character_name(name):
            logging.warning(f"Невалидное имя персонажа: {name}")
            return False  # Имя не прошло валидацию

        if not self.is_character_name_unique(name):
            logging.warning(f"Имя персонажа уже занято: {name}")
            return False  # Имя уже занято

        try:
            self.cursor.execute(
                "INSERT INTO characters (user_id, name, class, race, level, health, mana, strength, agility, intelligence, xp, gold) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, name, class_name, race, level, health, mana, strength, agility, intelligence, xp, gold)
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
                "class": result[3],
                "race": result[4],
                "level": result[5],
                "health": result[6],
                "mana": result[7],
                "strength": result[8],
                "agility": result[9],
                "intelligence": result[10],
                "xp": result[11],
                "gold": result[12]
            }
        return None

    def update_character(self, character_id, name=None, class_name=None, race=None, level=None, health=None, mana=None, strength=None, agility=None, intelligence=None, xp=None, gold=None):
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
            if class_name is not None:
                updates.append("class = %s")
                params.append(class_name)
            if race is not None:
                updates.append("race = %s")
                params.append(race)
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
            if xp is not None:
                updates.append("xp = %s")
                params.append(xp)
            if gold is not None:
                updates.append("gold = %s")
                params.append(gold)

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

    def add_item(self, name, description, item_type, weight=0, value=0):
        try:
            self.cursor.execute(
                "INSERT INTO items (name, description, type, weight, value) VALUES (%s, %s, %s, %s, %s)",
                (name, description, item_type, weight, value)
            )
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при добавлении предмета {name}: {err}")
            return False

    def get_item(self, item_id):
        self.cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "name": result[1],
                "description": result[2],
                "type": result[3],
                "weight": result[4],
                "value": result[5]
            }
        return None

    def add_item_to_inventory(self, character_id, item_id, quantity=1):
        try:
            self.cursor.execute(
                "INSERT INTO inventory (character_id, item_id, quantity) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
                (character_id, item_id, quantity, quantity)
            )
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при добавлении предмета {item_id} в инвентарь персонажа {character_id}: {err}")
            return False

    def remove_item_from_inventory(self, character_id, item_id, quantity=1):
        try:
            self.cursor.execute(
                "UPDATE inventory SET quantity = quantity - %s WHERE character_id = %s AND item_id = %s",
                (quantity, character_id, item_id)
            )
            self.cursor.execute(
                "DELETE FROM inventory WHERE character_id = %s AND item_id = %s AND quantity <= 0",
                (character_id, item_id)
            )
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при удалении предмета {item_id} из инвентаря персонажа {character_id}: {err}")
            return False

    def get_inventory(self, character_id):
        try:
            self.cursor.execute(
                "SELECT items.id, items.name, items.description, items.type, items.weight, items.value, inventory.quantity "
                "FROM inventory "
                "JOIN items ON inventory.item_id = items.id "
                "WHERE inventory.character_id = %s",
                (character_id,)
            )
            result = self.cursor.fetchall()
            inventory = []
            for row in result:
                inventory.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "weight": row[4],
                    "value": row[5],
                    "quantity": row[6]
                })
            return inventory
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при получении инвентаря персонажа {character_id}: {err}")
            return None

    def get_equipment(self, character_id):
        """
        Возвращает экипировку персонажа.
        :param character_id: ID персонажа.
        :return: Список экипированных предметов.
        """
        try:
            self.cursor.execute(
                "SELECT items.id, items.name, items.description, items.type, items.weight, items.value, equipment.slot "
                "FROM equipment "
                "JOIN items ON equipment.item_id = items.id "
                "WHERE equipment.character_id = %s",
                (character_id,)
            )
            result = self.cursor.fetchall()
            equipment = []
            for row in result:
                equipment.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "weight": row[4],
                    "value": row[5],
                    "slot": row[6]
                })
            return equipment
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при получении экипировки персонажа {character_id}: {err}")
            return None

    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            logging.info("Подключение к базе данных закрыто.")

    def get_item_stats(self, item_id):
        """
        Возвращает характеристики предмета.
        :param item_id: ID предмета.
        :return: Словарь с характеристиками или None, если предмет не найден.
        """
        self.cursor.execute("SELECT * FROM item_stats WHERE item_id = %s", (item_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                "item_id": result[0],
                "strength": result[1],
                "agility": result[2],
                "intelligence": result[3],
                "health": result[4],
                "mana": result[5]
            }
        return None

    def apply_item_stats(self, character_id, item_id, operation="add"):
        """
        Применяет или снимает характеристики предмета.
        :param character_id: ID персонажа.
        :param item_id: ID предмета.
        :param operation: "add" для добавления, "subtract" для снятия.
        """
        stats = self.get_item_stats(item_id)
        if not stats:
            return False

        updates = []
        params = []
        for stat, value in stats.items():
            if stat == "item_id":
                continue
            if value != 0:
                if operation == "add":
                    updates.append(f"{stat} = {stat} + %s")
                else:
                    updates.append(f"{stat} = {stat} - %s")
                params.append(value)

        if updates:
            query = f"UPDATE characters SET {', '.join(updates)} WHERE id = %s"
            params.append(character_id)
            self.cursor.execute(query, tuple(params))
            self.connection.commit()
        return True

    def equip_item(self, character_id, item_id, slot):
        """
        Экипирует предмет на персонажа и применяет его характеристики.
        """
        try:
            # Проверяем, есть ли предмет в инвентаре
            self.cursor.execute(
                "SELECT quantity FROM inventory WHERE character_id = %s AND item_id = %s",
                (character_id, item_id)
            )
            result = self.cursor.fetchone()
            if not result or result[0] < 1:
                logging.warning(f"Предмет {item_id} отсутствует в инвентаре персонажа {character_id}")
                return False

            # Применяем характеристики предмета
            if not self.apply_item_stats(character_id, item_id, operation="add"):
                logging.warning(f"Не удалось применить характеристики предмета {item_id}")
                return False

            # Экипируем предмет
            self.cursor.execute(
                "INSERT INTO equipment (character_id, item_id, slot) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE item_id = %s",
                (character_id, item_id, slot, item_id)
            )
            self.connection.commit()
            logging.info(f"Предмет {item_id} экипирован в слот {slot} для персонажа {character_id}")
            return True
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при экипировке предмета {item_id} для персонажа {character_id}: {err}")
            return False

    def unequip_item(self, character_id, slot):
        """
        Снимает предмет с персонажа и убирает его характеристики.
        """
        try:
            # Получаем ID предмета, который нужно снять
            self.cursor.execute(
                "SELECT item_id FROM equipment WHERE character_id = %s AND slot = %s",
                (character_id, slot)
            )
            result = self.cursor.fetchone()
            if not result:
                logging.warning(f"Слот {slot} пуст для персонажа {character_id}")
                return False

            item_id = result[0]

            # Убираем характеристики предмета
            if not self.apply_item_stats(character_id, item_id, operation="subtract"):
                logging.warning(f"Не удалось убрать характеристики предмета {item_id}")
                return False

            # Снимаем предмет
            self.cursor.execute(
                "DELETE FROM equipment WHERE character_id = %s AND slot = %s",
                (character_id, slot)
            )
            self.connection.commit()
            logging.info(f"Предмет {item_id} снят со слота {slot} для персонажа {character_id}")
            return True
        except mysql.connector.Error as err:
            logging.error(f"Ошибка при снятии предмета со слота {slot} для персонажа {character_id}: {err}")
            return False

    def get_character_with_equipment(self, character_id):
        """
        Возвращает характеристики персонажа с учётом экипированных предметов.
        """
        character = self.get_character(character_id)
        if not character:
            return None

        equipment = self.get_equipment(character_id)
        if equipment:
            for item in equipment:
                stats = self.get_item_stats(item["id"])
                if stats:
                    character["strength"] += stats.get("strength", 0)
                    character["agility"] += stats.get("agility", 0)
                    character["intelligence"] += stats.get("intelligence", 0)
                    character["health"] += stats.get("health", 0)
                    character["mana"] += stats.get("mana", 0)

        return character
