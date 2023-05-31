import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from utils import fillStockData,fillBondsData,fillCommoditiesData, fillCurrencyData


def gaugemeter(value): # Define the ranges and corresponding labels
    ranges = [-6, -2, 2, 6]
    labels = ['Risk Off', 'Neutral', 'Risk On']

    # Define the color scale for the gauge meter
    colorscale = [
        [0, 'red'], 
        [0.33, 'orange'],
        [0.67, 'green'],
        [1, 'blue']
    ]

    # Define the figure layout
    fig = go.Figure(
        go.Indicator(
            mode = "gauge+number",
            value = value,
            title = {'text': 'Risk Level'},
            gauge = {
                'axis': {'range': [-6, 6]},
                'steps' : [
                    {'range': [-6, -2], 'color': 'red'},
                    {'range': [-2, 2], 'color': 'orange'},
                    {'range': [2, 6], 'color': 'green'},
                ],
                'bar': {'color': 'blue'},
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            },
            domain = {'x': [0, 1], 'y': [0, 1]}
        )
    )

    # Add the labels to the figure
    for i in range(len(ranges)-1):
        fig.add_annotation(
            x = (ranges[i] + ranges[i+1])/2,
            y = 0.5,
            showarrow = False,
            font = {'size': 16}
        )

    # Display the figure
    st.plotly_chart(fig, use_container_width=True)



def getMajorityValues(objectives):
    result = {"Daily": {"equities": 0, "commodities": 0, "currencies": 0, "yeilds": 0, "gold":0, "VIX":0}, "Weekly":{"equities": 0, "commodities": 0, "currencies": 0, "yeilds": 0, "gold":0, "VIX":0},"Monthly":{"equities": 0, "commodities": 0, "currencies": 0, "yeilds": 0, "gold":0, "VIX":0}}
    for freq in result.keys():
        count = 0
        for type in result[freq].keys():
            l = []
            for asset in objectives[type].keys():
                l.append(objectives[type][asset][freq])
            result[freq][type] = max(l,key=l.count)
            count+=max(l,key=l.count)
        result[freq]["count"] = count
        
    return result

def getDatafromAPI(url):

    response = requests.get(url,headers = {'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    i = 0
    rows = []
    for table in tables:
        i+=1
        rows1 = []
        for tr in table.find_all('tr'):
            row = []
            for td in tr.find_all(['td', 'th']):
                row.append(td.get_text().strip())
            rows1.append(row)
        if i!=1:
            rows.extend(rows1[1:])
        else:
            rows.extend(rows1)


    df = pd.DataFrame(rows[1:], columns=rows[0])
    k = url.rfind("/")
    df.columns.values[1] = "name"
    # df.to_csv(url[k+1:]+".csv")
    
    return df

def getCommodityDatafromAPI(url):
    response = requests.get(url,headers = {'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    i = 0
    rows = []
    for table in tables:
        i+=1
        rows1 = []
        for tr in table.find_all('tr'):
            row = []
            for td in tr.find_all(['td', 'th']):
                row.append(td.get_text().strip())
            rows1.append(row)
        if i!=1:
            rows.extend(rows1[1:])
        else:
            rows.extend(rows1)

    for i in range(1,len(rows)):
        k = rows[i][0].find("\n")
        rows[i][0] = rows[i][0][:k]


    df = pd.DataFrame(rows[1:], columns=rows[0])
    k = url.rfind("/")
    df.columns.values[1] = "name"
    # df.to_csv(url[k+1:]+".csv")
    
    return df


with st.spinner('Downloading data, please wait....'):

    stock_df = getDatafromAPI(url = 'https://tradingeconomics.com/stocks')
    commodities_df = getCommodityDatafromAPI(url = 'https://tradingeconomics.com/commodities')
    bonds_df = getDatafromAPI(url = 'https://tradingeconomics.com/bonds')
    # currencies_df = getDatafromAPI(url = 'https://tradingeconomics.com/currencies')

    # Risk on - Equities - UP, Safe Heaven - DOWN, High Beta - UP, Commodities - UP, GovtBonds - DOWN
    #"AU02Y": 0, "GB02Y": 0, "CH02Y": 0, "DE02Y": 0, "NZ02Y": 0, "CA02Y": 0, "US02Y": 0, "JP02Y": 0, "AU05Y": 0, "GB05Y": 0, "CH05Y": 0, "DE05Y": 0, "NZ05Y": 0, "CA05Y": 0, "US05Y": 0, "JP05Y": 0, 
    objectives = {"equities": {"EU50": 0, "FR40": 0, "DE40": 0, "AU200": 0, "USNDX": 0, "JP225": 0, "GB100": 0, "US30": 0, "US500": 0, "HK50": 0, "CATSX": 0, "CH20": 0, "ES35": 0, "SHANGHAI":0, "NZX 50":0},
                "commodities": {"Crude Oil": 0, "Brent": 0, "Coal": 0, "Silver": 0, "Copper": 0, "Iron Ore": 0, "Platinum": 0, 'Natural gas':0}, 
                "currencies": {"AUD_CHF": 0, "AUD_JPY": 0, "AUD_USD": 0, "CAD_JPY": 0, "CAD_CHF": 0, "USD_CAD": 0, "NZD_USD": 0, "NZD_CHF": 0, "NZD_JPY": 0},
                "yeilds": {"Australia": 0, "United Kingdom": 0, "Switzerland": 0, "Germany": 0, "New Zealand": 0, "Canada": 0, "United States": 0, "Japan": 0},
                "gold": {"Gold":0},
                "VIX":{"VIX": {"Daily":-1, "Weekly":-1, "Monthly":-1}}}
    
    indicator = {"Daily":0,"Weekly":0,"Monthly":0}
    
    print(commodities_df.head())

    objectives = fillStockData(stock_df, "equities", objectives)
    objectives = fillBondsData(bonds_df, "yeilds", objectives)
    objectives = fillCommoditiesData(commodities_df, "commodities", objectives)
    objectives = fillCommoditiesData(commodities_df, "gold", objectives)
    objectives = fillCurrencyData("currencies", objectives)

    result = getMajorityValues(objectives)
    print(objectives)
    print("***************")
    print("***************")
    print(result)

st.success('Done!')

gaugemeter(result["Daily"]["count"])
if result["Daily"]["count"]<-2:
    st.title("Daily is in Risk off mode", anchor=None)
elif result["Daily"]["count"]>=-2 and result["Daily"]["count"]<=2 :
    st.title("Daily is in Neutral mode", anchor=None)
else:
    st.title("Daily is in risk On mode", anchor=None)
gaugemeter(result["Weekly"]["count"])
if result["Weekly"]["count"]<-2:
    st.title("Weekly is in Risk off mode", anchor=None)
elif result["Weekly"]["count"]>=-2 and result["Weekly"]["count"]<=2 :
    st.title("Weekly is in Neutral mode", anchor=None)
else:
    st.title("Weekly is in risk On mode", anchor=None)

gaugemeter(result["Monthly"]["count"])
if result["Monthly"]["count"]<-2:
    st.title("Monthly is in Risk off mode", anchor=None)
elif result["Monthly"]["count"]>=-2 and result["Monthly"]["count"]<=2 :
    st.title("Monthly is in Neutral mode", anchor=None)
else:
    st.title("Monthly is in risk On mode", anchor=None)

st.text("")
st.text("")
st.text("")
st.text("")
original_title = '<p style="font-family:Courier; color:White; font-size: 15px;">## Values from -6 to -2 is Risk Off</p>'
st.markdown(original_title, unsafe_allow_html=True)
original_title = '<p style="font-family:Courier; color:White; font-size: 15px;">## Values from -2 to 2 is Neutral</p>'
st.markdown(original_title, unsafe_allow_html=True)
original_title = '<p style="font-family:Courier; color:White; font-size: 15px;">## Values from 2 to 6 is Risk On</p>'
st.markdown(original_title, unsafe_allow_html=True)








