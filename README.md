# Elite Trading Tool Companion (ETTT) EDMC Plugin (Only Russian language)

## [Download zip archive](https://github.com/FordeD/ETTC/archive/refs/heads/main.zip)
![Plugin preview](https://github.com/FordeD/ETTC/blob/main/plugin.jpg)

# English Install
This is a simple plugin for [EDMarketConnector](https://github.com/Marginal/EDMarketConnector/wiki), based on the [Inara trading search](https://inara.cz/elite/market-traderoutes-search/) site, for find to find the best one-way trade route

As with other EDMC plugins, simply unzip the git directory into your plugins folder (or just place load.py inside a directory within the plugins directory) yielding something like
```
EDMarketConnector\plugins\ETTC\load.py 
EDMarketConnector\plugins\ETTC\logger.py 
EDMarketConnector\plugins\ETTC\plugin.log
EDMarketConnector\plugins\ETTC\plugin.jpeg
EDMarketConnector\plugins\ETTC\__init__.py 
EDMarketConnector\plugins\ETTC\bs4
```
and restart EDMC afterwards.

# Русский Установка
Простой плагин для [EDMarketConnector](https://github.com/Marginal/EDMarketConnector/wiki), основан на [Inara поиск торгового пути](https://inara.cz/elite/market-traderoutes-search/) сайте, для поиска лучшего торгового пути в одну сторону от текущей станции, где вы находитесь

Для установки плагина разархивируйте плагин в папку `C:/Users/<имя_пользователя>/AppData/Local/EDMarcetConnector/Plugins/`, чтобы в этой папке появялась папка ETTC c находящимися в ней файлами и использующимися папками внутри плагина:
```
ETTC\load.py 
ETTC\logger.py 
ETTC\plugin.log
ETTC\plugin.jpeg 
ETTC\__init__.py 
ETTC\bs4
```
После этого перезапустите программу EDMarketConnector.

Для настройки необходимо открыть Файл->Настройки->ETTC. 
**Важно! при изменении настроек ориенитуйтесь на значения из фильтров поиска [Inara trading search](https://inara.cz/elite/market-traderoutes-search/).
Значения в скобках указаны как примеры или варианты значений, при указании координально других значений плагин не будет искать маршруты!**
