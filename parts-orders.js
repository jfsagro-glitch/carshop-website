// Parts Orders System for EXPO MIR

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
    
    // Add car info header
    const carInfo = document.createElement('div');
    carInfo.style.cssText = 'text-align: center; margin-bottom: 2rem; padding: 1.5rem; background: rgba(15, 23, 42, 0.8); border-radius: 12px;';
    carInfo.innerHTML = `
        <h3 style="color: #f3f4f6; margin-bottom: 0.5rem;">${selectedBrand} ${selectedModel}${selectedYear ? ' ' + selectedYear : ''}</h3>
        <button class="btn-secondary" onclick="openAnalogSearchModal()" style="margin-top: 1rem;">
            <i class="fas fa-search"></i> Подобрать аналоги по артикулу
        </button>
    `;
    categoriesDiv.appendChild(carInfo);
    
    // Display all categories
    Object.keys(partsCatalog).forEach(categoryName => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'parts-category';
        categoryDiv.style.cssText = 'margin-bottom: 2.5rem;';
        
        const categoryHeader = document.createElement('h3');
        categoryHeader.style.cssText = 'color: #f3f4f6; font-size: 1.5rem; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 2px solid rgba(212, 175, 55, 0.3);';
        categoryHeader.textContent = categoryName;
        categoryDiv.appendChild(categoryHeader);
        
        const subcategories = partsCatalog[categoryName];
        Object.keys(subcategories).forEach(subcategoryName => {
            const subcategoryDiv = document.createElement('div');
            subcategoryDiv.style.cssText = 'margin-bottom: 1.5rem;';
            
            const subcategoryHeader = document.createElement('h4');
            subcategoryHeader.style.cssText = 'color: #d4af37; font-size: 1.2rem; margin-bottom: 1rem;';
            subcategoryHeader.textContent = subcategoryName;
            subcategoryDiv.appendChild(subcategoryHeader);
            
            const partsList = document.createElement('div');
            partsList.className = 'parts-list';
            partsList.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem;';
            
            subcategories[subcategoryName].forEach(partName => {
                const partCard = document.createElement('div');
                partCard.className = 'part-card';
                partCard.style.cssText = 'background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 8px; padding: 1rem; transition: all 0.3s; cursor: pointer;';
                
                partCard.innerHTML = `
                    <div style="color: #f3f4f6; font-weight: 500; margin-bottom: 0.5rem;">${partName}</div>
                    <button class="btn-primary" onclick="openPartsRequestModal('${categoryName}', '${subcategoryName}', '${partName}')" style="width: 100%; margin-top: 0.5rem; padding: 0.5rem;">
                        <i class="fas fa-shopping-cart"></i> Заказать
                    </button>
                `;
                
                partCard.addEventListener('mouseenter', function() {
                    this.style.borderColor = 'rgba(212, 175, 55, 0.5)';
                    this.style.transform = 'translateY(-2px)';
                });
                
                partCard.addEventListener('mouseleave', function() {
                    this.style.borderColor = 'rgba(212, 175, 55, 0.2)';
                    this.style.transform = 'translateY(0)';
                });
                
                partsList.appendChild(partCard);
            });
            
            subcategoryDiv.appendChild(partsList);
            categoryDiv.appendChild(subcategoryDiv);
        });
        
        categoriesDiv.appendChild(categoryDiv);
    });
    
    // Scroll to catalog
    catalogDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function openPartsRequestModal(category, subcategory, partName) {
    const modal = document.getElementById('partsRequestModal');
    if (!modal) return;
    
    document.getElementById('partsCarInfo').value = `${selectedBrand} ${selectedModel}`;
    document.getElementById('partsCarYear').value = selectedYear || '';
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
    
    document.getElementById('analogOEM').value = '';
    document.getElementById('analogCarInfo').value = `${selectedBrand} ${selectedModel}${selectedYear ? ' ' + selectedYear : ''}`;
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

