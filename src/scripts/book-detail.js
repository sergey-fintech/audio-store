/**
 * JavaScript для страницы детализации книги
 * Загружает данные книги по ID из URL и отображает детализированную карточку
 */

// Конфигурация API
const API_BASE_URL = 'http://localhost:8002';

// Утилиты
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const main = document.querySelector('main');
    if (main) {
        main.innerHTML = `
            <div class="error-container" style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 400px;
                text-align: center;
                padding: 20px;
            ">
                <h2 style="color: #dc3545; margin-bottom: 20px;">Ошибка загрузки</h2>
                <p style="color: #666; margin-bottom: 20px;">${escapeHtml(message)}</p>
                <button onclick="window.location.href='index.html'" style="
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                ">Вернуться в каталог</button>
            </div>
        `;
    }
}

function showLoading() {
    const main = document.querySelector('main');
    if (main) {
        main.innerHTML = `
            <div class="loading-container" style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 400px;
                text-align: center;
                padding: 20px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #007bff;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 20px;
                "></div>
                <p style="color: #666;">Загрузка информации о книге...</p>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
    }
}

// Функция для получения ID книги из URL параметров
function getBookIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('id');
    
    if (!bookId) {
        throw new Error('ID книги не указан в URL. Используйте формат: book-detail.html?id=1');
    }
    
    const parsedId = parseInt(bookId, 10);
    if (isNaN(parsedId) || parsedId <= 0) {
        throw new Error('Некорректный ID книги. ID должен быть положительным числом.');
    }
    
    return parsedId;
}

// Функция для получения данных книги через API
async function fetchBookData(bookId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/audiobooks/${bookId}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Книга с указанным ID не найдена');
            }
            throw new Error(`Ошибка сервера: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Не удается подключиться к серверу. Проверьте, что сервис каталога запущен.');
        }
        throw error;
    }
}

// Функция для очистки главного контейнера
function clearMainContainer() {
    const main = document.querySelector('main');
    if (main) {
        main.innerHTML = '';
    } else {
        // Если main не найден, создаем его
        const body = document.body;
        const header = document.querySelector('header');
        const footer = document.querySelector('footer');
        
        // Удаляем все секции между header и footer
        const sections = document.querySelectorAll('section');
        sections.forEach(section => section.remove());
        
        // Создаем main контейнер
        const mainElement = document.createElement('main');
        if (header && footer) {
            header.insertAdjacentElement('afterend', mainElement);
        } else {
            body.appendChild(mainElement);
        }
    }
}

// Функция для создания детализированной карточки товара
function createBookDetailCard(bookData) {
    const authorName = bookData.author ? bookData.author.name : 'Неизвестный автор';
    const description = bookData.description || 'Описание отсутствует';
    const coverImage = bookData.cover_image_url || 'assets/images/placeholder.svg';
    const categories = bookData.categories || [];
    
    // Формируем список категорий
    const categoriesList = categories.length > 0 
        ? categories.map(cat => `<span class="category-tag">${escapeHtml(cat.name)}</span>`).join('')
        : '<span class="category-tag">Без категории</span>';
    
    return `
        <!-- Главная секция с деталями книги -->
        <section class="hero-section">
            <div class="container">
                <div class="hero-media">
                    <div class="hero-cover">
                        <img src="${escapeHtml(coverImage)}" alt="Обложка книги ${escapeHtml(bookData.title)}" 
                             onerror="this.src='assets/images/placeholder.svg'">
                    </div>
                    <div class="hero-player">
                        <div class="hero-player-text">Слушать фрагмент</div>
                        <div class="hero-player-controls">
                            <img src="assets/images/player-controls.svg" alt="Контролы плеера">
                        </div>
                    </div>
                </div>
                <div class="hero-content">
                    <div class="hero-heading">
                        <div class="hero-title">
                            <div class="hero-title-text">${escapeHtml(bookData.title)}</div>
                            <div class="hero-labels">
                                <img src="assets/images/hero-labels.svg" alt="Лейблы">
                            </div>
                        </div>
                        <div class="hero-info-wrapper">
                            <div class="hero-info">
                                <div class="hero-info-text">
                                    <p>Автор: <a href="#">${escapeHtml(authorName)}</a></p>
                                    <p>Читает: <a href="#">Алексей Сквозной</a></p>
                                </div>
                                <div class="hero-rating">
                                    <div class="hero-rating-score">4.8</div>
                                    <div class="hero-rating-text">
                                        <p>Рейтинг аудитерии</p>
                                        <p>1 234 оценок</p>
                                    </div>
                                </div>
                            </div>
                            <div class="hero-description">
                                <div class="hero-description-text">
                                    ${escapeHtml(description)}
                                </div>
                                <div class="hero-cut-button">
                                    <div class="hero-cut-text">Развернуть</div>
                                    <div class="hero-cut-icon">
                                        <img src="assets/images/expand-icon.svg" alt="Развернуть">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="hero-actions" style="margin-top: 30px;">
                        <div class="hero-social-icons-wrapper">
                            <div class="hero-social-icons">
                                <div class="social-icon">
                                    <img src="assets/images/vk-icon.svg" alt="VK">
                                </div>
                                <div class="social-icon instagram">
                                    <img src="assets/images/instagram-icon.svg" alt="Instagram">
                                </div>
                                <div class="social-icon facebook">
                                    <img src="assets/images/facebook-icon.svg" alt="Facebook">
                                </div>
                                <div class="social-icon youtube">
                                    <img src="assets/images/youtube-icon.svg" alt="YouTube">
                                </div>
                            </div>
                        </div>
                        <div class="hero-buttons">
                            <button class="hero-buy-button add-to-cart-btn" 
                                    data-book-id="${bookData.id}" 
                                    data-book-title="${escapeHtml(bookData.title)}" 
                                    data-book-price="${bookData.price}">
                                Купить за ${bookData.price} руб.
                            </button>
                            <button class="hero-desktop-button">Отправить на рабочий стол</button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Секция с информацией о книге -->
        <section class="book-info-section" style="
            padding: 40px 0;
            background: #f8f9fa;
            margin-top: 40px;
        ">
            <div class="container">
                <div class="book-info-grid" style="
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    align-items: start;
                ">
                    <div class="book-details">
                        <h3 style="
                            font-size: 24px;
                            font-weight: 700;
                            margin-bottom: 20px;
                            color: #333;
                        ">Информация о книге</h3>
                        <div class="detail-item" style="
                            margin-bottom: 15px;
                            padding: 10px 0;
                            border-bottom: 1px solid #eee;
                        ">
                            <strong style="color: #666;">ID:</strong> 
                            <span style="color: #333;">${bookData.id}</span>
                        </div>
                        <div class="detail-item" style="
                            margin-bottom: 15px;
                            padding: 10px 0;
                            border-bottom: 1px solid #eee;
                        ">
                            <strong style="color: #666;">Название:</strong> 
                            <span style="color: #333;">${escapeHtml(bookData.title)}</span>
                        </div>
                        <div class="detail-item" style="
                            margin-bottom: 15px;
                            padding: 10px 0;
                            border-bottom: 1px solid #eee;
                        ">
                            <strong style="color: #666;">Автор:</strong> 
                            <span style="color: #333;">${escapeHtml(authorName)}</span>
                        </div>
                        <div class="detail-item" style="
                            margin-bottom: 15px;
                            padding: 10px 0;
                            border-bottom: 1px solid #eee;
                        ">
                            <strong style="color: #666;">Цена:</strong> 
                            <span style="color: #333; font-weight: 700; font-size: 18px;">${bookData.price} ₽</span>
                        </div>
                        <div class="detail-item" style="
                            margin-bottom: 15px;
                            padding: 10px 0;
                            border-bottom: 1px solid #eee;
                        ">
                            <strong style="color: #666;">Категории:</strong> 
                            <div style="margin-top: 5px;">${categoriesList}</div>
                        </div>
                    </div>
                    <div class="book-cover-large">
                        <img src="${escapeHtml(coverImage)}" 
                             alt="Обложка книги ${escapeHtml(bookData.title)}"
                             style="
                                width: 100%;
                                max-width: 300px;
                                height: auto;
                                border-radius: 8px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                             "
                             onerror="this.src='assets/images/placeholder.svg'">
                    </div>
                </div>
            </div>
        </section>

        <!-- Секция с полным описанием -->
        <section class="description-section" style="
            padding: 40px 0;
        ">
            <div class="container">
                <h3 style="
                    font-size: 24px;
                    font-weight: 700;
                    margin-bottom: 20px;
                    color: #333;
                ">Описание</h3>
                <div class="description-content" style="
                    line-height: 1.6;
                    color: #555;
                    font-size: 16px;
                ">
                    ${escapeHtml(description)}
                </div>
            </div>
        </section>

        <!-- Секция треков (заглушка) -->
        <section class="tracks-section">
            <div class="container">
                <div class="tracks-header">
                    <h2 class="tracks-title">Содержание книги</h2>
                    <div class="tracks-duration">18 частей / 23 часа 15 минут</div>
                </div>
                <div class="tracks-list">
                    <div class="track-card">
                        <div class="track-content">
                            <div class="track-icon">
                                <img src="assets/images/play-icon.svg" alt="Воспроизвести">
                            </div>
                            <div class="track-text">Глава 1. Начало истории</div>
                        </div>
                    </div>
                    <div class="track-card">
                        <div class="track-content">
                            <div class="track-icon">
                                <img src="assets/images/play-icon.svg" alt="Воспроизвести">
                            </div>
                            <div class="track-text">Глава 2. Развитие сюжета</div>
                        </div>
                    </div>
                    <div class="track-card locked">
                        <div class="track-content">
                            <div class="track-icon">
                                <img src="assets/images/lock-icon.svg" alt="Заблокировано">
                            </div>
                            <div class="track-text">Глава 3. Кульминация (требуется покупка)</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Секция отзывов (заглушка) -->
        <section class="reviews-section">
            <div class="container">
                <h2 class="reviews-title">Отзывы / Рецензии</h2>
                <div class="reviews-wrapper">
                    <div class="review-card">
                        <div class="review-content">
                            <div class="review-date">16 июля 2022</div>
                            <div class="review-rating">
                                <img src="assets/images/star-rating.svg" alt="Рейтинг 5 звезд">
                            </div>
                        </div>
                        <div class="review-text">
                            Отличная аудиокнига! Рекомендую всем любителям качественной литературы.
                        </div>
                    </div>
                    <div class="review-card">
                        <div class="review-content">
                            <div class="review-date">12 июля 2022</div>
                            <div class="review-rating">
                                <img src="assets/images/star-rating.svg" alt="Рейтинг 5 звезд">
                            </div>
                        </div>
                        <div class="review-text">
                            Превосходное качество записи и профессиональное чтение. Стоит своих денег!
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <style>
            .category-tag {
                display: inline-block;
                background: #e9ecef;
                color: #495057;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-right: 5px;
                margin-bottom: 5px;
            }
            
            .book-info-grid {
                @media (max-width: 768px) {
                    grid-template-columns: 1fr;
                    gap: 20px;
                }
            }
        </style>
    `;
}

// Основная функция инициализации
async function initializeBookDetail() {
    try {
        // Показываем индикатор загрузки
        showLoading();
        
        // Получаем ID книги из URL
        const bookId = getBookIdFromUrl();
        console.log('Загружаем книгу с ID:', bookId);
        
        // Получаем данные книги
        const bookData = await fetchBookData(bookId);
        console.log('Получены данные книги:', bookData);
        
        // Очищаем главный контейнер
        clearMainContainer();
        
        // Создаем и добавляем детализированную карточку
        const main = document.querySelector('main');
        if (main) {
            main.innerHTML = createBookDetailCard(bookData);
            
            // Обновляем заголовок страницы
            document.title = `${bookData.title} - Аудитерия`;
            
            // Инициализируем обработчики событий для кнопок корзины
            initializeCartButtons();
            
            // Обновляем счетчик корзины
            updateCartCount();
            
            // Добавляем класс для показа контента
            document.body.classList.add('content-loaded');
            
            console.log('Страница детализации книги успешно загружена');
        }
        
    } catch (error) {
        console.error('Ошибка при загрузке страницы детализации:', error);
        showError(error.message);
    }
}

// Функция для инициализации обработчиков кнопок корзины
function initializeCartButtons() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Предотвращаем переход по ссылке
            e.stopPropagation(); // Останавливаем всплытие события
            
            const bookId = this.getAttribute('data-book-id');
            const bookTitle = this.getAttribute('data-book-title');
            const bookPrice = parseFloat(this.getAttribute('data-book-price'));
            
            console.log('Добавление в корзину:', { bookId, bookTitle, bookPrice });
            
            // Добавляем товар в корзину
            addToCart(bookId, bookTitle, bookPrice);
        });
    });
}

// Функция для добавления товара в корзину
function addToCart(bookId, bookTitle, bookPrice) {
    try {
        // Получаем текущую корзину из localStorage
        let cart = JSON.parse(localStorage.getItem('cart')) || [];
        
        // Проверяем, есть ли уже такой товар в корзине
        const existingItem = cart.find(item => item.id === bookId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                id: bookId,
                title: bookTitle,
                price: bookPrice,
                quantity: 1
            });
        }
        
        // Сохраняем обновленную корзину
        localStorage.setItem('cart', JSON.stringify(cart));
        
        // Обновляем счетчик корзины
        updateCartCount();
        
        // Показываем уведомление
        showCartNotification(bookTitle);
        
    } catch (error) {
        console.error('Ошибка при добавлении в корзину:', error);
        alert('Ошибка при добавлении товара в корзину');
    }
}

// Функция для обновления счетчика корзины
function updateCartCount() {
    try {
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
        }
    } catch (error) {
        console.error('Ошибка при обновлении счетчика корзины:', error);
    }
}

// Функция для показа уведомления о добавлении в корзину
function showCartNotification(bookTitle) {
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">✓</span>
            <span class="notification-text">"${bookTitle}" добавлена в корзину</span>
        </div>
    `;
    
    // Добавляем стили для уведомления
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        font-family: 'Ubuntu', sans-serif;
        font-size: 14px;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Удаляем уведомление через 3 секунды
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Функции для работы с авторизацией
function checkAuthStatus() {
    // Проверяем обычные токены (из auth.js)
    const accessToken = localStorage.getItem('access_token');
    const userEmail = localStorage.getItem('user_email');
    
    // Проверяем администраторские токены
    const adminToken = localStorage.getItem('admin_token');
    const adminUsername = localStorage.getItem('admin_username');
    
    // Проверяем старые ключи для совместимости
    const authToken = localStorage.getItem('auth_token');
    const username = localStorage.getItem('username');
    
    const isAuthenticated = !!(accessToken || adminToken || authToken);
    const isAdmin = !!adminToken;
    
    // Определяем имя пользователя
    let displayName = '';
    if (isAdmin && adminUsername) {
        displayName = adminUsername;
    } else if (userEmail) {
        displayName = userEmail;
    } else if (username) {
        displayName = username;
    }
    
    return {
        isAuthenticated: isAuthenticated,
        username: displayName,
        isAdmin: isAdmin
    };
}

function updateAuthUI() {
    const authStatus = checkAuthStatus();
    const loginBtn = document.querySelector('.login-btn');
    const profile = document.querySelector('.profile');
    const profileName = document.querySelector('.profile-name');
    const logoutBtn = document.querySelector('.logout-btn');
    
    if (authStatus.isAuthenticated) {
        // Пользователь авторизован
        if (loginBtn) {
            loginBtn.style.display = 'none';
        }
        
        if (profile && profileName) {
            profile.style.display = 'flex';
            profileName.textContent = authStatus.username || 'Пользователь';
        }
        
        if (logoutBtn) {
            logoutBtn.style.display = 'block';
        }
    } else {
        // Пользователь не авторизован
        if (loginBtn) {
            loginBtn.style.display = 'block';
        }
        
        if (profile) {
            profile.style.display = 'none';
        }
        
        if (logoutBtn) {
            logoutBtn.style.display = 'none';
        }
    }
}

function setupAuthEventListeners() {
    const logoutBtn = document.querySelector('.logout-btn');
    const loginBtn = document.querySelector('.login-btn');
    
    // Обработчик кнопки выхода
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите выйти?')) {
                // Проверяем, является ли пользователь администратором
                const isAdmin = localStorage.getItem('admin_token');
                
                // Очищаем ВСЕ данные авторизации (новые и старые ключи)
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_email');
                localStorage.removeItem('admin_token');
                localStorage.removeItem('admin_username');
                localStorage.removeItem('admin_login_time');
                localStorage.removeItem('auth_token');
                localStorage.removeItem('username');
                localStorage.removeItem('login_time');
                localStorage.removeItem('is_admin');
                
                // Обновляем UI
                updateAuthUI();
                
                // Показываем уведомление
                showCartNotification('Вы успешно вышли из системы');
                
                // Если это был администратор, перенаправляем на главную страницу
                if (isAdmin) {
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 1500);
                }
            }
        });
    }
    
    // Обработчик кнопки входа
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            const authStatus = checkAuthStatus();
            
            // Если пользователь уже авторизован, показываем сообщение
            if (authStatus.isAuthenticated) {
                e.preventDefault();
                showCartNotification('Вы уже авторизованы');
                return;
            }
            
            // Если не авторизован, переходим на страницу входа
            window.location.href = 'login.html';
        });
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    // Обновляем UI авторизации
    updateAuthUI();
    
    // Настраиваем обработчики событий авторизации
    setupAuthEventListeners();
    
    // Инициализируем страницу детализации
    initializeBookDetail();
});
