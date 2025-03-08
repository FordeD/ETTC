# Elite Trading Tool Companion (ETTС) EDMC Plugin (Only Russian language)

[![Github All Releases](https://img.shields.io/github/downloads/FordeD/ETTC/latest/total)]() ![GitHub repo size](https://img.shields.io/github/repo-size/FordeD/ETTC) ![GitHub Repo stars](https://img.shields.io/github/stars/FordeD/ETTC)

*********
## [Download zip archive](https://github.com/FordeD/ETTC/archive/refs/heads/main.zip)
![Plugin preview](https://github.com/FordeD/ETTC/blob/main/plugin.png) 

# English. Install
This is a simple plugin for [EDMarketConnector](https://github.com/Marginal/EDMarketConnector/wiki), based on the [Inara trading search](https://inara.cz/elite/market-traderoutes-search/) site, for find to find the best one-way trade route

For installation of the plugin, uninstall the plugin into the `c:/Users/<user_name>/AppData/Local/EDMarcetConnector/Plugins/`, create the ETTC folder and copy all the files and folders from the plugin archive:
```
EDMarketConnector\plugins\ETTC\load.py 
EDMarketConnector\plugins\ETTC\logger.py 
EDMarketConnector\plugins\ETTC\plugin.log
EDMarketConnector\plugins\ETTC\plugin.jpeg
EDMarketConnector\plugins\ETTC\__init__.py 
EDMarketConnector\plugins\ETTC\bs4
EDMarketConnector\plugins\ETTC\soupsieve
EDMarketConnector\plugins\ETTC\pyperclip
```
and restart EDMC afterwards.

For configuration, you need to open the file->settings->ETTC. 
**Important! When changing the settings, focus on the values ​​from the search filters [Inara Trading Search](https://inara.cz/elite/market-traderoutes-search/).
The values ​​in the brackets are indicated as examples or options for values, when indicating the coordinate of other values, the plugin will not look for routes!**

********* 

# Русский. Установка
Простой плагин для [EDMarketConnector](https://github.com/Marginal/EDMarketConnector/wiki), основан на [Inara поиск торгового пути](https://inara.cz/elite/market-traderoutes-search/) сайте, для поиска лучшего торгового пути в одну сторону от текущей станции, где вы находитесь

Для установки плагина разархивируйте плагин в папку `C:/Users/<имя_пользователя>/AppData/Local/EDMarcetConnector/Plugins/`, Создайте папку ETTC и скопируйте все файлы и папки из архива плагина:
```
ETTC\load.py 
ETTC\logger.py 
ETTC\plugin.log
ETTC\plugin.jpeg 
ETTC\__init__.py 
ETTC\bs4
ETTC\soupsieve
ETTC\pyperclip
```
После этого перезапустите программу EDMarketConnector.

Для настройки необходимо открыть Файл->Настройки->ETTC. 
**Важно! при изменении настроек ориенитуйтесь на значения из фильтров поиска [Inara trading search](https://inara.cz/elite/market-traderoutes-search/).
Значения в скобках указаны как примеры или варианты значений, при указании координально других значений плагин не будет искать маршруты!**

********* 

## Настройка 
Плагин имеет свою настройку под каждый корабль. Для этого перейдиде в меню Файл->Настройки->ETTC.

* Макс. расстояние маршрута - максимальное расстояние в единицах Ly (световых лет) от текущей системы
* Макс. расстояние до станции - максимальное расстояние до станции в системе к которой будет проложен маршрут
* Грузоподъемность - количество места в единицах для покупки и продажи товаров (учитывается для рассчета прибыли)
* Макс. возраст цены - количество дней в единицах с последнего обновления (1,2,3,7,30,180 дней)
* Мин. посадочная площажка - размер посадочной площадки станции где нужно продать товар (1-малая, 2-средняя, 3-большая)
* Мин. поставки - минимальный объем покупаемого ресурса в единицах на станции для продажи по маршруту (0-любое, 100,500,1000,2500,5000,10000,50000)
* Мин. спрос - минимальное количество продаваемого ресурса в единицах на текущей станции для покупки (0-любое, 100,500,1000,2500,5000,10000,50000)
* Искать на планетах - нужен ли поиск торговых маршрутов на планетах (0 - Нет, 1 - Да, 2 - Да со станциями дополнения Одиссеи)
* Искать корабли носители - нужен ли поиск торговых маршрутов через корабли-носители (1 - Да, 0 - Нет)