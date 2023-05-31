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
import requests
import json
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd


def getData():
    url = 'https://c.fxssi.com/api/current-ratios?filter=AUDJPY&rand=0.5203286106651004&user_id=0'

    # Make a request to the URL
    response = requests.get(url)
    data = response.json()

    timestamp =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    d = {}

    for i in data["pairs"].keys():
        d[i] = {}
        d[i]["timestamp"] = timestamp
        d[i]["long"] = float(data["pairs"][i]["average"])
        d[i]["short"] = 100 - float(data["pairs"][i]["average"])

    print(d)

    with open("./retail_data.json","r") as p:
        data1 = json.load(p)

    with open("./retail_data.json","w") as p:
        data1.append(d)
        json.dump(data1, p)

    

    return data

def fillColor(df_data):
    cm = sns.light_palette("green", as_cmap=True)
    cm1 = sns.light_palette("red", as_cmap=True)
    df_data = df_data.style.background_gradient(cmap=cm, subset=pd.IndexSlice[:, ['Long', 'Net Positions']]).set_precision(2).background_gradient(cmap=cm1, subset=pd.IndexSlice[:, ['Short']]).set_precision(2)
    return df_data

def getIGData():
   url = 'https://www.dailyfx.com/sentiment-report'

   response = requests.get(url)

   if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')

      table = soup.find('table')

      headers = [header.text for header in table.find_all('th')]

      rows = table.find_all('tr')[1:] 

      data = []
      for row in rows:
         data.append([cell.text for cell in row.find_all('td')])

      df = pd.DataFrame(data, columns=headers)

   else:
      print(f"Request to {url} failed with status code {response.status_code}.")

   df_numeric = df.applymap(percent_to_numeric)
   df_numeric.index = df_numeric["SYMBOL"]
   print(df_numeric)
   return df_numeric

def percent_to_numeric(value):
    if isinstance(value, str) and value.endswith('%'):
        return float(value[:-1])
    return value

# Apply the custom function to each element in the DataFrame


with st.spinner('Downloading data, please wait....'):
    df = getData()
    df1 = getIGData()
st.success('Done!')


forex,Broker_myfxbook, IG_sentiment_data = st.tabs(["Forex Overall", 'Broker_myfxbook','IG_sentiment_data'])

with forex:
   l = list(df["pairs"].keys())
   l1 = []

   for i in l:
       l1.append((i,float(df["pairs"][i]["average"]), 100 -  float(df["pairs"][i]["average"])))

   df_data = pd.DataFrame(l1,columns=["pair","% Long","% Short"])

   df_data = df_data.sort_values('% Long')
   df_data.set_index('pair', inplace=True)
#    df_data["pair"] = df_data.index
   fig, ax = plt.subplots()
   df_data[["% Long", "% Short"]].plot.bar(stacked=True, ax=ax)
   ax.set_xlabel('Asset Type')
   ax.set_ylabel('Percentage')
   ax.set_title('Overall Retial sentiment tracker from 10 different brokers')
   ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
   st.pyplot(fig)

with Broker_myfxbook:
   l = list(df["brokers"]["myfxbook"].keys())
   l1 = []

   for i in l:
       l1.append((i,float(df["brokers"]["myfxbook"][i]), 100 -  float(df["brokers"]["myfxbook"][i]  )))

   df_data = pd.DataFrame(l1,columns=["pair","% Long","% Short"])

   df_data = df_data.sort_values('% Long')
   df_data.set_index('pair', inplace=True)
#    df_data["pair"] = df_data.index
   fig, ax = plt.subplots()
   df_data[["% Long", "% Short"]].plot.bar(stacked=True, ax=ax)
   ax.set_xlabel('Asset Type')
   ax.set_ylabel('Percentage')
   ax.set_title('Overall Retial sentiment tracker')
   ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
   st.pyplot(fig)

with IG_sentiment_data:
#    df_data["pair"] = df_data.index



   fig, ax = plt.subplots()
   df1[["NET-LONG%", "NET-SHORT%"]].plot.bar(stacked=True, ax=ax)
   ax.set_xlabel('SYMBOL')
   ax.set_ylabel('Percentage')
   ax.set_title('Overall Retial sentiment tracker')
   ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
   st.pyplot(fig)
