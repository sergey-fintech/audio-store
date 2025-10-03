import os
from flask import Flask, jsonify, render_template, g, request, abort
from database.connection import SessionLocal, initialize_database
from services.shared_services.catalog import CatalogService
from services.shared_services.cart import CartService, CartItemInput
from services.shared_services.prompts import PromptsService
from services.shared_services.auth import AuthService
from services.orders.services import OrderService
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from dotenv import load_dotenv
import openai
from database.models import Prompt # Added for Prompts Routes

# Определяем путь к корневой директории проекта
project_root = os.path.dirname(os.path.abspath(__file__))

# Загружаем переменные окружения
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Создаем экземпляр Flask, указывая пути к шаблонам и статическим файлам
app = Flask(__name__, 
            template_folder=os.path.join(project_root, 'src'),
            static_folder=os.path.join(project_root, 'src'),
            static_url_path='') # Отдаем статику из корня

# --- Инициализация базы данных ---

def add_initial_prompts(db_session):
    """Добавляет начальные промпты в БД, если они отсутствуют."""
    try:
        from database.models import Prompt
        
        # Проверяем, есть ли уже промпты
        existing_prompts = db_session.query(Prompt).count()
        if existing_prompts == 0:
            print("INFO:     Добавление начальных промптов в базу данных...")
            
            recommendation_prompt = Prompt(
                name="recommendation_prompt",
                description="Промпт для генерации общих рекомендаций на основе каталога.",
                content="""Ты — интеллектуальный помощник в книжном магазине. 
Твоя задача — проанализировать список доступных аудиокниг и предпочтения пользователя, а затем предоставить содержательные рекомендации.
Предпочтения пользователя: {user_preferences}
Доступные книги:
{available_books}
""",
                is_active=True
            )
            
            description_prompt = Prompt(
                name="description_generation_prompt",
                description="Промпт для генерации описания для конкретной книги.",
                content="""Напиши краткое, но интригующее описание для аудиокниги '{title}' автора {author}. 
Описание должно быть ёмким (2-3 предложения) и мотивировать пользователя к прослушиванию.
Стиль: художественный, немного загадочный.
""",
                is_active=True
            )
            
            db_session.add_all([recommendation_prompt, description_prompt])
            db_session.commit()
            print("INFO:     Начальные промпты успешно добавлены.")
        else:
            print("INFO:     Промпты уже существуют в базе данных, добавление не требуется.")
            
    except Exception as e:
        print(f"ERROR:    Не удалось добавить начальные промпты: {e}")
        db_session.rollback()

# Создаем все таблицы, если их нет
initialize_database()

# Добавляем начальные данные
with SessionLocal() as db:
    add_initial_prompts(db)

# --- AI / Recommender Configuration ---

# Настройка API-клиента для OpenRouter
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:5000", # Изменено на порт Flask
        "X-Title": "Audio Store",
    },
)

# Доступные модели LLM
AVAILABLE_MODELS = {
    "gemini-pro": "google/gemini-2.0-flash-001",
    "gemini-flash": "google/gemini-2.0-flash-001",
    "claude-3": "anthropic/claude-3.5-sonnet",
    "gpt-4": "openai/gpt-4-turbo",
    "llama-3": "meta-llama/llama-3-8b-instruct"
}

# --- DB Session Management ---

def get_db():
    """
    Создает и возвращает сессию БД для текущего запроса.
    Если сессия уже существует в контексте запроса (g), возвращает ее.
    """
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    """Закрывает сессию БД после завершения запроса."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Helpers ---
def audiobook_to_dict(ab):
    """Конвертирует объект Audiobook в словарь."""
    return {
        "id": ab.id,
        "title": ab.title,
        "description": ab.description,
        "price": float(ab.price) if isinstance(ab.price, Decimal) else ab.price,
        "cover_image_url": ab.cover_image_url,
        "author": {"id": ab.author.id, "name": ab.author.name} if ab.author else None,
        "categories": [{"id": cat.id, "name": cat.name} for cat in ab.categories]
    }

# --- Routes ---

@app.route('/')
def index():
    """Отдаем главный HTML-файл"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Проверка состояния приложения"""
    return jsonify({"status": "healthy", "service": "main_app"})

# --- Catalog Routes ---

@app.route('/api/v1/audiobooks', methods=['GET'])
def get_audiobooks():
    """Получить список аудиокниг."""
    db = get_db()
    catalog_service = CatalogService(db)
    
    # В Flask аргументы запроса получаем из request.args
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)
    
    # Используем метод репозитория напрямую через сервис
    audiobooks = catalog_service.audiobook_repo.get_all(limit=limit, offset=offset)
    
    return jsonify([audiobook_to_dict(ab) for ab in audiobooks])

@app.route('/api/v1/audiobooks/<int:audiobook_id>', methods=['GET'])
def get_audiobook(audiobook_id):
    """Получить аудиокнигу по ID."""
    db = get_db()
    catalog_service = CatalogService(db)
    audiobook = catalog_service.get_audiobook_by_id(audiobook_id)
    
    if not audiobook:
        abort(404, description="Аудиокнига не найдена")
        
    return jsonify(audiobook_to_dict(audiobook))

@app.route('/api/v1/search', methods=['GET'])
def search_audiobooks():
    """Поиск аудиокниг."""
    db = get_db()
    catalog_service = CatalogService(db)
    
    query = request.args.get('q')
    limit = request.args.get('limit', default=100, type=int)
    
    if not query:
        return jsonify({"error": "Параметр 'q' обязателен для поиска"}), 400
        
    audiobooks = catalog_service.search_audiobooks(q=query, limit=limit)
    
    return jsonify([audiobook_to_dict(ab) for ab in audiobooks])

# --- Cart Routes ---

@app.route('/api/v1/cart/calculate', methods=['POST'])
def calculate_cart():
    """Рассчитывает стоимость корзины."""
    db = get_db()
    
    # Сервис корзины зависит от сервиса каталога
    catalog_service = CatalogService(db)
    cart_service = CartService(catalog_service)
    
    # Получаем JSON из тела запроса
    data = request.get_json()
    if not data or 'items' not in data:
        abort(400, description="Отсутствует поле 'items' в запросе")
        
    # Валидируем входные данные с помощью Pydantic моделей из shared_services
    try:
        cart_items = [CartItemInput(**item) for item in data['items']]
    except Exception as e:
        abort(400, description=f"Ошибка валидации данных корзины: {e}")
        
    result = cart_service.calculate_cart(cart_items)
    
    # Pydantic модели содержат datetime, который нужно сериализовать
    return jsonify(result.dict())

# --- Orders Routes ---

def order_to_dict(order):
    """Конвертирует объект Order в словарь."""
    return {
        "id": order.id,
        "order_number": order.order_number,
        "total_amount": float(order.total_amount),
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        "items": [
            {
                "id": item.id,
                "audiobook_id": item.audiobook_id,
                "title": item.title,
                "price_per_unit": float(item.price_per_unit),
                "quantity": item.quantity,
                "total_price": float(item.price_per_unit * item.quantity),
                "created_at": item.created_at.isoformat()
            } for item in order.items
        ]
    }

@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    """Создает новый заказ."""
    db = get_db()
    catalog_service = CatalogService(db)
    cart_service = CartService(catalog_service)
    order_service = OrderService(db, cart_service)

    data = request.get_json()
    if not data or 'items' not in data:
        abort(400, description="Отсутствует поле 'items' в запросе")

    try:
        cart_items = [CartItemInput(**item) for item in data['items']]
    except Exception as e:
        abort(400, description=f"Ошибка валидации данных: {e}")

    cart_response = order_service.validate_cart(cart_items)
    if not cart_response.items:
        abort(400, description="Корзина пуста или содержит недействительные товары")
    
    try:
        order = order_service.create_order_transaction(cart_response)
        return jsonify(order_to_dict(order)), 201
    except SQLAlchemyError as e:
        abort(500, description=f"Ошибка при создании заказа: {e}")

@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Получает заказ по ID."""
    db = get_db()
    # OrderService не зависит от CartService для получения заказа
    order_service = OrderService(db, cart_service=None) 
    order = order_service.get_order_by_id(order_id)
    if not order:
        abort(404, description=f"Заказ с ID {order_id} не найден")
    return jsonify(order_to_dict(order))

@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    """Получает список всех заказов."""
    db = get_db()
    order_service = OrderService(db, cart_service=None)
    limit = request.args.get('limit', default=100, type=int)
    offset = request.args.get('offset', default=0, type=int)
    orders = order_service.get_all_orders(limit=limit, offset=offset)
    return jsonify([order_to_dict(o) for o in orders])

# --- Auth Routes ---

def user_to_dict(user):
    """Конвертирует объект User в словарь."""
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """Регистрация нового пользователя."""
    db = get_db()
    auth_service = AuthService(db)
    
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        abort(400, description="Отсутствуют поля 'email' или 'password'")
        
    email = data['email']
    password = data['password']
    
    if auth_service.get_user_by_email(email):
        return jsonify({"detail": "Пользователь с таким email уже зарегистрирован"}), 400
        
    user = auth_service.create_user(email, password)
    return jsonify(user_to_dict(user)), 201

@app.route('/api/v1/auth/token', methods=['POST'])
def get_token():
    """Аутентификация и выдача токена."""
    db = get_db()
    auth_service = AuthService(db)
    
    # Flask использует request.form для данных формы
    email = request.form.get('username')
    password = request.form.get('password')
    
    user = auth_service.authenticate_user(email, password)
    if not user:
        abort(401, description="Неверный email или пароль")
        
    access_token = auth_service.create_token(email=user.email)
    return jsonify({"access_token": access_token, "token_type": "bearer"})

@app.route('/api/v1/users/me', methods=['GET'])
def get_current_user():
    """Получение информации о текущем пользователе по токену."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        abort(401, description="Отсутствует или неверный токен авторизации")
        
    token = auth_header.split(' ')[1]
    
    db = get_db()
    auth_service = AuthService(db)
    
    user = auth_service.get_current_user_from_token(token)
    if not user:
        abort(401, description="Недействительный токен или пользователь не найден")
        
    return jsonify(user_to_dict(user))


# --- Prompts Routes (for Admin Panel) ---

def prompt_to_dict(prompt):
    """Конвертирует объект Prompt в словарь."""
    return {
        "id": prompt.id,
        "name": prompt.name,
        "description": prompt.description,
        "content": prompt.content,
        "is_active": str(prompt.is_active).lower(), # Приводим к строке 'true'/'false'
        "created_at": prompt.created_at.isoformat() if prompt.created_at else None
    }

@app.route('/api/v1/prompts', methods=['GET'])
def get_prompts():
    """Получить список всех промптов."""
    db = get_db()
    prompts_service = PromptsService(db)
    # Предполагаем, что в сервисе есть метод для получения всех промптов
    # Если его нет, его нужно будет добавить. 
    # Временно реализуем логику здесь.
    prompts = prompts_service.db_session.query(Prompt).all()
    return jsonify([prompt_to_dict(p) for p in prompts])

@app.route('/api/v1/prompts/<int:prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """Обновить содержимое промпта."""
    db = get_db()
    prompts_service = PromptsService(db)
    data = request.get_json()
    if not data or 'content' not in data:
        abort(400, description="Отсутствует поле 'content'")
    
    # Логика обновления, предполагаем наличие метода в сервисе
    prompt = prompts_service.db_session.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        abort(404, description="Промпт не найден")
        
    prompt.content = data['content']
    db.commit()
    db.refresh(prompt)
    
    return jsonify(prompt_to_dict(prompt))

@app.route('/api/v1/prompts/<int:prompt_id>/<action>', methods=['PUT'])
def toggle_prompt_status(prompt_id, action):
    """Активировать или деактивировать промпт."""
    if action not in ['activate', 'deactivate']:
        abort(400, description="Недопустимое действие. Используйте 'activate' или 'deactivate'.")
        
    db = get_db()
    prompts_service = PromptsService(db)
    
    prompt = prompts_service.db_session.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        abort(404, description="Промпт не найден")
        
    new_status = True if action == 'activate' else False
    prompt.is_active = new_status
    db.commit()
    
    message = "Промпт успешно активирован" if new_status else "Промпт успешно деактивирован"
    return jsonify({"message": message})


# --- Recommender Routes ---

@app.route('/api/v1/models', methods=['GET'])
def get_available_models():
    """Получить список доступных моделей"""
    return jsonify({
        "available_models": AVAILABLE_MODELS,
        "default_model": "gemini-pro",
        "description": "Доступные модели для генерации рекомендаций"
    })

@app.route('/api/v1/recommendations/generate', methods=['POST'])
def generate_recommendations():
    """Генерирует персонализированные рекомендации аудиокниг."""
    db = get_db()
    catalog_service = CatalogService(db)
    prompts_service = PromptsService(db)
    
    data = request.get_json()
    if not data or 'prompt' not in data:
        abort(400, description="Отсутствует поле 'prompt' в запросе")
        
    user_prompt = data['prompt']
    model_alias = data.get('model', 'gemini-pro')
    
    # 1. Получаем каталог аудиокниг
    audiobooks_models = catalog_service.audiobook_repo.get_all()
    audiobooks = [audiobook_to_dict(ab) for ab in audiobooks_models]
    if not audiobooks:
        abort(404, description="Каталог аудиокниг пуст")
        
    # 2. Создаем системный промпт
    base_prompt = prompts_service.get_prompt_by_name("recommendation_prompt").content
    books_list_text = "\n".join(
        [f"- {book['title']} (Автор: {book['author']['name'] if book.get('author') else 'Неизвестен'})" for book in audiobooks]
    )
    system_prompt = base_prompt.format(user_preferences=user_prompt, available_books=books_list_text)
    
    # 3. Вызываем LLM
    try:
        model_name = AVAILABLE_MODELS.get(model_alias, AVAILABLE_MODELS["gemini-pro"])
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        content = response.choices[0].message.content
        return jsonify({
            "recommendations": content,
            "model": model_name,
            "model_alias": model_alias,
            "total_books_analyzed": len(audiobooks)
        })
        
    except Exception as e:
        abort(500, description=f"Ошибка при обращении к LLM сервису: {e}")

@app.route('/api/v1/recommendations/generate-description/<int:audiobook_id>', methods=['POST'])
def generate_description(audiobook_id):
    """Генерирует и обновляет описание для конкретной аудиокниги."""
    db = get_db()
    catalog_service = CatalogService(db)
    prompts_service = PromptsService(db)
    
    data = request.get_json()
    model_alias = data.get('model', 'gemini-pro')
    
    # 1. Получаем данные аудиокниги
    audiobook = catalog_service.get_audiobook_by_id(audiobook_id)
    if not audiobook:
        abort(404, description="Аудиокнига не найдена")
        
    # 2. Создаем промпт для генерации описания
    prompt_template = prompts_service.get_prompt_by_name("description_generation_prompt")
    if not prompt_template:
        abort(404, description="Промпт 'description_generation_prompt' не найден")
        
    system_prompt = prompt_template.content.format(
        title=audiobook.title,
        author=audiobook.author.name if audiobook.author else "неизвестен"
    )
    
    # 3. Вызываем LLM
    try:
        model_name = AVAILABLE_MODELS.get(model_alias, AVAILABLE_MODELS["gemini-pro"])
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        generated_description = response.choices[0].message.content.strip()
        
        # 4. Обновляем описание в БД
        updated_audiobook = catalog_service.update_audiobook(
            audiobook_id, description=generated_description
        )
        
        return jsonify({
            "message": "Описание успешно сгенерировано и обновлено",
            "audiobook_id": audiobook_id,
            "generated_description": generated_description,
            "model_alias": model_alias,
            "model": model_name
        })
        
    except Exception as e:
        abort(500, description=f"Ошибка при генерации или обновлении описания: {e}")


if __name__ == '__main__':
    app.run(debug=True, port=5000)
