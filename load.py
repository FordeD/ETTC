"""
Plugin for "HITS"
"""
import traceback
from typing import Optional, Tuple
import sys
import json
import requests
from bs4 import BeautifulSoup
import re
from ttkHyperlinkLabel import HyperlinkLabel as hll
from urllib.parse import quote
from threading import Thread
from logger import LogContext
import os
import pyperclip
sys.path.insert(0, "./soupsieve")  # Добавляем папку в пути поиска модулей
sys.path.insert(0, "./pyperclip")  # Добавляем папку в пути поиска модулей

try: #py3
    import tkinter as tk
except: #py2
    import Tkinter as tk
try:
    from config import config
    import myNotebook as nb

except ImportError:  ## test mode
    config = dict()
    nb = None

this = sys.modules[__name__]

PLUGIN_NAME = "ETTC RU"
PLUGIN_VERSION = "1.1.0"

LOG = LogContext()
LOG.set_filename(os.path.join(os.path.abspath(os.path.dirname(__file__)), "plugin.log"))

DEFAULT_MAX_ROUTE_DISTANCE = 40
DEFAULT_MIN_SUPPLY = 1000
DEFAULT_MAX_PRICE_AGE = 1
DEFAULT_LANDING_PAD = 3
DEFAULT_INCLUDE_SURFACES = 1
DEFAULT_MAX_STATION_DISTANCE = 10000
DEFAULT_INCLUDE_CARIERS = 1
DEFAULT_MIN_CAPACITY = 720
DEFAULT_MIN_DEMAND = 0

ITEMS = dict([
    ("Wine", "Вино"),
    ("Onionhead Gamma Strain", "Луковая головка, сорт гамма"),
    ("Narcotics", "Наркотики"),
    ("Beer", "Пиво"),
    ("Bootleg Liquor", "Самогон"),
    ("Liquor", "Спиртное"),
    ("Tobacco", "Табак"),
    ("Combat Stabilisers", "Боевые стабилизаторы"),
    ("Agri-Medicines", "Ветмедикаменты"),
    ("Advanced Medicines", "Новейшие лекарства"),
    ("Basic Medicines", "Основные лекарства"),
    ("Progenitor Cells", "Прогениторные клетки"),
    ("Performance Enhancers", "Стимуляторы"),
    ("Emergency Power Cells", "Аварийные энергоячейки"),
    ("Atmospheric Processors", "Атмосферный процессор"),
    ("Water Purifiers", "Водоочистители"),
    ("Exhaust Manifold", "Выпускной коллектор"),
    ("Geological Equipment", "Геологическое оборудование"),
    ("Skimmer Components", "Детали оборон. беспилотников"),
    ("Ion Distributor", "Ионный распределитель"),
    ("Microbial Furnaces", "Микробные печи"),
    ("Modular Terminals", "Модульные терминалы"),
    ("Marine Equipment", "Морское оборудование"),
    ("Radiation Baffle", "Отражатель излучения"),
    ("Power Converter", "Преобразователь энергии"),
    ("Heatsink Interlink", "Радиаторный соединитель"),
    ("HN Shock Mount", "Разрядная установка HN"),
    ("Magnetic Emitter Coil", "Спираль магнитного излучателя"),
    ("Building Fabricators", "Строительные синтезаторы"),
    ("Thermal Cooling Units", "Термальные охладители"),
    ("Crop Harvesters", "Уборочный комбайн"),
    ("Reinforced Mounting Plate", "Усиленная монтажная плита"),
    ("Articulation Motors", "Шарнирные моторы"),
    ("Mineral Extractors", "Экстракторы минералов"),
    ("Power Generators", "Электрогенераторы"),
    ("Energy Grid Assembly", "Электросеть в сборе"),
    ("Power Transfer Bus", "Энергообменная шина"),
    ("Aluminium", "Алюминий"),
    ("Beryllium", "Бериллий"),
    ("Bismuth", "Висмут"),
    ("Gallium", "Галлий"),
    ("Hafnium 178", "Гафний-178"),
    ("Gold", "Золото"),
    ("Indium", "Индий"),
    ("Cobalt", "Кобальт"),
    ("Lanthanum", "Лантан"),
    ("Lithium", "Литий"),
    ("Copper", "Медь"),
    ("Osmium", "Осмий"),
    ("Palladium", "Палладий"),
    ("Platinum", "Платина"),
    ("Praseodymium", "Празеодим"),
    ("Samarium", "Самарий"),
    ("Silver", "Серебро"),
    ("Steel", "Сталь"),
    ("Thallium", "Таллий"),
    ("Tantalum", "Тантал"),
    ("Titanium", "Титан"),
    ("Thorium", "Торий"),
    ("Uranium", "Уран"),
    ("Alexandrite", "Александрит"),
    ("Benitoite", "Бенитоит"),
    ("Bertrandite", "Бертрандит"),
    ("Bauxite", "Боксит"),
    ("Bromellite", "Бромеллит"),
    ("Gallite", "Галлит"),
    ("Haematite", "Гематит"),
    ("Lithium Hydroxide", "Гидроксид лития"),
    ("Goslarite", "Госларит"),
    ("Grandidierite", "Грандидьерит"),
    ("Jadeite", "Жадеит"),
    ("Indite", "Индит"),
    ("Methane Clathrate", "Клатрат метана"),
    ("Coltan", "Колтан"),
    ("Cryolite", "Криолит"),
    ("Methanol Monohydrate Crystals", "Кристаллы моногидрата метанола"),
    ("Lepidolite", "Лепидолит"),
    ("Monazite", "Монацит"),
    ("Moissanite", "Муассанит"),
    ("Musgravite", "Мусгравит"),
    ("Low Temperature Diamonds", "Низкотемпературные алмазы"),
    ("Void Opals", "Опал бездны"),
    ("Pyrophyllite", "Пирофиллит"),
    ("Rhodplumsite", "Родплумсайт"),
    ("Rutile", "Рутил"),
    ("Serendibite", "Серендибит"),
    ("Taaffeite", "Тааффеит"),
    ("Uraninite", "Уранинит"),
    ("Battle Weapons", "Военное оружие"),
    ("Personal Weapons", "Личное оружие"),
    ("Landmines", "Мины"),
    ("Non-Lethal Weapons", "Нелетальное оружие"),
    ("Reactive Armour", "Реактивная защита"),
    ("Biowaste", "Биоотходы"),
    ("Chemical Waste", "Радиоактивные материалы"),
    ("Toxic Waste", "Токсичные отходы"),
    ("Scrap", "Утильсырье"),
    ("Trinkets of Hidden Fortune", "Безделушки таинственной Фортуны"),
    ("Domestic Appliances", "Бытовая техника"),
    ("Clothing", "Одежда"),
    ("Consumer Technology", "Потребительские товары"),
    ("Survival Equipment", "Снаряжение для выживания"),
    ("Evacuation Shelter", "Эвакуационное убежище"),
    ("Algae", "Водоросли"),
    ("Grain", "Зерно"),
    ("Coffee", "Кофе"),
    ("Animal Meat", "Мясо животных"),
    ("Food Cartridges", "Пищевые брикеты"),
    ("Fish", "Рыба"),
    ("Synthetic Meat", "Синтетическое мясо"),
    ("Fruit and Vegetables", "Фрукты и овощи"),
    ("Tea", "Чай"),
    ("CMM Composite", "CMM-композит"),
    ("Neofabric Insulation", "Высокотехнологичная изоляция"),
    ("Insulating Membrane", "Изолирующая мембрана"),
    ("Ceramic Composites", "Керамокомпозиты"),
    ("Meta-Alloys", "Метасплавы"),
    ("Polymers", "Полимеры"),
    ("Semiconductors", "Полупроводники"),
    ("Superconductors", "Сверхпроводники"),
    ("Micro-Weave Cooling Hoses", "Шланги системы охлаждения малых диаметров"),
    ("Imperial Slaves", "Имперские рабы"),
    ("Slaves", "Рабы"),
    ("Anomaly Particles", "Аномальные частицы"),
    ("Large Survey Data Cache", "Большой пакет с данными исследования"),
    ("Pod Outer Tissue", "Внешняя ткань семянки"),
    ("Military Plans", "Военные планы"),
    ("Gene Bank", "Генотека"),
    ("Diplomatic Bag", "Дипломатическая сумка"),
    ("Precious Gems", "Драгоценные камни"),
    ("Antiquities", "Древние реликвии"),
    ("Antique Jewellery", "Древние ювелирные украшения"),
    ("Ancient Artefact", "Древний артефакт"),
    ("Ancient Key", "Древний ключ"),
    ("Mollusc Fluid", "Жидкость моллюска"),
    ("Hostage", "Заложники"),
    ("Prohibited Research Materials", "Запретные материалы исследований"),
    ("Encrypted Data Storage", "Зашифрованный носитель данных"),
    ("Fossil Remnants", "Ископаемые останки"),
    ("Time Capsule", "Капсула времени"),
    ("Titan Drive Component", "Компонент двигателя титана"),
    ("SAP 8 Core Container", "Контейнер SAP 8 Core"),
    ("Antimatter Containment Unit", "Контейнер с антиматерией"),
    ("Coral Sap", "Коралловая смола"),
    ("Personal Effects", "Личные вещи"),
    ("Small Survey Data Cache", "Малый пакет с данными исследования"),
    ("Scientific Research", "Материалы исследования"),
    ("Pod Mesoglea", "Мезоглея семянки"),
    ("Mollusc Membrane", "Мембрана моллюска"),
    ("Pod Dead Tissue", "Мёртвая ткань семянки"),
    ("Mollusc Mycelium", "Мицелий моллюска"),
    ("Mollusc Brain Tissue", "Мозговое вещество моллюска"),
    ("Mollusc Soft Tissue", "Мягкие ткани моллюска"),
    ("Scientific Samples", "Научные образцы"),
    ("Unclassified Relic", "Неопознанная реликвия"),
    ("Impure Spire Mineral", "Неочищенный минерал со шпилей"),
    ("Titan Maw Partial Tissue Sample", "Неполный образец ткани пасти титана"),
    ("Titan Partial Tissue Sample", "Неполный образец ткани титана"),
    ("Unstable Data Core", "Нестабильное ядро данных"),
    ("Salvageable Wreckage", "Обломки кораблекрушения"),
    ("Titan Maw Deep Tissue Sample", "Образец глубокой ткани пасти титана"),
    ("Titan Deep Tissue Sample", "Образец глубокой ткани титана"),
    ("Caustic Tissue Sample", "Образец едких тканей"),
    ("Titan Maw Tissue Sample", "Образец ткани пасти титана"),
    ("Thargoid Scout Tissue Sample", "Образец тканей таргоида-разведчика"),
    ("Thargoid Basilisk Tissue Sample", "Образец ткани таргоидского корабля «Василиск»"),
    ("Thargoid Hydra Tissue Sample", "Образец ткани таргоидского корабля «Гидра»"),
    ("Thargoid Glaive Tissue Sample", "Образец ткани таргоидского корабля «Глефа»"),
    ("Thargoid Scythe Tissue Sample", "Образец ткани таргоидского корабля «Коса»"),
    ("Thargoid Medusa Tissue Sample", "Образец ткани таргоидского корабля «Медуза»"),
    ("Thargoid Cyclops Tissue Sample", "Образец ткани таргоидского корабля «Циклоп»"),
    ("Thargoid Orthrus Tissue Sample", "Образец ткани таргоидского корабля «Орф»"),
    ("Titan Tissue Sample", "Образец ткани титана"),
    ("Geological Samples", "Образцы породы"),
    ("Thargoid Technology Samples", "Образцы таргоидских технологий"),
    ("Rebel Transmissions", "Переговоры повстанцев"),
    ("Assault Plans", "Планы атак"),
    ("Pod Surface Tissue", "Поверхностная ткань семянки"),
    ("Damaged Escape Pod", "Повреждённая спасательная капсула"),
    ("Political Prisoner", "Политзаключённые"),
    ("Semi-Refined Spire Mineral", "Полуочищенный минерал со шпилей"),
    ("Technical Blueprints", "Промышленные чертежи"),
    ("Unoccupied Escape Pod", "Пустая спасательная капсула"),
    ("Galactic Travel Guides", "Путеводитель галактического путешественника"),
    ("Military Intelligence", "Разведданные"),
    ("Rare Artwork", "Редкие произведения искусства"),
    ("Commercial Samples", "Рекламные образцы"),
    ("Earth Relics", "Реликвии с Земли"),
    ("Guardian Relic", "Реликвия Стражей"),
    ("Space Pioneer Relics", "Следы первопроходцев космоса"),
    ("Occupied Escape Pod", "Спасательная капсула с пассажиром"),
    ("Mollusc Spores", "Споры моллюска"),
    ("Guardian Orb", "Сфера Стражей"),
    ("Guardian Tablet", "Табличка Стражей"),
    ("Mysterious Idol", "Таинственный идол"),
    ("Tactical Data", "Тактические данные"),
    ("Thargoid Biological Matter", "Таргоидская биомасса"),
    ("Thargoid Bio-storage Capsule", "Таргоидская капсула для биоматериалов"),
    ("Thargoid Resin", "Таргоидская смола"),
    ("Thargoid Probe", "Таргоидский зонд"),
    ("Thargoid Sensor", "Таргоидский сенсор"),
    ("Thargoid Heart", "Таргоидское «сердце»"),
    ("Thargoid Link", "Таргоидское звено"),
    ("Pod Shell Tissue", "Ткань оболочки семянки"),
    ("Pod Tissue", "Ткань семянки"),
    ("Pod Core Tissue", "Ткань ядра семянки"),
    ("Trade Data", "Торговая информация"),
    ("Guardian Totem", "Тотем Стражей"),
    ("Guardian Urn", "Урна Стражей"),
    ("AI Relics", "Фрагменты ИИ"),
    ("Black Box", "Чёрный ящик"),
    ("Encrypted Correspondence", "Шифрованная переписка"),
    ("Guardian Casket", "Шкатулка Стражей"),
    ("Prototype Tech", "Экспериментальная техника"),
    ("Experimental Chemicals", "Экспериментальные химикаты"),
    ("Data Core", "Ядро данных"),
    ("Leather", "Кожа"),
    ("Natural Fabrics", "Натуральная ткань"),
    ("Conductive Fabrics", "Проводящая ткань"),
    ("Synthetic Fabrics", "Синтетическая ткань"),
    ("Military Grade Fabrics", "Ткани военного класса"),
    ("Auto Fabricators", "Автосинтезаторы"),
    ("Aquaponic Systems", "Аквапонные системы"),
    ("Medical Diagnostic Equipment", "Диагностическое медоборудование"),
    ("H.E. Suits", "Защитные костюмы"),
    ("Computer Components", "Компьютерные компоненты"),
    ("Structural Regulators", "Конструкционные регуляторы"),
    ("Bioreducing Lichen", "Лишайник-биоредуктор"),
    ("Micro Controllers", "Микроконтроллеры"),
    ("Animal Monitors", "Мониторы фауны"),
    ("Muon Imager", "Мюонное видеоустройство"),
    ("Nanobreakers", "Нанопрерыватели"),
    ("Resonating Separators", "Резонансные сепараторы"),
    ("Robotics", "Роботы"),
    ("Hardware Diagnostic Sensor", "Сенсор диагностики оборудования"),
    ("Land Enrichment Systems", "Системы обогащения почвы"),
    ("Telemetry Suite", "Телеметрический комплект"),
    ("Advanced Catalysers", "Улучшенные катализаторы"),
    ("Nerve Agents", "Агенты нервно-паралитического действия"),
    ("Explosives", "Взрывчатка"),
    ("Water", "Вода"),
    ("Hydrogen Fuel", "Водородное топливо"),
    ("Liquid Oxygen", "Жидкий кислород"),
    ("Mineral Oil", "Нефтепродукт"),
    ("Hydrogen Peroxide", "Пероксид водорода"),
    ("Pesticides", "Пестициды"),
    ("Synthetic Reagents", "Синтетические реагенты"),
    ("Agronomic Treatment", "Средство очистки почвы"),
    ("Surface Stabilisers", "Стабилизаторы поверхности"),
    ("Tritium", "Тритий"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
    ("Bauxite", "Боксит"),
])


PREFNAME_MAX_ROUTE_DISTANCE = "Макс. расстояние маршрута" #pi1
PREFNAME_MAX_STATION_DISTANCE = "Макс. расстояние до станции" #pi6
PREFNAME_MIN_SUPPLY = "Мин. поставки(0,100,500,1000,2500,5000,10000,50000)" # pi2
PREFNAME_MAX_PRICE_AGE = "Макс. возраст цены(1,2,3,7,30,180)" #pi3
PREFNAME_LANDING_PAD = "Мин. посадочная площадка(1/2/3)" #pi4
PREFNAME_INCLUDE_SURFACES = "Искать на планетах(0/1/2)" #pi5
PREFNAME_INCLUDE_CARIERS = "Использовать корабли носители(1/0)" #pi7
PREFNAME_MIN_CAPACITY = "Грузовместимость(720)" # pi10
PREFNAME_MIN_DEMAND = "Мин. спрос(0,100,500,1000,2500,5000,10000,50000)" # pi13

MAX_ROUTE_DISTANCE = tk.StringVar(value=config.get(PREFNAME_MAX_ROUTE_DISTANCE))
MIN_SUPPLY = tk.StringVar(value=config.get(PREFNAME_MIN_SUPPLY))
MAX_PRICE_AGE = tk.StringVar(value=config.get(PREFNAME_MAX_PRICE_AGE))
LANDING_PAD = tk.StringVar(value=config.get(PREFNAME_LANDING_PAD))
INCLUDE_SURFACES = tk.StringVar(value=config.get(PREFNAME_INCLUDE_SURFACES))
MAX_STATION_DISTANCE = tk.StringVar(value=config.get(PREFNAME_MAX_STATION_DISTANCE))
INCLUDE_CARIERS = tk.StringVar(value=config.get(PREFNAME_INCLUDE_CARIERS))
MIN_CAPACITY = tk.StringVar(value=config.get(PREFNAME_MIN_CAPACITY))
MIN_DEMAND = tk.StringVar(value=config.get(PREFNAME_MIN_DEMAND))



cmdr_data = None
ROUTES = []
ROUTE_INDEX = 0
ROUTES_COUNT = 0
SEARCH_THREAD = None
STAR_SYSTEM = None
STATION = None
IS_REQUESTING = False
HTTPS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36', 
    'Cache-Control': 'max-age=0',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br'
}
SEARCH_IMPORT = False
SEARCH_URL = "https://inara.cz/elite/market-traderoutes-search/"

class TradeRoute:
    def __init__(self, station_name, system_name, distance, resource, count, price, revenue, update):
        self.station_name = station_name
        self.system_name = system_name
        self.distance = distance
        self.resource = resource
        self.count = count
        self.price = price
        self.revenue = revenue
        self.update = update

class ETTC():
    searchImportBtn: None
    findBtn: None
    prevBtn: None
    nextBtn: None
    routesCountLabel: None
    plaseLabel: None
    place: None
    placeCopyBtn: None
    distanceLabel: None
    distance: None
    resourceLabel: None
    resource: None
    supplyLabel: None
    supply: None
    priceLabel: None
    price: None
    earnLabel: None
    earn: None
    updatedLabel: None
    updated: None
    status: None
    spacer: None

def setStateBtn(state):
    if this.labels.findBtn["state"] != state:
        this.labels.findBtn["state"] = state
        this.labels.prevBtn["state"] = state
        this.labels.nextBtn["state"] = state
        this.labels.placeCopyBtn["state"] = state

def setStatus(status):
    this.labels.status["text"] = status

def plugin_stop() -> None:
    this.LOG.write(f"[INFO] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Stop plugin")
    pass

def plugin_start():
    this.LOG.write(f"[INFO] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Start plugin")
    cmdr_data.last = None
    labels = ETTC()
    this.labels = labels

    if not MAX_ROUTE_DISTANCE.get():
        MAX_ROUTE_DISTANCE.set(str(DEFAULT_MAX_ROUTE_DISTANCE))
        config.set(PREFNAME_MAX_ROUTE_DISTANCE, str(DEFAULT_MAX_ROUTE_DISTANCE))
    if not MIN_SUPPLY.get():
        MIN_SUPPLY.set(str(DEFAULT_MIN_SUPPLY))
        config.set(PREFNAME_MIN_SUPPLY, str(DEFAULT_MIN_SUPPLY))
    if not MAX_PRICE_AGE.get():
        MAX_PRICE_AGE.set(str(DEFAULT_MAX_PRICE_AGE))
        config.set(PREFNAME_MAX_PRICE_AGE, str(DEFAULT_MAX_PRICE_AGE))
    if not LANDING_PAD.get():
        LANDING_PAD.set(str(DEFAULT_LANDING_PAD))
        config.set(PREFNAME_LANDING_PAD, str(DEFAULT_LANDING_PAD))
    if not INCLUDE_SURFACES.get():
        INCLUDE_SURFACES.set(str(DEFAULT_INCLUDE_SURFACES))
        config.set(PREFNAME_INCLUDE_SURFACES, str(DEFAULT_INCLUDE_SURFACES))
    if not MAX_STATION_DISTANCE.get():
        MAX_STATION_DISTANCE.set(str(DEFAULT_MAX_STATION_DISTANCE))
        config.set(PREFNAME_MAX_STATION_DISTANCE, str(DEFAULT_MAX_STATION_DISTANCE))
    if not INCLUDE_CARIERS.get():
        INCLUDE_CARIERS.set(str(DEFAULT_INCLUDE_SURFACES))
        config.set(PREFNAME_INCLUDE_CARIERS, str(DEFAULT_INCLUDE_SURFACES))
    if not MIN_CAPACITY.get():
        MIN_CAPACITY.set(str(DEFAULT_MIN_CAPACITY))
        config.set(PREFNAME_MIN_CAPACITY, str(DEFAULT_MIN_CAPACITY))
    if not MIN_DEMAND.get():
        MIN_DEMAND.set(str(DEFAULT_MIN_DEMAND))
        config.set(PREFNAME_MIN_DEMAND, str(DEFAULT_MIN_DEMAND))

    this.LOG.write(f"[INFO] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Load config plugin")
    return this.PLUGIN_NAME

def plugin_start3(plugin_dir: str) -> str:
    plugin_start()

def prefs_changed(cmdr, isbeta):
    this.LOG.write(f"[INFO] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Update prefs plugin")
    config.set(PREFNAME_MAX_ROUTE_DISTANCE, MAX_ROUTE_DISTANCE.get())
    config.set(PREFNAME_MIN_SUPPLY, MIN_SUPPLY.get())
    config.set(PREFNAME_MAX_PRICE_AGE, MAX_PRICE_AGE.get())
    config.set(PREFNAME_LANDING_PAD, LANDING_PAD.get())
    config.set(PREFNAME_INCLUDE_SURFACES, INCLUDE_SURFACES.get())
    config.set(PREFNAME_MAX_STATION_DISTANCE, MAX_STATION_DISTANCE.get())
    config.set(PREFNAME_INCLUDE_CARIERS, INCLUDE_CARIERS.get())
    config.set(PREFNAME_MIN_CAPACITY, MIN_CAPACITY.get())
    config.set(PREFNAME_MIN_DEMAND, MIN_DEMAND.get())

def journal_entry(cmdr, isbeta, system, station, entry, state):
    if this.STAR_SYSTEM is not system or this.STATION is not station:
        this.STAR_SYSTEM = system
        this.STATION = station

    if this.STATION == this.ROUTES[this.ROUTE_INDEX].station_name:
        if this.SEARCH_IMPORT:
            setStatus("Вы прибыли на станцию закупки товара!")
        else:
            setStatus("Вы прибыли на станцию продажи товара!")
        this.labels.place["text"] = f"Текущая станция"

    if station:
        if not this.IS_REQUESTING:
            setStateBtn(tk.NORMAL)
    else:
        setStateBtn(tk.DISABLED)

def plugin_app(parent: tk.Frame):
    plugin_app.parent = parent
    frame = tk.Frame(parent)
    # VARIABLES
    this.labels.searchImportBtn = tk.Button(frame, text="Находить маршруты импорта", state=tk.NORMAL, command=this.formatTradeInfo)
    this.labels.searchImportBtn.grid(row=0, column=0, columnspan=4, sticky="nsew")

    this.labels.findBtn = tk.Button(frame, text="Искать торговые маршруты", state=tk.DISABLED, command=this.getBestTrade)
    this.labels.findBtn.grid(row=1, column=0, columnspan=4, sticky="nsew")

    this.labels.status = tk.Label(frame, text="", justify=tk.CENTER)
    this.labels.status.grid(row=2, column=0, columnspan=3, sticky="nsew")

    this.labels.routesCountLabel = tk.Label(frame, text="Маршруты: 0/0", justify=tk.LEFT)
    this.labels.routesCountLabel.grid(row=3, column=1, columnspan=1, sticky=tk.W)

    this.labels.prevBtn = tk.Button(frame, text="⬅️", state=tk.DISABLED, command=this.getPrevRoute)
    this.labels.prevBtn.grid(row=3, column=0, pady=10, sticky=tk.W)

    this.labels.nextBtn = tk.Button(frame, text="➡️", state=tk.DISABLED, command=this.getNextRoute)
    this.labels.nextBtn.grid(row=3, column=3, pady=10, sticky=tk.W)

    this.labels.plaseLabel = tk.Label(frame, text="К станции:", justify=tk.LEFT)
    this.labels.plaseLabel.grid(row=4, column=0, sticky=tk.W)
    this.labels.place = hll(frame, text="")
    # https://inara.cz/elite/station/?search=[sysyem]+[station]
    this.labels.place["url"]= ""
    this.labels.place.grid(row=4, column=1, columnspan=1, sticky="NSEW")
    this.labels.placeCopyBtn = tk.Button(frame, text="🗎 Copy", state=tk.DISABLED, command=this.copyPlace)
    this.labels.placeCopyBtn.grid(row=4, column=2, sticky="nsew")


    this.labels.distanceLabel = tk.Label(frame, text="Дистанция:", justify=tk.LEFT)
    this.labels.distanceLabel.grid(row=5, column=0, sticky=tk.W)
    this.labels.distance = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.distance.grid(row=5, column=1, columnspan=2, sticky=tk.W)

    this.labels.resourceLabel = tk.Label(frame, text="Ресурс:", justify=tk.LEFT)
    this.labels.resourceLabel.grid(row=6, column=0, sticky=tk.W)
    this.labels.resource = hll(frame, text="")
    # https://www.google.com/search?q=elite+dangerous+[resource]
    this.labels.resource["url"]= ""
    this.labels.resource.grid(row=6, column=1, columnspan=2, sticky="NSEW")

    this.labels.supplyLabel = tk.Label(frame, text="Количество:", justify=tk.LEFT)
    this.labels.supplyLabel.grid(row=7, column=0, sticky=tk.W)
    this.labels.supply = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.supply.grid(row=7, column=1, columnspan=2, sticky=tk.W)

    this.labels.priceLabel = tk.Label(frame, text="Стоимость:", justify=tk.LEFT)
    this.labels.priceLabel.grid(row=8, column=0, sticky=tk.W)
    this.labels.price = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.price.grid(row=8, column=1, columnspan=2, sticky=tk.W)

    this.labels.earnLabel = tk.Label(frame, text="Прибыль:", justify=tk.LEFT)
    this.labels.earnLabel.grid(row=9, column=0, sticky=tk.W)
    this.labels.earn = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.earn.grid(row=9, column=1, columnspan=2, sticky=tk.W)

    this.labels.updatedLabel = tk.Label(frame, text="Обновлено:", justify=tk.LEFT)
    this.labels.updatedLabel.grid(row=10, column=0, sticky=tk.W)
    this.labels.updated = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.updated.grid(row=10, column=1, columnspan=2, sticky=tk.W)

    frame.columnconfigure(10, weight=1)

    this.labels.spacer = tk.Frame(frame)
    setStateBtn(tk.NORMAL)
    return frame

def plugin_prefs(parent, cmdr, isbeta):
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)


    nb.Label(frame, text=this.PREFNAME_MAX_ROUTE_DISTANCE).grid(padx=10, row=11, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MAX_ROUTE_DISTANCE).grid(padx=10, row=11, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MAX_STATION_DISTANCE).grid(padx=10, row=12, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MAX_STATION_DISTANCE).grid(padx=10, row=12, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MIN_CAPACITY).grid(padx=10, row=13, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MIN_CAPACITY).grid(padx=10, row=13, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MAX_PRICE_AGE).grid(padx=10, row=14, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MAX_PRICE_AGE).grid(padx=10, row=14, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_LANDING_PAD).grid(padx=10, row=15, sticky=tk.W)
    nb.Entry(frame, textvariable=this.LANDING_PAD).grid(padx=10, row=15, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MIN_SUPPLY).grid(padx=10, row=16, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MIN_SUPPLY).grid(padx=10, row=16, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MIN_DEMAND).grid(padx=10, row=17, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MIN_DEMAND).grid(padx=10, row=17, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_INCLUDE_SURFACES).grid(padx=10, row=18, sticky=tk.W)
    nb.Entry(frame, textvariable=this.INCLUDE_SURFACES).grid(padx=10, row=18, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_INCLUDE_CARIERS).grid(padx=10, row=19, sticky=tk.W)
    nb.Entry(frame, textvariable=this.INCLUDE_CARIERS).grid(padx=10, row=19, column=1, sticky=tk.EW)


    return frame

def cmdr_data(data, is_beta):
    this.STAR_SYSTEM = data['lastSystem']['name']
    this.STATION = data['lastStarport']['name']

def copyPlace():
    if len(this.ROUTES) > 0 and this.ROUTES[this.ROUTE_INDEX]:
        pyperclip.copy(f"{this.ROUTES[this.ROUTE_INDEX].station_name}")

def getBestTrade():
    if this.STAR_SYSTEM and (this.STATION is not None):
        setStateBtn(tk.DISABLED)
        this.IS_REQUESTING = True
        setStatus("Идет поиск пути...")
        this.SEARCH_THREAD = Thread(target=doRequest)
        this.SEARCH_THREAD.start()
    else:
        setStatus("Прилетите на станцию!")

def formatTradeInfo():
    this.SEARCH_IMPORT = not this.SEARCH_IMPORT
    if this.SEARCH_IMPORT == True:
        this.labels.searchImportBtn["text"] = 'Находить маршруты экспорта'
        this.labels.plaseLabel["text"] = 'От станции:'
    else:
        this.labels.searchImportBtn["text"] = 'Находить маршруты импорта'
        this.labels.plaseLabel["text"] = 'К станции:'

def getNextRoute():
    if this.ROUTE_INDEX < this.ROUTES_COUNT - 1:
        this.ROUTE_INDEX += 1
    renderRoute(this.ROUTES[this.ROUTE_INDEX])

def getPrevRoute():
    if this.ROUTE_INDEX > 0:
        this.ROUTE_INDEX -= 1
    renderRoute(this.ROUTES[this.ROUTE_INDEX])



def doRequest():
    try:
        pl1 = quote(this.STATION+" ["+this.STAR_SYSTEM+"]")

        url = this.SEARCH_URL+"?ps1="+str(pl1)+"&ps2=&pi1="+str(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))+"&pi3="+str(config.get(this.PREFNAME_MAX_PRICE_AGE))+"&pi4="+str(config.get(this.PREFNAME_LANDING_PAD))+"&pi6="+str(config.get(this.PREFNAME_MAX_STATION_DISTANCE))+"&pi5="+str(config.get(this.PREFNAME_INCLUDE_SURFACES))+"&pi7="+str(config.get(this.PREFNAME_INCLUDE_CARIERS))+"&ps3=&pi2="+str(config.get(this.PREFNAME_MIN_SUPPLY))+"&pi13="+str(config.get(this.PREFNAME_MIN_DEMAND))+"&pi10="+str(config.get(this.PREFNAME_MIN_CAPACITY))+"&pi8=0"
        this.LOG.write(f"[INFO] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Search routes from: {url}")
        response = requests.get(url=url, headers=this.HTTPS_HEADERS, timeout=10)

        if response.status_code != requests.codes.ok:
            setStatus("Ошибка: error code." + str(response.status_code))

        this.IS_REQUESTING = False

        if response.text:
            parseData(response.text)
            renderRoute(this.ROUTES[0])
            setStatus(f"Пути найдены!")
        else:
            this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Catch request error")
            setStatus("Ошибка: невозможно найти маршруты.")
            setStateBtn(tk.NORMAL)
    except Exception as e:
        # Проверяем, содержит ли ошибка 'NoneType' object is not callable
        if "'NoneType' object is not callable" in str(e):
            setStatus("Маршруты от станции отсутсвуют")
            setStateBtn(tk.NORMAL)
        else:
            setStatus(f"Ошибка: {e}")
            this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] {e}")
            this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] {traceback.format_exc()}")
            setStateBtn(tk.NORMAL)

def parseData(html):
    soup = BeautifulSoup(html, 'html.parser')
    this.ROUTES = []
    route_type = 1
    station_elem_path = "div:nth-of-type(2) > a > span.standardcase.standardcolor.nowrap"
    system_elem_path = "div:nth-of-type(2) > a > span.uppercase.nowrap"
    distance_path = "div:nth-of-type(10) > div:nth-of-type(1) > div:nth-of-type(1) > div.itempairvalue.itempairvalueright > span.bigger"
    recource_path = ".traderouteboxtoright > div:nth-of-type(1) > .itempairvalue > a > span.avoidwrap"
    count_path = ".traderouteboxtoright > div:nth-of-type(3) > .itempairvalue"
    price_path = ".traderouteboxtoright > div:nth-of-type(2) > .itempairvalue"
    revenue_path = "div:nth-of-type(10) > .traderouteboxprofit > div:nth-of-type(3) > .itempairvalue.itempairvalueright"
    update_path = "div:nth-of-type(10) > div:nth-of-type(1) > div:nth-of-type(2) > .itempairvalue.itempairvalueright"

    if this.SEARCH_IMPORT == 1:
        route_type = 2
        recource_path = ".traderouteboxfromright > div:nth-of-type(1) > .itempairvalue > a > span.avoidwrap"
        count_path = ".traderouteboxtoleft > div:nth-of-type(3) > .itempairvalue"
        price_path = ".traderouteboxtoleft > div:nth-of-type(2) > .itempairvalue"
        
    
    for block in soup.find_all("div", class_="mainblock traderoutebox taggeditem", attrs={"data-tags": f'["{route_type}"]'}):
        try:
            # Извлечение имени станции
            station_elem = block.select_one(station_elem_path)
            station_text = station_elem.text
            station_name = station_text.split(" | ")[0].strip()
            if station_elem.find("span"):
                station_name += " " + station_elem.find("span").text.strip()
            
            # Извлечение имени системы
            system_name = block.select_one(system_elem_path).text.strip()
            
            # Дистанция
            distance = block.select_one(distance_path).text.strip()
            
            # Ресурс
            resource = block.select_one(recource_path).text.strip()
            
            # Количество
            count = block.select_one(count_path).text.strip()
            count = re.sub(r",", "", count).split("\ue84e︎")[0]  # Убираем запятые
            
            # Цена
            price = block.select_one(price_path).text.strip()
            price = re.sub(r",", "", price).split(" ")[0]
            
            # Доход
            revenue = block.select_one(revenue_path).text.strip()
            revenue = re.sub(r",", "", revenue).split(" ")[0]
            
            # Дата обновления
            update = block.select_one(update_path).text.strip()
            update = re.sub(r"minutes", "минут", update)
            update = re.sub(r"minute", "минуты", update)
            update = re.sub(r"hours", "часов", update)
            update = re.sub(r"hour", "час", update)
            update = re.sub(r"days", "дней", update)
            update = re.sub(r"day", "день", update)
            update = re.sub(r"seconds", "секунд", update)
            update = re.sub(r"second", "секунду", update)
            update = re.sub(r"ago", "назад", update)

            this.ROUTES.append(TradeRoute(station_name, system_name, distance, resource, count, price, revenue, update))
        except AttributeError:
            continue  # Пропускаем элементы с неполными данными

    this.ROUTE_INDEX = 0
    this.ROUTES_COUNT = len(this.ROUTES)

def renderRoute(route):
    try:
        this.labels.routesCountLabel["text"] = f"Маршруты: {this.ROUTE_INDEX+1}/{this.ROUTES_COUNT}"
        this.labels.place["text"] = f"{route.station_name} [{route.system_name}]"
        this.labels.place["url"] = f"https://inara.cz/elite/station/?search={quote(route.system_name + '[' + route.station_name + ']')}"
        this.labels.distance["text"] = route.distance
        this.labels.resource["text"] = ITEMS.get(route.resource, route.resource)
        if route.resource in ITEMS:
            this.labels.resource["url"] = f"https://elite-dangerous.fandom.com/ru/wiki/{quote(ITEMS.get(route.resource, route.resource))}"
        else:
            this.labels.resource["url"] = f"https://elite-dangerous.fandom.com/wiki/{quote(route.resource)}"
        this.labels.supply["text"] = f"{int(route.count):,} на складе"
        this.labels.price["text"] = f"{int(route.price):,} Кред./шт"
        this.labels.earn["text"] = f"{int(route.revenue):,} Кред."
        this.labels.updated["text"] = route.update
        setStateBtn(tk.NORMAL)
    except Exception as e:
        this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] {e}")
        this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] {traceback.format_exc()}")
