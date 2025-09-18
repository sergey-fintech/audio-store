@echo off
@chcp 1251
chcp 65001 >nul
title Audio Store - Запуск сервисов

echo 🎵 Запуск Audio Store...
echo ==================================================

:: Проверяем, что мы в корневой директории проекта
cd /d "%~dp0"

echo Текущая директория: %CD%

:: Проверяем наличие необходимых папок
if not exist "services\auth" (
    echo ОШИБКА: Папка services\auth не найдена!
    pause
    exit /b 1
)

if not exist "services\catalog" (
    echo ОШИБКА: Папка services\catalog не найдена!
    pause
    exit /b 1
)

if not exist "services\cart" (
    echo ОШИБКА: Папка services\cart не найдена!
    pause
    exit /b 1
)

if not exist "services\orders" (
    echo ОШИБКА: Папка services\orders не найдена!
    pause
    exit /b 1
)

if not exist "services\recommender" (
    echo ОШИБКА: Папка services\recommender не найдена!
    pause
    exit /b 1
)

if not exist "src" (
    echo ОШИБКА: Папка src не найдена!
    pause
    exit /b 1
)

:: Останавливаем процессы на портах 8000, 8001, 8002, 8003, 8004 и 8005
echo Остановка процессов на портах 8000, 8001, 8002, 8003, 8004 и 8005...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8004') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8005') do taskkill /f /pid %%a >nul 2>&1

:: Ждем немного
timeout /t 2 /nobreak >nul

:: Запускаем микросервис аутентификации
echo 🚀 Запуск микросервиса аутентификации...
start "Auth Service" cmd /c "cd services\auth && python run_app.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем микросервис каталога
echo 📚 Запуск микросервиса каталога...
start "Catalog Service" cmd /c "cd services\catalog && python run_app.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем микросервис корзины
echo 🛒 Запуск микросервиса корзины...
start "Cart Service" cmd /c "cd services\cart && python run_app.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем микросервис заказов
echo 📦 Запуск микросервиса заказов...
start "Orders Service" cmd /c "cd services\orders && python run_app.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем микросервис рекомендаций
echo 🤖 Запуск микросервиса рекомендаций...
start "Recommender Service" cmd /c "cd services\recommender && python run_app.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем веб-сервер для фронтенда
echo 🌐 Запуск веб-сервера...
start "Web Server" cmd /c "cd src && python -m http.server 8000"

:: Ждем запуска всех сервисов
echo Ожидание запуска сервисов...
timeout /t 5 /nobreak >nul

:: Проверяем, что все сервисы запустились
:check_loop
set /a attempts=0
:check_ports
set /a attempts+=1
if %attempts% gtr 60 (
    echo ОШИБКА: Сервисы не запустились за 60 секунд
    pause
    exit /b 1
)

:: Проверяем порт 8001 (аутентификация)
netstat -an | findstr :8001 >nul
if errorlevel 1 goto check_ports

:: Проверяем порт 8002 (каталог)
netstat -an | findstr :8002 >nul
if errorlevel 1 goto check_ports

:: Проверяем порт 8004 (корзина)
netstat -an | findstr :8004 >nul
if errorlevel 1 goto check_ports

:: Проверяем порт 8003 (заказы)
netstat -an | findstr :8003 >nul
if errorlevel 1 goto check_ports

:: Проверяем порт 8005 (рекомендации)
netstat -an | findstr :8005 >nul
if errorlevel 1 goto check_ports

:: Проверяем порт 8000 (веб-сервер)
netstat -an | findstr :8000 >nul
if errorlevel 1 goto check_ports

echo ✅ Все сервисы запущены успешно!
echo ==================================================
echo 📋 Доступные сервисы:
echo    🌐 Главная страница: http://localhost:8000/index.html
echo    ⚙️  Админ-панель: http://localhost:8000/admin/admin.html
echo    🔐 API аутентификации: http://localhost:8001/docs
echo    📚 API каталога: http://localhost:8002/docs
echo    🛒 API корзины: http://localhost:8004/docs
echo    📦 API заказов: http://localhost:8003/docs
echo    🤖 API рекомендаций: http://localhost:8005/docs
echo.
echo 💡 Для остановки закройте окна командных строк
echo ==================================================

:: Открываем браузер
echo 🌐 Открытие главной страницы в браузере...
start http://localhost:8000/index.html
echo ✅ Браузер открыт!

echo.
echo 🎉 Приложение работает! Нажмите любую клавишу для остановки...
pause >nul

:: Останавливаем сервисы
echo 🛑 Остановка сервисов...
taskkill /f /im python.exe >nul 2>&1
echo ✅ Сервисы остановлены
pause