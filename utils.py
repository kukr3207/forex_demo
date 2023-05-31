import requests
from bs4 import BeautifulSoup
import oandapyV20
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingInfo
import oandapyV20.endpoints.instruments as instruments
#Commodities Done
#Bonds done
#stocks Done
#currencies done
#VIX

def fillStockData(df, type, objectives):

    for i in objectives[type].keys():
        objectives[type][i] = {}
        df1 = df[df["name"]==i]
        values = list(df1.values)

        

        if float(values[0][4][:-1]) >= 0.15:
             objectives[type][i]["Daily"] = 1
        elif float(values[0][4][:-1]) <= -0.15:
            objectives[type][i]["Daily"] = -1
        else:
            objectives[type][i]["Daily"] = 0
        
        if float(values[0][5][:-1]) >= 0.5:
             objectives[type][i]["Weekly"] = 1
        elif float(values[0][5][:-1]) <= -0.5:
            objectives[type][i]["Weekly"] = -1
        else:
            objectives[type][i]["Weekly"] = 0

        if float(values[0][6][:-1]) >= 1:
             objectives[type][i]["Monthly"] = 1
        elif float(values[0][6][:-1]) <= -1:
            objectives[type][i]["Monthly"] = -1
        else:
            objectives[type][i]["Monthly"] = 0

    return objectives

def fillBondsData(df, type, objectives):

    for i in objectives[type].keys():
        objectives[type][i] = {}
        df1 = df[df["name"]==i]
        values = list(df1.values)
        daily_value  = ((float(values[0][2])+float(values[0][3])) - float(values[0][3]))/((float(values[0][2])+float(values[0][3])))

        if daily_value >= 0.15:
             objectives[type][i]["Daily"] = 1
        elif daily_value <= -0.15:
            objectives[type][i]["Daily"] =  -1
        else:
            objectives[type][i]["Daily"] =  0
                                                                                                         
        if float(values[0][4][:-1]) >= 0.5:
             objectives[type][i]["Weekly"] = 1
        elif float(values[0][4][:-1]) <= -0.5:
            objectives[type][i]["Weekly"] = -1
        else:
            objectives[type][i]["Weekly"] = 0

        if float(values[0][5][:-1]) >= 1:
             objectives[type][i]["Monthly"] = 1
        elif float(values[0][5][:-1]) <= -1:
            objectives[type][i]["Monthly"] = -1
        else:
            objectives[type][i]["Monthly"] = 0

    return objectives

def fillCommoditiesData(df, type, objectives):

    for i in objectives[type].keys():
        objectives[type][i] = {}
        df1 = df[df["Energy"]==i]
        values = list(df1.values)

        if float(values[0][3][:-1]) >= 0.15:
             objectives[type][i]["Daily"] = 1
        elif float(values[0][3][:-1]) <= -0.15:
            objectives[type][i]["Daily"] = -1
        else:
            objectives[type][i]["Daily"] = 0

        if float(values[0][4][:-1]) >= 0.5:
             objectives[type][i]["Weekly"] = 1
        elif float(values[0][4][:-1]) <= -0.5:
            objectives[type][i]["Weekly"] = -1
        else:
            objectives[type][i]["Weekly"] = 0

        if float(values[0][5][:-1]) >= 1:
             objectives[type][i]["Monthly"] = 1
        elif float(values[0][5][:-1]) <= -1:
            objectives[type][i]["Monthly"] = -1
        else:
            objectives[type][i]["Monthly"] = 0

    return objectives

def getCurrencyData(currency, client, type):
    params = {
    "granularity": type,
    "count": 2,
    "price": "M",
    }

    request = instruments.InstrumentsCandles(instrument=currency, params=params)
    response = client.request(request)
    prices = [float(candle["mid"]["c"]) for candle in response["candles"]]
    percent_change = ((prices[1] - prices[0]) / prices[0]) * 100

    return round(percent_change, 2)

def getusddata(type, objectives, client):
    i = "USD_CAD"
    objectives[type][i] = {}
    value = getCurrencyData(i,client,"D")
    if value >= 0.15:
        objectives[type][i]["Daily"] = -1
    elif value <= -0.15:
        objectives[type][i]["Daily"] = 1
    else:
        objectives[type][i]["Daily"] = 0

    value = getCurrencyData(i,client,"W")
    if value >= 0.5:
        objectives[type][i]["Weekly"] = -1
    elif value <= -0.5:
        objectives[type][i]["Weekly"] = 1
    else:
        objectives[type][i]["Weekly"] = 0

    value = getCurrencyData(i,client,"M")
    if value >= 1:
        objectives[type][i]["Monthly"] = -1
    elif value <= -1:
        objectives[type][i]["Monthly"] = 1
    else:
        objectives[type][i]["Monthly"] = 0
    
    return objectives

def fillCurrencyData(type, objectives):
    account_id = "101-001-25300193-001"
    access_token = "2919a85d9816bd961344a2e6970deb35-693e8e1ebdd2c13bd273b0480061d387"
    client = oandapyV20.API(access_token=access_token)
    for i in objectives[type].keys():
        if i == "USD_CAD":
            objectives = getusddata(type, objectives, client)
        else:
            objectives[type][i] = {}
            value = getCurrencyData(i,client,"D")
            if value >= 0.15:
                objectives[type][i]["Daily"] = 1
            elif value <= -0.15:
                objectives[type][i]["Daily"] = -1
            else:
                objectives[type][i]["Daily"] = 0

            value = getCurrencyData(i,client,"W")
            if value >= 0.5:
                objectives[type][i]["Weekly"] = 1
            elif value <= -0.5:
                objectives[type][i]["Weekly"] = -1
            else:
                objectives[type][i]["Weekly"] = 0

            value = getCurrencyData(i,client,"M")
            if value >= 1:
                objectives[type][i]["Monthly"] = 1
            elif value <= -1:
                objectives[type][i]["Monthly"] = -1
            else:
                objectives[type][i]["Monthly"] = 0

    return objectives