#Data Manipulation
import pandas as pd
import numpy as np
import datetime
#Web Scraping
from bs4 import BeautifulSoup as Soup
import requests
import json
#Alerts
import yagmail

#######################################################################################
"""Global Variables"""
#Dates
datetime_format = '%Y-%m-%d'
today = datetime.datetime.today().strftime(datetime_format)
print(today)

#Email Alerts
sending_email_username = 'klusjason.alerts@gmail.com'
sending_email_password = 'baapukaxehkjhowu'
recipient_email_address = 'klusjason@gmail.com'

#######################################################################################
"""Binance Long-to-Short Data"""
url_long_short = 'https://www.binance.com/futures/data/globalLongShortAccountRatio/?symbol=BTCUSDT&period=1d'
reponse_long_short = requests.get(url_long_short)
long_short_API = json.loads(reponse_long_short.text)
long_short_df = pd.DataFrame(long_short_API)
#Change Epoch Timestamp to Date
long_short_df['date'] = pd.to_datetime([datetime.datetime.fromtimestamp(float(i)/1000.).strftime(datetime_format) for i in long_short_df['timestamp']])
print(f"Binance Long/Short Max Date: {long_short_df['date'].max()}")

#######################################################################################
"""Fear and Greed Data"""
url_fear_greed = 'https://api.alternative.me/fng/?limit=0&date_format=kr'
response_fear_greed = requests.get(url_fear_greed)
fear_greed_API = json.loads(response_fear_greed.text)
fear_greed_df = pd.DataFrame(fear_greed_API['data'])\
    .drop(['time_until_update'],axis = 'columns')\
    .rename(columns={'value_classification':'fear_greed_class','value':'fear_greed_value','timestamp':'date'})\
    .sort_values('date')
#Convert Date to Datetime
fear_greed_df['date'] = pd.to_datetime(fear_greed_df['date'], format=datetime_format)

#######################################################################################
"""DataFrame Join"""
merged_df = long_short_df.merge(fear_greed_df, on='date', how='left')

#######################################################################################
"""Current Environment"""
try:
    current_df = merged_df.loc[merged_df['date'] == today]
    current_long_short = float(current_df['longShortRatio'])
    print(current_long_short)
except:
    print('Today is too early')

#######################################################################################
"""Notification"""
#Bool Checks
def environment_check():
    if current_long_short < 1:
        return True
    else:
        return False

def email_notification_favorable():
    try:
        yag = yagmail.SMTP(user=sending_email_username, 
                        password=sending_email_password) 
        yag.send(to=recipient_email_address,
                subject='ALERT: Bitcoin conditions are favorable') 
        print('Sucess')     
    except:
        print('Error')  
        
def email_notification_not_favorable():
    try:
        yag = yagmail.SMTP(user=sending_email_username, 
                        password=sending_email_password) 
        yag.send(to=recipient_email_address,
                subject='Bitcoin Conditions are NOT favorable') 
        print('Sucess')     
    except:
        print('Error')  
    
#Run
if environment_check():
    email_notification_favorable()
    print('Conditions Favorable')
else:
    email_notification_not_favorable()
    print('Conditions Not Favorable')