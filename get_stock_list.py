import os

import tushare as ts
import numpy as np
import pandas as pd
import time
import datetime
from requests.exceptions import ConnectionError

from config import Config


def get_all_stoke():
    """
    获取所有股票
    :return:
    """
    df = pd.DataFrame(columns=("ts_code", "symbol", "name"))
    if Config.now:
        end_date = datetime.datetime.now() - datetime.timedelta(days=-1)
    else:
        end_date = datetime.datetime.strptime(Config.time, "%Y-%m-%d")
    pro = ts.pro_api()
    stocks = pro.stock_basic(fields="ts_code,symbol,name,list_date")
    # 去掉上市日期短于700天的股票
    for stock in stocks.values:
        if datetime.datetime.strptime(stock[3], "%Y%m%d") + datetime.timedelta(days=700) <= end_date:
            df = df.append({"ts_code": stock[0], "symbol": stock[1], "name": stock[2]}, ignore_index=True)
    return df


def delete_ST_stock(stocks):
    """
    去掉股票名中含有ST的股票
    """
    stocks = stocks.values

    # 去掉股票名中含"ST"的一行
    stocks_without_ST = [stock for stock in stocks if "ST" not in stock[2]]

    df = pd.DataFrame(stocks_without_ST)
    # 重新设置表头
    df.rename(columns={0: "ts_code", 1: "symbol", 2: "name"}, inplace=True)
    return df


def delete_negative_value_stock(stocks):
    """
    去掉滚动净利润为负值的股票
    """
    if Config.now:
        end_date = datetime.datetime.now() - datetime.timedelta(days=-1)
    else:
        end_date = datetime.datetime.strptime(Config.time, "%Y-%m-%d")

    stocks = stocks.values

    stock_without_negative_value = delete_negative_value_stock_helper(stocks)  # 获取滚动净利润大于0的股票列表

    # 获取到当前文件的目录，并检查是否有该年份的文件夹，如果不存在则自动新建文件夹
    File_Path = os.getcwd() + "/data/" + datetime.datetime.strftime(end_date, "%Y-%m-%d")
    if not os.path.exists(File_Path):
        os.makedirs(File_Path)

    with open("data/{}/white_list.csv".format(datetime.datetime.strftime(end_date, "%Y-%m-%d")), "a", encoding="utf8") as f:
        f.write("ts_code,end_date,n_income\n")
        for stock in stock_without_negative_value:
            f.write("{},{},{}\n".format(stock[0], stock[1], stock[2]))


def delete_negative_value_stock_helper(stocks):
    """
    :param stocks numpy.array
    :return: 滚动净利润为正的股票
    """
    if Config.now:  # 以当前时间为准，否则使用Config.end_time
        # 计算结束时间
        end_time = datetime.datetime.now()+datetime.timedelta(-1)  # 用昨天的时间，因为今天的数据可能还没出来
    else:
        end_time = datetime.datetime.strptime(Config.time, "%Y-%m-%d")
    start_time = end_time + datetime.timedelta(days=-600)
    end_time = end_time.strftime("%Y%m%d")
    start_time = start_time.strftime("%Y%m%d")

    pro = ts.pro_api()
    # 遍历每支股票并返回滚动净利润为正的股票
    for stock in stocks:
        while True:
            try:
                profit_data = pro.income(ts_code=stock[0], start_date=start_time, end_date=end_time,
                                         fields="ts_code, end_date, n_income").values
                break
            except ConnectionError as e:
                print(e)
                print("wait for restart")
                time.sleep(5)
            except Exception as e:
                print(e)
                print("wait for restart")
                time.sleep(5)

        # 计算净利润，若大于0则返回
        try:
            profit = get_roll_profit(profit_data)
        except IndexError as e:
            print("未查询到该公司财报")
            continue
        if profit > 0:
            print(stock[0] + "净利润大于0")
            yield stock
        else:
            print(stock[0] + "净利润小于0")


def get_roll_profit(profit_data):
    """
    获取滚动净利润
    :param profit_data: numpy.array
    :return: int
    """
    season_count = 0
    current_season = ""
    profit = 0

    if profit_data[0][1][4:] == "1231":  # 当前季度为最后一个季度，则当前季度的累计净利润为一年的滚动净利润
        return profit_data[0][2]
    # 有重复数据，所以不能简单的读取前四个数据
    for index in range(len(profit_data)):
        if profit_data[index][1] != current_season:
            # 计算一个季度的净利润
            season_count += 1
            current_season = profit_data[index][1]  # 保存当前季度
            if current_season[4:] == "0331":  # 当前季度为第一季度，不需要减去上一季度的累计净利润
                profit += profit_data[index][2]
            else:
                profit += (profit_data[index][2] - profit_data[index + 1][2])
        if season_count == 4:  # 计算最近的四个季度净利润后，得出一年的滚动净利润
            break
    return profit


def get_stock_list():
    stocks = get_all_stoke()
    stocks = delete_ST_stock(stocks)
    delete_negative_value_stock(stocks)


if __name__ == '__main__':
    get_stock_list()
