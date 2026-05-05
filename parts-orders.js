// Parts Orders System for EXPO MIR

// VIN Search Function
function searchByVIN() {
    const vinInput = document.getElementById('vinSearchInput');
    if (!vinInput) return;
    
    const vin = vinInput.value.trim().toUpperCase();
    if (!vin || vin.length < 17) {
        alert('Пожалуйста, введите корректный VIN номер (17 символов)');
        return;
    }
    
    // Открываем модальное окно для заказа по VIN
    openPartsRequestModal('VIN Search', 'VIN', 'Запчасти по VIN');
    document.getElementById('partsVIN').value = vin;
    document.getElementById('partsCarInfo').value = `VIN: ${vin}`;
}

// Load parts catalog from Supabase (with graceful fallback if table empty)
let partsouqData = null;

async function loadPartsouqData() {
    try {
        if (typeof sbQueryParts === 'undefined') return; // supabase-client.js не загружен
        const { data } = await sbQueryParts({ limit: 200 });
        if (!data || data.length === 0) return; // таблица пуста — используем статический UI
        // Группируем по марке для совместимости с updateBrandsFromData
        partsouqData = {};
        data.forEach(part => {
            const brands = Array.isArray(part.models) ? part.models : [part.brand || 'Other'];
            brands.forEach(b => {
                if (!partsouqData[b]) partsouqData[b] = [];
                partsouqData[b].push(part);
            });
        });
        updateBrandsFromData();
    } catch (_) {
        // молча пропускаем — статический UI остаётся рабочим
    }
}

function updateBrandsFromData() {
    if (!partsouqData) return;
    
    const brandFilter = document.getElementById('partsBrandFilter');
    if (!brandFilter) return;
    
    // Add parsed brands to the filter
    const parsedBrands = Object.keys(partsouqData).sort();
    parsedBrands.forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandFilter.appendChild(option);
    });
}

// Popular car brands and models
const carBrandsModels = {
    'Toyota': {
        models: ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Land Cruiser', 'Prado', 'Avensis', 'Yaris', 'Prius', 'Hilux'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Volkswagen': {
        models: ['Jetta', 'Passat', 'Tiguan', 'Golf', 'Polo', 'Touareg', 'Amarok', 'T-Cross', 'Arteon', 'T-Roc'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'BMW': {
        models: ['3 Series', '5 Series', 'X3', 'X5', 'X1', 'X6', '7 Series', '1 Series', '4 Series', 'X7'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Mercedes-Benz': {
        models: ['C-Class', 'E-Class', 'S-Class', 'GLC', 'GLE', 'GLS', 'A-Class', 'B-Class', 'CLA', 'G-Class'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Audi': {
        models: ['A4', 'A6', 'A8', 'Q5', 'Q7', 'Q3', 'A3', 'A5', 'Q8', 'TT'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Hyundai': {
        models: ['Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Kona', 'Palisade', 'Genesis', 'i30', 'i20', 'Creta'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Kia': {
        models: ['Optima', 'Rio', 'Sportage', 'Sorento', 'Soul', 'Cerato', 'Stinger', 'Telluride', 'Seltos', 'Carnival'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Nissan': {
        models: ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'X-Trail', 'Qashqai', 'Murano', 'Maxima', 'Juke', 'Patrol'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Honda': {
        models: ['Accord', 'Civic', 'CR-V', 'Pilot', 'HR-V', 'Odyssey', 'Ridgeline', 'Passport', 'Fit', 'Insight'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Ford': {
        models: ['Focus', 'Fusion', 'Escape', 'Explorer', 'F-150', 'Edge', 'Mustang', 'Expedition', 'Ranger', 'Bronco'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Chevrolet': {
        models: ['Cruze', 'Malibu', 'Equinox', 'Tahoe', 'Silverado', 'Traverse', 'Camaro', 'Suburban', 'Trax', 'Blazer'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Mazda': {
        models: ['3', '6', 'CX-5', 'CX-9', 'CX-3', 'CX-30', 'MX-5', 'CX-7', 'CX-8', 'BT-50'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Lexus': {
        models: ['ES', 'RX', 'NX', 'GX', 'LX', 'IS', 'LS', 'UX', 'RC', 'LC'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Subaru': {
        models: ['Outback', 'Forester', 'Impreza', 'Legacy', 'Ascent', 'Crosstrek', 'WRX', 'BRZ', 'Tribeca', 'Baja'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Mitsubishi': {
        models: ['Outlander', 'Lancer', 'Pajero', 'ASX', 'Eclipse Cross', 'Montero', 'Galant', 'Mirage', 'RVR', 'Delica'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Peugeot': {
        models: ['308', '408', '508', '3008', '5008', '2008', 'Partner', 'Expert', 'Boxer', 'Traveller'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Renault': {
        models: ['Logan', 'Duster', 'Sandero', 'Koleos', 'Megane', 'Fluence', 'Captur', 'Kadjar', 'Scenic', 'Clio'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Opel': {
        models: ['Astra', 'Corsa', 'Insignia', 'Mokka', 'Crossland', 'Grandland', 'Zafira', 'Vectra', 'Meriva', 'Antara'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Skoda': {
        models: ['Octavia', 'Superb', 'Kodiaq', 'Karoq', 'Kamiq', 'Fabia', 'Rapid', 'Yeti', 'Roomster', 'Citigo'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    },
    'Volvo': {
        models: ['XC60', 'XC90', 'XC40', 'S60', 'S90', 'V60', 'V90', 'XC70', 'S40', 'C30'],
        years: Array.from({length: 30}, (_, i) => 2024 - i)
    }
};

// Comprehensive parts catalog by category
const partsCatalog = {
    'Двигатель': {
        'Блок цилиндров': ['Блок цилиндров', 'Головка блока цилиндров', 'Прокладка ГБЦ', 'Крышка клапанов', 'Масляный поддон'],
        'Кривошипно-шатунный механизм': ['Коленчатый вал', 'Шатун', 'Поршень', 'Поршневые кольца', 'Вкладыши коленвала', 'Вкладыши шатуна'],
        'Газораспределительный механизм': ['Распределительный вал', 'Клапаны', 'Толкатели', 'Рокеры', 'Гидрокомпенсаторы', 'Цепь ГРМ', 'Ремень ГРМ', 'Ролики ГРМ', 'Натяжитель цепи'],
        'Система смазки': ['Масляный насос', 'Масляный фильтр', 'Масляный радиатор', 'Масляный щуп', 'Прокладка поддона'],
        'Система охлаждения': ['Радиатор', 'Помпа (водяной насос)', 'Термостат', 'Вентилятор радиатора', 'Расширительный бачок', 'Патрубки', 'Прокладки радиатора'],
        'Система питания': ['Топливный насос', 'Топливный фильтр', 'Топливные форсунки', 'Топливная рампа', 'Дроссельная заслонка', 'Регулятор давления топлива', 'Топливный бак'],
        'Система зажигания': ['Свечи зажигания', 'Катушки зажигания', 'Модуль зажигания', 'Высоковольтные провода', 'Распределитель зажигания'],
        'Турбонаддув': ['Турбокомпрессор', 'Интеркулер', 'Клапан перепускной', 'Патрубки турбины', 'Прокладки турбины']
    },
    'Трансмиссия': {
        'Коробка передач (МКПП)': ['Коробка передач', 'Сцепление', 'Выжимной подшипник', 'Диск сцепления', 'Корзина сцепления', 'Трос сцепления', 'Гидроцилиндр сцепления'],
        'Коробка передач (АКПП)': ['Коробка передач', 'Гидротрансформатор', 'Масляный насос АКПП', 'Фрикционные диски', 'Планетарная передача', 'Клапанная плита', 'Радиатор АКПП', 'Фильтр АКПП'],
        'Вариатор (CVT)': ['Вариатор', 'Ремень вариатора', 'Шкивы вариатора', 'Масляный насос', 'Клапанная плита', 'Радиатор вариатора'],
        'Роботизированная КПП': ['Коробка передач', 'Сцепление', 'Актуатор сцепления', 'Мехатроник', 'Гидроцилиндры'],
        'Раздаточная коробка': ['Раздаточная коробка', 'Цепь раздатки', 'Муфта подключения', 'Масляный насос'],
        'Карданный вал': ['Карданный вал', 'Крестовина', 'Подвесной подшипник', 'Эластичная муфта'],
        'Приводной вал': ['Приводной вал', 'ШРУС наружный', 'ШРУС внутренний', 'Пыльник ШРУС', 'Подшипник ступицы'],
        'Дифференциал': ['Дифференциал', 'Сателлиты', 'Шестерни полуосей', 'Корпус дифференциала', 'Масло дифференциала']
    },
    'Подвеска': {
        'Передняя подвеска': ['Стойка амортизатора', 'Амортизатор', 'Пружина', 'Опорный подшипник', 'Сайлентблок', 'Рычаг передний', 'Шаровая опора', 'Стабилизатор поперечной устойчивости', 'Стяжка стабилизатора', 'Подшипник ступицы'],
        'Задняя подвеска': ['Стойка амортизатора', 'Амортизатор', 'Пружина', 'Рычаг задний', 'Сайлентблок', 'Балка задняя', 'Стабилизатор поперечной устойчивости', 'Стяжка стабилизатора'],
        'Рулевое управление': ['Рулевая рейка', 'Рулевая колонка', 'Рулевой наконечник', 'Рулевая тяга', 'Рулевой кардан', 'Рулевой насос', 'Рулевой шланг', 'Бачок ГУР', 'Ремень ГУР'],
        'Колеса и шины': ['Диск колесный', 'Шины', 'Колпак колесный', 'Гайки колесные', 'Болты колесные', 'Давление в шинах датчик']
    },
    'Тормозная система': {
        'Тормозные диски': ['Тормозной диск передний', 'Тормозной диск задний', 'Вентилируемый диск', 'Перфорированный диск'],
        'Тормозные колодки': ['Тормозные колодки передние', 'Тормозные колодки задние', 'Колодки керамические', 'Колодки органические'],
        'Тормозные суппорты': ['Суппорт передний', 'Суппорт задний', 'Поршень суппорта', 'Пыльник поршня', 'Скоба суппорта', 'Направляющие суппорта'],
        'Тормозные шланги': ['Тормозной шланг передний', 'Тормозной шланг задний', 'Тормозная трубка', 'Тормозной штуцер'],
        'Главный тормозной цилиндр': ['Главный тормозной цилиндр', 'Бачок тормозной жидкости', 'Тормозная жидкость'],
        'Вакуумный усилитель': ['Вакуумный усилитель тормозов', 'Шланг вакуумного усилителя', 'Обратный клапан'],
        'ABS система': ['Блок ABS', 'Датчик ABS', 'Кольцо ABS', 'Проводка ABS']
    },
    'Электрика': {
        'Аккумулятор и стартер': ['Аккумулятор', 'Стартер', 'Втягивающее реле', 'Щетки стартера', 'Якорь стартера', 'Бендикс'],
        'Генератор': ['Генератор', 'Регулятор напряжения', 'Щетки генератора', 'Подшипник генератора', 'Шкив генератора', 'Ремень генератора'],
        'Освещение': ['Фара передняя', 'Фара противотуманная', 'Фонарь задний', 'Поворотник', 'Лампа габаритная', 'Лампа стоп-сигнала', 'Лампа ближнего света', 'Лампа дальнего света', 'Лампа LED', 'Блок управления фарами'],
        'Датчики': ['Датчик температуры', 'Датчик давления масла', 'Датчик положения коленвала', 'Датчик положения распредвала', 'Датчик кислорода (лямбда-зонд)', 'Датчик массового расхода воздуха', 'Датчик детонации', 'Датчик скорости', 'Датчик педали тормоза', 'Датчик педали газа'],
        'Проводка': ['Жгут проводов', 'Предохранители', 'Реле', 'Разъемы', 'Провода высоковольтные']
    },
    'Кузов': {
        'Кузовные детали': ['Капот', 'Крыло переднее', 'Крыло заднее', 'Дверь передняя', 'Дверь задняя', 'Крышка багажника', 'Крыша', 'Пороги', 'Бампер передний', 'Бампер задний', 'Решетка радиатора'],
        'Стекла': ['Лобовое стекло', 'Стекло боковое', 'Стекло заднее', 'Стекло двери', 'Стекло зеркала'],
        'Зеркала': ['Зеркало боковое левое', 'Зеркало боковое правое', 'Корпус зеркала', 'Стекло зеркала', 'Привод зеркала'],
        'Фары и фонари': ['Фара передняя', 'Фонарь задний', 'Поворотник', 'Противотуманная фара'],
        'Молдинги и накладки': ['Молдинг двери', 'Накладка порога', 'Накладка бампера', 'Накладка решетки']
    },
    'Салон': {
        'Панель приборов': ['Панель приборов', 'Щиток приборов', 'Приборы', 'Экран мультимедиа', 'Кнопки управления'],
        'Руль': ['Руль', 'Подрулевой переключатель', 'Кнопки на руле', 'Накладка руля'],
        'Сиденья': ['Сиденье переднее', 'Сиденье заднее', 'Чехол сиденья', 'Подголовник', 'Механизм регулировки', 'Подогрев сиденья'],
        'Коврики и обивка': ['Коврик салона', 'Обивка двери', 'Обивка потолка', 'Обивка багажника'],
        'Зеркала салона': ['Зеркало заднего вида', 'Корпус зеркала', 'Крепление зеркала']
    },
    'Система отопления и кондиционирования': {
        'Кондиционер': ['Компрессор кондиционера', 'Конденсор (радиатор кондиционера)', 'Испаритель', 'Ресивер-осушитель', 'Терморегулирующий вентиль', 'Хладагент', 'Масло компрессора', 'Ремень кондиционера'],
        'Печка': ['Радиатор печки', 'Кран печки', 'Вентилятор печки', 'Резистор вентилятора', 'Датчик температуры салона', 'Панель управления климатом'],
        'Вентиляция': ['Вентилятор салона', 'Фильтр салонный', 'Воздуховоды', 'Дефлекторы']
    },
    'Выхлопная система': {
        'Глушитель': ['Глушитель основной', 'Глушитель дополнительный', 'Резонатор', 'Труба выхлопная'],
        'Катализатор': ['Катализатор', 'Лямбда-зонд', 'Кислородный датчик'],
        'Турбина': ['Турбокомпрессор', 'Интеркулер', 'Клапан перепускной', 'Патрубки'],
        'Крепления': ['Хомут выхлопной', 'Подвеска глушителя', 'Прокладка выхлопной системы']
    },
    'Фильтры и жидкости': {
        'Фильтры': ['Масляный фильтр', 'Воздушный фильтр', 'Топливный фильтр', 'Фильтр салонный', 'Фильтр АКПП', 'Фильтр ГУР'],
        'Жидкости': ['Моторное масло', 'Трансмиссионное масло', 'Тормозная жидкость', 'Охлаждающая жидкость', 'Жидкость ГУР', 'Жидкость омывателя']
    },
    'Прочее': {
        'Крепеж': ['Болты', 'Гайки', 'Шайбы', 'Шпильки', 'Хомуты', 'Заклепки'],
        'Прокладки и уплотнители': ['Прокладка ГБЦ', 'Прокладка поддона', 'Прокладка коллектора', 'Уплотнитель двери', 'Уплотнитель стекла', 'Сальники'],
        'Инструменты': ['Ключи', 'Отвертки', 'Специальный инструмент']
    }
};

let selectedBrand = '';
let selectedModel = '';
let selectedYear = '';

// Initialize parts page
document.addEventListener('DOMContentLoaded', function() {
    initializePartsPage();
    setupPartsEventListeners();
    loadPartsouqData(); // Load parsed partsouq data
    
    // Initialize language and currency
    if (typeof setLanguage === 'function') {
        const savedLang = localStorage.getItem('language') || 'ru';
        setLanguage(savedLang);
    }
    if (typeof setCurrency === 'function') {
        const savedCurrency = localStorage.getItem('currency') || 'USD';
        setCurrency(savedCurrency);
    }
});

function initializePartsPage() {
    populateBrandFilter();
    populateYearFilter();
}

function populateBrandFilter() {
    const brandFilter = document.getElementById('partsBrandFilter');
    if (!brandFilter) return;
    
    const brands = Object.keys(carBrandsModels).sort();
    brands.forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandFilter.appendChild(option);
    });
}

function populateModelFilter(brand) {
    const modelFilter = document.getElementById('partsModelFilter');
    if (!modelFilter) return;
    
    modelFilter.innerHTML = '<option value="">Выберите модель</option>';
    modelFilter.disabled = !brand;
    
    if (!brand) return;
    
    const models = carBrandsModels[brand]?.models || [];
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelFilter.appendChild(option);
    });
}

function populateYearFilter() {
    const yearFilter = document.getElementById('partsYearFilter');
    if (!yearFilter) return;
    
    for (let year = 2024; year >= 1990; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearFilter.appendChild(option);
    }
}

function setupPartsEventListeners() {
    const brandFilter = document.getElementById('partsBrandFilter');
    const modelFilter = document.getElementById('partsModelFilter');
    const applyBtn = document.getElementById('partsApplyFilters');
    const partsRequestSubmit = document.getElementById('partsRequestSubmit');
    const analogSearchSubmit = document.getElementById('analogSearchSubmit');
    
    if (brandFilter) {
        brandFilter.addEventListener('change', function() {
            selectedBrand = this.value;
            populateModelFilter(selectedBrand);
            selectedModel = '';
        });
    }
    
    if (modelFilter) {
        modelFilter.addEventListener('change', function() {
            selectedModel = this.value;
        });
    }
    
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            selectedYear = document.getElementById('partsYearFilter')?.value || '';
            if (selectedBrand && selectedModel) {
                displayPartsCatalog();
            } else {
                alert('Пожалуйста, выберите марку и модель автомобиля');
            }
        });
    }
    
    if (partsRequestSubmit) {
        partsRequestSubmit.addEventListener('click', submitPartsRequest);
    }
    
    if (analogSearchSubmit) {
        analogSearchSubmit.addEventListener('click', submitAnalogSearch);
    }
}

function displayPartsCatalog() {
    const catalogDiv = document.getElementById('partsCatalog');
    const categoriesDiv = document.getElementById('partsCategories');
    
    if (!catalogDiv || !categoriesDiv) return;
    
    catalogDiv.style.display = 'block';
    categoriesDiv.innerHTML = '';
    
    // Check if we have parsed data for this brand/model
    let parsedParts = null;
    if (partsouqData && partsouqData[selectedBrand] && partsouqData[selectedBrand].models && partsouqData[selectedBrand].models[selectedModel]) {
        parsedParts = partsouqData[selectedBrand].models[selectedModel];
    }
    
    // Add car info header
    const carInfo = document.createElement('div');
    carInfo.style.cssText = 'text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); border-radius: 12px; color: #ffffff; box-shadow: 0 4px 20px rgba(0,0,0,0.15);';
    carInfo.innerHTML = `
        <h3 style="color: #ffffff; margin-bottom: 0.5rem; font-size: 1.8rem;">${selectedBrand} ${selectedModel}${selectedYear ? ' ' + selectedYear : ''}</h3>
        ${parsedParts ? '<p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;"><i class="fas fa-check-circle"></i> Каталог запчастей загружен</p>' : ''}
        <div style="margin-top: 1.5rem; display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
            <button class="btn-secondary" onclick="openAnalogSearchModal()" style="background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.5); color: #ffffff;">
                <i class="fas fa-search"></i> Подобрать аналоги по артикулу
            </button>
        </div>
    `;
    categoriesDiv.appendChild(carInfo);
    
    // Use parsed data if available, otherwise use default catalog
    if (parsedParts && Object.keys(parsedParts).length > 0) {
        displayParsedPartsCatalog(parsedParts, categoriesDiv);
    } else {
        displayDefaultPartsCatalog(categoriesDiv);
    }
    
    // Scroll to catalog
    catalogDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayParsedPartsCatalog(parsedParts, container) {
    Object.keys(parsedParts).forEach(categoryName => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'parts-category';
        categoryDiv.style.cssText = 'margin-bottom: 2.5rem; background: #ffffff; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);';
        
        const categoryHeader = document.createElement('h3');
        categoryHeader.style.cssText = 'color: #1f2937; font-size: 1.5rem; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 2px solid #3b82f6;';
        categoryHeader.textContent = categoryName;
        categoryDiv.appendChild(categoryHeader);
        
        const partsList = document.createElement('div');
        partsList.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;';
        
        const parts = parsedParts[categoryName];
        if (Array.isArray(parts)) {
            parts.forEach(part => {
                const partCard = createPartCard(part.name || part, categoryName, part.number, part.price);
                partsList.appendChild(partCard);
            });
        }
        
        categoryDiv.appendChild(partsList);
        container.appendChild(categoryDiv);
    });
}

function displayDefaultPartsCatalog(categoriesDiv) {
    // Display all categories
    Object.keys(partsCatalog).forEach(categoryName => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'parts-category';
        categoryDiv.style.cssText = 'margin-bottom: 2.5rem; background: #ffffff; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);';
        
        const categoryHeader = document.createElement('h3');
        categoryHeader.style.cssText = 'color: #1f2937; font-size: 1.5rem; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 2px solid #3b82f6;';
        categoryHeader.textContent = categoryName;
        categoryDiv.appendChild(categoryHeader);
        
        const subcategories = partsCatalog[categoryName];
        Object.keys(subcategories).forEach(subcategoryName => {
            const subcategoryDiv = document.createElement('div');
            subcategoryDiv.style.cssText = 'margin-bottom: 2rem;';
            
            const subcategoryHeader = document.createElement('h4');
            subcategoryHeader.style.cssText = 'color: #3b82f6; font-size: 1.2rem; margin-bottom: 1rem; font-weight: 600;';
            subcategoryHeader.textContent = subcategoryName;
            subcategoryDiv.appendChild(subcategoryHeader);
            
            const partsList = document.createElement('div');
            partsList.className = 'parts-list';
            partsList.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;';
            
            subcategories[subcategoryName].forEach(partName => {
                const partCard = createPartCard(partName, `${categoryName} > ${subcategoryName}`);
                partsList.appendChild(partCard);
            });
            
            subcategoryDiv.appendChild(partsList);
            categoryDiv.appendChild(subcategoryDiv);
        });
        
        categoriesDiv.appendChild(categoryDiv);
    });
}

function createPartCard(partName, category, partNumber = '', price = '') {
    const partCard = document.createElement('div');
    partCard.className = 'part-card';
    partCard.style.cssText = 'background: #ffffff; border: 2px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; transition: all 0.3s; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
    
    partCard.innerHTML = `
        <div style="color: #1f2937; font-weight: 600; margin-bottom: 0.75rem; font-size: 1.1rem;">${partName}</div>
        ${partNumber ? `<div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;"><i class="fas fa-barcode"></i> ${partNumber}</div>` : ''}
        ${price ? `<div style="color: #059669; font-weight: 600; margin-bottom: 0.75rem; font-size: 1.1rem;">${price}</div>` : ''}
        <button class="btn-primary" onclick="openPartsRequestModal('${category}', '', '${partName.replace(/'/g, "\\'")}')" style="width: 100%; margin-top: 0.5rem; padding: 0.75rem; border-radius: 8px;">
            <i class="fas fa-shopping-cart"></i> Заказать
        </button>
    `;
    
    partCard.addEventListener('mouseenter', function() {
        this.style.borderColor = '#3b82f6';
        this.style.transform = 'translateY(-4px)';
        this.style.boxShadow = '0 4px 16px rgba(59, 130, 246, 0.2)';
    });
    
    partCard.addEventListener('mouseleave', function() {
        this.style.borderColor = '#e5e7eb';
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.05)';
    });
    
    return partCard;
}

function openPartsRequestModal(category, subcategory, partName) {
    const modal = document.getElementById('partsRequestModal');
    if (!modal) return;
    const ps = window._partsState;
    const brandName  = ps?.brand?.name  || selectedBrand  || '';
    const modelName  = ps?.model?.name  || selectedModel  || '';
    const yearVal    = ps?.year         || selectedYear   || '';
    const engineLabel = ps?.engine?.label || '';
    const carInfoParts = [brandName, modelName, engineLabel].filter(Boolean);
    document.getElementById('partsCarInfo').value = carInfoParts.join(' ');
    document.getElementById('partsCarYear').value = yearVal;
    document.getElementById('partsCategory').value = `${category} > ${subcategory}`;
    document.getElementById('partsName').value = partName;
    document.getElementById('partsOEM').value = '';
    document.getElementById('partsVIN').value = '';
    document.getElementById('partsQuantity').value = 1;
    document.getElementById('partsClientName').value = '';
    document.getElementById('partsClientPhone').value = '';
    document.getElementById('partsClientEmail').value = '';
    document.getElementById('partsComment').value = '';
    document.getElementById('partsRequestStatus').style.display = 'none';
    
    modal.style.display = 'block';
}

function closePartsRequestModal() {
    const modal = document.getElementById('partsRequestModal');
    if (modal) modal.style.display = 'none';
}

function openAnalogSearchModal() {
    const modal = document.getElementById('analogSearchModal');
    if (!modal) return;
    const ps = window._partsState;
    const brandName  = ps?.brand?.name  || selectedBrand  || '';
    const modelName  = ps?.model?.name  || selectedModel  || '';
    const year       = ps?.year         || selectedYear   || '';
    const engineLabel = ps?.engine?.label || '';
    const carInfo = [brandName, modelName, year, engineLabel].filter(Boolean).join(' ');
    document.getElementById('analogOEM').value = '';
    document.getElementById('analogCarInfo').value = carInfo;
    document.getElementById('analogPartName').value = '';
    document.getElementById('analogClientName').value = '';
    document.getElementById('analogClientPhone').value = '';
    document.getElementById('analogClientEmail').value = '';
    document.getElementById('analogComment').value = '';
    document.getElementById('analogSearchStatus').style.display = 'none';
    
    modal.style.display = 'block';
}

function closeAnalogSearchModal() {
    const modal = document.getElementById('analogSearchModal');
    if (modal) modal.style.display = 'none';
}

function submitPartsRequest() {
    const name = document.getElementById('partsClientName').value.trim();
    const phone = document.getElementById('partsClientPhone').value.trim();
    const email = document.getElementById('partsClientEmail').value.trim();
    const statusDiv = document.getElementById('partsRequestStatus');
    
    if (!name || !phone) {
        statusDiv.textContent = 'Пожалуйста, заполните все обязательные поля';
        statusDiv.style.display = 'block';
        return;
    }
    
    const requestData = {
        carInfo: document.getElementById('partsCarInfo').value,
        carYear: document.getElementById('partsCarYear').value,
        category: document.getElementById('partsCategory').value,
        partName: document.getElementById('partsName').value,
        oem: document.getElementById('partsOEM').value.trim(),
        vin: document.getElementById('partsVIN').value.trim(),
        quantity: document.getElementById('partsQuantity').value,
        clientName: name,
        clientPhone: phone,
        clientEmail: email,
        comment: document.getElementById('partsComment').value.trim()
    };
    
    // Send request (you can integrate with your backend)
    const emailBody = `Заказ запчасти:
Автомобиль: ${requestData.carInfo} ${requestData.carYear}
Категория: ${requestData.category}
Запчасть: ${requestData.partName}
Артикул/OEM: ${requestData.oem || 'Не указан'}
VIN: ${requestData.vin || 'Не указан'}
Количество: ${requestData.quantity}

Клиент:
Имя: ${requestData.clientName}
Телефон: ${requestData.clientPhone}
Email: ${requestData.clientEmail}

Комментарий: ${requestData.comment || 'Нет'}`;
    
    const mailtoLink = `mailto:carexportgeo@bk.ru?subject=Заказ запчасти: ${requestData.partName}&body=${encodeURIComponent(emailBody)}`;
    window.location.href = mailtoLink;
    
    statusDiv.textContent = 'Заявка отправлена! Мы свяжемся с вами в ближайшее время.';
    statusDiv.style.display = 'block';
    statusDiv.style.color = '#10b981';
    
    setTimeout(() => {
        closePartsRequestModal();
        statusDiv.style.display = 'none';
    }, 3000);
}

function submitAnalogSearch() {
    const oem = document.getElementById('analogOEM').value.trim();
    const name = document.getElementById('analogClientName').value.trim();
    const phone = document.getElementById('analogClientPhone').value.trim();
    const statusDiv = document.getElementById('analogSearchStatus');
    
    if (!oem || !name || !phone) {
        statusDiv.textContent = 'Пожалуйста, заполните все обязательные поля';
        statusDiv.style.display = 'block';
        return;
    }
    
    const requestData = {
        oem: oem,
        carInfo: document.getElementById('analogCarInfo').value,
        partName: document.getElementById('analogPartName').value.trim(),
        clientName: name,
        clientPhone: phone,
        clientEmail: document.getElementById('analogClientEmail').value.trim(),
        comment: document.getElementById('analogComment').value.trim()
    };
    
    const emailBody = `Подбор аналогов запчасти:
Оригинальный артикул/OEM: ${requestData.oem}
Автомобиль: ${requestData.carInfo}
Название запчасти: ${requestData.partName || 'Не указано'}

Клиент:
Имя: ${requestData.clientName}
Телефон: ${requestData.clientPhone}
Email: ${requestData.clientEmail || 'Не указан'}

Комментарий: ${requestData.comment || 'Нет'}`;
    
    const mailtoLink = `mailto:carexportgeo@bk.ru?subject=Подбор аналогов: ${requestData.oem}&body=${encodeURIComponent(emailBody)}`;
    window.location.href = mailtoLink;

    // Save to Supabase leads
    if (typeof sbSubmitLead !== 'undefined') {
        sbSubmitLead({
            type: 'analog_search',
            name: requestData.clientName,
            phone: requestData.clientPhone,
            message: emailBody,
            carInfo: {
                vehicle: requestData.carInfo,
                oem: requestData.oem,
                part: requestData.partName || null,
            },
            sourcePage: 'parts-orders'
        }).catch(() => {});
    }
    
    statusDiv.textContent = 'Заявка отправлена! Мы найдем аналоги и свяжемся с вами.';
    statusDiv.style.display = 'block';
    statusDiv.style.color = '#10b981';
    
    setTimeout(() => {
        closeAnalogSearchModal();
        statusDiv.style.display = 'none';
    }, 3000);
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    const partsModal = document.getElementById('partsRequestModal');
    const analogModal = document.getElementById('analogSearchModal');
    
    if (event.target === partsModal) {
        closePartsRequestModal();
    }
    if (event.target === analogModal) {
        closeAnalogSearchModal();
    }
});

// New local parts catalog UI
(() => {
    const state = {
        catalog: null,
        brand: null,
        model: null,
        year: '',
        engine: null,
        parts: [],
        selectedPart: null,
    };

    // Parts that are diesel-incompatible (require spark plugs / HV ignition)
    const DIESEL_INCOMPATIBLE_PARTS = new Set([
        'Свечи зажигания', 'Катушки зажигания',
        'Высоковольтные провода', 'Модуль зажигания',
        'Распределитель зажигания'
    ]);
    // Parts only for diesel engines
    const DIESEL_ONLY_PARTS = new Set(['Свечи накаливания']);
    // Parts that don't apply to pure electric vehicles
    const NOT_FOR_ELECTRIC = new Set([
        'Свечи зажигания', 'Катушки зажигания', 'Высоковольтные провода',
        'Топливный насос', 'Топливный фильтр', 'Топливная форсунка',
        'Масляный насос', 'Масляный фильтр', 'Масляный радиатор',
        'Свечи накаливания', 'Выхлопная труба', 'Глушитель',
        'Каталитический нейтрализатор', 'Ремень ГРМ', 'Цепь ГРМ'
    ]);

    const $ = (id) => document.getElementById(id);

    function esc(value) {
        return String(value ?? '').replace(/[&<>"']/g, ch => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[ch]));
    }

    function modelCode(modelName) {
        return String(modelName || '').toUpperCase().replace(/[^A-Z0-9А-Я]/g, '').slice(0, 4).padEnd(4, 'X');
    }

    function makePartNumber(part, index) {
        const prefix = state.brand?.prefix || String(state.brand?.name || 'EX').slice(0, 2).toUpperCase();
        return `${prefix}-${modelCode(state.model?.name)}-${part.code}-${String(index + 1).padStart(3, '0')}`;
    }

    function buildPartsForCurrentModel() {
        if (Array.isArray(state.model?.parts) && state.model.parts.length) return state.model.parts;
        const template = state.catalog?.parts_template || [];
        const fuel = state.engine?.fuel || null;
        return template
            .filter(part => {
                if (!fuel) return true;
                if (fuel === 'Электро') return !NOT_FOR_ELECTRIC.has(part.name);
                if (fuel === 'Дизель') return !DIESEL_INCOMPATIBLE_PARTS.has(part.name);
                // Бензин / Гибрид — hide diesel-only parts
                return !DIESEL_ONLY_PARTS.has(part.name);
            })
            .map((part, index) => {
                const engCode = state.engine?.code ? `-${state.engine.code.replace(/[^A-Z0-9]/gi, '').slice(0, 6).toUpperCase()}` : '';
                const number = makePartNumber(part, index) + engCode;
                return {
                    ...part,
                    number,
                    analog_numbers: [`${number}-A`, `${number}-B`, `${number}-X`],
                    note: 'Применимость и точный OEM подтверждаем по VIN перед заказом.'
                };
            });
    }

    async function initLocalPartsCatalog() {
        const brandSelect = $('partsBrandSelect');
        const modelSelect = $('partsModelSelect');
        const showBtn = $('partsShowBtn');
        if (!brandSelect || !modelSelect || !showBtn) return;

        try {
            const response = await fetch('data/parts_catalog.json?v=' + Date.now(), { cache: 'no-store' });
            if (!response.ok) throw new Error('parts catalog unavailable');
            state.catalog = await response.json();
            fillBrandSelect();
            updateStatsFromLocalCatalog();
        } catch (error) {
            const grid = $('partsGrid');
            if (grid) grid.innerHTML = '<div class="parts-empty-state">Каталог запчастей временно недоступен</div>';
            return;
        }

        brandSelect.addEventListener('change', () => {
            state.brand = state.catalog.brands.find(brand => brand.slug === brandSelect.value) || null;
            state.model = null;
            fillModelSelect();
        });

        modelSelect.addEventListener('change', () => {
            state.model = state.brand?.models.find(model => model.slug === modelSelect.value) || null;
            state.engine = null;
            fillYearSelect();
        });

        $('partsYearSelect')?.addEventListener('change', event => {
            state.year = event.target.value;
        });

        $('partsEngineSelect')?.addEventListener('change', event => {
            const slug = event.target.value;
            state.engine = state.model?.engines?.find(e => e.slug === slug) || null;
        });

        showBtn.addEventListener('click', () => {
            if (!state.brand || !state.model) {
                alert('Выберите марку и модель');
                return;
            }
            showPartsForSelection();
        });

        $('partsSearchInput')?.addEventListener('input', renderParts);
        $('partsCategorySelect')?.addEventListener('change', renderParts);
        $('partsOrderClose')?.addEventListener('click', closePartsOrderModal);
        $('partsOrderSubmit')?.addEventListener('click', submitLocalPartsOrder);
        $('partsOrderModal')?.addEventListener('click', event => {
            if (event.target === $('partsOrderModal')) closePartsOrderModal();
        });
    }

    function fillBrandSelect() {
        const brandSelect = $('partsBrandSelect');
        if (!brandSelect || !state.catalog) return;
        brandSelect.innerHTML = '<option value="">Выберите марку</option>' + state.catalog.brands
            .map(brand => `<option value="${esc(brand.slug)}">${esc(brand.name)}</option>`)
            .join('');
    }

    function fillModelSelect() {
        const modelSelect = $('partsModelSelect');
        const yearSelect = $('partsYearSelect');
        const engineSelect = $('partsEngineSelect');
        if (!modelSelect) return;
        modelSelect.disabled = !state.brand;
        modelSelect.innerHTML = '<option value="">Выберите модель</option>';
        if (yearSelect) {
            yearSelect.disabled = true;
            yearSelect.innerHTML = '<option value="">Любой год</option>';
        }
        if (engineSelect) {
            engineSelect.disabled = true;
            engineSelect.innerHTML = '<option value="">Любой двигатель</option>';
        }
        if (!state.brand) return;
        modelSelect.innerHTML += state.brand.models
            .map(model => `<option value="${esc(model.slug)}">${esc(model.name)}</option>`)
            .join('');
    }

    function fillYearSelect() {
        const yearSelect = $('partsYearSelect');
        if (!yearSelect) return;
        yearSelect.disabled = !state.model;
        yearSelect.innerHTML = '<option value="">Любой год</option>';
        if (!state.model) return;
        yearSelect.innerHTML += state.model.years
            .map(year => `<option value="${year}">${year}</option>`)
            .join('');
        fillEngineSelect();
    }

    function fillEngineSelect() {
        const engineSelect = $('partsEngineSelect');
        if (!engineSelect) return;
        const engines = state.model?.engines;
        engineSelect.innerHTML = '<option value="">Любой двигатель</option>';
        if (!engines?.length) {
            engineSelect.disabled = true;
            return;
        }
        engineSelect.disabled = false;
        engineSelect.innerHTML += engines
            .map(e => `<option value="${esc(e.slug)}">${esc(e.label)}</option>`)
            .join('');
        // Restore previously selected engine if it still applies
        if (state.engine?.slug) {
            const still = engines.find(e => e.slug === state.engine.slug);
            if (still) engineSelect.value = still.slug;
            else state.engine = null;
        }
    }

    function updateStatsFromLocalCatalog() {
        if (!state.catalog) return;
        const brandsCount = $('brandsCount');
        const modelsCount = $('modelsCount');
        const lastUpdate = $('lastUpdate');
        const totalModels = state.catalog.brands.reduce((sum, brand) => sum + brand.models.length, 0);
        if (brandsCount) brandsCount.textContent = state.catalog.brands.length;
        if (modelsCount) modelsCount.textContent = totalModels;
        if (lastUpdate && state.catalog.last_updated) {
            lastUpdate.textContent = new Date(state.catalog.last_updated).toLocaleDateString('ru-RU');
        }
    }

    function showPartsForSelection() {
        state.parts = buildPartsForCurrentModel();
        const panel = $('partsResultsPanel');
        const title = $('partsVehicleTitle');
        if (panel) panel.style.display = 'block';
        if (title) {
            const engineLabel = state.engine ? ` · ${state.engine.label}` : '';
            title.textContent = `${state.brand.name} ${state.model.name}${state.year ? ' ' + state.year : ''}${engineLabel}: доступные запчасти`;
        }
        fillCategorySelect();
        renderParts();
        panel?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function fillCategorySelect() {
        const select = $('partsCategorySelect');
        if (!select) return;
        const categories = [...new Set(state.parts.map(part => part.category))].sort((a, b) => a.localeCompare(b, 'ru'));
        select.innerHTML = '<option value="">Все категории</option>' + categories
            .map(category => `<option value="${esc(category)}">${esc(category)}</option>`)
            .join('');
    }

    function renderParts() {
        const grid = $('partsGrid');
        if (!grid) return;
        const query = ($('partsSearchInput')?.value || '').trim().toLowerCase();
        const category = $('partsCategorySelect')?.value || '';
        let list = state.parts;
        if (category) list = list.filter(part => part.category === category);
        if (query) {
            list = list.filter(part => [
                part.name, part.number, part.category, part.group, ...(part.analog_numbers || [])
            ].join(' ').toLowerCase().includes(query));
        }
        if (!list.length) {
            grid.innerHTML = '<div class="parts-empty-state">По выбранным условиям запчасти не найдены</div>';
            return;
        }
        grid.innerHTML = list.map((part, index) => `
            <article class="parts-item-card">
                <div class="parts-item-title">${esc(part.name)}</div>
                <div class="parts-item-meta">
                    <span>${esc(part.category)} / ${esc(part.group)}</span>
                    <span>Каталожный номер: <span class="parts-number">${esc(part.number)}</span></span>
                    <span>Аналоги: ${esc((part.analog_numbers || []).join(', '))}</span>
                    <span>Обычно требуется: ${esc(part.quantity)} шт.</span>
                </div>
                <div class="parts-card-actions">
                    <button class="btn-primary" type="button" data-part-index="${index}"><i class="fas fa-shopping-cart"></i> Заказать</button>
                </div>
            </article>
        `).join('');
        grid.querySelectorAll('[data-part-index]').forEach((button, index) => {
            button.addEventListener('click', () => openLocalPartsOrder(list[index]));
        });
    }

    function openLocalPartsOrder(part) {
        state.selectedPart = part;
        const engineStr = state.engine ? ` ${state.engine.label}` : '';
        const vehicle = `${state.brand?.name || ''} ${state.model?.name || ''}${state.year ? ' ' + state.year : ''}${engineStr}`.trim();
        $('partsOrderVehicle').value = vehicle;
        $('partsOrderNumber').value = part.number || '';
        $('partsOrderName').value = part.name || '';
        $('partsOrderQty').value = part.quantity || 1;
        $('partsOrderVin').value = '';
        $('partsOrderClient').value = '';
        $('partsOrderPhone').value = '';
        $('partsOrderComment').value = '';
        const status = $('partsOrderStatus');
        if (status) status.style.display = 'none';
        const modal = $('partsOrderModal');
        if (modal) {
            modal.classList.add('is-open');
            modal.setAttribute('aria-hidden', 'false');
        }
    }

    function closePartsOrderModal() {
        const modal = $('partsOrderModal');
        if (modal) {
            modal.classList.remove('is-open');
            modal.setAttribute('aria-hidden', 'true');
        }
    }

    function submitLocalPartsOrder() {
        const status = $('partsOrderStatus');
        const client = $('partsOrderClient').value.trim();
        const phone = $('partsOrderPhone').value.trim();
        if (!client || !phone) {
            if (status) {
                status.textContent = 'Укажите имя и телефон';
                status.style.display = 'block';
            }
            return;
        }
        const body = [
            'Заказ запчасти EXPO MIR',
            `Автомобиль: ${$('partsOrderVehicle').value}`,
            `Запчасть: ${$('partsOrderName').value}`,
            `Каталожный номер: ${$('partsOrderNumber').value}`,
            `VIN: ${$('partsOrderVin').value.trim() || 'не указан'}`,
            `Количество: ${$('partsOrderQty').value}`,
            `Клиент: ${client}`,
            `Телефон: ${phone}`,
            `Комментарий: ${$('partsOrderComment').value.trim() || 'нет'}`
        ].join('\n');

        // Сохраняем в Supabase leads
        if (typeof sbSubmitLead !== 'undefined') {
            sbSubmitLead({
                type: 'parts_order',
                name: client,
                phone: phone,
                message: body,
                carInfo: {
                    vehicle: $('partsOrderVehicle').value,
                    part: $('partsOrderName').value,
                    oem: $('partsOrderNumber').value,
                    vin: $('partsOrderVin').value.trim() || null,
                    qty: $('partsOrderQty').value
                },
                sourcePage: 'parts-orders'
            }).catch(() => {});
        }

        window.location.href = `mailto:carexportgeo@bk.ru?subject=${encodeURIComponent('Заказ запчасти ' + $('partsOrderNumber').value)}&body=${encodeURIComponent(body)}`;
        if (status) {
            status.textContent = 'Заявка подготовлена. Если почтовое окно не открылось, напишите нам в WhatsApp.';
            status.style.display = 'block';
            status.style.color = '#10b981';
        }
    }

    window.selectPartsModel = function(brandName, modelName) {
        if (!state.catalog) return;
        state.brand = state.catalog.brands.find(brand => brand.name === brandName) || null;
        state.model = state.brand?.models.find(model => model.name === modelName) || null;
        state.engine = null;
        if (!state.brand || !state.model) return;
        const brandSelect = $('partsBrandSelect');
        const modelSelect = $('partsModelSelect');
        if (brandSelect) brandSelect.value = state.brand.slug;
        fillModelSelect();
        if (modelSelect) modelSelect.value = state.model.slug;
        fillYearSelect();
        showPartsForSelection();
    };

    // Expose state for global helpers outside this IIFE
    window._partsState = state;

    document.addEventListener('DOMContentLoaded', initLocalPartsCatalog);
})();

