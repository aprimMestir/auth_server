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
