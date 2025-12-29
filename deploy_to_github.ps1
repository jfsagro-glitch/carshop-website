# Скрипт для автоматической загрузки сайта на GitHub
# Убедитесь, что Git установлен и вы авторизованы в GitHub

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$RepositoryName = "carshop-website"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Начинаем загрузку сайта EXPO MIR на GitHub..." -ForegroundColor Green

# Проверяем наличие Git
try {
    git --version | Out-Null
    Write-Host "✅ Git найден" -ForegroundColor Green
} catch {
    Write-Host "❌ Git не установлен! Скачайте с https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# Проверяем, инициализирован ли репозиторий
if (-not (Test-Path ".git")) {
    Write-Host "📁 Инициализация Git репозитория..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "✅ Git репозиторий уже инициализирован" -ForegroundColor Green
}

# Добавляем все файлы
Write-Host "📦 Добавление файлов в Git..." -ForegroundColor Yellow
git add .

# Проверяем статус
$status = git status --porcelain
if ($status) {
    Write-Host "📝 Создание коммита..." -ForegroundColor Yellow
    git commit -m "Update EXPO MIR website with new features and logo"
} else {
    Write-Host "ℹ️ Нет изменений для коммита" -ForegroundColor Blue
}

# Настраиваем удаленный репозиторий
$remoteUrl = "https://github.com/$GitHubUsername/$RepositoryName.git"
Write-Host "🔗 Настройка удаленного репозитория: $remoteUrl" -ForegroundColor Yellow

try {
    git remote get-url origin | Out-Null
    Write-Host "🔄 Обновление URL удаленного репозитория..." -ForegroundColor Yellow
    git remote set-url origin $remoteUrl
} catch {
    Write-Host "➕ Добавление удаленного репозитория..." -ForegroundColor Yellow
    git remote add origin $remoteUrl
}

# Переименовываем ветку в main (если нужно)
try {
    git branch -M main
    Write-Host "✅ Ветка переименована в 'main'" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ Ветка уже называется 'main'" -ForegroundColor Blue
}

# Загружаем на GitHub
Write-Host "🚀 Загрузка на GitHub..." -ForegroundColor Yellow
try {
    git push -u origin main
    Write-Host "✅ Успешно загружено на GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Ваш сайт будет доступен по адресу:" -ForegroundColor Cyan
    Write-Host "   https://$GitHubUsername.github.io/$RepositoryName" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Не забудьте включить GitHub Pages:" -ForegroundColor Yellow
    Write-Host "   1. Перейдите в Settings → Pages" -ForegroundColor Gray
    Write-Host "   2. Выберите 'Deploy from a branch'" -ForegroundColor Gray
    Write-Host "   3. Выберите 'main' branch и '/ (root)' folder" -ForegroundColor Gray
    Write-Host "   4. Нажмите 'Save'" -ForegroundColor Gray
} catch {
    Write-Host "❌ Ошибка при загрузке на GitHub" -ForegroundColor Red
    Write-Host "Возможные причины:" -ForegroundColor Yellow
    Write-Host "• Неверный username или название репозитория" -ForegroundColor Gray
    Write-Host "• Репозиторий не создан на GitHub" -ForegroundColor Gray
    Write-Host "• Проблемы с авторизацией" -ForegroundColor Gray
    Write-Host ""
    Write-Host "💡 Создайте репозиторий на GitHub:" -ForegroundColor Cyan
    Write-Host "   https://github.com/new" -ForegroundColor White
}

Write-Host ""
Write-Host "📞 Контакты EXPO MIR:" -ForegroundColor Green
Write-Host "   Телефон: +7 (915) 444-12-08" -ForegroundColor Gray
Write-Host "   Email: carexportgeo@bk.ru" -ForegroundColor Gray

