"""
# -*- coding: utf-8 -*-
# @Time    : 2023/6/13 11:12
# @Author  : Euclid-Jie
# @File    : Euclid_stEcharts_Test.py
"""
import os
from Euclid_work.Quant_Share.BackTest_Meng import *
from Euclid_work.Quant_Share import get_tradeDate, get_data
import streamlit as st
from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts.charts import Scatter
import datetime
import pyecharts
import warnings
import streamlit_echarts
import pickle
import pandas as pd
import numpy as np
import pyecharts.options as opts
from pyecharts.charts import Line
import streamlit as st
import pandas as pd
from scipy.stats import spearmanr


def get_nav_data_2_plot(data: pd.Series):
    return data / data.iloc[0] - 1


# 基本网页设置
st.set_page_config(page_title='因子回测', layout='wide')
st.markdown("<h1 style='text-align: center; color: black;'>因子回测分析结果</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: black;'>Factor Backtesting Analysis</h1>", unsafe_allow_html=True)
st.sidebar.header('回测参数设置')
st.sidebar.write('请完成以下基本回测参数设置')
st.sidebar.text(
    '基本事项说明：\n1. 当前支持的回测范围：2015年1月1日至2023年5月31日\n2. 研究标的对照：\n中证500 000905.XSHG\n中证1000 000852.XSHG\n沪深300 000300.XSHG\n3. 回测默认分5组')


@st.cache_resource
def data_prepare(_start_date, _end_date, _bench_code):
    # group beck data prepare
    _DataClass = DataPrepare(beginDate=_start_date, endDate=_end_date, bench=_bench_code[3:6])
    _DataClass.get_Tushare_data()
    return _DataClass


# 用户交互参数设置
# 起始时间
start_date = st.sidebar.date_input('回测起始日期', value=pd.to_datetime('20180101'))
# 截至时间
end_date = st.sidebar.date_input('回测截至日期', value=pd.to_datetime('20221231'))
# 研究标的
bench_code = st.sidebar.selectbox("研究标的", ('000852.XSHG', '000905.XSHG', '000300.XSHG'))

tradeDateCol_factor = st.text_input('因子日期列名称', value='tradeDate')
uploaded_factor = st.file_uploader("## uploader wide factor data", type=['h5','csv'])
tradeDateCol_rtn = st.text_input('回报率日期列名称', value='tradeDate')
uploaded_rtn = st.file_uploader("## uploader wide return data", type=['h5','csv'])

factor = None
score = None
rtn = None
def read_file(uploaded_file, tradeDateCol):
    if uploaded_file is not None:
        # Can be used wherever a "file-like" object is accepted:
        st.write("filename:", uploaded_file.name)
        if uploaded_file.name.endswith('csv'):
            data = pd.read_csv(uploaded_file)
            data = data.set_index(tradeDateCol)
            return data
        elif uploaded_file.name.endswith('h5'):
            data = pd.HDFStore(r'E:\Share\Stk_Data\gm\balance_sheet\balance_sheet_Y2022.h5')
            data = data.get('/a')
            data = data.set_index(tradeDateCol)
            return data
        return None

factor = read_file(uploaded_factor, tradeDateCol_factor)
if factor is not None:
    factor.index = pd.to_datetime(factor.index)
    factor = reindex(factor)
    score = info_lag(data2score(factor), n_lag=1)
    st.write("因子数据前五行为：")
    st.write(factor.head())

rtn = read_file(uploaded_rtn, tradeDateCol_rtn)

@st.cache_resource
def bkTest():
    global score
    # group beck test
    _DataClass = data_prepare(start_date, end_date, bench_code)
    BTClass = simpleBT(_DataClass.TICKER, _DataClass.BENCH)
    if score is not None:
        tmpScore = score
    else:
        tmpScore = _DataClass.Score

    _, _outMetrics, _group_res = BTClass.groupBT(tmpScore)

    return _outMetrics, _group_res


if st.sidebar.button('准备基础数据'):
    DataClass = data_prepare(start_date, end_date, bench_code)

if st.sidebar.button("分组回测指标"):
    outMetrics, group_res = bkTest()
    st.write("### 回测结束, 各组指标如下")
    st.dataframe(outMetrics.set_index('group'))

def nav_plot(_group_res, _plot_begin, _plot_end):
    _plot_begin = get_tradeDate(_plot_begin, 0)
    _plot_end = get_tradeDate(_plot_end, -1)

    bench_nav = _group_res['4'][0] / _group_res['4'][2]

    # 回测累计收益率图
    x_data = bench_nav.loc[_plot_begin:_plot_end].index.strftime("%Y%m%d").tolist()
    line = (
        Line(
            init_opts=opts.InitOpts(
                width='1000px',
                height='600px',
                theme="white"
            )
        )
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="group 1",
            y_axis=get_nav_data_2_plot(_group_res['{}'.format(1)][0].loc[_plot_begin:_plot_end]).tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="group 2",
            y_axis=get_nav_data_2_plot(_group_res['{}'.format(2)][0].loc[_plot_begin:_plot_end]).tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="group 3",
            y_axis=get_nav_data_2_plot(_group_res['{}'.format(3)][0].loc[_plot_begin:_plot_end]).tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="group 4",
            y_axis=get_nav_data_2_plot(_group_res['{}'.format(4)][0].loc[_plot_begin:_plot_end]).tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="group 5",
            y_axis=get_nav_data_2_plot(_group_res['{}'.format(5)][0].loc[_plot_begin:_plot_end]).tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="{}".format(bench_code),
            y_axis=get_nav_data_2_plot(bench_nav.loc[_plot_begin:_plot_end]).tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="回测累计收益率"),  # 标题参数
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
        .set_series_opts(
            linestyle_opts=opts.LineStyleOpts(
                is_show=True,
                width=2,
            )
        )
    )
    return line


# 绘图起始
plot_begin = st.sidebar.date_input('绘图开始日期', value=pd.to_datetime('20200531'))
# 绘图截至
plot_end = st.sidebar.date_input('绘图结束日期', value=pd.to_datetime('20221231'))

if st.sidebar.button("分组净值绘图"):
    outMetrics, group_res = bkTest()
    streamlit_echarts.st_pyecharts(nav_plot(group_res, plot_begin, plot_end), height="500px", width="100%")

def IC_Calc(start_date, end_date):
    global score, rtn
    if rtn is None:
        price_df = get_data('MktEqud', begin=start_date, end=end_date)
        rtn = reindex(price_df.pivot(index='tradeDate', columns='ticker', values='chgPct'))
        st.write('自动获取回报率数值')

    score.dropna(how='all', axis=0, inplace=True)
    rankIC = pd.DataFrame(np.zeros((score.shape[0], 1)), index=score.index, columns=['rankIC'])
    for index, values in score.iterrows():
        if index in rtn.index:
            tmp = pd.concat([values, rtn.loc[index]], axis=1, ignore_index=True)
            tmp.dropna(axis=0, inplace=True)
            tmp = tmp.rank(axis=0)
            # rank
            res = spearmanr(tmp)
            if res.pvalue > 0.05:
                rankIC.loc[index] = 0
            else:
                rankIC.loc[index] = res.statistic
    rankIC.dropna(axis=0, inplace=True)
    IR = (rankIC.mean()) / rankIC.std()
    return rankIC, IR

def ICIR_plot(rankIC, IR, plot_start, plot_end):
    plot_begin = get_tradeDate(plot_start, 0)
    plot_end = get_tradeDate(plot_end, -1)
    rankIC_lim = rankIC.loc[plot_begin:plot_end]
    st.write(f"IC数据量为{len(rankIC_lim)}")
    x_data = rankIC_lim.index.strftime("%Y%m%d").tolist()
    bar = (
        Bar(
            init_opts=opts.InitOpts(
                width='1000px',
                height='600px',
                theme="white"
            )
        )
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="IC",
            y_axis=list(rankIC_lim.values),
            itemstyle_opts = opts.ItemStyleOpts(color="#00CD96"))
        .set_global_opts(
            title_opts={"text": f"IR={float(IR)}"},
            brush_opts=opts.BrushOpts(),  # 设置操作图表的画笔功能
            # toolbox_opts=opts.ToolboxOpts(),  # 设置操作图表的工具箱功能
            yaxis_opts=opts.AxisOpts(name="IC"),
            # 设置Y轴名称、定制化刻度单位
            xaxis_opts=opts.AxisOpts(name="日期"),  # 设置X轴名称

        )
        )
    return bar

if st.sidebar.button("绘制因子ICIR图"):
    rankIC, IR = IC_Calc(plot_begin, plot_end)
    streamlit_echarts.st_pyecharts(ICIR_plot(rankIC, IR, plot_begin, plot_end), height="500px", width="100%")
