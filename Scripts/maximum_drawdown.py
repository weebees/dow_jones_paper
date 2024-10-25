from utils import folder_manipulation

import datetime
import pandas as pd
import yfinance as yf
import sys
import json
import numpy as np
import os
import math

capital = 100
TENURE = None
START_DATE = datetime.datetime(day=1, month=1, year=2009)
END_DATE = datetime.datetime(day=31, month=12, year=2022)
alr_print = []

indices = {
        "^DJI": "Dow Jones Industrial Average",
        "^GSPC": "S&P 500",
    }

stocks = ["MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX",
              "CSCO", "KO", "DD", "GS", "HD", "HON", "INTC", "IBM",
              "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "PG", "CRM",
              "TRV", "UNH", "VZ", "V", "WBA", "WMT", "DIS"]#, "^DJI", "EDOW", "DOW"]
print(len(stocks))

stock_list = stocks# + list(indices.keys())
print(stock_list)
SIZE = len(stocks)

rq = ["Date"]
for stock in stock_list:
    rq.append(stock)


def path_check(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def create_single_sheet(TENURE, n0, param=False):
    if param:
        df = pd.read_csv(f"./Results/Returns/Results-{n0*2}/{TENURE}/Force_dataset.csv")
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
        df = df.loc[(df["Date"] >= START_DATE) & (df["Date"] <= END_DATE)]
        return df
    else:
        dx = pd.DataFrame(columns=["Date"])
        dates = None
        for stock in stock_list:
            folder_manipulation.create_folder_if_not_exists(f"./Results/Returns/Results-{n0*2}/{TENURE}")
            df = pd.read_csv(f"./historical_data/{TENURE}/{stock}.csv")
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.loc[(df["Date"] >= START_DATE) & (df["Date"] <= END_DATE)]
            if dates is None:
                dates = df["Date"].iloc[::-1]
                dates = dates.reset_index(drop=True)
            req = df.iloc[::-1]
            req = req.reset_index()
            dx[stock] = req["Price_chg"]
        dx["Date"] = dates
        dx = dx.dropna(axis=0, how="any")
        dx = dx.reset_index(drop=True)
        dx = dx[rq]
        dx = dx[::-1]
        dx.to_csv(f"./Results/Returns/Results-{n0*2}/{TENURE}/Force_dataset.csv", index=False)
        return dx


def find_wl(df, top_bot, n0, cols):
    def applier(row):
        if top_bot == "all":
            return list(row.index)
        if top_bot == "winners":
            return list(row.nlargest(n=int(SIZE/3)).index)
        if top_bot == "losers":
            return list(row.nsmallest(n=int(SIZE/3)).index)
        if top_bot == "median":
            return list(dict(sorted(dict(row).items(), key=lambda x: x[1], reverse=True)).keys())[10:20]
        if top_bot == "average":
            return list(row.nlargest(n=n0).index) + list(row.nsmallest(n=n0).index)
        if top_bot not in alr_print:
            print(top_bot)
            alr_print.append(top_bot)

    def custom_returns(row, df):
        index = row["index"]
        count = 0
        if index != 0:
            res = df.at[index - 1, "Chosen"]
            row_sum = 0
            for symbol in res:
                count += 1
                row_sum += (row[symbol])
            if count not in alr_print:
                print(count)
                alr_print.append(count)
            return row_sum / count

    df_dates = df["Date"]
    df = df[cols]
    df["Chosen"] = df.apply(applier, axis=1)
    df["Date"] = df_dates

    df = df.reset_index(drop=True)
    df["index"] = df.index
    df["Chosen Return"] = df.apply(custom_returns, args=(df,), axis=1)
    portfolio_returns = (1 + df["Chosen Return"]).cumprod()
    df['Portfolio Returns'] = capital * portfolio_returns
    return df


def dowj():
    for n0 in [5, 10]:
        for i in ["^DJI", "^GSPC"]:
            df = pd.read_csv(f"./historical_data/{TENURE}/{i}.csv")
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.loc[(df["Date"] >= START_DATE) & (df["Date"] <= END_DATE)]
            df[f"{i}"] = df["Adj Close"].pct_change(1)
            portfolio_returns = (1 + df[f"{i}"]).cumprod()
            df['Portfolio Returns'] = capital * portfolio_returns
            df.to_csv(f"./Results/Returns/Results-{n0*2}/{TENURE}/{i}.csv", index=False)


def main(TENURE):
    for n0 in [5, 10]:
        dx = create_single_sheet(TENURE, n0, False)
        dx = dx.dropna(axis=0)
        cols = []
        for x in rq:
            if x != "Date":
                dx[x] = pd.to_numeric(dx[x], errors='coerce')
                cols.append(x)
        dx["Date"] = pd.to_datetime(dx["Date"], format="%Y-%m-%d")

        folder_manipulation.create_folder_if_not_exists(f"./Results/Returns/Results-{n0*2}/{TENURE}")
        winners = find_wl(dx.copy(), "winners", n0, cols)
        winners[rq + ["Chosen", "Chosen Return", "Portfolio Returns"]].to_csv(f"./Results/Returns/Results-{n0*2}/{TENURE}/Winners.csv", index=False)
        losers = find_wl(dx.copy(), "losers", n0, cols)
        losers[rq + ["Chosen", "Chosen Return", "Portfolio Returns"]].to_csv(f"./Results/Returns/Results-{n0*2}/{TENURE}/Losers.csv", index=False)
        median = find_wl(dx.copy(), "median", n0, cols)
        median[rq + ["Chosen", "Chosen Return", "Portfolio Returns"]].to_csv(f"./Results/Returns/Results-{n0*2}/{TENURE}/Median.csv", index=False)
        dy = find_wl(dx.copy(), "all", n0, cols)
        dy[rq + ["Chosen", "Chosen Return", "Portfolio Returns"]].to_csv(f"./Results/Returns/Results-{n0*2}/{TENURE}/Equal.csv", index=False)
        # average = find_wl(dx.copy(), "average", n0, cols)
        # average[rq + ["Chosen", "Chosen Return", "Portfolio Returns"]].to_csv(f"./Results/Returns/Results-{n0*2}/{TENURE}/Average.csv", index=False)


for tenure in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
    TENURE = tenure
    main(tenure)


###
for tenure in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
    TENURE = tenure
    dowj()