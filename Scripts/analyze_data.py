from utils import folder_manipulation

import datetime
import pandas as pd
import yfinance as yf
import empyrical as ep
import sys
import json
import numpy as np
import os
import math
import ast

capital = 100
TENURE = None
START_DATE = datetime.datetime(day=1, month=1, year=1998)
END_DATE = datetime.datetime(day=31, month=12, year=2023)
alr_print = []

indices = {
    "^DJI": "Dow Jones Industrial Average",
    "^GSPC": "S&P 500",
    "EDOW": "Equal Weight Dow Jones",
}

# stocks = ["MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX",
#               "CSCO", "KO", "DD", "GS", "HD", "HON", "INTC", "IBM",
#               "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "PG", "CRM",
#               "TRV", "UNH", "VZ", "V", "WBA", "WMT", "DIS"]#, "^DJI", "EDOW", "DOW"]
# print(len(stocks))
#
# stock_list = stocks# + list(indices.keys())
# print(stock_list)

stocks = list(pd.read_csv("./stock_list.csv")["ticker"])
stock_list = stocks + ["HP", "BAC", "RTX", "DD"]
SIZE = len(stock_list)

rq = ["Date"]
for stock in stock_list:
    rq.append(stock)
    rq.append(f"{stock} sharpe")

rq1 = ["Date"]
for stock in stocks:
    rq1.append(stock)

print(rq)


def path_check(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def dowj():
    for TENURE in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
        for n0 in [5, 10]:
            for i in ["^DJI", "^GSPC"]:
                df = pd.read_csv(f"./historical_data/{TENURE}/{i}.csv")
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.loc[(df["Date"] >= START_DATE) & (df["Date"] <= END_DATE)]
                df[f"{i}"] = df["Adj Close"].pct_change(1)
                portfolio_returns = (1 + df[f"{i}"]).cumprod()
                df['Portfolio Returns'] = capital * portfolio_returns
                df.to_csv(f"./Results/Returns/Results-{n0 * 2}/{TENURE}/{i}.csv", index=False)
                # df.to_csv(f"./Results/Sharpe/Results-{n0*2}/{TENURE}/{i}.csv", index=False)


def find_weights(df, top_bot, n0, cols):
    def applier(row):
        if top_bot == "all":
            return list(row.index)
        if top_bot == "winners":
            return list(row.nlargest(n=int(SIZE / 3)).index)
        if top_bot == "losers":
            return list(row.nsmallest(n=int(SIZE / 3)).index)
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
            if res is not np.nan:
                for symbol in res:
                    count += 1
                    row_sum += (row[symbol])
                if count not in alr_print:
                    print(count)
                    alr_print.append(count)
                return row_sum / count

    def convert_to_list(string):
        result_str = ast.literal_eval(string)
        return result_str

    df_dates = df["Date"]
    df = df[cols]
    if top_bot != "dogs":
        df["Chosen"] = df.apply(applier, axis=1)
    else:
        dogs_df = pd.read_csv("dogs_list.csv")['dogs']
        df["Chosen"] = dogs_df.apply(convert_to_list)

    df["Date"] = df_dates

    df = df.reset_index(drop=True)
    df["index"] = df.index
    df["Chosen Return"] = df.apply(custom_returns, args=(df,), axis=1)
    portfolio_returns = (1 + df["Chosen Return"]).cumprod()
    df['Portfolio Returns'] = capital * portfolio_returns
    return df


def combine_dataset(TENURE):
    dates = None
    folder_manipulation.create_folder_if_not_exists(f"./historical_returns/{TENURE}")
    folder_manipulation.create_folder_if_not_exists(f"./historical_data/{TENURE}")
    for HD in ["historical_returns", "historical_data"]:
        dx = pd.DataFrame(columns=["Date"])
        for stock in stock_list:
            df = pd.read_csv(f"./{HD}/{TENURE}/{stock}.csv")
            df["Date"] = pd.to_datetime(df["Date"])
            if dates is None:
                dates = df["Date"].iloc[::-1]
                dates = dates.reset_index(drop=True)
            req = df.iloc[::-1]
            req = req.reset_index()
            dx[stock] = req["Price_chg"]
            dx[f"{stock} sharpe"] = req["Sharpe_ratio"]
        dx["Date"] = dates
        dx = dx.reset_index(drop=True)
        dx = dx[rq]
        dx = dx[::-1]
        dx.to_csv(f"./{HD}/{TENURE}/{TENURE}_dataset.csv", index=False)
        dx.to_csv(f"./{HD}/{TENURE}_dataset.csv", index=False)
    return dx


def manipulate():
    replace_dict = {"V": ['HP', datetime.datetime(day=23, month=9, year=2013)],
                    "V sharpe": ['HP sharpe', datetime.datetime(day=23, month=9, year=2013)],
                    "GS": ['BAC', datetime.datetime(day=23, month=9, year=2013)],
                    "GS sharpe": ['BAC sharpe', datetime.datetime(day=23, month=9, year=2013)],
                    "DOW": ['DD', datetime.datetime(day=20, month=3, year=2019)],
                    "DOW sharpe": ['DD sharpe', datetime.datetime(day=20, month=3, year=2019)],
                    "CRM": ['RTX', datetime.datetime(day=31, month=8, year=2020)],
                    "CRM sharpe": ['RTX sharpe', datetime.datetime(day=31, month=8, year=2020)]}

    not_needed = ["HP", "BAC", "DD", "RTX",
                  "HP sharpe", "BAC sharpe", "DD sharpe", "RTX sharpe"]

    for TENURE in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
        for HD in ["historical_returns", "historical_data"]:
            df = pd.read_csv(f"./{HD}/{TENURE}_dataset.csv")
            df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
            dy = pd.DataFrame()
            for col in df.columns:
                if col not in not_needed:
                    if col in list(replace_dict.keys()):
                        if TENURE in ["quarterly", "annually"]:
                            col_df1 = df.loc[df["Date"] <= replace_dict[col][1].replace(day=31, month=12)][
                                replace_dict[col][0]]
                            col_df2 = df.loc[df["Date"] > replace_dict[col][1].replace(day=31, month=12)][col]
                        else:
                            col_df1 = df.loc[df["Date"] <= replace_dict[col][1]][replace_dict[col][0]]
                            col_df2 = df.loc[df["Date"] > replace_dict[col][1]][col]
                        temp_cols = pd.concat([col_df1, col_df2])
                        dy[col] = temp_cols
                    else:
                        dy[col] = df[col]
            folder_manipulation.create_folder_if_not_exists(f"./Returns/{HD}")
            dy.to_csv(f"./Returns/{HD}/{HD}_{TENURE}_dataset.csv", index=False)


# def calculate_max_drawdown(df):
#     cumulative_returns = (1 + df).cumprod() - 1
#     running_maximum = cumulative_returns.cummax()
#     drawdown = (cumulative_returns - running_maximum) / running_maximum
#     max_drawdown = drawdown.min()
#     return "{:.2%}".format(max_drawdown)


# def calculate_max_drawdown(daily_returns_df):
#     # Calculate cumulative returns
#     cumulative_returns = (1 + daily_returns_df).cumprod()
#
#     # Calculate peak values
#     peak_values = cumulative_returns.cummax()
#
#     # Calculate drawdown
#     drawdown = (cumulative_returns - peak_values) / peak_values
#
#     # Calculate maximum drawdown
#     max_drawdown = np.min(drawdown)
#
#     return max_drawdown


def calculate_max_drawdown(returns):
    max_dd = ep.max_drawdown(returns)
    return max_dd


def main():
    for tenure in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
        combine_dataset(tenure)


def analysis():
    max_dd = []
    for tenure in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
        for n0 in [5, 10]:
            dx = pd.read_csv(f"./Returns/historical_returns/historical_returns_{tenure}_dataset.csv")
            dx = dx[["Date"] + stocks]
            cols = []
            for x in stocks:
                if x != "Date":
                    dx[x] = pd.to_numeric(dx[x], errors='coerce')
                    cols.append(x)
            dx["Date"] = pd.to_datetime(dx["Date"], format="%Y-%m-%d")
            folder_manipulation.create_folder_if_not_exists(f"./Results/Returns/Results-{n0 * 2}/{tenure}")
            winners = find_weights(dx.copy(), "winners", n0, cols)
            winners = winners[rq1 + ["Chosen", "Chosen Return", "Portfolio Returns"]]
            winners.to_csv(f"./Results/Returns/Results-{n0 * 2}/{tenure}/Winners.csv", index=False)

            losers = find_weights(dx.copy(), "losers", n0, cols)
            losers = losers[rq1 + ["Chosen", "Chosen Return", "Portfolio Returns"]]
            losers.to_csv(f"./Results/Returns/Results-{n0 * 2}/{tenure}/Losers.csv", index=False)

            median = find_weights(dx.copy(), "median", n0, cols)
            median = median[rq1 + ["Chosen", "Chosen Return", "Portfolio Returns"]]
            median.to_csv(f"./Results/Returns/Results-{n0 * 2}/{tenure}/Median.csv", index=False)

            equal = find_weights(dx.copy(), "all", n0, cols)
            equal = equal[rq1 + ["Chosen", "Chosen Return", "Portfolio Returns"]]
            equal.to_csv(f"./Results/Returns/Results-{n0 * 2}/{tenure}/Equal.csv", index=False)

            dogs = find_weights(dx.copy(), "dogs", n0, cols)
            dogs = dogs[rq1 + ["Chosen", "Chosen Return", "Portfolio Returns"]]
            dogs.to_csv(f"./Results/Returns/Results-{n0 * 2}/{tenure}/dogs.csv", index=False)

            # average = find_weights(dx.copy(), "average", n0, cols)
            # average = average[rq1 + ["Chosen", "Chosen Return", "Portfolio Returns"]]
            # average.to_csv(f"./Results/Returns/Results-{n0*2}/{tenure}/Average.csv", index=False)

            winners_dr = calculate_max_drawdown(winners["Chosen Return"])
            losers_dr = calculate_max_drawdown(losers["Chosen Return"])
            median_dr = calculate_max_drawdown(median["Chosen Return"])
            equal_dr = calculate_max_drawdown(equal["Chosen Return"])
            dogs_dr = calculate_max_drawdown(dogs["Chosen Return"])
            print("EQ", equal_dr)
            print("Dogs", dogs_dr)
            print("--")
            # average_dr = calculate_max_drawdown(average["Chosen Return"])

            max_dd.append([f"Winners", n0 * 2, tenure, round(winners_dr * 100, 2)])
            max_dd.append([f"Losers", n0 * 2, tenure, round(losers_dr * 100, 2)])
            max_dd.append([f"Median", n0 * 2, tenure, round(median_dr * 100, 2)])
            max_dd.append([f"Dogs", n0*2, tenure, round(dogs_dr * 100, 2)])
            max_dd.append([f"Equal", n0 * 2, tenure, round(equal_dr * 100, 2)])

    maxdd_df = pd.DataFrame(max_dd, columns=["Strategy", "n0", "Timeframe", "Maximum Drawdown"])
    maxdd_df1 = maxdd_df.loc[maxdd_df["n0"] == 10][["Strategy", "Timeframe", "Maximum Drawdown"]]
    maxdd_df2 = maxdd_df.loc[maxdd_df["n0"] == 20][["Strategy", "Timeframe", "Maximum Drawdown"]]

    maxdd_df1.to_csv(f"./Results/Returns/Results-10/Maximum_Drawdown.csv", index=False)
    maxdd_df2.to_csv(f"./Results/Returns/Results-20/Maximum_Drawdown.csv", index=False)


main()
manipulate()
analysis()
dowj()

import empyrical as ep


def calculate_max_drawdown(returns):
    max_dd = ep.max_drawdown(returns)
    return max_dd


# drawdowns = calculate_max_drawdown(returns["Return"])
