import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pprint
import json
import seaborn as sns

#GET A LIST WITH ALL THE AVAILABLE CRYPTO CURRENCIES
#RETURNS A DICT WITH ALL THE COINS AND THEIR ATTRIBUTES
def coin_list():
    url = 'https://www.cryptocompare.com/api/data/coinlist/'
    page = requests.get(url)
    data = page.json()['Data']
    return data

def get_top(num):
    coindict = coin_list()
    top=[]
    for c,v in coindict.items():
        for i in range(1,num+1):
            if v['SortOrder'] == str(i):
                top.append(v['Symbol'])
    return top

#LETS GET THE CURRENT PRICES FOR THE TOP-5 COINS
# https://www.cryptocompare.com/api/#-api-data-price-
def price(symbol, comparison_symbols=['EUR'], exchange=''):
    url = 'https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}'\
            .format(symbol.upper(), ','.join(comparison_symbols).upper())
    if exchange:
        url += '&e={}'.format(exchange)
    page = requests.get(url)
    data = page.json()
    return data

#LETS GET THE HISTORICAL DAILY PRICES FOR THE TOP-5 COINS
def daily_price_historical(symbol, comparison_symbol, limit=1, aggregate=1, exchange='', allData='True'):
    url = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&limit={}&aggregate={}&allData={}'\
            .format(symbol.upper(), comparison_symbol.upper(), limit, aggregate, allData)
    if exchange:
        url += '&e={}'.format(exchange)
    page = requests.get(url)
    data = page.json()['Data']
    df = pd.DataFrame(data)
    df['timestamp'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
    return df

#LETS GET THE HOURLY HISTORICAL PRICE
def hourly_price_historical(symbol, comparison_symbol, limit, aggregate, exchange=''):
    url = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&limit={}&aggregate={}'\
            .format(symbol.upper(), comparison_symbol.upper(), limit, aggregate)
    if exchange:
        url += '&e={}'.format(exchange)
    page = requests.get(url)
    data = page.json()['Data']
    df = pd.DataFrame(data)
    df['timestamp'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
    return df

#LETS GET THE MINUTELY HISTORICAL DATA
def minute_price_historical(symbol, comparison_symbol, limit, aggregate, exchange=''):
    url = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&limit={}&aggregate={}'\
            .format(symbol.upper(), comparison_symbol.upper(), limit, aggregate)
    if exchange:
        url += '&e={}'.format(exchange)
    page = requests.get(url)
    data = page.json()['Data']
    df = pd.DataFrame(data)
    df['timestamp'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
    return df

#PLOT THE HISTORICAL DAILY PRICES FOR THE TOP 3
def plot_top_history(top5,scale):
    clr=['red','blue','green','orange','purple','tomato','olive','lime','teal','black','sienna','grey','cyan','pink','lavender']
    for i in range(0,len(top5)):
        df = daily_price_historical(top5[i],'EUR')
        df.to_csv(str(top5[i])+".csv")
        plt.plot(df.timestamp, df.close , label = str(top5[i]) , c=clr[i])
    plt.legend()
    plt.yscale(scale)
    plt.xlabel("Date")
    plt.ylabel("Price in Euro")
    plt.grid()
    plt.xticks(rotation=45)
    plt.show()

#timedelta bar width in hours
#period: timedelta * period / 24 = days
def plot_top_hourly_historical(top5,scale,timedelta,period):
    clr=['red','blue','green','orange','purple','tomato','olive','lime','teal','lavender','grey','cyan','black','pink','sienna']
    for i in range(0, len(top5)):
        df = hourly_price_historical(top5[i], 'EUR', period, timedelta)
        plt.plot(df.timestamp, df.close, label=str(top5[i]), c=clr[i])
        print('Max length = %s' % len(df))
        print('Max time = %s' % (df.timestamp.max() - df.timestamp.min()))
    plt.yscale(scale)
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Price in Euro")
    plt.xticks(rotation=45)
    plt.show()

#period: timedelta * period / 60 = hours
def plot_top_minute_historical(top5,scale,timedelta,period):
    clr=['red','blue','green','orange','purple','tomato','olive','lime','teal','lavender','grey','cyan','black','pink','sienna']
    for i in range(0, len(top5)):
        df = minute_price_historical(top5[i], 'EUR', period, timedelta)
        plt.plot(df.timestamp, df.close, label=str(top5[i]), c=clr[i])
        print('Max length = %s' % len(df))
        print('Max time = %s' % (df.timestamp.max() - df.timestamp.min()))
    plt.xticks(rotation=45)
    plt.yscale(scale)
    plt.xlabel("Date")
    plt.ylabel("Price in Euro")
    plt.legend()
    plt.show()

def live_social_status(symbol, symbol_id_dict={}):
    if not symbol_id_dict:
        symbol_id_dict = {
            'BTC': 1182,
            'ETH': 7605,
            'LTC': 3808
        }
    symbol_id = symbol_id_dict[symbol.upper()]
    url = 'https://www.cryptocompare.com/api/data/socialstats/?id={}'\
            .format(symbol_id)
    page = requests.get(url)
    data = page.json()['Data']
    return data

def get_correlation(top):
    newdf = pd.DataFrame(columns=top)
    for i in range(0,len(top)):
        df = hourly_price_historical(top[i],'EUR',30,24)
        df.to_csv(str(top[i])+".csv")
        newdf[top[i]] = df.close
        newdf['timestamp']=df.timestamp
    corr = newdf.corr()
    f, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, mask=np.zeros_like(corr, dtype=np.bool), cmap=sns.diverging_palette(220, 10, as_cmap=True),
                square=True, ax=ax)
    plt.show()
    print (newdf)



# print (price('LTC',exchange="Coinbase"))
#print (daily_price_historical('BTC','EUR'))
top = get_top(10)
# print (top)
# top.pop(2)
# print (top)
#plot_top_history(top,'log')
plot_top_hourly_historical(top,'linear',1,360)
#plot_top_minute_historical(top,'linear',1,360)
#pprint.pprint (live_social_status('ETH'))
# pprint.pprint (live_social_status('ETH')['Facebook'])
# pprint.pprint (live_social_status('ETH')['Twitter'])
# pprint.pprint (live_social_status('ETH')['Reddit'])
#get_correlation(top)