from matplotlib import pyplot as plt
import tushare as ts
import pandas as pd
import numpy as np
import os

from config import Config


def draw():
    plt.title("收益率变化情况")
    plt.xlabel("时间")
    plt.ylabel("收益率")
    # plt.show()
    path_list = os.listdir("data/{}/stock_income".format(Config.stock_list_date))
    for path in path_list:
        income = pd.read_csv("data/{}/stock_income/{}".format(Config.stock_list_date, path)).values
        avg_profit = sum([i[1] for i in income]) / len(income)
        print(avg_profit)


draw()