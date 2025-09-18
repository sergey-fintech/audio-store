// JavaScript для страницы корзины

// Ждем загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('Страница корзины загружена!');
    
    // Инициализация корзины
    initCartPage();
    
    // Инициализация состояния аутентификации
    if (window.AudioStore && window.AudioStore.initAuthState) {
        window.AudioStore.initAuthState();
    }
});

// Функция для инициализации страницы корзины
async function initCartPage() {
    await renderCart();
    initCartButtons();
}

// Функция для отображения товаров в корзине
async function renderCart() {
    const cartItemsContainer = document.getElementById('cart-items');
    const emptyCartElement = document.getElementById('empty-cart');
    const cartContent = document.querySelector('.cart-content');
    const cartLoading = document.getElementById('cart-loading');
    
    if (!cartItemsContainer) {
        console.error('Элемент cart-items не найден');
        return;
    }
    
    const cart = getCart();
    console.log('renderCart: получена корзина:', cart);
    console.log('renderCart: количество товаров:', cart.length);
    
    if (cart.length === 0) {
        console.log('renderCart: корзина пуста, показываем сообщение');
        // Показываем сообщение о пустой корзине
        if (emptyCartElement) emptyCartElement.style.display = 'block';
        if (cartContent) cartContent.style.display = 'none';
        if (cartLoading) cartLoading.style.display = 'none';
        return;
    }
    
    // Скрываем сообщение о пустой корзине и показываем загрузку
    if (emptyCartElement) emptyCartElement.style.display = 'none';
    if (cartContent) cartContent.style.display = 'block';
    if (cartLoading) cartLoading.style.display = 'block';
    
    try {
        // Получаем данные о товарах из микросервиса cart
        const cartData = await fetchCartData(cart);
        
        // Скрываем индикатор загрузки
        if (cartLoading) cartLoading.style.display = 'none';
        
        // Очищаем контейнер
        cartItemsContainer.innerHTML = '';
        
        // Отображаем товары
        cartData.items.forEach(item => {
            const cartItemElement = createCartItemElement(item);
            cartItemsContainer.appendChild(cartItemElement);
        });
        
        // Обновляем общую сумму
        updateCartTotalWithData(cartData.total);
        
    } catch (error) {
        console.error('Ошибка при загрузке данных корзины:', error);
        // Скрываем индикатор загрузки
        if (cartLoading) cartLoading.style.display = 'none';
        
        // Если сервис недоступен, используем fallback
        if (error.message === 'SERVICE_UNAVAILABLE') {
            console.log('Используем fallback режим (localStorage)');
            renderCartFallback(cart);
        } else {
            // Для других ошибок показываем уведомление
            if (window.AudioStore && window.AudioStore.showNotification) {
                window.AudioStore.showNotification('Ошибка загрузки корзины');
            }
            renderCartFallback(cart);
        }
    }
}

// Функция для получения данных корзины из микросервиса
async function fetchCartData(cart) {
    console.log('Данные корзины из localStorage:', cart);
    
    // Преобразуем данные корзины в формат, ожидаемый API
    const items = cart.map(item => ({
        audiobook_id: parseInt(item.id) || 0,
        quantity: item.quantity || 1
    })).filter(item => item.audiobook_id > 0); // Фильтруем только валидные ID
    
    console.log('Данные для отправки в API:', items);
    
    try {
        const response = await fetch('http://localhost:8004/api/v1/cart/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                items: items
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Ответ сервера при ошибке:', errorText);
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json();
        
        // Проверяем структуру ответа
        if (!data.items || data.total_price === undefined) {
            throw new Error('Неверная структура ответа от сервера');
        }
        
        console.log('Ответ от Cart Service:', data);
        
        // Преобразуем ответ в формат, ожидаемый нашим кодом
        const transformedItems = data.items.map(item => {
            const transformedItem = {
                id: item.audiobook_id.toString(),
                title: item.title,
                price: item.price_per_unit,
                quantity: item.quantity,
                total: item.total_price
            };
            console.log('Преобразованный товар:', transformedItem);
            return transformedItem;
        });
        
        const result = {
            items: transformedItems,
            total: data.total_price
        };
        
        console.log('Итоговый результат для отображения:', result);
        return result;
        
    } catch (error) {
        console.error('Ошибка при получении данных корзины:', error);
        
        // Если это CORS ошибка или сеть недоступна, используем fallback
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            console.log('Микросервис недоступен, используем данные из localStorage');
            throw new Error('SERVICE_UNAVAILABLE');
        }
        
        throw error;
    }
}

// Fallback функция для отображения корзины из localStorage
function renderCartFallback(cart) {
    const cartItemsContainer = document.getElementById('cart-items');
    
    // Очищаем контейнер
    cartItemsContainer.innerHTML = '';
    
    // Отображаем товары
    cart.forEach(item => {
        const cartItemElement = createCartItemElement(item);
        cartItemsContainer.appendChild(cartItemElement);
    });
    
    // Обновляем общую сумму
    updateCartTotal();
}

// Функция для создания элемента товара в корзине
function createCartItemElement(item) {
    const cartItem = document.createElement('div');
    cartItem.className = 'cart-item';
    cartItem.setAttribute('data-book-id', item.id);
    
    const totalPrice = item.price * (item.quantity || 1);
    
    cartItem.innerHTML = `
        <div class="cart-item-content">
            <div class="cart-item-info">
                <h3 class="cart-item-title">${item.title}</h3>
                <div class="cart-item-price">${item.price} ₽</div>
            </div>
            <div class="cart-item-controls">
                <div class="quantity-controls">
                    <button class="quantity-btn minus-btn" data-book-id="${item.id}">-</button>
                    <span class="quantity-value">${item.quantity || 1}</span>
                    <button class="quantity-btn plus-btn" data-book-id="${item.id}">+</button>
                </div>
                <div class="cart-item-total">${totalPrice} ₽</div>
                <button class="remove-item-btn" data-book-id="${item.id}">Удалить</button>
            </div>
        </div>
    `;
    
    return cartItem;
}

// Функция для обновления общей суммы корзины
function updateCartTotal() {
    const totalElement = document.getElementById('cart-total-price');
    if (!totalElement) return;
    
    const cart = getCart();
    const total = cart.reduce((sum, item) => {
        return sum + (item.price * (item.quantity || 1));
    }, 0);
    
    totalElement.textContent = `${total} ₽`;
}

// Функция для обновления общей суммы с данными из API
function updateCartTotalWithData(total) {
    const totalElement = document.getElementById('cart-total-price');
    if (!totalElement) return;
    
    totalElement.textContent = `${total} ₽`;
}

// Функция для инициализации кнопок корзины
function initCartButtons() {
    // Кнопка очистки корзины
    const clearCartBtn = document.getElementById('clear-cart-btn');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', clearCart);
    }
    
    // Кнопка оформления заказа
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', checkout);
    }
    
    // Делегирование событий для кнопок количества и удаления
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('minus-btn')) {
            const bookId = e.target.getAttribute('data-book-id');
            decreaseQuantity(bookId);
        } else if (e.target.classList.contains('plus-btn')) {
            const bookId = e.target.getAttribute('data-book-id');
            increaseQuantity(bookId);
        } else if (e.target.classList.contains('remove-item-btn')) {
            const bookId = e.target.getAttribute('data-book-id');
            removeFromCart(bookId);
        }
    });
}

// Функция для увеличения количества товара
function increaseQuantity(bookId) {
    console.log('Увеличение количества для ID:', bookId, 'тип:', typeof bookId);
    const cart = getCart();
    console.log('Текущая корзина:', cart);
    
    // Ищем товар по ID (сравниваем как строки)
    const item = cart.find(item => String(item.id) === String(bookId));
    
    if (item) {
        item.quantity = (item.quantity || 1) + 1;
        saveCart(cart);
        renderCart();
        
        if (window.AudioStore && window.AudioStore.showNotification) {
            window.AudioStore.showNotification('Количество увеличено');
        }
    } else {
        console.error('Товар с ID', bookId, 'не найден в корзине');
    }
}

// Функция для уменьшения количества товара
function decreaseQuantity(bookId) {
    console.log('Уменьшение количества для ID:', bookId, 'тип:', typeof bookId);
    const cart = getCart();
    
    // Ищем товар по ID (сравниваем как строки)
    const item = cart.find(item => String(item.id) === String(bookId));
    
    if (item && (item.quantity || 1) > 1) {
        item.quantity = (item.quantity || 1) - 1;
        saveCart(cart);
        renderCart();
        
        if (window.AudioStore && window.AudioStore.showNotification) {
            window.AudioStore.showNotification('Количество уменьшено');
        }
    } else if (item && (item.quantity || 1) === 1) {
        // Если количество равно 1, удаляем товар
        removeFromCart(bookId);
    } else {
        console.error('Товар с ID', bookId, 'не найден в корзине');
    }
}

// Функция для удаления товара из корзины
function removeFromCart(bookId) {
    console.log('Удаление товара с ID:', bookId, 'тип:', typeof bookId);
    
    if (confirm('Вы уверены, что хотите удалить этот товар из корзины?')) {
        const cart = getCart();
        console.log('Корзина до удаления:', cart);
        
        // Фильтруем товары по ID (сравниваем как строки)
        const updatedCart = cart.filter(item => String(item.id) !== String(bookId));
        console.log('Корзина после удаления:', updatedCart);
        
        saveCart(updatedCart);
        renderCart();
        
        if (window.AudioStore && window.AudioStore.showNotification) {
            window.AudioStore.showNotification('Товар удален из корзины');
        }
    }
}

// Функция для очистки корзины
function clearCart() {
    if (confirm('Вы уверены, что хотите очистить корзину?')) {
        saveCart([]);
        renderCart();
        
        // Обновляем счетчик корзины
        updateCartCount();
        
        // Вызываем глобальное обновление
        if (window.updateGlobalCartCount) {
            window.updateGlobalCartCount();
        }
        
        // Вызываем обновление из navigation.js
        if (window.Navigation && window.Navigation.updateCartCount) {
            window.Navigation.updateCartCount();
        }
        
        if (window.AudioStore && window.AudioStore.showNotification) {
            window.AudioStore.showNotification('Корзина очищена');
        }
    }
}

// Функция для оформления заказа
async function checkout() {
    const cart = getCart();
    
    if (cart.length === 0) {
        alert('Ваша корзина пуста');
        return;
    }
    
    // Проверяем аутентификацию
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        alert('Для оформления заказа необходимо войти в систему');
        window.location.href = 'login.html';
        return;
    }
    
    try {
        // Показываем индикатор загрузки
        const checkoutBtn = document.getElementById('checkout-btn');
        const originalText = checkoutBtn.textContent;
        checkoutBtn.textContent = 'Оформление...';
        checkoutBtn.disabled = true;
        
        console.log('Данные корзины для заказа:', cart);
        
        // Отправляем заказ в микросервис orders
        const items = cart.map(item => {
            const audiobookId = parseInt(item.id) || 0;
            console.log(`Преобразование ID: "${item.id}" -> ${audiobookId}`);
            return {
                audiobook_id: audiobookId,
                quantity: item.quantity || 1
            };
        }).filter(item => item.audiobook_id > 0); // Фильтруем только валидные ID
        
        console.log('Данные для отправки в Orders Service:', items);
        
        if (items.length === 0) {
            throw new Error('Нет валидных товаров для заказа');
        }
        
        const response = await fetch('http://localhost:8003/api/v1/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                items: items
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const orderResult = await response.json();
        
        // Очищаем корзину в localStorage
        saveCart([]);
        
        // Обновляем отображение
        renderCart();
        
        // Показываем сообщение об успехе
        alert('Заказ успешно оформлен!');
        
        // Перенаправляем на главную страницу
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
        
    } catch (error) {
        console.error('Ошибка при оформлении заказа:', error);
        
        // Если сервис недоступен, показываем соответствующее сообщение
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            alert('Сервис заказов временно недоступен. Попробуйте позже.');
        } else {
            alert('Ошибка при оформлении заказа. Попробуйте еще раз.');
        }
    } finally {
        // Восстанавливаем кнопку
        const checkoutBtn = document.getElementById('checkout-btn');
        checkoutBtn.textContent = 'Оформить заказ';
        checkoutBtn.disabled = false;
    }
}

// Вспомогательные функции (используем из основного script.js)
function getCart() {
    // Всегда используем ключ 'cart' для единообразия
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    console.log('getCart из localStorage:', cart);
    return cart;
}

// Функция для обновления счетчика корзины
function updateCartCount() {
    try {
        const cart = getCart();
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
            console.log('Счетчик корзины обновлен в cart.js:', totalItems);
        } else {
            console.warn('Элемент cart-count не найден в cart.js');
        }
    } catch (error) {
        console.error('Ошибка при обновлении счетчика корзины в cart.js:', error);
    }
}

function saveCart(cart) {
    // Всегда используем ключ 'cart' для единообразия
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Обновляем глобальную переменную cartItems
    if (window.cartItems !== undefined) {
        window.cartItems = cart;
    }
    
    // Также обновляем через AudioStore если доступен
    if (window.AudioStore && window.AudioStore.saveCart) {
        window.AudioStore.saveCart(cart);
    }
}
