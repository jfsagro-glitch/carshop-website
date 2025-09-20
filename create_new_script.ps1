# Create a new script.js with correct prices and encoding
Write-Host "Creating new script.js with correct prices..." -ForegroundColor Green

$newScriptContent = @"
// Функция для получения прямых ссылок на изображения из Google Drive
function getGoogleDriveImageUrl(folderId) {
    // Для Google Drive папок используем специальный формат
    return `https://drive.google.com/thumbnail?id=${folderId}&sz=w400-h300`;
}

// Функция для получения ID папки из Google Drive ссылки
function extractFolderId(url) {
    const match = url.match(/folders\/([a-zA-Z0-9_-]+)/);
    return match ? match[1] : null;
}

// Функция для создания галереи с реальными фотографиями
function createCarGallery(car) {
    return `
        <div class="car-gallery" style="position: relative; margin-bottom: 1rem;">
            <div class="gallery-container" style="position: relative; width: 100%; height: 500px; overflow: hidden; border-radius: 8px; background: #374151;">
                <!-- Попытка загрузить реальное фото -->
                <img 
                    src="images/car${car.id}/main.jpg" 
                    alt="${car.year} ${car.brand} ${car.model}"
                    style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;"
                    onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'">
                
                <!-- Fallback если фото не загрузилось -->
                <div class="gallery-fallback" style="display: none; width: 100%; height: 500px; background: linear-gradient(135deg, #374151 0%, #4b5563 100%); align-items: center; justify-content: center; color: #f3f4f6; flex-direction: column;">
                    <div style="text-align: center;">
                        <div style="font-size: 6rem; margin-bottom: 1rem;">🚗</div>
                        <h3 style="color: #f3f4f6; margin-bottom: 0.5rem; font-size: 1.5rem;">${car.year} ${car.brand} ${car.model}</h3>
                        <p style="color: #9ca3af; margin-bottom: 1.5rem;">Фотографии автомобиля</p>
                        <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                            <div style="background: #6b7280; color: #f3f4f6; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.9rem;">
                                <i class="fas fa-images"></i> Галерея
                            </div>
                            <div style="background: #6b7280; color: #f3f4f6; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.9rem;">
                                <i class="fas fa-camera"></i> Фото
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 1rem;">
                <a href="${car.photos}" target="_blank" style="background: #4b5563; color: #f3f4f6; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; display: inline-block; border: 1px solid #6b7280; transition: all 0.3s;" onmouseover="this.style.background='#6b7280'" onmouseout="this.style.background='#4b5563'">
                    <i class="fas fa-external-link-alt"></i> Открыть в Google Drive
                </a>
            </div>
        </div>
    `;
}


// Данные автомобилей
const carsData = [
    {
        id: 1,
        brand: "Lexus",
        model: "UX",
        year: 2021,
        engine: "200",
        vin: "JTHX3JBH2M2040913",
        price: 2530000, // Включает растаможку и доставку
        mileage: 62400,
        date: "01.04.2021",
        photos: "https://drive.google.com/drive/folders/1FR5s24AvCCFwheEODFLvBXko11UaIBwx?usp=sharing",
        folderId: "1FR5s24AvCCFwheEODFLvBXko11UaIBwx"
    },
    {
        id: 2,
        brand: "KIA",
        model: "K5 AWD",
        year: 2021,
        engine: "1,6",
        vin: "5XXG64J21MG051872",
        price: 1800000, // Включает растаможку и доставку
        mileage: 71300,
        date: "01.12.2020",
        photos: "https://drive.google.com/drive/folders/1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE?usp=sharing",
        folderId: "1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"
    },
    {
        id: 3,
        brand: "KIA",
        model: "K5",
        year: 2021,
        engine: "1,6",
        vin: "5XXG64J20MG066301",
        price: 1950000, // Включает растаможку и доставку
        mileage: 85300,
        date: "01.02.2021",
        photos: "https://drive.google.com/drive/folders/1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67?usp=sharing",
        folderId: "1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"
    },
    {
        id: 4,
        brand: "KIA",
        model: "K5 GT Line",
        year: 2022,
        engine: "1,6",
        vin: "5XXG64J26NG143772",
        price: 1920000, // Включает растаможку и доставку
        mileage: 89000,
        date: "01.02.2022",
        photos: "https://drive.google.com/drive/folders/1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b?usp=sharing",
        folderId: "1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b"
    },
    {
        id: 5,
        brand: "Chevrolet",
        model: "Equinox",
        year: 2022,
        engine: "1,5",
        vin: "3GNAXKEV2NL254391",
        price: 1830000, // Включает растаможку и доставку
        mileage: 22800,
        date: "01.06.2022",
        photos: "https://drive.google.com/drive/folders/1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK?usp=sharing",
        folderId: "1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK"
    },
    {
        id: 6,
        brand: "Chevrolet",
        model: "Equinox AWD",
        year: 2022,
        engine: "1,5",
        vin: "3GNAXUEV7NL295692",
        price: 1830000, // Включает растаможку и доставку
        mileage: 25400,
        date: "01.08.2022",
        photos: "https://drive.google.com/drive/folders/1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT?usp=sharing",
        folderId: "1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT"
    },
    {
        id: 7,
        brand: "Chevrolet",
        model: "Equinox",
        year: 2021,
        engine: "1,5",
        vin: "2GNAXKEV6M6147749",
        price: 1490000, // Включает растаможку и доставку
        mileage: 99000,
        date: "01.01.2021",
        photos: "https://drive.google.com/drive/folders/1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB?usp=sharing",
        folderId: "1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB"
    },
    {
        id: 8,
        brand: "Chevrolet",
        model: "Malibu",
        year: 2022,
        engine: "1,5",
        vin: "1G1ZD5ST8NF204106",
        price: 1420000, // Включает растаможку и доставку
        mileage: 52800,
        date: "01.09.2022",
        photos: "https://drive.google.com/drive/folders/1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud?usp=sharing",
        folderId: "1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud"
    },
    {
        id: 9,
        brand: "Chevrolet",
        model: "Malibu",
        year: 2022,
        engine: "1,5",
        vin: "1G1ZD5ST7NF142830",
        price: 1320000, // Включает растаможку и доставку
        mileage: 65000,
        date: "01.04.2022",
        photos: "https://drive.google.com/drive/folders/1SLPy7kA6U3GHvmaWMCv1aLV1hgJp78ht?usp=sharing",
        folderId: "1SLPy7kA6U3GHvmaWMCv1aLV1hgJp78ht"
    },
    {
        id: 10,
        brand: "Chevrolet",
        model: "Trax",
        year: 2021,
        engine: "1,4",
        vin: "KL7CJPSB3MB359450",
        price: 1260000, // Включает растаможку и доставку
        mileage: 53700,
        date: "01.02.2021",
        photos: "https://drive.google.com/drive/folders/1AneTIy_JInzve71jMfyHRAaMmdmv0p9e?usp=sharing",
        folderId: "1AneTIy_JInzve71jMfyHRAaMmdmv0p9e"
    },
    {
        id: 11,
        brand: "KIA",
        model: "Sportage",
        year: 2022,
        engine: "2,0",
        vin: "KNDPRCA6XN7979842",
        price: 2110000, // Включает растаможку и доставку
        mileage: 76000,
        date: "01.05.2021",
        photos: "https://drive.google.com/drive/folders/1fndY8K0rjlF0JbqnNSl7KRF-kvpyfElP?usp=sharing",
        folderId: "1fndY8K0rjlF0JbqnNSl7KRF-kvpyfElP"
    },
    {
        id: 12,
        brand: "KIA",
        model: "Sportage",
        year: 2021,
        engine: "2,4",
        vin: "KNDPMCAC6N7951184",
        price: 2010000, // Включает растаможку и доставку
        mileage: 80000,
        date: "01.03.2021",
        photos: "https://drive.google.com/drive/folders/1vI6ngtd-7pS-Q6GZyx3cT1TAbLP02cJ2?usp=sharing",
        folderId: "1vI6ngtd-7pS-Q6GZyx3cT1TAbLP02cJ2"
    },
    {
        id: 13,
        brand: "KIA",
        model: "Sportage",
        year: 2021,
        engine: "2,4",
        vin: "KNDPMCAC1N7022584",
        price: 2030000, // Включает растаможку и доставку
        mileage: 25600,
        date: "01.11.2021",
        photos: "https://drive.google.com/drive/folders/1ktbbcV03TNaxOo85hcxdRI12cf48PDlA?usp=sharing",
        folderId: "1ktbbcV03TNaxOo85hcxdRI12cf48PDlA"
    },
    {
        id: 14,
        brand: "Hyundai",
        model: "Elantra Limited",
        year: 2021,
        engine: "1,6",
        vin: "5NPLP4AG4MH039503",
        price: 1770000, // Включает растаможку и доставку
        mileage: 70400,
        date: "01.04.2021",
        photos: "https://drive.google.com/drive/folders/1T_WJeiasoMStwqfsrrKCQMrqhauDO2HV?usp=sharing",
        folderId: "1T_WJeiasoMStwqfsrrKCQMrqhauDO2HV"
    },
    {
        id: 15,
        brand: "Hyundai",
        model: "Elantra N Line",
        year: 2022,
        engine: "1,6",
        vin: "KMHLR4AF0NU363102",
        price: 1880000, // Включает растаможку и доставку
        mileage: 44600,
        date: "01.04.2021",
        photos: "https://drive.google.com/drive/folders/11m3ri2m9na7jmqV-Zf2gRwhoXTga4Ruo?usp=sharing",
        folderId: "11m3ri2m9na7jmqV-Zf2gRwhoXTga4Ruo"
    },
    {
        id: 16,
        brand: "BMW",
        model: "3 Series 330XI",
        year: 2021,
        engine: "2,0",
        vin: "3MW5R7J0XM8B93091",
        price: 3150000, // Включает растаможку и доставку
        mileage: 79000,
        date: "01.03.2021",
        photos: "https://drive.google.com/drive/folders/1wbbCZ90K5ph9vunmCnuQJTxSx2sqxQ8n?usp=sharing",
        folderId: "1wbbCZ90K5ph9vunmCnuQJTxSx2sqxQ8n"
    },
    {
        id: 17,
        brand: "Volkswagen",
        model: "Passat R-Line",
        year: 2021,
        engine: "2,0",
        vin: "1VWMA7A31MC010344",
        price: 1960000, // Включает растаможку и доставку
        mileage: 75000,
        date: "01.03.2021",
        photos: "https://drive.google.com/drive/folders/1lts5r3t6ftPayg55mjSHdMbwRBGMoz78?usp=sharing",
        folderId: "1lts5r3t6ftPayg55mjSHdMbwRBGMoz78"
    },
    {
        id: 18,
        brand: "Volkswagen",
        model: "Jetta 1.4T R-Line",
        year: 2021,
        engine: "1,4",
        vin: "3VWC57BUXMM099157",
        price: 1390000, // Включает растаможку и доставку
        mileage: 67200,
        date: "01.12.2021",
        photos: "https://drive.google.com/drive/folders/18gkgVMN3UWPXSSVtB73M1SUxj7Sd6BpG?usp=sharing",
        folderId: "18gkgVMN3UWPXSSVtB73M1SUxj7Sd6BpG"
    },
    {
        id: 19,
        brand: "Subaru",
        model: "XV Crosstrek Premium",
        year: 2022,
        engine: "2,0",
        vin: "JF2GTAPC6N8230227",
        price: 1730000, // Включает растаможку и доставку
        mileage: 89000,
        date: "01.01.2022",
        photos: "https://drive.google.com/drive/folders/1PMVX5wAq0amBEmIotp7DN0Xfvpb1bPHU?usp=sharing",
        folderId: "1PMVX5wAq0amBEmIotp7DN0Xfvpb1bPHU"
    },
    {
        id: 20,
        brand: "KIA",
        model: "Forte LXS",
        year: 2021,
        engine: "2,0",
        vin: "3KPF24AD3ME354590",
        price: 1480000, // Включает растаможку и доставку
        mileage: 23195,
        date: "01.03.2021",
        photos: "https://drive.google.com/drive/folders/1PV5UOJxvCIn52_qrxFJdcvcWuiyE3yM4?usp=sharing",
        folderId: "1PV5UOJxvCIn52_qrxFJdcvcWuiyE3yM4"
    },
    {
        id: 21,
        brand: "Honda",
        model: "Accord Sport SE",
        year: 2022,
        engine: "1,5",
        vin: "1HGCV1F43NA097759",
        price: 1910000, // Включает растаможку и доставку
        mileage: 92000,
        date: "01.10.2022",
        photos: "https://drive.google.com/drive/folders/1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H?usp=sharing",
        folderId: "1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H"
    },
    {
        id: 22,
        brand: "Toyota",
        model: "Venza LE",
        year: 2021,
        engine: "2,5",
        vin: "JTEAAAAH4MJ071578",
        price: 2520000, // Включает растаможку и доставку
        mileage: 67000,
        date: "01.08.2021",
        photos: "https://drive.google.com/drive/folders/1PpnoOBW5SxQvATGHODbNrDco5SBFXgAc?usp=sharing",
        folderId: "1PpnoOBW5SxQvATGHODbNrDco5SBFXgAc"
    },
    {
        id: 23,
        brand: "Mitsubishi",
        model: "Outlander Sport 2.0 4WD Limited",
        year: 2022,
        engine: "2,0",
        vin: "JA4ARUAU4NU014433",
        price: 1590000, // Включает растаможку и доставку
        mileage: 84000,
        date: "01.04.2022",
        photos: "https://drive.google.com/drive/folders/1bv6Te0NZyRaskQVJ1bYJItgprQMYlbAZ?usp=sharing",
        folderId: "1bv6Te0NZyRaskQVJ1bYJItgprQMYlbAZ"
    },
    {
        id: 24,
        brand: "Mitsubishi",
        model: "Outlander Sport 2.0 4WD Limited",
        year: 2021,
        engine: "2,0",
        vin: "JA4ARUAU8MU024316",
        price: 1750000, // Включает растаможку и доставку
        mileage: 93600,
        date: "01.02.2021",
        photos: "https://drive.google.com/drive/folders/1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG?usp=sharing",
        folderId: "1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG"
    },
    {
        id: 25,
        brand: "Mitsubishi",
        model: "Eclipse LE Limited 4WD",
        year: 2021,
        engine: "2,4",
        vin: "JA4ATVAA9NZ001578",
        price: 1700000, // Включает растаможку и доставку
        mileage: 83300,
        date: "01.01.2021",
        photos: "https://drive.google.com/drive/folders/1u9kNrW8mwUnRMku1O4hjx3bdVHcyCpKI?usp=sharing",
        folderId: "1u9kNrW8mwUnRMku1O4hjx3bdVHcyCpKI"
    },
    {
        id: 26,
        brand: "Mitsubishi",
        model: "Eclipse ES 4WD",
        year: 2021,
        engine: "2,4",
        vin: "JA4ATUAA6NZ055186",
        price: 1680000, // Включает растаможку и доставку
        mileage: 80600,
        date: "01.11.2021",
        photos: "https://drive.google.com/drive/folders/1m4mktjJLI0feWy8EtHAuEBZB5OetMWqg?usp=sharing",
        folderId: "1m4mktjJLI0feWy8EtHAuEBZB5OetMWqg"
    },
    {
        id: 27,
        brand: "Audi",
        model: "A4 Premium Plus 45",
        year: 2022,
        engine: "2,0",
        vin: "WAUEAAF44NN014025",
        price: 3070000, // Включает растаможку и доставку
        mileage: 93000,
        date: "01.05.2022",
        photos: "https://drive.google.com/drive/folders/1cZ0NU_NfNc8VKCBdRklkQBETifuKhMLe?usp=sharing",
        folderId: "1cZ0NU_NfNc8VKCBdRklkQBETifuKhMLe"
    },
    {
        id: 28,
        brand: "BMW",
        model: "X2 Xdrive28I",
        year: 2021,
        engine: "2,0",
        vin: "WBXYJ1C00N5U30528",
        price: 2360000, // Включает растаможку и доставку
        mileage: 108000,
        date: "01.09.2021",
        photos: "https://drive.google.com/drive/folders/1G3wdYypzFOTNVuuUFiXwKnXZtu5y5VXl?usp=sharing",
        folderId: "1G3wdYypzFOTNVuuUFiXwKnXZtu5y5VXl"
    },
    {
        id: 29,
        brand: "BMW",
        model: "X3 Sdrive30I",
        year: 2021,
        engine: "2,0",
        vin: "5UX43DP0XN9J97749",
        price: 3240000, // Включает растаможку и доставку
        mileage: 41500,
        date: "01.10.2021",
        photos: "https://drive.google.com/drive/folders/1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG?usp=sharing",
        folderId: "1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG"
    },
    {
        id: 30,
        brand: "BMW",
        model: "X3 Sdrive30I",
        year: 2022,
        engine: "2,0",
        vin: "5UX43DP04N9L08991",
        price: 3490000, // Включает растаможку и доставку
        mileage: 11500,
        date: "01.01.2022",
        photos: "https://drive.google.com/drive/folders/1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO?usp=sharing",
        folderId: "1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO"
    },
    {
        id: 31,
        brand: "Audi",
        model: "Q3 Premium 40",
        year: 2021,
        engine: "2,0",
        vin: "A1AUCF31N1001715",
        price: 2940000, // Включает растаможку и доставку
        mileage: 44500,
        date: "01.06.2021",
        photos: "https://drive.google.com/drive/folders/17TPAkN76U8TCT_l81FJbnpHJLyQGcwo2?usp=sharing",
        folderId: "17TPAkN76U8TCT_l81FJbnpHJLyQGcwo2"
    },
    {
        id: 32,
        brand: "BMW",
        model: "X3 Xdrive30I",
        year: 2021,
        engine: "2,0",
        vin: "5UXTY5C00M9G20624",
        price: 3030000, // Включает растаможку и доставку
        mileage: 105500,
        date: "01.03.2021",
        photos: "https://drive.google.com/drive/folders/12IE_Wr0f6VJ3h5wiFnyCQnzYhu8Fxgyu?usp=sharing",
        folderId: "12IE_Wr0f6VJ3h5wiFnyCQnzYhu8Fxgyu"
    },
    {
        id: 33,
        brand: "Audi",
        model: "Q5 Premium 45",
        year: 2022,
        engine: "2,0",
        vin: "WA1GAAFY8N2089627",
        price: 3110000, // Включает растаможку и доставку
        mileage: 45000,
        date: "01.03.2022",
        photos: "https://drive.google.com/drive/folders/1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl?usp=sharing",
        folderId: "1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl"
    }
];

// Continue with the rest of the script...
"@

# Save the new script content
$newScriptContent | Out-File "script_new.js" -Encoding UTF8

Write-Host "Created new script_new.js with correct prices!" -ForegroundColor Green
Write-Host "Now copying the rest of the original script..." -ForegroundColor Yellow

# Read the original script to get the rest of the functions
$originalScript = Get-Content "script.js" -Raw
$restOfScript = $originalScript -replace ".*// Р"Р°РЅРЅС‹Рµ Р°РІС‚РѕРјРѕР±РёР»РµР№.*?];", "", "Singleline"

# Append the rest of the script
$completeScript = $newScriptContent + $restOfScript
$completeScript | Out-File "script.js" -Encoding UTF8

Write-Host "Complete script.js updated with correct prices and encoding!" -ForegroundColor Green

