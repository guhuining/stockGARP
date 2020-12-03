import pandas as pd
import numpy as np
import os
from copy import deepcopy

from config import Config


def score(df, index, ascending):
    """
    @param df 数据dataframe
    @param index 需要打分的字段
    @param ascending 是否升序
    """
    df_copy = df.sort_values(by=index, ascending=ascending)
    count = len(df_copy)
    scores = dict()
    i = count  # 记录股票位置
    for index, row in df_copy.iterrows():
        scores[row["ts_code"]] = int(i / count * 100)  # 排名越靠前分数越高
        i -= 1
    return scores


def select():
    path_list = os.listdir("data/{}/stock_data".format(Config.stock_list_date))
    for path in path_list:
        df = pd.read_csv("data/{}/stock_data/{}".format(Config.stock_list_date, path))
        df = df.dropna(axis=0, how="any")
        pe_score = score(df, "pe", ascending=False)
        roe_score = score(df, "roe", ascending=False)
        nprg_score = score(df, "nprg", ascending=True)
        mbrg_score = score(df, "mbrg", ascending=True)
        epsg_score = score(df, "epsg", ascending=True)

        value_score = deepcopy(pe_score)  # 价值指标分数
        for key, value in roe_score.items():
            value_score[key] += value

        grow_score = deepcopy(nprg_score)  # 成长指标分数
        for key, value in mbrg_score.items():
            grow_score[key] += value
        for key, value in epsg_score.items():
            grow_score[key] += value

        value_score = [(ts_code, v) for ts_code, v in value_score.items()]
        grow_score = [(ts_code, v) for ts_code, v in grow_score.items()]

        value_score.sort(key=lambda x: x[1], reverse=True)
        grow_score.sort(key=lambda x: x[1], reverse=True)

        length = len(grow_score)
        # 取前15%的股票
        value_score = value_score[:int(length*0.15)]
        grow_score = grow_score[:int(length*0.15)]

        value_stock_list = [i[0] for i in value_score]
        grow_stock_list = [i[0] for i in grow_score]

        # 交叉选股
        file_name = path[:-4] + "stock_list.csv"  # 保存对应日期的股票列表文件名
        if not os.path.exists("data/{}/stock_list".format(Config.stock_list_date)):
            os.mkdir("data/{}/stock_list".format(Config.stock_list_date))
        with open("data/{}/stock_list/{}".format(Config.stock_list_date, file_name), "w") as f:
            f.write("ts_code\n")
            for ts_code in value_stock_list:
                if ts_code in grow_stock_list:
                    f.write("{}\n".format(ts_code))
        print("{} done".format(file_name[:-4]))


if __name__ == '__main__':
    select()
