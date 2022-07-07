#Import Packages
from os import path
import pandas as pd
import numpy as np
import requests
import json
import datetime as dt
from bs4 import BeautifulSoup as Soup
import talib as ta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
import plotly

########################################################################################################################
#Global Variables
ticker = 'BTC'
time_start = '2017-01-01'
time_end = dt.datetime.today().strftime('%Y-%m-%d')

########################################################################################################################
#Import Data

'''Price/Indicator Data'''
#CoinAPI.io
api_key = 'AD0B6C3A-2B4C-4394-B1C3-3CE294250F27'
url_coinAPI = f"https://rest.coinapi.io/v1/ohlcv/{ticker}/USD/history?period_id=1DAY&time_start={time_start}T00:00:00&time_end={time_end}T23:59:00&limit=100000"
headers = {"X-CoinAPI-Key" : api_key}
response = requests.get(url_coinAPI, headers = headers)
if(response.status_code == 429):
    # API response
    print("Too many requests.")
coinAPI_data  = json.loads(response.text)
price_data = pd.DataFrame(coinAPI_data).drop(['time_period_end','time_open','time_close','trades_count'],axis = 'columns').rename(columns={'time_period_start':'date'})
price_data['date']=pd.to_datetime(price_data['date']).dt.date

#Indicator Calculations
'''TA Variables'''
close = price_data['price_close']
open = price_data['price_open']
high = price_data['price_high']
low = price_data['price_low']
volume = price_data['volume_traded']

'''Overlap Studies'''
price_data['EMA_21']=ta.EMA(close,timeperiod=21)
price_data['EMA_50']=ta.EMA(close,timeperiod=50)
price_data['EMA_100']=ta.EMA(close,timeperiod=100)
price_data['EMA_200']=ta.EMA(close,timeperiod=200)
price_data['SAR'] = ta.SAR(high,low)
#TODO ICHIMOKU

'''Momentum Indicators'''
price_data['ADX'] = ta.ADX(high,low,close,timeperiod=14)
price_data['AROON'] = ta.AROONOSC(high,low,timeperiod=14)
price_data['CCI'] = ta.CCI(high,low,close,timeperiod=14)
price_data['MFI'] = ta.MFI(high,low,close,volume,timeperiod=14)
price_data['ROC'] = ta.ROC(close,timeperiod=10)
price_data['RSI'] = ta.RSI(close,timeperiod=14)
stoch_list = ta.STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
price_data['STOCH_K']=stoch_list[0]
price_data['STOCH_D']=stoch_list[1]
stoch_RSI_list = ta.STOCHRSI(close, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
price_data['STOCHRSI_K']=stoch_RSI_list[0]
price_data['STOCHRSI_D']=stoch_RSI_list[1]
#TODO TDI

'''Volume Indicators'''
price_data['AD'] = ta.AD(high,low,close,volume)
price_data['ADOSC'] = ta.ADOSC(high,low,close,volume,fastperiod=3,slowperiod=10)
price_data['OBV'] = ta.OBV(close,volume)

'''Volatility'''
price_data['ATR'] = ta.ATR(high,low,close,timeperiod=14)
price_data['NATR'] = ta.NATR(high,low,close,timeperiod=14)

'''Candle Recognition'''
price_data['THREEBLACKCROWS'] = ta.CDL3BLACKCROWS(open,high,low,close)
price_data['BREAKAWAY'] = ta.CDLBREAKAWAY(open,high,low,close)
price_data['DOJI'] = ta.CDLDOJI(open,high,low,close)
price_data['DOJISTAR'] = ta.CDLDOJISTAR(open,high,low,close)
price_data['EVENINGDOJISTAR'] = ta.CDLEVENINGSTAR(open,high,low,close,penetration = 0)
price_data['ECENINGSTAR'] = ta.CDLEVENINGDOJISTAR(open,high,low,close,penetration = 0)
price_data['GRAVESTONEDOJI'] = ta.CDLGRAVESTONEDOJI(open,high,low,close)
price_data['HAMMER'] = ta.CDLHAMMER(open,high,low,close)
price_data['HANGINGMAN'] = ta.CDLHANGINGMAN(open,high,low,close)
price_data['HARAMI'] = ta.CDLHARAMI(open,high,low,close)
price_data['HARAMICROSS'] = ta.CDLHARAMICROSS(open,high,low,close)
price_data['INVERTEDHAMMER'] = ta.CDLINVERTEDHAMMER(open,high,low,close)
price_data['MORINGDOJISTAR'] = ta.CDLMORNINGDOJISTAR(open,high,low,close,penetration = 0)
price_data['MORNINGSTAR'] = ta.CDLMORNINGSTAR(open,high,low,close,penetration = 0)
price_data['SHOOTINGSTAR'] = ta.CDLSHOOTINGSTAR(open,high,low,close)
price_data['SPINNINGTOP'] = ta.CDLSPINNINGTOP(open,high,low,close)

price_data.to_csv(f'{ticker}_historical_data.csv', index = False)

#COT Data
#Fear and Greed Data
url_fear_greed = 'https://api.alternative.me/fng/?limit=0&date_format=kr'
response_fear_greed = requests.get(url_fear_greed)
fear_greed_API = json.loads(response_fear_greed.text)
fear_greed_df = pd.DataFrame(fear_greed_API['data'])\
    .drop(['time_until_update'],axis = 'columns')\
    .rename(columns={'value_classification':'fear_greed_class','value':'fear_greed_value','timestamp':'date'})\
    .sort_values('date')

#Long/Short Ratio Data
#url_long_short = 'https://www.binance.com/futures/data/globalLongShortAccountRatio/?symbol=BTCUSDT&period=1d'
url_long_short = 'https://open-api.coinglass.com/api/pro/v1/futures/longShort_chart?symbol=BTC&interval=5'
long_short_api_key = {'coinglassSecret':'2f32f417b9e04665a47b65792cc89e58'}
response_long_short = requests.get(url_long_short,headers = long_short_api_key)
long_short_API = json.loads(response_long_short.text)
long_short_df = pd.DataFrame(long_short_API)



#CBBI Data
#Bitcoin Dominance Data
#Glassnode Data
#S&P 500 Data/Traditional Markets
#DXY Data
#Twitter Sentiment Data
#Google Search History Data

########################################################################################################################
#Merge Data


########################################################################################################################
#Build Model


########################################################################################################################
#Assess Model


########################################################################################################################
#Figures












