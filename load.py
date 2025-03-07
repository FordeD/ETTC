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
sys.path.insert(0, "./soupsieve")  # Добавляем папку в пути поиска модулей

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

PLUGIN_NAME = "ETTC(Inara)"

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


PREFNAME_MAX_ROUTE_DISTANCE = "Макс. расстояние маршрута" #pi1
PREFNAME_MIN_SUPPLY = "Мин. поставки" # pi2
PREFNAME_MAX_PRICE_AGE = "Макс. возраст цены" #pi3
PREFNAME_LANDING_PAD = "Мин. посадочная площадка(1/2/3)" #pi4
PREFNAME_INCLUDE_SURFACES = "Искать на планетах(1/0/2)" #pi5
PREFNAME_MAX_STATION_DISTANCE = "Макс.расстояние до станции" #pi6
PREFNAME_INCLUDE_CARIERS = "Использовать корабли носители(1/0)" #pi7
PREFNAME_MIN_CAPACITY = "Грузовместимость(720)" # pi10
PREFNAME_MIN_DEMAND = "Мин. спрос(0)" # pi13

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
    findBtn: None
    prevBtn: None
    nextBtn: None
    routesCountLabel: None
    plaseLabel: None
    place: None
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

def setStatus(status):
    this.labels.status["text"] = status

def plugin_stop() -> None:
    this.LOG.write("Stop Elite Trading Tool Companion")
    pass

def plugin_start():
    this.LOG.write("Starting Elite Trading Tool Companion")
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

    return this.PLUGIN_NAME

def plugin_start3(plugin_dir: str) -> str:
    plugin_start()

def prefs_changed(cmdr, isbeta):
    this.LOG.write("Update prefs")
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

    if station:
        if not this.IS_REQUESTING:
            setStateBtn(tk.NORMAL)
    else:
        setStateBtn(tk.DISABLED)

def plugin_app(parent: tk.Frame):
    plugin_app.parent = parent
    frame = tk.Frame(parent)
    # VARIABLES
    this.labels.findBtn = tk.Button(frame, text="Искать торговый путь", state=tk.DISABLED, command=this.getBestTrade)
    this.labels.findBtn.grid(row=0, column=1, sticky=tk.W)

    this.labels.prevBtn = tk.Button(frame, text="<<", state=tk.DISABLED, command=this.getPrevRoute)
    this.labels.prevBtn.grid(row=0, column=0, sticky=tk.W)
    this.labels.nextBtn = tk.Button(frame, text=">>", state=tk.DISABLED, command=this.getNextRoute)
    this.labels.nextBtn.grid(row=0, column=2, sticky=tk.W)

    this.labels.status = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.status.grid(row=1, column=1, sticky=tk.W)

    this.labels.routesCountLabel = tk.Label(frame, text="Пути: 0/0", justify=tk.LEFT)
    this.labels.routesCountLabel.grid(row=2, column=1, sticky=tk.W)
    this.labels.plaseLabel = tk.Label(frame, text="Назначение:", justify=tk.LEFT)
    this.labels.plaseLabel.grid(row=3, column=0, sticky=tk.W)
    this.labels.place = hll(frame, text="")
    # https://inara.cz/elite/station/?search=[sysyem] [station]
    this.labels.place["url"]= ""
    this.labels.place.grid(row=3, column=1, columnspan=1, sticky="NSEW")


    this.labels.distanceLabel = tk.Label(frame, text="Дистанция:", justify=tk.LEFT)
    this.labels.distanceLabel.grid(row=4, column=0, sticky=tk.W)
    this.labels.distance = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.distance.grid(row=4, column=1, sticky=tk.W)

    this.labels.resourceLabel = tk.Label(frame, text="Ресурс:", justify=tk.LEFT)
    this.labels.resourceLabel.grid(row=5, column=0, sticky=tk.W)
    this.labels.resource = hll(frame, text="")
    # https://www.google.com/search?q=elite+dangerous+[resource]
    this.labels.resource["url"]= ""
    this.labels.resource.grid(row=5, column=1, columnspan=1, sticky="NSEW")

    this.labels.supplyLabel = tk.Label(frame, text="Количество:", justify=tk.LEFT)
    this.labels.supplyLabel.grid(row=6, column=0, sticky=tk.W)
    this.labels.supply = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.supply.grid(row=6, column=1, sticky=tk.W)

    this.labels.priceLabel = tk.Label(frame, text="Стоимость:", justify=tk.LEFT)
    this.labels.priceLabel.grid(row=7, column=0, sticky=tk.W)
    this.labels.price = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.price.grid(row=7, column=1, sticky=tk.W)

    this.labels.earnLabel = tk.Label(frame, text="Прибыль:", justify=tk.LEFT)
    this.labels.earnLabel.grid(row=8, column=0, sticky=tk.W)
    this.labels.earn = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.earn.grid(row=8, column=1, sticky=tk.W)

    this.labels.updatedLabel = tk.Label(frame, text="Обновлено:", justify=tk.LEFT)
    this.labels.updatedLabel.grid(row=9, column=0, sticky=tk.W)
    this.labels.updated = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.updated.grid(row=9, column=1, sticky=tk.W)

    frame.columnconfigure(9, weight=1)

    this.labels.spacer = tk.Frame(frame)
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

def getBestTrade():
    if this.STAR_SYSTEM and (this.STATION is not None):
        setStateBtn(tk.DISABLED)
        this.IS_REQUESTING = True
        setStatus("Идет поиск пути...")
        this.SEARCH_THREAD = Thread(target=doRequest)
        this.SEARCH_THREAD.start()
    else:
        setStatus("Прилетите на станцию!")

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
        this.LOG.write(f"{url}")
        response = requests.get(url=url, headers=this.HTTPS_HEADERS, timeout=10)

        if response.status_code != requests.codes.ok:
            setStatus("Ошибка: error code." + str(response.status_code))

        this.IS_REQUESTING = False

        if response.text:
            parseData(response.text)
            renderRoute(this.ROUTES[0])
            setStatus(f"Пути найдены!")
        else:
            this.LOG.write("Catch request error")
            setStatus("Ошибка: not catch web source.")
            setStateBtn(tk.NORMAL)
    except Exception as e:
        # Проверяем, содержит ли ошибка 'NoneType' object is not callable
        if "'NoneType' object is not callable" in str(e):
            setStatus("Маршруты от станции отсутсвуют")
            setStateBtn(tk.NORMAL)
        else:
            setStatus(f"Ошибка: {e}")
            this.LOG.write(f"{e}")
            this.LOG.write(f"{traceback.format_exc()}")
            setStateBtn(tk.NORMAL)

def parseData(html):
    soup = BeautifulSoup(html, 'html.parser')
    this.ROUTES = []
    
    for block in soup.find_all("div", class_="mainblock traderoutebox taggeditem", attrs={"data-tags": '["1"]'}):
        try:
            # Извлечение имени станции
            station_elem = block.select_one("div:nth-of-type(1) a span.standardcase.standardcolor.nowrap")
            station_text = station_elem.text
            station_name = station_text.split(" | ")[0].strip()
            if station_elem.find("span"):
                station_name += " " + station_elem.find("span").text.strip()
            
            # Извлечение имени системы
            system_name = block.select_one("div:nth-of-type(1) a span.uppercase.nowrap").text.strip()
            
            # Дистанция
            distance = block.select_one("div:nth-of-type(10) div:nth-of-type(1) div:nth-of-type(1) div.itempairvalue.itempairvalueright span.bigger").text.strip()
            
            # Ресурс
            resource = block.select_one(".traderouteboxtoright div:nth-of-type(1) .itempairvalue a span.avoidwrap").text.strip()
            
            # Количество
            count = block.select_one(".traderouteboxtoright div:nth-of-type(3) .itempairvalue").text.strip()
            count = re.sub(r",", "", count).split("\ue84e︎")[0]  # Убираем запятые
            
            # Цена
            price = block.select_one(".traderouteboxtoright div:nth-of-type(2) .itempairvalue").text.strip()
            price = re.sub(r",", "", price).split(" ")[0]
            
            # Доход
            revenue = block.select_one("div:nth-of-type(10) .traderouteboxprofit div:nth-of-type(3) .itempairvalue.itempairvalueright").text.strip()
            revenue = re.sub(r",", "", revenue).split(" ")[0]
            
            # Дата обновления
            update = block.select_one("div:nth-of-type(10) div:nth-of-type(1) div:nth-of-type(2) .itempairvalue.itempairvalueright").text.strip()
            
            this.ROUTES.append(TradeRoute(station_name, system_name, distance, resource, count, price, revenue, update))
        except AttributeError:
            continue  # Пропускаем элементы с неполными данными

    this.ROUTE_INDEX = 0
    this.ROUTES_COUNT = len(this.ROUTES)

def renderRoute(route):
    try:
        this.labels.routesCountLabel["text"] = f"Пути: {this.ROUTE_INDEX+1}/{this.ROUTES_COUNT}"
        this.labels.place["text"] = f"{route.station_name} [{route.system_name}]"
        this.labels.place["url"] = f"https://inara.cz/elite/station/?search={quote(route.system_name + '[' + route.station_name + ']')}"
        this.labels.distance["text"] = route.distance
        this.labels.resource["text"] = route.resource
        this.labels.resource["url"] = f"https://elite-dangerous.fandom.com/wiki/{quote(route.resource)}"
        this.labels.supply["text"] = f"{int(route.count):,} на складе"
        this.labels.price["text"] = f"{int(route.price):,} Кред./шт"
        this.labels.earn["text"] = f"{int(route.revenue):,} Кред."
        this.labels.updated["text"] = route.update

        setStateBtn(tk.NORMAL)
    except Exception as e:
        this.LOG.write(f"{e}")
        this.LOG.write(f"{traceback.format_exc()}")
