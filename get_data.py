import tushare as ts
import numpy as np
import pandas as pd
import datetime
import time

from config import Config


def get_data():
    stock_list = pd.read_csv("data/white_list.csv").values  # 读取白名单
    stock_data = pd.DataFrame(columns=("ts_code", "stock_name", "pe", "roe", "nprg", "mbrg", "epsg"))
    if Config.now:
        trade_date = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y%m%d")  # 用昨天的时间，因为今天的数据可能还没出来
        start_date = (datetime.datetime.now() + datetime.timedelta(days=-700)).strftime("%Y%m%d")
    else:
        trade_date = ''.join(Config.time.split("-"))
        start_date = (datetime.datetime.strptime(trade_date, "%Y%m%d") + datetime.timedelta(days=-700)).strftime(
            "%Y%m%d")

    for stock in stock_list:
        while True:
            try:
                ts_code = stock[0]
                stock_name = stock[2]
                # 价值指标pe,roe
                pe = pro.daily_basic(ts_code=ts_code, trade_date=trade_date, fields="pe").values[0][0]
                roe = pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=trade_date,
                                         fields="roe").values[0][0]
                # 成长指标nprg,mbrg
                # nprg
                nprg = get_nprg(ts_code, start_date, trade_date)
                # mbrg
                mbrg = get_mbrg(ts_code, start_date, trade_date)
                # epsg
                epsg = get_epsg(ts_code, start_date, trade_date)

                # 保存结果
                data = {"ts_code": ts_code, "stock_name": stock_name, "pe": pe, "roe": roe,
                        "nprg": nprg, "mbrg": mbrg, "epsg": epsg}
                stock_data = stock_data.append([data], ignore_index=True)
                print(data)
                break
            except ConnectionError as e:
                print("wait for restart")
                time.sleep(5)
            except ZeroDivisionError as e:
                print("该股上期每股收益为0，没有价值")
                break
            except IndexError:
                print("财报不完整，暂不考虑")
                break
            except Exception as e:
                print("wait for restart")
                print(e)
                time.sleep(5)
            time.sleep(1)
    stock_data.to_csv("data/stock_data.csv")


def get_nprg(ts_code, start_date, end_date):
    nprg_data = pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date,
                           fields="ann_date, n_income").values
    income_1 = nprg_data[0][1]
    income_1_date = nprg_data[0][0]
    income_2 = income_1
    for date, income in nprg_data:
        if date != income_1_date:
            income_2 = income
            break
    nprg = (income_1 - income_2) / income_2
    return nprg


def get_mbrg(ts_code, start_date, end_date):
    mbrg_data = pro.fina_mainbz(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                fields="end_date, bz_sales")
    mbrg_data = mbrg_data.groupby("end_date").agg("sum")[::-1].values
    # 主营业务收入只有年报和半年报
    mbrg = (mbrg_data[0][0] - mbrg_data[2][0]) / mbrg_data[2][0]
    return mbrg


def get_epsg(ts_code, start_date, end_date):
    epsg_data = pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                   fields="end_date, eps")
    epsg_data = epsg_data.groupby("end_date", as_index=False).mean()[::-1].values
    if epsg_data[0][0][-4:] == "1231":  # 代表当前季度的报告是年报，需要计算后得出结果
        epsg = (epsg_data[0][1] - epsg_data[1][1]*2 - epsg_data[2][1] - epsg_data[3][1]) / epsg_data[1][1]
    elif epsg_data[0][0][-4:] == "0331":  # 上一个季度的报告是年报，需要计算
        last_season_epsg = (epsg_data[1][1] - epsg_data[2][1] - epsg_data[3][1] - epsg_data[4][1])
        epsg = (epsg_data[0][1] - last_season_epsg) / last_season_epsg
    else:
        epsg = (epsg_data[0][1] - epsg_data[1][1]) / epsg_data[1][1]
    return epsg


if __name__ == '__main__':
    pro = ts.pro_api()
    get_data()