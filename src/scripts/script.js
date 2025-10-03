// Основной JavaScript файл для AudioStore

// Глобальные переменные
let cartItems = JSON.parse(localStorage.getItem('cart')) || [];

// Ждем загрузки DOM
document.addEventListener('DOMContentLoaded', async function() {
    console.log('AudioStore загружен!');
    
    // Инициализация всех компонентов
    initNavigation();
    initSearch();
    initBookCards();
    initLogout();
    
    // Инициализация корзины
    initCart();
    
    // Инициализация состояния аутентификации
    await initAuthState();
    
    // Инициализация кнопки входа
    initLoginButton();
});

// Функция для инициализации навигации
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
                    // Не предотвращаем переход для ссылок на корзину, админ-панель и каталог
        const href = this.getAttribute('href');
        if (href === 'cart.html' || href === 'admin/admin.html' || href.includes('index.html')) {
            return;
        }
            
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Функции для работы с корзиной
function getCart() {
    return JSON.parse(localStorage.getItem('cart')) || [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
    cartItems = cart; // Обновляем глобальную переменную
}

function updateCartCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        const cart = getCart();
        cartCountElement.textContent = cart.length;
    }
}

function addToCart(bookId, bookTitle, bookPrice) {
    const cart = getCart();
    
    // Проверяем, есть ли уже такая книга в корзине
    const existingItem = cart.find(item => item.id === bookId);
    
    if (existingItem) {
        // Если книга уже в корзине, увеличиваем количество
        existingItem.quantity = (existingItem.quantity || 1) + 1;
    } else {
        // Если книги нет в корзине, добавляем новую
        cart.push({
            id: parseInt(bookId), // Убеждаемся, что id - это число
            title: bookTitle,
            price: bookPrice,
            quantity: 1
        });
    }
    
    saveCart(cart);
    updateCartCount();
    
    // Показываем уведомление
    showNotification('Книга добавлена в корзину!');
}

function initCart() {
    // Обновляем счетчик корзины при загрузке страницы
    updateCartCount();
    
    // Используем делегирование событий для кнопок добавления в корзину
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-cart-btn')) {
            e.preventDefault();
            
            const button = e.target;
            const bookCard = button.closest('.book-card');
            
            let bookId, bookTitle, bookPrice;
            
            if (bookCard) {
                // Для карточек книг в списке
                bookId = parseInt(bookCard.getAttribute('data-book-id'));
                bookTitle = bookCard.querySelector('.book-title').textContent;
                bookPrice = parseInt(bookCard.querySelector('.book-price').textContent.replace(' ₽', ''));
            } else {
                // Для кнопок в hero и offer секциях
                bookId = parseInt(button.getAttribute('data-book-id'));
                bookTitle = button.getAttribute('data-book-title');
                bookPrice = parseInt(button.getAttribute('data-book-price'));
            }
            
            // Проверяем, что bookId валидный
            if (bookId && !isNaN(bookId)) {
                addToCart(bookId, bookTitle, bookPrice);
            } else {
                console.error('Невалидный bookId:', bookId);
                showNotification('Ошибка: не удалось добавить товар в корзину');
            }
        }
    });
}

// Старая функция для добавления в корзину (оставлена для совместимости)
function addToCartOld(bookTitle, bookPrice) {
    cartItems.push({
        title: bookTitle,
        price: bookPrice
    });
    localStorage.setItem('cart', JSON.stringify(cartItems));
    
    // Показываем уведомление
    showNotification('Книга добавлена в корзину!');
}

// Функция для инициализации поиска
function initSearch() {
    const searchBtn = document.querySelector('.search-btn');
    
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            // Переходим на страницу поиска
            window.location.href = 'search.html';
        });
    }
    
    function performSearch(term) {
        // Здесь будет логика поиска
        console.log(`Поиск: ${term}`);
        alert(`Поиск по запросу "${term}" будет реализован позже`);
    }
}

// Функция для инициализации карточек книг (обновлена для новой логики корзины)
function initBookCards() {
    // Эта функция больше не нужна, так как используется делегирование событий в initCart()
    // Оставляем для совместимости
    console.log('Карточки книг инициализированы');
}

// Функция для инициализации состояния аутентификации
async function initAuthState() {
    const accessToken = localStorage.getItem('access_token');
    const loginBtn = document.querySelector('.login-btn');
    const profileBlock = document.querySelector('.profile');
    const logoutBtn = document.querySelector('.logout-btn');
    
    if (accessToken) {
        // Пользователь аутентифицирован
        await showAuthenticatedState(loginBtn, profileBlock, logoutBtn);
    } else {
        // Пользователь не аутентифицирован
        showUnauthenticatedState(loginBtn, profileBlock, logoutBtn);
    }
}

// Функция для показа состояния аутентифицированного пользователя
async function showAuthenticatedState(loginBtn, profileBlock, logoutBtn) {
    // Скрываем кнопку входа
    if (loginBtn) {
        loginBtn.style.display = 'none';
    }
    
    // Показываем блок профиля
    if (profileBlock) {
        profileBlock.style.display = 'flex';
        
        // Обновляем имя пользователя
        await updateUserName(profileBlock);
    }
    
    // Показываем кнопку выхода
    if (logoutBtn) {
        logoutBtn.style.display = 'block';
    }
}

// Функция для показа состояния неаутентифицированного пользователя
function showUnauthenticatedState(loginBtn, profileBlock, logoutBtn) {
    // Показываем кнопку входа
    if (loginBtn) {
        loginBtn.style.display = 'block';
    }
    
    // Скрываем блок профиля
    if (profileBlock) {
        profileBlock.style.display = 'none';
    }
    
    // Скрываем кнопку выхода
    if (logoutBtn) {
        logoutBtn.style.display = 'none';
    }
}

// Функция для обновления имени пользователя
async function updateUserName(profileBlock) {
    const userNameElement = profileBlock.querySelector('.profile-name');
    const accessToken = localStorage.getItem('access_token');
    
    if (userNameElement) {
        if (accessToken) {
            try {
                // Получаем данные пользователя из API
                const response = await fetch('/api/v1/users/me', {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                
                if (response.ok) {
                    const user = await response.json();
                    userNameElement.textContent = user.email;
                } else {
                    // Если токен недействителен, очищаем localStorage
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('user');
                    userNameElement.textContent = 'Профиль';
                }
            } catch (error) {
                console.error('Ошибка при получении данных пользователя:', error);
                userNameElement.textContent = 'Профиль';
            }
        } else {
            userNameElement.textContent = 'Профиль';
        }
    }
}

// Функция для инициализации кнопки входа
function initLoginButton() {
    const loginBtn = document.querySelector('.login-btn');
    
    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            window.location.href = 'login.html';
        });
    }
}

// Функция для инициализации кнопки выхода
function initLogout() {
    const logoutBtn = document.querySelector('.logout-btn');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите выйти?')) {
                // Очищаем данные пользователя
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                localStorage.removeItem('cart');
                cartItems = [];
                
                // Показываем уведомление
                showNotification('Вы успешно вышли из системы');
                
                // Обновляем UI
                initAuthState();
                
                // Перенаправляем на страницу входа
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
            }
        });
    }
}

// Функция для показа уведомлений
function showNotification(message) {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    // Стили для уведомления
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #27ae60;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Показываем уведомление
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Скрываем уведомление через 3 секунды
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Функция для плавной прокрутки к секциям
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Обработчик для кнопки "Начать покупки"
document.addEventListener('DOMContentLoaded', function() {
    const startShoppingBtn = document.querySelector('.hero .btn-primary');
    if (startShoppingBtn) {
        startShoppingBtn.addEventListener('click', function() {
            smoothScrollTo('catalog');
        });
    }
});

// Функция для загрузки данных книг (будет использоваться позже)
function loadBooks() {
    // Здесь будет API запрос для загрузки книг
    const sampleBooks = [
        {
            title: 'Война и мир',
            author: 'Лев Толстой',
            price: 299,
            cover: 'assets/images/book1.jpg'
        },
        {
            title: 'Преступление и наказание',
            author: 'Федор Достоевский',
            price: 249,
            cover: 'assets/images/book2.jpg'
        }
    ];
    
    return sampleBooks;
}

// Функция для обновления состояния аутентификации (для использования из других модулей)
async function updateAuthState() {
    await initAuthState();
}

// Экспортируем функции для использования в других модулях
window.AudioStore = {
    addToCart,
    getCart,
    saveCart,
    updateCartCount,
    initCart,
    smoothScrollTo,
    loadBooks,
    showNotification,
    initLogout,
    updateAuthState,
    initAuthState,
    initLoginButton
};

// Используем функции из auth.js для аутентификации
// Основной script.js теперь фокусируется на общей функциональности сайта