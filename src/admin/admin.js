// Проверка авторизации администратора
function checkAdminAuth() {
    const token = localStorage.getItem('admin_token');
    const username = localStorage.getItem('admin_username');
    const loginTime = localStorage.getItem('admin_login_time');
    
    // Проверяем наличие токена
    if (!token || !username || !loginTime) {
        redirectToLogin();
        return false;
    }
    
    // Проверяем, не истек ли токен (24 часа)
    const currentTime = Date.now();
    const tokenAge = currentTime - parseInt(loginTime);
    const maxAge = 24 * 60 * 60 * 1000; // 24 часа в миллисекундах
    
    if (tokenAge > maxAge) {
        // Токен истек, очищаем данные и перенаправляем
        clearAdminAuth();
        redirectToLogin();
        return false;
    }
    
    // Обновляем имя пользователя в интерфейсе
    const usernameElement = document.getElementById('admin-username');
    if (usernameElement) {
        usernameElement.textContent = username;
    }
    
    return true;
}

// Очистка данных авторизации
function clearAdminAuth() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    localStorage.removeItem('admin_login_time');
}

// Перенаправление на страницу входа
function redirectToLogin() {
    window.location.href = 'login.html';
}

// Выход из системы
function logoutAdmin() {
    if (confirm('Вы уверены, что хотите выйти из системы?')) {
        clearAdminAuth();
        redirectToLogin();
    }
}

// Конфигурация API
const API_BASE_URL = 'http://localhost:8002'; // Порт каталога товаров

// Элементы DOM
const productForm = document.getElementById('product-form');
const productsTable = document.getElementById('products-table');
const productsTbody = document.getElementById('products-tbody');
const productsContainer = document.getElementById('products-container');
const cancelEditBtn = document.getElementById('cancel-edit');

// Состояние приложения
let isEditing = false;
let editingProductId = null;

// Утилиты для работы с уведомлениями
function showMessage(message, type = 'success') {
    // Удаляем существующие уведомления
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Вставляем уведомление после заголовка
    const h1 = document.querySelector('h1');
    h1.parentNode.insertBefore(messageDiv, h1.nextSibling);
    
    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

// Функция для получения и отображения товаров
async function fetchAndRenderProducts() {
    try {
        // Показываем индикатор загрузки
        productsContainer.innerHTML = '<div class="loading">Загрузка товаров...</div>';
        productsTable.style.display = 'none';
        
        const response = await fetch(`${API_BASE_URL}/api/v1/audiobooks`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const products = await response.json();
        
        // Скрываем индикатор загрузки и показываем таблицу
        productsContainer.innerHTML = '';
        productsTable.style.display = 'table';
        
        // Очищаем таблицу
        productsTbody.innerHTML = '';
        
        if (products.length === 0) {
            productsTbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #666;">Товары не найдены</td></tr>';
            return;
        }
        
        // Заполняем таблицу товарами
        products.forEach(product => {
            const row = document.createElement('tr');
            const authorName = product.author ? product.author.name : `ID: ${product.author_id}`;
            const description = product.description || 'Описание отсутствует';
            row.innerHTML = `
                <td>${product.id}</td>
                <td>${escapeHtml(product.title)}</td>
                <td>${escapeHtml(authorName)}</td>
                <td>${escapeHtml(description)}</td>
                <td class="price">${product.price} ₽</td>
                <td class="actions">
                    <button class="edit" data-product-id="${product.id}">Редактировать</button>
                    <button class="delete" data-product-id="${product.id}">Удалить</button>
                </td>
            `;
            productsTbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Ошибка при загрузке товаров:', error);
        productsContainer.innerHTML = `<div class="error">Ошибка при загрузке товаров: ${error.message}</div>`;
    }
}

// Функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Функция для получения данных товара по ID
async function fetchProductById(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/audiobooks/${productId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при получении товара:', error);
        throw error;
    }
}

// Функция для создания нового товара
async function createProduct(productData) {
    try {
        console.log('Отправляем данные на сервер:', productData);
        
        let url, body;
        
        if (productData.author_name) {
            // Если указано имя автора, используем comprehensive endpoint
            const params = new URLSearchParams({
                title: productData.title,
                author_name: productData.author_name,
                price: productData.price.toString()
            });
            
            if (productData.description) {
                params.append('description', productData.description);
            }
            if (productData.cover_image_url) {
                params.append('cover_image_url', productData.cover_image_url);
            }
            
            url = `${API_BASE_URL}/catalog/audiobooks/comprehensive?${params.toString()}`;
            body = null;
        } else {
            // Если указан ID автора, используем обычный endpoint
            url = `${API_BASE_URL}/api/v1/audiobooks`;
            body = productData;
        }
        
        console.log('URL:', url);
        console.log('Body:', body);
        
        const fetchOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (body) {
            fetchOptions.body = JSON.stringify(body);
        }
        
        const response = await fetch(url, fetchOptions);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Ошибка сервера:', errorText);
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при создании товара:', error);
        throw error;
    }
}

// Функция для обновления товара
async function updateProduct(productId, productData) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/audiobooks/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при обновлении товара:', error);
        throw error;
    }
}

// Функция для удаления товара
async function deleteProduct(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/audiobooks/${productId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return true;
    } catch (error) {
        console.error('Ошибка при удалении товара:', error);
        throw error;
    }
}

// Функция для заполнения формы данными товара
function fillFormWithProduct(product) {
    console.log('Заполнение формы данными товара:', product);
    
    document.getElementById('title').value = product.title;
    
    // Проверяем и устанавливаем ID автора
    const authorIdField = document.getElementById('author_id');
    if (authorIdField) {
        // ID автора может быть в product.author_id или в product.author.id
        const authorId = product.author_id || (product.author && product.author.id);
        console.log('ID автора из товара:', authorId);
        authorIdField.value = authorId || '';
    } else {
        console.error('Поле author_id не найдено в форме');
    }
    
    document.getElementById('description').value = product.description || '';
    document.getElementById('price').value = product.price;
    document.getElementById('cover_image_url').value = product.cover_image_url || '';
    
    // Заполняем имя автора, если оно доступно
    const authorNameField = document.getElementById('author_name');
    if (authorNameField && product.author && product.author.name) {
        authorNameField.value = product.author.name;
    } else {
        authorNameField.value = '';
    }
}

// Функция для очистки формы
function clearForm() {
    productForm.reset();
    isEditing = false;
    editingProductId = null;
    productForm.removeAttribute('data-editing-id');
    cancelEditBtn.style.display = 'none';
    // Очищаем поле author_name, так как оно может не сбрасываться через reset()
    document.getElementById('author_name').value = '';
}

// Функция для получения данных из формы
function getFormData() {
    const authorName = document.getElementById('author_name').value.trim();
    const authorId = document.getElementById('author_id').value;
    
    const data = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        price: parseFloat(document.getElementById('price').value),
        cover_image_url: document.getElementById('cover_image_url').value || null
    };
    
    // Приоритет: если указано имя автора, используем его для автоматического создания
    if (authorName) {
        data.author_name = authorName;
    } else if (authorId) {
        data.author_id = parseInt(authorId);
    } else {
        // Если ни имя, ни ID не указаны, показываем ошибку
        throw new Error('Необходимо указать либо ID автора, либо имя автора');
    }
    
    return data;
}

// Обработчик отправки формы
productForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    try {
        // Валидация формы
        const authorName = document.getElementById('author_name').value.trim();
        const authorId = document.getElementById('author_id').value;
        
        if (!authorName && !authorId) {
            showMessage('Необходимо указать либо ID автора, либо имя автора', 'error');
            return;
        }
        
        const formData = getFormData();
        
        if (isEditing) {
            // Обновляем существующий товар
            await updateProduct(editingProductId, formData);
            showMessage('Товар успешно обновлен!');
        } else {
            // Создаем новый товар
            await createProduct(formData);
            showMessage('Товар успешно создан!');
        }
        
        // Очищаем форму и обновляем список товаров
        clearForm();
        await fetchAndRenderProducts();
        
    } catch (error) {
        showMessage(`Ошибка: ${error.message}`, 'error');
    }
});

// Обработчик кнопки отмены редактирования
cancelEditBtn.addEventListener('click', function() {
    clearForm();
});

// Обработчик событий таблицы товаров (делегирование)
productsTable.addEventListener('click', async function(e) {
    const target = e.target;
    
    if (target.classList.contains('delete')) {
        // Удаление товара
        const productId = target.getAttribute('data-product-id');
        
        if (confirm('Вы уверены, что хотите удалить этот товар?')) {
            try {
                await deleteProduct(productId);
                showMessage('Товар успешно удален!');
                await fetchAndRenderProducts();
            } catch (error) {
                showMessage(`Ошибка при удалении: ${error.message}`, 'error');
            }
        }
    } else if (target.classList.contains('edit')) {
        // Редактирование товара
        const productId = target.getAttribute('data-product-id');
        
        try {
            const product = await fetchProductById(productId);
            console.log('Полученный товар для редактирования:', product);
            
            // Заполняем форму данными товара
            fillFormWithProduct(product);
            
            // Устанавливаем режим редактирования
            isEditing = true;
            editingProductId = productId;
            productForm.setAttribute('data-editing-id', productId);
            cancelEditBtn.style.display = 'inline-block';
            
            // Прокручиваем к форме
            productForm.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            showMessage(`Ошибка при загрузке товара: ${error.message}`, 'error');
        }
    }
});

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем авторизацию администратора
    if (!checkAdminAuth()) {
        return; // Если не авторизован, функция checkAdminAuth уже перенаправит на login.html
    }
    
    // Инициализируем обработчик кнопки выхода
    const logoutBtn = document.getElementById('admin-logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logoutAdmin);
    }
    
    // Загружаем данные и инициализируем форму
    fetchAndRenderProducts();
    initFormValidation();
});

// Функция для инициализации валидации формы
function initFormValidation() {
    const authorNameField = document.getElementById('author_name');
    const authorIdField = document.getElementById('author_id');
    
    // Функция для обновления подсказки
    function updateHint() {
        const authorName = authorNameField.value.trim();
        const authorId = authorIdField.value;
        
        if (authorName && !authorId) {
            // Если указано только имя автора
            authorIdField.style.borderColor = '#28a745';
            authorIdField.title = 'Автор будет создан автоматически';
        } else if (!authorName && !authorId) {
            // Если ничего не указано
            authorIdField.style.borderColor = '#dc3545';
            authorIdField.title = 'Необходимо указать ID автора или имя автора';
        } else {
            // Если указан ID автора
            authorIdField.style.borderColor = '';
            authorIdField.title = '';
        }
    }
    
    // Добавляем обработчики событий
    authorNameField.addEventListener('input', updateHint);
    authorIdField.addEventListener('input', updateHint);
    
    // Инициализируем подсказку
    updateHint();
}

// Обработка ошибок сети
window.addEventListener('online', function() {
    showMessage('Соединение восстановлено', 'success');
    fetchAndRenderProducts();
});

window.addEventListener('offline', function() {
    showMessage('Отсутствует подключение к интернету', 'error');
});
