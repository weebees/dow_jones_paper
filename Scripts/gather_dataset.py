import math

from utils import folder_manipulation

import datetime
import traceback
import sys
import numpy as np
import pandas as pd
import yfinance as yf

# DOW_JONES_FILE = pd.read_csv("./DowJonesList.csv")
FIRST_DATE = datetime.date(year=(datetime.datetime.now().date() - pd.Timedelta(days=25 * 365)).year, month=1, day=1)

START_DATE = datetime.datetime(day=1, month=1, year=1998)
END_DATE = datetime.datetime(day=31, month=12, year=2023)
CLOSE = "Adj Close"  # or "Adj Close"


def find_returns(df, tenure="daily"):
    """
    :param df: the dataset for any stock.
    :param tenure: "daily", "weekly", "monthly", "yearly".
    :return: A series of returns column for respective tenure.
    """
    tenure_str = f"{tenure} Returns"
    sharpe_ = 252
    if tenure == "weekly":
        resample_dict = {
            "Week_Number": "first",
            "Year_Week": "first",
            "Year": "first",
            "Month": "first",
            "Day": "first",
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Adj Close": "last",
            "Volume": "sum",
        }
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.resample("W", on="Date", closed="right", label="right").apply(resample_dict)  # resample to weekly
        df = df.reset_index()
        sharpe_ = 52

    if tenure == "monthly":
        resample_dict = {
            "Week_Number": "first",
            "Year_Week": "first",
            "Year": "first",
            "Month": "first",
            "Day": "first",
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Adj Close": "last",
            "Volume": "sum",
        }
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.resample("M", on="Date", closed="right", label="right").apply(resample_dict)  # resample to weekly
        df = df.reset_index()
        sharpe_ = 12

    if tenure == "quarterly":
        resample_dict = {
            "Week_Number": "first",
            "Year_Week": "first",
            "Year": "first",
            "Month": "first",
            "Day": "first",
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Adj Close": "last",
            "Volume": "sum",
        }
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.resample("Q", on="Date", closed="right", label="right").apply(resample_dict)  # resample to weekly
        df = df.reset_index()
        sharpe_ = 3

    if tenure == "biweekly":
        resample_dict = {
            "Week_Number": "first",
            "Year_Week": "first",
            "Year": "first",
            "Month": "first",
            "Day": "first",
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Adj Close": "last",
            "Volume": "sum",
        }
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.resample("SM", on="Date", closed="right", label="right").apply(resample_dict)  # resample to weekly
        df = df.reset_index()
        sharpe_ = 26

    if tenure == "halfyearly":
        resample_dict = {
            "Week_Number": "first",
            "Year_Week": "first",
            "Year": "first",
            "Month": "first",
            "Day": "first",
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Adj Close": "last",
            "Volume": "sum",
        }
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.resample("6M", on="Date", closed="right", label="right").apply(resample_dict)  # resample to weekly
        df = df.reset_index()
        sharpe_ = 2

    if tenure == "annually":
        resample_dict = {
            "Week_Number": "first",
            "Year_Week": "first",
            "Year": "first",
            "Month": "first",
            "Day": "first",
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Adj Close": "last",
            "Volume": "sum",
        }
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.resample("A", on="Date", closed="right", label="right").apply(resample_dict)  # resample to weekly
        df = df.reset_index()
        sharpe_ = 1
    df["Price_chg"] = df[CLOSE].pct_change()
    std_dev = np.std(df['Price_chg'], ddof=1)
    risk_free_rate = 0
    df['Sharpe_ratio'] = (df['Price_chg'] - risk_free_rate) * math.sqrt(sharpe_) / std_dev
    return df


# HistoricalData - get all info
class StockData:
    def __init__(self, stock_name):
        self.stock_name = stock_name
        self.stock = yf.Ticker(self.stock_name)
        self.df = None

    def get_stock_name(self):
        stock = self.stock_name

        if "SPY" in stock.upper():
            return stock.upper()
        return self.stock_name

    def get_stock(self, s_window=14, l_window=50, make_csv=False):
        ticker = self.stock_name
        try:
            df = yf.download(ticker)  # , start=start_date, end=end_date)
            df['Return'] = df['Adj Close'].pct_change()
            df['Price_chg'] = df['Return'] * 100
            df['Return'].fillna(0, inplace=True)
            df = df.reset_index()
            df['Date'] = pd.to_datetime(df['Date'])
            df['Month'] = df['Date'].dt.month
            df['Year'] = df['Date'].dt.year
            df['Day'] = df['Date'].dt.day
            for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
                df[col] = df[col].round(2)
            df['Weekday'] = df['Date'].dt.day_name()
            df['Week_Number'] = df['Date'].dt.strftime('%U')
            df['Year_Week'] = df['Date'].dt.strftime('%Y-%U')
            df['Short_MA'] = df['Adj Close'].rolling(window=s_window, min_periods=1).mean()
            df['Long_MA'] = df['Adj Close'].rolling(window=l_window, min_periods=1).mean()
            col_list = ['Date', 'Year', 'Month', 'Day', 'Weekday',
                        'Week_Number', 'Year_Week', 'Open',
                        'High', 'Low', 'Close', 'Volume', 'Adj Close',
                        'Return', 'Price_chg', 'Short_MA', 'Long_MA']
            col_rq = ["Date", "Close", "Adj Close", "Price_chg", 'Sharpe_ratio']
            num_lines = len(df)
            df = df.reset_index()[col_list]
            # print('read ', num_lines, ' lines of data for ticker: ', ticker)
            df = df.loc[(df["Date"] >= START_DATE) & (df["Date"] <= END_DATE)]
            daily = find_returns(df, "daily")
            weekly = find_returns(df, "weekly")
            biweekly = find_returns(df, "biweekly")
            monthly = find_returns(df, "monthly")
            quarterly = find_returns(df, "quarterly")
            annually = find_returns(df, "annually")
            halfyearly = find_returns(df, "halfyearly")
            if make_csv:
                for d in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
                    folder_manipulation.create_folder_if_not_exists(f"./historical_data/{d}")
                    folder_manipulation.create_folder_if_not_exists(f"./historical_returns/{d}")
                daily.to_csv(f"./historical_data/daily/{self.stock_name}.csv", index=False)
                daily[col_rq].to_csv(f"./historical_returns/daily/{self.stock_name}.csv", index=False)
                weekly.to_csv(f"./historical_data/weekly/{self.stock_name}.csv", index=False)
                weekly[col_rq].to_csv(f"./historical_returns/weekly/{self.stock_name}.csv", index=False)
                biweekly.to_csv(f"./historical_data/biweekly/{self.stock_name}.csv", index=False)
                biweekly[col_rq].to_csv(f"./historical_returns/biweekly/{self.stock_name}.csv", index=False)
                monthly.to_csv(f"./historical_data/monthly/{self.stock_name}.csv", index=False)
                monthly[col_rq].to_csv(f"./historical_returns/monthly/{self.stock_name}.csv", index=False)
                quarterly.to_csv(f"./historical_data/quarterly/{self.stock_name}.csv", index=False)
                quarterly[col_rq].to_csv(f"./historical_returns/quarterly/{self.stock_name}.csv", index=False)
                halfyearly.to_csv(f"./historical_data/halfyearly/{self.stock_name}.csv", index=False)
                halfyearly[col_rq].to_csv(f"./historical_returns/halfyearly/{self.stock_name}.csv", index=False)
                annually.to_csv(f"./historical_data/annually/{self.stock_name}.csv", index=False)
                annually[col_rq].to_csv(f"./historical_returns/annually/{self.stock_name}.csv", index=False)
                # print(self.stock_name, "Generated CSV.")
            self.df = df
            return df
        except Exception as error:
            traceback.print_exc()
            return None


def gathering():
    indices = {
        "^DJI": "Dow Jones Industrial Average",
        "^GSPC": "S&P 500",
        "EDOW": "Equal Weight Dow Jones",
    }

    # stocks = ["MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX",
    #               "CSCO", "KO", "DD", "GS", "HD", "HON", "INTC", "IBM",
    #               "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "PG", "CRM",
    #               "TRV", "UNH", "VZ", "V", "WBA", "WMT", "DIS"]

    # stocks = list(pd.read_csv("./stock_list.csv")["ticker"])
    # stocks = ["HP", "BAC", "RTX", "DD"]

    stocks = [] # put your stocks here, if you want this to run comment next line.

    stocks = list(pd.read_csv("./stock_list.csv")["ticker"]) + ["HP", "BAC", "RTX", "DD"]
    stock_list = stocks + list(indices.keys())

    print(len(stocks))


    print(stock_list)

    stock_info = {}
    for stock_name in stock_list:
        stock = StockData(stock_name)
        stock_info[stock_name] = stock.get_stock(make_csv=True)  # DO NOT DELETE LINE - allows downloading the data
        print(f"{stock.stock_name} = {len(stock_info[stock_name])}")


# GS (04-05-1999) -> BAC, CRM (23-06-2004) -> RTX, V (19-03-2008) -> HP, Dow (20-03-2019) -> DD
if "main" in __name__:
    gathering()
