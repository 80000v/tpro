#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@Author: freemoses
@Since: 2019-08-30 00:37:37
@LastEditTime: 2019-09-19 08:31:42
@Description: 字段名中英文转换
'''

# 主界面表头字段名
Table_Header = (("_id", "ID"), ("name", "名称"), ("mode", "类型"), ("last_modify", "最新修改时间"), ("state", "状态"),
                ("operate", "操作"), ("total_equity", "总权益"), ("available_funds", "可用资金"), ("today_income", "当日盈亏"),
                ("total_income", "累计收益"), ("start_time", "开始时间"), ("end_time", "结束时间"), ("stop_reason", "原因"),
                ("trade_name", "名称"), ("account", "资金账户"), ("broker", "经纪商"), ("comment", "备注"), ("enabled", "是否启用"),
                ("connect_state", "连接状态"), ("message", "消息"), ("backtest_time", "回测时间"), ("frequency", "频率"),
                ("code&param", "代码与参数"), ("income", "收益"))

# 回测报告字段名
Backtest_Report = (("alpha", "阿尔法"), ("beta", "贝塔"), ("information_ratio", "信息比率"), ("sharpe", "夏普比率"),
                   ("benchmark_annualized_returns",
                    "年化基准收益"), ("downside_risk", "年化下行波动率"), ("tracking_error", "年化跟踪误差"), ("sortino", "索提诺比率"),
                   ("volatility", "年化波动率"), ("max_drawdown", "最大回撤"), ("total_value", "总权益"), ("cash", "可用资金"),
                   ("total_returns", "回测收益"), ("annualized_returns", "年化回测收益"), ("unit_net_value", "组合单位净值"),
                   ("units", "组合份额"), ("benchmark_total_returns", "基准收益"))

# 货币符号
Vaild_Currency = (('CNY', '￥'), ('USD', '$'))

# 周期
Frequency = (('1d', '每日'), ('1m', '分钟'), ('tick', 'Tick'))

# 撮合方式
Matching_Type = (('current_bar', '当前bar收盘'), ('next_bar', '下一bar开盘'), ('best_own', '己方最优'),
                 ('best_counterparty', '对手方最优'), ('last', '最新成交价'))

Matching_Type_Options = {0: ['当前bar收盘'], 1: ['当前bar收盘', '下一bar开盘'], 2: ['己方最优', '对手方最优', '最新成交价']}

# 滑点类型
Slippape_Model = (('PriceRatioSlippage', '百分比'), ('TickSizeSlippage', '跳/手'))


def translate_field(target_set: tuple, field: str):
    """
    Translate field in target fields set to another language
    """
    trans_fields = [item for item in target_set if field in item]

    if trans_fields:
        trans_fields = trans_fields.pop()
        return trans_fields[trans_fields.index(field) - 1]
    return ''


def index_field(target_set: tuple, field: str):
    """
    Index field in target fields set, return it's index-value
    """
    index_fields = [item for item in target_set if field in item]

    if index_fields:
        return target_set.index(index_fields.pop())
    return -1
