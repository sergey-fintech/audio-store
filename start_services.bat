@echo off
chcp 65001 >nul
title Audio Store - Запуск сервисов

echo 🎵 Запуск Audio Store...
echo ==================================================

:: Проверяем, что мы в корневой директории проекта
cd /d "%~dp0"

echo 📁 Текущая директория: %CD%

:: Проверяем наличие необходимых папок
if not exist "services\auth" (
    echo ❌ Папка services\auth не найдена!
    pause
    exit /b 1
)

if not exist "services\catalog" (
    echo ❌ Папка services\catalog не найдена!
    pause
    exit /b 1
)

if not exist "services\cart" (
    echo ❌ Папка services\cart не найдена!
    pause
    exit /b 1
)

if not exist "services\orders" (
    echo ❌ Папка services\orders не найдена!
    pause
    exit /b 1
)

if not exist "src" (
    echo ❌ Папка src не найдена!
    pause
    exit /b 1
)

:: Останавливаем процессы на портах 8000, 8001, 8002, 8003 и 8004
echo 🔍 Остановка процессов на портах 8000, 8001, 8002, 8003 и 8004...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8004') do taskkill /f /pid %%a >nul 2>&1

:: Ждем немного
timeout /t 2 /nobreak >nul

:: Запускаем микросервис аутентификации
echo 🚀 Запуск микросервиса аутентификации...
start "Auth Service" cmd /c "cd services\auth && python main.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем микросервис каталога
echo 📚 Запуск микросервиса каталога...
start "Catalog Service" cmd /c "cd services\catalog && python main.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем микросервис корзины
echo 🛒 Запуск микросервиса корзины...
start "Cart Service" cmd /c "cd services\cart && python main.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем микросервис заказов
echo 📦 Запуск микросервиса заказов...
start "Orders Service" cmd /c "cd services\orders && python main.py"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Запускаем веб-сервер
echo 🌐 Запуск веб-сервера...
start "Web Server" cmd /c "cd src && python -m http.server 8000"

:: Ждем запуска
timeout /t 3 /nobreak >nul

:: Проверяем, что сервисы запустились
echo ⏳ Проверка запуска сервисов...

:check_loop
set /a attempts=0
:check_ports
set /a attempts+=1
if %attempts% gtr 60 (
    echo ❌ Сервисы не запустились за 60 секунд
    pause
    exit /b 1
)

:: Проверяем порт 8001 (аутентификация)
netstat -an | findstr :8001 >nul
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto check_ports
)

:: Проверяем порт 8002 (каталог)
netstat -an | findstr :8002 >nul
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto check_ports
)

:: Проверяем порт 8004 (корзина)
netstat -an | findstr :8004 >nul
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto check_ports
)

:: Проверяем порт 8003 (заказы)
netstat -an | findstr :8003 >nul
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto check_ports
)

:: Проверяем порт 8000 (веб-сервер)
netstat -an | findstr :8000 >nul
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto check_ports
)

:: Все сервисы запущены
echo.
echo ==================================================
echo 🎉 Audio Store успешно запущен!
echo.
echo 📋 Доступные URL:
echo    • Главная страница: http://localhost:8000/index.html
echo    • Страница входа: http://localhost:8000/login.html
echo    • Страница регистрации: http://localhost:8000/register.html
echo    • Страница корзины: http://localhost:8000/cart.html
echo    • Админ-панель: http://localhost:8000/admin/admin.html
echo    • API аутентификации: http://localhost:8001/docs
echo    • API каталога: http://localhost:8002/docs
echo    • API корзины: http://localhost:8004/docs
echo    • API заказов: http://localhost:8003/docs
echo.
echo 💡 Для остановки закройте окна командных строк
echo ==================================================

:: Открываем браузер
echo 🌐 Открытие главной страницы в браузере...
start http://localhost:8000/index.html
echo ✅ Браузер открыт!

echo.
echo 🎵 Приложение работает! Нажмите любую клавишу для остановки...
pause >nul

:: Останавливаем сервисы
echo 🛑 Остановка сервисов...
taskkill /f /im python.exe >nul 2>&1
echo ✅ Сервисы остановлены
pause
