"""
Plugin for "HITS"
"""
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
ROUTES = None
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


class ETTC():
    findBtn: None
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

def setStatus(status):
    this.labels.status["text"] = status

def plugin_stop() -> None:
    this.LOG.write("Stop Elite Trading Tool Companion")
    pass

def plugin_start():
    this.LOG.write("Starting Elite Trading Tool Companion")
    cmdr_data.last = None
    labels = ETTC()
    this.ROUTES = []
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

    this.labels.status = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.status.grid(row=1, column=1, sticky=tk.W)

    this.labels.plaseLabel = tk.Label(frame, text="Назначение:", justify=tk.LEFT)
    this.labels.plaseLabel.grid(row=2, column=0, sticky=tk.W)
    this.labels.place = hll(frame, text="")
    # https://inara.cz/elite/station/?search=[sysyem] [station]
    this.labels.place["url"]= ""
    this.labels.place.grid(row=2, column=1, columnspan=1, sticky="NSEW")


    this.labels.distanceLabel = tk.Label(frame, text="Дистанция:", justify=tk.LEFT)
    this.labels.distanceLabel.grid(row=3, column=0, sticky=tk.W)
    this.labels.distance = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.distance.grid(row=3, column=1, sticky=tk.W)

    this.labels.resourceLabel = tk.Label(frame, text="Ресурс:", justify=tk.LEFT)
    this.labels.resourceLabel.grid(row=4, column=0, sticky=tk.W)
    this.labels.resource = hll(frame, text="")
    # https://www.google.com/search?q=elite+dangerous+[resource]
    this.labels.resource["url"]= ""
    this.labels.resource.grid(row=4, column=1, columnspan=1, sticky="NSEW")

    this.labels.supplyLabel = tk.Label(frame, text="Количество:", justify=tk.LEFT)
    this.labels.supplyLabel.grid(row=5, column=0, sticky=tk.W)
    this.labels.supply = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.supply.grid(row=5, column=1, sticky=tk.W)

    this.labels.priceLabel = tk.Label(frame, text="Стоимость:", justify=tk.LEFT)
    this.labels.priceLabel.grid(row=6, column=0, sticky=tk.W)
    this.labels.price = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.price.grid(row=6, column=1, sticky=tk.W)

    this.labels.earnLabel = tk.Label(frame, text="Прибыль:", justify=tk.LEFT)
    this.labels.earnLabel.grid(row=7, column=0, sticky=tk.W)
    this.labels.earn = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.earn.grid(row=7, column=1, sticky=tk.W)

    this.labels.updatedLabel = tk.Label(frame, text="Обновлено:", justify=tk.LEFT)
    this.labels.updatedLabel.grid(row=8, column=0, sticky=tk.W)
    this.labels.updated = tk.Label(frame, text="", justify=tk.LEFT)
    this.labels.updated.grid(row=8, column=1, sticky=tk.W)

    frame.columnconfigure(8, weight=1)

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

def doRequest():
    pl1 = quote(this.STATION+" ["+this.STAR_SYSTEM+"]")

    url = this.SEARCH_URL+"?ps1="+str(pl1)+"&ps2=&pi1="+str(config.get(this.PREFNAME_MAX_ROUTE_DISTANCE))+"&pi3="+str(config.get(this.PREFNAME_MAX_PRICE_AGE))+"&pi4="+str(config.get(this.PREFNAME_LANDING_PAD))+"&pi6="+str(config.get(this.PREFNAME_MAX_STATION_DISTANCE))+"&pi5="+str(config.get(this.PREFNAME_INCLUDE_SURFACES))+"&pi7="+str(config.get(this.PREFNAME_INCLUDE_CARIERS))+"&ps3=&pi2="+str(config.get(this.PREFNAME_MIN_SUPPLY))+"&pi13="+str(config.get(this.PREFNAME_MIN_DEMAND))+"&pi10="+str(config.get(this.PREFNAME_MIN_CAPACITY))+"&pi8=0"

    response = requests.get(url=url, headers=this.HTTPS_HEADERS, timeout=10)

    if response.status_code != requests.codes.ok:
        setStatus("Ошибка: error code." + str(response.status_code))

    this.IS_REQUESTING = False

    if response.text:
        soup = BeautifulSoup(response.text, 'html.parser')
        htmls = soup.findAll("div", {"class": re.compile(r'mainblock traderoutebox taggeditem')}, limit=1)

        setStatus("Путь обрабатывается..") 
        if htmls:
            parseData(htmls[0])
        else:
            setStatus("Нет маршрутов для этой станции") 
    else:
        this.LOG.write("Catch request error")
        setStatus("Ошибка: not catch web source.")

def parseData(html):
    soupDom = BeautifulSoup(str(html), 'html.parser')
    stationDom = soupDom.findAll("span", {"class": re.compile(r'standardcase standardcolor nowrap')})
    systemDom = soupDom.findAll("span", {"class": re.compile(r'uppercase nowrap')})
    distDom = soupDom.findAll("span", {"class": re.compile(r'bigger')})
    resourceDom = soupDom.findAll("span", {"class": re.compile(r'avoidwrap')})

    countValueDom = soupDom.findAll("div", {"class": re.compile(r'itempairvalue')})
    countRegGroups = re.search(r'([0-9,]+)', str(countValueDom[3]))

    priceValueDom = soupDom.findAll("div", {"class": re.compile(r'itempairvalue')})
    priceRegGroups = re.search(r'([0-9,]+)', str(priceValueDom[2]))

    revenueValueDom = soupDom.findAll("span", {"class": re.compile(r'major')})
    revenueRegGroups = re.search(r'([0-9,]+)\b', str(revenueValueDom[0]))
    dateDom = soupDom.findAll("div", {"class": re.compile(r'itempairvalue itempairvalueright')})

    stationRegGroups = re.search(r'([a-zA-Z\b ]+)<wbr/>', str(stationDom[1]))
    systemRegGroups = re.search(r'([a-zA-Z-\[\]0-9. ]+)</span>', str(systemDom[1]))
    distRegGroups = re.search(r'([a-zA-Z-\[\]0-9. ]+)</span>', str(distDom[0]))
    resourceRegGroups = re.search(r'([a-zA-Z-\[\]0-9. ]+)</span>', str(resourceDom[0]))
    updateRegGroups = re.search(r'([a-zA-Z-\[\]0-9. ]+)</div>', str(dateDom[1]))

    FOUND_STATION_NAME = stationRegGroups.group(1)
    FOUND_SYSTEM_NAME = systemRegGroups.group(1)
    FOUND_DISTANTION = distRegGroups.group(1)
    FOUND_RESOURCE = resourceRegGroups.group(1)
    FOUND_COUNT = str(int(countRegGroups.group(0).replace(",", "")))
    FOUND_PRICE = str(int(priceRegGroups.group(0).replace(",", "")))
    FOUND_REVERNUE = str(int(revenueRegGroups.group(0).replace(",", ""))*int(config.get(this.PREFNAME_MIN_CAPACITY)))
    FOUND_UPDATE = updateRegGroups.group(1)

    renderRoute(FOUND_STATION_NAME, FOUND_SYSTEM_NAME, FOUND_DISTANTION, FOUND_RESOURCE, FOUND_COUNT, FOUND_PRICE, FOUND_REVERNUE, FOUND_UPDATE)

def renderRoute(station, system, dist, resource, count, price, revenue, update):
    this.labels.place["text"] = station + " [" + system + "]"
    pl1 = quote(system +"["+ station+"]")
    # https://inara.cz/elite/station/?search=[sysyem] [station]
    this.labels.place["url"] = "https://inara.cz/elite/station/?search="+pl1
    this.labels.distance["text"] = dist
    this.labels.resource["text"]= resource
    pl2 = quote(resource)
    # "https://elite-dangerous.fandom.com/wiki/[resource]
    this.labels.resource["url"] = "https://elite-dangerous.fandom.com/wiki/"+pl2
    this.labels.supply["text"] = '{:,}'.format(int(count)) + " на хранении"
    this.labels.price["text"] = '{:,}'.format(int(price)) + " Кред./шт"
    this.labels.earn["text"] = '{:,}'.format(int(revenue)) + " Кред."
    this.labels.updated["text"] = update

    setStatus("Путь найден!")
    setStateBtn(tk.NORMAL)