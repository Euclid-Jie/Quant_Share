"""
# -*- coding: utf-8 -*-
# @Time    : 2023/6/28 21:02
# @Author  : Euclid-Jie
# @File    : BackTestBase.py
# @Desc    : 回测 base Class
"""
import datetime
from typing import Union

import pandas as pd

from Euclid_work.Quant_Share.Utils import format_date, format_stockCode, reindex
from Euclid_work.Quant_Share.EuclidGetData import get_data


class BackTestBase:
    """
    整合回测所需要的组件, 主要包括:
        1 数据准备
            1.1 bench's info: self.get_bench_info
            1.2 stock's base: self.dataget_price_data
            1.3 stock's limit data: self.get_limit_data
        2 因子处理
        3 数据回测
        4 结果存储
        5 可视化
    """

    def __init__(
            self,
            beginDate: Union[str, int, datetime.date, datetime.datetime] = "20150101",
            endDate: Union[str, int, datetime.date, datetime.datetime] = None,
            **kwargs
    ):
        """

        :param beginDate:
        :param endDate:
        :param kwargs:

        :return:
        """
        # setting begin date and end date
        self.beginDate = beginDate
        if endDate:
            self.endDate_dt = format_date(endDate)
            self.endDate = self.endDate_dt.strftime("%Y%m%d")
        else:
            self.endDate = datetime.datetime.now().strftime("%Y%m%d")
            self.endDate_dt = pd.to_datetime(self.endDate)

        # bench code list
        self.bench_code_list = kwargs.get(
            "bench_code_list", ["000300", "000905", "000852"]
        )
        assert isinstance(
            self.bench_code_list, list
        ), "bench_code_list should be str or list[str]"

        # consts init
        self.TICKER = {}  # store ticker's data
        self.BENCH = {}  # store bench's data

        # Score init
        self.Score = None

    def get_bench_info(self):
        """
        get bench's pct change and con code data
        :return:
        self.BENCH = {
            "000300" :
            {
                "pct_chg" : pd.Series(dt index and float values),
                "con_code" : pd.DataFrame(pivot_data_format with dt index and wind_code)
            },
            "000905" :
            {
                ...
            },
            ...
        }

        """
        # 1 bench pct change
        bench_price_df = get_data(
            "MktIdx",
            begin=self.beginDate,
            end=self.endDate,
            ticker=self.bench_code_list,
        )
        bench_price_df["tradeDate"] = pd.to_datetime(bench_price_df["tradeDate"])
        bench_price_df = bench_price_df.sort_values("tradeDate", ascending=True)
        bench_price_df.set_index("tradeDate", inplace=True)
        # 2 bench con code
        con_code_df = get_data("mIdxCloseWeight", ticker=self.bench_code_list)
        con_code_df["consTickerSymbol"] = con_code_df["consTickerSymbol"].map(
            format_stockCode
        )
        for bench_code in self.bench_code_list:
            self.BENCH[bench_code] = {}
            self.BENCH[bench_code]["pct_chg"] = bench_price_df.loc[
                bench_price_df["ticker"] == bench_code, "CHGPct"
            ]
            self.BENCH[bench_code]["con_code"] = con_code_df.loc[
                con_code_df["ticker"] == bench_code
                ].pivot(index="effDate", columns="consTickerSymbol", values="weight")

    def get_price_data(self):
        """
        get stock's openPrice, closePrice, turnoverRate", isOpen", "vwap", negMarketValue", "chgPct", "isOpen" data
            notice: each pivot data has been reindex
        :return:
        self.TICKER = {
            "openPrice" : pd.DataFrame(pivot_data_format with dt index and wind_code),
            "closePrice" : ...,
            ...
        }
        """
        price_df = get_data("MktEqud", begin=self.beginDate, end=self.endDate)
        for coli in [
            "openPrice",
            "closePrice",
            "turnoverRate",
            "isOpen",
            "vwap",
            "negMarketValue",
            "chgPct",
            "isOpen",
        ]:
            self.TICKER[coli] = reindex(
                price_df.pivot(index="tradeDate", columns="ticker", values=coli)
            )

    def get_limit_data(self):
        """
        get stock's limitUpPrice, limitDownPrice data, has been reindex
        :return:
        self.TICKER = {
            "limitUpPrice" : pd.DataFrame(pivot_data_format with dt index and wind_code),
            "limitDownPrice" : ...
        }
        """
        MktLimit_df = get_data("MktLimit", begin=self.beginDate, end=self.endDate)
        for coli in ["limitUpPrice", "limitDownPrice"]:
            self.TICKER[coli] = reindex(
                MktLimit_df.pivot(index="tradeDate", columns="ticker", values=coli)
            )