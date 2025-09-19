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
        // Используем общую функцию выхода из Auth модуля
        if (window.Auth && window.Auth.logout) {
            window.Auth.logout();
        } else {
            // Fallback на старую логику
            clearAdminAuth();
            redirectToLogin();
        }
    }
}

// Конфигурация API
const API_BASE_URL = 'http://localhost:8002'; // Порт каталога товаров
const AI_RECOMMENDER_URL = 'http://localhost:8005'; // Порт AI-рекомендатора
const PROMPTS_MANAGER_URL = 'http://localhost:8006'; // Порт менеджера промптов

// Элементы DOM
const productForm = document.getElementById('product-form');
const productsTable = document.getElementById('products-table');
const productsTbody = document.getElementById('products-tbody');
const productsContainer = document.getElementById('products-container');
const cancelEditBtn = document.getElementById('cancel-edit');

// AI Recommendations элементы
const generateBtn = document.getElementById('generate-btn');
const aiPrompt = document.getElementById('ai-prompt');
const aiModel = document.getElementById('ai-model');
const aiResult = document.getElementById('ai-result');
const aiResultContent = document.querySelector('.ai-result-content');

// Prompts Manager элементы
const promptsList = document.getElementById('prompts-list');

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
                <td class="description-cell" data-product-id="${product.id}">${escapeHtml(description)}</td>
                <td class="price">${product.price} ₽</td>
                <td class="actions">
                    <button class="edit" data-product-id="${product.id}">Редактировать</button>
                    <button class="delete" data-product-id="${product.id}">Удалить</button>
                    <button class="generate-description-btn" data-product-id="${product.id}">AI-описание</button>
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
    } else if (target.classList.contains('generate-description-btn')) {
        // Генерация AI-описания
        const productId = target.getAttribute('data-product-id');
        
        try {
            await generateDescriptionForProduct(productId, target);
        } catch (error) {
            showMessage(`Ошибка при генерации описания: ${error.message}`, 'error');
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
    
    // Обновляем UI навигации
    if (window.Navigation && window.Navigation.updateUI) {
        window.Navigation.updateUI();
    }
    
    // Загружаем данные и инициализируем форму
    fetchAndRenderProducts();
    initFormValidation();
    
    // Загружаем промпты
    fetchAndRenderPrompts();
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

// ===== AI RECOMMENDATIONS FUNCTIONALITY =====

// Функция для генерации AI-рекомендаций
async function generateAIRecommendations() {
    const prompt = aiPrompt.value.trim();
    const model = aiModel.value;
    
    if (!prompt) {
        showMessage('Пожалуйста, введите запрос для AI-рекомендаций', 'error');
        return;
    }
    
    // Показываем состояние загрузки
    setGenerateButtonLoading(true);
    hideAIResult();
    
    try {
        console.log('Отправляем запрос к AI-рекомендатору:', { prompt, model });
        
        const response = await fetch(`${AI_RECOMMENDER_URL}/api/v1/recommendations/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                model: model
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Получен ответ от AI-рекомендатора:', result);
        
        // Отображаем результат
        displayAIResult(result);
        showMessage('AI-рекомендации успешно сгенерированы!', 'success');
        
    } catch (error) {
        console.error('Ошибка при генерации AI-рекомендаций:', error);
        showMessage(`Ошибка при генерации рекомендаций: ${error.message}`, 'error');
        hideAIResult();
    } finally {
        setGenerateButtonLoading(false);
    }
}

// Функция для отображения результата AI-анализа
function displayAIResult(result) {
    const modelAlias = result.model_alias || result.model || 'Неизвестная модель';
    const totalBooks = result.total_books_analyzed || 'Не указано';
    const recommendations = result.recommendations || 'Результат не получен';
    
    aiResultContent.innerHTML = `
        <div class="ai-result-meta">
            <p><strong>Модель:</strong> ${modelAlias}</p>
            <p><strong>Проанализировано книг:</strong> ${totalBooks}</p>
        </div>
        <div class="ai-result-text">
            <h4>Рекомендации:</h4>
            <div class="recommendations-content">${formatRecommendations(recommendations)}</div>
        </div>
    `;
    
    aiResult.style.display = 'block';
    
    // Прокручиваем к результату
    aiResult.scrollIntoView({ behavior: 'smooth' });
}

// Функция для форматирования рекомендаций
function formatRecommendations(text) {
    // Простое форматирование текста - заменяем переносы строк на <br>
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

// Функция для скрытия результата AI-анализа
function hideAIResult() {
    aiResult.style.display = 'none';
    aiResultContent.innerHTML = '';
}

// Функция для управления состоянием кнопки генерации
function setGenerateButtonLoading(isLoading) {
    const btnText = generateBtn.querySelector('.btn-text');
    const btnLoading = generateBtn.querySelector('.btn-loading');
    
    if (isLoading) {
        generateBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
    } else {
        generateBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// Обработчик кнопки генерации AI-рекомендаций
generateBtn.addEventListener('click', generateAIRecommendations);

// Обработчик Enter в textarea для быстрой генерации
aiPrompt.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey) {
        e.preventDefault();
        generateAIRecommendations();
    }
});

// ===== AI DESCRIPTION GENERATION FUNCTIONALITY =====

// Функция для генерации описания конкретного товара
async function generateDescriptionForProduct(productId, buttonElement) {
    try {
        // Показываем состояние загрузки на кнопке
        setDescriptionButtonLoading(buttonElement, true);
        
        console.log(`Генерируем описание для товара ${productId}`);
        
        // Отправляем запрос к эндпоинту-оркестратору
        const response = await fetch(`${AI_RECOMMENDER_URL}/api/v1/recommendations/generate-description/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: 'gemini-pro' // Используем модель по умолчанию
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Получен ответ от AI-оркестратора:', result);
        
        // Обновляем ячейку описания в таблице
        updateDescriptionCell(productId, result.generated_description);
        
        showMessage(`Описание для товара ${productId} успешно сгенерировано!`, 'success');
        
    } catch (error) {
        console.error('Ошибка при генерации описания:', error);
        showMessage(`Ошибка при генерации описания: ${error.message}`, 'error');
    } finally {
        // Убираем состояние загрузки с кнопки
        setDescriptionButtonLoading(buttonElement, false);
    }
}

// Функция для управления состоянием кнопки генерации описания
function setDescriptionButtonLoading(buttonElement, isLoading) {
    if (isLoading) {
        buttonElement.disabled = true;
        buttonElement.textContent = 'Генерация...';
        buttonElement.style.opacity = '0.6';
    } else {
        buttonElement.disabled = false;
        buttonElement.textContent = 'AI-описание';
        buttonElement.style.opacity = '1';
    }
}

// Функция для обновления ячейки описания в таблице
function updateDescriptionCell(productId, newDescription) {
    // Находим ячейку описания для данного товара
    const descriptionCell = document.querySelector(`.description-cell[data-product-id="${productId}"]`);
    
    if (descriptionCell) {
        // Обновляем содержимое ячейки
        descriptionCell.innerHTML = escapeHtml(newDescription);
        
        // Добавляем визуальный эффект обновления
        descriptionCell.style.backgroundColor = '#d4edda';
        descriptionCell.style.transition = 'background-color 0.3s ease';
        
        // Убираем эффект через 2 секунды
        setTimeout(() => {
            descriptionCell.style.backgroundColor = '';
        }, 2000);
        
        console.log(`Ячейка описания для товара ${productId} обновлена`);
    } else {
        console.warn(`Ячейка описания для товара ${productId} не найдена`);
    }
}

// ===== PROMPTS MANAGER FUNCTIONALITY =====

// Функция для получения и отображения промптов
async function fetchAndRenderPrompts() {
    try {
        // Показываем индикатор загрузки
        promptsList.innerHTML = '<div class="loading">Загрузка промптов...</div>';
        
        const response = await fetch(`${PROMPTS_MANAGER_URL}/prompts`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const prompts = await response.json();
        
        // Очищаем контейнер
        promptsList.innerHTML = '';
        
        if (prompts.length === 0) {
            promptsList.innerHTML = '<div class="no-data">Промпты не найдены</div>';
            return;
        }
        
        // Создаем карточки для каждого промпта
        prompts.forEach(prompt => {
            const promptCard = createPromptCard(prompt);
            promptsList.appendChild(promptCard);
        });
        
    } catch (error) {
        console.error('Ошибка при загрузке промптов:', error);
        promptsList.innerHTML = `<div class="error">Ошибка при загрузке промптов: ${error.message}</div>`;
    }
}

// Функция для создания карточки промпта
function createPromptCard(prompt) {
    const card = document.createElement('div');
    card.className = 'prompt-card';
    card.innerHTML = `
        <div class="prompt-header">
            <h3>${escapeHtml(prompt.name)}</h3>
            <div class="prompt-status">
                <span class="status-badge ${prompt.is_active === 'true' ? 'active' : 'inactive'}">
                    ${prompt.is_active === 'true' ? 'Активен' : 'Неактивен'}
                </span>
            </div>
        </div>
        <div class="prompt-description">
            <p>${escapeHtml(prompt.description || 'Описание отсутствует')}</p>
        </div>
        <div class="prompt-content">
            <label for="prompt-content-${prompt.id}">Содержимое промпта:</label>
            <textarea 
                id="prompt-content-${prompt.id}" 
                class="prompt-textarea" 
                rows="8"
                placeholder="Введите содержимое промпта..."
            >${escapeHtml(prompt.content)}</textarea>
        </div>
        <div class="prompt-actions">
            <button class="save-prompt-btn" data-prompt-id="${prompt.id}">
                Сохранить
            </button>
            <button class="toggle-status-btn" data-prompt-id="${prompt.id}" data-current-status="${prompt.is_active}">
                ${prompt.is_active === 'true' ? 'Деактивировать' : 'Активировать'}
            </button>
        </div>
        <div class="prompt-meta">
            <small>ID: ${prompt.id} | Создан: ${new Date(prompt.created_at).toLocaleString('ru-RU')}</small>
        </div>
    `;
    
    // Добавляем обработчики событий
    const saveBtn = card.querySelector('.save-prompt-btn');
    const toggleBtn = card.querySelector('.toggle-status-btn');
    
    saveBtn.addEventListener('click', () => savePrompt(prompt.id, card));
    toggleBtn.addEventListener('click', () => togglePromptStatus(prompt.id, card));
    
    return card;
}

// Функция для сохранения промпта
async function savePrompt(promptId, cardElement) {
    const textarea = cardElement.querySelector('.prompt-textarea');
    const saveBtn = cardElement.querySelector('.save-prompt-btn');
    const newContent = textarea.value.trim();
    
    if (!newContent) {
        showMessage('Содержимое промпта не может быть пустым', 'error');
        return;
    }
    
    try {
        // Показываем состояние загрузки
        saveBtn.disabled = true;
        saveBtn.textContent = 'Сохранение...';
        
        const response = await fetch(`${PROMPTS_MANAGER_URL}/prompts/${promptId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: newContent
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const updatedPrompt = await response.json();
        showMessage(`Промпт "${updatedPrompt.name}" успешно сохранен!`, 'success');
        
        // Обновляем метаданные в карточке
        const metaElement = cardElement.querySelector('.prompt-meta');
        metaElement.innerHTML = `<small>ID: ${updatedPrompt.id} | Обновлен: ${new Date().toLocaleString('ru-RU')}</small>`;
        
    } catch (error) {
        console.error('Ошибка при сохранении промпта:', error);
        showMessage(`Ошибка при сохранении промпта: ${error.message}`, 'error');
    } finally {
        // Убираем состояние загрузки
        saveBtn.disabled = false;
        saveBtn.textContent = 'Сохранить';
    }
}

// Функция для переключения статуса промпта
async function togglePromptStatus(promptId, cardElement) {
    const toggleBtn = cardElement.querySelector('.toggle-status-btn');
    const currentStatus = toggleBtn.getAttribute('data-current-status');
    const newStatus = currentStatus === 'true' ? 'false' : 'true';
    
    try {
        // Показываем состояние загрузки
        toggleBtn.disabled = true;
        toggleBtn.textContent = 'Обновление...';
        
        const endpoint = newStatus === 'true' ? 'activate' : 'deactivate';
        const response = await fetch(`${PROMPTS_MANAGER_URL}/prompts/${promptId}/${endpoint}`, {
            method: 'PUT'
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        showMessage(result.message, 'success');
        
        // Обновляем UI
        const statusBadge = cardElement.querySelector('.status-badge');
        statusBadge.className = `status-badge ${newStatus === 'true' ? 'active' : 'inactive'}`;
        statusBadge.textContent = newStatus === 'true' ? 'Активен' : 'Неактивен';
        
        toggleBtn.setAttribute('data-current-status', newStatus);
        toggleBtn.textContent = newStatus === 'true' ? 'Деактивировать' : 'Активировать';
        
    } catch (error) {
        console.error('Ошибка при изменении статуса промпта:', error);
        showMessage(`Ошибка при изменении статуса: ${error.message}`, 'error');
    } finally {
        // Убираем состояние загрузки
        toggleBtn.disabled = false;
    }
}
