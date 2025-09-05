// Клиент API аутентификации
// Отдельный модуль для работы с API аутентификации

// Конфигурация API
const AUTH_API_BASE_URL = 'http://localhost:8001';

// Функция для показа уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Базовые стили
    let backgroundColor = '#3498db';
    if (type === 'success') backgroundColor = '#27ae60';
    if (type === 'error') backgroundColor = '#e74c3c';
    if (type === 'warning') backgroundColor = '#f39c12';
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: ${backgroundColor};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        font-family: 'Ubuntu', sans-serif;
        font-weight: 500;
    `;
    
    document.body.appendChild(notification);
    
    // Показываем уведомление
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Скрываем уведомление через 4 секунды
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Функция для регистрации пользователя
async function registerUser(email, password) {
    try {
        const response = await fetch(`${AUTH_API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        if (response.ok) {
            const userData = await response.json();
            showNotification('Регистрация успешна! Перенаправляем на страницу входа...', 'success');
            
            // Перенаправляем на страницу входа через 2 секунды
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            
            // Обновляем состояние аутентификации на главной странице
            if (window.AudioStore && window.AudioStore.updateAuthState) {
                await window.AudioStore.updateAuthState();
            }
            
            return { success: true, data: userData };
            
        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Ошибка при регистрации', 'error');
            return { success: false, error: errorData.detail };
        }
        
    } catch (error) {
        console.error('Ошибка при регистрации:', error);
        showNotification('Ошибка соединения с сервером', 'error');
        return { success: false, error: 'Ошибка соединения с сервером' };
    }
}

// Функция для аутентификации пользователя
async function authenticateUser(email, password) {
    try {
        const response = await fetch(`${AUTH_API_BASE_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'username': email,
                'password': password
            })
        });
        
        if (response.ok) {
            const tokenData = await response.json();
            showNotification('Вход выполнен успешно! Перенаправляем...', 'success');
            
            // Сохраняем токен в localStorage
            localStorage.setItem('access_token', tokenData.access_token);
            
            // Перенаправляем на главную страницу через 2 секунды
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
            
            // Обновляем состояние аутентификации на главной странице
            if (window.AudioStore && window.AudioStore.updateAuthState) {
                await window.AudioStore.updateAuthState();
            }
            
            return { success: true, data: tokenData };
            
        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Неверный email или пароль', 'error');
            return { success: false, error: errorData.detail };
        }
        
    } catch (error) {
        console.error('Ошибка при входе:', error);
        showNotification('Ошибка соединения с сервером', 'error');
        return { success: false, error: 'Ошибка соединения с сервером' };
    }
}

// Функция для проверки аутентификации
function isAuthenticated() {
    const token = localStorage.getItem('access_token');
    return !!token;
}

// Функция для выхода из системы
function logout() {
    localStorage.removeItem('access_token');
    showNotification('Вы успешно вышли из системы', 'success');
    
    // Перенаправляем на страницу входа
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 1500);
}

// Функция для получения токена
function getAccessToken() {
    return localStorage.getItem('access_token');
}

// Функция для инициализации формы регистрации
function initRegisterForm() {
    const registerForm = document.getElementById('register-form');
    
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const email = formData.get('email');
            const password = formData.get('password');
            
            // Валидация
            if (!email || !password) {
                showNotification('Пожалуйста, заполните все поля', 'error');
                return;
            }
            
            if (password.length < 6) {
                showNotification('Пароль должен содержать минимум 6 символов', 'error');
                return;
            }
            
            // Вызываем функцию регистрации
            await registerUser(email, password);
        });
    }
}

// Функция для инициализации формы входа
function initLoginForm() {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const email = formData.get('username'); // OAuth2 использует 'username' для email
            const password = formData.get('password');
            
            // Валидация
            if (!email || !password) {
                showNotification('Пожалуйста, заполните все поля', 'error');
                return;
            }
            
            // Вызываем функцию аутентификации
            await authenticateUser(email, password);
        });
    }
}

// Функция для инициализации кнопки выхода
function initLogoutButton() {
    const logoutBtn = document.querySelector('.logout-btn');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите выйти?')) {
                logout();
            }
        });
    }
}

// Функция для проверки аутентификации и обновления UI
function updateAuthUI() {
    const isAuth = isAuthenticated();
    
    // Если пользователь аутентифицирован и находится на страницах входа/регистрации
    if (isAuth && (window.location.pathname.includes('login.html') || window.location.pathname.includes('register.html'))) {
        showNotification('Вы уже авторизованы', 'info');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
    }
    
    // Если пользователь не аутентифицирован и находится на защищенных страницах
    if (!isAuth && window.location.pathname.includes('index.html')) {
        showNotification('Пожалуйста, войдите в систему', 'warning');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auth.js загружен!');
    
    // Инициализируем формы
    initRegisterForm();
    initLoginForm();
    initLogoutButton();
    
    // Проверяем аутентификацию и обновляем UI
    updateAuthUI();
});

// Экспортируем функции для использования в других модулях
window.Auth = {
    registerUser,
    authenticateUser,
    isAuthenticated,
    logout,
    getAccessToken,
    showNotification
};
