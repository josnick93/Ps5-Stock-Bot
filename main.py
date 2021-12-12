#!/usr/bin/python3

import requests
import lxml.html
import json
import time,os
import sys
import cfscrape
import random

from datetime import datetime


def parseMusimundo(raw):
    stream = json.loads(raw)
    hits = stream['hits']['hits']

    items = []
    for hit in hits:
        items.append(hit["_source"]["Descripcion"])

    return items


def parseJumbo(raw):
    stream = json.loads(raw)

    items = []
    for element in stream:
        items.append(element["productTitle"])

    return items

def parseWakkap(raw):
    stream = json.loads(raw)

    items = []
    for element in stream["data"]:
        if float(element["minPrice"]) > 400.0 :
            items.append(element["name"])
    return items

def parseXtralife(raw):
    stream = json.loads(raw)

    items = []
    
    for element in stream["body"]["members"]["results"]:
        if element["disponibility"]["disponibility"] != "out_of_stock" and element["disponibility"]["disponibility"] != "reservation_out_of_stock":
            items.append(element["name"])
    return items


GARBAGE = ['cascos','nintendo','marvels', 'sackboy', 'souls', 'morales', 'dualsense', 'juego', 'ps4', 'cámara', 'camara', 'camera', 'control', 'joystick', 'dualshock', 'parlante', 'celular', 'funda', 'lavarropas', 'cocina', 'plancha', 'auriculares', 'auricular', 'headset', 'kombat', 'android', 'nes', 'retro', 'pc', 'mixer', 'xbox', 'microsoft', 'audio', 'fighter', 'nba', 'vr', 'meses', 'posavasos', 'lámpara', 'remote', 'hd', 'kanji', 'stickers', 'duty', 'alien', 'lente', 'noga', 'torre', 'reflex', 'barra', 'compacta', 'minicomponente', 'atari', 'bateria', 'batería', 'ce7', 'radio', 'multimedia', 'reloj', 'cargador', 'nioh', 'pack', 'ratchet', 'returnal', 'nisuta', 'balanceado', 'calefactores', 'acolchado', 'brazos', 'cartuchera', 'tsushima', 'deathloop', 'stranding', 'fifa', 'kd-75x80j', 'xr-65a80j', 'resident', 'portatil']

KEYWORDS = ['playstation', 'ps5', 'consola', 'console', 'sony', 'comprar','stock' ,'Fnac.es','€','carrito']
#KEYWORDS = ['nintendo', 'switch','stock' ,'Fnac.es']


STORES = [
    #
    # Garbarino
    #
    [False, 'https://www.garbarino.com/q/playstation/srch?q=playstation', '//*[contains(@id, "item-description")]/text()'],
    [False, 'https://www.garbarino.com/q/ps5/srch?q=ps5', '//*[contains(@id, "item-description")]/text()'],

    #
    # Sony
    #
    [False, 'https://store.sony.com.ar/playstation%205', './/a[@class="title ellipsis"]/text()'],
    [False, 'https://store.sony.com.ar/ps5', './/a[@class="title ellipsis"]/text()'],

    #
    # Musimundo
    #
    # [True, 'https://u.braindw.com/els/musimundoapi?ft=playstation&qt=100&sc=carsa&refreshmetadata=true&exclusive=0&aggregations=true', parseMusimundo],
    # [True, 'https://u.braindw.com/els/musimundoapi?ft=ps5&qt=100&sc=carsa&refreshmetadata=true&exclusive=0&aggregations=true', parseMusimundo],
    
    #
    # Jumbo
    #
    [True, 'https://www.jumbo.com.ar/api/catalog_system/pub/products/search/?=,&ft=playstation', parseJumbo],
    [True, 'https://www.jumbo.com.ar/api/catalog_system/pub/products/search/?=,&ft=ps5', parseJumbo],
    
    #
    # Fravega
    #
    [False, 'https://www.fravega.com/l/?keyword=playstation', '//*[contains(@class, "PieceTitle")]/text()'],
    [False, 'https://www.fravega.com/l/?keyword=ps5', '//*[contains(@class, "PieceTitle")]/text()'],

    #
    # Compumundo
    #
    [False, 'https://www.compumundo.com.ar/q/playstation/srch?q=playstation', '//*[contains(@id, "item-description")]/text()'],
    [False, 'https://www.compumundo.com.ar/q/ps5/srch?q=ps5', '//*[contains(@id, "item-description")]/text()'],
    
    #
    # Walmart
    #
    [False, 'https://www.walmart.com.ar/buscar?text=playstation', '//*[contains(@class, "prateleira__name")]/text()'],
    [False, 'https://www.walmart.com.ar/buscar?text=ps5', '//*[contains(@class, "prateleira__name")]/text()'],

    #
    # Naldo
    #
    [False, 'https://www.naldo.com.ar/search/?text=playstation', '//*[contains(@class, "product__list--name")]/text()'],
    [False, 'https://www.naldo.com.ar/search/?text=ps5', '//*[contains(@class, "product__list--name")]/text()'],
    
    #
    # Carrefour
    #
    [False, 'https://www.carrefour.com.ar/catalogsearch/result/?q=playstation', '//*[contains(@class, "producto-info")]/a/p[@class="title"]/text()'],
    [False, 'https://www.carrefour.com.ar/catalogsearch/result/?q=ps5', '//*[contains(@class, "producto-info")]/a/p[@class="title"]/text()'],
    
    #
    # Coppel
    #
    # [False, 'https://www.coppel.com.ar/search/?q=playstation', '//*[contains(@class, "item-name")]/text()'],
    # [False, 'https://www.coppel.com.ar/search/?q=ps5', '//*[contains(@class, "item-name")]/text()'],
    
    #
    # Falabella
    #
    # [False, 'https://www.falabella.com.ar/falabella-ar/category/cat10166/Mundo-gamer?facetSelected=true&f.product.brandName=sony&isPLP=1', '//*[contains(@class, "pod-subTitle")]/text()'],
    
    #
    # CD Market
    #
    [False, 'https://www.cdmarket.com.ar/Item/Result?getfilterdata=true&page=1&id=0&recsperpage=32&order=CustomDate&sort=False&itemtype=Product&view=&term=playstation&filters=&hasStock=true', '//*/div[contains(@class, "box_data") and not(contains(@class, "box_data nonavailable"))]/h3/text()'],
    [False, 'https://www.cdmarket.com.ar/Item/Result?getfilterdata=true&page=1&id=0&recsperpage=32&order=CustomDate&sort=False&itemtype=Product&view=&term=ps5&filters=&hasStock=true', '//*/div[contains(@class, "box_data") and not(contains(@class, "box_data nonavailable"))]/h3/text()'],

    #
    # Necxus
    #
    # [False, 'https://www.necxus.com.ar/buscar/ps5/', '*//titulo-producto-grilla/text()'],
    
    #
    # Cetrogar
    #
    [False, 'https://www.cetrogar.com.ar/catalogsearch/result/?q=ps5', '*//a[@class="product-item-link"]/text()'],

    #Xtralife
    
    [True, 'https://api.xtralife.com/public-api/v1/group?storefront_id=1&id=1629&members%5Border%5D%5Bby%5D=&members%5Border%5D%5Btype%5D=DESC&members%5Bpage%5D=1&members%5Bhow_many%5D=24&members%5Bfilters%5D=%5B%5D', '*//a[@class="product-item-link"]/text()'],

]

STORES_SPAIN = [


    #[False, 'https://www.carrefour.es/consolas-switch/N-brkb0gZc4yhgj/c', '//a[contains(@class, "product-card__title")]//text()'],

    #game
    [False, 'https://www.game.es/HARDWARE/PACK-CONSOLA/PLAYSTATION-5/PLAYSTATION-5-RATCHET-AND-CLANK-UNA-DIMENSION-APARTE/190928', '//span[contains(@class, "sr-only")]/text()[last()]'],
    [False, 'https://www.game.es/HARDWARE/CONSOLA/PLAYSTATION-5/CONSOLA-PLAYSTATION-5/183224', '//span[contains(@class, "sr-only")]/text()[last()]'],
    #corte ingles
    #[False, 'https://www.elcorteingles.es/videojuegos/ps5/consolas/', '//span[contains(@class, "sr-only")]/text()[last()]'],
    #[False, 'https://www.elcorteingles.es/videojuegos/nintendo-switch/consolas/?gclsrc=aw.ds&nobeta=false', '//a[contains(@class, "js-add-to-cart")]/span[@class="tooltip"]/text()'],

    #Pc componentes
    #[False, 'https://www.pccomponentes.com/videoconsolas-ps5', '//span[contains(@class, "sr-only")]/text()[last()]'],
    [False, 'https://www.pccomponentes.com/videoconsolas-nintendo-switch', '//div[contains(@class, "cy-product-availability-date")]/text()[last()]'],

    #fnac
    [False, 'https://www.fnac.es/n127487/Playstation/Consolas-PS5', '//span[contains(@class, "f-buyBox-availabilityStatus-available")]/text()[last()]'],
    #[False, 'https://www.fnac.es/n127519/Nintendo/Consolas-Nintendo-Switch', '//span[contains(@class, "f-buyBox-availabilityStatus-available")]/text()[last()]'],

    #amazon
    [False, 'https://www.amazon.es/s?k=consola+playstation+5&i=videogames&rh=n%3A20938002031%2Cp_36%3A30000-&s=date-desc-rank&__mk_es_ES=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1638816318&rnid=831274031&ref=sr_st_date-desc-rank', '//span[contains(@class, "a-price-symbol")]/text()[last()]'],
    #[False, 'https://www.amazon.es/b?ie=UTF8&node=12366199031', '//span[contains(@class, "a-price-symbol")]/text()[last()]'],

    #Ardistel
    [False, 'https://www.ardistel.com/buscar.asp?search=CONSOLA+PS5', '//span[contains(@class, "cart")]/text()[last()]'],
    #[False, 'https://www.ardistel.com/buscar.asp?search=PSN+PLUS', '//a[contains(@class, "cart")]/text()[last()]'],

    #carrefour
    [False, 'https://www.carrefour.es/consolas-ps5/N-brkb0gZ18dif5/c', '//*[contains(@class, "product-card__title")]/a/text()'],

    #the shop gamer
    [False, 'https://theshopgamer.com/es/154-consolas-ps5', '//h2[contains(@class, "product-title")]/a/text()'],
    #[False, 'https://theshopgamer.com/es/131-consolas-switch', '//h2[contains(@class, "product-title")]/a/text()'],

    #Wakkap
    #[False, 'https://wakkap.com/search/consola%20ps5/filter/on-sale', '//div[contains(@class, "title")]/text()'],
    [True, 'https://api.wakkap.com/v2/items/search/Consola%20ps5/page/1/per/20', parseWakkap],

    #worten
    [False, 'https://www.worten.es/productos/consolas-juegos/playstation/consola/consola-ps5-825gb-7196053', '//button[contains(@class, "checkout-button")]/text()'],

    #Xtralife
    [True, 'https://api.xtralife.com/public-api/v1/group?storefront_id=1&id=1629&members%5Border%5D%5Bby%5D=&members%5Border%5D%5Btype%5D=DESC&members%5Bpage%5D=1&members%5Bhow_many%5D=24&members%5Bfilters%5D=%5B%5D', parseXtralife],

    

]

def main():
    # bot_token = sys.argv[1]
    bot_token = "5057379938:AAFI4oWz9DaZVvFsuU1nr8ZA_Oot6J9LPEI"
    #recipients = json.loads(sys.argv[2])
    recipients = json.loads('["1000866880"]')
    start_time = time.time()

    results = []
    for store in STORES_SPAIN:
        results = scrap(store)
        results["items"] = cleanup(results["items"])
        print (results["items"])

        if results["items"]:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%d-%m-%Y %H:%M:%S")
            message = "🎮 Encontré un vendedor con stock!\n\n📆 " + timestampStr + "\n🔗 " + results["store"] + "\n\n▶ " + ','.join(results["items"])
            print(message)
            telegram_bot_sendtext(message, bot_token, recipients)
    
    elapsed_time = time.time() - start_time
    elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%m-%Y %H:%M:%S")

    print("\n\n ---------------------")
    print("\nDate: " + timestampStr)
    print("\nElapsed time: " + elapsed)
    print("\n ---------------------\n\n")


def scrap(store):
    isJson = store[0]
    url = store[1]
    items = []

    print("Scraping " + url + "...")

    if isJson:
        callback = store[2]
        json = requests.get(url).content
        #print(json)
        items = callback(json)
    else:
        xpath = store[2]
        scraper = cfscrape.create_scraper()
        html = scraper.get(url)
        doc = lxml.html.fromstring(html.content)
        items = doc.xpath(xpath)
        print(items)
    return { "store": url, "items": items }


def cleanup(items):
    ps5Related = []
    for item in items:
        if not any(ext in item.lower() for ext in GARBAGE) and any(ext in item.lower() for ext in KEYWORDS):
            ps5Related.append(item)
    
    return ps5Related


def telegram_bot_sendtext(bot_message, bot_token, recipients):
    for bot_chatID in recipients:
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
        response = requests.get(send_text)
        print(response.json())


if __name__ == '__main__':
    main()
