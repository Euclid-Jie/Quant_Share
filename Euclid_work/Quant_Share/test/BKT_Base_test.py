"""
# -*- coding: utf-8 -*-
# @Time    : 2023/6/28 21:34
# @Author  : Euclid-Jie
# @File    : BKT_Base_test.py
"""
from Euclid_work.Quant_Share.BackTestPackage import BackTestBase
demoClas = BackTestBase(beginDate='20200101', endDate='20201231')
demoClas.get_bench_info()
