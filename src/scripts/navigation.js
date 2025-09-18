// Скрипт для управления навигацией в зависимости от прав пользователя

// Функция для обновления навигации
function updateNavigation() {
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;
    
    // Проверяем, является ли пользователь админом
    const isAdminUser = window.Auth && window.Auth.isAdmin();
    
    // Проверяем, находимся ли мы в админ-панели
    const isInAdminPanel = window.location.pathname.includes('/admin/') || 
                          window.location.pathname.includes('admin.html');
    
    // Находим или создаем ссылку на админ-панель
    let adminLink = navMenu.querySelector('a[href*="admin"]');
    
    if (isAdminUser && !isInAdminPanel) {
        // Если пользователь админ, НЕ находится в админ-панели и ссылки нет - добавляем
        if (!adminLink) {
            adminLink = document.createElement('a');
            adminLink.href = 'admin/admin.html';
            adminLink.textContent = 'Админ-панель';
            adminLink.style.color = '#ff6b35';
            adminLink.style.fontWeight = 'bold';
            
            // Добавляем ссылку в конец навигации
            navMenu.appendChild(adminLink);
        }
    } else {
        // Если пользователь не админ ИЛИ находится в админ-панели - удаляем ссылку
        if (adminLink) {
            adminLink.remove();
        }
    }
}

// Функция для обновления состояния кнопок входа/выхода
function updateAuthButtons() {
    const loginBtn = document.querySelector('.login-btn');
    const logoutBtn = document.querySelector('.logout-btn');
    const profile = document.querySelector('.profile');
    
    const isAuth = window.Auth && window.Auth.isAuthenticated();
    const isAdminUser = window.Auth && window.Auth.isAdmin();
    
    if (isAuth) {
        // Пользователь авторизован
        if (loginBtn) {
            loginBtn.style.display = 'none';
            loginBtn.style.visibility = 'hidden';
        }
        if (logoutBtn) {
            logoutBtn.style.display = 'block';
            logoutBtn.style.visibility = 'visible';
        }
        if (profile) {
            profile.style.display = 'flex';
            profile.style.visibility = 'visible';
        }
        
        // Обновляем имя пользователя
        const profileName = document.querySelector('.profile-name');
        if (profileName) {
            if (isAdminUser) {
                profileName.textContent = 'Администратор';
            } else {
                // Показываем email пользователя
                const userEmail = localStorage.getItem('user_email');
                profileName.textContent = userEmail || 'Пользователь';
            }
        }
    } else {
        // Пользователь не авторизован
        if (loginBtn) {
            loginBtn.style.display = 'block';
            loginBtn.style.visibility = 'visible';
        }
        if (logoutBtn) {
            logoutBtn.style.display = 'none';
            logoutBtn.style.visibility = 'hidden';
        }
        if (profile) {
            profile.style.display = 'none';
            profile.style.visibility = 'hidden';
        }
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
            console.log('Navigation: счетчик корзины обновлен:', totalItems);
        } else {
            console.warn('Navigation: элемент cart-count не найден');
        }
    } catch (error) {
        console.error('Navigation: ошибка при обновлении счетчика корзины:', error);
    }
}

// Функция для полного обновления UI
function updateUI() {
    updateNavigation();
    updateAuthButtons();
    updateCartCount();
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Ждем загрузки Auth модуля
    setTimeout(() => {
        updateUI();
    }, 100);
});

// Экспортируем функции
window.Navigation = {
    updateNavigation,
    updateAuthButtons,
    updateUI,
    updateCartCount
};
