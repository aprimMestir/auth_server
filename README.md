Регистрация:

    curl -X POST http://127.0.0.1:5000/register \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "testpass"}'
Вход:

    curl -X POST http://127.0.0.1:5000/login \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "testpass"}'
Проверка авторизации:

    curl -X GET http://127.0.0.1:5000/check_auth?username=testuser
Логаут:
    
    curl -X POST http://127.0.0.1:5000/logout \
    -H "Authorization: your_jwt_token_here"
Создание персонажа:
    
    curl -X POST http://127.0.0.1:5000/create_character \
    -H "Content-Type: application/json" \
    -d '{
      "user_id": 1,
      "name": "Warrior",
      "class": "Warrior",
      "race": "Human",
      "level": 1,
      "health": 100,
      "mana": 50,
      "strength": 15,
      "agility": 10,
      "intelligence": 5,
      "xp": 0,
      "gold": 0,
      "inventory": "Sword, Shield"
    }'
Получение данных персонажа:
    
    curl -X GET http://127.0.0.1:5000/get_character?user_id=1

Обновление данных персонажа:

    curl -X POST http://127.0.0.1:5000/update_character \
    -H "Content-Type: application/json" \
    -d '{
      "character_id": 1,
      "updates": {
        "level": 2,
        "health": 120,
        "gold": 100
      }
    }'
Создание персонажа с невалидным именем:

    curl -X POST http://127.0.0.1:5000/create_character \
    -H "Content-Type: application/json" \
    -d '{"user_id": 1, "name": "W@rrior"}'
    
    Ответ:

    {
      "error": "Failed to create character. Invalid name or database error."
    }
Создание персонажа с валидным именем:

    curl -X POST http://127.0.0.1:5000/create_character \
    -H "Content-Type: application/json" \
    -d '{"user_id": 1, "name": "Warrior"}'

    Ответ:

    {
      "message": "Character created successfully"
    }
