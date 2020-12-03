from matplotlib import pyplot as plt
import matplotlib
import tushare as ts
import pandas as pd
import numpy as np
import os
import datetime

from config import Config


def draw():
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.title("收益率变化情况")
    plt.xlabel("时间")
    plt.ylabel("收益率")
    date = []
    profit = []
    sh_profits = []
    sz_profits = []

    path_list = os.listdir("data/{}/stock_income".format(Config.stock_list_date))
    for path in path_list:
        income = pd.read_csv("data/{}/stock_income/{}".format(Config.stock_list_date, path)).values
        avg_profit = sum([i[1] for i in income]) / len(income)
        date.append(path[:-4])
        profit.append(avg_profit)

        # 获取大盘信息
        start_date = "".join(path[:-4].split("-"))
        end_date = (datetime.datetime.strptime(start_date, "%Y%m%d") + datetime.timedelta(days=30)).strftime("%Y%m%d")
        sh_profit_data = pro.index_daily(ts_code="000001.SH", start_date=start_date,
                                         end_date=end_date, fields="trade_date, close").values

        sh_profit = (sh_profit_data[0][1] - sh_profit_data[-1][1]) / sh_profit_data[-1][1]

        sz_profit_data = pro.index_daily(ts_code="399001.SZ", start_date=start_date,
                                         end_date=end_date, fields="trade_date, close").values

        sz_profit = (sz_profit_data[0][1] - sz_profit_data[-1][1]) / sz_profit_data[-1][1]

        sh_profits.append(sh_profit)
        sz_profits.append(sz_profit)

    date = np.array(date)
    profit = np.array(profit)
    sh_profits = np.array(sh_profits)
    sz_profits = np.array(sz_profits)

    plt.plot(date, profit, "-og", label="选股结果")
    plt.plot(date, sh_profits, "-or", label="上证指数")
    plt.plot(date, sz_profits, "-ob", label="深圳成指")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    pro = ts.pro_api()
    draw()
