# KpiBoard-1.0
KpiBoard анализ расходов и доходов разных банков 
Локальное веб-приложение для учёта показателей и данных пользователей.
Стек: FastAPI + PostgreSQL + Docker + HTML/CSS/JS (Vanilla).
kpi_board_backend/

│
├── app/
│   ├── main.py              # Точка входа FastAPI
│   ├── models.py            # SQLAlchemy-модели (User, Profile, Settings)
│   ├── schemas.py           # Pydantic-схемы
│   ├── routers/
│   │   ├── users.py         # Работа с пользователями, профилем, настройками
│   │   └── auth.py          # Авторизация / JWT
│   ├── db.py                # Подключение к PostgreSQL
│   ├── security.py          # Хэширование, JWT
│   └── ...
│
├── frontend/
│   ├── register.html        # Регистрация нового пользователя
│   ├── login.html           # Вход в аккаунт
│   └── profile.html         # Личный кабинет пользователя
│
├── docker-compose.yml       # Контейнеры: API, DB, (опционально frontend)
├── requirements.txt         # Python-зависимости
└── README.md                # Этот файл

Запуск бэкенда
 — через Docker
cmd: docker compose up --build
После запуска:

API доступен на: http://127.0.0.1:8080/docs

БД PostgreSQL доступна в контейнере db
Проверка: 
http://127.0.0.1:8080/health
 → должно вернуть {"status":"ok"}

Запуска фронта
Открой терминал в папке frontend:

cd frontend
python -m http.server 3000
Теперь открой в браузере:

Регистрация → http://127.0.0.1:3000/register.html

Вход → http://127.0.0.1:3000/login.html

Профиль → http://127.0.0.1:3000/profile.html

После запуска:

Регистрируешь нового пользователя на register.html.

Входишь через login.html.

Редактируешь данные в profile.html — они сохраняются в БД.
