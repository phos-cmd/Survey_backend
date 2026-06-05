# 📊 SurveyProject (Бэкенд)

Современное веб-приложение для опросов и голосований (API бэкенд).
**Стек:** Django REST Framework + JWT + Swagger

---

## 🚀 Быстрый старт

### 1. Бэкенд (Django)

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
.venv\Scripts\activate

# Активировать (Linux/Mac)
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Заполнить БД тестовыми данными
python manage.py seed_data

# Запустить сервер
python manage.py runserver
```

Бэкенд доступен на: http://localhost:8000

---

## 🔗 Ссылки

| URL | Описание |
|-----|----------|
| http://localhost:8000/admin | Django Admin |
| http://localhost:8000/api/schema/swagger-ui/ | Swagger UI |
| http://localhost:8000/api/schema/redoc/ | ReDoc |

---

## 👤 Тестовый аккаунт (после seed_data)

- **Логин:** `admin`
- **Пароль:** `admin123`

---

## 📁 Структура проекта

```
SurveyProject/
├── manage.py
├── requirements.txt
├── db.sqlite3
│
├── SurveyProject/          # Конфигурация Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── surveys/                # Основное приложение
    ├── models.py           # Survey, Poll, Vote...
    ├── serializers.py      # DRF сериализаторы
    ├── views.py            # API ViewSets
    ├── urls.py             # API маршруты
    ├── admin.py            # Панель администратора
    ├── tests.py            # Тесты API
    └── management/
        └── commands/
            └── seed_data.py
```

---

## 🧪 Тесты

```bash
python manage.py test surveys
```

---

## 📡 API Endpoints

### Auth
| Method | URL | Описание |
|--------|-----|----------|
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/login/` | Получить JWT токены |
| POST | `/api/auth/refresh/` | Обновить access token |
| GET  | `/api/auth/me/` | Профиль пользователя |

### Surveys
| Method | URL | Описание |
|--------|-----|----------|
| GET  | `/api/surveys/` | Список опросов |
| GET  | `/api/surveys/{id}/` | Детали опроса |
| POST | `/api/surveys/{id}/submit/` | Отправить ответы |

### Polls
| Method | URL | Описание |
|--------|-----|----------|
| GET  | `/api/polls/` | Список голосований |
| GET  | `/api/polls/{id}/` | Детали голосования |
| POST | `/api/polls/{id}/vote/` | Проголосовать (требует JWT) |
| GET  | `/api/polls/{id}/result/` | Результаты |
