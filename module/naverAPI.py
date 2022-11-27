import requests
import urllib
import random
import json
from PIL import Image
from Product import Product

def searchNaverShop(query):
    query = urllib.parse.quote(query)

    display = "100"
    # start = random.randrange(1, 1001)
    count = 1
    itemList = list()
    for i in range(count):
        start = int(display) * i + 1
        url = "https://openapi.naver.com/v1/search/shop?query=" + query + "&display=" + display + "&start="+ str(start)
        request = urllib.request.Request(url)
        request.add_header('X-Naver-Client-Id', "<Your-naverAPI-ID")
        request.add_header('X-Naver-Client-Secret', "Your-naverAPI-Secret")
        response = urllib.request.urlopen(request)
        itemList.extend(json.loads(response.read().decode('utf-8'))["items"])

    products = list()
    for i, item in enumerate(itemList):
        title = item["title"].replace('<b>', '')
        title = title.replace('</b>', '')
        imageBytes = saveUrlToImg(item["image"])
        products.append(Product(title, item["link"], item["image"], item["lprice"], imageBytes))
    return products

def saveUrlToImg(url):
    response = requests.get(url)
    return response.content