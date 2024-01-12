import pandas as pd
import pytz
import requests
import yfinance
from bs4 import BeautifulSoup
from datetime import datetime
# https://github.com/je-suis-tm/quant-trading

def get_sp500_tickers():
    res = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = BeautifulSoup(res.content,'lxml')
    table = soup.find_all('table')[0] # 1st table
    df = pd.read_html(str(table))
    tickers = list(df[0].Symbol)
    return tickers
def get_history(ticker, period_start, period_end, granularity="d"):
    df = yfinance.Ticker(ticker).history(start=period_start,
                                         end=period_end,
                                         interval=granularity,
                                         auto_adjust=True
    ).reset_index()
    # index datetime open high low close volume
    df = df.rename(columns={"Date": "datetime",
                            "Open": "open",
                            "High": "high",
                            "Low": "low",
                            "Close": "close",
                            "Volume": "volume"}
    )
    if df.empty:
        return pd.DataFrame()
    # timezone aware
    # df["datetime"] = df["datetime"].dt.tz_localize(pytz.utc)
    df["datetime"] = df["datetime"].dt.tz_convert(pytz.utc)
    df = df.drop(columns=["Dividends", "Stock Splits"])
    df = df.set_index("datetime", drop=True)
    return df


tickers = get_sp500_tickers()
period_start = datetime(2010, 1, 1, tzinfo=pytz.utc)
period_end = datetime(2020, 1, 1, tzinfo=pytz.utc)
print(len(tickers))

import threading
def get_histories(tickers, period_start, period_end, granularity="d"):
    for i, ticker in enumerate(tickers):
        print(i)
        df = get_history(ticker, period_start, period_end)
        if i == 0:
            print(df.columns)
            print(ticker)
            print(df.head())