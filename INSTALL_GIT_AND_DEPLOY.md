# 🚀 Загрузка сайта на GitHub - Полная инструкция

## ❌ Проблема
Git не установлен в системе, поэтому автоматическая загрузка невозможна.

## ✅ Решение: Установка Git + Автоматическая загрузка

### Шаг 1: Установите Git
1. **Скачайте Git для Windows:**
   - Перейдите на https://git-scm.com/download/win
   - Скачайте "64-bit Git for Windows Setup"
   - Запустите установщик

2. **Настройки установки (важно!):**
   - ✅ Use Git from the command line and also from 3rd-party software
   - ✅ Use the OpenSSL library
   - ✅ Checkout Windows-style, commit Unix-style line endings
   - ✅ Use Windows' default console window
   - ✅ Enable file system caching
   - ✅ Enable Git Credential Manager

3. **Завершите установку** и перезагрузите компьютер

### Шаг 2: Проверьте установку
Откройте PowerShell и выполните:
```powershell
git --version
```
Должно показать версию Git.

### Шаг 3: Автоматическая загрузка
После установки Git выполните в PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File deploy_simple.ps1 -GitHubUsername jfsagro-glitch
```

---

## 🔄 Альтернатива: Ручная загрузка (без Git)

Если не хотите устанавливать Git, используйте ручную загрузку:

### 1. Создайте репозиторий на GitHub
- Перейдите на https://github.com/new
- Название: `carshop-website`
- Тип: Public
- Нажмите "Create repository"

### 2. Загрузите файлы через веб-интерфейс
1. В созданном репозитории нажмите "uploading an existing file"
2. Перетащите все файлы из папки проекта:
   - `index.html`
   - `styles.css`
   - `script.js`
   - `README.md`
   - Все файлы `.md`
3. Загрузите папку `images/` со всеми подпапками

### 3. Включите GitHub Pages
- Settings → Pages
- Source: "Deploy from a branch"
- Branch: "main"
- Folder: "/ (root)"
- Save

---

## 🌐 Результат
После выполнения любого из вариантов ваш сайт будет доступен по адресу:
**https://jfsagro-glitch.github.io/carshop-website**

---

## 📞 Поддержка
- Телефон: +7 (915) 444-12-08
- Email: carexportgeo@bk.ru

**Рекомендую установить Git - это займет 5 минут, но упростит все будущие обновления сайта!**

