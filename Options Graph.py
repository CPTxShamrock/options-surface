import matplotlib.pyplot as plt
#import mplfinance as mpf
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
import pandas as pd
import pandas_datareader.data as web
#import os, math, random, string, statistics, datetime, time
from yahoo_fin.options import *
from datetime import datetime
from requests_html import HTMLSession
#from sys import argv

def get_expiration_dates(ticker):
    site = build_options_url(ticker)
    
    session = HTMLSession()
    resp = session.get(site)
    
    html = resp.html.raw_html.decode()
    splits = html.split('tabindex="-1" data-value=') #change to split criteria
    
    dates = [elt[elt.find(">")+1:elt.find("<")-1] for elt in splits[1:]] # tweak
    dates = [elt for elt in dates if ', ' in elt] # just dates # added the space after the comma to account for expensive stocks
    
    session.close()
    
    return dates

## Creates Option chain dataFrame for Calls
def createCallChainData(ticker):
    ##Gets all expiration dates
    dates = get_expiration_dates(ticker)

    info = {}
    for date in dates:
        info[date] = get_calls(ticker, date)


    ##Builds dataFrame from dictionary
    df = pd.concat(info)

    df['Expiration Date'] = findDate(df['Contract Name'])
    df['Expiration Date'] = pd.to_datetime(df['Expiration Date'])
    df['days'] = df['Expiration Date'] - pd.to_datetime('today')
    df['days'] = df['days'].dt.days
    df['Implied Volatility'] = cleanVolNumbers(df['Implied Volatility'])

    
    return df


## Creates Option chain DataFrame for Puts
def createPutChainData(ticker):
    dates = get_expiration_dates(ticker)

    info = {}
    for date in dates:
        info[date] = get_puts(ticker, date)

    ##Builds dataFrame from dictionary
    df = pd.concat(info)

    df['Expiration Date'] = findDate(df['Contract Name'])
    df['Expiration Date'] = pd.to_datetime(df['Expiration Date'])
    df['days'] = df['Expiration Date'] - pd.to_datetime('today')
    df['days'] = df['days'].dt.days
    df['Implied Volatility'] = cleanVolNumbers(df['Implied Volatility'])

    return df


##Returns Expiration date list from Contract names
def findDate(dates):
    namesList = []

    for date in dates:
        x=0
        for i, c in enumerate(date):
            if c.isdigit():
                x=i
                break
    
        date = date[x:x+6]
        date = '20' + date
        date = datetime.strptime(date, '%Y%m%d').strftime('%m/%d/%Y')
        namesList.append(date)
    
    return namesList


def cleanVolNumbers(vol):
    volList = []

    for v in vol:
        v = v[:-1]
        v = v.replace(',', '')
        v=float(v)
        v=v/100
        volList.append(v)


    return volList


##Creates data frame of jsut needed data
def CreateVolSurfaceData(name, callOrPut):
    if callOrPut == 'call':
        df = createCallChainData(name)
    elif callOrPut == 'put':
        df = createPutChainData(name)
    else:
        return 'Error: check ticker and option type'

    plotSurface = pd.DataFrame()
    plotSurface['vol'] = pd.to_numeric(df['Implied Volatility'], downcast='float')
    plotSurface['strike'] = pd.to_numeric(df['Strike'], downcast='float')
    plotSurface['days'] = pd.to_numeric(df['days'], downcast='float')


    plotSurface.to_csv(r'plot.csv', header=True)

    return plotSurface


def plotSurface(df):
    x,y,z = df['days'], df['strike'], df['vol']
    # fig = plt.figure().add_subplot(projection='3d')
    ax = plt.figure().add_subplot(projection='3d')
    surf = ax.plot_trisurf(x, y, z, cmap=cm.jet, linewidth=.1)
    # ax.colorbar(surf, shrink=0.5, aspect=5)

    ax.set_xlabel('Days to Expiration')
    ax.set_ylabel('Strike Price')
    ax.set_zlabel('implied Volatility')

    plt.show()


# df = CreateVolSurfaceData('F', 'call')
# plotSurface(df)
# print(df)

# print(df['days'])

get_calls('msft', '10/9/2024')