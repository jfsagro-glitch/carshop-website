# Руководство по размещению сайта на GitHub

## Шаг 1: Установка Git
1. Скачайте Git с официального сайта: https://git-scm.com/download/win
2. Установите Git с настройками по умолчанию
3. Перезапустите командную строку/PowerShell

## Шаг 2: Создание репозитория на GitHub
1. Войдите в ваш аккаунт GitHub: https://github.com
2. Нажмите кнопку "New" или "+" → "New repository"
3. Название репозитория: `carshop-website` (или любое другое)
4. Выберите "Public" для бесплатного хостинга
5. Поставьте галочку "Add a README file"
6. Нажмите "Create repository"

## Шаг 3: Подготовка файлов
Все файлы уже готовы в папке проекта:
- `index.html` - главная страница
- `styles.css` - стили
- `script.js` - JavaScript код
- `images/` - папка с изображениями
- `images/logo.svg` - логотип

## Шаг 4: Команды для загрузки на GitHub

Откройте PowerShell в папке проекта и выполните:

```powershell
# Инициализация git репозитория
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: CarExport website"

# Добавление удаленного репозитория (замените USERNAME на ваш GitHub username)
git remote add origin https://github.com/USERNAME/carshop-website.git

# Переименование основной ветки в main
git branch -M main

# Загрузка на GitHub
git push -u origin main
```

## Шаг 5: Включение GitHub Pages
1. Перейдите в ваш репозиторий на GitHub
2. Нажмите на вкладку "Settings"
3. Прокрутите до раздела "Pages"
4. В разделе "Source" выберите "Deploy from a branch"
5. Выберите "main" branch и "/ (root)" folder
6. Нажмите "Save"

## Шаг 6: Доступ к сайту
Через несколько минут ваш сайт будет доступен по адресу:
`https://jfsagro-glitch.github.io/carshop-website`

## Дополнительные команды для обновления сайта

При внесении изменений в код:

```powershell
# Добавить изменения
git add .

# Создать коммит с описанием изменений
git commit -m "Описание изменений"

# Загрузить изменения на GitHub
git push
```

## Структура проекта
```
carshop-website/
├── index.html          # Главная страница
├── styles.css          # Стили CSS
├── script.js           # JavaScript код
├── images/             # Папка с изображениями
│   ├── logo.svg        # Логотип компании
│   ├── car1/           # Фото автомобиля 1
│   ├── car2/           # Фото автомобиля 2
│   └── ...             # Остальные автомобили
└── README.md           # Описание проекта
```

## Возможные проблемы и решения

### Ошибка авторизации
Если Git запрашивает логин и пароль:
1. Используйте Personal Access Token вместо пароля
2. Создайте токен в GitHub: Settings → Developer settings → Personal access tokens

### Файлы не загружаются
Убедитесь, что все файлы добавлены:
```powershell
git status
git add .
git commit -m "Add all files"
```

### Сайт не отображается
1. Проверьте настройки GitHub Pages в Settings → Pages
2. Убедитесь, что файл `index.html` находится в корне репозитория
3. Подождите 5-10 минут для обновления

## Контакты для поддержки
Если возникнут вопросы, обращайтесь:
- Телефон: +7 (915) 444-12-08
- Email: carexportgeo@bk.ru
