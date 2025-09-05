#!/usr/bin/env python3
"""
Скрипт для запуска всех микросервисов audio-store
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
    def start_auth_service(self):
        """Запуск микросервиса аутентификации"""
        print("🚀 Запуск микросервиса аутентификации...")
        auth_dir = self.base_dir / "services" / "auth"
        
        if not auth_dir.exists():
            print(f"❌ Папка {auth_dir} не найдена!")
            return False
            
        try:
            # Запускаем микросервис аутентификации
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=auth_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(("Auth Service", process))
            print("✅ Микросервис аутентификации запущен на порту 8001")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска микросервиса аутентификации: {e}")
            return False
    
    def start_web_server(self):
        """Запуск веб-сервера для статических файлов"""
        print("🌐 Запуск веб-сервера...")
        src_dir = self.base_dir / "src"
        
        if not src_dir.exists():
            print(f"❌ Папка {src_dir} не найдена!")
            return False
            
        try:
            # Запускаем веб-сервер
            process = subprocess.Popen(
                [sys.executable, "-m", "http.server", "8000"],
                cwd=src_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(("Web Server", process))
            print("✅ Веб-сервер запущен на порту 8000")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска веб-сервера: {e}")
            return False
    
    def check_ports(self):
        """Проверка доступности портов"""
        import socket
        
        ports_to_check = [8000, 8001]
        available_ports = []
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        available_ports.append(port)
            except:
                pass
        
        return available_ports
    
    def wait_for_services(self, timeout=30):
        """Ожидание запуска сервисов"""
        print("⏳ Ожидание запуска сервисов...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            available_ports = self.check_ports()
            if len(available_ports) >= 2:
                print(f"✅ Все сервисы запущены! Доступные порты: {available_ports}")
                return True
            time.sleep(1)
        
        print("❌ Таймаут ожидания запуска сервисов")
        return False
    
    def open_browser(self):
        """Открытие браузера"""
        try:
            import webbrowser
            print("🌐 Открытие главной страницы в браузере...")
            webbrowser.open("http://localhost:8000/index.html")
            print("✅ Браузер открыт!")
        except Exception as e:
            print(f"❌ Ошибка открытия браузера: {e}")
    
    def run(self):
        """Основной метод запуска"""
        print("🎵 Запуск Audio Store...")
        print("=" * 50)
        
        # Запускаем сервисы
        auth_ok = self.start_auth_service()
        web_ok = self.start_web_server()
        
        if not auth_ok or not web_ok:
            print("❌ Не удалось запустить все сервисы")
            self.cleanup()
            return False
        
        # Ждем запуска сервисов
        if self.wait_for_services():
            print("\n" + "=" * 50)
            print("🎉 Audio Store успешно запущен!")
            print("\n📋 Доступные URL:")
            print("   • Главная страница: http://localhost:8000/index.html")
            print("   • Страница входа: http://localhost:8000/login.html")
            print("   • Страница регистрации: http://localhost:8000/register.html")
            print("   • API документация: http://localhost:8001/docs")
            print("\n💡 Для остановки нажмите Ctrl+C")
            print("=" * 50)
            
            # Открываем браузер
            self.open_browser()
            
            # Ждем сигнала завершения
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Получен сигнал завершения...")
                self.cleanup()
                return True
        else:
            self.cleanup()
            return False
    
    def cleanup(self):
        """Очистка процессов"""
        print("🧹 Остановка сервисов...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} остановлен")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ {name} принудительно остановлен")
            except Exception as e:
                print(f"❌ Ошибка остановки {name}: {e}")

def main():
    manager = ServiceManager()
    success = manager.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 