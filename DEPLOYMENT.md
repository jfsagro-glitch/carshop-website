# 🚀 Развертывание CarSalesBot

## Подготовка к развертыванию

### 1. Системные требования

- Python 3.8+
- SQLite 3 (или PostgreSQL для продакшена)
- 512MB RAM минимум
- 1GB свободного места на диске

### 2. Установка зависимостей

```bash
# Клонирование репозитория
git clone <repository_url>
cd carshop-bot

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка конфигурации

```bash
# Копирование конфигурации
cp config_example.py config.py

# Создание файла переменных окружения
cp .env.example .env
```

Отредактируйте файлы:
- `config.py` - основные настройки
- `.env` - секретные данные (токены, пароли)

## Локальное развертывание

### 1. Запуск в режиме разработки

```bash
# Простой запуск
python enhanced_bot.py

# Запуск с переменными окружения
python run_enhanced_bot.py
```

### 2. Тестирование

```bash
# Запуск тестов
python test_bot.py

# Проверка импорта данных
python import_data.py
```

## Продакшен развертывание

### 1. Настройка сервера

#### Ubuntu/Debian:
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv git -y

# Создание пользователя для бота
sudo useradd -m -s /bin/bash botuser
sudo su - botuser

# Клонирование и настройка
git clone <repository_url> carshop-bot
cd carshop-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка systemd сервиса

Создайте файл `/etc/systemd/system/carsalesbot.service`:

```ini
[Unit]
Description=CarSalesBot Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/carshop-bot
Environment=PATH=/home/botuser/carshop-bot/venv/bin
ExecStart=/home/botuser/carshop-bot/venv/bin/python run_enhanced_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable carsalesbot
sudo systemctl start carsalesbot
sudo systemctl status carsalesbot
```

### 3. Настройка логирования

Создайте директории для логов:
```bash
sudo mkdir -p /var/log/carsalesbot
sudo chown botuser:botuser /var/log/carsalesbot
```

Настройте ротацию логов в `/etc/logrotate.d/carsalesbot`:
```
/var/log/carsalesbot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 botuser botuser
    postrotate
        systemctl reload carsalesbot
    endscript
}
```

### 4. Настройка базы данных

#### SQLite (для небольших проектов):
```bash
# Создание директории для БД
mkdir -p /var/lib/carsalesbot
sudo chown botuser:botuser /var/lib/carsalesbot

# Настройка в config.py
DATABASE_PATH = "/var/lib/carsalesbot/cars.db"
```

#### PostgreSQL (рекомендуется для продакшена):
```bash
# Установка PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Создание базы данных
sudo -u postgres createdb carsalesbot
sudo -u postgres createuser botuser

# Настройка прав доступа
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE carsalesbot TO botuser;"
```

### 5. Настройка Nginx (опционально)

Если нужен веб-интерфейс для администрирования:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6. Настройка мониторинга

#### Создание скрипта мониторинга `/home/botuser/monitor.sh`:
```bash
#!/bin/bash
if ! systemctl is-active --quiet carsalesbot; then
    echo "CarSalesBot is down, restarting..."
    systemctl restart carsalesbot
    # Отправка уведомления администратору
    # curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
    #      -d "chat_id=<ADMIN_ID>" \
    #      -d "text=CarSalesBot was restarted"
fi
```

#### Настройка cron для мониторинга:
```bash
# Добавьте в crontab
*/5 * * * * /home/botuser/monitor.sh
```

## Резервное копирование

### 1. Автоматическое резервное копирование

Создайте скрипт `/home/botuser/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/home/botuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание резервной копии базы данных
cp /var/lib/carsalesbot/cars.db "$BACKUP_DIR/cars_$DATE.db"

# Сжатие старых резервных копий
find "$BACKUP_DIR" -name "cars_*.db" -mtime +7 -delete
```

### 2. Настройка cron для резервного копирования:
```bash
# Ежедневное резервное копирование в 2:00
0 2 * * * /home/botuser/backup.sh
```

## Обновление бота

### 1. Процедура обновления

```bash
# Остановка сервиса
sudo systemctl stop carsalesbot

# Создание резервной копии
cp -r /home/botuser/carshop-bot /home/botuser/carshop-bot.backup.$(date +%Y%m%d)

# Обновление кода
cd /home/botuser/carshop-bot
git pull origin main

# Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt

# Запуск сервиса
sudo systemctl start carsalesbot
```

### 2. Проверка после обновления

```bash
# Проверка статуса
sudo systemctl status carsalesbot

# Проверка логов
tail -f /var/log/carsalesbot/bot.log

# Тестирование функционала
# (отправьте команду /start боту)
```

## Масштабирование

### 1. Горизонтальное масштабирование

Для высоких нагрузок рассмотрите:
- Использование Redis для кэширования
- Разделение на микросервисы
- Использование load balancer

### 2. Оптимизация базы данных

```sql
-- Создание индексов для ускорения запросов
CREATE INDEX idx_cars_brand ON cars(brand);
CREATE INDEX idx_cars_price ON cars(price);
CREATE INDEX idx_cars_year ON cars(year);
CREATE INDEX idx_cars_active ON cars(is_active, is_moderated);
```

## Безопасность

### 1. Настройка файрвола

```bash
# Разрешение только необходимых портов
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Регулярные обновления

```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Мониторинг безопасности

- Регулярно проверяйте логи на подозрительную активность
- Используйте fail2ban для защиты от брутфорса
- Настройте уведомления о критических событиях

## Поддержка

При возникновении проблем:

1. Проверьте логи: `sudo journalctl -u carsalesbot -f`
2. Проверьте статус сервиса: `sudo systemctl status carsalesbot`
3. Проверьте конфигурацию: `python -c "import config; print('Config OK')"`
4. Обратитесь к документации или создайте issue в репозитории




