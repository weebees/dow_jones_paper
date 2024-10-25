from utils import folder_manipulation
from utils.folder_manipulation import write_to_excel

import datetime
import pandas as pd
import yfinance as yf
import empyrical as ep
import sys
import json
import numpy as np
import os
import math

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


# Collate maximum drawdown:
for n0 in [5, 10]:
    for return_type in ["Returns"]:
        dfs = []
        for tenure in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
            dx = pd.DataFrame()
            for split in ["Winners", "Losers", "Median", "Equal", "^DJI"]:
                df = pd.read_csv(f"./maximum_drawdowns/{return_type}/Results-{n0*2}/{tenure}.csv", index_col="Year")
                dx[split] = df[split]
            for split in ["Winners", "Losers", "Median", "Equal"]:
                dx[f"TE {split}"] = dx[f"{split}"] - dx["^DJI"]

            rq = ["Winners", "TE Winners", "Losers", "TE Losers",
                  "Median", "TE Median",
                  "Equal", "TE Equal", "^DJI"]

            rq2 = ["Winners", "Losers", "Median", "Dogs", "Equal", "^DJI"]
            dx = round(dx, 2)
            dx.index = list(range(1998, 1998 + len(dx)))
            dx = dx[rq]
            dfs.append((dx, f"{tenure}"))
            # Plotting the data
            plt.figure(figsize=(15, 8))  # Optional: Set the figure size

            # Loop through each strategy and plot a line for it
            strategies = dx[rq2]  # Exclude the 'Year' column from the strategies
            colors = ["green", "red", "orange", "blue", "brown"]
            for i, strategy in enumerate(strategies):
                if strategy.lower() == "median":
                    plt.plot(df.index, dx[strategy], label=strategy, color=colors[i], linewidth=5)
                else:
                    plt.plot(df.index, dx[strategy], label=strategy, color=colors[i], linewidth=2)

            plt.xlabel("Year")
            plt.ylabel("Maximum drawdown")
            plt.title(f"Maximum drawdown {tenure}")
            plt.legend()
            plt.grid()
            folder_manipulation.create_folder_if_not_exists(f"./Maximum_drawdown_graphs")
            plt.savefig(f"./Maximum_drawdown_graphs/{tenure}_portfolio.jpeg")

        write_to_excel(dfs, f"./maximum_drawdowns/{return_type}/Results-{n0*2}/Max_dd.xlsx", "Year")
sys.exit()
# Collate tables:
for n0 in [5, 10]:
    for return_type in ["Returns"]:
        dfs = []
        for tenure in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
            dx = pd.DataFrame()
            for split in ["Winners", "Losers", "Median", "Dogs", "Equal", "^DJI"]:
                df = pd.read_csv(f"./Tables/{return_type}/Results-{n0*2}/{tenure}/{split}.csv")
                dx[split] = df[split]*100
            for split in ["Winners", "Losers", "Median", "Equal"]:
                dx[f"TE DJI {split}"] = dx[f"{split}"] - dx["^DJI"]

            rq = ["Winners", "TE DJI Winners", "Losers", "TE DJI Losers",
                  "Median", "TE DJI Median",
                  "Equal", "TE DJI Equal", "^DJI"]

            dx = round(dx, 2)
            dx.index = list(range(1998, 1998 + len(dx)))
            dx = dx[rq]
            dx.to_csv(f"./Tables/{return_type}/Results-{n0*2}/{tenure}.csv", index_label="Year")
        #     dfs.append((dx, tenure))
        #
        # write_to_excel(dfs, f"./Results/{return_type}/Table.xlsx", "Year")


for return_type in ["Returns"]:
    dfs = []
    for n0 in [5, 10]:
        for tenure in ["daily", "weekly", "biweekly", "monthly", "quarterly", "halfyearly", "annually"]:
            df = pd.read_csv(f"./Tables/{return_type}/Results-{n0*2}/{tenure}.csv", index_col="Year")
            dfs.append((df, tenure))
    write_to_excel(dfs, f"./Tables/{return_type}.xlsx", "Year")