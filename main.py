from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.request import Request, urlopen
import numpy as np
import requests
import urllib
import operator
import ssl
import json
from tkinter import *
from selenium import webdriver


def getWifi(city):
    startnumber=0
    endnumber=999
    key_url = urllib.parse.quote(city.encode('utf-8'))
    wifiResult = []

    while True:
        url='http://openapi.seoul.go.kr:8088/5665675969646f6e3934494d4f5556/xml/PublicWiFiPlaceInfo/{}/{}/{}'\
            .format(startnumber, endnumber, key_url)
        req = requests.get(url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        x = soup.find_all("instl_x")
        for xx in range(0, len(x)):
            x[xx] = x[xx].get_text()
        y = soup.find_all("instl_y")
        for yy in range(0, len(y)):
            y[yy] = y[yy].get_text()
        if(len(x) == 0):
            break
        for a, b in zip(x, y):
            wifiResult.append((float(a),float(b)))
        startnumber+=1000
        endnumber+=1000

    return wifiResult

def getToilet():
    startnumber=0
    endnumber=999
    toiletResult = []

    while True:
        url='http://openapi.seoul.go.kr:8088/4b6f677841646f6e36396453424b4f/xml/SearchPublicToiletPOIService/{}/{}/'\
            .format(startnumber, endnumber)
        req = requests.get(url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        x = soup.find_all("x_wgs84")
        for xx in range(0, len(x)):
            x[xx] = x[xx].get_text()
        y = soup.find_all("y_wgs84")
        for yy in range(0, len(y)):
            y[yy] = y[yy].get_text()
        if(len(x) == 0):
            break
        for a, b in zip(x, y):
            toiletResult.append((float(a),float(b)))
        startnumber+=1000
        endnumber+=1000

    return toiletResult

def getFestival(location):
    try:
        URL = 'https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyCdQVb24M4w2-VUGociO8eAtLUmuTlVg2o' \
        '&sensor=false&language=ko&address={}'.format(location)
        response = requests.get(URL)
        data = response.json()
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']

        kor_url = quote(location)
        url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + kor_url + '&key=AIzaSyCdQVb24M4w2-VUGociO8eAtLUmuTlVg2o&language=ko'
        req = Request(url, headers={'X-Mashape-Key': 'AIzaSyCdQVb24M4w2-VUGociO8eAtLUmuTlVg2o'})
        ssltext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        company_addr_json = urlopen(req, context=ssltext).read().decode('utf8')
        addr = json.loads(company_addr_json)
        addr_detail = addr['results'][0]
        city_addr = addr_detail['address_components'][3]['long_name']

        return np.array((float(lng),float(lat))), city_addr

    except:
        return None



driver = webdriver.Chrome('chromedriver')
driver.implicitly_wait(3)
driver.get('https://www.google.com/maps')
w = Tk()
w.title("1조")

location = StringVar()
wifinum = 0
toiletnum = 0

def wifiSearch():
    loca = location.get()
    if loca != "":
        spot, city = getFestival(loca)
        wifi = getWifi(city)
        dist = []
        for a in wifi:
            dist.append([wifi.index(a), np.sqrt(((np.array(spot) - np.array(a)) ** 2).sum())])
        sortDist = sorted(dist, key=operator.itemgetter(1))
        wifiSearch = ""
        wifiSearch = str(wifi[sortDist[wifinum][0]][1]) + ", " + str(wifi[sortDist[wifinum][0]][0])
        driver.get('https://www.google.com/maps')
        driver.find_element_by_name('q').send_keys(wifiSearch)
        driver.find_element_by_xpath('//button[@aria-label="검색"]').click()

def pluswifi():
    global wifinum
    wifinum += 1
    wifiSearch()

def minuswifi():
    global wifinum
    wifinum -= 1
    wifiSearch()

def firstwifi():
    global wifinum
    wifinum = 0
    wifiSearch()

def toiletSearch():
    loca = location.get()
    if loca != "":
        spot, city = getFestival(loca)
        toilet = getToilet()
        dist = []
        for a in toilet:
            dist.append([toilet.index(a), np.sqrt(((np.array(spot) - np.array(a)) ** 2).sum())])
        sortDist = sorted(dist, key=operator.itemgetter(1))
        toiletSearch = ""
        toiletSearch = str(toilet[sortDist[toiletnum][0]][1]) + ", " + str(toilet[sortDist[toiletnum][0]][0])
        driver.get('https://www.google.com/maps')
        driver.find_element_by_name('q').send_keys(toiletSearch)
        driver.find_element_by_xpath('//button[@aria-label="검색"]').click()

def plustoilet():
    global toiletnum
    toiletnum += 1
    toiletSearch()

def minustoilet():
    global toiletnum
    toiletnum -= 1
    toiletSearch()

def firsttoilet():
    global toiletnum
    toiletnum = 0
    toiletSearch()

def quit():
    driver.close()
    w.quit()


Label(w, text="축제 장소: ").grid(row=0, column=0)
Entry(w, textvariable=location).grid(row=0, column=1)
bt0 = Button(w, text="종료", command=quit).grid(row=0, column=2)

bt1 = Button(w, text="이전", command=minuswifi).grid(row=1, column=0)
bt2 = Button(w, text="와이파이 위치 찾기", command=wifiSearch).grid(row=1, column=1)
bt3 = Button(w, text="다음", command=pluswifi).grid(row=1, column=2)

bt4 = Button(w, text="이전", command=minustoilet).grid(row=2, column=0)
bt5 = Button(w, text="화장실 위치 찾기", command=toiletSearch).grid(row=2, column=1)
bt6 = Button(w, text="다음", command=plustoilet).grid(row=2, column=2)

w.mainloop()
