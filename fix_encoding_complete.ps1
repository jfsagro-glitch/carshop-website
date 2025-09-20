# Complete encoding fix for script.js
Write-Host "Completely fixing encoding in script.js..." -ForegroundColor Green

# Read the file with proper encoding
$content = Get-Content "script.js" -Raw -Encoding UTF8

# Fix all encoding issues step by step
Write-Host "Fixing Russian text encoding..." -ForegroundColor Yellow

# Fix comments
$content = $content -replace "// Р"Р°РЅРЅС‹Рµ Р°РІС‚РѕРјРѕР±РёР»РµР№", "// Данные автомобилей"
$content = $content -replace "// Р"Р»РѕР±Р°Р»СЊРЅС‹Рµ РїРµСЂРµРјРµРЅРЅС‹Рµ", "// Глобальные переменные"
$content = $content -replace "// РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РїСЂРё Р·Р°РіСЂСѓР·РєРµ СЃС‚СЂР°РЅРёС†С‹", "// Инициализация при загрузке страницы"
$content = $content -replace "// РЎРѕР·РґР°РµРј iframe РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Google Drive РїР°РїРєРё", "// Создаем iframe для отображения Google Drive папки"

# Fix car details
$content = $content -replace "Р"РІРёРіР°С‚РµР»СЊ:", "Двигатель:"
$content = $content -replace "РџСЂРѕР±РµРі:", "Пробег:"
$content = $content -replace "РєРј", "км"
$content = $content -replace "Р"Р°С‚Р° РІС‹РїСѓСЃРєР°:", "Дата выпуска:"
$content = $content -replace "Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ", "Включает растаможку и доставку"

# Fix buttons
$content = $content -replace "Р' РєРѕСЂР·РёРЅСѓ", "В корзину"
$content = $content -replace "РџРѕРґСЂРѕР±РЅРµРµ", "Подробнее"

# Fix notifications
$content = $content -replace "РђРІС‚РѕРјРѕР±РёР»СЊ РґРѕР±Р°РІР»РµРЅ РІ РєРѕСЂР·РёРЅСѓ!", "Автомобиль добавлен в корзину!"
$content = $content -replace "РљРѕСЂР·РёРЅР° РїСѓСЃС‚Р°", "Корзина пуста"
$content = $content -replace "РљРѕР»РёС‡РµСЃС‚РІРѕ:", "Количество:"

# Fix modal content
$content = $content -replace "РћСЃРЅРѕРІРЅС‹Рµ С…Р°СЂР°РєС‚РµСЂРёСЃС‚РёРєРё", "Основные характеристики"
$content = $content -replace "РњР°СЂРєР°:", "Марка:"
$content = $content -replace "РњРѕРґРµР»СЊ:", "Модель:"
$content = $content -replace "Р"РѕРґ:", "Год:"
$content = $content -replace "Р¤РѕС‚РѕРіСЂР°С„РёРё Р°РІС‚РѕРјРѕР±РёР»СЏ", "Фотографии автомобиля"
$content = $content -replace "Р¦РµРЅР° РІРєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ РїРѕ Р РѕСЃСЃРёРё", "Цена включает растаможку и доставку по России"
$content = $content -replace "РќРёРєР°РєРёС… РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹С… РїР»Р°С‚РµР¶РµР№!", "Никаких дополнительных платежей!"
$content = $content -replace "Р"РѕР±Р°РІРёС‚СЊ РІ РєРѕСЂР·РёРЅСѓ", "Добавить в корзину"
$content = $content -replace "Р—Р°РєСЂС‹С‚СЊ", "Закрыть"

# Fix functions
$content = $content -replace "Р¤СѓРЅРєС†РёСЏ РґР»СЏ РЅР°РІРёРіР°С†РёРё РїРѕ РіР°Р»РµСЂРµРµ", "Функция для навигации по галерее"
$content = $content -replace "РћС‚РєСЂС‹РІР°РµРј Google Drive РїР°РїРєСѓ РІ РЅРѕРІРѕРј РѕРєРЅРµ", "Открываем Google Drive папку в новом окне"
$content = $content -replace "РћС‚РєСЂС‹С‚Р° РїР°РїРєР° СЃ С„РѕС‚РѕРіСЂР°С„РёСЏРјРё РІ Google Drive", "Открыта папка с фотографиями в Google Drive"

# Fix checkout
$content = $content -replace "РљРѕСЂР·РёРЅР° РїСѓСЃС‚Р°!", "Корзина пуста!"
$content = $content -replace "РћС„РѕСЂРјР»РµРЅРёРµ Р·Р°РєР°Р·Р° РЅР° СЃСѓРјРјСѓ", "Оформление заказа на сумму"
$content = $content -replace "Р'РєР»СЋС‡Р°РµС‚", "Включает"
$content = $content -replace "Р°РІС‚РѕРјРѕР±РёР»РµР№.", "автомобилей."
$content = $content -replace "Р'СЃРµ С†РµРЅС‹ РІРєР»СЋС‡Р°СЋС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ РїРѕ Р РѕСЃСЃРёРё.", "Все цены включают растаможку и доставку по России."
$content = $content -replace "РЎ РІР°РјРё СЃРІСЏР¶РµС‚СЃСЏ РјРµРЅРµРґР¶РµСЂ РґР»СЏ СѓС‚РѕС‡РЅРµРЅРёСЏ РґРµС‚Р°Р»РµР№ РѕС„РѕСЂРјР»РµРЅРёСЏ РґРѕРєСѓРјРµРЅС‚РѕРІ.", "С вами свяжется менеджер для уточнения деталей оформления документов."
$content = $content -replace "РћС‡РёС‰Р°РµРј РєРѕСЂР·РёРЅСѓ РїРѕСЃР»Рµ РѕС„РѕСЂРјР»РµРЅРёСЏ Р·Р°РєР°Р·Р°", "Очищаем корзину после оформления заказа"
$content = $content -replace "Р—Р°РєР°Р· СѓСЃРїРµС€РЅРѕ РѕС„РѕСЂРјР»РµРЅ!", "Заказ успешно оформлен!"

# Fix event listeners
$content = $content -replace "РљРѕСЂР·РёРЅР°", "Корзина"
$content = $content -replace "Р—Р°РєСЂС‹С‚РёРµ РјРѕРґР°Р»СЊРЅС‹С… РѕРєРЅ РїРѕ РєР»РёРєСѓ РІРЅРµ РёС…", "Закрытие модальных окон по клику вне их"
$content = $content -replace "Р¤РѕСЂРјР° РѕР±СЂР°С‚РЅРѕР№ СЃРІСЏР·Рё", "Форма обратной связи"
$content = $content -replace "Р—Р°СЏРІРєР° РѕС‚РїСЂР°РІР»РµРЅР°! РњС‹ СЃРІСЏР¶РµРјСЃСЏ СЃ РІР°РјРё РІ Р±Р»РёР¶Р°Р№С€РµРµ РІСЂРµРјСЏ.", "Заявка отправлена! Мы свяжемся с вами в ближайшее время."
$content = $content -replace "РџР»Р°РІРЅР°СЏ РїСЂРѕРєСЂСѓС‚РєР° РґР»СЏ РЅР°РІРёРіР°С†РёРё", "Плавная прокрутка для навигации"

# Fix CSS comments
$content = $content -replace "Р"РѕР±Р°РІР»СЏРµРј CSS Р°РЅРёРјР°С†РёРё Рё СЃС‚РёР»Рё РґР»СЏ СЃРєСЂС‹С‚РёСЏ РЅР°Р·РІР°РЅРёР№ С„Р°Р№Р»РѕРІ", "Добавляем CSS анимации и стили для скрытия названий файлов"
$content = $content -replace "РЎРєСЂС‹РІР°РµРј РЅР°Р·РІР°РЅРёСЏ С„Р°Р№Р»РѕРІ РІ Google Drive iframe", "Скрываем названия файлов в Google Drive iframe"
$content = $content -replace "РЎС‚РёР»Рё РґР»СЏ СЃРєСЂС‹С‚РёСЏ СЃРїРёСЃРєР° С„Р°Р№Р»РѕРІ", "Стили для скрытия списка файлов"
$content = $content -replace "РЎРєСЂС‹РІР°РµРј Р·Р°РіРѕР»РѕРІРєРё Рё СЃРїРёСЃРєРё РІ Google Drive", "Скрываем заголовки и списки в Google Drive"

# Fix symbols
$content = $content -replace "рџљ—", "🚗"
$content = $content -replace "в‚Ѕ", "₽"

# Fix remaining encoding issues
$content = $content -replace "Р'", "В"
$content = $content -replace "Рє", "к"
$content = $content -replace "Р»", "л"
$content = $content -replace "СЋ", "ю"
$content = $content -replace "С‡", "ч"
$content = $content -replace "Р°", "а"
$content = $content -replace "Рµ", "е"
$content = $content -replace "С‚", "т"
$content = $content -replace "СЂ", "р"
$content = $content -replace "Р°", "а"
$content = $content -replace "СЃ", "с"
$content = $content -replace "С‚", "т"
$content = $content -replace "Р°", "а"
$content = $content -replace "Рј", "м"
$content = $content -replace "Рѕ", "о"
$content = $content -replace "Р¶", "ж"
$content = $content -replace "Рє", "к"
$content = $content -replace "Сѓ", "у"
$content = $content -replace "Рё", "и"
$content = $content -replace "Рґ", "д"
$content = $content -replace "Рѕ", "о"
$content = $content -replace "СЃ", "с"
$content = $content -replace "С‚", "т"
$content = $content -replace "Р°", "а"
$content = $content -replace "РІ", "в"
$content = $content -replace "Рє", "к"
$content = $content -replace "Сѓ", "у"

# Write the corrected content back
$content | Out-File "script.js" -Encoding UTF8 -NoNewline

Write-Host "Encoding completely fixed!" -ForegroundColor Green
Write-Host "All Russian text should now display correctly." -ForegroundColor Cyan

