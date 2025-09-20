# Script to download photos from Google Drive folders
# Note: This requires manual download as Google Drive API needs authentication

$cars = @(
    @{id=1; brand="Lexus"; model="UX"; folderId="1FR5s24AvCCFwheEODFLvBXko11UaIBwx"; url="https://drive.google.com/drive/folders/1FR5s24AvCCFwheEODFLvBXko11UaIBwx"},
    @{id=2; brand="KIA"; model="K5 AWD"; folderId="1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"; url="https://drive.google.com/drive/folders/1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"},
    @{id=3; brand="KIA"; model="K5"; folderId="1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"; url="https://drive.google.com/drive/folders/1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"},
    @{id=4; brand="KIA"; model="K5 GT Line"; folderId="1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b"; url="https://drive.google.com/drive/folders/1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b"},
    @{id=5; brand="Chevrolet"; model="Equinox"; folderId="1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK"; url="https://drive.google.com/drive/folders/1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK"},
    @{id=6; brand="Chevrolet"; model="Equinox AWD"; folderId="1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT"; url="https://drive.google.com/drive/folders/1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT"},
    @{id=7; brand="Chevrolet"; model="Equinox"; folderId="1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB"; url="https://drive.google.com/drive/folders/1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB"},
    @{id=8; brand="Chevrolet"; model="Malibu"; folderId="1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud"; url="https://drive.google.com/drive/folders/1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud"},
    @{id=9; brand="Chevrolet"; model="Malibu"; folderId="1SLPy7kA6U3GHvmaWMCv1aLV1hgJp78ht"; url="https://drive.google.com/drive/folders/1SLPy7kA6U3GHvmaWMCv1aLV1hgJp78ht"},
    @{id=10; brand="Chevrolet"; model="Trax"; folderId="1AneTIy_JInzve71jMfyHRAaMmdmv0p9e"; url="https://drive.google.com/drive/folders/1AneTIy_JInzve71jMfyHRAaMmdmv0p9e"},
    @{id=11; brand="KIA"; model="Sportage"; folderId="1fndY8K0rjlF0JbqnNSl7KRF-kvpyfElP"; url="https://drive.google.com/drive/folders/1fndY8K0rjlF0JbqnNSl7KRF-kvpyfElP"},
    @{id=12; brand="KIA"; model="Sportage"; folderId="1vI6ngtd-7pS-Q6GZyx3cT1TAbLP02cJ2"; url="https://drive.google.com/drive/folders/1vI6ngtd-7pS-Q6GZyx3cT1TAbLP02cJ2"},
    @{id=13; brand="KIA"; model="Sportage"; folderId="1ktbbcV03TNaxOo85hcxdRI12cf48PDlA"; url="https://drive.google.com/drive/folders/1ktbbcV03TNaxOo85hcxdRI12cf48PDlA"},
    @{id=14; brand="Hyundai"; model="Elantra Limited"; folderId="1T_WJeiasoMStwqfsrrKCQMrqhauDO2HV"; url="https://drive.google.com/drive/folders/1T_WJeiasoMStwqfsrrKCQMrqhauDO2HV"},
    @{id=15; brand="Hyundai"; model="Elantra N Line"; folderId="11m3ri2m9na7jmqV-Zf2gRwhoXTga4Ruo"; url="https://drive.google.com/drive/folders/11m3ri2m9na7jmqV-Zf2gRwhoXTga4Ruo"},
    @{id=16; brand="BMW"; model="3 Series 330XI"; folderId="1wbbCZ90K5ph9vunmCnuQJTxSx2sqxQ8n"; url="https://drive.google.com/drive/folders/1wbbCZ90K5ph9vunmCnuQJTxSx2sqxQ8n"},
    @{id=17; brand="Volkswagen"; model="Passat R-Line"; folderId="1lts5r3t6ftPayg55mjSHdMbwRBGMoz78"; url="https://drive.google.com/drive/folders/1lts5r3t6ftPayg55mjSHdMbwRBGMoz78"},
    @{id=18; brand="Volkswagen"; model="Jetta 1.4T R-Line"; folderId="18gkgVMN3UWPXSSVtB73M1SUxj7Sd6BpG"; url="https://drive.google.com/drive/folders/18gkgVMN3UWPXSSVtB73M1SUxj7Sd6BpG"},
    @{id=19; brand="Subaru"; model="XV Crosstrek Premium"; folderId="1PMVX5wAq0amBEmIotp7DN0Xfvpb1bPHU"; url="https://drive.google.com/drive/folders/1PMVX5wAq0amBEmIotp7DN0Xfvpb1bPHU"},
    @{id=20; brand="KIA"; model="Forte LXS"; folderId="1PV5UOJxvCIn52_qrxFJdcvcWuiyE3yM4"; url="https://drive.google.com/drive/folders/1PV5UOJxvCIn52_qrxFJdcvcWuiyE3yM4"},
    @{id=21; brand="Honda"; model="Accord Sport SE"; folderId="1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H"; url="https://drive.google.com/drive/folders/1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H"},
    @{id=22; brand="Toyota"; model="Venza LE"; folderId="1PpnoOBW5SxQvATGHODbNrDco5SBFXgAc"; url="https://drive.google.com/drive/folders/1PpnoOBW5SxQvATGHODbNrDco5SBFXgAc"},
    @{id=23; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; folderId="1bv6Te0NZyRaskQVJ1bYJItgprQMYlbAZ"; url="https://drive.google.com/drive/folders/1bv6Te0NZyRaskQVJ1bYJItgprQMYlbAZ"},
    @{id=24; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; folderId="1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG"; url="https://drive.google.com/drive/folders/1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG"},
    @{id=25; brand="Mitsubishi"; model="Eclipse LE Limited 4WD"; folderId="1u9kNrW8mwUnRMku1O4hjx3bdVHcyCpKI"; url="https://drive.google.com/drive/folders/1u9kNrW8mwUnRMku1O4hjx3bdVHcyCpKI"},
    @{id=26; brand="Mitsubishi"; model="Eclipse ES 4WD"; folderId="1m4mktjJLI0feWy8EtHAuEBZB5OetMWqg"; url="https://drive.google.com/drive/folders/1m4mktjJLI0feWy8EtHAuEBZB5OetMWqg"},
    @{id=27; brand="Audi"; model="A4 Premium Plus 45"; folderId="1cZ0NU_NfNc8VKCBdRklkQBETifuKhMLe"; url="https://drive.google.com/drive/folders/1cZ0NU_NfNc8VKCBdRklkQBETifuKhMLe"},
    @{id=28; brand="BMW"; model="X2 Xdrive28I"; folderId="1G3wdYypzFOTNVuuUFiXwKnXZtu5y5VXl"; url="https://drive.google.com/drive/folders/1G3wdYypzFOTNVuuUFiXwKnXZtu5y5VXl"},
    @{id=29; brand="BMW"; model="X3 Sdrive30I"; folderId="1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG"; url="https://drive.google.com/drive/folders/1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG"},
    @{id=30; brand="BMW"; model="X3 Sdrive30I"; folderId="1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO"; url="https://drive.google.com/drive/folders/1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO"},
    @{id=31; brand="Audi"; model="Q3 Premium 40"; folderId="17TPAkN76U8TCT_l81FJbnpHJLyQGcwo2"; url="https://drive.google.com/drive/folders/17TPAkN76U8TCT_l81FJbnpHJLyQGcwo2"},
    @{id=32; brand="BMW"; model="X3 Xdrive30I"; folderId="12IE_Wr0f6VJ3h5wiFnyCQnzYhu8Fxgyu"; url="https://drive.google.com/drive/folders/12IE_Wr0f6VJ3h5wiFnyCQnzYhu8Fxgyu"},
    @{id=33; brand="Audi"; model="Q5 Premium 45"; folderId="1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl"; url="https://drive.google.com/drive/folders/1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl"}
)

Write-Host "=== ИНСТРУКЦИИ ПО СКАЧИВАНИЮ ФОТОГРАФИЙ ===" -ForegroundColor Green
Write-Host ""
Write-Host "Для каждого автомобиля:" -ForegroundColor Yellow
Write-Host "1. Откройте ссылку на Google Drive папку" -ForegroundColor Yellow
Write-Host "2. Скачайте все фотографии из папки" -ForegroundColor Yellow
Write-Host "3. Поместите их в соответствующую папку images/car[номер]/" -ForegroundColor Yellow
Write-Host "4. Переименуйте главное фото как 'main.jpg' или '1.jpg'" -ForegroundColor Yellow
Write-Host ""

foreach ($car in $cars) {
    Write-Host "=== АВТОМОБИЛЬ $($car.id): $($car.brand) $($car.model) ===" -ForegroundColor Cyan
    Write-Host "Папка: images/car$($car.id)/" -ForegroundColor White
    Write-Host "Ссылка: $($car.url)" -ForegroundColor Blue
    Write-Host ""
}

Write-Host "=== АВТОМАТИЧЕСКОЕ СОЗДАНИЕ СТРУКТУРЫ ===" -ForegroundColor Green

# Create download instructions for each car
foreach ($car in $cars) {
    $carFolder = "images\car$($car.id)"
    
    # Create download instructions file
    $instructions = @"
# Инструкции по скачиванию фотографий для $($car.brand) $($car.model)

## Ссылка на Google Drive:
$($car.url)

## Шаги:
1. Откройте ссылку выше в браузере
2. Скачайте все фотографии из папки
3. Поместите их в папку: $carFolder
4. Переименуйте главное фото как 'main.jpg'
5. Остальные фото назовите '2.jpg', '3.jpg', и т.д.

## Структура файлов:
- main.jpg (главное фото)
- 2.jpg, 3.jpg, 4.jpg... (дополнительные фото)

## После скачивания:
- Обновите код в script.js для отображения реальных фотографий
- Проверьте, что все изображения загружаются корректно
"@
    
    $instructions | Out-File -FilePath "$carFolder\DOWNLOAD_INSTRUCTIONS.txt" -Encoding UTF8
    
    Write-Host "Созданы инструкции для автомобиля $($car.id): $($car.brand) $($car.model)"
}

Write-Host ""
Write-Host "=== ГОТОВО! ===" -ForegroundColor Green
Write-Host "Инструкции по скачиванию созданы в каждой папке автомобиля." -ForegroundColor White
Write-Host "Следуйте инструкциям в файлах DOWNLOAD_INSTRUCTIONS.txt" -ForegroundColor White

