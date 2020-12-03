import datetime

import tushare as ts
import pandas as pd
import numpy as np
import os

from config import Config


def get_income(start_date, end_date):
    df = pd.read_csv("data/{}/stock_list/{}stock_list.csv".format(Config.stock_list_date, start_date))

    if not os.path.exists("data/{}/stock_income".format(Config.stock_list_date)):
        os.mkdir("data/{}/stock_income".format(Config.stock_list_date))

    with open("data/{}/stock_income/{}.csv".format(Config.stock_list_date, start_date), "w") as f:
        f.write("ts_code, rate\n")
        for i in df.iterrows():
            income = pro.daily(ts_code=i[1]["ts_code"], start_date="".join(start_date.split("-")),
                               end_date="".join(end_date.split("-")), fields="close").values
            rate = (income[0][0] - income[-1][0]) / income[-1][0]
            f.write("{},{}\n".format(i[1]["ts_code"], rate))


def walk_file():
    path_list = os.listdir("data/{}/stock_list".format(Config.stock_list_date))
    for path in path_list:
        start_date = path[:-14]
        end_date = (datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=30)).\
            strftime("%Y-%m-%d")
        get_income(start_date, end_date)


if __name__ == '__main__':
    pro = ts.pro_api()
    walk_file()
