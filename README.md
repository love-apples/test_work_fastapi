# Практика FastAPI

### Запуск проекта

```bash
# Клонируем репозиторий
git clone https://github.com/love-apples/test_work_fastapi.git


# Переходим в папку проекта
cd test_work_fastapi


# Заполняем .env (отличие от .env.example в MONGO_HOST=mongo)
echo -e 'MONGO_HOST=mongo\nMONGO_PORT=27017\nMONGO_NAME=test_api' > .env


# Запускаем
docker compose up --build -d
```

### Тесты

```bash
cd test_work_fastapi

pytest -v
```