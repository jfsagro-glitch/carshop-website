# 📁 Ручная загрузка на GitHub (без Git)

Поскольку Git не установлен, вот инструкция для загрузки файлов через веб-интерфейс GitHub:

## 🚀 Пошаговая инструкция

### Шаг 1: Создайте репозиторий на GitHub
1. Перейдите на https://github.com/jfsagro-glitch
2. Нажмите зеленую кнопку "New" или "+" → "New repository"
3. Название репозитория: `carshop-website`
4. Описание: `CarExport - Автомобили из Грузии с доставкой в Россию`
5. Выберите "Public"
6. Поставьте галочку "Add a README file"
7. Нажмите "Create repository"

### Шаг 2: Загрузите файлы
1. В созданном репозитории нажмите "uploading an existing file"
2. Перетащите или выберите все файлы из папки проекта:
   - `index.html`
   - `styles.css` 
   - `script.js`
   - `README.md`
   - `GITHUB_DEPLOYMENT_GUIDE.md`
   - `QUICK_START.md`
   - `MANUAL_UPLOAD_GUIDE.md`

### Шаг 3: Загрузите папку images
1. После загрузки основных файлов нажмите "Add file" → "Upload files"
2. Загрузите всю папку `images/` со всеми подпапками:
   - `images/logo.svg`
   - `images/car1/` (со всеми файлами внутри)
   - `images/car2/` (со всеми файлами внутри)
   - ... (все остальные папки car3-car33)

### Шаг 4: Включите GitHub Pages
1. Перейдите в Settings → Pages
2. В разделе "Source" выберите "Deploy from a branch"
3. Выберите "main" branch и "/ (root)" folder
4. Нажмите "Save"

### Шаг 5: Проверьте сайт
Через 5-10 минут ваш сайт будет доступен по адресу:
**https://jfsagro-glitch.github.io/carshop-website**

## 📋 Список файлов для загрузки

### Основные файлы:
- ✅ `index.html` - главная страница
- ✅ `styles.css` - стили
- ✅ `script.js` - JavaScript код
- ✅ `README.md` - описание проекта
- ✅ `GITHUB_DEPLOYMENT_GUIDE.md` - инструкция по деплою
- ✅ `QUICK_START.md` - быстрый старт
- ✅ `MANUAL_UPLOAD_GUIDE.md` - эта инструкция

### Папка images/:
- ✅ `images/logo.svg` - логотип
- ✅ `images/car1/` - фото автомобиля 1
- ✅ `images/car2/` - фото автомобиля 2
- ✅ ... (все папки car3-car33)
- ✅ `images/car33/` - фото автомобиля 33

## ⚠️ Важные замечания

1. **Структура папок**: Сохраните структуру папок точно как в проекте
2. **Все файлы**: Загрузите ВСЕ файлы, включая car-info.json в каждой папке
3. **Порядок загрузки**: Сначала основные файлы, потом папку images
4. **Проверка**: Убедитесь, что все 33 папки с автомобилями загружены

## 🔧 Альтернатива: Установка Git

Если хотите использовать автоматическую загрузку:
1. Скачайте Git: https://git-scm.com/download/win
2. Установите с настройками по умолчанию
3. Перезапустите PowerShell
4. Запустите: `.\deploy_to_github.ps1 -GitHubUsername jfsagro-glitch`

## 📞 Поддержка

Если возникнут вопросы:
- Телефон: +7 (915) 444-12-08
- Email: carexportgeo@bk.ru

---

**Ваш сайт CarExport будет доступен по адресу:**
**https://jfsagro-glitch.github.io/carshop-website**

