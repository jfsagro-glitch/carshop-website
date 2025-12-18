# Настройка автоматической отправки заказов

## Email отправка

### Вариант 1: EmailJS (Рекомендуется)

1. Зарегистрируйтесь на https://www.emailjs.com/
2. Создайте Email Service:
   - Добавьте Gmail или другой email сервис
   - Service ID будет вида `service_xxxxx`
3. Создайте Email Template:
   - To Email: `carexportgeo@bk.ru`
   - Subject: `{{subject}}`
   - Body: `{{message}}`
   - Template ID будет вида `template_xxxxx`
4. Получите Public Key в разделе Account → API Keys
5. Замените в `europe-orders.html`:
   ```javascript
   const EMAILJS_SERVICE_ID = 'ваш_service_id';
   const EMAILJS_TEMPLATE_ID = 'ваш_template_id';
   const EMAILJS_PUBLIC_KEY = 'ваш_public_key';
   ```

### Вариант 2: Web3Forms

1. Зарегистрируйтесь на https://web3forms.com/
2. Получите Access Key
3. Замените в коде:
   ```javascript
   const ACCESS_KEY = 'ваш_access_key';
   ```

## Telegram уведомления

1. Создайте бота через @BotFather в Telegram:
   - Отправьте `/newbot`
   - Следуйте инструкциям
   - Сохраните Bot Token (вида `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. Узнайте Chat ID пользователя @Aleksandr_N_444:
   - Отправьте боту @userinfobot сообщение
   - Или используйте @getidsbot
   - Chat ID будет числом (например, `123456789`)

3. Замените в `europe-orders.html`:
   ```javascript
   const TELEGRAM_BOT_TOKEN = 'ваш_bot_token';
   const TELEGRAM_CHAT_ID = 'ваш_chat_id';
   ```

## Тестирование

После настройки протестируйте отправку заказа:
1. Добавьте автомобиль в корзину
2. Нажмите "Оформить заказ"
3. Заполните форму
4. Проверьте получение email и Telegram уведомления

