# Скрипт для запуска всех сервисов Audio Store
# Запуск: .\start_services.ps1

param(
    [switch]$NoBrowser
)

Write-Host "🎵 Запуск Audio Store..." -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# Функция для проверки портов
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Функция для ожидания запуска сервиса
function Wait-ForService {
    param([int]$Port, [string]$ServiceName, [int]$Timeout = 30)
    
    Write-Host "⏳ Ожидание запуска $ServiceName на порту $Port..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    while ((Get-Date) - $startTime).TotalSeconds -lt $Timeout) {
        if (Test-Port -Port $Port) {
            Write-Host "✅ $ServiceName запущен!" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Seconds 1
    }
    
    Write-Host "❌ $ServiceName не запустился за $Timeout секунд" -ForegroundColor Red
    return $false
}

# Проверяем, что мы в корневой директории проекта
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "📁 Текущая директория: $(Get-Location)" -ForegroundColor Gray

# Проверяем наличие необходимых папок
$authDir = Join-Path $scriptDir "services\auth"
$srcDir = Join-Path $scriptDir "src"

if (-not (Test-Path $authDir)) {
    Write-Host "❌ Папка $authDir не найдена!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $srcDir)) {
    Write-Host "❌ Папка $srcDir не найдена!" -ForegroundColor Red
    exit 1
}

# Останавливаем процессы на портах 8000 и 8001, если они заняты
Write-Host "🔍 Проверка занятых портов..." -ForegroundColor Yellow

$processesToKill = @()
if (Test-Port -Port 8000) {
    $processesToKill += Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
}
if (Test-Port -Port 8001) {
    $processesToKill += Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
}

if ($processesToKill) {
    Write-Host "🛑 Остановка процессов на портах 8000 и 8001..." -ForegroundColor Yellow
    $processesToKill | ForEach-Object {
        try {
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Процесс $_ остановлен" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️ Не удалось остановить процесс $_" -ForegroundColor Yellow
        }
    }
    Start-Sleep -Seconds 2
}

# Запускаем микросервис аутентификации
Write-Host "🚀 Запуск микросервиса аутентификации..." -ForegroundColor Yellow
$authJob = Start-Job -ScriptBlock {
    Set-Location $using:authDir
    python main.py
}

if ($authJob.State -eq "Running") {
    Write-Host "✅ Микросервис аутентификации запущен" -ForegroundColor Green
} else {
    Write-Host "❌ Не удалось запустить микросервис аутентификации" -ForegroundColor Red
    exit 1
}

# Запускаем веб-сервер
Write-Host "🌐 Запуск веб-сервера..." -ForegroundColor Yellow
$webJob = Start-Job -ScriptBlock {
    Set-Location $using:srcDir
    python -m http.server 8000
}

if ($webJob.State -eq "Running") {
    Write-Host "✅ Веб-сервер запущен" -ForegroundColor Green
} else {
    Write-Host "❌ Не удалось запустить веб-сервер" -ForegroundColor Red
    Stop-Job $authJob
    Remove-Job $authJob
    exit 1
}

# Ждем запуска сервисов
$authReady = Wait-ForService -Port 8001 -ServiceName "Микросервис аутентификации"
$webReady = Wait-ForService -Port 8000 -ServiceName "Веб-сервер"

if (-not $authReady -or -not $webReady) {
    Write-Host "❌ Не все сервисы запустились" -ForegroundColor Red
    Stop-Job $authJob, $webJob
    Remove-Job $authJob, $webJob
    exit 1
}

# Выводим информацию о запущенных сервисах
Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "🎉 Audio Store успешно запущен!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Доступные URL:" -ForegroundColor White
Write-Host "   • Главная страница: http://localhost:8000/index.html" -ForegroundColor Cyan
Write-Host "   • Страница входа: http://localhost:8000/login.html" -ForegroundColor Cyan
Write-Host "   • Страница регистрации: http://localhost:8000/register.html" -ForegroundColor Cyan
Write-Host "   • API документация: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Cyan

# Открываем браузер, если не указан флаг -NoBrowser
if (-not $NoBrowser) {
    Write-Host "🌐 Открытие главной страницы в браузере..." -ForegroundColor Yellow
    Start-Process "http://localhost:8000/index.html"
    Write-Host "✅ Браузер открыт!" -ForegroundColor Green
}

# Функция очистки при завершении
function Cleanup {
    Write-Host ""
    Write-Host "🛑 Остановка сервисов..." -ForegroundColor Yellow
    
    if ($authJob -and $authJob.State -eq "Running") {
        Stop-Job $authJob
        Remove-Job $authJob
        Write-Host "✅ Микросервис аутентификации остановлен" -ForegroundColor Green
    }
    
    if ($webJob -and $webJob.State -eq "Running") {
        Stop-Job $webJob
        Remove-Job $webJob
        Write-Host "✅ Веб-сервер остановлен" -ForegroundColor Green
    }
    
    Write-Host "🎵 Audio Store остановлен" -ForegroundColor Green
}

# Регистрируем обработчик для корректного завершения
Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

try {
    # Ждем завершения или прерывания
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Проверяем, что джобы еще работают
        if ($authJob.State -ne "Running" -or $webJob.State -ne "Running") {
            Write-Host "⚠️ Один из сервисов завершился неожиданно" -ForegroundColor Yellow
            break
        }
    }
}
catch {
    Write-Host "🛑 Получен сигнал завершения..." -ForegroundColor Yellow
}
finally {
    Cleanup
}
