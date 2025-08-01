// Основной JavaScript файл для AudioStore

// Глобальные переменные
let cartItems = JSON.parse(localStorage.getItem('cartItems')) || [];

// Ждем загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('AudioStore загружен!');
    
    // Инициализация всех компонентов
    initNavigation();
    initSearch();
    initBookCards();
    initLogout();
});

// Функция для инициализации навигации
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
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

// Функция для добавления в корзину
function addToCart(bookTitle, bookPrice) {
    cartItems.push({
        title: bookTitle,
        price: bookPrice
    });
    localStorage.setItem('cartItems', JSON.stringify(cartItems));
    
    // Показываем уведомление
    showNotification('Книга добавлена в корзину!');
}

// Функция для инициализации поиска
function initSearch() {
    const searchBtn = document.querySelector('.search-btn');
    
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const searchTerm = prompt('Введите название книги или автора:');
            if (searchTerm) {
                performSearch(searchTerm);
            }
        });
    }
    
    function performSearch(term) {
        // Здесь будет логика поиска
        console.log(`Поиск: ${term}`);
        alert(`Поиск по запросу "${term}" будет реализован позже`);
    }
}

// Функция для инициализации карточек книг
function initBookCards() {
    const addToCartButtons = document.querySelectorAll('.btn-secondary');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookCard = this.closest('.book-card');
            const bookTitle = bookCard.querySelector('h3').textContent;
            const bookPrice = parseInt(bookCard.querySelector('.price').textContent.replace('₽', ''));
            
            addToCart(bookTitle, bookPrice);
        });
    });
}

// Функция для инициализации кнопки выхода
function initLogout() {
    const logoutBtn = document.querySelector('.logout-btn');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите выйти?')) {
                // Очищаем данные пользователя
                localStorage.removeItem('cartItems');
                cartItems = [];
                
                // Показываем уведомление
                showNotification('Вы успешно вышли из системы');
                
                // Здесь можно добавить редирект на страницу входа
                // window.location.href = '/login';
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

// Экспортируем функции для использования в других модулях
window.AudioStore = {
    addToCart,
    smoothScrollTo,
    loadBooks,
    showNotification,
    initLogout
}; 