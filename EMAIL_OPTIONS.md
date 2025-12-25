# Варианты настройки отправки email уведомлений

## 🎯 Рекомендуемые варианты (от простого к сложному)

### 1. FormSubmit.co (САМЫЙ ПРОСТОЙ - без настройки) ⭐

**Преимущества:**
- ✅ Не требует регистрации
- ✅ Не требует настройки
- ✅ Работает сразу
- ✅ Бесплатно до 50 писем/месяц

**Как использовать:**
Просто замените в коде `europe-orders.html` функцию `sendOrderEmail` на:

```javascript
async function sendOrderEmail(name, phone, email, orderItems, total, subject, body) {
    const payload = new URLSearchParams();
    payload.append('name', name);
    payload.append('phone', phone);
    payload.append('email', email);
    payload.append('message', body);
    payload.append('_captcha', 'false');
    payload.append('_subject', subject);
    payload.append('_to', 'carexportgeo@bk.ru');
    
    try {
        const response = await fetch('https://formsubmit.co/carexportgeo@bk.ru', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: payload
        });
        
        if (response.ok) {
            return true;
        } else {
            throw new Error('FormSubmit error');
        }
    } catch (error) {
        console.error('FormSubmit error:', error);
        return false;
    }
}
```

**Готово!** Работает сразу без настройки.

---

### 2. Web3Forms (Простой, больше лимитов)

**Преимущества:**
- ✅ Простая настройка (только Access Key)
- ✅ 250 писем/месяц бесплатно
- ✅ Не требует подтверждения email

**Настройка:**
1. Зайдите на https://web3forms.com/
2. Введите email `carexportgeo@bk.ru`
3. Получите Access Key
4. Замените в коде `ACCESS_KEY`

**Код:**
```javascript
async function sendOrderEmail(name, phone, email, orderItems, total, subject, body) {
    const ACCESS_KEY = 'ваш_access_key'; // Получите на web3forms.com
    
    try {
        const response = await fetch('https://api.web3forms.com/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                access_key: ACCESS_KEY,
                subject: subject,
                from_name: name,
                from_email: email,
                phone: phone,
                message: body
            })
        });
        
        if (response.ok) {
            return true;
        } else {
            throw new Error('Web3Forms error');
        }
    } catch (error) {
        console.error('Web3Forms error:', error);
        return false;
    }
}
```

---

### 3. Google Apps Script (Бесплатно, неограниченно)

**Преимущества:**
- ✅ Полностью бесплатно
- ✅ Неограниченное количество писем
- ✅ Работает с Gmail
- ✅ Можно настроить Telegram тоже

**Настройка:**
1. Откройте https://script.google.com/
2. Создайте новый проект
3. Вставьте код:
```javascript
function doPost(e) {
    const data = JSON.parse(e.postData.contents);
    
    const subject = data.subject || 'Новый заказ';
    const body = data.body || '';
    
    MailApp.sendEmail({
        to: 'carexportgeo@bk.ru',
        subject: subject,
        body: body
    });
    
    return ContentService.createTextOutput('OK');
}
```

4. Опубликуйте как веб-приложение (Deploy → New deployment → Web app)
5. Скопируйте URL веб-приложения
6. Используйте этот URL в коде

**Код:**
```javascript
async function sendOrderEmail(name, phone, email, orderItems, total, subject, body) {
    const GOOGLE_SCRIPT_URL = 'ваш_url_веб_приложения';
    
    try {
        const response = await fetch(GOOGLE_SCRIPT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject: subject,
                body: body
            })
        });
        
        if (response.ok) {
            return true;
        } else {
            throw new Error('Google Script error');
        }
    } catch (error) {
        console.error('Google Script error:', error);
        return false;
    }
}
```

---

### 4. EmailJS (Требует настройки, но надежный)

**Преимущества:**
- ✅ Надежный сервис
- ✅ 200 писем/месяц бесплатно
- ✅ Хорошая документация

**Настройка:** См. инструкцию выше или https://www.emailjs.com/docs/

---

### 5. PHP скрипт на сервере (Если есть сервер)

**Преимущества:**
- ✅ Полный контроль
- ✅ Неограниченно
- ✅ Можно добавить любую логику

**Создайте файл `send_order.php` на сервере:**
```php
<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$data = json_decode(file_get_contents('php://input'), true);

$to = 'carexportgeo@bk.ru';
$subject = $data['subject'] ?? 'Новый заказ';
$message = $data['body'] ?? '';
$headers = "From: noreply@cmsauto.store\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

if (mail($to, $subject, $message, $headers)) {
    echo json_encode(['success' => true]);
} else {
    echo json_encode(['success' => false]);
}
?>
```

**Код:**
```javascript
async function sendOrderEmail(name, phone, email, orderItems, total, subject, body) {
    try {
        const response = await fetch('https://cmsauto.store/send_order.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject: subject,
                body: body
            })
        });
        
        if (response.ok) {
            return true;
        } else {
            throw new Error('PHP error');
        }
    } catch (error) {
        console.error('PHP error:', error);
        return false;
    }
}
```

---

## 🚀 Быстрый старт (FormSubmit.co)

Самый простой вариант - использовать FormSubmit.co, который уже используется на других страницах сайта. Просто замените функцию отправки в `europe-orders.html`.








