# 🚀 Быстрый старт - Размещение на GitHub

## Вариант 1: Автоматический скрипт (рекомендуется)

1. **Установите Git** (если не установлен):
   - Скачайте с https://git-scm.com/download/win
   - Установите с настройками по умолчанию

2. **Создайте репозиторий на GitHub**:
   - Перейдите на https://github.com/new
   - Название: `carshop-website`
   - Выберите "Public"
   - Нажмите "Create repository"

3. **Запустите скрипт**:
   ```powershell
   .\deploy_to_github.ps1 -GitHubUsername ВАШ_USERNAME
   ```

## Вариант 2: Ручные команды

```powershell
git init
git add .
git commit -m "Initial commit: CarExport website"
git remote add origin https://github.com/ВАШ_USERNAME/carshop-website.git
git branch -M main
git push -u origin main
```

## Включение GitHub Pages

1. Перейдите в Settings → Pages
2. Source: "Deploy from a branch"
3. Branch: "main", Folder: "/ (root)"
4. Save

## Результат

Сайт будет доступен по адресу:
`https://jfsagro-glitch.github.io/carshop-website`

---
*Полная инструкция в файле GITHUB_DEPLOYMENT_GUIDE.md*