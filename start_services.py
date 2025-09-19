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
import socket
import psutil
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        self.services = {
            "auth": {"port": 8001, "dir": "services/auth", "script": "run_app.py"},
            "catalog": {"port": 8002, "dir": "services/catalog", "script": "run_app.py"},
            "orders": {"port": 8003, "dir": "services/orders", "script": "run_app.py"},
            "cart": {"port": 8004, "dir": "services/cart", "script": "run_app.py"},
            "recommender": {"port": 8005, "dir": "services/recommender", "script": "run_app.py"},
            "prompts-manager": {"port": 8006, "dir": "services/prompts-manager", "script": "run_app.py"},
            "web": {"port": 8000, "dir": "src", "script": "-m http.server 8000"}
        }
        
    def check_directories(self):
        """Проверка существования всех необходимых папок"""
        print("🔍 Проверка структуры проекта...")
        missing_dirs = []
        
        for service_name, config in self.services.items():
            if service_name == "web":
                continue  # web сервер использует src папку
            service_dir = self.base_dir / config["dir"]
            if not service_dir.exists():
                missing_dirs.append(str(service_dir))
        
        # Проверяем папку src
        src_dir = self.base_dir / "src"
        if not src_dir.exists():
            missing_dirs.append(str(src_dir))
        
        if missing_dirs:
            print("❌ ОШИБКА: Не найдены следующие папки:")
            for dir_path in missing_dirs:
                print(f"   • {dir_path}")
            return False
        
        print("✅ Все необходимые папки найдены")
        return True
    
    def kill_processes_on_ports(self):
        """Остановка процессов на портах 8000-8006"""
        print("🛑 Остановка процессов на портах 8000-8006...")
        ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006]
        
        for port in ports:
            try:
                for conn in psutil.net_connections():
                    if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                        try:
                            process = psutil.Process(conn.pid)
                            process.terminate()
                            print(f"   • Остановлен процесс на порту {port} (PID: {conn.pid})")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            except Exception as e:
                print(f"   ⚠️ Ошибка при остановке процессов на порту {port}: {e}")
        
        # Ждем немного
        time.sleep(2)
    
    def start_service(self, service_name, config):
        """Запуск отдельного сервиса"""
        print(f"🚀 Запуск микросервиса {service_name}...")
        service_dir = self.base_dir / config["dir"]
        
        try:
            if service_name == "web":
                # Для веб-сервера используем специальную команду
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen(
                        ["cmd", "/c", "start", "Web Server", "cmd", "/k", 
                         f"cd /d {service_dir} && python -m http.server 8000"],
                        cwd=service_dir
                    )
                else:  # Linux/Mac
                    process = subprocess.Popen(
                        [sys.executable, "-m", "http.server", "8000"],
                        cwd=service_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
            else:
                # Для микросервисов
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen(
                        ["cmd", "/c", "start", f"{service_name.title()} Service", "cmd", "/k", 
                         f"cd /d {service_dir} && python {config['script']}"],
                        cwd=service_dir
                    )
                else:  # Linux/Mac
                    process = subprocess.Popen(
                        [sys.executable, config["script"]],
                        cwd=service_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
            
            self.processes.append((service_name, process))
            print(f"✅ Микросервис {service_name} запущен на порту {config['port']}")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска микросервиса {service_name}: {e}")
            return False
    
    def check_ports(self):
        """Проверка доступности портов"""
        ports_to_check = [config["port"] for config in self.services.values()]
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
    
    def check_service_health(self, port):
        """Проверка здоровья сервиса через HTTP"""
        try:
            import urllib.request
            import urllib.error
            
            # Определяем endpoint для проверки здоровья
            if port == 8000:  # Web server
                url = f"http://localhost:{port}/index.html"
            else:  # API services
                url = f"http://localhost:{port}/health"
            
            with urllib.request.urlopen(url, timeout=3) as response:
                return response.status == 200
        except Exception as e:
            # Для отладки можно раскомментировать следующую строку
            # print(f"Health check failed for port {port}: {e}")
            return False
    
    def wait_for_services(self, services_to_check=None, timeout=60):
        """Ожидание запуска сервисов"""
        print("⏳ Ожидание запуска сервисов...")
        start_time = time.time()
        
        if services_to_check is None:
            expected_ports = [config["port"] for config in self.services.values()]
        else:
            expected_ports = [self.services[service]["port"] for service in services_to_check]
        
        while time.time() - start_time < timeout:
            # Сначала проверяем, что порты открыты
            available_ports = self.check_ports()
            if len(available_ports) >= len(expected_ports):
                # Затем проверяем, что сервисы отвечают на HTTP запросы
                healthy_services = []
                for port in expected_ports:
                    if self.check_service_health(port):
                        healthy_services.append(port)
                
                if len(healthy_services) >= len(expected_ports):
                    print(f"✅ Все сервисы запущены и готовы! Порты: {healthy_services}")
                    return True
                else:
                    print(f"⏳ Порты открыты: {available_ports}, готовы: {healthy_services}")
            else:
                print(f"⏳ Ожидание открытия портов... Открыто: {len(available_ports)}/{len(expected_ports)}")
            
            time.sleep(2)
        
        print("❌ Таймаут ожидания запуска сервисов")
        print(f"   Ожидаемые порты: {expected_ports}")
        print(f"   Доступные порты: {self.check_ports()}")
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
    
    def run(self, minimal=False):
        """Основной метод запуска"""
        print("🎵 Запуск Audio Store...")
        print("=" * 50)
        
        # Проверяем структуру проекта
        if not self.check_directories():
            return False
        
        # Останавливаем процессы на портах
        self.kill_processes_on_ports()
        
        # Определяем какие сервисы запускать
        if minimal:
            # Минимальный набор: только веб-сервер и каталог
            services_to_run = ["web", "catalog"]
            print("\n🚀 Запуск минимального набора сервисов (веб-сервер + каталог)...")
        else:
            # Все сервисы
            services_to_run = list(self.services.keys())
            print("\n🚀 Запуск всех микросервисов...")
        
        services_started = []
        
        for service_name in services_to_run:
            config = self.services[service_name]
            if self.start_service(service_name, config):
                services_started.append(service_name)
                time.sleep(3)  # Уменьшаем время ожидания для минимального набора
            else:
                print(f"❌ Не удалось запустить сервис {service_name}")
        
        if len(services_started) != len(services_to_run):
            print("❌ Не удалось запустить все необходимые сервисы")
            self.cleanup()
            return False
        
        # Ждем запуска сервисов
        if self.wait_for_services(services_to_run):
            print("\n" + "=" * 50)
            print("🎉 Audio Store успешно запущен!")
            print("\n📋 Доступные URL:")
            print("   🌐 Главная страница: http://localhost:8000/index.html")
            print("   ⚙️  Админ-панель: http://localhost:8000/admin/admin.html")
            print("   🔐 API аутентификации: http://localhost:8001/docs")
            print("   📚 API каталога: http://localhost:8002/docs")
            print("   📦 API заказов: http://localhost:8003/docs")
            print("   🛒 API корзины: http://localhost:8004/docs")
            print("   🤖 API рекомендаций: http://localhost:8005/docs")
            print("   📝 API промптов: http://localhost:8006/docs")
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Запуск микросервисов Audio Store')
    parser.add_argument('--minimal', action='store_true', 
                       help='Запустить только веб-сервер и каталог (для тестирования)')
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    success = manager.run(minimal=args.minimal)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 