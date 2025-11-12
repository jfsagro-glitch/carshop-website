'use strict';

const state = {
    cart: [],
    filteredCars: [],
    carGalleries: {},
    touch: {
        startX: null,
        galleryId: null
    }
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
        name: 'Haval Jolion Tech Plus',
        brand: 'Haval',
        model: 'Jolion',
        engine: '1.5 л, турбо, CVT',
        power: '143 л.с.',
        drive: 'Передний',
        leadTime: '50-60 дней',
        highlights: ['Комплекс ADAS L2', 'Салон из эко-кожи', 'Камеры 360°'],
        price: 2390000,
        image: 'images/china/haval-jolion.svg'
    },
    {
        name: 'Chery Tiggo 7 Pro Prestige',
        brand: 'Chery',
        model: 'Tiggo 7 Pro',
        engine: '1.5 л, турбо, CVT',
        power: '147 л.с.',
        drive: 'Передний',
        leadTime: '45-55 дней',
        highlights: ['Панорамная крыша', 'Подогрев всех сидений', 'Бесключевой доступ'],
        price: 2490000,
        image: 'images/china/chery-tiggo7.svg'
    },
    {
        name: 'Geely Coolray Flagship',
        brand: 'Geely',
        model: 'Coolray',
        engine: '1.5 л, турбо, 7DCT',
        power: '150 л.с.',
        drive: 'Передний',
        leadTime: '55-65 дней',
        highlights: ['Цифровая приборная панель', 'Парктроники 360°', 'Адаптивный круиз-контроль'],
        price: 2280000,
        image: 'images/china/geely-coolray.svg'
    },
    {
        name: 'Exeed LX Premium',
        brand: 'Exeed',
        model: 'LX',
        engine: '1.5 л, турбо, 7DCT',
        power: '147 л.с.',
        drive: 'Передний',
        leadTime: '55-70 дней',
        highlights: ['Стерео камера ADAS', 'Вентиляция передних сидений', 'Матрица 7680×4320 в медиасистеме'],
        price: 2830000,
        image: 'images/china/exeed-lx.svg'
    },
    {
        name: 'Omoda C5 Ultimate AWD',
        brand: 'Omoda',
        model: 'C5',
        engine: '1.6 л, турбо, 7DCT',
        power: '150 л.с.',
        drive: 'Полный',
        leadTime: '55-65 дней',
        highlights: ['Полный привод AWD', 'Набор систем безопасности ADAS', 'Акустика Sony'],
        price: 2940000,
        image: 'images/china/omoda-c5.svg'
    },
    {
        name: 'Changan CS35 Plus Luxe',
        brand: 'Changan',
        model: 'CS35 Plus',
        engine: '1.4 л, турбо, 7DCT',
        power: '150 л.с.',
        drive: 'Передний',
        leadTime: '45-55 дней',
        highlights: ['Зимний пакет', 'Электропривод сиденья водителя', 'CarPlay/Android Auto'],
        price: 2170000,
        image: 'images/china/changan-cs35.svg'
    }
];

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
    const grid = document.getElementById('chinaOrdersGrid');
    const metrics = document.getElementById('chinaMetrics');
    if (!grid || !metrics) return;

    const prices = chinaCars.map(car=>car.price).filter(Boolean).sort((a,b)=>a-b);
    const avg = prices.length ? Math.round(prices.reduce((sum,val)=>sum+val,0)/prices.length) : null;
    const min = prices.length ? prices[0] : null;

    metrics.querySelector('[data-metric="count"]').textContent = numberFormatter.format(chinaCars.length);
    metrics.querySelector('[data-metric="avg"]').textContent = avg ? formatCurrency(avg) : '—';
    metrics.querySelector('[data-metric="min"]').textContent = min ? formatCurrency(min) : '—';

    grid.innerHTML = '';

    chinaCars.forEach(car=>{
        const card = document.createElement('article');
        card.className = 'orders-card china-card';
        const highlightsHtml = car.highlights && car.highlights.length
            ? `<ul class="orders-highlights">${car.highlights.map(item=>`<li><i class=\"fas fa-check\"></i>${item}</li>`).join('')}</ul>`
            : '';
        card.innerHTML = `
            <img src="${car.image}" alt="${car.name}" loading="lazy">
            <div class="orders-card-body">
                <h4>${car.name}</h4>
                <ul class="usa-preferential-meta">
                    <li><span>Двигатель:</span> ${car.engine}</li>
                    <li><span>Мощность:</span> ${car.power}</li>
                    <li><span>Привод:</span> ${car.drive}</li>
                    <li><span>Срок:</span> ${car.leadTime || '45-70 дней'}</li>
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
                prefillChinaRequest(car);
            });
        }

        attachImageFallback(card.querySelector('img'), car);

        grid.appendChild(card);
    });
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
        priceEl.value = car.price || '';
        const details = [
            `Авто из Китая: ${car.name}`,
            car.engine ? `Двигатель: ${car.engine}` : null,
            car.power ? `Мощность: ${car.power}` : null,
            car.drive ? `Привод: ${car.drive}` : null,
            car.leadTime ? `Срок поставки: ${car.leadTime}` : null
        ].filter(Boolean).join('\n');
        noteEl.value = details;
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
        priceEl.value = car.price || '';
        const details = [
            `Авто из Кореи: ${car.name}`,
            car.engine ? `Двигатель: ${car.engine}` : null,
            car.power ? `Мощность: ${car.power}` : null,
            car.drive ? `Привод: ${car.drive}` : null,
            car.leadTime ? `Срок поставки: ${car.leadTime}` : null
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
                <div class="car-image-fallback">
                    <div class="car-image-fallback-icon">🚗</div>
                    <h4 class="car-image-fallback-title">${car.year} ${car.brand} ${car.model}</h4>
                    <p class="car-image-fallback-text">Нажмите для просмотра галереи</p>
                    <div class="car-image-fallback-cta">
                        <i class="fas fa-images"></i> Галерея
                    </div>
                </div>
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
