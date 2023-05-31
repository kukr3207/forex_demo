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
st.success('Done!')


index,vix, btc, sp500, nasdaq100,russell_emini,jpy_index = st.tabs(["Index Overall", "VIX", "BTC", "S&P500",
                                                      "NASDAQ100", "RUSSELL E-MINI","JAPAN INDEX"])

with index:
   l = ['VIX FUTURES - CBOE FUTURES EXCHANGE',
  'BITCOIN - CHICAGO MERCANTILE EXCHANGE',
  'E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE',
  'NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE',
  'RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE',
  'NIKKEI STOCK AVERAGE - CHICAGO MERCANTILE EXCHANGE']

   l1 = ['VIX', "BTC", "S&P500", "NASDAQ100", "RUSSELL_EMINI", "JPY_INDEX"]

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

with vix:
   st.header("VIX Smart Money tracker")
   df_data = df[df["Asset"] == 'VIX FUTURES - CBOE FUTURES EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()
   df_data = fillColor(df_data)
   st.dataframe(df_data)

   stretch_data(df_data1)
   
with btc:
   st.header("Bitcoin Smart Money tracker")
   df_data = df[df["Asset"] == 'BITCOIN - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()
   df_data = fillColor(df_data)
   st.dataframe(df_data)

   stretch_data(df_data1)

with sp500:
   st.header("S&P500 Smart Money tracker")
   df_data = df[df["Asset"] == 'E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()
   df_data = fillColor(df_data)
   st.dataframe(df_data)

   stretch_data(df_data1)

with nasdaq100:
   st.header("Nasdaq100 Smart Money tracker")
   df_data = df[df["Asset"] == 'NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()
   df_data = fillColor(df_data)
   st.dataframe(df_data)

   stretch_data(df_data1)

with russell_emini:
   st.header("RUSSELL E-MINI Smart Money tracker")
   df_data = df[df["Asset"] == 'RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()
   df_data = fillColor(df_data)
   st.dataframe(df_data)

   stretch_data(df_data1)

with jpy_index:
   st.header("JAPAN INDEX Smart Money tracker")
   df_data = df[df["Asset"] == 'NIKKEI STOCK AVERAGE - CHICAGO MERCANTILE EXCHANGE'].iloc[:,1:]
   df_data1 = df_data.copy()
   df_data = fillColor(df_data)
   st.dataframe(df_data)

   stretch_data(df_data1)
