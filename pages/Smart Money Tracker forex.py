import cot_reports as cot
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

import seaborn as sns
import matplotlib.pyplot as plt
import base64
import requests
import json

def getRetailData():
    url = 'https://raw.githubusercontent.com/kukr3207/forex_demo_auto_run1/master/retail_data.json'
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        json_data = json.loads(req.content)
        df = pd.json_normalize(json_data)
    else:
        print('Content was not found.')
        
    return df

def calculate_percentile(data, point):
    sorted_data = np.sort(data)

    index = np.searchsorted(sorted_data, point)

    percentile = (index / len(sorted_data)) * 100

    return percentile

def find_extreme_points(data):
    diff = np.diff(data)
    extreme_points = []
    sign_changes = np.where(np.diff(np.sign(diff)))[0]

    for index in sign_changes:
        if diff[index] < 0:
            extreme_points.append((index + 1, data[index + 1], 'peak'))
        else:
            extreme_points.append((index + 1, data[index + 1], 'trough'))

    return extreme_points

def retail_data(df,asset):
   df.sort_values(by=asset+".timestamp", inplace = True) 
   data = list(df[asset+".long"]) 
   fig, ax = plt.subplots()
   print(df)
   ax.plot(df[asset+".timestamp"], df[asset+".long"], label='Line Chart')
    # Set chart title and labels
   ax.set_title('Retail data ' + asset)
   ax.set_xlabel('Date')
   ax.set_ylabel('% long')
   st.pyplot(fig)

def stretch_data(df_data):
   df_data.sort_values(by='Date', inplace = True) 
   data = list(df_data["%OI"]) 
   l = []
   for i in data:
    percentile = calculate_percentile(data, i)
    l.append(percentile)
    
   df_data["OI stretched"] = l
   extreme_points = find_extreme_points(list(df_data["OI stretched"]))
   k1,k2=[],[]
   for point in extreme_points:
        if point[1]>=50 and point[2]=="peak":
            k1.append(point[1])  
        elif point[1]<50 and point[2]=="peak":
            k2.append(point[1])

   k11 = round(sum(k1)/len(k1),2)
   k22 = round(sum(k2)/len(k2),2)

   fig, ax = plt.subplots()
   ax.plot(df_data["Date"], df_data["OI stretched"], label='Line Chart')
   ax.axhline(k11, color='red', linestyle='--', label='Horizontal Line 1')
   ax.axhline(k22, color='green', linestyle='--', label='Horizontal Line 2')
   ax.text(0, k11, k11, ha='right', va='bottom', color='red')
   ax.text(0, k22, k22, ha='right', va='top', color='green')

    # Set chart title and labels
   ax.set_title('OI stretched data')
   ax.set_xlabel('Date')
   ax.set_ylabel('OI %')
    # Display the chart using Streamlit
   st.pyplot(fig)


def getData():
    df = pd.DataFrame()
    begin_year = 2017
    end_year = 2023
    for i in range(begin_year, end_year + 1):
        single_year = pd.DataFrame(cot.cot_year(i, cot_report_type='legacy_futopt')) 
        df = df.append(single_year, ignore_index=True)
    df1 = df[['Market and Exchange Names','As of Date in Form YYYY-MM-DD','Noncommercial Positions-Long (All)','Noncommercial Positions-Short (All)','Change in Noncommercial-Long (All)','Change in Noncommercial-Short (All)','Open Interest (All)','Change in Open Interest (All)','% of Open Interest (OI) (All)','% of OI-Noncommercial-Long (All)','% of OI-Noncommercial-Short (All)']]
    df1.rename(columns={'Market and Exchange Names': 'Asset', 'As of Date in Form YYYY-MM-DD': 'Date', 'Noncommercial Positions-Long (All)': 'Long', 'Noncommercial Positions-Short (All)': 'Short', 'Change in Noncommercial-Long (All)': 'Change Long', 'Change in Noncommercial-Short (All)': 'Change Short', 'Open Interest (All)' : "OI ALL",'Change in Open Interest (All)' : "OI ALL change",'% of Open Interest (OI) (All)': "%OI ALL",'% of OI-Noncommercial-Long (All)': "%OI ALL Long",'% of OI-Noncommercial-Short (All)': "%OI ALL short"}, inplace=True)
    df1["% Long"] = (df1['Long'] / (df1['Long'] + df1['Short'])) * 100
    df1["% Short"] = (df1['Short'] / (df1['Long'] + df1['Short'])) * 100
    df1["Net Positions"] = df1['Long'] - df1['Short']
    df1["%OI"] = df1["%OI ALL Long"] - df1["%OI ALL short"]

    return df1

def fillColor(df_data):
    cm = sns.light_palette("green", as_cmap=True)
    cm1 = sns.light_palette("red", as_cmap=True)
    df_data = df_data.style.background_gradient(cmap=cm, subset=pd.IndexSlice[:, ['Long', 'Net Positions']]).set_precision(2).background_gradient(cmap=cm1, subset=pd.IndexSlice[:, ['Short']]).set_precision(2)
    return df_data



with st.spinner('Downloading data, please wait....'):
    df = getData()
    retail_df = getRetailData()
st.success('Done!')


forex,cad, chf, peso, gbp, jpy, usd, eur, nzd, rand, aud, eur_gbp,eur_jpy = st.tabs(["Forex Overall", 'CAD', "CHF", 
                                                      "PESO", "GBP", "JPY","USD", "EUR", "NZD", "RAND","AUD","EUR/GBP", "EUR/JPY"])

with forex:
   l = ['CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE','SWISS FRANC - CHICAGO MERCANTILE EXCHANGE',
'MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE','BRITISH POUND - CHICAGO MERCANTILE EXCHANGE','JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE','USD INDEX - ICE FUTURES U.S.','EURO FX - CHICAGO MERCANTILE EXCHANGE',
'NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE','SO AFRICAN RAND - CHICAGO MERCANTILE EXCHANGE',
'AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE','EURO FX/BRITISH POUND XRATE - CHICAGO MERCANTILE EXCHANGE','EURO FX/JAPANESE YEN XRATE - CHICAGO MERCANTILE EXCHANGE']

   l1 = ['CAD', "CHF", "PESO", "GBP", "JPY", "USD", "EUR", "NZD", "RAND", "AUD","EUR/GBP", "EUR/JPY"]

   df_data = df[df["Asset"].isin(l)]

   for i in range(len(l)):
      df_data.loc[df_data['Asset'] == l[i], 'Asset'] = l1[i]
      
   df_data = df_data[df_data["Date"]==df_data['Date'].max()]
   df_data = df_data.sort_values('% Long')
   df_data.set_index('Asset', inplace=True)
   fig, ax = plt.subplots()
   df_data[["% Long", "% Short"]].plot.bar(stacked=True, ax=ax)
   ax.set_xlabel('Asset Type')
   ax.set_ylabel('Percentage')
   ax.set_title('Overall Smart Money tracker')
   ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
   st.pyplot(fig)

with eur:
   st.header("Euro Smart Money tracker")
   df_data = df[df["Asset"] == 'EURO FX - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()
   df_data = fillColor(df_data)
   st.dataframe(df_data)

   stretch_data(df_data1)
   retail_data(retail_df,"EURUSD")
   retail_data(retail_df,"EURJPY")
   retail_data(retail_df,"EURAUD")

   
with jpy:
   st.header("Japan Smart Money tracker")
   df_data = df[df["Asset"] == 'JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()
   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)

with usd:
   st.header("USD Smart Money tracker")
   df_data = df[df["Asset"] == 'USD INDEX - ICE FUTURES U.S.'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)
   retail_data(retail_df,"USDX")
   retail_data(retail_df,"USDJPY")
   retail_data(retail_df,"USDCHF")
   retail_data(retail_df,"USDCAD")

with cad:
   st.header("Canada Smart Money tracker")
   df_data = df[df["Asset"] == 'CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)

with aud:
   st.header("Australia Smart Money tracker")
   df_data = df[df["Asset"] == 'AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)
   retail_data(retail_df,"AUDUSD")
   retail_data(retail_df,"AUDJPY")

with gbp:
   st.header("UK Smart Money tracker")
   df_data = df[df["Asset"] == 'BRITISH POUND - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)
   retail_data(retail_df,"GBPUSD")
   retail_data(retail_df,"GBPJPY")

with nzd:
   st.header("New Zealaand Smart Money tracker")
   df_data = df[df["Asset"] == 'NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)
   retail_data(retail_df,"NZDUSD")

with chf:
   st.header("Swiss Smart Money tracker")
   df_data = df[df["Asset"] == 'SWISS FRANC - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)

with eur_gbp:
   st.header("EUR/GBP Smart Money tracker")
   df_data = df[df["Asset"] == 'EURO FX/BRITISH POUND XRATE - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)

with eur_jpy:
   st.header("EUR/JPY Smart Money tracker")
   df_data = df[df["Asset"] == 'EURO FX/JAPANESE YEN XRATE - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)


with peso:
   st.header("Mexican peso Smart Money tracker")
   df_data = df[df["Asset"] == 'MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)

with rand:
   st.header("African rand Smart Money tracker")
   df_data = df[df["Asset"] == 'SO AFRICAN RAND - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()

   df_data = fillColor(df_data)
   st.dataframe(df_data)
   stretch_data(df_data1)

      