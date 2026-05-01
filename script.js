'use strict';

const state = {
    cart: [],
    filteredCars: [],
    carGalleries: {},
    touch: {
        startX: null,
        galleryId: null
    },
    chinaUnder160: null,
    koreaUnder160: null,
    favorites: JSON.parse(localStorage.getItem('expomirFavorites') || '[]'),
    viewMode: localStorage.getItem('expomirViewMode') || 'grid',
};

// numberFormatter объявлен в translations.js, используем глобальную переменную
// Не объявляем здесь, чтобы избежать конфликта с translations.js

// Глобальная переменная для курса USD/RUB от ЦБ РФ
let usdToRubRate = null;
// Кеш курса EUR/RUB (заполняется при первом fetch, избегая дублирующих запросов)
let cachedEurRateRub = null;

// Загрузка курсов USD/RUB и EUR/RUB от ЦБ РФ при загрузке страницы
async function loadUsdToRubRate() {
    if (usdToRubRate) return usdToRubRate; // Уже загружен
    
    try {
        const response = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
        if (response.ok) {
            const data = await response.json();
            const usd = data.Valute?.USD;
            const eur = data.Valute?.EUR;
            if (usd?.Value) { usdToRubRate = usd.Value; }
            if (eur?.Value) { cachedEurRateRub = eur.Value; }
            if (usdToRubRate) return usdToRubRate;
        }
    } catch (error) {
        console.warn('Не удалось загрузить курс ЦБ, используем fallback');
    }
    
    // Fallback курс если API недоступен
    usdToRubRate = 88.0;
    return usdToRubRate;
}

// Конвертация рублей в доллары
function convertRubToUsd(rubValue) {
    if (!usdToRubRate) {
        // Если курс еще не загружен, возвращаем значение как есть (будет обновлено после загрузки курса)
        return rubValue;
    }
    return Math.round(rubValue / usdToRubRate);
}

// Определение, является ли значение ценой в рублях (обычно > 10000)
function isPriceInRubles(value) {
    return value && value > 10000;
}

// Форматирование валюты с автоматической конвертацией рублей в доллары и поддержкой выбранной валюты
const formatCurrency = (value) => {
    if (!value || value <= 0) {
        // Используем функцию из translations.js если доступна
        if (typeof formatPrice === 'function') {
            try {
                return formatPrice(0);
            } catch (e) {
                console.warn('formatPrice error:', e);
            }
        }
        return '$0';
    }
    
    // Если значение похоже на рубли (> 10000), конвертируем в доллары
    let usdValue = value;
    if (isPriceInRubles(value) && usdToRubRate) {
        usdValue = convertRubToUsd(value);
    }
    
    // Используем функцию из translations.js для форматирования с выбранной валютой
    if (typeof formatPrice === 'function') {
        try {
            return formatPrice(usdValue);
        } catch (e) {
            console.warn('formatPrice error:', e);
        }
    }
    
    // Fallback если translations.js не загружен
    return `$${numberFormatter.format(Math.round(usdValue))}`;
};

// Функция для обновления всех отображаемых цен после загрузки курса
function updateAllDisplayedPrices() {
    if (!usdToRubRate) return; // Курс еще не загружен
    
    // Обновляем цены в карточках автомобилей
    document.querySelectorAll('.car-price').forEach(el => {
        const text = el.textContent.trim();
        // Извлекаем число из текста (может быть в рублях)
        const match = text.match(/[\d\s,]+/);
        if (match) {
            const numStr = match[0].replace(/[\s,]/g, '');
            const num = parseInt(numStr);
            if (num && isPriceInRubles(num)) {
                const usdValue = convertRubToUsd(num);
                el.textContent = formatCurrency(usdValue);
            }
        }
    });
    
    // Обновляем цены в корзине
    updateCartModal();
    
    // Обновляем метрики (если есть)
    if (typeof updateUsaMetrics === 'function') {
        updateUsaMetrics();
    }
    if (typeof updateChinaMetrics === 'function') {
        updateChinaMetrics();
    }
    if (typeof updateKoreaMetrics === 'function') {
        updateKoreaMetrics();
    }
}

// Функция для создания галереи с реальными фотографиями
function createCarGallery(car) {
    return `
        <div class="car-gallery">
            <div id="gallery-${car.id}" class="gallery-container" data-car-id="${car.id}">
                <div class="gallery-track"></div>
                <button class="gallery-nav-btn gallery-prev" data-gallery-nav="prev" data-car-id="${car.id}" aria-label="Предыдущая">&#8249;</button>
                <button class="gallery-nav-btn gallery-next" data-gallery-nav="next" data-car-id="${car.id}" aria-label="Следующая">&#8250;</button>
                <div id="gallery-dots-${car.id}" class="gallery-dots"></div>
                ${car.sold ? `
                <div class="sold-overlay">
                    <div class="sold-overlay__label">ПРОДАНО</div>
                </div>` : ''}
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
        price: 2590000, // Включает растаможку и доставку
        mileage: 62400,
        date: "01.04.2021",
        photos: "https://drive.google.com/drive/folders/1FR5s24AvCCFwheEODFLvBXko11UaIBwx?usp=sharing",
        folderId: "1FR5s24AvCCFwheEODFLvBXko11UaIBwx",
        sold: true
    },
    {
        id: 2,
        brand: "KIA",
        model: "K5 AWD",
        year: 2021,
        engine: "1,6",
        vin: "5XXG64J21MG051872",
        price: 1840000, // Включает растаможку и доставку
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
        price: 2000000, // Включает растаможку и доставку
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
        price: 1960000, // Включает растаможку и доставку
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
        price: 1860000, // Включает растаможку и доставку
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
        price: 1520000, // Включает растаможку и доставку
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
        price: 1450000, // Включает растаможку и доставку
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
        price: 1350000, // Включает растаможку и доставку
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
        price: 2170000, // Включает растаможку и доставку
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
        price: 2070000, // Включает растаможку и доставку
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
        price: 2090000, // Включает растаможку и доставку
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
        price: 1850000, // Включает растаможку и доставку
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
        price: 1930000, // Включает растаможку и доставку
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
        price: 3220000, // Включает растаможку и доставку
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
        price: 2020000, // Включает растаможку и доставку
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
        price: 1400000, // Включает растаможку и доставку
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
        price: 1790000, // Включает растаможку и доставку
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
        price: 1540000, // Включает растаможку и доставку
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
        price: 1940000, // Включает растаможку и доставку
        mileage: 92000,
        date: "01.10.2022",
        photos: "https://drive.google.com/drive/folders/1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H?usp=sharing",
        folderId: "1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H",
        sold: true
    },
    {
        id: 22,
        brand: "Toyota",
        model: "Venza LE",
        year: 2021,
        engine: "2,5",
        vin: "JTEAAAAH4MJ071578",
        price: 2580000, // Включает растаможку и доставку
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
        price: 1640000, // Включает растаможку и доставку
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
        price: 1810000, // Включает растаможку и доставку
        mileage: 93600,
        date: "01.02.2021",
        photos: "https://drive.google.com/drive/folders/1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG?usp=sharing",
        folderId: "1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG",
        sold: true
    },
    {
        id: 25,
        brand: "Mitsubishi",
        model: "Eclipse LE Limited 4WD",
        year: 2021,
        engine: "2,4",
        vin: "JA4ATVAA9NZ001578",
        price: 1730000, // Включает растаможку и доставку
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
        price: 1720000, // Включает растаможку и доставку
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
        price: 3140000, // Включает растаможку и доставку
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
        price: 2420000, // Включает растаможку и доставку
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
        price: 3180000, // Включает растаможку и доставку
        mileage: 41500,
        date: "01.10.2021",
        photos: "https://drive.google.com/drive/folders/1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG?usp=sharing",
        folderId: "1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG",
        sold: true
    },
    {
        id: 30,
        brand: "BMW",
        model: "X3 Sdrive30I",
        year: 2022,
        engine: "2,0",
        vin: "5UX43DP04N9L08991",
        price: 3560000, // Включает растаможку и доставку
        mileage: 11500,
        date: "01.01.2022",
        photos: "https://drive.google.com/drive/folders/1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO?usp=sharing",
        folderId: "1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO",
        sold: true
    },
    {
        id: 31,
        brand: "Audi",
        model: "Q3 Premium 40",
        year: 2021,
        engine: "2,0",
        vin: "A1AUCF31N1001715",
        price: 3010000, // Включает растаможку и доставку
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
        price: 3100000, // Включает растаможку и доставку
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
        price: 3180000, // Включает растаможку и доставку
        mileage: 45000,
        date: "01.03.2022",
        photos: "https://drive.google.com/drive/folders/1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl?usp=sharing",
        folderId: "1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl"
    },
    {
        id: 34,
        brand: "Ford",
        model: "Escape SEL",
        year: 2022,
        engine: "2,0",
        vin: "1FMCU0H6XNUA48711",
        price: 1526849,
        mileage: 90400,
        date: "янв.22",
        photos: "images/car34",
        folderId: "local",
        sold: true
    }
];

// Инициализация глобального состояния
state.filteredCars = [...carsData];

// РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РїСЂРё Р·Р°РіСЂСѓР·РєРµ СЃС‚СЂР°РЅРёС†С‹
// Загружаем курс USD/RUB при загрузке страницы
document.addEventListener('DOMContentLoaded', async function() {
    // Загружаем курс USD/RUB в фоне
    await loadUsdToRubRate();
    
    // Инициализируем приложение
    initializeApp();
    
    // Обновляем все отображаемые цены после загрузки курса
    updateAllDisplayedPrices();
});

function initializeApp() {
    // loadCars(); // Отключено - каталог перенесен на страницу Грузия-сток
    populateBrandFilter(); // нужен для фильтров даже без полного каталога
    updateCartCount();
    updateFavoritesCount();
    setupEventListeners();
    setupScrollReveal();
    
    // Загружаем секции только если соответствующие элементы существуют на странице
    if (document.getElementById('usaUnder160Grid') || document.getElementById('usaMetrics')) {
        loadUsaOrdersSection();
    }
    
    if (document.getElementById('chinaUnder160Grid')) {
        loadChinaOrdersSection();
    }
    
    if (document.getElementById('koreaUnder160Grid') || document.getElementById('koreaOrdersGrid')) {
        loadKoreaOrdersSection();
    }
    
    // Обработчики свайпа для всех галерей (делегирование)
    document.addEventListener('touchstart', onTouchStart, { passive: true });
    document.addEventListener('touchmove', onTouchMove, { passive: true });
    document.addEventListener('touchend', onTouchEnd, { passive: true });
}

function buildSvgPlaceholder(title) {
    const safeTitle = (title || 'EXPO MIR').replace(/[<>&]/g, char => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[char]));
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#111827"/><stop offset="100%" stop-color="#1f2937"/></linearGradient></defs><rect width="1600" height="900" fill="url(#grad)"/><text x="50%" y="50%" fill="#374151" font-family="Inter,Arial,sans-serif" font-size="96" text-anchor="middle" dominant-baseline="middle">${safeTitle}</text></svg>`;
    try {
        if (typeof window !== 'undefined' && window.btoa) {
            return `data:image/svg+xml;base64,${window.btoa(unescape(encodeURIComponent(svg)))}`;
        }
    } catch (err) {
        // ignore and fallback to UTF-8 variant
    }
    return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

function attachImageFallback(imageEl, car) {
    if (!imageEl) return;
    const fallbackTitle = (car && (car.name || `${car.brand || ''} ${car.model || ''}`.trim())) || 'EXPO MIR';
    const fallbackUrl = buildSvgPlaceholder(fallbackTitle);
    imageEl.addEventListener('error', () => {
        if (imageEl.dataset.fallbackApplied) return;
        imageEl.dataset.fallbackApplied = '1';
        imageEl.src = fallbackUrl;
        imageEl.alt = `${fallbackTitle} (изображение временно недоступно)`;
    }, { once: true });
}

const usaUnder160Cars = [
    {
        name: 'Mitsubishi Outlander Sport',
        brand: 'Mitsubishi',
        model: 'Outlander Sport',
        engine: '2.0 л',
        power: '148 л.с.',
        drive: 'Полный / передний',
        price: 2000000,
        image: 'images/PHOTO USA/Mitsubishi Outlander Sport.jpg'
    },
    {
        name: 'Mitsubishi Eclipse Cross',
        brand: 'Mitsubishi',
        model: 'Eclipse Cross',
        engine: '1.5 л',
        power: '152 л.с.',
        drive: 'Полный',
        price: 1900000,
        image: 'images/PHOTO USA/Mitsubishi Eclipse Cross.webp'
    },
    {
        name: 'Mitsubishi Mirage',
        brand: 'Mitsubishi',
        model: 'Mirage',
        engine: '1.2 л',
        power: '78 л.с.',
        drive: 'Передний',
        price: 1300000,
        image: 'images/PHOTO USA/Mitsubishi Mirage.webp'
    },
    {
        name: 'Nissan Rogue Sport',
        brand: 'Nissan',
        model: 'Rogue Sport',
        engine: '2.0 л',
        power: '141 л.с.',
        drive: 'Полный / передний',
        price: 1800000,
        image: 'images/PHOTO USA/Nissan Rogue Sport.jpg'
    },
    {
        name: 'Nissan Sentra',
        brand: 'Nissan',
        model: 'Sentra',
        engine: '2.0 л',
        power: '149 л.с.',
        drive: 'Передний',
        price: 1600000,
        image: 'images/PHOTO USA/Nissan Sentra.webp'
    },
    {
        name: 'Nissan Versa',
        brand: 'Nissan',
        model: 'Versa',
        engine: '1.6 л',
        power: '122 л.с.',
        drive: 'Передний',
        price: 1500000,
        image: 'images/PHOTO USA/Nissan Versa.webp'
    },
    {
        name: 'Nissan Kicks',
        brand: 'Nissan',
        model: 'Kicks',
        engine: '1.6 л',
        power: '122 л.с.',
        drive: 'Передний',
        price: 1600000,
        image: 'images/PHOTO USA/Nissan Kicks.jpg'
    },
    {
        name: 'Kia Seltos',
        brand: 'Kia',
        model: 'Seltos',
        engine: '2.0 л',
        power: '147 л.с.',
        drive: 'Полный / передний',
        price: 1900000,
        image: 'images/PHOTO USA/Kia Seltos.webp'
    },
    {
        name: 'Kia Forte',
        brand: 'Kia',
        model: 'Forte',
        engine: '2.0 л',
        power: '147 л.с.',
        drive: 'Передний',
        price: 1600000,
        image: 'images/PHOTO USA/Kia Forte.jpg'
    },
    {
        name: 'Kia Soul',
        brand: 'Kia',
        model: 'Soul',
        engine: '2.0 л',
        power: '147 л.с.',
        drive: 'Передний',
        price: 1900000,
        image: 'images/PHOTO USA/Kia Soul.webp'
    },
    {
        name: 'Kia Rio',
        brand: 'Kia',
        model: 'Rio',
        engine: '1.6 л',
        power: '120 л.с.',
        drive: 'Передний',
        price: 1700000,
        image: 'images/PHOTO USA/Kia Rio.webp'
    },
    {
        name: 'Kia K4 (2025)',
        brand: 'Kia',
        model: 'K4',
        engine: '2.0 л',
        power: '147 л.с.',
        drive: 'Передний',
        price: 2300000,
        image: 'images/PHOTO USA/Kia K4.webp'
    },
    {
        name: 'Hyundai Elantra',
        brand: 'Hyundai',
        model: 'Elantra',
        engine: '2.0 л',
        power: '147 л.с.',
        drive: 'Передний',
        price: 1800000,
        image: 'images/PHOTO USA/Hyundai Elantra.webp'
    },
    {
        name: 'Hyundai Kona',
        brand: 'Hyundai',
        model: 'Kona',
        engine: '2.0 л',
        power: '147 л.с.',
        drive: 'Полный / передний',
        price: 1700000,
        image: 'images/PHOTO USA/Hyundai Kona.webp'
    },
    {
        name: 'Hyundai Venue',
        brand: 'Hyundai',
        model: 'Venue',
        engine: '1.6 л',
        power: '121 л.с.',
        drive: 'Передний',
        price: 1500000,
        image: 'images/PHOTO USA/Hyundai Venue.jpg'
    },
    {
        name: 'Hyundai Accent',
        brand: 'Hyundai',
        model: 'Accent',
        engine: '1.6 л',
        power: '120 л.с.',
        drive: 'Передний',
        price: 1400000,
        image: 'images/PHOTO USA/Hyundai Accent.jpg'
    },
    {
        name: 'Toyota C-HR',
        brand: 'Toyota',
        model: 'C-HR',
        engine: '2.0 л',
        power: '145 л.с.',
        drive: 'Передний',
        price: 2000000,
        image: 'images/PHOTO USA/Toyota C-HR.jpg'
    },
    {
        name: 'Honda HR-V',
        brand: 'Honda',
        model: 'HR-V',
        engine: '1.8 л',
        power: '141 л.с.',
        drive: 'Полный / передний',
        price: 1700000,
        image: 'images/PHOTO USA/Honda HR-V.jpg'
    },
    {
        name: 'Chevrolet Trailblazer',
        brand: 'Chevrolet',
        model: 'Trailblazer',
        engine: '1.3 л',
        power: '155 л.с.',
        drive: 'Полный',
        price: 1600000,
        image: 'images/PHOTO USA/Chevrolet Trailblazer.webp'
    },
    {
        name: 'Chevrolet Trax',
        brand: 'Chevrolet',
        model: 'Trax',
        engine: '1.5 л',
        power: '155 л.с.',
        drive: 'Передний',
        price: 1300000,
        image: 'images/PHOTO USA/Chevrolet Trax.jpeg'
    },
    {
        name: 'Chevrolet Spark',
        brand: 'Chevrolet',
        model: 'Spark',
        engine: '1.4 л',
        power: '98 л.с.',
        drive: 'Передний',
        price: 1300000,
        image: 'images/PHOTO USA/Chevrolet Spark.jpg'
    },
    {
        name: 'Buick Encore',
        brand: 'Buick',
        model: 'Encore',
        engine: '1.4 л',
        power: '155 л.с.',
        drive: 'Полный / передний',
        price: 1400000,
        image: 'images/PHOTO USA/Buick Encore.webp'
    },
    {
        name: 'Ford EcoSport',
        brand: 'Ford',
        model: 'EcoSport',
        engine: '1.0 л',
        power: '123 л.с.',
        drive: 'Передний',
        price: 1200000,
        image: 'images/PHOTO USA/Ford EcoSport.webp'
    },
    {
        name: 'Volkswagen Jetta',
        brand: 'Volkswagen',
        model: 'Jetta',
        engine: '1.4 л',
        power: '147 л.с.',
        drive: 'Передний',
        price: 1800000,
        image: 'images/PHOTO USA/Volkswagen Jetta.webp'
    },
    {
        name: 'Mini Cooper',
        brand: 'MINI',
        model: 'Cooper',
        engine: '1.5 л',
        power: '134 л.с.',
        drive: 'Передний',
        price: 1800000,
        image: 'images/PHOTO USA/Mini Cooper.webp'
    },
    {
        name: 'Mini Countryman',
        brand: 'MINI',
        model: 'Countryman',
        engine: '1.5 л',
        power: '134 л.с.',
        drive: 'Полный / передний',
        price: 2000000,
        image: 'images/PHOTO USA/Mini Countryman.webp'
    },
    {
        name: 'Subaru Impreza',
        brand: 'Subaru',
        model: 'Impreza',
        engine: '2.0 л',
        power: '152 л.с.',
        drive: 'Полный',
        price: 1500000,
        image: 'images/PHOTO USA/Subaru Impreza.webp'
    },
    {
        name: 'Subaru Crosstrek',
        brand: 'Subaru',
        model: 'Crosstrek',
        engine: '2.0 л',
        power: '152 л.с.',
        drive: 'Полный',
        price: 1600000,
        image: 'images/PHOTO USA/Subaru Crosstrek.webp'
    },
    {
        name: 'Mazda CX-3',
        brand: 'Mazda',
        model: 'CX-3',
        engine: '2.0 л',
        power: '148 л.с.',
        drive: 'Полный / передний',
        price: 1800000,
        image: 'images/PHOTO USA/Mazda CX-3.webp'
    },
    {
        name: 'Mazda 3',
        brand: 'Mazda',
        model: '3',
        engine: '2.5 л',
        power: '155 л.с.',
        drive: 'Передний',
        price: 1800000,
        image: 'images/PHOTO USA/Mazda 3.webp'
    }
];

const chinaCars = [
    {
        "name": "Nissan Sylphy",
        "brand": "Nissan",
        "model": "Sylphy",
        "image": "images/china/catalog/nissan-sylphy.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 135",
            "Макс. скорость, км/ч: 185",
            "Привод: Передний",
            "Разгон 0-100 км, сек: -",
            "Расход топлива: 5.57-5.87"
        ],
        "engineType": "Бензин",
        "power": "135 л.с.",
        "maxSpeed": "185 км/ч",
        "drive": "Передний",
        "acceleration": "-",
        "consumption": "5.57-5.87 л/100 км"
    },
    {
        "name": "Nissan X-Trail",
        "brand": "Nissan",
        "model": "X-Trail",
        "image": "images/china/catalog/nissan-x-trail.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 151",
            "Макс. скорость, км/ч: 183",
            "Привод: Передний",
            "Объем двигателя: 1997",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "151 л.с.",
        "maxSpeed": "183 км/ч",
        "drive": "Передний",
        "engineVolume": "1997",
        "transmission": "Вариатор"
    },
    {
        "name": "Nissan Teana",
        "brand": "Nissan",
        "model": "Teana",
        "image": "images/china/catalog/nissan-teana.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 156",
            "Макс. скорость, км/ч: 197",
            "Привод: Передний",
            "Объем двигателя: 1997",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "156 л.с.",
        "maxSpeed": "197 км/ч",
        "drive": "Передний",
        "engineVolume": "1997",
        "transmission": "Вариатор"
    },
    {
        "name": "Volkswagen Lavida",
        "brand": "Volkswagen",
        "model": "Lavida",
        "image": "images/china/catalog/volkswagen-lavida.webp",
        "priceFrom": 2600000,
        "specs": [
            "Тип двигателя: ДВС",
            "Мощность, л.с.: 110/116/160",
            "Макс. скорость, км/ч: 188/198/200",
            "Привод: Задний",
            "Объем двигателя: 1197/1498",
            "Трансмиссия: Робот/Автомат"
        ],
        "engineType": "ДВС",
        "power": "110/116/160 л.с.",
        "maxSpeed": "188/198/200 км/ч",
        "drive": "Задний",
        "engineVolume": "1197/1498",
        "transmission": "Робот/Автомат"
    },
    {
        "name": "Honda Fit",
        "brand": "Honda",
        "model": "Fit",
        "image": "images/china/catalog/honda-fit.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: ДВС",
            "Мощность, л.с.: 124",
            "Макс. скорость, км/ч: 188",
            "Привод: Передний",
            "Объем двигателя: 1498",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "ДВС",
        "power": "124 л.с.",
        "maxSpeed": "188 км/ч",
        "drive": "Передний",
        "engineVolume": "1498",
        "transmission": "Вариатор"
    },
    {
        "name": "Nissan Kick",
        "brand": "Nissan",
        "model": "Kick",
        "image": "images/china/catalog/nissan-kick.webp",
        "priceFrom": 1900000,
        "specs": [
            "Тип двигателя: ДВС",
            "Мощность, л.с.: 122",
            "Макс. скорость, км/ч: 170",
            "Привод: Передний",
            "Объем двигателя: 1498",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "ДВС",
        "power": "122 л.с.",
        "maxSpeed": "170 км/ч",
        "drive": "Передний",
        "engineVolume": "1498",
        "transmission": "Вариатор"
    },
    {
        "name": "Nissan Tiida",
        "brand": "Nissan",
        "model": "Tiida",
        "image": "images/china/catalog/nissan-tiida.webp",
        "priceFrom": 2000000,
        "specs": [
            "Тип двигателя: ДВС",
            "Мощность, л.с.: 122",
            "Макс. скорость, км/ч: 179",
            "Привод: Передний",
            "Объем двигателя: 1598",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "ДВС",
        "power": "122 л.с.",
        "maxSpeed": "179 км/ч",
        "drive": "Передний",
        "engineVolume": "1598",
        "transmission": "Вариатор"
    },
    {
        "name": "Mazda 3",
        "brand": "Mazda",
        "model": "3",
        "image": "images/china/catalog/mazda-3.webp",
        "priceFrom": 2286000,
        "specs": [
            "Тип двигателя: ДВС",
            "Мощность, л.с.: 117",
            "Макс. скорость, км/ч: 196",
            "Привод: Передний",
            "Объем двигателя: 1496",
            "Трансмиссия: Механика"
        ],
        "engineType": "ДВС",
        "power": "117 л.с.",
        "maxSpeed": "196 км/ч",
        "drive": "Передний",
        "engineVolume": "1496",
        "transmission": "Механика"
    },
    {
        "name": "Volkswagen Polo",
        "brand": "Volkswagen",
        "model": "Polo",
        "image": "images/china/catalog/volkswagen-polo.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 110",
            "Макс. скорость, км/ч: 182",
            "Привод: Передний",
            "Разгон 0-100 км, сек: -",
            "Расход топлива: 5.60-5.90"
        ],
        "engineType": "Бензин",
        "power": "110 л.с.",
        "maxSpeed": "182 км/ч",
        "drive": "Передний",
        "acceleration": "-",
        "consumption": "5.60-5.90 л/100 км"
    },
    {
        "name": "Volkswagen Bora",
        "brand": "Volkswagen",
        "model": "Bora",
        "image": "images/china/catalog/volkswagen-bora.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 116/150",
            "Макс. скорость, км/ч: 200",
            "Привод: Передний",
            "Объем двигателя: 1197/1395",
            "Трансмиссия: Механика"
        ],
        "engineType": "Бензин",
        "power": "116/150 л.с.",
        "maxSpeed": "200 км/ч",
        "drive": "Передний",
        "engineVolume": "1197/1395",
        "transmission": "Механика"
    },
    {
        "name": "Volkswagen T-Cross",
        "brand": "Volkswagen",
        "model": "T-Cross",
        "image": "images/china/catalog/volkswagen-t-cross.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 110",
            "Макс. скорость, км/ч: 185",
            "Привод: Передний",
            "Объем двигателя: 1498",
            "Трансмиссия: Механика"
        ],
        "engineType": "Бензин",
        "power": "110 л.с.",
        "maxSpeed": "185 км/ч",
        "drive": "Передний",
        "engineVolume": "1498",
        "transmission": "Механика"
    },
    {
        "name": "Honda Life",
        "brand": "Honda",
        "model": "Life",
        "image": "images/china/catalog/honda-life.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: ДВС",
            "Мощность, л.с.: 124",
            "Макс. скорость, км/ч: 188",
            "Привод: Передний",
            "Объем двигателя: 1496",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "ДВС",
        "power": "124 л.с.",
        "maxSpeed": "188 км/ч",
        "drive": "Передний",
        "engineVolume": "1496",
        "transmission": "Вариатор"
    },
    {
        "name": "Jetta VA7",
        "brand": "Jetta",
        "model": "VA7",
        "image": "images/china/catalog/jetta-va7.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 200",
            "Привод: Передний",
            "Запас хода, км: 1395",
            "Трансмиссия: Механика/Автомат"
        ],
        "engineType": "Бензин",
        "power": "150 л.с.",
        "maxSpeed": "200 км/ч",
        "drive": "Передний",
        "range": "1395 км",
        "transmission": "Механика/Автомат"
    },
    {
        "name": "Jetta VS8",
        "brand": "Jetta",
        "model": "VS8",
        "image": "images/china/catalog/jetta-vs8.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 1 50",
            "Макс. скорость, км/ч: 175",
            "Привод: Передний",
            "Объем двигателя: 1395",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "1 50 л.с.",
        "maxSpeed": "175 км/ч",
        "drive": "Передний",
        "engineVolume": "1395",
        "transmission": "Вариатор"
    },
    {
        "name": "Hyundai Elantra",
        "brand": "Hyundai",
        "model": "Elantra",
        "image": "images/china/catalog/hyundai-elantra.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 115-140",
            "Макс. скорость, км/ч: 190/208",
            "Привод: Передний",
            "Запас хода, км: 1497/1353",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "115-140 л.с.",
        "maxSpeed": "190/208 км/ч",
        "drive": "Передний",
        "range": "1497/1353 км",
        "transmission": "Вариатор"
    },
    {
        "name": "Skoda Kamiq",
        "brand": "Skoda",
        "model": "Kamiq",
        "image": "images/china/catalog/skoda-kamiq.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 109",
            "Макс. скорость, км/ч: 178",
            "Привод: Передний",
            "Запас хода, км: 1498",
            "Трансмиссия: Автомат"
        ],
        "engineType": "Бензин",
        "power": "109 л.с.",
        "maxSpeed": "178 км/ч",
        "drive": "Передний",
        "range": "1498 км",
        "transmission": "Автомат"
    },
    {
        "name": "Skoda Octavia",
        "brand": "Skoda",
        "model": "Octavia",
        "image": "images/china/catalog/skoda-octavia.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 200",
            "Привод: Передний",
            "Объем двигателя: 1395",
            "Трансмиссия: Робот"
        ],
        "engineType": "Бензин",
        "power": "150 л.с.",
        "maxSpeed": "200 км/ч",
        "drive": "Передний",
        "engineVolume": "1395",
        "transmission": "Робот"
    },
    {
        "name": "Skoda Karoq",
        "brand": "Skoda",
        "model": "Karoq",
        "image": "images/china/catalog/skoda-karoq.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 198",
            "Привод: Передний",
            "Объем двигателя: 1395",
            "Трансмиссия: Робот"
        ],
        "engineType": "Бензин",
        "power": "150 л.с.",
        "maxSpeed": "198 км/ч",
        "drive": "Передний",
        "engineVolume": "1395",
        "transmission": "Робот"
    },
    {
        "name": "Skoda Superb",
        "brand": "Skoda",
        "model": "Superb",
        "image": "images/china/catalog/skoda-superb.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 210",
            "Привод: Передний",
            "Объем двигателя: 1395",
            "Трансмиссия: Робот"
        ],
        "engineType": "Бензин",
        "power": "150 л.с.",
        "maxSpeed": "210 км/ч",
        "drive": "Передний",
        "engineVolume": "1395",
        "transmission": "Робот"
    },
    {
        "name": "Mazda CX-30",
        "brand": "Mazda",
        "model": "CX-30",
        "image": "images/china/catalog/mazda-cx-30.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 158",
            "Макс. скорость, км/ч: 202-204",
            "Привод: Передний",
            "Объем двигателя: 1998",
            "Трансмиссия: Механика"
        ],
        "engineType": "Бензин",
        "power": "158 л.с.",
        "maxSpeed": "202-204 км/ч",
        "drive": "Передний",
        "engineVolume": "1998",
        "transmission": "Механика"
    },
    {
        "name": "Mazda CX-5",
        "brand": "Mazda",
        "model": "CX-5",
        "image": "images/china/catalog/mazda-cx-5.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 1 55",
            "Макс. скорость, км/ч: 187",
            "Привод: Передний",
            "Объем двигателя: 1998",
            "Трансмиссия: Автомат"
        ],
        "engineType": "Бензин",
        "power": "1 55 л.с.",
        "maxSpeed": "187 км/ч",
        "drive": "Передний",
        "engineVolume": "1998",
        "transmission": "Автомат"
    },
    {
        "name": "Mercedes-Benz A-Class",
        "brand": "Mercedes-Benz",
        "model": "A-Class",
        "image": "images/china/catalog/mercedes-benz-a-class.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 136",
            "Макс. скорость, км/ч: 218",
            "Привод: Передний",
            "Объем двигателя: 1332",
            "Трансмиссия: Робот"
        ],
        "engineType": "Бензин",
        "power": "136 л.с.",
        "maxSpeed": "218 км/ч",
        "drive": "Передний",
        "engineVolume": "1332",
        "transmission": "Робот"
    },
    {
        "name": "Honda Envix",
        "brand": "Honda",
        "model": "Envix",
        "image": "images/china/catalog/honda-envix.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 122",
            "Макс. скорость, км/ч: 190",
            "Привод: Передний",
            "Объем двигателя: 998",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "122 л.с.",
        "maxSpeed": "190 км/ч",
        "drive": "Передний",
        "engineVolume": "998",
        "transmission": "Вариатор"
    },
    {
        "name": "Honda Crider",
        "brand": "Honda",
        "model": "Crider",
        "image": "images/china/catalog/honda-crider.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 122",
            "Макс. скорость, км/ч: 190",
            "Привод: Передний",
            "Объем двигателя: 988",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "122 л.с.",
        "maxSpeed": "190 км/ч",
        "drive": "Передний",
        "engineVolume": "988",
        "transmission": "Вариатор"
    },
    {
        "name": "Honda Civic",
        "brand": "Honda",
        "model": "Civic",
        "image": "images/china/catalog/honda-civic.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 1 29",
            "Макс. скорость, км/ч: 200",
            "Привод: Передний",
            "Объем двигателя: 1498",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "1 29 л.с.",
        "maxSpeed": "200 км/ч",
        "drive": "Передний",
        "engineVolume": "1498",
        "transmission": "Вариатор"
    },
    {
        "name": "Kia Sethus",
        "brand": "Kia",
        "model": "Sethus",
        "image": "images/china/catalog/kia-sethus.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 115/140",
            "Макс. скорость, км/ч: 172/190",
            "Привод: Передний",
            "Объем двигателя: 1497/1353",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "115/140 л.с.",
        "maxSpeed": "172/190 км/ч",
        "drive": "Передний",
        "engineVolume": "1497/1353",
        "transmission": "Вариатор"
    },
    {
        "name": "Kia K3",
        "brand": "Kia",
        "model": "K3",
        "image": "images/china/catalog/kia-k3.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 115/140",
            "Макс. скорость, км/ч: 190/200",
            "Привод: Передний",
            "Объем двигателя: 1497/1353",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "115/140 л.с.",
        "maxSpeed": "190/200 км/ч",
        "drive": "Передний",
        "engineVolume": "1497/1353",
        "transmission": "Вариатор"
    },
    {
        "name": "Toyota Levin",
        "brand": "Toyota",
        "model": "Levin",
        "image": "images/china/catalog/toyota-levin.webp",
        "priceFrom": 2100000,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 116/121",
            "Макс. скорость, км/ч: 180",
            "Привод: Передний",
            "Объем двигателя: 1197/1490",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "116/121 л.с.",
        "maxSpeed": "180 км/ч",
        "drive": "Передний",
        "engineVolume": "1197/1490",
        "transmission": "Вариатор"
    },
    {
        "name": "Toyota Corolla",
        "brand": "Toyota",
        "model": "Corolla",
        "image": "images/china/catalog/toyota-corolla.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 116/121",
            "Макс. скорость, км/ч: 180",
            "Привод: Передний",
            "Объем двигателя: 1197/1490",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "Бензин",
        "power": "116/121 л.с.",
        "maxSpeed": "180 км/ч",
        "drive": "Передний",
        "engineVolume": "1197/1490",
        "transmission": "Вариатор"
    },
    {
        "name": "Volkswagen Tharu",
        "brand": "Volkswagen",
        "model": "Tharu",
        "image": "images/china/catalog/volkswagen-tharu.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 110",
            "Макс. скорость, км/ч: 182",
            "Привод: Передний",
            "Объем двигателя: 1498",
            "Трансмиссия: Автомат"
        ],
        "engineType": "Бензин",
        "power": "110 л.с.",
        "maxSpeed": "182 км/ч",
        "drive": "Передний",
        "engineVolume": "1498",
        "transmission": "Автомат"
    },
    {
        "name": "Volkswagen T-Roc",
        "brand": "Volkswagen",
        "model": "T-Roc",
        "image": "images/china/catalog/volkswagen-t-roc.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 200",
            "Привод: Передний",
            "Объем двигателя: 1395",
            "Трансмиссия: Робот"
        ],
        "engineType": "Бензин",
        "power": "150 л.с.",
        "maxSpeed": "200 км/ч",
        "drive": "Передний",
        "engineVolume": "1395",
        "transmission": "Робот"
    },
    {
        "name": "Volkswagen Passat",
        "brand": "Volkswagen",
        "model": "Passat",
        "image": "images/china/catalog/volkswagen-passat.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 210",
            "Привод: Передний",
            "Объем двигателя: 1395",
            "Трансмиссия: Робот"
        ],
        "engineType": "Бензин",
        "power": "150 л.с.",
        "maxSpeed": "210 км/ч",
        "drive": "Передний",
        "engineVolume": "1395",
        "transmission": "Робот"
    },
    {
        "name": "Volkswagen Touran",
        "brand": "Volkswagen",
        "model": "Touran",
        "image": "images/china/catalog/volkswagen-touran.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 190",
            "Привод: Передний",
            "Объем двигателя: 1395",
            "Трансмиссия: Робот"
        ],
        "engineType": "Бензин",
        "power": "150 л.с.",
        "maxSpeed": "190 км/ч",
        "drive": "Передний",
        "engineVolume": "1395",
        "transmission": "Робот"
    },
    {
        "name": "Nissan Qashqai",
        "brand": "Nissan",
        "model": "Qashqai",
        "image": "images/china/catalog/nissan-qashqai.webp",
        "priceFrom": 2934000,
        "specs": [
            "Тип двигателя: ДВС",
            "Мощность, л.с.: 151",
            "Макс. скорость, км/ч: 186",
            "Привод: Передний",
            "Объем двигателя: 1997",
            "Трансмиссия: Вариатор"
        ],
        "engineType": "ДВС",
        "power": "151 л.с.",
        "maxSpeed": "186 км/ч",
        "drive": "Передний",
        "engineVolume": "1997",
        "transmission": "Вариатор"
    },
    {
        "name": "Volkswagen Magotan",
        "brand": "Volkswagen",
        "model": "Magotan",
        "image": "images/china/catalog/volkswagen-magotan.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Бензин",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 210",
            "Привод: Передний",
            "Объем двигателя: 1395",
            "Трансмиссия: Робот"
        ],
        "engineType": "Бензин",
        "power": "150 л.с.",
        "maxSpeed": "210 км/ч",
        "drive": "Передний",
        "engineVolume": "1395",
        "transmission": "Робот"
    },
    {
        "name": "MG MG4",
        "brand": "MG",
        "model": "MG4",
        "image": "images/china/catalog/mg-mg4.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 163",
            "Макс. скорость, км/ч: 160",
            "Привод: Передний",
            "Энергия батареи, кВтч: 42.8",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "163 л.с.",
        "maxSpeed": "160 км/ч",
        "drive": "Передний",
        "battery": "42.8 кВт·ч",
        "transmission": "Редуктор"
    },
    {
        "name": "Geely Galaxy Starwish",
        "brand": "Geely",
        "model": "Galaxy Starwish",
        "image": "images/china/catalog/geely-galaxy-starwish.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 79-116",
            "Макс. скорость, км/ч: 125-135",
            "Привод: Задний",
            "Энергия батареи, кВтч: 30.12-40.16",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "79-116 л.с.",
        "maxSpeed": "125-135 км/ч",
        "drive": "Задний",
        "battery": "30.12-40.16 кВт·ч",
        "transmission": "Редуктор"
    },
    {
        "name": "Mazda EZ-6",
        "brand": "Mazda",
        "model": "EZ-6",
        "image": "images/china/catalog/mazda-ez-6.webp",
        "priceFrom": 3500000,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 217/95",
            "Макс. скорость, км/ч: 170",
            "Привод: Задний",
            "Батарея, кВтч: 28.4",
            "Запас хода, км: 200"
        ],
        "engineType": "Электро",
        "power": "217/95 л.с.",
        "maxSpeed": "170 км/ч",
        "drive": "Задний",
        "battery": "28.4 кВт·ч",
        "range": "200 км"
    },
    {
        "name": "BYD Seagull",
        "brand": "BYD",
        "model": "Seagull",
        "image": "images/china/catalog/byd-seagull.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 75",
            "Макс. скорость, км/ч: 130",
            "Привод: Передний",
            "Энергия батареи, кВтч: 30.08-38.88",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "75 л.с.",
        "maxSpeed": "130 км/ч",
        "drive": "Передний",
        "battery": "30.08-38.88 кВт·ч",
        "transmission": "Редуктор"
    },
    {
        "name": "BYD Yuan UP",
        "brand": "BYD",
        "model": "Yuan UP",
        "image": "images/china/catalog/byd-yuan-up.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 95",
            "Макс. скорость, км/ч: 150-160",
            "Привод: Передний",
            "Энергия батареи, кВтч: 32-45.12",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "95 л.с.",
        "maxSpeed": "150-160 км/ч",
        "drive": "Передний",
        "battery": "32-45.12 кВт·ч",
        "transmission": "Редуктор"
    },
    {
        "name": "BYD Qin Plus EV",
        "brand": "BYD",
        "model": "Qin Plus EV",
        "image": "images/china/catalog/byd-qin-plus-ev.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 136",
            "Макс. скорость, км/ч: 150",
            "Привод: Передний",
            "Энергия батареи, кВтч: 48-57.6",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "136 л.с.",
        "maxSpeed": "150 км/ч",
        "drive": "Передний",
        "battery": "48-57.6 кВт·ч",
        "transmission": "Редуктор"
    },
    {
        "name": "BYD Qin L",
        "brand": "BYD",
        "model": "Qin L",
        "image": "images/china/catalog/byd-qin-l.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 150",
            "Макс. скорость, км/ч: 160",
            "Привод: Задний",
            "Энергия батареи, кВтч: 46.08",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "150 л.с.",
        "maxSpeed": "160 км/ч",
        "drive": "Задний",
        "battery": "46.08 кВт·ч",
        "transmission": "Редуктор"
    },
    {
        "name": "Aion UT",
        "brand": "Aion",
        "model": "UT",
        "image": "images/china/catalog/aion-ut.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 136",
            "Макс. скорость, км/ч: 150",
            "Привод: Передний",
            "Энергия батареи, кВтч: 34.8-44.12",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "136 л.с.",
        "maxSpeed": "150 км/ч",
        "drive": "Передний",
        "battery": "34.8-44.12 кВт·ч",
        "transmission": "Редуктор"
    },
    {
        "name": "JAC Yttrium 3",
        "brand": "JAC",
        "model": "Yttrium 3",
        "image": "images/china/catalog/jac-yttrium-3.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 82/95/136",
            "Макс. скорость, км/ч: 135-150",
            "Привод: Передний",
            "Энергия батареи, кВтч: -",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "82/95/136 л.с.",
        "maxSpeed": "135-150 км/ч",
        "drive": "Передний",
        "battery": "-",
        "transmission": "Редуктор"
    },
    {
        "name": "Baojun Yep Plus",
        "brand": "Baojun",
        "model": "Yep Plus",
        "image": "images/china/catalog/baojun-yep-plus.webp",
        "priceFrom": null,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, л.с.: 102",
            "Макс. скорость, км/ч: 150",
            "Привод: Передний",
            "Энергия батареи, кВтч: 31.9-54",
            "Трансмиссия: Редуктор"
        ],
        "engineType": "Электро",
        "power": "102 л.с.",
        "maxSpeed": "150 км/ч",
        "drive": "Передний",
        "battery": "31.9-54 кВт·ч",
        "transmission": "Редуктор"
    },
    {
        "name": "Toyota BZ3X",
        "brand": "Toyota",
        "model": "BZ3X",
        "image": "images/china/catalog/toyota-bz3x.webp",
        "priceFrom": 2400000,
        "specs": [
            "Тип двигателя: Электро",
            "Мощность, кВт: 150-165",
            "Макс. скорость, км/ч: 160",
            "Привод: Передний",
            "Энергия аккумулятора, кВтч: 50.03-67.92",
            "Запас хода, км: 430-610"
        ],
        "engineType": "Электро",
        "power": "150-165 кВт",
        "maxSpeed": "160 км/ч",
        "drive": "Передний",
        "battery": "50.03-67.92 кВт·ч",
        "range": "430-610 км"
    },
    {
        "name": "Geely Galaxy Starshine 6",
        "brand": "Geely",
        "model": "Galaxy Starshine 6",
        "image": "images/china/catalog/geely-galaxy-starshine-6.webp",
        "priceFrom": 1800608,
        "specs": [
            "Тип двигателя: Гибрид",
            "Мощность, л.с.: 160",
            "Макс. скорость, км/ч: 180",
            "Привод: Передний",
            "Энергия батареи, кВтч: 8.5-17",
            "Трансмиссия: Гибридна я"
        ],
        "engineType": "Гибрид",
        "power": "160 л.с.",
        "maxSpeed": "180 км/ч",
        "drive": "Передний",
        "battery": "8.5-17 кВт·ч",
        "transmission": "Гибридна я"
    }
];;

const koreaCars = [
    {
        name: 'Hyundai Palisade Calligraphy',
        brand: 'Hyundai',
        model: 'Palisade',
        engine: '3.8 л',
        power: '295 л.с.',
        drive: 'Полный',
        leadTime: '60-70 дней',
        highlights: ['7 мест, вентиляция сидений', 'Премиальная акустика Harman Kardon'],
        price: 3990000,
        image: 'https://cdn.motor1.com/images/mgl/4mZxG/s1/2023-hyundai-palisade.jpg'
    },
    {
        name: 'Kia Carnival Hi-Limousine',
        brand: 'Kia',
        model: 'Carnival',
        engine: '3.5 л',
        power: '294 л.с.',
        drive: 'Передний',
        leadTime: '65-75 дней',
        highlights: ['Капсула с подсветкой и креслами Relax', 'Двухпанорамная крыша и медиасистема'],
        price: 3890000,
        image: 'https://cdn.motor1.com/images/mgl/vB6eE/s1/2022-kia-carnival-hi-limousine.jpg'
    },
    {
        name: 'Kia Sorento Hybrid AWD',
        brand: 'Kia',
        model: 'Sorento Hybrid',
        engine: '1.6 л гибрид',
        power: '230 л.с.',
        drive: 'Полный',
        leadTime: '55-65 дней',
        highlights: ['Расход 6.5 л/100 км', 'Полный пакет систем безопасности Drive Wise'],
        price: 3290000,
        image: 'https://cdn.motor1.com/images/mgl/2rJ0k/s1/2023-kia-sorento-hybrid.jpg'
    },
    {
        name: 'Genesis GV70 2.5T AWD',
        brand: 'Genesis',
        model: 'GV70',
        engine: '2.5 л турбо',
        power: '304 л.с.',
        drive: 'Полный',
        leadTime: '65-75 дней',
        highlights: ['Салон из кожи Napa и дерево', 'Электронная подвеска и проекция'],
        price: 4590000,
        image: 'https://cdn.motor1.com/images/mgl/y6Opn/s1/2022-genesis-gv70.jpg'
    },
    {
        name: 'Genesis G80 2.5T',
        brand: 'Genesis',
        model: 'G80',
        engine: '2.5 л турбо',
        power: '304 л.с.',
        drive: 'Полный / задний',
        leadTime: '60-70 дней',
        highlights: ['Пакет Smart Sense', 'Салон с комфортными креслами Relax'],
        price: 3990000,
        image: 'https://cdn.motor1.com/images/mgl/Onq9Q/s1/2021-genesis-g80.jpg'
    }
];

const koreaUnder160Cars = Array.isArray(window.koreaUnder160CarsData) ? window.koreaUnder160CarsData : [];

async function loadUsaOrdersSection(){
    // Проверяем наличие контейнера на странице
    const container = document.getElementById('usaUnder160Grid');
    const metrics = document.getElementById('usaMetrics');
    
    if (!container && !metrics) {
        return; // Элементы не найдены на этой странице
    }
    
    // Убеждаемся, что данные загружены
    if (typeof usaUnder160Cars === 'undefined' || !Array.isArray(usaUnder160Cars) || usaUnder160Cars.length === 0) {
        if (container) {
            container.innerHTML = '<div class="usa-empty-state">Нет доступных предложений</div>';
        }
        if (metrics) {
            const countEl = metrics.querySelector('[data-metric="count"]');
            if (countEl) countEl.textContent = '0';
            const avgEl = metrics.querySelector('[data-metric="avg"]');
            if (avgEl) avgEl.textContent = '—';
            const minEl = metrics.querySelector('[data-metric="min"]');
            if (minEl) minEl.textContent = '—';
        }
        return;
    }
    
    // Обновляем метрики если есть секция
    if (metrics) {
        try {
            const prices = usaUnder160Cars.map(item=>item.price).filter(Boolean).sort((a,b)=>a-b);
            const avg = prices.length ? Math.round(prices.reduce((sum,val)=>sum+val,0)/prices.length) : null;
            const min = prices.length ? prices[0] : null;

            const countEl = metrics.querySelector('[data-metric="count"]');
            const avgEl = metrics.querySelector('[data-metric="avg"]');
            const minEl = metrics.querySelector('[data-metric="min"]');
            
            if (countEl) countEl.textContent = numberFormatter.format(usaUnder160Cars.length);
            if (avgEl) avgEl.textContent = avg ? formatCurrency(avg) : '—';
            if (minEl) minEl.textContent = min ? formatCurrency(min) : '—';
        } catch (error) {
            console.error('Ошибка обновления метрик USA:', error);
        }
    }

    // Рендерим автомобили
    if (container) {
        renderPreferentialCars();
    }
}

function parseUsaCsv(text){
    const lines = text.split(/\r?\n/).map(line=>line.trim()).filter(Boolean);
    const entries = [];
    for (const line of lines){
        const parts = line.split(';').map(part=>part.trim());
        if (parts.length < 7) continue;
        const id = parseInt(parts[0], 10);
        if (!Number.isFinite(id)) continue;
        const name = parts[1].replace(/\s+/g,' ').trim();
        const vin = parts[2];
        const price = safeParseNumber(parts[3]);
        const photos = parts[4];
        const mileage = safeParseNumber(parts[5]);
        const productionDate = parts[6];
        entries.push({ id, name, vin, price, photos, mileage, productionDate });
    }
    return entries;
}

function parseBaseCsv(text){
    const lines = text.split(/\r?\n/);
    if (!lines.length) return [];
    const entries = [];
    for (let i = 1; i < lines.length; i++){
        const line = lines[i];
        if (!line || !line.trim()) continue;
        const parts = splitCsvLine(line);
        if (parts.length < 11) continue;
        const id = safeParseNumber(parts[0]);
        if (!Number.isFinite(id)) continue;
        const brand = parts[1];
        const model = parts[2];
        const year = parts[3];
        const price = safeParseNumber(parts[4]);
        const mileage = safeParseNumber(parts[5]);
        const vin = null;
        const name = `${year} ${brand} ${model}`.trim();
        entries.push({ id, name, vin, price, mileage, productionDate: year, photos: parts[10] || '' });
    }
    return entries;
}

function splitCsvLine(line){
    const result = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++){
        const char = line[i];
        if (char === '"'){
            if (inQuotes && line[i+1] === '"'){
                current += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (char === ',' && !inQuotes){
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current.trim());
    return result;
}

function safeParseNumber(value){
    if (!value) return null;
    const numeric = String(value).replace(/[^0-9]/g, '');
    if (!numeric) return null;
    const num = parseInt(numeric, 10);
    return Number.isFinite(num) ? num : null;
}

function renderPreferentialCars(){
    const container = document.getElementById('usaUnder160Grid');
    if (!container) return;

    if (typeof usaUnder160Cars === 'undefined' || !Array.isArray(usaUnder160Cars) || !usaUnder160Cars.length){
        container.innerHTML = '<div class="usa-empty-state">Нет подготовленных предложений по льготному утильсбору</div>';
        return;
    }

    container.innerHTML = '';

    usaUnder160Cars.forEach(car=>{
        const imageSrc = car.image || buildSvgPlaceholder(car.name || 'Автомобиль');
        const card = document.createElement('article');
        card.className = 'orders-card usa-under-card';
        card.innerHTML = `
            <img src="${imageSrc}" alt="${car.name || 'Автомобиль'}" loading="lazy">
            <div class="orders-card-body">
                <h4>${car.name || 'Автомобиль'}</h4>
                <span class="usa-preferential-badge"><i class="fas fa-leaf"></i> льготный утильсбор</span>
                <ul class="usa-preferential-meta">
                    <li><span>Двигатель:</span> ${car.engine || '—'}</li>
                    <li><span>Мощность:</span> ${car.power || '—'}</li>
                    <li><span>Привод:</span> ${car.drive || '—'}</li>
                </ul>
                <div class="usa-preferential-price">от ${typeof formatCurrency === 'function' ? formatCurrency(car.price || 0) : (typeof formatPrice === 'function' ? formatPrice(car.price || 0, 'USD') : `$${car.price || 0}`)}</div>
                <div class="usa-order-actions" style="margin-top:0.5rem;">
                    <button class="btn-primary" type="button">Запросить расчет</button>
                </div>
            </div>
        `;

        const actionBtn = card.querySelector('.btn-primary');
        if (actionBtn) {
            actionBtn.addEventListener('click', ()=>{
                openRequestModal();
                prefillUsaRequest({ name: car.name, brand: car.brand, model: car.model, price: car.price });
            });
        }

        attachImageFallback(card.querySelector('img'), car);

        container.appendChild(card);
    });
}

function loadChinaOrdersSection(){
    const grid = document.getElementById('chinaUnder160Grid');
    
    if (!grid) {
        return; // Элемент не найден на этой странице
    }
    
    // Убеждаемся, что данные загружены
    if (typeof chinaCars === 'undefined' || !Array.isArray(chinaCars) || chinaCars.length === 0) {
        grid.innerHTML = '<div class="usa-empty-state">Нет доступных предложений</div>';
        updateChinaUnder160Counters();
        return;
    }
    
    try {
        setupChinaUnder160Section();
        updateChinaUnder160Counters();
    } catch (error) {
        console.error('Ошибка загрузки секции China:', error);
        grid.innerHTML = '<div class="usa-empty-state">Ошибка загрузки данных</div>';
    }
}

function loadKoreaOrdersSection(){
    const koreaUnder160Grid = document.getElementById('koreaUnder160Grid');
    const koreaOrdersGrid = document.getElementById('koreaOrdersGrid');
    const koreaMetrics = document.getElementById('koreaMetrics');
    
    // Если нет ни одного элемента на странице, выходим
    if (!koreaUnder160Grid && !koreaOrdersGrid) {
        return;
    }
    
    // Сначала настраиваем секцию для автомобилей до 160 л.с.
    if (koreaUnder160Grid) {
        try {
            setupKoreaUnder160Section();
        } catch (error) {
            console.error('Ошибка настройки секции Korea Under 160:', error);
            if (koreaUnder160Grid) {
                koreaUnder160Grid.innerHTML = '<div class="usa-empty-state">Ошибка загрузки данных</div>';
            }
        }
    }
    
    // Проверяем наличие секции для обычных автомобилей (может отсутствовать)
    if (koreaOrdersGrid && koreaMetrics && typeof koreaCars !== 'undefined' && Array.isArray(koreaCars) && koreaCars.length > 0) {
        try {
            // Конвертируем цены из рублей в доллары если нужно
            const prices = koreaCars.map(car => {
                let price = car.price;
                if (price && price > 10000 && typeof usdToRubRate !== 'undefined' && usdToRubRate) {
                    price = convertRubToUsd(price);
                }
                return price;
            }).filter(Boolean).sort((a,b)=>a-b);
            
            const avg = prices.length ? Math.round(prices.reduce((sum,val)=>sum+val,0)/prices.length) : null;
            const min = prices.length ? prices[0] : null;

            const countEl = koreaMetrics.querySelector('[data-metric="count"]');
            const avgEl = koreaMetrics.querySelector('[data-metric="avg"]');
            const minEl = koreaMetrics.querySelector('[data-metric="min"]');
            
            if (countEl) countEl.textContent = numberFormatter.format(koreaCars.length);
            if (avgEl) avgEl.textContent = avg ? formatCurrency(avg) : '—';
            if (minEl) minEl.textContent = min ? formatCurrency(min) : '—';

            koreaOrdersGrid.innerHTML = '';

            koreaCars.forEach(car=>{
                const highlightsHtml = car.highlights && car.highlights.length
                    ? `<ul class="orders-highlights">${car.highlights.map(item=>`<li><i class=\"fas fa-check\"></i>${item}</li>`).join('')}</ul>`
                    : '';
                
                // Конвертируем цену из рублей в доллары если нужно
                let displayPrice = car.price;
                if (displayPrice && displayPrice > 10000 && typeof usdToRubRate !== 'undefined' && usdToRubRate) {
                    displayPrice = convertRubToUsd(displayPrice);
                }
                
                const card = document.createElement('article');
                card.className = 'orders-card korea-card';
                card.innerHTML = `
                    <img src="${car.image || buildSvgPlaceholder(car.name)}" alt="${car.name}" loading="lazy">
                    <div class="orders-card-body">
                        <h4>${car.name}</h4>
                        <ul class="usa-preferential-meta">
                            <li><span>Двигатель:</span> ${car.engine || '—'}</li>
                            <li><span>Мощность:</span> ${car.power || '—'}</li>
                            <li><span>Привод:</span> ${car.drive || '—'}</li>
                            <li><span>Срок:</span> ${car.leadTime || '60-75 дней'}</li>
                        </ul>
                        ${highlightsHtml}
                        <div class="usa-preferential-price">от ${formatCurrency(displayPrice)}</div>
                        <div class="usa-order-actions" style="margin-top:0.5rem;">
                            <button class="btn-primary" type="button">Запросить расчет</button>
                        </div>
                    </div>
                `;

                const btn = card.querySelector('.btn-primary');
                if (btn) {
                    btn.addEventListener('click', ()=>{
                        openRequestModal();
                        prefillKoreaRequest(car);
                    });
                }

                attachImageFallback(card.querySelector('img'), car);
                koreaOrdersGrid.appendChild(card);
            });
        } catch (error) {
            console.error('Ошибка рендеринга автомобилей Korea:', error);
            if (koreaOrdersGrid) {
                koreaOrdersGrid.innerHTML = '<div class="usa-empty-state">Ошибка загрузки данных</div>';
            }
        }
    }
}

function renderChinaUnder160Cars(){
    const grid = document.getElementById('chinaUnder160Grid');
    if (!grid) return;

    const list = state.chinaUnder160 ? state.chinaUnder160.filtered : chinaCars;

    if (!list.length){
        grid.innerHTML = '<div class="usa-empty-state">Нет подготовленных предложений по льготному утильсбору</div>';
        return;
    }

    grid.innerHTML = '';

    list.forEach(car=>{
        const specs = buildUnder160CarSpecs(car);
        // Конвертируем цену из рублей в доллары если нужно
        let priceValue = getUnder160PriceValue(car);
        
        // Обрабатываем priceLabel: если он содержит рубли, конвертируем в доллары
        let priceLabel = car.priceLabel;
        if (priceLabel && (priceLabel.includes('₽') || priceLabel.includes('руб'))) {
            // Извлекаем число из priceLabel (убираем пробелы, ₽, руб)
            const priceMatch = priceLabel.match(/[\d\s,]+/);
            if (priceMatch) {
                const priceNum = parseInt(priceMatch[0].replace(/[\s,]/g, ''), 10);
                // Если цена больше 1000, вероятно это рубли - конвертируем в доллары
                if (priceNum && priceNum > 1000 && usdToRubRate) {
                    const usdPrice = convertRubToUsd(priceNum);
                    priceLabel = `от ${formatCurrency(usdPrice)}`;
                }
            }
        } else if (!priceLabel) {
            // Если priceValue уже в USD (после конвертации), используем его
            priceLabel = priceValue ? `от ${formatCurrency(priceValue)}` : 'Цена по запросу';
        } else if (priceLabel && !priceLabel.includes('от')) {
            // Проверяем, не является ли цена в рублях (число больше 1000 без символа валюты)
            const priceMatch = priceLabel.match(/[\d\s,]+/);
            if (priceMatch) {
                const priceNum = parseInt(priceMatch[0].replace(/[\s,]/g, ''), 10);
                if (priceNum && priceNum > 1000 && priceNum < 1000000 && usdToRubRate) {
                    // Вероятно это рубли - конвертируем
                    const usdPrice = convertRubToUsd(priceNum);
                    priceLabel = `от ${formatCurrency(usdPrice)}`;
                } else {
                    priceLabel = `от ${priceLabel}`;
                }
            } else {
                priceLabel = `от ${priceLabel}`;
            }
        }
        const brandBadge = car.brand ? `<span class="orders-card-brand">${car.brand}</span>` : '';
        const descriptionHtml = car.description ? `<p class="orders-card-desc">${car.description}</p>` : '';
        const imageSrc = car.image || buildSvgPlaceholder(`${car.brand || ''} ${car.model || car.name || ''}`.trim() || car.name);

        const card = document.createElement('article');
        card.className = 'orders-card china-card';
        card.innerHTML = `
            <img src="${imageSrc}" alt="${car.name}" loading="lazy">
            <div class="orders-card-body">
                ${brandBadge}
                <h4>${car.name}</h4>
                ${descriptionHtml}
                <ul class="usa-preferential-meta">
                    ${specs.map(item => `<li>${item}</li>`).join('')}
                </ul>
                <div class="usa-preferential-price">${priceLabel}</div>
                <div class="usa-order-actions" style="margin-top:0.5rem;">
                    <button class="btn-primary" type="button">Запросить расчет</button>
                </div>
            </div>
        `;

        const btn = card.querySelector('.btn-primary');
        if (btn) {
            btn.addEventListener('click', ()=>{
                openRequestModal();
                prefillChinaRequest(car);
            });
        }

        const img = card.querySelector('img');
        if (img) {
            attachImageFallback(img, car);
        }

        grid.appendChild(card);
    });
}

function prefillUsaRequest(entry){
    try{
        const brandModel = extractBrandModel(entry.name || `${entry.brand || ''} ${entry.model || ''}`.trim());
        const brandEl = document.getElementById('reqBrand');
        const modelEl = document.getElementById('reqModel');
        const yearFromEl = document.getElementById('reqYearFrom');
        const yearToEl = document.getElementById('reqYearTo');
        const priceEl = document.getElementById('reqPriceTo');
        const note = document.getElementById('reqNote');
        if (!brandEl || !modelEl || !yearFromEl || !yearToEl || !priceEl || !note) return;
        brandEl.value = entry.brand || brandModel.brand;
        modelEl.value = entry.model || brandModel.model;
        yearFromEl.value = brandModel.year || '';
        yearToEl.value = brandModel.year || '';
        priceEl.value = entry.price || '';
        const parts = [
            `Автомобиль из США: ${entry.name}`,
            entry.vin ? `VIN: ${entry.vin}` : null,
            entry.photos ? `Фото / лот: ${entry.photos}` : null,
            entry.mileage ? `Пробег: ${numberFormatter.format(entry.mileage)} км` : null
        ].filter(Boolean);
        note.value = parts.join('\n');
    }catch(e){ /* ignore */ }
}

function prefillChinaRequest(car){
    try{
        const brandEl = document.getElementById('reqBrand');
        const modelEl = document.getElementById('reqModel');
        const priceEl = document.getElementById('reqPriceTo');
        const noteEl = document.getElementById('reqNote');
        if (!brandEl || !modelEl || !priceEl || !noteEl) return;
        brandEl.value = car.brand || '';
        modelEl.value = car.model || car.name || '';
        const priceValue = getUnder160PriceValue(car);
        priceEl.value = priceValue ? String(priceValue) : '';
        const details = [
            `Авто из Китая: ${car.name}`,
            car.engineType ? `Тип двигателя: ${car.engineType}` : null,
            car.engineVolume ? `Объем двигателя: ${car.engineVolume}` : null,
            car.power ? `Мощность: ${car.power}` : null,
            car.maxSpeed ? `Максимальная скорость: ${car.maxSpeed}` : null,
            car.drive ? `Привод: ${car.drive}` : null,
            car.transmission ? `Трансмиссия: ${car.transmission}` : null,
            car.consumption ? `Расход топлива: ${car.consumption}` : null,
            car.battery ? `Энергия батареи: ${car.battery}` : null,
            car.range ? `Запас хода: ${car.range}` : null
        ].filter(Boolean);
        if (Array.isArray(car.specs) && car.specs.length){
            car.specs.forEach(spec => {
                if (!details.includes(spec)){
                    details.push(spec);
                }
            });
        }
        noteEl.value = details.join('\n');
    }catch(e){ /* ignore */ }
}

function prefillKoreaRequest(car){
    try{
        const brandEl = document.getElementById('reqBrand');
        const modelEl = document.getElementById('reqModel');
        const priceEl = document.getElementById('reqPriceTo');
        const noteEl = document.getElementById('reqNote');
        if (!brandEl || !modelEl || !priceEl || !noteEl) return;
        brandEl.value = car.brand || '';
        modelEl.value = car.model || car.name || '';
        const priceValue = getUnder160PriceValue(car);
        priceEl.value = priceValue ? String(priceValue) : '';
        const details = [
            `Авто из Кореи: ${car.name}`,
            car.years ? `Годы выпуска: ${car.years}` : null,
            car.engineType ? `Тип двигателя: ${car.engineType}` : null,
            car.engineVolume ? `Объем двигателя: ${car.engineVolume}` : null,
            car.power ? `Мощность: ${car.power}` : null,
            car.drive ? `Привод: ${car.drive}` : null,
            car.transmission ? `Трансмиссия: ${car.transmission}` : null,
            car.description ? `Описание: ${car.description}` : null
        ].filter(Boolean).join('\n');
        noteEl.value = details;
    }catch(e){ /* ignore */ }
}

function extractBrandModel(name){
    const result = { brand: '', model: '', year: '' };
    if (!name) return result;
    const clean = name.split(',')[0].trim();
    const yearMatch = clean.match(/^(\d{4})\s+(.+)$/);
    if (yearMatch){
        result.year = yearMatch[1];
        const rest = yearMatch[2].trim();
        const parts = rest.split(/\s+/);
        result.brand = parts.shift() || '';
        result.model = parts.join(' ');
    } else {
        const segments = clean.split(/\s+/);
        result.brand = segments.shift() || '';
        result.model = segments.join(' ');
    }
    return result;
}

function openCheckoutModal(){
    const modal = document.getElementById('checkoutModal');
    if (!modal) return;
    // Populate checkout summary with cart items
    const summaryEl = document.getElementById('checkoutSummary');
    if (summaryEl && state.cart.length > 0) {
        const rows = state.cart.map(item =>
            `<div class="checkout-summary__row">
                <span>${item.year} ${item.brand} ${item.model}</span>
                <span>${formatCurrency(item.price)}</span>
            </div>`
        ).join('');
        const total = state.cart.reduce((s, i) => s + i.price, 0);
        summaryEl.innerHTML = `
            <div class="checkout-summary__inner">
                ${rows}
                <div class="checkout-summary__total">
                    <span>Итого</span>
                    <span>${formatCurrency(total)}</span>
                </div>
            </div>`;
    }
    modal.style.display = 'block';
}
function closeCheckoutModal(){
    const modal = document.getElementById('checkoutModal');
    if (modal) modal.style.display = 'none';
}

// ── Favorites ────────────────────────────────────────────
function toggleFavorite(carId) {
    const idx = state.favorites.indexOf(carId);
    if (idx === -1) {
        state.favorites.push(carId);
        showNotification('Добавлено в избранное ❤️');
    } else {
        state.favorites.splice(idx, 1);
        showNotification('Удалено из избранного');
    }
    try { localStorage.setItem('expomirFavorites', JSON.stringify(state.favorites)); } catch(e) {}
    updateFavoritesCount();
    // flip icon on visible card
    const btn = document.querySelector(`.fav-btn[data-car-id="${carId}"]`);
    if (btn) btn.classList.toggle('fav-btn--active', state.favorites.includes(carId));
}

function updateFavoritesCount() {
    const count = state.favorites.length;
    document.querySelectorAll('.fav-badge').forEach(el => {
        el.textContent = count || '';
        el.classList.toggle('fav-badge--visible', count > 0);
    });
}

// ── Sort ─────────────────────────────────────────────────
function applySort(cars) {
    const sortEl = document.getElementById('sortSelect');
    const sortBy = sortEl ? sortEl.value : 'default';
    const sorted = [...cars];
    switch (sortBy) {
        case 'price-asc':  return sorted.sort((a, b) => a.price - b.price);
        case 'price-desc': return sorted.sort((a, b) => b.price - a.price);
        case 'year-desc':  return sorted.sort((a, b) => b.year - a.year);
        case 'mileage-asc': return sorted.sort((a, b) => a.mileage - b.mileage);
        case 'fav':        return sorted.sort((a, b) => {
            const af = state.favorites.includes(a.id) ? -1 : 1;
            const bf = state.favorites.includes(b.id) ? -1 : 1;
            return af - bf;
        });
        default: return sorted;
    }
}

// ── View mode ────────────────────────────────────────────
function setViewMode(mode) {
    state.viewMode = mode;
    try { localStorage.setItem('expomirViewMode', mode); } catch(e) {}
    const grid = document.getElementById('carsGrid');
    if (grid) grid.classList.toggle('cars-grid--list', mode === 'list');
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-view') === mode);
    });
}

// ── VIN clipboard copy ────────────────────────────────────
function copyVin(vin) {
    if (!vin) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(vin).then(() => showNotification('VIN скопирован: ' + vin)).catch(() => {});
    } else {
        const ta = document.createElement('textarea');
        ta.value = vin;
        ta.style.cssText = 'position:fixed;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); showNotification('VIN скопирован: ' + vin); } catch(e) {}
        document.body.removeChild(ta);
    }
}

// ── Update catalog count label ────────────────────────────
function updateCatalogCount(total) {
    const el = document.getElementById('catalogCount');
    if (!el) return;
    const avail = state.filteredCars.filter(c => !c.sold).length;
    el.innerHTML = `Найдено: <strong>${total}</strong> авто, <strong>${avail}</strong> в наличии`;
}

function showSkeletonCards(grid, count) {
    grid.innerHTML = '';
    for (var i = 0; i < count; i++) {
        var sk = document.createElement('div');
        sk.className = 'car-card skeleton-card';
        sk.innerHTML = '<div class="skeleton-img"></div><div class="skeleton-body"><div class="skeleton-line"></div><div class="skeleton-line skeleton-line--short"></div><div class="skeleton-line skeleton-line--price"></div></div>';
        grid.appendChild(sk);
    }
}

function loadCars() {
    const carsGrid = document.getElementById('carsGrid');
    if (!carsGrid) return;

    const sorted = applySort(state.filteredCars);
    updateCatalogCount(sorted.length);

    // Apply list/grid class immediately
    carsGrid.classList.toggle('cars-grid--list', state.viewMode === 'list');

    // Empty state when no results match filters
    if (sorted.length === 0) {
        carsGrid.innerHTML = `
            <div class="catalog-empty-state">
                <div class="catalog-empty-state__icon"><i class="fas fa-car-side"></i></div>
                <h3 class="catalog-empty-state__title">Автомобилей не найдено</h3>
                <p class="catalog-empty-state__text">По вашему запросу ничего не нашли. Измените параметры поиска или сбросьте фильтры — мы подберём любой автомобиль по заявке.</p>
                <div class="catalog-empty-state__actions">
                    <button class="btn-primary catalog-empty-state__btn" id="emptyStateReset">
                        <i class="fas fa-redo"></i> Сбросить фильтры
                    </button>
                    <button class="btn-secondary catalog-empty-state__btn" onclick="openRequestModal()">
                        <i class="fas fa-search"></i> Оставить заявку
                    </button>
                </div>
            </div>`;
        const resetBtn = carsGrid.querySelector('#emptyStateReset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                const resetFiltersBtn = document.getElementById('resetFilters');
                if (resetFiltersBtn) resetFiltersBtn.click();
            });
        }
        return;
    }

    // Show skeleton placeholders while rendering
    showSkeletonCards(carsGrid, Math.min(sorted.length, 8));

    // Render real cards asynchronously so skeletons show first
    requestAnimationFrame(function () {
        const fragment = document.createDocumentFragment();
        sorted.forEach(car => fragment.appendChild(createCarCard(car)));
        carsGrid.innerHTML = '';
        carsGrid.appendChild(fragment);
        // After render, update all fav buttons
        state.favorites.forEach(id => {
            const btn = carsGrid.querySelector(`.fav-btn[data-car-id="${id}"]`);
            if (btn) btn.classList.add('fav-btn--active');
        });
    });
}

function createCarCard(car) {
    const card = document.createElement('div');
    card.className = 'car-card';
    const isFav = state.favorites.includes(car.id);
    
    card.innerHTML = `
        <div class="car-image">
            <div class="single-photo-container" data-action="show-details" data-car-id="${car.id}">
                <img 
                    src="images/car${car.id}/main.jpg" 
                    alt="${car.year} ${car.brand} ${car.model}"
                    class="car-photo"
                    loading="lazy">
                ${car.sold ? `
                <div class="sold-overlay">
                    <div class="sold-overlay__label">ПРОДАНО</div>
                </div>
                ` : ''}
            </div>
            <button class="fav-btn${isFav ? ' fav-btn--active' : ''}" data-car-id="${car.id}" aria-label="В избранное" title="В избранное">
                <i class="fas fa-heart"></i>
            </button>
        </div>
        <div class="car-info">
            <h3 class="car-title">${car.year} ${car.brand} ${car.model}</h3>
            <div class="car-details">
                <div><strong>Двигатель:</strong> ${formatEngine(car.engine)}</div>
                <div><strong>Пробег:</strong> ${numberFormatter.format(car.mileage)} км</div>
                <div class="vin-row">
                    <strong>VIN:</strong>
                    <a href="https://www.google.com/search?q=${car.vin}" target="_blank" rel="noopener" class="vin-link">${car.vin}</a>
                    <button class="vin-copy-btn" data-vin="${car.vin}" title="Скопировать VIN"><i class="fas fa-copy"></i></button>
                </div>
                <div><strong>Дата выпуска:</strong> ${car.date}</div>
            </div>
            <div class="car-price">${formatCurrency(car.price)}</div>
            <div class="price-note">
                <i class="fas fa-check-circle"></i> Включает растаможку и доставку
            </div>
            <div class="car-actions">
                ${car.sold ? `
                <button class="btn-primary" data-action="request-similar" data-car-id="${car.id}">
                    Подобрать аналогичный
                </button>
                ` : `
                <button class="btn-primary" data-action="add-to-cart" data-car-id="${car.id}">
                    <i class="fas fa-shopping-cart"></i> Заказать
                </button>
                `}
                <button class="btn-secondary" data-action="show-details" data-car-id="${car.id}">
                    <i class="fas fa-eye"></i> Подробнее
                </button>
            </div>
        </div>
    `;

    const imageEl = card.querySelector('.car-photo');
    if (imageEl) {
        attachImageFallback(imageEl, car);
    }

    // Fav button
    const favBtn = card.querySelector('.fav-btn');
    if (favBtn) {
        favBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleFavorite(car.id);
        });
    }

    // VIN copy button
    const copyBtn = card.querySelector('.vin-copy-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            copyVin(car.vin);
        });
    }

    const actionButtons = card.querySelectorAll('[data-action]');
    actionButtons.forEach(button => {
        const action = button.getAttribute('data-action');
        const id = Number(button.getAttribute('data-car-id'));
        if (!Number.isFinite(id)) return;

        if (action === 'show-details') {
            button.addEventListener('click', () => showCarDetails(id));
        } else if (action === 'add-to-cart') {
            button.addEventListener('click', () => addToCart(id));
        } else if (action === 'request-similar') {
            button.addEventListener('click', () => openSimilarRequest(id));
        }
    });

    return card;
}

function populateBrandFilter() {
    const brandFilter = document.getElementById('brandFilter');
    if (!brandFilter) return;
    const brands = [...new Set(carsData.map(car => car.brand))].sort();
    
    brands.forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandFilter.appendChild(option);
    });

    // Populate year filter
    const yearFilter = document.getElementById('yearFilter');
    if (yearFilter) {
        const years = [...new Set(carsData.map(car => car.year))].sort((a, b) => b - a);
        years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearFilter.appendChild(option);
        });
    }
}

function applyFilters() {
    const brandFilterEl = document.getElementById('brandFilter');
    const priceFromEl = document.getElementById('priceFrom');
    const priceToEl = document.getElementById('priceTo');
    const mileageToEl = document.getElementById('mileageTo');
    const yearFilterEl = document.getElementById('yearFilter');
    const searchEl = document.getElementById('carSearch');

    const brandFilter = brandFilterEl ? brandFilterEl.value : '';
    const priceFrom = parseInt(priceFromEl?.value) || 0;
    const priceTo = parseInt(priceToEl?.value) || Infinity;
    const mileageTo = parseInt(mileageToEl?.value) || Infinity;
    const yearFilter = yearFilterEl ? parseInt(yearFilterEl.value) || 0 : 0;
    const searchQuery = (searchEl ? searchEl.value.trim().toLowerCase() : '');

    state.filteredCars = carsData.filter(car => {
        const brandMatch = !brandFilter || car.brand === brandFilter;
        const priceMatch = car.price >= priceFrom && car.price <= priceTo;
        const mileageMatch = car.mileage <= mileageTo;
        const yearMatch = !yearFilter || car.year >= yearFilter;
        const searchMatch = !searchQuery ||
            `${car.brand} ${car.model} ${car.year} ${car.vin || ''}`.toLowerCase().includes(searchQuery);

        return brandMatch && priceMatch && mileageMatch && yearMatch && searchMatch;
    });

    loadCars();
}

function addToCart(carId) {
    const car = carsData.find(c => c.id === carId);
    if (!car) return;
    if (car.sold) {
        showNotification('Автомобиль уже продан', 'error');
        return;
    }

    const existingItem = state.cart.find(item => item.id === carId);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
        state.cart.push({ ...car, quantity: 1 });
        }
        updateCartCount();
        showNotification('Автомобиль добавлен в заказ!');
}

function removeFromCart(carId) {
    state.cart = state.cart.filter(item => item.id !== carId);
    updateCartCount();
    updateCartModal();
}

function updateCartCount() {
    const cartCount = document.getElementById('cartCount');
    if (!cartCount) return;
    const totalItems = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;
}

function showCart() {
    const cartModal = document.getElementById('cartModal');
    if (!cartModal) return;
    cartModal.style.display = 'block';
    updateCartModal();
}

function closeCart() {
    const cartModal = document.getElementById('cartModal');
    if (!cartModal) return;
    cartModal.style.display = 'none';
}

function updateCartModal() {
    const cartBody = document.getElementById('cartBody');
    const cartTotal = document.getElementById('cartTotal');
    if (!cartBody || !cartTotal) return;
    
    if (state.cart.length === 0) {
        cartBody.innerHTML = '<p class="cart-empty">Ваш заказ пуст</p>';
        if (cartTotal) cartTotal.textContent = '$0';
        return;
    }

    let total = 0;
    cartBody.innerHTML = '';

    state.cart.forEach(item => {
        total += item.price * item.quantity;
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div class="cart-item-info">
                <h4>${item.year} ${item.brand} ${item.model}</h4>
                <p class="cart-item-meta">Пробег: ${numberFormatter.format(item.mileage)} км</p>
                <p class="cart-include-note"><i class="fas fa-check-circle"></i> Включает растаможку и доставку</p>
            </div>
            <div class="cart-item-price">
                ${formatCurrency(item.price * item.quantity)}
            </div>
            <button class="remove-item" data-remove-from-cart="${item.id}">
                <i class="fas fa-trash"></i>
            </button>
        `;
        cartBody.appendChild(cartItem);
    });

    cartTotal.textContent = formatCurrency(total);
}

function showCarDetails(carId) {
    const car = carsData.find(c => c.id === carId);
    if (!car) return;

    const carModal = document.getElementById('carModal');
    const carModalTitle = document.getElementById('carModalTitle');
    const carModalBody = document.getElementById('carModalBody');

    carModalTitle.textContent = `${car.year} ${car.brand} ${car.model}`;

    // WhatsApp / Telegram deep links
    const waText = encodeURIComponent(
        `Здравствуйте! Интересует ${car.year} ${car.brand} ${car.model}, VIN: ${car.vin}, цена ${formatCurrency(car.price)}. Хотел бы узнать подробности.`
    );
    const waHref   = `https://wa.me/996755666805?text=${waText}`;
    const tgHref   = `https://t.me/expo_mir`;

    carModalBody.innerHTML = `
        <div class="car-detail">
            <div class="car-detail__gallery">
                ${createCarGallery(car)}
            </div>
            <div class="car-detail__body">
                <div class="car-detail__spec-grid">
                    <div class="car-detail__spec">
                        <span class="car-detail__spec-label"><i class="fas fa-calendar-alt"></i> Год</span>
                        <span class="car-detail__spec-value">${car.year}</span>
                    </div>
                    <div class="car-detail__spec">
                        <span class="car-detail__spec-label"><i class="fas fa-cog"></i> Двигатель</span>
                        <span class="car-detail__spec-value">${formatEngine(car.engine)}</span>
                    </div>
                    <div class="car-detail__spec">
                        <span class="car-detail__spec-label"><i class="fas fa-tachometer-alt"></i> Пробег</span>
                        <span class="car-detail__spec-value">${numberFormatter.format(car.mileage)} км</span>
                    </div>
                    <div class="car-detail__spec">
                        <span class="car-detail__spec-label"><i class="fas fa-clock"></i> Выпуск</span>
                        <span class="car-detail__spec-value">${car.date}</span>
                    </div>
                </div>
                <div class="car-detail__vin">
                    <span class="car-detail__spec-label"><i class="fas fa-id-card"></i> VIN</span>
                    <a href="https://www.google.com/search?q=${car.vin}" target="_blank" rel="noopener" class="vin-link">${car.vin}</a>
                    <button class="vin-copy-btn" data-vin="${car.vin}" title="Скопировать VIN"><i class="fas fa-copy"></i></button>
                </div>
                <div class="car-detail__price-box">
                    ${car.sold ? `<div class="car-detail__sold-badge">ПРОДАНО</div>` : ''}
                    <div class="car-detail__price">${formatCurrency(car.price)}</div>
                    <div class="car-detail__price-note">
                        <i class="fas fa-check-circle"></i> Включает растаможку и доставку
                    </div>
                </div>
                <div class="car-detail__actions">
                    ${car.sold ? `
                    <button class="btn-primary" onclick="openSimilarRequest(${car.id}); closeCarModal();">
                        <i class="fas fa-search"></i> Найти аналогичный
                    </button>
                    ` : `
                    <button class="btn-primary" onclick="addToCart(${car.id}); closeCarModal();">
                        <i class="fas fa-shopping-cart"></i> Заказать
                    </button>
                    `}
                    <a href="${waHref}" target="_blank" rel="noopener" class="btn-whatsapp">
                        <i class="fab fa-whatsapp"></i> WhatsApp
                    </a>
                    <a href="${tgHref}" target="_blank" rel="noopener" class="btn-telegram">
                        <i class="fab fa-telegram-plane"></i> Telegram
                    </a>
                </div>
                <button class="car-detail__calc-btn" onclick="openSelfCalcPreFill(${car.price}, '${car.engine}')">
                    <i class="fas fa-calculator"></i> Рассчитать стоимость под ключ
                </button>
            </div>
        </div>
    `;

    carModal.style.display = 'block';

    setTimeout(() => {
        initializeGallery(car);
        const container = document.getElementById(`gallery-${car.id}`);
        if (container) {
            const prevBtn = container.querySelector('.gallery-prev');
            const nextBtn = container.querySelector('.gallery-next');
            if (prevBtn) prevBtn.addEventListener('click', (e) => { e.stopPropagation(); navigateGallery(car.id, 'prev'); });
            if (nextBtn) nextBtn.addEventListener('click', (e) => { e.stopPropagation(); navigateGallery(car.id, 'next'); });
        }
        // VIN copy button inside modal
        const vinCopyBtn = carModalBody.querySelector('.vin-copy-btn');
        if (vinCopyBtn) {
            vinCopyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                copyVin(vinCopyBtn.dataset.vin);
            });
        }

        // Keyboard navigation for gallery (← →)
        const _keyHandler = (e) => {
            if (e.key === 'ArrowLeft')  navigateGallery(car.id, 'prev');
            if (e.key === 'ArrowRight') navigateGallery(car.id, 'next');
            if (e.key === 'Escape') {
                closeCarModal();
                document.removeEventListener('keydown', _keyHandler);
            }
        };
        document.addEventListener('keydown', _keyHandler);
        // Clean up on close
        carModal.addEventListener('click', function _closeListener(ev) {
            if (ev.target === carModal) {
                document.removeEventListener('keydown', _keyHandler);
                carModal.removeEventListener('click', _closeListener);
            }
        });
    }, 100);
}

// Р¤СѓРЅРєС†РёСЏ РґР»СЏ РЅР°РІРёРіР°С†РёРё РїРѕ РіР°Р»РµСЂРµРµ (СѓРїСЂРѕС‰РµРЅРЅР°СЏ РІРµСЂСЃРёСЏ)
function navigateGallery(carId, direction) {
    if (!state.carGalleries[carId]) return;
    const gallery = state.carGalleries[carId];
    const nextIndex = (gallery.index + (direction === 'next' ? 1 : -1) + gallery.photos.length) % gallery.photos.length;
    setGalleryIndex(carId, nextIndex);
}

function closeCarModal() {
    const carModal = document.getElementById('carModal');
    if (carModal) carModal.style.display = 'none';
}

function checkout() {
    if (state.cart.length === 0) {
        showNotification('Ваш заказ пуст!', 'error');
        return;
    }
    // Открываем модал ввода контактов
    openCheckoutModal();
}

function showNotification(message, type = 'success') {
    // Remove previous toast if still visible
    document.querySelectorAll('.notification').forEach(n => {
        n.classList.add('hiding');
        setTimeout(() => n.remove(), 350);
    });

    const iconMap = {
        success: 'fa-check-circle',
        error:   'fa-times-circle',
        info:    'fa-info-circle',
        warning: 'fa-exclamation-triangle',
    };
    const icon = iconMap[type] || iconMap.success;

    const el = document.createElement('div');
    el.className = `notification notification--${type}`;
    el.innerHTML = `<i class="fas ${icon}"></i> ${message}`;
    document.body.appendChild(el);

    setTimeout(() => {
        el.classList.add('hiding');
        setTimeout(() => el.remove(), 380);
    }, 3200);
}

// Scroll-reveal: fade-up cards and sections when they enter the viewport
function setupScrollReveal() {
    if (!('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });

    document.querySelectorAll('.why-card, .testimonial-card, .hero-stat, .contact-item').forEach(el => {
        el.classList.add('reveal');
        observer.observe(el);
    });

    // Animate hero stat counters when they enter viewport
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const numEl = entry.target.querySelector('[data-count]');
            if (!numEl || numEl.dataset.animated) return;
            numEl.dataset.animated = '1';
            const target = parseInt(numEl.dataset.count, 10);
            const suffix = numEl.dataset.suffix || '';
            if (!Number.isFinite(target)) return;
            const duration = 1400;
            const start = performance.now();
            function tick(now) {
                const elapsed = now - start;
                const progress = Math.min(elapsed / duration, 1);
                // ease-out cubic
                const eased = 1 - Math.pow(1 - progress, 3);
                numEl.textContent = Math.round(eased * target) + suffix;
                if (progress < 1) requestAnimationFrame(tick);
            }
            requestAnimationFrame(tick);
            counterObserver.unobserve(entry.target);
        });
    }, { threshold: 0.5 });
    document.querySelectorAll('.hero-stat').forEach(el => counterObserver.observe(el));
}

function setupEventListeners() {
    // Scroll progress bar + back-to-top + header shrink
    const _header = document.querySelector('.header');
    window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = docHeight > 0 ? scrollTop / docHeight : 0;
        const bar = document.getElementById('scrollProgress');
        if (bar) bar.style.transform = `scaleX(${progress})`;
        const btn = document.getElementById('backToTop');
        if (btn) btn.classList.toggle('back-to-top--visible', scrollTop > 450);
        if (_header) _header.classList.toggle('header--scrolled', scrollTop > 60);
    }, { passive: true });

    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    }

    // Escape key closes any open modal
    document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape') return;
        ['carModal', 'cartModal', 'checkoutModal', 'requestModal', 'selfCalcModal', 'customsModal'].forEach(id => {
            const m = document.getElementById(id);
            if (m && m.style.display === 'block') m.style.display = 'none';
        });
    });

    // Brand filter → auto-populate model filter
    const brandFilterEl = document.getElementById('brandFilter');
    const modelFilterEl = document.getElementById('modelFilter');
    if (brandFilterEl && modelFilterEl) {
        brandFilterEl.addEventListener('change', () => {
            const brand = brandFilterEl.value;
            const models = brand
                ? [...new Set(carsData.filter(c => c.brand === brand).map(c => c.model))].sort()
                : [];
            // Keep "all models" option
            modelFilterEl.innerHTML = '<option value="">Все модели</option>';
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                modelFilterEl.appendChild(opt);
            });
        });
    }

    // Catalog filters
    const applyBtn = document.getElementById('applyFilters');
    const resetBtn = document.getElementById('resetFilters');
    if (applyBtn) applyBtn.addEventListener('click', applyFilters);
    if (resetBtn) resetBtn.addEventListener('click', () => {
        ['brandFilter', 'modelFilter', 'yearFilter', 'priceFrom', 'priceTo', 'mileageTo'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        const searchEl = document.getElementById('carSearch');
        if (searchEl) searchEl.value = '';
        state.filteredCars = [...carsData];
        loadCars();
    });

    // Live search (debounced 300ms)
    const searchEl = document.getElementById('carSearch');
    if (searchEl) {
        let searchTimer;
        searchEl.addEventListener('input', () => {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(applyFilters, 300);
        });
    }

    // Sort
    const sortEl = document.getElementById('sortSelect');
    if (sortEl) sortEl.addEventListener('change', loadCars);

    // View toggle
    const viewToggle = document.getElementById('viewToggle');
    if (viewToggle) {
        viewToggle.addEventListener('click', (e) => {
            const btn = e.target.closest('.view-btn');
            if (!btn) return;
            setViewMode(btn.getAttribute('data-view'));
        });
        // Set initial active state
        setViewMode(state.viewMode);
    }

    // Корзина
    const cartBtn = document.getElementById('cartBtn');
    if (cartBtn) cartBtn.addEventListener('click', showCart);
    const cartBody = document.getElementById('cartBody');
    if (cartBody) {
        cartBody.addEventListener('click', (event) => {
            const removeBtn = event.target.closest('[data-remove-from-cart]');
            if (!removeBtn) return;
            const carId = Number(removeBtn.getAttribute('data-remove-from-cart'));
            if (Number.isFinite(carId)) {
                removeFromCart(carId);
            }
        });
    }
    
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
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const btn = this.querySelector('[type=submit]') || this.querySelector('button');
            const origText = btn ? btn.textContent : '';
            if (btn) { btn.disabled = true; btn.textContent = 'Отправляем…'; }
            const payload = new URLSearchParams(new FormData(this));
            payload.append('_captcha', 'false');
            payload.append('_subject', 'Сообщение с сайта EXPO MIR');
            try {
                const resp = await fetch('https://formsubmit.co/carexportgeo@bk.ru', { method: 'POST', body: payload });
                if (resp.ok) {
                    showNotification('Сообщение отправлено! Свяжемся с вами в ближайшее время.', 'success');
                    this.reset();
                } else {
                    showNotification('Ошибка отправки. Напишите нам напрямую в WhatsApp.', 'error');
                }
            } catch (err) {
                showNotification('Нет соединения. Попробуйте позже или напишите в WhatsApp.', 'error');
            } finally {
                if (btn) { btn.disabled = false; btn.textContent = origText; }
            }
        });
    }

    // Форма контактов для заказа
    const checkoutForm = document.getElementById('checkoutContactForm');
    if (checkoutForm) {
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
        const total = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const items = state.cart.map(i => `${i.year} ${i.brand} ${i.model} — ${i.quantity} шт. — ${formatCurrency(i.price)}`).join('\n');
        const message = `Новый заказ с сайта EXPO MIR\n\nИмя: ${name}\nТелефон: ${phone}\nEmail: ${email}\n\nТовары:\n${items}\n\nИтого: ${formatCurrency(total)}`;

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
        state.cart = [];
        updateCartCount();
        closeCheckoutModal();
        closeCart();
        });
    }

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

    // Управление галереей
    document.addEventListener('click', (event) => {
        const navBtn = event.target.closest('[data-gallery-nav]');
        if (!navBtn) return;
        const carId = Number(navBtn.getAttribute('data-car-id'));
        if (!Number.isFinite(carId)) return;
        const direction = navBtn.getAttribute('data-gallery-nav') === 'next' ? 'next' : 'prev';
        navigateGallery(carId, direction);
    });
}

// === Таможенный калькулятор ===
async function fetchEurRateRub() {
    // Use cached value from initial page load — avoids extra network request
    if (cachedEurRateRub) return cachedEurRateRub;
    try {
        const resp = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
        const data = await resp.json();
        const eur = data?.Valute?.EUR?.Value;
        const usd = data?.Valute?.USD?.Value;
        if (typeof eur === 'number' && eur > 0) { cachedEurRateRub = eur; }
        if (typeof usd === 'number' && usd > 0 && !usdToRubRate) { usdToRubRate = usd; }
        if (cachedEurRateRub) return cachedEurRateRub;
    } catch (e) { /* ignore */ }
    return 100;
}

// Шкала евро/см³ по возрасту (официальные ставки ЕАЭС/КР)
const CUSTOMS_RATES_TABLE = {
    '3-5': [
        { max: 1000, rate: 1.5 },
        { max: 1500, rate: 1.7 },
        { max: 1800, rate: 2.5 },
        { max: 2300, rate: 2.7 },
        { max: 3000, rate: 3.0 },
        { max: Infinity, rate: 3.6 }
    ],
    '5-7': [
        { max: 1000, rate: 3.0 },
        { max: 1500, rate: 3.2 },
        { max: 1800, rate: 3.5 },
        { max: 2300, rate: 4.8 },
        { max: 3000, rate: 5.0 },
        { max: Infinity, rate: 5.7 }
    ],
    '7+': [
        { max: 1000, rate: 3.6 },
        { max: 1500, rate: 4.0 },
        { max: 1800, rate: 4.8 },
        { max: 2300, rate: 5.8 },
        { max: 3000, rate: 6.0 },
        { max: Infinity, rate: 6.6 }
    ]
};

function customsRatePerCc(cc, ageGroup = '3-5') {
    const table = CUSTOMS_RATES_TABLE[ageGroup] || CUSTOMS_RATES_TABLE['3-5'];
    const row = table.find(r => cc <= r.max);
    return row ? row.rate : table[table.length - 1].rate;
}

function customsClearanceFee(costUsd) {
    if (costUsd <= 14999) return 4269;
    if (costUsd <= 40000) return 11746;
    return 16524;
}

// Калькулятор растаможки (для карточек каталога)
async function handleCalc() {
    const costUsd = parseFloat(document.getElementById('costUsd').value);
    const cc      = parseInt(document.getElementById('engineCc').value, 10);
    const ageGroup = (document.getElementById('carAge') || {}).value || '3-5';
    const resultEl = document.getElementById('calcResult');

    if (!isFinite(costUsd) || costUsd <= 0 || !isFinite(cc) || cc <= 0) {
        resultEl.innerHTML = '<span class="calc-error"><i class="fas fa-exclamation-circle"></i> Введите корректные значения стоимости и объёма.</span>';
        return;
    }

    resultEl.innerHTML = '<div class="calc-loading"><i class="fas fa-spinner fa-spin"></i> Загрузка курсов...</div>';

    const eurPerCc  = customsRatePerCc(cc, ageGroup);
    const eurAmount = eurPerCc * cc;
    const [eurRub, usdRub] = await Promise.all([fetchEurRateRub(), fetchUsdRateRub()]);

    const dutyRub   = Math.round(eurAmount * eurRub);
    const dutyUsd   = Math.round(dutyRub / usdRub);
    const feeRub    = customsClearanceFee(costUsd);
    const feeUsd    = Math.round(feeRub / usdRub);
    const totalRub  = dutyRub + feeRub;
    const totalUsd  = dutyUsd + feeUsd;
    const grandUsd  = costUsd + totalUsd;
    const grandRub  = Math.round(grandUsd * usdRub);

    const fmt = n => numberFormatter.format(Math.round(n));
    resultEl.innerHTML = `
        <div class="calc-breakdown">
            <div class="calc-breakdown__title">Расчёт растаможки для Кыргызстана</div>
            <div class="calc-breakdown__row">
                <span>Стоимость автомобиля</span>
                <span><strong>$${fmt(costUsd)}</strong></span>
            </div>
            <div class="calc-breakdown__row calc-breakdown__row--sub">
                <span>Там. пошлина (${eurPerCc} €/см³ × ${fmt(cc)} см³)</span>
                <span>${fmt(Math.round(eurAmount))} € &asymp; $${fmt(dutyUsd)}</span>
            </div>
            <div class="calc-breakdown__row calc-breakdown__row--sub">
                <span>Таможенный сбор</span>
                <span>${fmt(feeRub)} ₽ &asymp; $${fmt(feeUsd)}</span>
            </div>
            <div class="calc-breakdown__row">
                <span><em>Итого растаможка</em></span>
                <span>${fmt(totalRub)} ₽ ≈ $${fmt(totalUsd)}</span>
            </div>
            <div class="calc-breakdown__total">
                <span>Полная стоимость (авто + растаможка)</span>
                <span><strong>$${fmt(grandUsd)}</strong> ≈ ${fmt(grandRub)} ₽</span>
            </div>
            <div class="calc-breakdown__note">
                <i class="fas fa-info-circle"></i>
                Цены автомобилей в каталоге уже включают доставку и растаможку.
                Курсы: 1 $ = ${fmt(usdRub)} ₽, 1 € = ${fmt(eurRub)} ₽.
            </div>
        </div>`;
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
        if (requestBtn.disabled) return;
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
            s.style.removeProperty('display');
            s.className = 'request-status request-status--error';
            s.innerHTML = '<i class="fas fa-exclamation-circle"></i> Заполните обязательные поля: имя, телефон, марка, модель.';
            return;
        }

        const origInner = requestBtn.innerHTML;
        requestBtn.disabled = true;
        requestBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправляем…';

        // отправка через formsubmit.co (без сервера)
        const payload = new URLSearchParams();
        payload.append('name', name);
        payload.append('phone', phone);
        if (email) payload.append('email', email);
        payload.append('message', `Марка: ${brand}\nМодель: ${model}\nГод: ${yf || '-'} - ${yt || '-'}\nБюджет до: ${pt || '-'} $\nПримечание: ${note || '-'}`);
        payload.append('_captcha','false');
        payload.append('_subject','Заявка на подбор (сайт EXPO MIR)');

        try {
            const resp = await fetch('https://formsubmit.co/carexportgeo@bk.ru', { method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body: payload});
            const s = document.getElementById('requestStatus');
            s.style.removeProperty('display');
            if (resp.ok) {
                s.className = 'request-status request-status--success';
                s.innerHTML = '<i class="fas fa-check-circle"></i> Заявка отправлена! Мы свяжемся с вами в ближайшие 15 минут.';
                document.getElementById('requestForm')?.reset();
            } else {
                s.className = 'request-status request-status--error';
                s.innerHTML = '<i class="fas fa-times-circle"></i> Не удалось отправить. Попробуйте позже или напишите в WhatsApp.';
            }
        } catch (_) {
            const s = document.getElementById('requestStatus');
            if (s) {
                s.style.removeProperty('display');
                s.className = 'request-status request-status--error';
                s.innerHTML = '<i class="fas fa-times-circle"></i> Нет соединения. Напишите нам напрямую в WhatsApp.';
            }
        } finally {
            requestBtn.disabled = false;
            requestBtn.innerHTML = origInner;
        }
    });

    // Самостоятельный просчет
    window.openSelfCalcModal = function(){
        const m = document.getElementById('selfCalcModal');
        if (m) m.style.display = 'block';
    }
    window.closeSelfCalcModal = function(){
        const m = document.getElementById('selfCalcModal');
        if (m) m.style.display = 'none';
    }
    const selfBtn = document.getElementById('selfCalcBtn');
    if (selfBtn) selfBtn.addEventListener('click', handleSelfCalc);
});

// Открыть калькулятор стоимости под ключ с предзаполнением данных авто
window.openSelfCalcPreFill = function(priceKgs, engineStr) {
    const m = document.getElementById('selfCalcModal');
    if (!m) return;
    m.style.display = 'block';
    // Конвертируем цену из KGS в USD (используем текущий курс или fallback)
    const rate = usdToRubRate || 88.0;
    const KGS_TO_RUB = 1.17; // примерный курс KGS/RUB
    const priceUsd = Math.round(priceKgs * KGS_TO_RUB / rate);
    const costEl = document.getElementById('selfCostUsd');
    if (costEl) costEl.value = priceUsd;
    // Конвертируем объём двигателя в куб. см
    const engEl = document.getElementById('selfEngineCc');
    if (engEl) {
        const cc = engineToCc(String(engineStr));
        if (cc) engEl.value = cc;
    }
};

// Хелпер для заявки на аналогичный автомобиль
window.openSimilarRequest = function(carId){
    const car = carsData.find(c=>c.id===carId);
    if(!car) return;
    openRequestModal();
    try{
        document.getElementById('reqBrand').value = car.brand || '';
        document.getElementById('reqModel').value = car.model || '';
        document.getElementById('reqYearFrom').value = car.year ? Math.max(1990, parseInt(car.year)-2) : '';
        document.getElementById('reqYearTo').value = car.year || '';
        document.getElementById('reqPriceTo').value = car.price || '';
        const note = document.getElementById('reqNote');
        note.value = `Ищу аналогичный автомобилю: ${car.year} ${car.brand} ${car.model}. VIN: ${car.vin}.`;
    }catch(_){}}

async function handleSelfCalc() {
    const costUsd  = parseFloat(document.getElementById('selfCostUsd').value);
    const cc       = parseInt(document.getElementById('selfEngineCc').value, 10);
    const ageGroup = (document.getElementById('selfCarAge') || {}).value || '3-5';
    const resultEl = document.getElementById('selfCalcResult');

    if (!isFinite(costUsd) || costUsd <= 0 || !isFinite(cc) || cc <= 0) {
        resultEl.innerHTML = '<span class="calc-error"><i class="fas fa-exclamation-circle"></i> Введите корректные значения стоимости и объёма.</span>';
        return;
    }

    resultEl.innerHTML = '<div class="calc-loading"><i class="fas fa-spinner fa-spin"></i> Загрузка курсов...</div>';

    const DELIVERY_USD    = 400;   // доставка Грузия → Кыргызстан
    const SERVICE_FEE_USD = 2400;  // комиссия EXPO MIR

    const eurPerCc  = customsRatePerCc(cc, ageGroup);
    const eurAmount = eurPerCc * cc;
    const [eurRub, usdRub] = await Promise.all([fetchEurRateRub(), fetchUsdRateRub()]);

    const dutyRub  = Math.round(eurAmount * eurRub);
    const dutyUsd  = Math.round(dutyRub / usdRub);
    const feeRub   = customsClearanceFee(costUsd + DELIVERY_USD);
    const feeUsd   = Math.round(feeRub / usdRub);

    const totalCustomsUsd = dutyUsd + feeUsd;
    const grandUsd  = costUsd + DELIVERY_USD + totalCustomsUsd + SERVICE_FEE_USD;
    const grandRub  = Math.round(grandUsd * usdRub);

    const fmt = n => numberFormatter.format(Math.round(n));
    resultEl.innerHTML = `
        <div class="calc-breakdown">
            <div class="calc-breakdown__title">Полная стоимость под ключ — Кыргызстан</div>
            <div class="calc-breakdown__row">
                <span>Стоимость авто на сайте</span>
                <span><strong>$${fmt(costUsd)}</strong></span>
            </div>
            <div class="calc-breakdown__row">
                <span>Доставка Грузия → Кыргызстан</span>
                <span>~$${fmt(DELIVERY_USD)}</span>
            </div>
            <div class="calc-breakdown__row calc-breakdown__row--sub">
                <span>Там. пошлина (${eurPerCc} €/см³ × ${fmt(cc)} см³)</span>
                <span>${fmt(Math.round(eurAmount))} € ≈ $${fmt(dutyUsd)}</span>
            </div>
            <div class="calc-breakdown__row calc-breakdown__row--sub">
                <span>Там. сбор оформления</span>
                <span>${fmt(feeRub)} ₽ ≈ $${fmt(feeUsd)}</span>
            </div>
            <div class="calc-breakdown__row">
                <span>Услуги EXPO MIR (проверка, оформление)</span>
                <span>$${fmt(SERVICE_FEE_USD)}</span>
            </div>
            <div class="calc-breakdown__total">
                <span>ИТОГО к оплате</span>
                <span><strong>$${fmt(grandUsd)}</strong> ≈ ${fmt(grandRub)} ₽</span>
            </div>
            <div class="calc-breakdown__note">
                <i class="fas fa-info-circle"></i>
                Расчёт ориентировочный. Точная стоимость уточняется у менеджера.
                Курсы: 1 $ = ${fmt(usdRub)} ₽, 1 € = ${fmt(eurRub)} ₽.
            </div>
        </div>`;
}

async function fetchUsdRateRub(){
    // Use cached value from initial page load — avoids extra network request
    if (usdToRubRate) return usdToRubRate;
    try{
        const resp = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
        const data = await resp.json();
        const usd = data?.Valute?.USD?.Value;
        const eur = data?.Valute?.EUR?.Value;
        if (typeof usd === 'number' && usd > 0) { usdToRubRate = usd; }
        if (typeof eur === 'number' && eur > 0 && !cachedEurRateRub) { cachedEurRateRub = eur; }
        if (usdToRubRate) return usdToRubRate;
    }catch(e){}
    return 90; // фолбэк
}

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
        const slide = document.createElement('div');
        slide.className = 'gallery-slide';
        const img = document.createElement('img');
        img.src = src;
        img.alt = `${car.year} ${car.brand} ${car.model}`;
        slide.appendChild(img);
        track.appendChild(slide);

        const dot = document.createElement('div');
        dot.className = 'gallery-dot'+(idx===0?' active':'');
        dot.addEventListener('click',()=> setGalleryIndex(car.id, idx));
        dotsWrap.appendChild(dot);
    });

    // Если ни одной фотки — покажем заглушку
    if (photos.length === 0) {
        const fallbackSlide = document.createElement('div');
        fallbackSlide.className = 'gallery-slide';
        const placeholder = document.createElement('div');
        placeholder.style.cssText = 'display:flex;align-items:center;justify-content:center;color:#f3f4f6;font-size:1rem;width:100%;height:100%;';
        placeholder.textContent = 'Фотографии скоро будут';
        fallbackSlide.appendChild(placeholder);
        track.appendChild(fallbackSlide);
    }

    state.carGalleries[car.id] = { index: 0, photos, container, track, dotsWrap };
    setGalleryIndex(car.id, 0);
}

function setGalleryIndex(carId, index){
    const g = state.carGalleries[carId];
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

function onTouchStart(e){
    const gallery = e.target.closest?.('.gallery-container');
    if(!gallery) return;
    const galleryId = Number(gallery.getAttribute('data-car-id'));
    if (!Number.isFinite(galleryId)) {
        state.touch.galleryId = null;
        state.touch.startX = null;
        return;
    }
    state.touch.galleryId = galleryId;
    state.touch.startX = e.touches[0].clientX;
}
function onTouchMove(e){ /* пассивный слушатель, логика не нужна */ }
function onTouchEnd(e){
    if(state.touch.startX===null || state.touch.galleryId===null) return;
    const endX = (e.changedTouches && e.changedTouches[0]?.clientX) || 0;
    const dx = endX - state.touch.startX;
    if(Math.abs(dx) > 40){
        navigateGallery(state.touch.galleryId, dx < 0 ? 'next' : 'prev');
    }
    state.touch.startX = null;
    state.touch.galleryId = null;
}

/**
 * Smart engine display: handles "200" (2.0L), "1,6" (1.6L), "1998" (2.0L), "2,0" (2.0L)
 */
function formatEngine(engine) {
    if (engine == null || engine === '') return '—';
    const s = String(engine).replace(',', '.').trim();
    const n = parseFloat(s);
    if (isNaN(n)) return engine;
    // 100–999 integer: model-variant notation, e.g. "200" = 2.0L
    if (n >= 100 && n < 1000 && Number.isInteger(n)) return (n / 100).toFixed(1) + 'L';
    // ≥1000: cubic centimetres
    if (n >= 1000) return (n / 1000).toFixed(1) + 'L';
    // Otherwise already in litres
    return n.toFixed(1) + 'L';
}

/**
 * Convert engine string to cubic centimetres for customs calculator
 */
function engineToCc(engineStr) {
    if (engineStr == null) return null;
    const s = String(engineStr).replace(',', '.').trim();
    const n = parseFloat(s);
    if (isNaN(n)) return null;
    if (n >= 100 && n < 1000 && Number.isInteger(n)) return Math.round(n * 10); // "200" → 2000cc
    if (n >= 1000) return Math.round(n);  // already cc
    return Math.round(n * 1000);          // litres → cc
}

function buildUnder160CarSpecs(car){
    if (!car) return [];
    if (Array.isArray(car.specs) && car.specs.length){
        return car.specs.slice();
    }
    const specs = [
        car.engineType ? `Тип двигателя: ${car.engineType}` : null,
        car.engineVolume ? `Объем двигателя: ${car.engineVolume}` : null,
        car.power ? `Мощность: ${car.power}` : null,
        car.maxSpeed ? `Макс. скорость: ${car.maxSpeed}` : null,
        car.drive ? `Привод: ${car.drive}` : null,
        car.transmission ? `Трансмиссия: ${car.transmission}` : null,
        car.consumption ? `Расход топлива: ${car.consumption}` : null,
        car.range ? `Запас хода: ${car.range}` : null,
        car.battery ? `Энергия батареи: ${car.battery}` : null
    ].filter(Boolean);
    return specs.length ? specs : ['Характеристики уточняйте у менеджера'];
}

function getUnder160PriceValue(car){
    if (!car) return null;
    let price = null;
    if (typeof car.priceFrom === 'number' && car.priceFrom > 0) {
        price = car.priceFrom;
    } else if (typeof car.price === 'number' && car.price > 0) {
        price = car.price;
    }
    
    if (!price) return null;
    
    // Цены в данных chinaCars указаны в рублях (обычно от 1,000,000 и выше)
    // Цены в долларах для автомобилей обычно от 10,000 до 100,000 USD
    // Если цена больше 500,000, это скорее всего рубли - конвертируем в доллары
    if (price > 500000 && usdToRubRate) {
        const usdPrice = convertRubToUsd(price);
        // Проверяем, что после конвертации получилось разумное значение (от 5,000 до 100,000 USD)
        if (usdPrice >= 5000 && usdPrice <= 100000) {
            return usdPrice;
        }
    }
    
    // Если цена меньше 500,000, вероятно уже в долларах (или очень дешевая в рублях)
    // Для автомобилей из Китая минимальная цена обычно от 15,000 USD
    // Если цена меньше 15,000, это может быть рубли - конвертируем
    if (price < 15000 && price > 1000 && usdToRubRate) {
        const possibleUsd = convertRubToUsd(price);
        // Если после конвертации получилось разумное значение для авто (от 10,000 USD)
        if (possibleUsd >= 10000) {
            return possibleUsd;
        }
    }
    
    // Если цена в диапазоне 15,000 - 500,000, считаем что это уже в долларах
    return price;
}

function setupChinaUnder160Section(){
    const grid = document.getElementById('chinaUnder160Grid');
    if (!grid) return;

    // Проверяем наличие данных
    if (typeof chinaCars === 'undefined' || !Array.isArray(chinaCars) || chinaCars.length === 0) {
        grid.innerHTML = '<div class="usa-empty-state">Нет доступных предложений</div>';
        updateChinaUnder160Counters();
        return;
    }

    if (!state.chinaUnder160) {
        state.chinaUnder160 = {
            data: chinaCars.map((car, index) => ({
                ...car,
                price: getUnder160PriceValue(car),
                _order: index
            })),
            filtered: [],
            filters: { brand: '', query: '', sort: 'default' },
            initialized: false
        };
    }

    if (!state.chinaUnder160.initialized) {
        populateChinaUnder160Filters();
        state.chinaUnder160.initialized = true;
    }

    applyChinaUnder160Filters();
}

function populateChinaUnder160Filters(){
    const store = state.chinaUnder160;
    if (!store) return;

    const brandSelect = document.getElementById('chinaBrandFilter');
    const modelInput = document.getElementById('chinaModelSearch');
    const sortSelect = document.getElementById('chinaSort');
    const resetBtn = document.getElementById('chinaResetFilters');

    if (brandSelect) {
        const brands = [...new Set(store.data.map(car => car.brand).filter(Boolean))]
            .sort((a, b) => a.localeCompare(b, 'ru'));
        brandSelect.innerHTML = '<option value="">Все марки</option>' + brands.map(brand => `<option value="${brand}">${brand}</option>`).join('');
        brandSelect.addEventListener('change', () => {
            store.filters.brand = brandSelect.value;
            applyChinaUnder160Filters();
        });
    }

    if (modelInput) {
        modelInput.addEventListener('input', () => {
            store.filters.query = modelInput.value.trim();
            applyChinaUnder160Filters();
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            store.filters.sort = sortSelect.value;
            applyChinaUnder160Filters();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            store.filters = { brand: '', query: '', sort: 'default' };
            if (brandSelect) brandSelect.value = '';
            if (modelInput) modelInput.value = '';
            if (sortSelect) sortSelect.value = 'default';
            applyChinaUnder160Filters();
        });
    }
}

function applyChinaUnder160Filters(){
    const store = state.chinaUnder160;
    if (!store) return;

    const { brand, query, sort } = store.filters;
    let result = [...store.data];

    if (brand) {
        result = result.filter(car => car.brand === brand);
    }

    if (query) {
        const q = query.toLowerCase();
        result = result.filter(car => {
            const text = `${car.name} ${car.model || ''}`.toLowerCase();
            return text.includes(q);
        });
    }

    switch (sort) {
        case 'price-asc':
            result.sort((a, b) => {
                const priceA = getUnder160PriceValue(a);
                const priceB = getUnder160PriceValue(b);
                return (priceA ?? Infinity) - (priceB ?? Infinity);
            });
            break;
        case 'price-desc':
            result.sort((a, b) => {
                const priceA = getUnder160PriceValue(a);
                const priceB = getUnder160PriceValue(b);
                return (priceB ?? -Infinity) - (priceA ?? -Infinity);
            });
            break;
        case 'name-asc':
            result.sort((a, b) => (a.name || '').localeCompare(b.name || '', 'ru'));
            break;
        case 'name-desc':
            result.sort((a, b) => (b.name || '').localeCompare(a.name || '', 'ru'));
            break;
        default:
            result.sort((a, b) => (a._order ?? 0) - (b._order ?? 0));
    }

    store.filtered = result;
    renderChinaUnder160Cars();
    updateChinaUnder160Counters();
}

function updateChinaUnder160Counters(){
    const metrics = document.getElementById('chinaMetrics');
    if (!metrics) return;

    const list = state.chinaUnder160 ? state.chinaUnder160.filtered : chinaCars;

    metrics.querySelector('[data-metric="count"]').textContent = numberFormatter.format(list.length);

    const prices = list
        .map(getUnder160PriceValue)
        .filter(value => typeof value === 'number' && value > 0)
        .sort((a, b) => a - b);

    const avg = prices.length ? Math.round(prices.reduce((sum, value) => sum + value, 0) / prices.length) : null;
    const min = prices.length ? prices[0] : null;

    metrics.querySelector('[data-metric="avg"]').textContent = avg ? formatCurrency(avg) : '—';
    metrics.querySelector('[data-metric="min"]').textContent = min ? formatCurrency(min) : '—';
}

// Алиас для совместимости с updateAllDisplayedPrices
function updateChinaMetrics() {
    updateChinaUnder160Counters();
    // Также перерисовываем карточки, чтобы обновить цены
    if (document.getElementById('chinaUnder160Grid')) {
        renderChinaUnder160Cars();
    }
}

function setupKoreaUnder160Section(){
    const grid = document.getElementById('koreaUnder160Grid');
    if (!grid) return;
    
    // Обновляем данные из window.koreaUnder160CarsData если они загружены
    let dataSource = [];
    if (Array.isArray(window.koreaUnder160CarsData) && window.koreaUnder160CarsData.length) {
        dataSource = window.koreaUnder160CarsData;
    } else if (typeof koreaUnder160Cars !== 'undefined' && Array.isArray(koreaUnder160Cars) && koreaUnder160Cars.length) {
        dataSource = koreaUnder160Cars;
    } else {
        // Если данных нет, показываем сообщение
        grid.innerHTML = '<div class="usa-empty-state">Нет доступных предложений</div>';
        updateKoreaUnder160Counters();
        return;
    }

    if (!state.koreaUnder160 || state.koreaUnder160.data.length !== dataSource.length) {
        state.koreaUnder160 = {
            data: dataSource.map((car, index) => ({
                ...car,
                price: getUnder160PriceValue(car),
                _order: index
            })),
            filtered: [],
            filters: { brand: '', query: '', sort: 'default' },
            initialized: false
        };
    }

    if (!state.koreaUnder160.initialized) {
        populateKoreaUnder160Filters();
        state.koreaUnder160.initialized = true;
    }

    if (grid) {
        applyKoreaUnder160Filters();
    } else {
        state.koreaUnder160.filtered = [...state.koreaUnder160.data];
        updateKoreaUnder160Counters();
    }
}

function populateKoreaUnder160Filters(){
    const store = state.koreaUnder160;
    if (!store) return;

    const brandSelect = document.getElementById('koreaBrandFilter');
    const modelInput = document.getElementById('koreaModelSearch');
    const sortSelect = document.getElementById('koreaSort');
    const resetBtn = document.getElementById('koreaResetFilters');

    if (brandSelect) {
        const brands = [...new Set(store.data.map(car => car.brand).filter(Boolean))]
            .sort((a, b) => a.localeCompare(b, 'ru'));
        brandSelect.innerHTML = '<option value="">Все марки</option>' + brands.map(brand => `<option value="${brand}">${brand}</option>`).join('');
        brandSelect.addEventListener('change', () => {
            store.filters.brand = brandSelect.value;
            applyKoreaUnder160Filters();
        });
    }

    if (modelInput) {
        modelInput.addEventListener('input', () => {
            store.filters.query = modelInput.value.trim();
            applyKoreaUnder160Filters();
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            store.filters.sort = sortSelect.value;
            applyKoreaUnder160Filters();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            store.filters = { brand: '', query: '', sort: 'default' };
            if (brandSelect) brandSelect.value = '';
            if (modelInput) modelInput.value = '';
            if (sortSelect) sortSelect.value = 'default';
            applyKoreaUnder160Filters();
        });
    }
}

function applyKoreaUnder160Filters(){
    const store = state.koreaUnder160;
    if (!store) return;

    const { brand, query, sort } = store.filters;
    let result = [...store.data];

    if (brand) {
        result = result.filter(car => car.brand === brand);
    }

    if (query) {
        const q = query.toLowerCase();
        result = result.filter(car => {
            const text = `${car.name} ${car.model || ''}`.toLowerCase();
            return text.includes(q);
        });
    }

    switch (sort) {
        case 'price-asc':
            result.sort((a, b) => {
                const priceA = getUnder160PriceValue(a);
                const priceB = getUnder160PriceValue(b);
                return (priceA ?? Infinity) - (priceB ?? Infinity);
            });
            break;
        case 'price-desc':
            result.sort((a, b) => {
                const priceA = getUnder160PriceValue(a);
                const priceB = getUnder160PriceValue(b);
                return (priceB ?? -Infinity) - (priceA ?? -Infinity);
            });
            break;
        case 'name-asc':
            result.sort((a, b) => (a.name || '').localeCompare(b.name || '', 'ru'));
            break;
        case 'name-desc':
            result.sort((a, b) => (b.name || '').localeCompare(a.name || '', 'ru'));
            break;
        default:
            result.sort((a, b) => (a._order ?? 0) - (b._order ?? 0));
    }

    store.filtered = result;
    renderKoreaUnder160Cars();
    updateKoreaUnder160Counters();
}

function updateKoreaUnder160Counters(){
    const metrics = document.getElementById('koreaUnder160Metrics');
    if (!metrics) return;

    const list = state.koreaUnder160 ? state.koreaUnder160.filtered : koreaUnder160Cars;

    metrics.querySelector('[data-metric="count"]').textContent = numberFormatter.format(list.length);

    const prices = list
        .map(getUnder160PriceValue)
        .filter(value => typeof value === 'number' && value > 0)
        .sort((a, b) => a - b);

    const avg = prices.length ? Math.round(prices.reduce((sum, value) => sum + value, 0) / prices.length) : null;
    const min = prices.length ? prices[0] : null;

    metrics.querySelector('[data-metric="avg"]').textContent = avg ? formatCurrency(avg) : '—';
    metrics.querySelector('[data-metric="min"]').textContent = min ? formatCurrency(min) : '—';
}

function renderKoreaUnder160Cars(){
    const grid = document.getElementById('koreaUnder160Grid');
    if (!grid) return;

    const list = state.koreaUnder160 ? state.koreaUnder160.filtered : koreaUnder160Cars;

    // Скрываем индикатор загрузки
    const loadingIndicator = document.getElementById('koreaLoadingIndicator');
    if (loadingIndicator) loadingIndicator.style.display = 'none';

    if (!list.length){
        grid.innerHTML = '<div class="usa-empty-state">Нет подготовленных предложений по льготному утильсбору</div>';
        return;
    }

    // Оптимизация: используем DocumentFragment для батчинга
    const fragment = document.createDocumentFragment();
    
    // Preload первых 3 изображений для быстрой загрузки
    const preloadImages = [];
    
    list.forEach((car, index)=>{
        const specs = buildUnder160CarSpecs(car);
        // Конвертируем цену из рублей в доллары если нужно
        let priceValue = getUnder160PriceValue(car);
        
        // Обрабатываем priceLabel: если он содержит рубли, конвертируем в доллары
        let priceLabel = car.priceLabel;
        if (priceLabel && priceLabel.includes('₽')) {
            // Извлекаем число из priceLabel (убираем пробелы и ₽)
            const priceMatch = priceLabel.match(/[\d\s]+/);
            if (priceMatch) {
                const priceNum = parseInt(priceMatch[0].replace(/\s/g, ''), 10);
                if (priceNum && priceNum > 10000 && usdToRubRate) {
                    const usdPrice = convertRubToUsd(priceNum);
                    priceLabel = formatCurrency(usdPrice);
                }
            }
        } else if (!priceLabel) {
            priceLabel = priceValue ? formatCurrency(priceValue) : 'Цена по запросу';
        }
        const brandBadge = car.brand ? `<span class="orders-card-brand">${car.brand}</span>` : '';
        const utilBadge = '<span class="util-badge">льготный утильсбор</span>';
        const descriptionHtml = car.description ? `<p class="orders-card-desc">${utilBadge} ${car.description}</p>` : `<p class="orders-card-desc">${utilBadge}</p>`;

        // Нормализуем путь к изображению (исправляем регистр)
        let imageSrc = car.image || '';
        if (imageSrc && imageSrc.includes('images/korea/')) {
            imageSrc = imageSrc.replace('images/korea/', 'images/Korea/');
        }
        imageSrc = imageSrc || buildSvgPlaceholder(`${car.brand || ''} ${car.model || car.name || ''}`.trim() || car.name);

        const card = document.createElement('article');
        card.className = 'orders-card korea-card';
        card.innerHTML = `
            <img src="${imageSrc}" alt="${car.name}" loading="lazy" decoding="async">
            <div class="orders-card-body">
                ${brandBadge}
                <h4>${car.name}</h4>
                ${descriptionHtml}
                <ul class="usa-preferential-meta">
                    ${specs.map(item => `<li>${item}</li>`).join('')}
                </ul>
                <div class="usa-preferential-price">${priceLabel}</div>
                <div class="usa-order-actions" style="margin-top:0.5rem;">
                    <button class="btn-primary" type="button">Запросить расчет</button>
                </div>
            </div>
        `;

        const btn = card.querySelector('.btn-primary');
        if (btn) {
            btn.addEventListener('click', ()=>{
                openRequestModal();
                prefillKoreaRequest(car);
            });
        }

        const img = card.querySelector('img');
        if (img) {
            // Preload первых 3 изображений
            if (index < 3 && img.src && !img.src.startsWith('data:')) {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.as = 'image';
                link.href = img.src;
                document.head.appendChild(link);
                preloadImages.push(link);
            }
            attachImageFallback(img, car);
        }

        fragment.appendChild(card);
    });
    
    grid.innerHTML = '';
    grid.appendChild(fragment);
}
