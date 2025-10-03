// Каталог аудиокниг
class CatalogManager {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 6; // По 6 товаров на странице
        this.currentFilters = {
            genre: '',
            author: '',
            price: '',
            sort: 'newest'
        };
        this.allBooks = [];
        this.filteredBooks = [];
        this.uniqueGenres = new Set();
        this.uniqueAuthors = new Set();
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadBooks();
        
        // Обновляем счетчик корзины с небольшой задержкой, чтобы DOM был готов
        setTimeout(() => {
            this.updateCartCount();
        }, 100);
    }
    
    // Загрузка книг с API
    async loadBooks() {
        try {
            this.showLoading();
            
            // Используем относительный путь
            const response = await fetch('/api/v1/audiobooks');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            // API возвращает данные в формате {"items": [...]}
            this.allBooks = data.items || data.audiobooks || data || [];
            
            // Убеждаемся, что allBooks является массивом
            if (!Array.isArray(this.allBooks)) {
                console.error('Ошибка: allBooks не является массивом:', this.allBooks);
                this.allBooks = [];
            }
            
            // Извлекаем уникальные жанры и авторов
            this.extractUniqueValues();
            
            // Заполняем фильтры
            this.populateFilters();
            
            this.applyFilters();
            this.renderBooks();
            this.renderPagination();
            
        } catch (error) {
            console.error('Ошибка загрузки каталога:', error);
            this.showError('Ошибка загрузки каталога. Проверьте подключение к серверу.');
        }
    }
    
    // Извлечение уникальных значений для фильтров
    extractUniqueValues() {
        this.uniqueGenres.clear();
        this.uniqueAuthors.clear();
        
        this.allBooks.forEach(book => {
            // Жанры могут быть в поле genre или в categories
            if (book.genre) {
                this.uniqueGenres.add(book.genre);
            } else if (book.categories && book.categories.length > 0) {
                book.categories.forEach(category => {
                    this.uniqueGenres.add(category.name);
                });
            }
            
            if (book.author && book.author.name) {
                this.uniqueAuthors.add(book.author.name);
            }
        });
    }
    
    // Заполнение фильтров уникальными значениями
    populateFilters() {
        // Заполняем жанры
        const genreSelect = document.getElementById('genre-filter');
        const currentGenre = genreSelect.value;
        genreSelect.innerHTML = '<option value="">Все жанры</option>';
        
        Array.from(this.uniqueGenres).sort().forEach(genre => {
            const option = document.createElement('option');
            option.value = genre;
            option.textContent = this.formatGenreName(genre);
            genreSelect.appendChild(option);
        });
        
        if (currentGenre && this.uniqueGenres.has(currentGenre)) {
            genreSelect.value = currentGenre;
        }
        
        // Заполняем авторов
        const authorSelect = document.getElementById('author-filter');
        const currentAuthor = authorSelect.value;
        authorSelect.innerHTML = '<option value="">Все авторы</option>';
        
        Array.from(this.uniqueAuthors).sort().forEach(author => {
            const option = document.createElement('option');
            option.value = author;
            option.textContent = author;
            authorSelect.appendChild(option);
        });
        
        if (currentAuthor && this.uniqueAuthors.has(currentAuthor)) {
            authorSelect.value = currentAuthor;
        }
    }
    
    // Форматирование названия жанра
    formatGenreName(genre) {
        const genreNames = {
            'fiction': 'Художественная литература',
            'non-fiction': 'Нонфикшн',
            'psychology': 'Психология',
            'business': 'Бизнес',
            'finance': 'Финансы',
            'history': 'История',
            'science': 'Наука',
            'self-help': 'Саморазвитие'
        };
        return genreNames[genre] || genre;
    }
    
    // Настройка обработчиков событий
    setupEventListeners() {
        // Фильтры
        document.getElementById('genre-filter').addEventListener('change', (e) => {
            this.currentFilters.genre = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('author-filter').addEventListener('change', (e) => {
            this.currentFilters.author = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('price-filter').addEventListener('change', (e) => {
            this.currentFilters.price = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('sort-filter').addEventListener('change', (e) => {
            this.currentFilters.sort = e.target.value;
            this.applyFilters();
        });
        
        // Сброс фильтров
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Обработчик для кнопок "В корзину" (делегирование событий)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart-btn')) {
                e.preventDefault(); // Предотвращаем переход по ссылке
                e.stopPropagation(); // Останавливаем всплытие события
                
                const bookId = e.target.dataset.bookId;
                const bookTitle = e.target.dataset.bookTitle;
                const bookPrice = parseFloat(e.target.dataset.bookPrice);
                
                console.log('Добавление в корзину из каталога:', { bookId, bookTitle, bookPrice });
                
                // Вызываем функцию добавления в корзину
                this.addToCart(e.target);
            }
        });
    }
    
    // Применение фильтров
    applyFilters() {
        this.filteredBooks = [...this.allBooks];
        
        // Фильтр по жанру
        if (this.currentFilters.genre) {
            this.filteredBooks = this.filteredBooks.filter(book => {
                // Проверяем поле genre
                if (book.genre === this.currentFilters.genre) {
                    return true;
                }
                // Проверяем categories
                if (book.categories && book.categories.length > 0) {
                    return book.categories.some(category => 
                        category.name === this.currentFilters.genre
                    );
                }
                return false;
            });
        }
        
        // Фильтр по автору
        if (this.currentFilters.author) {
            this.filteredBooks = this.filteredBooks.filter(book => 
                book.author && book.author.name === this.currentFilters.author
            );
        }
        
        // Фильтр по цене
        if (this.currentFilters.price) {
            const [min, max] = this.currentFilters.price.split('-').map(p => 
                p === '+' ? Infinity : parseInt(p)
            );
            this.filteredBooks = this.filteredBooks.filter(book => {
                if (max === Infinity) return book.price >= min;
                return book.price >= min && book.price <= max;
            });
        }
        
        // Сортировка
        this.sortBooks();
        
        this.currentPage = 1;
        this.renderBooks();
        this.renderPagination();
    }
    
    // Сортировка книг
    sortBooks() {
        switch (this.currentFilters.sort) {
            case 'newest':
                this.filteredBooks.sort((a, b) => b.id - a.id);
                break;
            case 'oldest':
                this.filteredBooks.sort((a, b) => a.id - b.id);
                break;
            case 'price-low':
                this.filteredBooks.sort((a, b) => a.price - b.price);
                break;
            case 'price-high':
                this.filteredBooks.sort((a, b) => b.price - a.price);
                break;
            case 'rating':
                this.filteredBooks.sort((a, b) => (b.rating || 0) - (a.rating || 0));
                break;
            case 'popular':
                // Для демонстрации используем ID как популярность
                this.filteredBooks.sort((a, b) => b.id - a.id);
                break;
        }
    }
    
    // Сброс фильтров
    clearFilters() {
        document.getElementById('genre-filter').value = '';
        document.getElementById('author-filter').value = '';
        document.getElementById('price-filter').value = '';
        document.getElementById('sort-filter').value = 'newest';
        
        this.currentFilters = {
            genre: '',
            author: '',
            price: '',
            sort: 'newest'
        };
        
        this.applyFilters();
    }
    
    // Добавление товара в корзину
    addToCart(button) {
        try {
            const bookId = button.dataset.bookId;
            const bookTitle = button.dataset.bookTitle;
            const bookPrice = parseFloat(button.dataset.bookPrice);
            
            console.log('addToCart вызвана с параметрами:', { bookId, bookTitle, bookPrice });
            
            // Получаем текущую корзину из localStorage
            let cart = JSON.parse(localStorage.getItem('cart')) || [];
            console.log('Текущая корзина до добавления:', cart);
            
            // Проверяем, есть ли уже такой товар в корзине
            const existingItem = cart.find(item => item.id === bookId);
            
            if (existingItem) {
                existingItem.quantity += 1;
                console.log('Увеличиваем количество для существующего товара');
            } else {
                cart.push({
                    id: bookId,
                    title: bookTitle,
                    price: bookPrice,
                    quantity: 1
                });
                console.log('Добавляем новый товар в корзину');
            }
            
            // Сохраняем обновленную корзину
            localStorage.setItem('cart', JSON.stringify(cart));
            console.log('Корзина сохранена в localStorage:', cart);
            
            // Обновляем счетчик корзины
            this.updateCartCount();
            
            // Также вызываем глобальное обновление
            if (window.updateGlobalCartCount) {
                window.updateGlobalCartCount();
            }
            
            // Вызываем обновление из navigation.js
            if (window.Navigation && window.Navigation.updateCartCount) {
                window.Navigation.updateCartCount();
            }
            
            // Показываем уведомление
            this.showCartNotification(bookTitle);
            
        } catch (error) {
            console.error('Ошибка в addToCart:', error);
            alert('Ошибка при добавлении товара в корзину: ' + error.message);
        }
    }
    
    // Обновление счетчика корзины
    updateCartCount() {
        try {
            const cart = JSON.parse(localStorage.getItem('cart')) || [];
            const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
            
            console.log('Обновляем счетчик корзины. Товаров в корзине:', totalItems);
            
            // Пробуем найти элемент разными способами
            let cartCountElement = document.getElementById('cart-count');
            
            if (!cartCountElement) {
                // Пробуем найти по селектору
                cartCountElement = document.querySelector('#cart-count');
            }
            
            if (!cartCountElement) {
                // Пробуем найти среди всех span элементов
                const allSpans = document.querySelectorAll('span');
                for (let span of allSpans) {
                    if (span.id === 'cart-count') {
                        cartCountElement = span;
                        break;
                    }
                }
            }
            
            if (!cartCountElement) {
                // Пробуем найти в навигации
                const navMenu = document.querySelector('.nav-menu');
                if (navMenu) {
                    cartCountElement = navMenu.querySelector('#cart-count');
                }
            }
            
            if (cartCountElement) {
                cartCountElement.textContent = totalItems;
                console.log('Счетчик корзины обновлен:', totalItems);
            } else {
                console.warn('Элемент cart-count не найден всеми способами, попробуем еще раз через 500мс');
                console.log('DOM состояние:', document.readyState);
                console.log('Все span элементы:', document.querySelectorAll('span').length);
                console.log('Все элементы с ID:', document.querySelectorAll('[id]').length);
                
                // Попробуем еще раз через 500мс, если элемент не найден
                setTimeout(() => {
                    const retryElement = document.getElementById('cart-count');
                    if (retryElement) {
                        retryElement.textContent = totalItems;
                        console.log('Счетчик корзины обновлен при повторной попытке:', totalItems);
                    } else {
                        console.error('Элемент cart-count так и не найден после повторной попытки');
                        console.log('Попробуем создать элемент программно...');
                        this.createCartCountElement(totalItems);
                    }
                }, 500);
            }
        } catch (error) {
            console.error('Ошибка при обновлении счетчика корзины:', error);
        }
    }
    
    // Создание элемента cart-count программно, если он не найден
    createCartCountElement(totalItems) {
        try {
            const navMenu = document.querySelector('.nav-menu');
            if (navMenu) {
                // Ищем ссылку на корзину
                const cartLink = navMenu.querySelector('a[href*="cart"]');
                if (cartLink) {
                    // Создаем span элемент
                    const cartCountSpan = document.createElement('span');
                    cartCountSpan.id = 'cart-count';
                    cartCountSpan.textContent = totalItems;
                    
                    // Вставляем в ссылку на корзину
                    cartLink.innerHTML = cartLink.innerHTML.replace(/\(\d+\)/, `(${totalItems})`);
                    if (!cartLink.innerHTML.includes('(')) {
                        cartLink.innerHTML += ` (${totalItems})`;
                    }
                    
                    console.log('Элемент cart-count создан программно:', totalItems);
                }
            }
        } catch (error) {
            console.error('Ошибка при создании элемента cart-count:', error);
        }
    }
    
    // Показ уведомления о добавлении в корзину
    showCartNotification(bookTitle) {
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
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // Отображение книг
    renderBooks() {
        const grid = document.getElementById('catalog-grid');
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const booksToShow = this.filteredBooks.slice(startIndex, endIndex);
        
        if (booksToShow.length === 0) {
            grid.innerHTML = '<div class="no-results">Книги не найдены</div>';
            return;
        }
        
        grid.innerHTML = booksToShow.map(book => this.createBookCard(book)).join('');
    }
    
    // Создание карточки книги
    createBookCard(book) {
        const coverImage = book.cover_image_url || 'assets/images/placeholder.svg';
        const authorName = (book.author && book.author.name) || 'Неизвестный автор';
        const rating = book.rating || 0;
        
        return `
            <a href="book-detail.html?id=${book.id}" class="book-card-link" data-book-id="${book.id}">
                <div class="book-card">
                    <div class="book-image-wrapper">
                        <div class="book-image">
                            <img src="${coverImage}" alt="${book.title}" onerror="this.src='assets/images/placeholder.svg'">
                        </div>
                    </div>
                    <div class="book-content">
                        <div class="book-author">${authorName}</div>
                        <div class="book-title">${book.title}</div>
                        <div class="book-rating">
                            <span class="rating-stars">★</span>
                            <span class="rating-value">${rating.toFixed(1)}</span>
                        </div>
                        <div class="book-price">${book.price} ₽</div>
                        <button class="add-to-cart-btn" data-book-id="${book.id}" data-book-title="${book.title}" data-book-price="${book.price}">
                            В корзину
                        </button>
                    </div>
                </div>
            </a>
        `;
    }
    
    // Отображение пагинации
    renderPagination() {
        const pagination = document.getElementById('pagination');
        const totalPages = Math.ceil(this.filteredBooks.length / this.itemsPerPage);
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let paginationHTML = '<div class="pagination-wrapper">';
        
        // Предыдущая страница
        if (this.currentPage > 1) {
            paginationHTML += `<button class="pagination-btn prev-btn" data-page="${this.currentPage - 1}">‹ Предыдущая</button>`;
        }
        
        // Номера страниц
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);
        
        if (startPage > 1) {
            paginationHTML += `<button class="pagination-btn" data-page="1">1</button>`;
            if (startPage > 2) {
                paginationHTML += '<span class="pagination-dots">...</span>';
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const isActive = i === this.currentPage ? 'active' : '';
            paginationHTML += `<button class="pagination-btn ${isActive}" data-page="${i}">${i}</button>`;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += '<span class="pagination-dots">...</span>';
            }
            paginationHTML += `<button class="pagination-btn" data-page="${totalPages}">${totalPages}</button>`;
        }
        
        // Следующая страница
        if (this.currentPage < totalPages) {
            paginationHTML += `<button class="pagination-btn next-btn" data-page="${this.currentPage + 1}">Следующая ›</button>`;
        }
        
        paginationHTML += '</div>';
        pagination.innerHTML = paginationHTML;
        
        // Обработчики для кнопок пагинации
        pagination.querySelectorAll('.pagination-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.currentPage = parseInt(e.target.dataset.page);
                this.renderBooks();
                this.renderPagination();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });
    }
    
    // Показать состояние загрузки
    showLoading() {
        const grid = document.getElementById('catalog-grid');
        grid.innerHTML = '<div class="loading-message">Загрузка каталога...</div>';
    }
    
    // Показать ошибку
    showError(message) {
        const grid = document.getElementById('catalog-grid');
        grid.innerHTML = `<div class="error-message">${message}</div>`;
    }
}

// Глобальная функция для обновления счетчика корзины
window.updateGlobalCartCount = function() {
    try {
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
            console.log('Глобальное обновление счетчика корзины:', totalItems);
        } else {
            console.warn('Элемент cart-count не найден для глобального обновления');
        }
        
        // Также вызываем обновление из navigation.js
        if (window.Navigation && window.Navigation.updateCartCount) {
            window.Navigation.updateCartCount();
        }
    } catch (error) {
        console.error('Ошибка при глобальном обновлении счетчика корзины:', error);
    }
};

// Инициализация каталога при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new CatalogManager();
    
    // Обновляем счетчик корзины при загрузке страницы
    setTimeout(() => {
        window.updateGlobalCartCount();
    }, 200);
});
