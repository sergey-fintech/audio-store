// Поиск аудиокниг
class SearchManager {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 6;
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
        this.searchQuery = '';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadBooks();
        this.updateCartCount();
        this.handleSearchFromURL();
    }
    
    // Обработка поискового запроса из URL
    handleSearchFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');
        if (query) {
            this.searchQuery = decodeURIComponent(query);
            document.getElementById('search-input').value = this.searchQuery;
            this.performSearch();
        } else {
            this.loadBooks();
        }
    }
    
    // Загрузка книг с API
    async loadBooks() {
        try {
            this.showLoading();
            
            const response = await fetch('http://localhost:8002/api/v1/audiobooks');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
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
    
    // Выполнение поиска
    async performSearch() {
        if (!this.searchQuery.trim()) {
            this.loadBooks();
            return;
        }
        
        try {
            this.showLoading();
            
            // Используем API поиска
            const searchParams = new URLSearchParams();
            searchParams.append('q', this.searchQuery);
            searchParams.append('limit', '100');
            
            const response = await fetch(`http://localhost:8002/api/v1/search?${searchParams.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.allBooks = data || [];
            
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
            console.error('Ошибка поиска:', error);
            console.log('Переключаемся на локальный поиск...');
            // Если поиск не работает, загружаем все книги и фильтруем локально
            if (this.allBooks.length === 0) {
                await this.loadBooks();
            }
            this.filterBooksBySearch();
        }
    }
    
    // Локальная фильтрация по поисковому запросу
    filterBooksBySearch() {
        if (!this.searchQuery.trim()) {
            this.applyFilters();
            return;
        }
        
        const query = this.searchQuery.toLowerCase().trim();
        this.filteredBooks = this.allBooks.filter(book => {
            const title = (book.title || '').toLowerCase();
            const author = (book.author?.name || '').toLowerCase();
            const description = (book.description || '').toLowerCase();
            
            return title.includes(query) || 
                   author.includes(query) || 
                   description.includes(query);
        });
        
        // Применяем дополнительные фильтры
        this.applyFiltersWithoutSearch();
        this.currentPage = 1;
        this.renderBooks();
        this.renderPagination();
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
        // Поиск по вводу
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                // Добавляем задержку для поиска
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.performSearch();
                }, 500);
            });
            
            // Поиск по Enter
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.searchQuery = e.target.value;
                    this.performSearch();
                }
            });
        }
        
        // Кнопка поиска
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    this.searchQuery = searchInput.value;
                    this.performSearch();
                }
            });
        }
        
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
                this.addToCart(e.target);
            }
        });
    }
    
    // Применение фильтров
    applyFilters() {
        this.filteredBooks = [...this.allBooks];
        this.applyFiltersWithoutSearch();
    }
    
    // Применение фильтров без сброса поиска
    applyFiltersWithoutSearch() {
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
        const bookId = button.dataset.bookId;
        const bookTitle = button.dataset.bookTitle;
        const bookPrice = parseFloat(button.dataset.bookPrice);
        
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
        this.updateCartCount();
        
        // Показываем уведомление
        this.showCartNotification(bookTitle);
    }
    
    // Обновление счетчика корзины
    updateCartCount() {
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
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
            if (this.searchQuery) {
                grid.innerHTML = `<div class="no-results">По запросу "${this.searchQuery}" ничего не найдено</div>`;
            } else {
                grid.innerHTML = '<div class="no-results">Книги не найдены</div>';
            }
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
            <div class="book-card" data-book-id="${book.id}">
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

// Инициализация поиска при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new SearchManager();
});
