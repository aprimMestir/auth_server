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

Получение инвентаря:
    
    curl -X GET http://127.0.0.1:5000/get_inventory?character_id=1

Добавление предмета в инвентарь:

    curl -X POST http://127.0.0.1:5000/add_item_to_inventory \
    -H "Content-Type: application/json" \
    -d '{
      "character_id": 1,
      "item_id": 1,
      "quantity": 2
    }'

Удаление предмета из инвентаря:

    curl -X POST http://127.0.0.1:5000/remove_item_from_inventory \
    -H "Content-Type: application/json" \
    -d '{
      "character_id": 1,
      "item_id": 1,
      "quantity": 1
    }'

Получение экипировки:

    curl -X GET http://127.0.0.1:5000/get_equipment?character_id=1
Экипировка предмета:

    curl -X POST http://127.0.0.1:5000/equip_item \
    -H "Content-Type: application/json" \
    -d '{
      "character_id": 1,
      "item_id": 1,
      "slot": "weapon"
    }'
Снятие предмета:

    curl -X POST http://127.0.0.1:5000/unequip_item \
    -H "Content-Type: application/json" \
    -d '{
      "character_id": 1,
      "slot": "weapon"
    }'

Экипировка меча (тип "weapon") в слот "weapon":


    curl -X POST http://localhost:5000/equip_item \
    -H "Content-Type: application/json" \
    -d '{"character_id": 1, "item_id": 5, "slot": "weapon"}'

Попытка экипировать броню (тип "armor") в слот "weapon":

    curl -X POST http://localhost:5000/equip_item \
    -H "Content-Type: application/json" \
    -d '{"character_id": 1, "item_id": 8, "slot": "weapon"}'
    
    # Ответ: 
    # {"error": "Invalid slot weapon for armor"}

Попытка экипировать предмет в занятый слот:

    curl -X POST http://localhost:5000/equip_item \
    -H "Content-Type: application/json" \
    -d '{"character_id": 1, "item_id": 5, "slot": "weapon"}'
    
    # Ответ: 
    # {"error": "Slot already occupied"}

Экипировка меча (увеличивает силу на 10):

    curl -X POST http://localhost:5000/equip \
    -H "Content-Type: application/json" \
    -d '{"character_id": 1, "item_id": 5, "slot": "weapon"}'

Получение характеристик персонажа:

    curl -X GET http://localhost:5000/character/1
    
    # Ответ:
    # {
    #   "id": 1,
    #   "name": "Warrior",
    #   "strength": 20,  # Базовая сила 10 + 10 от меча
    #   "agility": 10,
    #   "intelligence": 5,
    #   "health": 100,
    #   "mana": 50
    # }

Снятие меча:

    curl -X POST http://localhost:5000/unequip \
    -H "Content-Type: application/json" \
    -d '{"character_id": 1, "slot": "weapon"}'

    Получение характеристик после снятия
    
    curl -X GET http://localhost:5000/character/1
    
    # Ответ:
    # {
    #   "id": 1,
    #   "name": "Warrior",
    #   "strength": 10,  # Базовая сила 10
    #   "agility": 10,
    #   "intelligence": 5,
    #   "health": 100,
    #   "mana": 50
    # }