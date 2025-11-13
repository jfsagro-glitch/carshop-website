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
    koreaUnder160: null
};

const numberFormatter = new Intl.NumberFormat('ru-RU');
const formatCurrency = (value) => `${numberFormatter.format(Math.round(value))} ₽`;

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
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    loadCars();
    populateBrandFilter();
    updateCartCount();
    setupEventListeners();
    loadUsaOrdersSection();
    loadChinaOrdersSection();
    loadKoreaOrdersSection();
    // Обработчики свайпа для всех галерей (делегирование)
    document.addEventListener('touchstart', onTouchStart, { passive: true });
    document.addEventListener('touchmove', onTouchMove, { passive: true });
    document.addEventListener('touchend', onTouchEnd, { passive: true });
}

function buildSvgPlaceholder(title) {
    const safeTitle = (title || 'CarExport').replace(/[<>&]/g, char => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[char]));
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
    const fallbackTitle = (car && (car.name || `${car.brand || ''} ${car.model || ''}`.trim())) || 'CarExport';
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
            "Мощность, л.с.: 1 10",
            "Макс. скорость, км/ч: 182",
            "Привод: Передний",
            "Объем двигателя: 1498",
            "Трансмиссия: Автомат"
        ],
        "engineType": "Бензин",
        "power": "1 10 л.с.",
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

const koreaUnder160Cars = [
    {
        "id": "40940918",
        "name": "Audi Q3 F3 35 TDI",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI",
        "image": "images/korea/catalog/audi-40940918.jpg",
        "priceFrom": 3995062,
        "priceLabel": "3 995 062 ₽",
        "link": "https://pan-auto.ru/details/40940918",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 49 873 км",
            "Дата выпуска: Февраль, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 313 175 ₽ через 3 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40940750",
        "name": "Audi Q3 F3 35 TDI Quattro Premium",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI Quattro Premium",
        "image": "images/korea/catalog/audi-40940750.jpg",
        "priceFrom": 4314202,
        "priceLabel": "4 314 202 ₽",
        "link": "https://pan-auto.ru/details/40940750",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 29 515 км",
            "Дата выпуска: Октябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40918191",
        "name": "Audi Q3 F3 35 TDI Premium",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI Premium",
        "image": "images/korea/catalog/audi-40918191.jpg",
        "priceFrom": 3554307,
        "priceLabel": "3 554 307 ₽",
        "link": "https://pan-auto.ru/details/40918191",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 66 062 км",
            "Дата выпуска: Январь, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 012 549 ₽ через 2 месяца"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40924805",
        "name": "Audi Q3 F3 35 TDI Premium Sportback",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI Premium Sportback",
        "image": "images/korea/catalog/audi-40924805.jpg",
        "priceFrom": 4855432,
        "priceLabel": "4 855 432 ₽",
        "link": "https://pan-auto.ru/details/40924805",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 22 260 км",
            "Дата выпуска: Декабрь, 2022 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 901 526 ₽ через 1 месяц"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40908480",
        "name": "Audi Q3 F3 35 TDI Quattro Premium",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI Quattro Premium",
        "image": "images/korea/catalog/audi-40908480.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40908480",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 19 171 км",
            "Дата выпуска: Август, 2023 год"
        ],
        "description": "Высокая ставка · Дилерский"
    },
    {
        "id": "40823466",
        "name": "Audi Q3 F3 35 TDI Quattro Premium Sportback",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI Quattro Premium Sportback",
        "image": "images/korea/catalog/audi-40823466.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40823466",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 53 063 км",
            "Дата выпуска: Июнь, 2023 год"
        ]
    },
    {
        "id": "40816680",
        "name": "Audi Q2 GA 35 TDI Premium",
        "brand": "Audi",
        "model": "Q2 GA 35 TDI Premium",
        "image": "images/korea/catalog/audi-40816680.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40816680",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 88 912 км",
            "Дата выпуска: Февраль, 2023 год"
        ],
        "description": "Дилерский"
    },
    {
        "id": "40813560",
        "name": "Audi Q2 GA 35 TDI Premium",
        "brand": "Audi",
        "model": "Q2 GA 35 TDI Premium",
        "image": "images/korea/catalog/audi-40813560.jpg",
        "priceFrom": 3055442,
        "priceLabel": "3 055 442 ₽",
        "link": "https://pan-auto.ru/details/40813560",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 8 719 км",
            "Дата выпуска: Июнь, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 540 943 ₽ через 7 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40802153",
        "name": "Audi Q3 F3 35 TDI",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI",
        "image": "images/korea/catalog/audi-40802153.jpg",
        "priceFrom": 2812104,
        "priceLabel": "2 812 104 ₽",
        "link": "https://pan-auto.ru/details/40802153",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 63 748 км",
            "Дата выпуска: Октябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40757312",
        "name": "Audi Q3 F3 35 TDI Quattro Premium Sportback",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI Quattro Premium Sportback",
        "image": "images/korea/catalog/audi-40757312.jpg",
        "priceFrom": 3822143,
        "priceLabel": "3 822 143 ₽",
        "link": "https://pan-auto.ru/details/40757312",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 67 358 км",
            "Дата выпуска: Сентябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40503465",
        "name": "Audi Q3 F3 35 TDI Premium",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI Premium",
        "image": "images/korea/catalog/audi-40503465.jpg",
        "priceFrom": 3865342,
        "priceLabel": "3 865 342 ₽",
        "link": "https://pan-auto.ru/details/40503465",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 23 712 км",
            "Дата выпуска: Июль, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40478734",
        "name": "Audi Q3 F3 35 TDI Premium Sportback",
        "brand": "Audi",
        "model": "Q3 F3 35 TDI Premium Sportback",
        "image": "images/korea/catalog/audi-40478734.jpg",
        "priceFrom": 4171786,
        "priceLabel": "4 171 786 ₽",
        "link": "https://pan-auto.ru/details/40478734",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 25 552 км",
            "Дата выпуска: Сентябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40763638",
        "name": "BMW 1-я серия F40 118d Joy",
        "brand": "BMW",
        "model": "1-я серия F40 118d Joy",
        "image": "images/korea/catalog/bmw-40763638.jpg",
        "priceFrom": 2111526,
        "priceLabel": "2 111 526 ₽",
        "link": "https://pan-auto.ru/details/40763638",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 59 916 км",
            "Дата выпуска: Март, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 504 062 ₽ через 2 месяца"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40741655",
        "name": "BMW 1-я серия F40 118d M Sport",
        "brand": "BMW",
        "model": "1-я серия F40 118d M Sport",
        "image": "images/korea/catalog/bmw-40741655.jpg",
        "priceFrom": 2530095,
        "priceLabel": "2 530 095 ₽",
        "link": "https://pan-auto.ru/details/40741655",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 26 494 км",
            "Дата выпуска: Февраль, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 922 631 ₽ через 1 месяц"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40710232",
        "name": "BMW 2-я серия Active Tourer (U06) 218d Luxury",
        "brand": "BMW",
        "model": "2-я серия Active Tourer (U06) 218d Luxury",
        "image": "images/korea/catalog/bmw-40710232.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40710232",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 23 035 км",
            "Дата выпуска: Ноябрь, 2022 год"
        ],
        "description": "Проходной · Дилерский"
    },
    {
        "id": "40701956",
        "name": "BMW 2-я серия Active Tourer (U06) 218d Advantage",
        "brand": "BMW",
        "model": "2-я серия Active Tourer (U06) 218d Advantage",
        "image": "images/korea/catalog/bmw-40701956.jpg",
        "priceFrom": 3263908,
        "priceLabel": "3 263 908 ₽",
        "link": "https://pan-auto.ru/details/40701956",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 14 726 км",
            "Дата выпуска: Март, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 742 326 ₽ через 4 месяца"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40692702",
        "name": "BMW 1-я серия F40 118d M Sport",
        "brand": "BMW",
        "model": "1-я серия F40 118d M Sport",
        "image": "images/korea/catalog/bmw-40692702.jpg",
        "priceFrom": 1891818,
        "priceLabel": "1 891 818 ₽",
        "link": "https://pan-auto.ru/details/40692702",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 124 380 км",
            "Дата выпуска: Июль, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 284 354 ₽ через 6 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40667035",
        "name": "BMW 1-я серия F40 118d Sport",
        "brand": "BMW",
        "model": "1-я серия F40 118d Sport",
        "image": "images/korea/catalog/bmw-40667035.jpg",
        "priceFrom": 2319712,
        "priceLabel": "2 319 712 ₽",
        "link": "https://pan-auto.ru/details/40667035",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 81 819 км",
            "Дата выпуска: Январь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 319 712 ₽ через 0 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40633439",
        "name": "BMW 2-я серия Gran Coupe (F44) 218d M Sport",
        "brand": "BMW",
        "model": "2-я серия Gran Coupe (F44) 218d M Sport",
        "image": "images/korea/catalog/bmw-40633439.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40633439",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 94 693 км",
            "Дата выпуска: Июнь, 2021 год"
        ],
        "description": "Проходной · Дилерский"
    },
    {
        "id": "40649520",
        "name": "BMW 2-я серия Active Tourer (U06) 218d Advantage",
        "brand": "BMW",
        "model": "2-я серия Active Tourer (U06) 218d Advantage",
        "image": "images/korea/catalog/bmw-40649520.jpg",
        "priceFrom": 3163644,
        "priceLabel": "3 163 644 ₽",
        "link": "https://pan-auto.ru/details/40649520",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 31 500 км",
            "Дата выпуска: Март, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 642 062 ₽ через 4 месяца"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40639677",
        "name": "BMW 2-я серия Gran Coupe (F44) 218d M Sport",
        "brand": "BMW",
        "model": "2-я серия Gran Coupe (F44) 218d M Sport",
        "image": "images/korea/catalog/bmw-40639677.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40639677",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 106 790 км",
            "Дата выпуска: Январь, 2021 год"
        ],
        "description": "Проходной · Лизинговый"
    },
    {
        "id": "40450041",
        "name": "BMW 2-я серия Active Tourer (U06) 218d M Sport First Edition",
        "brand": "BMW",
        "model": "2-я серия Active Tourer (U06) 218d M Sport First Edition",
        "image": "images/korea/catalog/bmw-40450041.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40450041",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 23 045 км",
            "Дата выпуска: Декабрь, 2022 год"
        ],
        "description": "Лизинговый"
    },
    {
        "id": "40433105",
        "name": "BMW 1-я серия F40 118d M Sport",
        "brand": "BMW",
        "model": "1-я серия F40 118d M Sport",
        "image": "images/korea/catalog/bmw-40433105.jpg",
        "priceFrom": 2663256,
        "priceLabel": "2 663 256 ₽",
        "link": "https://pan-auto.ru/details/40433105",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 56 928 км",
            "Дата выпуска: Январь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 663 256 ₽ через 0 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40390583",
        "name": "BMW 2-я серия Gran Coupe (F44) 218d M Sport",
        "brand": "BMW",
        "model": "2-я серия Gran Coupe (F44) 218d M Sport",
        "image": "images/korea/catalog/bmw-40390583.jpg",
        "priceFrom": 2606704,
        "priceLabel": "2 606 704 ₽",
        "link": "https://pan-auto.ru/details/40390583",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 12 111 км",
            "Дата выпуска: Февраль, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 999 240 ₽ через 1 месяц"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40223019",
        "name": "BMW X1 U11 sDrive 18d M Sport",
        "brand": "BMW",
        "model": "X1 U11 sDrive 18d M Sport",
        "image": "images/korea/catalog/bmw-40223019.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40223019",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 995 см³",
            "Пробег: 37 462 км",
            "Дата выпуска: Декабрь, 2023 год"
        ],
        "description": "Высокая ставка · Лизинговый"
    },
    {
        "id": "40957966",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40957966.jpg",
        "priceFrom": 3102284,
        "priceLabel": "3 102 284 ₽",
        "link": "https://pan-auto.ru/details/40957966",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 28 532 км",
            "Дата выпуска: Октябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 485 966 ₽ через 9 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40930728",
        "name": "Mercedes-Benz A-Class W177 A200d Sedan",
        "brand": "Mercedes-Benz",
        "model": "A-Class W177 A200d Sedan",
        "image": "images/korea/catalog/mercedes-benz-40930728.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40930728",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 20 051 км",
            "Дата выпуска: Сентябрь, 2022 год"
        ],
        "description": "Проходной"
    },
    {
        "id": "40921473",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40921473.jpg",
        "priceFrom": 2778086,
        "priceLabel": "2 778 086 ₽",
        "link": "https://pan-auto.ru/details/40921473",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 70 237 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 161 768 ₽ через 8 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40898874",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40898874.jpg",
        "priceFrom": 3778943,
        "priceLabel": "3 778 943 ₽",
        "link": "https://pan-auto.ru/details/40898874",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 51 099 км",
            "Дата выпуска: Апрель, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 161 214 ₽ через 5 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40897846",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40897846.jpg",
        "priceFrom": 3125856,
        "priceLabel": "3 125 856 ₽",
        "link": "https://pan-auto.ru/details/40897846",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 59 797 км",
            "Дата выпуска: Октябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40898429",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40898429.jpg",
        "priceFrom": 2860588,
        "priceLabel": "2 860 588 ₽",
        "link": "https://pan-auto.ru/details/40898429",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 98 281 км",
            "Дата выпуска: Ноябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40828801",
        "name": "Mercedes-Benz A-Class W177 A200d Sedan",
        "brand": "Mercedes-Benz",
        "model": "A-Class W177 A200d Sedan",
        "image": "images/korea/catalog/mercedes-benz-40828801.jpg",
        "priceFrom": 2601767,
        "priceLabel": "2 601 767 ₽",
        "link": "https://pan-auto.ru/details/40828801",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 61 878 км",
            "Дата выпуска: Январь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 601 767 ₽ через 0 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40780032",
        "name": "Mercedes-Benz A-Class W177 A200d Sedan",
        "brand": "Mercedes-Benz",
        "model": "A-Class W177 A200d Sedan",
        "image": "images/korea/catalog/mercedes-benz-40780032.jpg",
        "priceFrom": 2159072,
        "priceLabel": "2 159 072 ₽",
        "link": "https://pan-auto.ru/details/40780032",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 43 405 км",
            "Дата выпуска: Июль, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 542 754 ₽ через 6 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40791541",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40791541.jpg",
        "priceFrom": 2536390,
        "priceLabel": "2 536 390 ₽",
        "link": "https://pan-auto.ru/details/40791541",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 106 208 км",
            "Дата выпуска: Октябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 920 072 ₽ через 9 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40758656",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40758656.jpg",
        "priceFrom": 2748621,
        "priceLabel": "2 748 621 ₽",
        "link": "https://pan-auto.ru/details/40758656",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 71 720 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 132 303 ₽ через 8 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40757875",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40757875.jpg",
        "priceFrom": 2819337,
        "priceLabel": "2 819 337 ₽",
        "link": "https://pan-auto.ru/details/40757875",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 91 692 км",
            "Дата выпуска: Август, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40722612",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40722612.jpg",
        "priceFrom": 2660143,
        "priceLabel": "2 660 143 ₽",
        "link": "https://pan-auto.ru/details/40722612",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 98 677 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 043 825 ₽ через 8 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40697156",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40697156.jpg",
        "priceFrom": 2807551,
        "priceLabel": "2 807 551 ₽",
        "link": "https://pan-auto.ru/details/40697156",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 80 457 км",
            "Дата выпуска: Июль, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40693847",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40693847.jpg",
        "priceFrom": 2825230,
        "priceLabel": "2 825 230 ₽",
        "link": "https://pan-auto.ru/details/40693847",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 70 809 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 3 208 912 ₽ через 8 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40647266",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40647266.jpg",
        "priceFrom": 2748621,
        "priceLabel": "2 748 621 ₽",
        "link": "https://pan-auto.ru/details/40647266",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 92 410 км",
            "Дата выпуска: Ноябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40628221",
        "name": "Mercedes-Benz GLB-Class X247 GLB200 d",
        "brand": "Mercedes-Benz",
        "model": "GLB-Class X247 GLB200 d",
        "image": "images/korea/catalog/mercedes-benz-40628221.jpg",
        "priceFrom": 2819337,
        "priceLabel": "2 819 337 ₽",
        "link": "https://pan-auto.ru/details/40628221",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 81 217 км",
            "Дата выпуска: Октябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40532180",
        "name": "Mercedes-Benz A-Class W177 A200d Sedan",
        "brand": "Mercedes-Benz",
        "model": "A-Class W177 A200d Sedan",
        "image": "images/korea/catalog/mercedes-benz-40532180.jpg",
        "priceFrom": 2365410,
        "priceLabel": "2 365 410 ₽",
        "link": "https://pan-auto.ru/details/40532180",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 21 887 км",
            "Дата выпуска: Май, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40491286",
        "name": "Mercedes-Benz A-Class W177 A200d Sedan",
        "brand": "Mercedes-Benz",
        "model": "A-Class W177 A200d Sedan",
        "image": "images/korea/catalog/mercedes-benz-40491286.jpg",
        "priceFrom": 2247550,
        "priceLabel": "2 247 550 ₽",
        "link": "https://pan-auto.ru/details/40491286",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 64 734 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 631 232 ₽ через 8 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "39790187",
        "name": "Mercedes-Benz A-Class W177 A200d Sedan",
        "brand": "Mercedes-Benz",
        "model": "A-Class W177 A200d Sedan",
        "image": "images/korea/catalog/mercedes-benz-39790187.jpg",
        "priceFrom": 2300587,
        "priceLabel": "2 300 587 ₽",
        "link": "https://pan-auto.ru/details/39790187",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 950 см³",
            "Пробег: 24 400 км",
            "Дата выпуска: Октябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40955537",
        "name": "Volkswagen Tiguan 2-е поколение 2.0 TDI 4Motion Prestige",
        "brand": "Volkswagen",
        "model": "Tiguan 2-е поколение 2.0 TDI 4Motion Prestige",
        "image": "images/korea/catalog/volkswagen-40955537.jpg",
        "priceFrom": 3307282,
        "priceLabel": "3 307 282 ₽",
        "link": "https://pan-auto.ru/details/40955537",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 94 697 км",
            "Дата выпуска: Октябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40940977",
        "name": "Volkswagen Golf 8-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Golf 8-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40940977.jpg",
        "priceFrom": 3120265,
        "priceLabel": "3 120 265 ₽",
        "link": "https://pan-auto.ru/details/40940977",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 34 410 км",
            "Дата выпуска: Февраль, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 605 766 ₽ через 3 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "36566591",
        "name": "Volkswagen Golf 8-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Golf 8-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-36566591.jpg",
        "priceFrom": 2010407,
        "priceLabel": "2 010 407 ₽",
        "link": "https://pan-auto.ru/details/36566591",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 19 900 км",
            "Дата выпуска: Апрель, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40945707",
        "name": "Volkswagen Golf 8-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Golf 8-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40945707.jpg",
        "priceFrom": 2517371,
        "priceLabel": "2 517 371 ₽",
        "link": "https://pan-auto.ru/details/40945707",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 43 368 км",
            "Дата выпуска: Февраль, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40939300",
        "name": "Volkswagen Tiguan 2-е поколение 2.0 TDI 4Motion Prestige",
        "brand": "Volkswagen",
        "model": "Tiguan 2-е поколение 2.0 TDI 4Motion Prestige",
        "image": "images/korea/catalog/volkswagen-40939300.jpg",
        "priceFrom": 3600900,
        "priceLabel": "3 600 900 ₽",
        "link": "https://pan-auto.ru/details/40939300",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 68 467 км",
            "Дата выпуска: Февраль, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40953666",
        "name": "Volkswagen T-Roc 2.0 TDI Premium",
        "brand": "Volkswagen",
        "model": "T-Roc 2.0 TDI Premium",
        "image": "images/korea/catalog/volkswagen-40953666.jpg",
        "priceFrom": 2251522,
        "priceLabel": "2 251 522 ₽",
        "link": "https://pan-auto.ru/details/40953666",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 48 402 км",
            "Дата выпуска: Июнь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 638 709 ₽ через 5 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40947910",
        "name": "Volkswagen Tiguan 2-е поколение 2.0 TDI Premium",
        "brand": "Volkswagen",
        "model": "Tiguan 2-е поколение 2.0 TDI Premium",
        "image": "images/korea/catalog/volkswagen-40947910.jpg",
        "priceFrom": 3238208,
        "priceLabel": "3 238 208 ₽",
        "link": "https://pan-auto.ru/details/40947910",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 51 439 км",
            "Дата выпуска: Декабрь, 2022 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 723 709 ₽ через 1 месяц"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40947519",
        "name": "Volkswagen T-Roc 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "T-Roc 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40947519.jpg",
        "priceFrom": 2057551,
        "priceLabel": "2 057 551 ₽",
        "link": "https://pan-auto.ru/details/40947519",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 109 061 км",
            "Дата выпуска: Ноябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 444 738 ₽ через 10 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40952614",
        "name": "Volkswagen T-Roc 2.0 TDI Premium",
        "brand": "Volkswagen",
        "model": "T-Roc 2.0 TDI Premium",
        "image": "images/korea/catalog/volkswagen-40952614.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40952614",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 19 663 км",
            "Дата выпуска: Апрель, 2021 год"
        ],
        "description": "Добавлен сегодня · Проходной · Дилерский"
    },
    {
        "id": "40933151",
        "name": "Volkswagen Golf 8-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Golf 8-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40933151.jpg",
        "priceFrom": 2587506,
        "priceLabel": "2 587 506 ₽",
        "link": "https://pan-auto.ru/details/40933151",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 24 417 км",
            "Дата выпуска: Январь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40932626",
        "name": "Volkswagen Tiguan 2-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Tiguan 2-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40932626.jpg",
        "priceFrom": 4604754,
        "priceLabel": "4 604 754 ₽",
        "link": "https://pan-auto.ru/details/40932626",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 16 037 км",
            "Дата выпуска: Ноябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40946516",
        "name": "Volkswagen T-Roc 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "T-Roc 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40946516.jpg",
        "priceFrom": 2075230,
        "priceLabel": "2 075 230 ₽",
        "link": "https://pan-auto.ru/details/40946516",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 37 166 км",
            "Дата выпуска: Апрель, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 462 417 ₽ через 3 месяца"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40941766",
        "name": "Volkswagen Tiguan 2-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Tiguan 2-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40941766.jpg",
        "priceFrom": 3291245,
        "priceLabel": "3 291 245 ₽",
        "link": "https://pan-auto.ru/details/40941766",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 137 773 км",
            "Дата выпуска: Декабрь, 2022 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 776 746 ₽ через 1 месяц"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40937444",
        "name": "Volkswagen Jetta 7-е поколение 1.5 TSI Prestige",
        "brand": "Volkswagen",
        "model": "Jetta 7-е поколение 1.5 TSI Prestige",
        "image": "images/korea/catalog/volkswagen-40937444.jpg",
        "priceFrom": 2819673,
        "priceLabel": "2 819 673 ₽",
        "link": "https://pan-auto.ru/details/40937444",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 495 см³",
            "Пробег: 31 210 км",
            "Дата выпуска: Декабрь, 2022 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 251 746 ₽ через 1 месяц"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40937684",
        "name": "Volkswagen Golf 8-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Golf 8-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40937684.jpg",
        "priceFrom": 2599873,
        "priceLabel": "2 599 873 ₽",
        "link": "https://pan-auto.ru/details/40937684",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 30 562 км",
            "Дата выпуска: Февраль, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40930859",
        "name": "Volkswagen Golf 8-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Golf 8-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40930859.jpg",
        "priceFrom": 3055442,
        "priceLabel": "3 055 442 ₽",
        "link": "https://pan-auto.ru/details/40930859",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 37 835 км",
            "Дата выпуска: Ноябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40915879",
        "name": "Volkswagen Tiguan 2-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Tiguan 2-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40915879.jpg",
        "priceFrom": 3367854,
        "priceLabel": "3 367 854 ₽",
        "link": "https://pan-auto.ru/details/40915879",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 96 646 км",
            "Дата выпуска: Май, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 853 355 ₽ через 6 месяцев"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40916828",
        "name": "Volkswagen Tiguan 2-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Tiguan 2-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40916828.jpg",
        "priceFrom": 3571435,
        "priceLabel": "3 571 435 ₽",
        "link": "https://pan-auto.ru/details/40916828",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 29 933 км",
            "Дата выпуска: Июль, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40933447",
        "name": "Volkswagen Jetta 7-е поколение 1.4 TSI Prestige",
        "brand": "Volkswagen",
        "model": "Jetta 7-е поколение 1.4 TSI Prestige",
        "image": "images/korea/catalog/volkswagen-40933447.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40933447",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 395 см³",
            "Пробег: 45 629 км",
            "Дата выпуска: Апрель, 2021 год"
        ],
        "description": "Проходной"
    },
    {
        "id": "40922395",
        "name": "Volkswagen Tiguan 2-е поколение 2.0 TDI Prestige",
        "brand": "Volkswagen",
        "model": "Tiguan 2-е поколение 2.0 TDI Prestige",
        "image": "images/korea/catalog/volkswagen-40922395.jpg",
        "priceFrom": 3018442,
        "priceLabel": "3 018 442 ₽",
        "link": "https://pan-auto.ru/details/40922395",
        "specs": [
            "Мощность: 150 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 968 см³",
            "Пробег: 38 389 км",
            "Дата выпуска: Август, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40959109",
        "name": "Hyundai Sonata (DN8) 2.0 Modern",
        "brand": "Hyundai",
        "model": "Sonata (DN8) 2.0 Modern",
        "image": "images/korea/catalog/hyundai-40959109.jpg",
        "priceFrom": 1964549,
        "priceLabel": "1 964 549 ₽",
        "link": "https://pan-auto.ru/details/40959109",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 32 658 км",
            "Дата выпуска: Июнь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 357 853 ₽ через 5 месяцев"
        ],
        "description": "Добавлен сегодня · Проходной"
    },
    {
        "id": "40939569",
        "name": "Kia Ray Новый Prestige",
        "brand": "Kia",
        "model": "Ray Новый Prestige",
        "image": "images/korea/catalog/kia-40939569.jpg",
        "priceFrom": 1327028,
        "priceLabel": "1 327 028 ₽",
        "link": "https://pan-auto.ru/details/40939569",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 52 914 км",
            "Дата выпуска: Ноябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40911979",
        "name": "Hyundai Avante (CN7) 1.6 Modern",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Modern",
        "image": "images/korea/catalog/hyundai-40911979.jpg",
        "priceFrom": 1525638,
        "priceLabel": "1 525 638 ₽",
        "link": "https://pan-auto.ru/details/40911979",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 122 000 км",
            "Дата выпуска: Апрель, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 675 363 ₽ через 3 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40957541",
        "name": "Hyundai Avante (CN7) 1.6 Inspiration",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Inspiration",
        "image": "images/korea/catalog/hyundai-40957541.jpg",
        "priceFrom": 1987042,
        "priceLabel": "1 987 042 ₽",
        "link": "https://pan-auto.ru/details/40957541",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 28 927 км",
            "Дата выпуска: Июнь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 136 767 ₽ через 5 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40918871",
        "name": "Hyundai Casper Inspiration",
        "brand": "Hyundai",
        "model": "Casper Inspiration",
        "image": "images/korea/catalog/hyundai-40918871.jpg",
        "priceFrom": 1321135,
        "priceLabel": "1 321 135 ₽",
        "link": "https://pan-auto.ru/details/40918871",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 82 286 км",
            "Дата выпуска: Май, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40945381",
        "name": "Hyundai Avante (CN7) 1.6 Inspiration",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Inspiration",
        "image": "images/korea/catalog/hyundai-40945381.jpg",
        "priceFrom": 1737869,
        "priceLabel": "1 737 869 ₽",
        "link": "https://pan-auto.ru/details/40945381",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 69 393 км",
            "Дата выпуска: Апрель, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 887 594 ₽ через 3 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40958316",
        "name": "Kia Ray Новый Best Picks",
        "brand": "Kia",
        "model": "Ray Новый Best Picks",
        "image": "images/korea/catalog/kia-40958316.jpg",
        "priceFrom": 1191406,
        "priceLabel": "1 191 406 ₽",
        "link": "https://pan-auto.ru/details/40958316",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 40 111 км",
            "Дата выпуска: Апрель, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40940117",
        "name": "Hyundai Avante (CN7) 1.6 Smart",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Smart",
        "image": "images/korea/catalog/hyundai-40940117.jpg",
        "priceFrom": 1384206,
        "priceLabel": "1 384 206 ₽",
        "link": "https://pan-auto.ru/details/40940117",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 142 321 км",
            "Дата выпуска: Июль, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 533 931 ₽ через 6 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40959004",
        "name": "Kia Morning Urban (JA) Standard",
        "brand": "Kia",
        "model": "Morning Urban (JA) Standard",
        "image": "images/korea/catalog/kia-40959004.jpg",
        "priceFrom": 1055784,
        "priceLabel": "1 055 784 ₽",
        "link": "https://pan-auto.ru/details/40959004",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 26 700 км",
            "Дата выпуска: Ноябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40954917",
        "name": "Chevrolet (GM Daewoo) Trailblazer 1.3 турбо 2WD Premier",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Trailblazer 1.3 турбо 2WD Premier",
        "image": "images/korea/catalog/chevrolet-40954917.jpg",
        "priceFrom": 1726145,
        "priceLabel": "1 726 145 ₽",
        "link": "https://pan-auto.ru/details/40954917",
        "specs": [
            "Мощность: 155 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 341 см³",
            "Пробег: 25 480 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 914 595 ₽ через 8 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40958299",
        "name": "Hyundai Casper турбо Inspiration",
        "brand": "Hyundai",
        "model": "Casper турбо Inspiration",
        "image": "images/korea/catalog/hyundai-40958299.jpg",
        "priceFrom": 1844164,
        "priceLabel": "1 844 164 ₽",
        "link": "https://pan-auto.ru/details/40958299",
        "specs": [
            "Мощность: 100 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 23 414 км",
            "Дата выпуска: Март, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 486 139 ₽ через 4 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40939949",
        "name": "Kia K3 Новый 2-го поколения 1.6 Signature",
        "brand": "Kia",
        "model": "K3 Новый 2-го поколения 1.6 Signature",
        "image": "images/korea/catalog/kia-40939949.jpg",
        "priceFrom": 2128239,
        "priceLabel": "2 128 239 ₽",
        "link": "https://pan-auto.ru/details/40939949",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 50 555 км",
            "Дата выпуска: Сентябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40958817",
        "name": "Kia Morning Urban (JA) Signature",
        "brand": "Kia",
        "model": "Morning Urban (JA) Signature",
        "image": "images/korea/catalog/kia-40958817.jpg",
        "priceFrom": 1524367,
        "priceLabel": "1 524 367 ₽",
        "link": "https://pan-auto.ru/details/40958817",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 27 000 км",
            "Дата выпуска: Апрель, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 268 015 ₽ через 5 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40958752",
        "name": "Kia Ray Новый Signature",
        "brand": "Kia",
        "model": "Ray Новый Signature",
        "image": "images/korea/catalog/kia-40958752.jpg",
        "priceFrom": 1338814,
        "priceLabel": "1 338 814 ₽",
        "link": "https://pan-auto.ru/details/40958752",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 6 750 км",
            "Дата выпуска: Август, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40958216",
        "name": "Renault Korea (Samsung) XM3 1.6 RE",
        "brand": "Renault",
        "model": "Korea (Samsung) XM3 1.6 RE",
        "image": "images/korea/catalog/renault-40958216.jpg",
        "priceFrom": 1519745,
        "priceLabel": "1 519 745 ₽",
        "link": "https://pan-auto.ru/details/40958216",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 24 447 км",
            "Дата выпуска: Октябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 669 470 ₽ через 9 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40939831",
        "name": "Hyundai Casper турбо Inspiration",
        "brand": "Hyundai",
        "model": "Casper турбо Inspiration",
        "image": "images/korea/catalog/hyundai-40939831.jpg",
        "priceFrom": 1456674,
        "priceLabel": "1 456 674 ₽",
        "link": "https://pan-auto.ru/details/40939831",
        "specs": [
            "Мощность: 100 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 17 932 км",
            "Дата выпуска: Ноябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40957026",
        "name": "Kia Ray Новый Van 2 места Prestige Special",
        "brand": "Kia",
        "model": "Ray Новый Van 2 места Prestige Special",
        "image": "images/korea/catalog/kia-40957026.jpg",
        "priceFrom": 1303786,
        "priceLabel": "1 303 786 ₽",
        "link": "https://pan-auto.ru/details/40957026",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 20 353 км",
            "Дата выпуска: Август, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40957940",
        "name": "Chevrolet (GM Daewoo) Trax кроссовер 1.2 Active Plus",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Trax кроссовер 1.2 Active Plus",
        "image": "images/korea/catalog/chevrolet-40957940.jpg",
        "priceFrom": 2283757,
        "priceLabel": "2 283 757 ₽",
        "link": "https://pan-auto.ru/details/40957940",
        "specs": [
            "Мощность: 137 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 199 см³",
            "Пробег: 27 630 км",
            "Дата выпуска: Ноябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40940468",
        "name": "Hyundai Avante (CN7) 1.6 Modern",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Modern",
        "image": "images/korea/catalog/hyundai-40940468.jpg",
        "priceFrom": 1785013,
        "priceLabel": "1 785 013 ₽",
        "link": "https://pan-auto.ru/details/40940468",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 27 995 км",
            "Дата выпуска: Апрель, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40958720",
        "name": "Kia K3 Новый 2-го поколения 1.6 Prestige",
        "brand": "Kia",
        "model": "K3 Новый 2-го поколения 1.6 Prestige",
        "image": "images/korea/catalog/kia-40958720.jpg",
        "priceFrom": 2010614,
        "priceLabel": "2 010 614 ₽",
        "link": "https://pan-auto.ru/details/40958720",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 27 697 км",
            "Дата выпуска: Июль, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40958690",
        "name": "Kia K5 3-го поколения 2.0 Prestige",
        "brand": "Kia",
        "model": "K5 3-го поколения 2.0 Prestige",
        "image": "images/korea/catalog/kia-40958690.jpg",
        "priceFrom": 2318876,
        "priceLabel": "2 318 876 ₽",
        "link": "https://pan-auto.ru/details/40958690",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 65 402 км",
            "Дата выпуска: Октябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 712 180 ₽ через 9 месяцев"
        ],
        "description": "Добавлен сегодня · Проходной"
    },
    {
        "id": "40918729",
        "name": "Hyundai Casper Inspiration",
        "brand": "Hyundai",
        "model": "Casper Inspiration",
        "image": "images/korea/catalog/hyundai-40918729.jpg",
        "priceFrom": 1237969,
        "priceLabel": "1 237 969 ₽",
        "link": "https://pan-auto.ru/details/40918729",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 101 656 км",
            "Дата выпуска: Май, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40951662",
        "name": "Chevrolet (GM Daewoo) Trailblazer 1.3 турбо 2WD RS",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Trailblazer 1.3 турбо 2WD RS",
        "image": "images/korea/catalog/chevrolet-40951662.jpg",
        "priceFrom": 1655346,
        "priceLabel": "1 655 346 ₽",
        "link": "https://pan-auto.ru/details/40951662",
        "specs": [
            "Мощность: 155 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 341 см³",
            "Пробег: 94 196 км",
            "Дата выпуска: Апрель, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 843 796 ₽ через 3 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40955079",
        "name": "Hyundai Avante (CN7) 1.6 Modern",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Modern",
        "image": "images/korea/catalog/hyundai-40955079.jpg",
        "priceFrom": 1608223,
        "priceLabel": "1 608 223 ₽",
        "link": "https://pan-auto.ru/details/40955079",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 83 509 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 757 948 ₽ через 8 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40946310",
        "name": "Hyundai Casper турбо Inspiration",
        "brand": "Hyundai",
        "model": "Casper турбо Inspiration",
        "image": "images/korea/catalog/hyundai-40946310.jpg",
        "priceFrom": 1527390,
        "priceLabel": "1 527 390 ₽",
        "link": "https://pan-auto.ru/details/40946310",
        "specs": [
            "Мощность: 100 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 11 672 км",
            "Дата выпуска: Август, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40952581",
        "name": "Chevrolet (GM Daewoo) Trax кроссовер 1.2 Active",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Trax кроссовер 1.2 Active",
        "image": "images/korea/catalog/chevrolet-40952581.jpg",
        "priceFrom": 2257837,
        "priceLabel": "2 257 837 ₽",
        "link": "https://pan-auto.ru/details/40952581",
        "specs": [
            "Мощность: 137 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 199 см³",
            "Пробег: 13 177 км",
            "Дата выпуска: Июнь, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 821 387 ₽ через 7 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40939286",
        "name": "Hyundai Casper турбо the Essential",
        "brand": "Hyundai",
        "model": "Casper турбо the Essential",
        "image": "images/korea/catalog/hyundai-40939286.jpg",
        "priceFrom": 1939203,
        "priceLabel": "1 939 203 ₽",
        "link": "https://pan-auto.ru/details/40939286",
        "specs": [
            "Мощность: 100 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 11 969 км",
            "Дата выпуска: Сентябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40958628",
        "name": "Hyundai Avante (CN7) 1.6 Modern",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Modern",
        "image": "images/korea/catalog/hyundai-40958628.jpg",
        "priceFrom": 1892754,
        "priceLabel": "1 892 754 ₽",
        "link": "https://pan-auto.ru/details/40958628",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 42 359 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 042 479 ₽ через 8 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40953809",
        "name": "Hyundai Sonata (DN8) 2.0 Premium",
        "brand": "Hyundai",
        "model": "Sonata (DN8) 2.0 Premium",
        "image": "images/korea/catalog/hyundai-40953809.jpg",
        "priceFrom": 1839212,
        "priceLabel": "1 839 212 ₽",
        "link": "https://pan-auto.ru/details/40953809",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 29 000 км",
            "Дата выпуска: Апрель, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 232 516 ₽ через 3 месяца"
        ],
        "description": "Добавлен сегодня · Проходной"
    },
    {
        "id": "40958602",
        "name": "Kia K5 3-го поколения 2.0 Prestige",
        "brand": "Kia",
        "model": "K5 3-го поколения 2.0 Prestige",
        "image": "images/korea/catalog/kia-40958602.jpg",
        "priceFrom": 2318876,
        "priceLabel": "2 318 876 ₽",
        "link": "https://pan-auto.ru/details/40958602",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 66 442 км",
            "Дата выпуска: Октябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 712 180 ₽ через 9 месяцев"
        ],
        "description": "Добавлен сегодня · Проходной"
    },
    {
        "id": "40948278",
        "name": "Chevrolet (GM Daewoo) Malibu Совершенно новый 1.3 турбо Premier",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Malibu Совершенно новый 1.3 турбо Premier",
        "image": "images/korea/catalog/chevrolet-40948278.jpg",
        "priceFrom": 1600725,
        "priceLabel": "1 600 725 ₽",
        "link": "https://pan-auto.ru/details/40948278",
        "specs": [
            "Мощность: 156 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 341 см³",
            "Пробег: 25 054 км",
            "Дата выпуска: Ноябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 789 175 ₽ через 10 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40953204",
        "name": "Chevrolet (GM Daewoo) Trax кроссовер 1.2 Active",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Trax кроссовер 1.2 Active",
        "image": "images/korea/catalog/chevrolet-40953204.jpg",
        "priceFrom": 2266477,
        "priceLabel": "2 266 477 ₽",
        "link": "https://pan-auto.ru/details/40953204",
        "specs": [
            "Мощность: 137 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 199 см³",
            "Пробег: 16 185 км",
            "Дата выпуска: Апрель, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 827 280 ₽ через 5 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40957552",
        "name": "Hyundai Casper турбо Inspiration",
        "brand": "Hyundai",
        "model": "Casper турбо Inspiration",
        "image": "images/korea/catalog/hyundai-40957552.jpg",
        "priceFrom": 1427209,
        "priceLabel": "1 427 209 ₽",
        "link": "https://pan-auto.ru/details/40957552",
        "specs": [
            "Мощность: 100 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 18 298 км",
            "Дата выпуска: Декабрь, 2021 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40958315",
        "name": "Kia Ray Новый Wheelchair Lift / Slope",
        "brand": "Kia",
        "model": "Ray Новый Wheelchair Lift / Slope",
        "image": "images/korea/catalog/kia-40958315.jpg",
        "priceFrom": 1645447,
        "priceLabel": "1 645 447 ₽",
        "link": "https://pan-auto.ru/details/40958315",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 14 383 км",
            "Дата выпуска: Июль, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40944453",
        "name": "Kia Ray Новый Signature",
        "brand": "Kia",
        "model": "Ray Новый Signature",
        "image": "images/korea/catalog/kia-40944453.jpg",
        "priceFrom": 1291587,
        "priceLabel": "1 291 587 ₽",
        "link": "https://pan-auto.ru/details/40944453",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 27 543 км",
            "Дата выпуска: Март, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 431 849 ₽ через 2 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40957634",
        "name": "Hyundai Casper Modern",
        "brand": "Hyundai",
        "model": "Casper Modern",
        "image": "images/korea/catalog/hyundai-40957634.jpg",
        "priceFrom": 1350600,
        "priceLabel": "1 350 600 ₽",
        "link": "https://pan-auto.ru/details/40957634",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 57 888 км",
            "Дата выпуска: Апрель, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40957125",
        "name": "Hyundai Sonata (DN8) 2.0 Modern",
        "brand": "Hyundai",
        "model": "Sonata (DN8) 2.0 Modern",
        "image": "images/korea/catalog/hyundai-40957125.jpg",
        "priceFrom": 1947451,
        "priceLabel": "1 947 451 ₽",
        "link": "https://pan-auto.ru/details/40957125",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 56 369 км",
            "Дата выпуска: Апрель, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Проходной"
    },
    {
        "id": "40946319",
        "name": "Kia Morning Urban (JA) Van",
        "brand": "Kia",
        "model": "Morning Urban (JA) Van",
        "image": "images/korea/catalog/kia-40946319.jpg",
        "priceFrom": 867208,
        "priceLabel": "867 208 ₽",
        "link": "https://pan-auto.ru/details/40946319",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 45 066 км",
            "Дата выпуска: Март, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 007 470 ₽ через 2 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40958172",
        "name": "Renault Korea (Samsung) SM6 Новый 1.3 LE",
        "brand": "Renault",
        "model": "Korea (Samsung) SM6 Новый 1.3 LE",
        "image": "images/korea/catalog/renault-40958172.jpg",
        "priceFrom": 1634650,
        "priceLabel": "1 634 650 ₽",
        "link": "https://pan-auto.ru/details/40958172",
        "specs": [
            "Мощность: 156 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 332 см³",
            "Пробег: 24 537 км",
            "Дата выпуска: Май, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40941898",
        "name": "Renault Korea (Samsung) SM6 Новый 1.3 LE",
        "brand": "Renault",
        "model": "Korea (Samsung) SM6 Новый 1.3 LE",
        "image": "images/korea/catalog/renault-40941898.jpg",
        "priceFrom": null,
        "priceLabel": null,
        "link": "https://pan-auto.ru/details/40941898",
        "specs": [
            "Мощность: 156 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 332 см³",
            "Пробег: 59 594 км",
            "Дата выпуска: Ноябрь, 2021 год"
        ],
        "description": "Проходной"
    },
    {
        "id": "40956022",
        "name": "Kia Morning Urban (JA) Prestige",
        "brand": "Kia",
        "model": "Morning Urban (JA) Prestige",
        "image": "images/korea/catalog/kia-40956022.jpg",
        "priceFrom": 996854,
        "priceLabel": "996 854 ₽",
        "link": "https://pan-auto.ru/details/40956022",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 41 615 км",
            "Дата выпуска: Ноябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 137 116 ₽ через 10 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40957771",
        "name": "Hyundai Casper The Essentials",
        "brand": "Hyundai",
        "model": "Casper The Essentials",
        "image": "images/korea/catalog/hyundai-40957771.jpg",
        "priceFrom": 1344707,
        "priceLabel": "1 344 707 ₽",
        "link": "https://pan-auto.ru/details/40957771",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 19 039 км",
            "Дата выпуска: Ноябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40958130",
        "name": "Renault Korea (Samsung) XM3 1.6 LE",
        "brand": "Renault",
        "model": "Korea (Samsung) XM3 1.6 LE",
        "image": "images/korea/catalog/renault-40958130.jpg",
        "priceFrom": 1791506,
        "priceLabel": "1 791 506 ₽",
        "link": "https://pan-auto.ru/details/40958130",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 37 094 км",
            "Дата выпуска: Январь, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 643 581 ₽ через 2 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40956780",
        "name": "Hyundai Casper The Essentials",
        "brand": "Hyundai",
        "model": "Casper The Essentials",
        "image": "images/korea/catalog/hyundai-40956780.jpg",
        "priceFrom": 1722354,
        "priceLabel": "1 722 354 ₽",
        "link": "https://pan-auto.ru/details/40956780",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 13 871 км",
            "Дата выпуска: Декабрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40958059",
        "name": "Renault Korea (Samsung) XM3 1.3 RE Signature",
        "brand": "Renault",
        "model": "Korea (Samsung) XM3 1.3 RE Signature",
        "image": "images/korea/catalog/renault-40958059.jpg",
        "priceFrom": 1730024,
        "priceLabel": "1 730 024 ₽",
        "link": "https://pan-auto.ru/details/40958059",
        "specs": [
            "Мощность: 152 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 332 см³",
            "Пробег: 32 700 км",
            "Дата выпуска: Февраль, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40940138",
        "name": "Mini Countryman Cooper Classic 2-е поколение",
        "brand": "Mini",
        "model": "Countryman Cooper Classic 2-е поколение",
        "image": "images/korea/catalog/mini-40940138.jpg",
        "priceFrom": 2217025,
        "priceLabel": "2 217 025 ₽",
        "link": "https://pan-auto.ru/details/40940138",
        "specs": [
            "Мощность: 136 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 499 см³",
            "Пробег: 47 950 км",
            "Дата выпуска: Ноябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40914805",
        "name": "Kia Morning Urban (JA) Best Picks",
        "brand": "Kia",
        "model": "Morning Urban (JA) Best Picks",
        "image": "images/korea/catalog/kia-40914805.jpg",
        "priceFrom": 973282,
        "priceLabel": "973 282 ₽",
        "link": "https://pan-auto.ru/details/40914805",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 27 000 км",
            "Дата выпуска: Май, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40954646",
        "name": "Kia K5 3-го поколения 2.0 Prestige",
        "brand": "Kia",
        "model": "K5 3-го поколения 2.0 Prestige",
        "image": "images/korea/catalog/kia-40954646.jpg",
        "priceFrom": 2344236,
        "priceLabel": "2 344 236 ₽",
        "link": "https://pan-auto.ru/details/40954646",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 20 031 км",
            "Дата выпуска: Июль, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Высокая ставка"
    },
    {
        "id": "40955593",
        "name": "Kia Ray Новый Standard",
        "brand": "Kia",
        "model": "Ray Новый Standard",
        "image": "images/korea/catalog/kia-40955593.jpg",
        "priceFrom": 1161941,
        "priceLabel": "1 161 941 ₽",
        "link": "https://pan-auto.ru/details/40955593",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 25 875 км",
            "Дата выпуска: Ноябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 302 203 ₽ через 10 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40941793",
        "name": "Hyundai Avante (CN7) 1.6 Inspiration",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Inspiration",
        "image": "images/korea/catalog/hyundai-40941793.jpg",
        "priceFrom": 2171439,
        "priceLabel": "2 171 439 ₽",
        "link": "https://pan-auto.ru/details/40941793",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 44 035 км",
            "Дата выпуска: Январь, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 945 791 ₽ через 2 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40957668",
        "name": "Hyundai Casper Smart",
        "brand": "Hyundai",
        "model": "Casper Smart",
        "image": "images/korea/catalog/hyundai-40957668.jpg",
        "priceFrom": 1173727,
        "priceLabel": "1 173 727 ₽",
        "link": "https://pan-auto.ru/details/40957668",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 63 213 км",
            "Дата выпуска: Май, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40947723",
        "name": "Kia Morning Urban (JA) Signature",
        "brand": "Kia",
        "model": "Morning Urban (JA) Signature",
        "image": "images/korea/catalog/kia-40947723.jpg",
        "priceFrom": 1374172,
        "priceLabel": "1 374 172 ₽",
        "link": "https://pan-auto.ru/details/40947723",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 30 540 км",
            "Дата выпуска: Январь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40954708",
        "name": "Hyundai Avante (CN7) 1.6 Inspiration",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Inspiration",
        "image": "images/korea/catalog/hyundai-40954708.jpg",
        "priceFrom": 1922219,
        "priceLabel": "1 922 219 ₽",
        "link": "https://pan-auto.ru/details/40954708",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 20 220 км",
            "Дата выпуска: Апрель, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 071 944 ₽ через 3 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40357299",
        "name": "Kia Seltos 1.6 2WD Signature",
        "brand": "Kia",
        "model": "Seltos 1.6 2WD Signature",
        "image": "images/korea/catalog/kia-40357299.jpg",
        "priceFrom": 1939898,
        "priceLabel": "1 939 898 ₽",
        "link": "https://pan-auto.ru/details/40357299",
        "specs": [
            "Мощность: 136 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 598 см³",
            "Пробег: 45 350 км",
            "Дата выпуска: Март, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 089 623 ₽ через 2 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40944361",
        "name": "Hyundai Casper турбо Inspiration",
        "brand": "Hyundai",
        "model": "Casper турбо Inspiration",
        "image": "images/korea/catalog/hyundai-40944361.jpg",
        "priceFrom": 1515604,
        "priceLabel": "1 515 604 ₽",
        "link": "https://pan-auto.ru/details/40944361",
        "specs": [
            "Мощность: 100 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 39 763 км",
            "Дата выпуска: Апрель, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40948450",
        "name": "Chevrolet (GM Daewoo) Trailblazer 1.3 турбо 2WD RS",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Trailblazer 1.3 турбо 2WD RS",
        "image": "images/korea/catalog/chevrolet-40948450.jpg",
        "priceFrom": 1726145,
        "priceLabel": "1 726 145 ₽",
        "link": "https://pan-auto.ru/details/40948450",
        "specs": [
            "Мощность: 155 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 341 см³",
            "Пробег: 36 262 км",
            "Дата выпуска: Сентябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 914 595 ₽ через 8 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40939524",
        "name": "Chevrolet (GM Daewoo) Trax кроссовер 1.2 Active",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Trax кроссовер 1.2 Active",
        "image": "images/korea/catalog/chevrolet-40939524.jpg",
        "priceFrom": 2266477,
        "priceLabel": "2 266 477 ₽",
        "link": "https://pan-auto.ru/details/40939524",
        "specs": [
            "Мощность: 137 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 199 см³",
            "Пробег: 15 412 км",
            "Дата выпуска: Июнь, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 827 280 ₽ через 7 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40944558",
        "name": "Hyundai Sonata (DN8) 2.0 Modern",
        "brand": "Hyundai",
        "model": "Sonata (DN8) 2.0 Modern",
        "image": "images/korea/catalog/hyundai-40944558.jpg",
        "priceFrom": 2195040,
        "priceLabel": "2 195 040 ₽",
        "link": "https://pan-auto.ru/details/40944558",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 26 727 км",
            "Дата выпуска: Октябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Проходной"
    },
    {
        "id": "40955950",
        "name": "Renault Korea (Samsung) XM3 1.6 RE",
        "brand": "Renault",
        "model": "Korea (Samsung) XM3 1.6 RE",
        "image": "images/korea/catalog/renault-40955950.jpg",
        "priceFrom": 1584651,
        "priceLabel": "1 584 651 ₽",
        "link": "https://pan-auto.ru/details/40955950",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 62 129 км",
            "Дата выпуска: Июнь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40939293",
        "name": "Renault Korea (Samsung) SM6 Новый 1.3 RE",
        "brand": "Renault",
        "model": "Korea (Samsung) SM6 Новый 1.3 RE",
        "image": "images/korea/catalog/renault-40939293.jpg",
        "priceFrom": 1575720,
        "priceLabel": "1 575 720 ₽",
        "link": "https://pan-auto.ru/details/40939293",
        "specs": [
            "Мощность: 156 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 332 см³",
            "Пробег: 75 832 км",
            "Дата выпуска: Январь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40956548",
        "name": "Renault Korea (Samsung) XM3 1.6 SE",
        "brand": "Renault",
        "model": "Korea (Samsung) XM3 1.6 SE",
        "image": "images/korea/catalog/renault-40956548.jpg",
        "priceFrom": 1443136,
        "priceLabel": "1 443 136 ₽",
        "link": "https://pan-auto.ru/details/40956548",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 25 735 км",
            "Дата выпуска: Август, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 592 861 ₽ через 7 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40954312",
        "name": "Hyundai Casper турбо Inspiration",
        "brand": "Hyundai",
        "model": "Casper турбо Inspiration",
        "image": "images/korea/catalog/hyundai-40954312.jpg",
        "priceFrom": 1904643,
        "priceLabel": "1 904 643 ₽",
        "link": "https://pan-auto.ru/details/40954312",
        "specs": [
            "Мощность: 100 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 16 676 км",
            "Дата выпуска: Декабрь, 2022 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 527 390 ₽ через 1 месяц"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40954658",
        "name": "Kia K5 3-го поколения 2.0 Prestige",
        "brand": "Kia",
        "model": "K5 3-го поколения 2.0 Prestige",
        "image": "images/korea/catalog/kia-40954658.jpg",
        "priceFrom": 2077180,
        "priceLabel": "2 077 180 ₽",
        "link": "https://pan-auto.ru/details/40954658",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 39 912 км",
            "Дата выпуска: Июль, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 470 484 ₽ через 6 месяцев"
        ],
        "description": "Добавлен сегодня · Проходной"
    },
    {
        "id": "40954803",
        "name": "Chevrolet (GM Daewoo) Trax кроссовер 1.2 RS",
        "brand": "Chevrolet",
        "model": "(GM Daewoo) Trax кроссовер 1.2 RS",
        "image": "images/korea/catalog/chevrolet-40954803.jpg",
        "priceFrom": 2154159,
        "priceLabel": "2 154 159 ₽",
        "link": "https://pan-auto.ru/details/40954803",
        "specs": [
            "Мощность: 137 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 199 см³",
            "Пробег: 25 472 км",
            "Дата выпуска: Июль, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40954105",
        "name": "Kia Ray Новый Signature",
        "brand": "Kia",
        "model": "Ray Новый Signature",
        "image": "images/korea/catalog/kia-40954105.jpg",
        "priceFrom": 1762025,
        "priceLabel": "1 762 025 ₽",
        "link": "https://pan-auto.ru/details/40954105",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 7 704 км",
            "Дата выпуска: Июль, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40955217",
        "name": "Kia Ray Новый Signature",
        "brand": "Kia",
        "model": "Ray Новый Signature",
        "image": "images/korea/catalog/kia-40955217.jpg",
        "priceFrom": 1766405,
        "priceLabel": "1 766 405 ₽",
        "link": "https://pan-auto.ru/details/40955217",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 25 748 км",
            "Дата выпуска: Март, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 433 102 ₽ через 4 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025"
    },
    {
        "id": "40955928",
        "name": "Kia K3 Совершенно новый Prestige",
        "brand": "Kia",
        "model": "K3 Совершенно новый Prestige",
        "image": "images/korea/catalog/kia-40955928.jpg",
        "priceFrom": 1620009,
        "priceLabel": "1 620 009 ₽",
        "link": "https://pan-auto.ru/details/40955928",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 16 568 км",
            "Дата выпуска: Март, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 769 734 ₽ через 2 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40952958",
        "name": "Kia Ray Новый Van Prestige",
        "brand": "Kia",
        "model": "Ray Новый Van Prestige",
        "image": "images/korea/catalog/kia-40952958.jpg",
        "priceFrom": 973282,
        "priceLabel": "973 282 ₽",
        "link": "https://pan-auto.ru/details/40952958",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 63 239 км",
            "Дата выпуска: Август, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 113 544 ₽ через 7 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40952474",
        "name": "Kia K3 Новый 2-го поколения 1.6 Prestige",
        "brand": "Kia",
        "model": "K3 Новый 2-го поколения 1.6 Prestige",
        "image": "images/korea/catalog/kia-40952474.jpg",
        "priceFrom": 1855748,
        "priceLabel": "1 855 748 ₽",
        "link": "https://pan-auto.ru/details/40952474",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 34 351 км",
            "Дата выпуска: Октябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40956135",
        "name": "Peugeot 508 2-е поколение 1.5 BlueHDi GT",
        "brand": "Peugeot",
        "model": "508 2-е поколение 1.5 BlueHDi GT",
        "image": "images/korea/catalog/peugeot-40956135.jpg",
        "priceFrom": 1751312,
        "priceLabel": "1 751 312 ₽",
        "link": "https://pan-auto.ru/details/40956135",
        "specs": [
            "Мощность: 130 л.с.",
            "Топливо: дизель",
            "Объем двигателя: 1 499 см³",
            "Пробег: 64 809 км",
            "Дата выпуска: Декабрь, 2021 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40943279",
        "name": "Kia Ray Новый Signature",
        "brand": "Kia",
        "model": "Ray Новый Signature",
        "image": "images/korea/catalog/kia-40943279.jpg",
        "priceFrom": 1818245,
        "priceLabel": "1 818 245 ₽",
        "link": "https://pan-auto.ru/details/40943279",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 15 657 км",
            "Дата выпуска: Октябрь, 2023 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Высокая ставка"
    },
    {
        "id": "40939505",
        "name": "Renault Korea (Samsung) XM3 1.6 LE Plus",
        "brand": "Renault",
        "model": "Korea (Samsung) XM3 1.6 LE Plus",
        "image": "images/korea/catalog/renault-40939505.jpg",
        "priceFrom": 1348848,
        "priceLabel": "1 348 848 ₽",
        "link": "https://pan-auto.ru/details/40939505",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 104 533 км",
            "Дата выпуска: Март, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 498 573 ₽ через 2 месяца"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40943837",
        "name": "Hyundai Avante (CN7) 1.6 Inspiration",
        "brand": "Hyundai",
        "model": "Avante (CN7) 1.6 Inspiration",
        "image": "images/korea/catalog/hyundai-40943837.jpg",
        "priceFrom": 1926950,
        "priceLabel": "1 926 950 ₽",
        "link": "https://pan-auto.ru/details/40943837",
        "specs": [
            "Мощность: 128 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 53 677 км",
            "Дата выпуска: Ноябрь, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40944767",
        "name": "Hyundai Sonata (DN8) 2.0 Premium Plus",
        "brand": "Hyundai",
        "model": "Sonata (DN8) 2.0 Premium Plus",
        "image": "images/korea/catalog/hyundai-40944767.jpg",
        "priceFrom": 2219324,
        "priceLabel": "2 219 324 ₽",
        "link": "https://pan-auto.ru/details/40944767",
        "specs": [
            "Мощность: 160 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 999 см³",
            "Пробег: 54 661 км",
            "Дата выпуска: Январь, 2023 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 2 071 287 ₽ через 2 месяца"
        ],
        "description": "Добавлен сегодня"
    },
    {
        "id": "40948783",
        "name": "Kia K3 Новый 2-го поколения 1.6 Prestige",
        "brand": "Kia",
        "model": "K3 Новый 2-го поколения 1.6 Prestige",
        "image": "images/korea/catalog/kia-40948783.jpg",
        "priceFrom": 1637688,
        "priceLabel": "1 637 688 ₽",
        "link": "https://pan-auto.ru/details/40948783",
        "specs": [
            "Мощность: 123 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 1 598 см³",
            "Пробег: 43 310 км",
            "Дата выпуска: Ноябрь, 2021 год",
            "Логистика: до Владивостока",
            "Дополнительная цена: 1 787 413 ₽ через 10 месяцев"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    },
    {
        "id": "40952940",
        "name": "Kia Ray Новый Van Prestige Special",
        "brand": "Kia",
        "model": "Ray Новый Van Prestige Special",
        "image": "images/korea/catalog/kia-40952940.jpg",
        "priceFrom": 973282,
        "priceLabel": "973 282 ₽",
        "link": "https://pan-auto.ru/details/40952940",
        "specs": [
            "Мощность: 76 л.с.",
            "Топливо: бензин",
            "Объем двигателя: 998 см³",
            "Пробег: 72 899 км",
            "Дата выпуска: Апрель, 2022 год",
            "Логистика: до Владивостока"
        ],
        "description": "Добавлен сегодня · Пошлина: Без изменений c 01.12.2025 · Проходной"
    }
];

async function loadUsaOrdersSection(){
    const metrics = document.getElementById('usaMetrics');
    if (!metrics) {
        renderPreferentialCars();
        return;
    }

    const prices = usaUnder160Cars.map(item=>item.price).filter(Boolean).sort((a,b)=>a-b);
    const avg = prices.length ? Math.round(prices.reduce((sum,val)=>sum+val,0)/prices.length) : null;
    const min = prices.length ? prices[0] : null;

    metrics.querySelector('[data-metric="count"]').textContent = numberFormatter.format(usaUnder160Cars.length);
    metrics.querySelector('[data-metric="avg"]').textContent = avg ? formatCurrency(avg) : '—';
    metrics.querySelector('[data-metric="min"]').textContent = min ? formatCurrency(min) : '—';

    renderPreferentialCars();
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

    if (!usaUnder160Cars.length){
        container.innerHTML = '<div class="usa-empty-state">Нет подготовленных предложений по льготному утильсбору</div>';
        return;
    }

    container.innerHTML = '';

    usaUnder160Cars.forEach(car=>{
        const card = document.createElement('article');
        card.className = 'orders-card usa-under-card';
        card.innerHTML = `
            <img src="${car.image}" alt="${car.name}" loading="lazy">
            <div class="orders-card-body">
                <h4>${car.name}</h4>
                <span class="usa-preferential-badge"><i class="fas fa-leaf"></i> льготный утильсбор</span>
                <ul class="usa-preferential-meta">
                    <li><span>Двигатель:</span> ${car.engine}</li>
                    <li><span>Мощность:</span> ${car.power}</li>
                    <li><span>Привод:</span> ${car.drive}</li>
                </ul>
                <div class="usa-preferential-price">от ${formatCurrency(car.price)}</div>
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
    setupChinaUnder160Section();
    updateChinaUnder160Counters();
}

function loadKoreaOrdersSection(){
    const grid = document.getElementById('koreaOrdersGrid');
    const metrics = document.getElementById('koreaMetrics');
    if (!grid || !metrics) return;

    const prices = koreaCars.map(car=>car.price).filter(Boolean).sort((a,b)=>a-b);
    const avg = prices.length ? Math.round(prices.reduce((sum,val)=>sum+val,0)/prices.length) : null;
    const min = prices.length ? prices[0] : null;

    metrics.querySelector('[data-metric="count"]').textContent = numberFormatter.format(koreaCars.length);
    metrics.querySelector('[data-metric="avg"]').textContent = avg ? formatCurrency(avg) : '—';
    metrics.querySelector('[data-metric="min"]').textContent = min ? formatCurrency(min) : '—';

    grid.innerHTML = '';

    koreaCars.forEach(car=>{
        const highlightsHtml = car.highlights && car.highlights.length
            ? `<ul class="orders-highlights">${car.highlights.map(item=>`<li><i class=\"fas fa-check\"></i>${item}</li>`).join('')}</ul>`
            : '';
        const card = document.createElement('article');
        card.className = 'orders-card korea-card';
        card.innerHTML = `
            <img src="${car.image}" alt="${car.name}" loading="lazy">
            <div class="orders-card-body">
                <h4>${car.name}</h4>
                <ul class="usa-preferential-meta">
                    <li><span>Двигатель:</span> ${car.engine}</li>
                    <li><span>Мощность:</span> ${car.power}</li>
                    <li><span>Привод:</span> ${car.drive}</li>
                    <li><span>Срок:</span> ${car.leadTime || '60-75 дней'}</li>
                </ul>
                ${highlightsHtml}
                <div class="usa-preferential-price">от ${formatCurrency(car.price)}</div>
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

        grid.appendChild(card);
    });

    setupKoreaUnder160Section();
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
        const priceValue = getUnder160PriceValue(car);
        const priceLabel = priceValue ? `от ${formatCurrency(priceValue)}` : 'Цена по запросу';
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
    if (modal) modal.style.display = 'block';
}
function closeCheckoutModal(){
    const modal = document.getElementById('checkoutModal');
    if (modal) modal.style.display = 'none';
}

function loadCars() {
    const carsGrid = document.getElementById('carsGrid');
    if (!carsGrid) return;
    carsGrid.innerHTML = '';

    state.filteredCars.forEach(car => {
        const carCard = createCarCard(car);
        carsGrid.appendChild(carCard);
    });
}

function createCarCard(car) {
    const card = document.createElement('div');
    card.className = 'car-card';
    
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
        </div>
        <div class="car-info">
            <h3 class="car-title">${car.year} ${car.brand} ${car.model}</h3>
            <div class="car-details">
                <div><strong>Двигатель:</strong> ${car.engine}L</div>
                <div><strong>Пробег:</strong> ${numberFormatter.format(car.mileage)} км</div>
                <div><strong>VIN:</strong> <a href="https://www.google.com/search?q=${car.vin}" target="_blank" rel="noopener">${car.vin}</a></div>
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
    const fallbackEl = card.querySelector('.car-image-fallback');
    if (imageEl && fallbackEl) {
        imageEl.addEventListener('error', () => {
            imageEl.classList.add('is-hidden');
            fallbackEl.style.display = 'flex';
        }, { once: true });
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
}

function applyFilters() {
    const brandFilterEl = document.getElementById('brandFilter');
    const priceFromEl = document.getElementById('priceFrom');
    const priceToEl = document.getElementById('priceTo');
    const mileageToEl = document.getElementById('mileageTo');

    if (!brandFilterEl || !priceFromEl || !priceToEl || !mileageToEl) return;

    const brandFilter = brandFilterEl.value;
    const priceFrom = parseInt(priceFromEl.value) || 0;
    const priceTo = parseInt(priceToEl.value) || Infinity;
    const mileageTo = parseInt(mileageToEl.value) || Infinity;

    state.filteredCars = carsData.filter(car => {
        const brandMatch = !brandFilter || car.brand === brandFilter;
        const priceMatch = car.price >= priceFrom && car.price <= priceTo;
        const mileageMatch = car.mileage <= mileageTo;
        
        return brandMatch && priceMatch && mileageMatch;
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
        cartBody.innerHTML = '<p style="text-align: center; color: #64748b;">Ваш заказ пуст</p>';
        cartTotal.textContent = '0';
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
                <p>Пробег: ${numberFormatter.format(item.mileage)} км</p>
                <p>Количество: ${item.quantity}</p>
                <p style="color: #10b981; font-size: 0.8rem;"><i class="fas fa-check-circle"></i> Включает растаможку и доставку</p>
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

    cartTotal.textContent = numberFormatter.format(total);
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
                    <li><strong>Пробег:</strong> ${numberFormatter.format(car.mileage)} км</li>
                    <li><strong>VIN:</strong> <a href="https://www.google.com/search?q=${car.vin}" target="_blank" rel="noopener">${car.vin}</a></li>
                    <li><strong>Дата выпуска:</strong> ${car.date}</li>
                </ul>
            </div>
            <div>
                <h4>Фотографии автомобиля</h4>
                ${createCarGallery(car)}
            </div>
        </div>
        <div style="text-align: center; padding: 2rem; background: #1f2937; border-radius: 8px; border: 1px solid #374151;">
            <h3 style="color: #f3f4f6; margin-bottom: 1rem;">${formatCurrency(car.price)}</h3>
            <p style="color: #10b981; margin-bottom: 1rem; font-weight: 500;">
                <i class="fas fa-check-circle"></i> Цена включает растаможку и доставку по России
            </p>
            <p style="color: #9ca3af; margin-bottom: 1.5rem;">Никаких дополнительных платежей!</p>
            ${car.sold ? `
            <button class="btn-primary" onclick="openSimilarRequest(${car.id})" style="margin-right: 1rem;">Подобрать аналогичный</button>
            ` : `
            <button class="btn-primary" onclick="addToCart(${car.id}); closeCarModal();" style="margin-right: 1rem;">
                <i class="fas fa-shopping-cart"></i> Сделать заказ
            </button>
            `}
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
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showNotification('Заявка отправлена! Мы свяжемся с вами в ближайшее время.');
            this.reset();
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
        const message = `Новый заказ с сайта CarExport\n\nИмя: ${name}\nТелефон: ${phone}\nEmail: ${email}\n\nТовары:\n${items}\n\nИтого: ${formatCurrency(total)}`;

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

    document.getElementById('calcResult').textContent = `${numberFormatter.format(totalRub)} ₽`;
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

async function handleSelfCalc(){
    const costUsd = parseFloat(document.getElementById('selfCostUsd').value);
    const cc = parseInt(document.getElementById('selfEngineCc').value, 10);
    if (!isFinite(costUsd) || costUsd <= 0 || !isFinite(cc) || cc <= 0){
        document.getElementById('selfCalcResult').textContent = 'Введите корректные значения стоимости и объема.';
        return;
    }
    // 1) Растаможка по тому же алгоритму, что и калькулятор: евро/см3
    const eurPerCc = customsRatePerCc(cc);
    const eurAmount = eurPerCc * cc; // евро
    const eurRub = await fetchEurRateRub();
    const customsRub = eurAmount * eurRub;

    // 2) Стоимость автомобиля в рублях: USD * курс ЦБ USD * 1.5%
    const usdRub = await fetchUsdRateRub();
    const carRub = costUsd * usdRub * 1.015; // +1.5%

    // 3) Плюс 2400 USD по курсу ЦБ РФ
    const serviceRub = 2400 * usdRub;

    const total = Math.round(customsRub + carRub + serviceRub);
    document.getElementById('selfCalcResult').textContent = `${numberFormatter.format(total)} ₽`;
}

async function fetchUsdRateRub(){
    try{
        const resp = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
        const data = await resp.json();
        const usd = data?.Valute?.USD?.Value;
        if (typeof usd === 'number' && usd > 0) return usd;
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
    if (typeof car.priceFrom === 'number' && car.priceFrom > 0) return car.priceFrom;
    if (typeof car.price === 'number' && car.price > 0) return car.price;
    return null;
}

function setupChinaUnder160Section(){
    const grid = document.getElementById('chinaUnder160Grid');

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

    if (grid) {
        applyChinaUnder160Filters();
    } else {
        state.chinaUnder160.filtered = [...state.chinaUnder160.data];
        updateChinaUnder160Counters();
    }
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

function setupKoreaUnder160Section(){
    const grid = document.getElementById('koreaUnder160Grid');

    if (!state.koreaUnder160) {
        state.koreaUnder160 = {
            data: koreaUnder160Cars.map((car, index) => ({
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

    if (!list.length){
        grid.innerHTML = '<div class="usa-empty-state">Нет подготовленных предложений по льготному утильсбору</div>';
        return;
    }

    grid.innerHTML = '';

    list.forEach(car=>{
        const specs = buildUnder160CarSpecs(car);
        const priceValue = getUnder160PriceValue(car);
        const priceLabel = priceValue ? `от ${formatCurrency(priceValue)}` : 'Цена по запросу';
        const brandBadge = car.brand ? `<span class="orders-card-brand">${car.brand}</span>` : '';
        const descriptionHtml = car.description ? `<p class="orders-card-desc">${car.description}</p>` : '';

        const card = document.createElement('article');
        card.className = 'orders-card korea-card';
        card.innerHTML = `
            <img src="${buildSvgPlaceholder(`${car.brand || ''} ${car.model || car.name || ''}`.trim() || car.name)}" alt="${car.name}" loading="lazy">
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

        grid.appendChild(card);
    });
}
