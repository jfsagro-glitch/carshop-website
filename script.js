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
    // Локальная галерея со свайпом и стрелками, без ссылок на Google Drive
    return `
        <div class="car-gallery" style="position: relative; margin-bottom: 1rem;">
            <div id="gallery-${car.id}" class="gallery-container" data-car-id="${car.id}" style="position: relative; width: 100%; height: 500px; overflow: hidden; border-radius: 8px; background: #374151;">
                <div class="gallery-track" style="display: flex; width: 100%; height: 100%; transition: transform 0.3s ease;"></div>
                <button class="gallery-prev" onclick="prevPhoto(${car.id})" aria-label="Предыдущая" style="position:absolute;left:12px;top:50%;transform:translateY(-50%);background:rgba(0,0,0,0.4);color:#fff;border:none;width:40px;height:40px;border-radius:50%;cursor:pointer;">‹</button>
                <button class="gallery-next" onclick="nextPhoto(${car.id})" aria-label="Следующая" style="position:absolute;right:12px;top:50%;transform:translateY(-50%);background:rgba(0,0,0,0.4);color:#fff;border:none;width:40px;height:40px;border-radius:50%;cursor:pointer;">›</button>
                <div id="gallery-dots-${car.id}" style="position:absolute;bottom:12px;left:50%;transform:translateX(-50%);display:flex;gap:6px;"></div>
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
        price: 2530000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1800000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1950000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1920000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1830000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1830000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1490000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1420000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1320000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1260000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 2110000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 2010000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1770000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1880000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1960000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1390000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1730000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1480000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1910000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1590000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1750000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1700000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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
        price: 1680000, // Р’РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ
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

// Р“Р»РѕР±Р°Р»СЊРЅС‹Рµ РїРµСЂРµРјРµРЅРЅС‹Рµ
let cart = [];
let filteredCars = [...carsData];
// Состояние галерей по carId
const carGalleries = {};

// РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РїСЂРё Р·Р°РіСЂСѓР·РєРµ СЃС‚СЂР°РЅРёС†С‹
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    loadCars();
    populateBrandFilter();
    updateCartCount();
    setupEventListeners();
    // Обработчики свайпа для всех галерей (делегирование)
    document.addEventListener('touchstart', onTouchStart, { passive: true });
    document.addEventListener('touchmove', onTouchMove, { passive: true });
    document.addEventListener('touchend', onTouchEnd, { passive: true });
}

function openCheckoutModal(){
    document.getElementById('checkoutModal').style.display = 'block';
}
function closeCheckoutModal(){
    document.getElementById('checkoutModal').style.display = 'none';
}

function loadCars() {
    const carsGrid = document.getElementById('carsGrid');
    carsGrid.innerHTML = '';

    filteredCars.forEach(car => {
        const carCard = createCarCard(car);
        carsGrid.appendChild(carCard);
    });
}

function createCarCard(car) {
    const card = document.createElement('div');
    card.className = 'car-card';
    
    // Локальный предпросмотр первой фотографии, без ссылок на Google Drive
    
    card.innerHTML = `
        <div class="car-image">
            <div class="single-photo-container" style="position: relative; width: 100%; height: 400px; overflow: hidden; border-radius: 8px; background: #374151; cursor: pointer;" onclick="showCarDetails(${car.id})">
                <!-- Попытка загрузить реальное фото -->
                <img 
                    src="images/car${car.id}/main.jpg" 
                    alt="${car.year} ${car.brand} ${car.model}"
                    style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;"
                    onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'">
                
                <!-- Fallback если фото не загрузилось -->
                <div class="car-image-fallback" style="display: none; width: 100%; height: 400px; background: linear-gradient(135deg, #374151 0%, #4b5563 100%); align-items: center; justify-content: center; color: #f3f4f6; flex-direction: column;">
                    <div style="text-align: center;">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">🚗</div>
                        <h4 style="color: #f3f4f6; margin-bottom: 0.5rem; font-size: 1.2rem;">${car.year} ${car.brand} ${car.model}</h4>
                        <p style="color: #9ca3af; margin-bottom: 1rem; font-size: 0.9rem;">Нажмите для просмотра галереи</p>
                        <div style="background: #6b7280; color: #f3f4f6; padding: 0.5rem 1rem; border-radius: 6px; display: inline-block; font-size: 0.9rem;">
                            <i class="fas fa-images"></i> Галерея
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="car-info">
            <h3 class="car-title">${car.year} ${car.brand} ${car.model}</h3>
            <div class="car-details">
                <div><strong>Двигатель:</strong> ${car.engine}L</div>
                <div><strong>Пробег:</strong> ${car.mileage.toLocaleString()} км</div>
                <div><strong>VIN:</strong> <a href="https://bid.cars/?s=${car.vin}" target="_blank" rel="noopener">${car.vin}</a></div>
                <div><strong>Дата выпуска:</strong> ${car.date}</div>
            </div>
            <div class="car-price">${car.price.toLocaleString()} ₽</div>
            <div class="price-note" style="font-size: 0.8rem; color: #10b981; margin-bottom: 1rem;">
                <i class="fas fa-check-circle"></i> Включает растаможку и доставку
            </div>
            <div class="car-actions">
                <button class="btn-primary" onclick="addToCart(${car.id})">
                    <i class="fas fa-shopping-cart"></i> Заказать
                </button>
                <button class="btn-secondary" onclick="showCarDetails(${car.id})">
                    <i class="fas fa-eye"></i> Подробнее
                </button>
            </div>
        </div>
    `;
    return card;
}

function populateBrandFilter() {
    const brandFilter = document.getElementById('brandFilter');
    const brands = [...new Set(carsData.map(car => car.brand))].sort();
    
    brands.forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandFilter.appendChild(option);
    });
}

function applyFilters() {
    const brandFilter = document.getElementById('brandFilter').value;
    const priceFrom = parseInt(document.getElementById('priceFrom').value) || 0;
    const priceTo = parseInt(document.getElementById('priceTo').value) || Infinity;
    const mileageTo = parseInt(document.getElementById('mileageTo').value) || Infinity;

    filteredCars = carsData.filter(car => {
        const brandMatch = !brandFilter || car.brand === brandFilter;
        const priceMatch = car.price >= priceFrom && car.price <= priceTo;
        const mileageMatch = car.mileage <= mileageTo;
        
        return brandMatch && priceMatch && mileageMatch;
    });

    loadCars();
}

function addToCart(carId) {
    const car = carsData.find(c => c.id === carId);
    if (car) {
        const existingItem = cart.find(item => item.id === carId);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({ ...car, quantity: 1 });
        }
        updateCartCount();
        showNotification('Автомобиль добавлен в заказ!');
    }
}

function removeFromCart(carId) {
    cart = cart.filter(item => item.id !== carId);
    updateCartCount();
    updateCartModal();
}

function updateCartCount() {
    const cartCount = document.getElementById('cartCount');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;
}

function showCart() {
    const cartModal = document.getElementById('cartModal');
    cartModal.style.display = 'block';
    updateCartModal();
}

function closeCart() {
    const cartModal = document.getElementById('cartModal');
    cartModal.style.display = 'none';
}

function updateCartModal() {
    const cartBody = document.getElementById('cartBody');
    const cartTotal = document.getElementById('cartTotal');
    
    if (cart.length === 0) {
        cartBody.innerHTML = '<p style="text-align: center; color: #64748b;">Ваш заказ пуст</p>';
        cartTotal.textContent = '0';
        return;
    }

    let total = 0;
    cartBody.innerHTML = '';

    cart.forEach(item => {
        total += item.price * item.quantity;
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div class="cart-item-info">
                <h4>${item.year} ${item.brand} ${item.model}</h4>
                <p>Пробег: ${item.mileage.toLocaleString()} км</p>
                <p>Количество: ${item.quantity}</p>
                <p style="color: #10b981; font-size: 0.8rem;"><i class="fas fa-check-circle"></i> Включает растаможку и доставку</p>
            </div>
            <div class="cart-item-price">
                ${(item.price * item.quantity).toLocaleString()} ₽
            </div>
            <button class="remove-item" onclick="removeFromCart(${item.id})">
                <i class="fas fa-trash"></i>
            </button>
        `;
        cartBody.appendChild(cartItem);
    });

    cartTotal.textContent = total.toLocaleString();
}

function showCarDetails(carId) {
    const car = carsData.find(c => c.id === carId);
    if (!car) return;

    const carModal = document.getElementById('carModal');
    const carModalTitle = document.getElementById('carModalTitle');
    const carModalBody = document.getElementById('carModalBody');

    carModalTitle.textContent = `${car.year} ${car.brand} ${car.model}`;
    
    carModalBody.innerHTML = `
        <div style="margin-bottom: 2rem;">
            <div style="margin-bottom: 2rem;">
                <h4>Основные характеристики</h4>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Марка:</strong> ${car.brand}</li>
                    <li><strong>Модель:</strong> ${car.model}</li>
                    <li><strong>Год:</strong> ${car.year}</li>
                    <li><strong>Двигатель:</strong> ${car.engine}L</li>
                    <li><strong>Пробег:</strong> ${car.mileage.toLocaleString()} км</li>
                    <li><strong>VIN:</strong> <a href="https://bid.cars/?s=${car.vin}" target="_blank" rel="noopener">${car.vin}</a></li>
                    <li><strong>Дата выпуска:</strong> ${car.date}</li>
                </ul>
            </div>
            <div>
                <h4>Фотографии автомобиля</h4>
                ${createCarGallery(car)}
            </div>
        </div>
        <div style="text-align: center; padding: 2rem; background: #1f2937; border-radius: 8px; border: 1px solid #374151;">
            <h3 style="color: #f3f4f6; margin-bottom: 1rem;">${car.price.toLocaleString()} ₽</h3>
            <p style="color: #10b981; margin-bottom: 1rem; font-weight: 500;">
                <i class="fas fa-check-circle"></i> Цена включает растаможку и доставку по России
            </p>
            <p style="color: #9ca3af; margin-bottom: 1.5rem;">Никаких дополнительных платежей!</p>
            <button class="btn-primary" onclick="addToCart(${car.id}); closeCarModal();" style="margin-right: 1rem;">
                <i class="fas fa-shopping-cart"></i> Сделать заказ
            </button>
            <button class="btn-secondary" onclick="closeCarModal();">
                Закрыть
            </button>
        </div>
    `;

    carModal.style.display = 'block';

    // Инициализация галереи после открытия модального окна
    initializeGallery(car);
}

// Р¤СѓРЅРєС†РёСЏ РґР»СЏ РЅР°РІРёРіР°С†РёРё РїРѕ РіР°Р»РµСЂРµРµ (СѓРїСЂРѕС‰РµРЅРЅР°СЏ РІРµСЂСЃРёСЏ)
function navigateGallery(carId, direction) {
    if (!carGalleries[carId]) return;
    const gallery = carGalleries[carId];
    const nextIndex = (gallery.index + (direction === 'next' ? 1 : -1) + gallery.photos.length) % gallery.photos.length;
    setGalleryIndex(carId, nextIndex);
}

function closeCarModal() {
    const carModal = document.getElementById('carModal');
    carModal.style.display = 'none';
}

function checkout() {
    if (cart.length === 0) {
        showNotification('Ваш заказ пуст!', 'error');
        return;
    }
    // Открываем модал ввода контактов
    openCheckoutModal();
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    let backgroundColor = '#10b981';
    if (type === 'error') backgroundColor = '#ef4444';
    if (type === 'info') backgroundColor = '#6b7280';
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${backgroundColor};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 3000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function setupEventListeners() {
    // Корзина
    document.getElementById('cartBtn').addEventListener('click', showCart);
    
    // Закрытие модальных окон по клику вне их
    window.addEventListener('click', function(event) {
        const cartModal = document.getElementById('cartModal');
        const carModal = document.getElementById('carModal');
        
        if (event.target === cartModal) {
            closeCart();
        }
        if (event.target === carModal) {
            closeCarModal();
        }
    });

    // Форма обратной связи
    document.getElementById('contactForm').addEventListener('submit', function(e) {
        e.preventDefault();
        showNotification('Заявка отправлена! Мы свяжемся с вами в ближайшее время.');
        this.reset();
    });

    // Форма контактов для заказа
    const checkoutForm = document.getElementById('checkoutContactForm');
    checkoutForm.addEventListener('submit', async function(e){
        e.preventDefault();
        const name = document.getElementById('contactName').value.trim();
        const phone = document.getElementById('contactPhone').value.trim();
        const email = document.getElementById('contactEmail').value.trim();

        if(!name || !phone || !email){
            showNotification('Заполните все поля контактов', 'error');
            return;
        }

        // Собираем заказ
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const items = cart.map(i => `${i.year} ${i.brand} ${i.model} — ${i.quantity} шт. — ${i.price.toLocaleString()} ₽`).join('\n');
        const message = `Новый заказ с сайта CarExport\n\nИмя: ${name}\nТелефон: ${phone}\nEmail: ${email}\n\nТовары:\n${items}\n\nИтого: ${total.toLocaleString()} ₽`;

        // Пытаемся отправить через FormSubmit (без сервера)
        try{
            document.getElementById('fs_name').value = name;
            document.getElementById('fs_phone').value = phone;
            document.getElementById('fs_email').value = email;
            document.getElementById('fs_message').value = message;
            document.getElementById('emailFallbackForm').submit();
            showNotification('Заказ отправлен! Мы свяжемся с вами.', 'success');
        }catch(err){
            console.error(err);
            showNotification('Не удалось отправить заявку. Попробуйте позже.', 'error');
            return;
        }

        // Чистим корзину
        cart = [];
        updateCartCount();
        closeCheckoutModal();
        closeCart();
    });

    // Плавная прокрутка для навигации
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// === Таможенный калькулятор ===
async function fetchEurRateRub() {
    try {
        // Курсы ЦБ РФ JSON: https://www.cbr-xml-daily.ru/daily_json.js
        const resp = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
        const data = await resp.json();
        const eur = data?.Valute?.EUR?.Value;
        if (typeof eur === 'number' && eur > 0) return eur;
    } catch (e) { /* ignore */ }
    // Фолбэк курс EUR→RUB, если сеть недоступна
    return 100; // приблизительное значение; пользователь увидит ориентировочную сумму
}

function customsRatePerCc(cc){
    if (cc <= 999) return 1.5;
    if (cc <= 1499) return 1.7;
    if (cc <= 1999) return 2.7;
    if (cc <= 2999) return 3.0;
    return 3.6;
}

function customsClearanceFee(costUsd){
    if (costUsd <= 14999) return 4269;
    if (costUsd <= 40000) return 11746;
    return 16524;
}

async function handleCalc(){
    const costUsd = parseFloat(document.getElementById('costUsd').value);
    const cc = parseInt(document.getElementById('engineCc').value, 10);
    const age = document.getElementById('age').value; // зарезервировано для будущей логики

    if (!isFinite(costUsd) || costUsd <= 0 || !isFinite(cc) || cc <= 0){
        document.getElementById('calcResult').textContent = 'Введите корректные значения стоимости и объема двигателя.';
        return;
    }

    const eurPerCc = customsRatePerCc(cc); // евро на см³
    const eurAmount = eurPerCc * cc;       // сумма в евро
    const eurRub = await fetchEurRateRub();// курс EUR→RUB
    const rubByCc = eurAmount * eurRub;    // рубли по объему
    const fee = customsClearanceFee(costUsd); // пошлина оформления
    const totalRub = Math.round(rubByCc + fee);

    document.getElementById('calcResult').textContent = `${totalRub.toLocaleString('ru-RU')} ₽`;
}

document.addEventListener('DOMContentLoaded', ()=>{
    const btn = document.getElementById('calcBtn');
    if (btn) btn.addEventListener('click', handleCalc);
    // Калькулятор в модалке
    window.openCustomsModal = function(){
        const m = document.getElementById('customsModal');
        if (m) m.style.display = 'block';
    }
    window.closeCustomsModal = function(){
        const m = document.getElementById('customsModal');
        if (m) m.style.display = 'none';
    }

    // Заявка на подбор
    window.openRequestModal = function(){
        const m = document.getElementById('requestModal');
        if (!m) return;
        m.style.display = 'block';
        // фокус для мобильных
        const firstField = document.getElementById('reqBrand');
        if (firstField) setTimeout(()=> firstField.focus(), 50);
    }
    window.closeRequestModal = function(){
        const m = document.getElementById('requestModal');
        if (m) m.style.display = 'none';
    }

    const requestBtn = document.getElementById('requestSubmit');
    if (requestBtn) requestBtn.addEventListener('click', async ()=>{
        const name = document.getElementById('reqName').value.trim();
        const phone = document.getElementById('reqPhone').value.trim();
        const email = document.getElementById('reqEmail').value.trim();
        const brand = document.getElementById('reqBrand').value.trim();
        const model = document.getElementById('reqModel').value.trim();
        const yf = document.getElementById('reqYearFrom').value.trim();
        const yt = document.getElementById('reqYearTo').value.trim();
        const pt = document.getElementById('reqPriceTo').value.trim();
        const note = document.getElementById('reqNote').value.trim();

        if(!name || !phone || !brand || !model){
            const s = document.getElementById('requestStatus');
            s.style.display='block'; s.textContent='Пожалуйста, заполните обязательные поля: имя, телефон, марка, модель.'; return;
        }

        // отправка через formsubmit.co (без сервера)
        const payload = new URLSearchParams();
        payload.append('name', name);
        payload.append('phone', phone);
        if (email) payload.append('email', email);
        payload.append('message', `Марка: ${brand}\nМодель: ${model}\nГод: ${yf || '-'} - ${yt || '-'}\nБюджет до: ${pt || '-'} ₽\nПримечание: ${note || '-'}`);
        payload.append('_captcha','false');
        payload.append('_subject','Заявка на подбор (сайт CarExport)');

        const resp = await fetch('https://formsubmit.co/carexportgeo@bk.ru', { method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body: payload});
        const s = document.getElementById('requestStatus');
        s.style.display='block';
        if (resp.ok){ s.textContent='Заявка отправлена! Мы свяжемся с вами.'; }
        else { s.textContent='Не удалось отправить заявку. Попробуйте позже.'; }
    });
});

// Добавляем CSS анимации и стили для скрытия названий файлов
const style = document.createElement('style');
style.textContent = `
    .gallery-dot{width:8px;height:8px;border-radius:50%;background:#9ca3af;opacity:.6}
    .gallery-dot.active{background:#f3f4f6;opacity:1}
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    /* Скрываем названия файлов в Google Drive iframe */
    .car-image iframe,
    .gallery-container iframe {
        position: relative;
    }
    
    /* Стили для скрытия списка файлов */
    .car-image iframe[src*="embeddedfolderview"] {
        background: #374151;
    }
    
    /* Скрываем заголовки и списки в Google Drive */
    .car-image iframe::before,
    .gallery-container iframe::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 40px;
        background: #374151;
        z-index: 10;
        pointer-events: none;
    }
`;
document.head.appendChild(style);

// ---------- Галерея: инициализация, рендер и свайпы ----------
function buildPhotoCandidates(car){
    // Кандидаты имен файлов внутри images/car{id}
    const exts = ['jpg','JPG'];
    const names = new Set();
    // main
    exts.forEach(ext => names.add(`main.${ext}`));
    // Формат "1 (1).jpg" .. "1 (30).jpg"
    for (let i = 1; i <= 30; i++) {
        exts.forEach(ext => names.add(`1 (${i}).${ext}`));
    }
    // Простые номера 1..30
    for (let i = 1; i <= 30; i++) {
        exts.forEach(ext => names.add(`${i}.${ext}`));
    }
    // photo1..photo30
    for (let i = 1; i <= 30; i++) {
        exts.forEach(ext => names.add(`photo${i}.${ext}`));
    }
    // original1..original30 и "original (1..30)"
    for (let i = 1; i <= 30; i++) {
        exts.forEach(ext => names.add(`original${i}.${ext}`));
    }
    for (let i = 1; i <= 30; i++) {
        exts.forEach(ext => names.add(`original (${i}).${ext}`));
    }
    // Доп частые имена
    ['front','rear','left','right','interior','dashboard','engine'].forEach(base => {
        exts.forEach(ext => names.add(`${base}.${ext}`));
    });
    return Array.from(names).map(n => `images/car${car.id}/${n}`);
}

async function loadManifestPhotos(car){
    try{
        const resp = await fetch(`images/car${car.id}/car-info.json`);
        if(!resp.ok) return null;
        const data = await resp.json();
        if(Array.isArray(data.photos)){
            return data.photos.map(p=> `images/car${car.id}/${p}`);
        }
        return null;
    }catch(e){
        return null;
    }
}

function photoKeyFromSrc(src){
    try{
        const file = src.split('/').pop();
        const base = file.replace(/\.[^.]+$/, '');
        const m = base.match(/original\s*\((\d+)\)/i) ||
                  base.match(/original(\d+)/i) ||
                  base.match(/^1\s*\((\d+)\)$/) ||
                  base.match(/^(\d+)$/) ||
                  base.match(/photo(\d+)/i);
        if (m) return `num-${m[1]}`;
        return base.toLowerCase();
    }catch(_){ return src; }
}

async function initializeGallery(car){
    const container = document.getElementById(`gallery-${car.id}`);
    if(!container) return;
    const track = container.querySelector('.gallery-track');
    const dotsWrap = document.getElementById(`gallery-dots-${car.id}`);

    // 1) пробуем получить список из манифеста, 2) иначе используем паттерны
    let candidates = await loadManifestPhotos(car);
    if(!candidates || candidates.length===0){
        candidates = buildPhotoCandidates(car);
    }
    // Предзагрузка и фильтрация валидных фото
    const valid = await Promise.all(candidates.map(src => new Promise(res => {
        const im = new Image();
        im.onload = () => res(src);
        im.onerror = () => res(null);
        im.src = src;
    })));
    let photos = valid.filter(Boolean);

    // Удаляем дубликаты по нормализованному ключу имени
    const seen = new Set();
    const unique = [];
    for (const s of photos){
        const key = photoKeyFromSrc(s);
        if (seen.has(key)) continue;
        seen.add(key);
        unique.push(s);
    }
    photos = unique;

    track.innerHTML = '';
    dotsWrap.innerHTML = '';

    photos.forEach((src,idx)=>{
        const img = document.createElement('img');
        img.src = src;
        img.alt = `${car.year} ${car.brand} ${car.model}`;
        img.style.cssText = 'width:100%;height:100%;object-fit:contain;flex:0 0 100%;';
        track.appendChild(img);

        const dot = document.createElement('div');
        dot.className = 'gallery-dot'+(idx===0?' active':'');
        dot.addEventListener('click',()=> setGalleryIndex(car.id, idx));
        dotsWrap.appendChild(dot);
    });

    // Если ни одной фотки — покажем заглушку
    if (photos.length === 0) {
        const fallback = document.createElement('div');
        fallback.style.cssText = 'width:100%;height:100%;display:flex;align-items:center;justify-content:center;color:#f3f4f6;flex:0 0 100%;font-size:1rem;';
        fallback.textContent = 'Фотографии скоро будут';
        track.appendChild(fallback);
    }

    carGalleries[car.id] = { index: 0, photos, container, track, dotsWrap };
    setGalleryIndex(car.id, 0);
}

function setGalleryIndex(carId, index){
    const g = carGalleries[carId];
    if(!g) return;
    const length = g.photos ? g.photos.length : g.track.children.length;
    if (length === 0) return;
    g.index = ((index % length) + length) % length;
    const offset = -g.index * 100;
    g.track.style.transform = `translateX(${offset}%)`;
    Array.from(g.dotsWrap.children).forEach((d,i)=>{
        d.classList.toggle('active', i===g.index);
    });
}

function prevPhoto(carId){ navigateGallery(carId, 'prev'); }
function nextPhoto(carId){ navigateGallery(carId, 'next'); }

let touchStartX = null; let touchActiveGalleryId = null;
function onTouchStart(e){
    const gallery = e.target.closest?.('.gallery-container');
    if(!gallery) return;
    touchActiveGalleryId = parseInt(gallery.getAttribute('data-car-id'));
    touchStartX = e.touches[0].clientX;
}
function onTouchMove(e){ /* пассивный слушатель, логика не нужна */ }
function onTouchEnd(e){
    if(touchStartX===null || touchActiveGalleryId===null) return;
    const endX = (e.changedTouches && e.changedTouches[0]?.clientX) || 0;
    const dx = endX - touchStartX;
    if(Math.abs(dx) > 40){
        if(dx < 0) nextPhoto(touchActiveGalleryId); else prevPhoto(touchActiveGalleryId);
    }
    touchStartX = null; touchActiveGalleryId = null;
}
