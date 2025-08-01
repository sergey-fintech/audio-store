# Примеры использования API микросервиса "Корзина"

## Примеры запросов с помощью curl

### 1. Расчет корзины с существующими товарами

```bash
curl -X POST "http://localhost:8001/api/v1/cart/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"audiobook_id": 1, "quantity": 2},
      {"audiobook_id": 2, "quantity": 1},
      {"audiobook_id": 3, "quantity": 3}
    ]
  }'
```

**Ожидаемый ответ:**
```json
{
  "items": [
    {
      "audiobook_id": 1,
      "title": "Название аудиокниги 1",
      "price_per_unit": 299.99,
      "quantity": 2,
      "total_price": 599.98
    },
    {
      "audiobook_id": 2,
      "title": "Название аудиокниги 2",
      "price_per_unit": 199.99,
      "quantity": 1,
      "total_price": 199.99
    },
    {
      "audiobook_id": 3,
      "title": "Название аудиокниги 3",
      "price_per_unit": 399.99,
      "quantity": 3,
      "total_price": 1199.97
    }
  ],
  "total_price": 1999.94,
  "calculated_at": "2024-01-15T10:30:00"
}
```

### 2. Расчет корзины с несуществующими товарами

```bash
curl -X POST "http://localhost:8001/api/v1/cart/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"audiobook_id": 1, "quantity": 1},
      {"audiobook_id": 999, "quantity": 2},
      {"audiobook_id": 888, "quantity": 1}
    ]
  }'
```

**Ожидаемый ответ:**
```json
{
  "items": [
    {
      "audiobook_id": 1,
      "title": "Название аудиокниги 1",
      "price_per_unit": 299.99,
      "quantity": 1,
      "total_price": 299.99
    }
  ],
  "total_price": 299.99,
  "calculated_at": "2024-01-15T10:30:00"
}
```

### 3. Пустая корзина

```bash
curl -X POST "http://localhost:8001/api/v1/cart/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "items": []
  }'
```

**Ожидаемый ответ:**
```json
{
  "items": [],
  "total_price": 0.0,
  "calculated_at": "2024-01-15T10:30:00"
}
```

### 4. Проверка состояния сервиса

```bash
curl -X GET "http://localhost:8001/health"
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "service": "cart"
}
```

## Примеры с помощью Python

### Использование httpx

```python
import httpx
import asyncio

async def calculate_cart():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1/cart/calculate",
            json={
                "items": [
                    {"audiobook_id": 1, "quantity": 2},
                    {"audiobook_id": 2, "quantity": 1}
                ]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Общая стоимость: {result['total_price']}")
            print(f"Количество товаров: {len(result['items'])}")

# Запуск
asyncio.run(calculate_cart())
```

### Использование requests (синхронно)

```python
import requests

def calculate_cart_sync():
    response = requests.post(
        "http://localhost:8001/api/v1/cart/calculate",
        json={
            "items": [
                {"audiobook_id": 1, "quantity": 2},
                {"audiobook_id": 2, "quantity": 1}
            ]
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Общая стоимость: {result['total_price']}")
        print(f"Количество товаров: {len(result['items'])}")

# Запуск
calculate_cart_sync()
```

## Особенности работы

1. **Асинхронная обработка**: Все запросы к микросервису "Каталог" выполняются параллельно
2. **Обработка ошибок**: Товары с несуществующими ID игнорируются
3. **Таймауты**: Установлен таймаут 10 секунд для HTTP запросов
4. **Валидация**: Входные данные автоматически валидируются с помощью Pydantic

## Коды ошибок

- `200` - Успешный расчет корзины
- `422` - Ошибка валидации входных данных
- `500` - Внутренняя ошибка сервера

## Примечания

- Сервис работает на порту 8001
- Требуется запущенный микросервис "Каталог" на порту 8000
- Все цены возвращаются в формате float
- Время расчета указывается в UTC 