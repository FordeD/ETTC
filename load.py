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
from collections import defaultdict
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
PLUGIN_VERSION = "1.3.2.2"

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
DEFAULT_MIN_DEMAND_SEARCH = 0
DEFAULT_DEBUG_MODE = 0
DEFAULT_ADD_ROUTE_DISTANCE = 5

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
PREFNAME_ADD_ROUTE_DISTANCE = "Шаг изменения маршрута"
PREFNAME_MAX_STATION_DISTANCE = "Макс. расстояние до станции" #pi6
PREFNAME_MIN_SUPPLY = "Мин. поставки(0,100,500,1000,2500,5000,10000,50000)" # pi2
PREFNAME_MAX_PRICE_AGE = "Макс. время обновления(кол-во часов)" #pi3
PREFNAME_LANDING_PAD = "Мин. посадочная площадка(1/2/3)" #pi4
PREFNAME_INCLUDE_SURFACES = "Искать на планетах(0/1/2)" #pi5
PREFNAME_INCLUDE_CARIERS = "Использовать корабли носители(0/1)" #pi7
PREFNAME_MIN_CAPACITY = "Грузовместимость(720)" # pi10
PREFNAME_MIN_DEMAND = "Мин. спрос(0,100,500,1000,2500,5000,10000,50000)" # pi13
PREFNAME_MIN_DEMAND_SEARCH = "Мин. качество спроса (0/1/2/3)"
PREFNAME_DEBUG_MODE = "Включить отладку(0/1)"

MAX_ROUTE_DISTANCE = tk.StringVar(value=config.get(PREFNAME_MAX_ROUTE_DISTANCE))
ADD_ROUTE_DISTANCE = tk.StringVar(value=config.get(PREFNAME_ADD_ROUTE_DISTANCE))
MIN_SUPPLY = tk.StringVar(value=config.get(PREFNAME_MIN_SUPPLY))
MAX_PRICE_AGE = tk.StringVar(value=config.get(PREFNAME_MAX_PRICE_AGE))
LANDING_PAD = tk.StringVar(value=config.get(PREFNAME_LANDING_PAD))
INCLUDE_SURFACES = tk.StringVar(value=config.get(PREFNAME_INCLUDE_SURFACES))
MAX_STATION_DISTANCE = tk.StringVar(value=config.get(PREFNAME_MAX_STATION_DISTANCE))
INCLUDE_CARIERS = tk.StringVar(value=config.get(PREFNAME_INCLUDE_CARIERS))
MIN_CAPACITY = tk.StringVar(value=config.get(PREFNAME_MIN_CAPACITY))
MIN_DEMAND = tk.StringVar(value=config.get(PREFNAME_MIN_DEMAND))
MIN_DEMAND_SEARCH = tk.StringVar(value=config.get(PREFNAME_MIN_DEMAND_SEARCH))
DEBUG_MODE = tk.StringVar(value=config.get(PREFNAME_DEBUG_MODE))

cmdr_data = None
TIMED_ROUTE_DISTANCE = 0
ROUTES = defaultdict(list)
STATIONS = []
ROUTE_INDEX = 0
STATION_INDEX = 0
ROUTES_COUNT = defaultdict(list)
STATIONS_COUNT = 0
SEARCH_THREAD = None
STAR_SYSTEM = None
STATION = None
# Для тестов
# STAR_SYSTEM = "Aornum"
# STATION = "Agassiz City"
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
    def __init__(self, station_name, system_name, distance, resource, count, price, revenue, update, sell_percent, sell_per_item, demand, station_distance):
        self.station_name = station_name
        self.system_name = system_name
        self.distance = distance
        self.station_distance = station_distance
        self.resource = resource
        self.count = count
        self.price = price
        self.revenue = revenue
        self.update = update
        self.sell_percent = sell_percent
        self.sell_per_item = sell_per_item
        self.demand = demand

class ETTC():
    searchImportLabel: None
    searchImportBtn: None
    findBtn: None
    decDistBtn: None
    addDistBtn: None
    distLabel: None
    prevStationBtn: None
    nextStationBtn: None
    prevItemBtn: None
    nextItemBtn: None
    stationsCountLabel: None
    itemsCountLabel: None
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
    demandLabel: None
    demand: None
    earnLabel: None
    earn: None
    detailEarn: None
    updatedLabel: None
    updated: None
    status: None
    spacer: None

def setStateBtn(state):
    if this.labels.findBtn["state"] != state:
        this.labels.findBtn["state"] = state
        this.labels.prevStationBtn["state"] = state
        this.labels.nextStationBtn["state"] = state
        this.labels.prevItemBtn["state"] = state
        this.labels.nextItemBtn["state"] = state
        this.labels.placeCopyBtn["state"] = state
        this.labels.decDistBtn["state"] = state
        this.labels.addDistBtn["state"] = state

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
    if not ADD_ROUTE_DISTANCE.get():
        ADD_ROUTE_DISTANCE.set(str(DEFAULT_ADD_ROUTE_DISTANCE))
        config.set(PREFNAME_ADD_ROUTE_DISTANCE, str(DEFAULT_ADD_ROUTE_DISTANCE))
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
    if not MIN_DEMAND_SEARCH.get():
        MIN_DEMAND_SEARCH.set(str(DEFAULT_MIN_DEMAND_SEARCH))
        config.set(PREFNAME_MIN_DEMAND_SEARCH, str(DEFAULT_MIN_DEMAND_SEARCH))
    if not DEBUG_MODE.get():
        DEBUG_MODE.set(str(DEFAULT_DEBUG_MODE))
        config.set(PREFNAME_DEBUG_MODE, str(DEFAULT_DEBUG_MODE))

    this.LOG.write(f"[INFO] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Load config plugin")
    return this.PLUGIN_NAME

def plugin_start3(plugin_dir: str) -> str:
    plugin_start()

def prefs_changed(cmdr, isbeta):
    oldDistance = int(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))
    oldStep = int(config.get(this.PREFNAME_ADD_ROUTE_DISTANCE))
    this.LOG.write(f"[INFO] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Update prefs plugin")
    config.set(PREFNAME_MAX_ROUTE_DISTANCE, MAX_ROUTE_DISTANCE.get())
    config.set(PREFNAME_ADD_ROUTE_DISTANCE, ADD_ROUTE_DISTANCE.get())
    config.set(PREFNAME_MIN_SUPPLY, MIN_SUPPLY.get())
    config.set(PREFNAME_MAX_PRICE_AGE, MAX_PRICE_AGE.get())
    config.set(PREFNAME_LANDING_PAD, LANDING_PAD.get())
    config.set(PREFNAME_INCLUDE_SURFACES, INCLUDE_SURFACES.get())
    config.set(PREFNAME_MAX_STATION_DISTANCE, MAX_STATION_DISTANCE.get())
    config.set(PREFNAME_INCLUDE_CARIERS, INCLUDE_CARIERS.get())
    config.set(PREFNAME_MIN_CAPACITY, MIN_CAPACITY.get())
    config.set(PREFNAME_MIN_DEMAND, MIN_DEMAND.get())
    config.set(PREFNAME_MIN_DEMAND_SEARCH, MIN_DEMAND_SEARCH.get())
    config.set(PREFNAME_DEBUG_MODE, DEBUG_MODE.get())

    newDistance = int(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))
    newStep = int(config.get(this.PREFNAME_ADD_ROUTE_DISTANCE))
    if this.TIMED_ROUTE_DISTANCE > 0:
        this.TIMED_ROUTE_DISTANCE -= oldDistance
        this.TIMED_ROUTE_DISTANCE += newDistance
    else:
       this.TIMED_ROUTE_DISTANCE = newDistance

    if oldStep - newStep != 0:
        this.TIMED_ROUTE_DISTANCE = newDistance

def journal_entry(cmdr, isbeta, system, station, entry, state):
    if system and station and (this.STAR_SYSTEM is not system or this.STATION is not station):
        this.STAR_SYSTEM = system
        this.STATION = station

    if this.STATION == this.ROUTES[this.ROUTE_INDEX].station_name:
        if this.SEARCH_IMPORT:
            setStatus("Вы прибыли на станцию закупки товара!")
        else:
            setStatus("Вы прибыли на станцию продажи товара!")
        this.labels.place["text"] = f"Текущая станция"

    if this.STATION:
        if not this.IS_REQUESTING:
            setStateBtn(tk.NORMAL)
    else:
        setStateBtn(tk.DISABLED)

def plugin_app(parent: tk.Frame):
    plugin_app.parent = parent
    frame = tk.Frame(parent)

    distance = str(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))
    if this.TIMED_ROUTE_DISTANCE > 0:
        distance = str(this.TIMED_ROUTE_DISTANCE)

    # VARIABLES
    this.labels.searchImportBtn = tk.Checkbutton(frame, text="", variable=SEARCH_IMPORT, justify=tk.RIGHT, state=tk.NORMAL, onvalue=True, offvalue=False, command=this.formatTradeInfo)
    this.labels.searchImportBtn.grid(row=0, column=0, columnspan=1, sticky=tk.E)
    this.labels.searchImportLabel = tk.Label(frame, text="Искать импорт", justify=tk.LEFT)
    this.labels.searchImportLabel.grid(row=0, column=1, columnspan=1, sticky=tk.W)

    this.labels.findBtn = tk.Button(frame, text="Искать", state=tk.DISABLED, command=this.getBestTrade)
    this.labels.findBtn.grid(row=1, column=0, columnspan=2, sticky="nsew")
    this.labels.decDistBtn = tk.Button(frame, text="⬅️", state=tk.DISABLED, command=this.decDist)
    this.labels.decDistBtn.grid(row=1, column=3, sticky="nsew")
    this.labels.distLabel = tk.Label(frame, text=f"{distance} Св.л", justify=tk.LEFT)
    this.labels.distLabel.grid(row=1, column=4, columnspan=1, sticky="nsew")
    this.labels.addDistBtn = tk.Button(frame, text="➡️", state=tk.DISABLED, command=this.addDist)
    this.labels.addDistBtn.grid(row=1, column=5, columnspan=1, sticky="nsew")

    this.labels.status = tk.Label(frame, text="", justify=tk.CENTER)
    this.labels.status.grid(row=2, column=0, columnspan=6, sticky="nsew")

    this.labels.distanceLabel = tk.Label(frame, text="Дистанция:", justify=tk.LEFT)
    this.labels.distanceLabel.grid(row=4, column=0, sticky=tk.E)
    this.labels.distance = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.distance.grid(row=4, column=1, columnspan=1, sticky=tk.W)
    this.labels.prevStationBtn = tk.Button(frame, text="⬅️", state=tk.DISABLED, command=this.getPrevStation)
    this.labels.prevStationBtn.grid(row=4, column=3, columnspan=1, pady=10, sticky="nsew")
    this.labels.stationsCountLabel = tk.Label(frame, text="0/0", justify=tk.LEFT)
    this.labels.stationsCountLabel.grid(row=4, column=4, columnspan=1, sticky="nsew")
    this.labels.nextStationBtn = tk.Button(frame, text="➡️", state=tk.DISABLED, command=this.getNextStation)
    this.labels.nextStationBtn.grid(row=4, column=5, columnspan=1, pady=10, sticky="nsew")


    this.labels.plaseLabel = tk.Label(frame, text="К станции:", justify=tk.LEFT)
    this.labels.plaseLabel.grid(row=5, column=0, sticky=tk.E)
    this.labels.place = hll(frame, text="", justify=tk.LEFT)
    # https://inara.cz/elite/station/?search=[sysyem]+[station]
    this.labels.place["url"]= ""
    this.labels.place.grid(row=5, column=1, columnspan=5, sticky="nsew")
    this.labels.placeCopyBtn = tk.Button(frame, text="🗎 Copy", state=tk.DISABLED, command=this.copyPlace)
    this.labels.placeCopyBtn.grid(row=5, column=3, columnspan=3, pady=10, sticky="nsew")

    this.labels.resourceLabel = tk.Label(frame, text="Товар:", justify=tk.LEFT)
    this.labels.resourceLabel.grid(row=6, column=0, sticky=tk.E)
    this.labels.resource = hll(frame, text="", justify=tk.RIGHT)
    this.labels.resource["url"]= ""
    this.labels.resource.grid(row=6, column=1, columnspan=1, sticky=tk.E)
    this.labels.demand = tk.Label(frame, text="📶", justify=tk.LEFT, fg="#636362")
    this.labels.demand.grid(row=6, column=2, columnspan=1, sticky=tk.W)
    this.labels.prevItemBtn = tk.Button(frame, text="⬅️", state=tk.DISABLED, command=this.getPrevItem)
    this.labels.prevItemBtn.grid(row=6, column=3, pady=10, sticky=tk.W)
    this.labels.itemsCountLabel = tk.Label(frame, text="0/0", justify=tk.LEFT)
    this.labels.itemsCountLabel.grid(row=6, column=4, sticky="nsew")
    this.labels.nextItemBtn = tk.Button(frame, text="➡️", state=tk.DISABLED, command=this.getNextItem)
    this.labels.nextItemBtn.grid(row=6, column=5, pady=10, sticky=tk.W)

    this.labels.supplyLabel = tk.Label(frame, text="Количество:", justify=tk.LEFT)
    this.labels.supplyLabel.grid(row=7, column=0, sticky=tk.E)
    this.labels.supply = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.supply.grid(row=7, column=1, columnspan=1, sticky=tk.W)
    this.labels.price = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.price.grid(row=7, column=2, columnspan=1, sticky=tk.W)

    this.labels.earnLabel = tk.Label(frame, text="Прибыль:", justify=tk.LEFT)
    this.labels.earnLabel.grid(row=10, column=0, sticky=tk.E)
    this.labels.earn = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.earn.grid(row=10, column=1, columnspan=1, sticky=tk.W)

    this.labels.detailEarn = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.detailEarn.grid(row=11, column=1, columnspan=2, sticky=tk.W)

    this.labels.updatedLabel = tk.Label(frame, text="Обновлено:", justify=tk.LEFT)
    this.labels.updatedLabel.grid(row=12, column=0, sticky=tk.E)
    this.labels.updated = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.updated.grid(row=12, column=1, columnspan=2, sticky=tk.W)

    # frame.columnconfigure(12, weight=1)

    this.labels.spacer = tk.Frame(frame)
    setStateBtn(tk.NORMAL)
    return frame

def plugin_prefs(parent, cmdr, isbeta):
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)


    nb.Label(frame, text=this.PREFNAME_MAX_ROUTE_DISTANCE).grid(padx=10, row=11, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MAX_ROUTE_DISTANCE).grid(padx=10, row=11, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_ADD_ROUTE_DISTANCE).grid(padx=10, row=12, sticky=tk.W)
    nb.Entry(frame, textvariable=this.ADD_ROUTE_DISTANCE).grid(padx=10, row=12, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MAX_STATION_DISTANCE).grid(padx=10, row=13, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MAX_STATION_DISTANCE).grid(padx=10, row=13, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MIN_CAPACITY).grid(padx=10, row=14, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MIN_CAPACITY).grid(padx=10, row=14, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MAX_PRICE_AGE).grid(padx=10, row=15, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MAX_PRICE_AGE).grid(padx=10, row=15, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_LANDING_PAD).grid(padx=10, row=16, sticky=tk.W)
    nb.Entry(frame, textvariable=this.LANDING_PAD).grid(padx=10, row=16, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MIN_SUPPLY).grid(padx=10, row=17, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MIN_SUPPLY).grid(padx=10, row=17, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MIN_DEMAND).grid(padx=10, row=18, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MIN_DEMAND).grid(padx=10, row=18, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_MIN_DEMAND_SEARCH).grid(padx=10, row=19, sticky=tk.W)
    nb.Entry(frame, textvariable=this.MIN_DEMAND_SEARCH).grid(padx=10, row=19, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_INCLUDE_SURFACES).grid(padx=10, row=20, sticky=tk.W)
    nb.Entry(frame, textvariable=this.INCLUDE_SURFACES).grid(padx=10, row=20, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_INCLUDE_CARIERS).grid(padx=10, row=21, sticky=tk.W)
    nb.Entry(frame, textvariable=this.INCLUDE_CARIERS).grid(padx=10, row=21, column=1, sticky=tk.EW)

    nb.Label(frame, text=this.PREFNAME_DEBUG_MODE).grid(padx=10, row=22, sticky=tk.W)
    nb.Entry(frame, textvariable=this.DEBUG_MODE).grid(padx=10, row=22, column=1, sticky=tk.EW)

    nb.Label(frame, text="Помощь:").grid(padx=10, row=24, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Макс. расстояние маршрута - максимальное расстояние в единицах Ly (световых лет) от системы").grid(padx=10, row=25, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Шаг изменения маршрута - Шаг увеличения или уменьшения в единицах Ly (световых лет) от системы по кнопкам").grid(padx=10, row=25, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Макс. расстояние до станции - максимальное расстояние в световых секундах до станции к которой будет проложен маршрут").grid(padx=10, row=26, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Грузоподъемность - количество места в тоннах для покупки и продажи товаров (учитывается для рассчета прибыли)").grid(padx=10, row=27, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Макс. время обновления - количество часов с последнего обновления (количество часов)").grid(padx=10, row=28, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Мин. посадочная площадка - размер посадочной площадки станции где нужно продать товар (1-малая, 2-средняя, 3-большая)").grid(padx=10, row=29, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Мин. поставки - минимальный объем покупаемого товара в единицах (0-любое, 100,500,1000,2500,5000,10000,50000)").grid(padx=10, row=30, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Мин. спрос - минимальное количество продаваемого товара в единицах (0-любое, 100,500,1000,2500,5000,10000,50000)").grid(padx=10, row=31, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Мин. качество спроса - минимальное качество продаваемого товара(0-любое, 1-низкий, 2-стандарт, 3-высокий)").grid(padx=10, row=32, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Искать на планетах - нужен ли поиск торговых маршрутов на планетах (0 - Нет, 1 - Да, 2 - Да + станции Одиссеи)").grid(padx=10, row=33, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Искать корабли носители - нужен ли поиск торговых маршрутов через корабли-носители (0 - Нет, 1 - Да)").grid(padx=10, row=34, columnspan=2, sticky=tk.W)
    nb.Label(frame, text="Включить отладку - включить режим отладки в логах (0 - нет, 1 - да)").grid(padx=10, row=35, columnspan=2, sticky=tk.W)

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
        this.labels.plaseLabel["text"] = 'От станции:'
    else:
        this.labels.plaseLabel["text"] = 'К станции:'

def getNextStation():
    if this.STATION_INDEX < this.STATIONS_COUNT - 1:
        this.STATION_INDEX += 1
        this.ROUTE_INDEX = 0
    station = this.STATIONS[this.STATION_INDEX]
    renderRoute(this.ROUTES[station][this.ROUTE_INDEX])

def getPrevStation():
    if this.STATION_INDEX > 0:
        this.STATION_INDEX -= 1
        this.ROUTE_INDEX = 0
    station = this.STATIONS[this.STATION_INDEX]
    renderRoute(this.ROUTES[station][this.ROUTE_INDEX])

def getNextItem():
    if this.ROUTE_INDEX < this.ROUTES_COUNT[this.STATIONS[this.STATION_INDEX]] - 1:
        this.ROUTE_INDEX += 1
    station = this.STATIONS[this.STATION_INDEX]
    renderRoute(this.ROUTES[station][this.ROUTE_INDEX])

def getPrevItem():
    if this.ROUTE_INDEX > 0:
        this.ROUTE_INDEX -= 1
    station = this.STATIONS[this.STATION_INDEX]
    renderRoute(this.ROUTES[station][this.ROUTE_INDEX])

def decDist():
    if this.TIMED_ROUTE_DISTANCE == 0:
        this.TIMED_ROUTE_DISTANCE = int(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))
    if this.TIMED_ROUTE_DISTANCE - int(config.get(PREFNAME_ADD_ROUTE_DISTANCE)) > 0:
        this.TIMED_ROUTE_DISTANCE -= int(config.get(PREFNAME_ADD_ROUTE_DISTANCE))
    this.labels.distLabel["text"] = f"{this.TIMED_ROUTE_DISTANCE} Св.л"

def addDist():
    if this.TIMED_ROUTE_DISTANCE == 0:
        this.TIMED_ROUTE_DISTANCE = int(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))
    this.TIMED_ROUTE_DISTANCE += int(config.get(PREFNAME_ADD_ROUTE_DISTANCE))
    this.labels.distLabel["text"] = f"{this.TIMED_ROUTE_DISTANCE} Св.л"

def doRequest():
    try:
        pl1 = quote(this.STATION+" ["+this.STAR_SYSTEM+"]")
        # Переворачивание значений для фильтра по кораблям-носителям
        cariers = 1 - int(config.get(this.PREFNAME_INCLUDE_CARIERS))
        # Переворачивание значений для фильтра по наземным станциям
        surface = int(config.get(this.PREFNAME_INCLUDE_SURFACES))
        match surface:
            case 0:
                surface = 1
            case 1:
                surface = 2
            case 2:
                surface = 0
        distance = str(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))
        if this.TIMED_ROUTE_DISTANCE > 0:
            distance = str(this.TIMED_ROUTE_DISTANCE)
        url = this.SEARCH_URL+"?ps1="+str(pl1)+"&ps2=&pi1="+str(distance)+"&pi3="+str(config.get(this.PREFNAME_MAX_PRICE_AGE))+"&pi4="+str(config.get(this.PREFNAME_LANDING_PAD))+"&pi6="+str(config.get(this.PREFNAME_MAX_STATION_DISTANCE))+"&pi5="+str(config.get(this.PREFNAME_INCLUDE_SURFACES))+"&pi7="+str(cariers)+"&ps3=&pi2="+str(config.get(this.PREFNAME_MIN_SUPPLY))+"&pi13="+str(config.get(this.PREFNAME_MIN_DEMAND))+"&pi10="+str(config.get(this.PREFNAME_MIN_CAPACITY))+"&pi8=0"
        this.LOG.write(f"[INFO] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Search routes from: {url}")
        response = requests.get(url=url, headers=this.HTTPS_HEADERS, timeout=10)

        if response.status_code != requests.codes.ok:
            setStatus("Ошибка: error code." + str(response.status_code))

        this.IS_REQUESTING = False

        if response.text:
            parseData(response.text)
            if this.STATIONS_COUNT > 0:
                if this.ROUTES_COUNT[this.STATIONS[this.STATION_INDEX]] > 0:
                    renderRoute(this.ROUTES[this.STATIONS[this.STATION_INDEX]][0])
                    if this.TIMED_ROUTE_DISTANCE > 0:
                        setStatus(f"Пути найдены на дистанции {this.TIMED_ROUTE_DISTANCE} Св.л!")
                    else:
                        setStatus(f"Пути найдены!")
                else:
                    this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Search empty routes, {pl1} - Import: {this.SEARCH_IMPORT}")
                    if this.SEARCH_IMPORT == 0:
                        setStatus(f"От станции нет путей!")
                    else:
                        setStatus(f"На станцию нет путей!")
            else:
                this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Search empty routes, {pl1} - Import: {this.SEARCH_IMPORT}")
                if this.SEARCH_IMPORT == 0:
                    setStatus(f"От станции нет путей!")
                else:
                    setStatus(f"На станцию нет путей!")
            setStateBtn(tk.NORMAL)
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
    this.ROUTES.clear()
    this.STATIONS.clear()
    this.ROUTES_COUNT.clear()
    timed_routes = defaultdict(list)
    route_type = 1
    station_elem_path = "div:nth-of-type(2) > a > span.standardcase.standardcolor.nowrap"
    system_elem_path = "div:nth-of-type(2) > a > span.uppercase.nowrap"
    distance_path = "div:nth-of-type(10) > div:nth-of-type(1) > div:nth-of-type(1) > div.itempairvalue.itempairvalueright > span.bigger"
    station_distance_path = "div:nth-of-type(7) > .itempaircontainer > .itempairvalue > .minor"
    recource_path = ".traderouteboxtoright > div:nth-of-type(1) > .itempairvalue > a > span.avoidwrap"
    count_path = ".traderouteboxtoright > div:nth-of-type(3) > .itempairvalue"
    price_path = ".traderouteboxtoright > div:nth-of-type(2) > .itempairvalue"
    revenue_path = "div:nth-of-type(10) > .traderouteboxprofit > div:nth-of-type(3) > .itempairvalue.itempairvalueright"
    update_path = "div:nth-of-type(10) > div:nth-of-type(1) > div:nth-of-type(2) > .itempairvalue.itempairvalueright"
    sell_percent_path = "div:nth-of-type(10) > .traderouteboxprofit > div:nth-of-type(2) > .itempairvalue.itempairvalueright"
    sell_per_item_path = "div:nth-of-type(10) > .traderouteboxprofit > div:nth-of-type(1) > .itempairvalue.itempairvalueright"
    demand_path = ".traderouteboxfromleft > div:nth-of-type(3) > .itempairvalue"

    if this.SEARCH_IMPORT == 1:
        route_type = 2
        recource_path = ".traderouteboxfromright > div:nth-of-type(1) > .itempairvalue > a > span.avoidwrap"
        count_path = ".traderouteboxtoleft > div:nth-of-type(3) > .itempairvalue"
        price_path = ".traderouteboxtoleft > div:nth-of-type(2) > .itempairvalue"
        demand_path = ".traderouteboxfromright > div:nth-of-type(3) > .itempairvalue"
        station_distance_path = "div:nth-of-type(4) > .itempaircontainer > .itempairvalue > .minor"
        
    
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
            distance = re.sub(r"Ly", "Св.л", distance)

            # Дистанция станции
            station_distance = block.select_one(station_distance_path).text.strip()
            station_distance = re.sub(r",", "", station_distance)  # Убираем запятые
            station_distance = re.sub(r"-", "0", station_distance)  # Убираем неизвестное
            station_distance = re.sub(r'\D', '', station_distance) # Убираем спец. символ ︎
            
            # Ресурс
            resource = block.select_one(recource_path).text.strip()
            
            # Количество
            count = block.select_one(count_path).text.strip()
            count = re.sub(r",", "", count)  # Убираем запятые
            count = re.sub(r'\D', '', count) # Убираем спец. символ ︎

            # helpmarkleft - нет спроса
            # supplydemandicon0 - низкий
            # отсутсвует 
            # supplydemandicon3 - высокий
            demandText = str(block.select_one(demand_path))
            demand = 2
            match demandText:
                case t if "helpmarkleft" in t:
                    demand = 0
                case t if "supplydemandicon0" in t:
                    demand = 1
                case t if "supplydemandicon3" in t:
                    demand = 3
                case _:
                    demand = 2

            # Цена
            price = block.select_one(price_path).text.strip()
            price = re.sub(r",", "", price)
            price = re.sub(r'\D', '', price)

            sell_per_item = block.select_one(sell_per_item_path).text.strip() 
            sell_per_item = re.sub(r",", "", sell_per_item)  # Убираем запятые
            sell_per_item = re.sub(r'\D', '', sell_per_item) # Убираем спец. символ ︎

            sell_percent = block.select_one(sell_percent_path).text.strip()
            sell_percent = re.sub(r",", "", sell_percent)  # Убираем запятые
            sell_percent = re.sub(r'\D', '', sell_percent) # Убираем спец. символ ︎
            
            # Доход
            revenue = block.select_one(revenue_path).text.strip()
            revenue = re.sub(r",", "", revenue)
            revenue = re.sub(r'\D', '', revenue)
            
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
            update = re.sub(r"now", "сейчас", update)

            if int(config.get(this.PREFNAME_DEBUG_MODE)):
                this.LOG.write(f"[DEBUG] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Result block: {station_name}, {system_name}, {distance}, {station_distance}, {resource}, {count}, {price}, {revenue}, {update}, {sell_percent}, {sell_per_item}, {demand}")
            
            timed_route = TradeRoute(station_name, system_name, distance, resource, count, price, revenue, update, sell_percent, sell_per_item, demand, station_distance)
            timed_routes[station_name].append(timed_route)
            # timed_routes.append(TradeRoute(station_name, system_name, distance, resource, count, price, revenue, update, sell_percent, sell_per_item, demand, station_distance))
        except Exception as e:
            this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] {e}")
            this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] {traceback.format_exc()}")
        # except AttributeError:
        #     continue  # Пропускаем элементы с неполными данными
    
    min_demand_filter = int(config.get(this.PREFNAME_MIN_DEMAND_SEARCH))

    this.STATIONS = list(timed_routes.keys())
    this.ROUTE_INDEX = 0
    this.STATION_INDEX = 0
    this.STATIONS_COUNT = len(this.STATIONS)

    if min_demand_filter > 0:
        for station in this.STATIONS:
            tempRoutes = [route for route in timed_routes[station] if route.demand >= min_demand_filter]
            if len(tempRoutes) > 0:
                this.ROUTES[station] = tempRoutes
    else:
        this.ROUTES = timed_routes

    for station in this.STATIONS:
            if len(this.ROUTES[station]) > 0:
                this.ROUTES_COUNT[station] = len(this.ROUTES[station])
    this.STATIONS = list(this.ROUTES_COUNT.keys())
    this.STATIONS_COUNT = len(this.ROUTES_COUNT)

def renderRoute(route):
    if int(config.get(this.PREFNAME_DEBUG_MODE)):
        this.LOG.write(f"[DEBUG] [{PLUGIN_NAME} v{PLUGIN_VERSION}] Render route: {route.station_name}, {route.system_name}, {route.distance}, {route.station_distance}, {route.resource}, {route.count}, {route.price}, {route.revenue}, {route.update}, {route.sell_percent}, {route.sell_per_item}, {route.demand}")
    try:
        pl1 = quote(this.STATION+" ["+this.STAR_SYSTEM+"]")
        # Переворачивание значений для фильтра по кораблям-носителям
        cariers = 1 - int(config.get(this.PREFNAME_INCLUDE_CARIERS))
        # Переворачивание значений для фильтра по наземным станциям
        surface = int(config.get(this.PREFNAME_INCLUDE_SURFACES))
        match surface:
            case 0:
                surface = 1
            case 1:
                surface = 2
            case 2:
                surface = 0

        url = this.SEARCH_URL+"?ps1="+str(pl1)+"&ps2="+str(quote(route.system_name + ' [' + route.station_name + ']'))+"&pi1="+str(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))+"&pi3="+str(config.get(this.PREFNAME_MAX_PRICE_AGE))+"&pi4="+str(config.get(this.PREFNAME_LANDING_PAD))+"&pi6="+str(config.get(this.PREFNAME_MAX_STATION_DISTANCE))+"&pi5="+str(config.get(this.PREFNAME_INCLUDE_SURFACES))+"&pi7="+str(cariers)+"&ps3=&pi2="+str(config.get(this.PREFNAME_MIN_SUPPLY))+"&pi13="+str(config.get(this.PREFNAME_MIN_DEMAND))+"&pi10="+str(config.get(this.PREFNAME_MIN_CAPACITY))+"&pi8=0"

        demandText = "📶"
        this.labels.demand["fg"] = "#ffcc00"
        match route.demand:
            case 0:
                this.labels.demand["fg"] = "#636362"
            case 1:
                this.labels.demand["fg"] = "#ff0000"
            case 2:
                this.labels.demand["fg"] = "#ffcc00"
            case 3:
                this.labels.demand["fg"] = "#4dff00"

        this.labels.stationsCountLabel["text"] = f"{this.STATION_INDEX+1}/{this.STATIONS_COUNT}"
        this.labels.itemsCountLabel["text"] = f"{this.ROUTE_INDEX+1}/{this.ROUTES_COUNT[this.STATIONS[this.STATION_INDEX]]}"
        this.labels.place["text"] = f"{route.station_name} [{route.system_name}]"
        # this.labels.place["url"] = f"https://inara.cz/elite/station/?search={quote(route.system_name + '[' + route.station_name + ']')}"
        this.labels.place["url"] = url
        this.labels.distance["text"] = f"{route.distance} >> {route.station_distance} Св.c"

        this.labels.resource["text"] = ITEMS.get(route.resource, route.resource)
        this.labels.demand["text"] = demandText
        if route.resource in ITEMS:
            this.labels.resource["url"] = f"https://elite-dangerous.fandom.com/ru/wiki/{quote(ITEMS.get(route.resource, route.resource))}"
        else:
            this.labels.resource["url"] = f"https://elite-dangerous.fandom.com/wiki/{quote(route.resource)}"

        this.labels.supply["text"] = f"{int(route.count):,} Ед."
        this.labels.price["text"] = f"{int(route.price):,} Кр."

        this.labels.earn["text"] = f"{int(route.revenue):,} Кр."
        this.labels.detailEarn["text"] = f"+{int(route.sell_percent):,}% или +{int(route.sell_per_item):,} Кр./Ед."

        this.labels.updated["text"] = route.update
        setStateBtn(tk.NORMAL)
    except Exception as e:
        this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] {e}")
        this.LOG.write(f"[ERROR] [{PLUGIN_NAME} v{PLUGIN_VERSION}] {traceback.format_exc()}")
