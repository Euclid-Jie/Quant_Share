"""
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 23:20
# @Author  : Euclid-Jie
# @File    : continuous_contracts.py
"""
from .base_package import *


def continuous_contracts(begin, end, **kwargs):
    # if 'balance_sheet_fields' not in kwargs.keys():
    #     raise AttributeError('balance sheet fields should in kwargs!')
    if 'csymbol' not in kwargs.keys():
        raise AttributeError('csymbol should in kwargs!')

    begin = format_date(begin).strftime("%Y-%m-%d")
    end = format_date(end).strftime("%Y-%m-%d")
    csymbol = kwargs['csymbol']
    # balance_sheet_fields = kwargs['balance_sheet_fields']
    outData = pd.DataFrame()
    # with tqdm(patList(csymbol, 30)) as t:
    with tqdm(csymbol) as t:
        t.set_description("begin:{} -- end:{}".format(begin, end))
        for patSymbol in t:
            try:
                # tmpData = get_fundamentals(table='balance_sheet', symbols=patSymbol, limit=1000,
                #                            start_date=begin, end_date=end, fields=balance_sheet_fields, df=True)
                # print(patSymbol)
                tmpData = get_continuous_contracts(
                    csymbol=patSymbol,
                    start_date=begin,
                    end_date=end,
                )
                t.set_postfix({"状态": "已成功获取{}条数据".format(len(tmpData))})  # 进度条右边显示信息
                errors_num = 0
                if len(tmpData) == 0: continue
            except GmError:
                errors_num += 1
                if errors_num > 5:
                    raise RuntimeError("重试五次后，仍旧GmError")
                time.sleep(60)
                t.set_postfix({"状态": "GmError:{}, 将第{}次重试".format(GmError, errors_num)})
            tmpData = pd.DataFrame(tmpData)
            tmpData.trade_date = tmpData.trade_date.dt.strftime('%Y-%m-%d')
            outData = pd.concat([outData, tmpData], ignore_index=True, axis=0)
    return outData


if __name__ == '__main__':
    continuous_contracts_info = pd.read_excel(r'E:\Euclid\Quant_Share\Euclid_work\Quant_Share\dev_files\continuous_contracts_csymbol.xlsx')
    csymbol = continuous_contracts_info.csymbol.tolist()
    data = continuous_contracts(begin='20150101', end='20231231', csymbol=csymbol)
    save_gm_data_Y(data, 'trade_date', 'continuous_contracts', reWrite=True)