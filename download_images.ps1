# Скрипт для скачивания изображений автомобилей
# Создаем папки для каждого автомобиля
$cars = @(
    @{id=1; brand="Lexus"; model="UX"; folderId="1FR5s24AvCCFwheEODFLvBXko11UaIBwx"},
    @{id=2; brand="KIA"; model="K5 AWD"; folderId="1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"},
    @{id=3; brand="KIA"; model="K5"; folderId="1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"},
    @{id=4; brand="KIA"; model="K5 GT Line"; folderId="1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b"},
    @{id=5; brand="Chevrolet"; model="Equinox"; folderId="1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK"},
    @{id=6; brand="Chevrolet"; model="Equinox AWD"; folderId="1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT"},
    @{id=7; brand="Chevrolet"; model="Equinox"; folderId="1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB"},
    @{id=8; brand="Chevrolet"; model="Malibu"; folderId="1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud"},
    @{id=9; brand="Chevrolet"; model="Malibu"; folderId="1SLPy7kA6U3GHvmaWMCv1aLV1hgJp78ht"},
    @{id=10; brand="Chevrolet"; model="Trax"; folderId="1AneTIy_JInzve71jMfyHRAaMmdmv0p9e"},
    @{id=11; brand="KIA"; model="Sportage"; folderId="1fndY8K0rjlF0JbqnNSl7KRF-kvpyfElP"},
    @{id=12; brand="KIA"; model="Sportage"; folderId="1vI6ngtd-7pS-Q6GZyx3cT1TAbLP02cJ2"},
    @{id=13; brand="KIA"; model="Sportage"; folderId="1ktbbcV03TNaxOo85hcxdRI12cf48PDlA"},
    @{id=14; brand="Hyundai"; model="Elantra Limited"; folderId="1T_WJeiasoMStwqfsrrKCQMrqhauDO2HV"},
    @{id=15; brand="Hyundai"; model="Elantra N Line"; folderId="11m3ri2m9na7jmqV-Zf2gRwhoXTga4Ruo"},
    @{id=16; brand="BMW"; model="3 Series 330XI"; folderId="1wbbCZ90K5ph9vunmCnuQJTxSx2sqxQ8n"},
    @{id=17; brand="Volkswagen"; model="Passat R-Line"; folderId="1lts5r3t6ftPayg55mjSHdMbwRBGMoz78"},
    @{id=18; brand="Volkswagen"; model="Jetta 1.4T R-Line"; folderId="18gkgVMN3UWPXSSVtB73M1SUxj7Sd6BpG"},
    @{id=19; brand="Subaru"; model="XV Crosstrek Premium"; folderId="1PMVX5wAq0amBEmIotp7DN0Xfvpb1bPHU"},
    @{id=20; brand="KIA"; model="Forte LXS"; folderId="1PV5UOJxvCIn52_qrxFJdcvcWuiyE3yM4"},
    @{id=21; brand="Honda"; model="Accord Sport SE"; folderId="1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H"},
    @{id=22; brand="Toyota"; model="Venza LE"; folderId="1PpnoOBW5SxQvATGHODbNrDco5SBFXgAc"},
    @{id=23; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; folderId="1bv6Te0NZyRaskQVJ1bYJItgprQMYlbAZ"},
    @{id=24; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; folderId="1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG"},
    @{id=25; brand="Mitsubishi"; model="Eclipse LE Limited 4WD"; folderId="1u9kNrW8mwUnRMku1O4hjx3bdVHcyCpKI"},
    @{id=26; brand="Mitsubishi"; model="Eclipse ES 4WD"; folderId="1m4mktjJLI0feWy8EtHAuEBZB5OetMWqg"},
    @{id=27; brand="Audi"; model="A4 Premium Plus 45"; folderId="1cZ0NU_NfNc8VKCBdRklkQBETifuKhMLe"},
    @{id=28; brand="BMW"; model="X2 Xdrive28I"; folderId="1G3wdYypzFOTNVuuUFiXwKnXZtu5y5VXl"},
    @{id=29; brand="BMW"; model="X3 Sdrive30I"; folderId="1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG"},
    @{id=30; brand="BMW"; model="X3 Sdrive30I"; folderId="1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO"},
    @{id=31; brand="Audi"; model="Q3 Premium 40"; folderId="17TPAkN76U8TCT_l81FJbnpHJLyQGcwo2"},
    @{id=32; brand="BMW"; model="X3 Xdrive30I"; folderId="12IE_Wr0f6VJ3h5wiFnyCQnzYhu8Fxgyu"},
    @{id=33; brand="Audi"; model="Q5 Premium 45"; folderId="1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl"}
)

# Создаем заглушки изображений для каждого автомобиля
foreach ($car in $cars) {
    $carFolder = "images\car$($car.id)"
    
    # Создаем заглушку изображения
    $placeholderContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>$($car.brand) $($car.model) - Фотографии</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #1f2937; 
            color: #f3f4f6; 
            text-align: center; 
            padding: 2rem;
        }
        .car-info {
            background: #374151;
            padding: 2rem;
            border-radius: 12px;
            margin: 2rem 0;
        }
        .placeholder {
            background: #4b5563;
            padding: 3rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        .btn {
            background: #6b7280;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            margin: 1rem;
        }
    </style>
</head>
<body>
    <h1>$($car.brand) $($car.model)</h1>
    <div class="car-info">
        <h2>Фотографии автомобиля</h2>
        <div class="placeholder">
            <h3>📸 Фотографии загружаются...</h3>
            <p>Ссылка на Google Drive: <a href="https://drive.google.com/drive/folders/$($car.folderId)" target="_blank">Открыть папку</a></p>
        </div>
        <a href="https://drive.google.com/drive/folders/$($car.folderId)" target="_blank" class="btn">Посмотреть все фотографии</a>
    </div>
</body>
</html>
"@
    
    # Сохраняем заглушку
    $placeholderContent | Out-File -FilePath "$carFolder\index.html" -Encoding UTF8
    
    # Создаем файл с информацией об автомобиле
    $carInfo = @{
        id = $car.id
        brand = $car.brand
        model = $car.model
        folderId = $car.folderId
        googleDriveUrl = "https://drive.google.com/drive/folders/$($car.folderId)"
    }
    
    $carInfo | ConvertTo-Json | Out-File -FilePath "$carFolder\car-info.json" -Encoding UTF8
    
    Write-Host "Создана папка для автомобиля $($car.id): $($car.brand) $($car.model)"
}

Write-Host "Все папки для автомобилей созданы!"
Write-Host "Теперь вы можете вручную скачать фотографии из Google Drive папок и поместить их в соответствующие папки images\car1, images\car2, и т.д."

