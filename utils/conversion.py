#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@Author: freemoses
@Since: 2019-08-30 00:37:37
@LastEditTime: 2019-09-10 06:47:06
@Description: 字段名中英文转换
'''

# 回测报告字段名转换
Backtest_Fields_forward = {
    "alpha": "阿尔法",
    "beta": "贝塔",
    "sharpe": "夏普比率",
    "information_ratio": "信息比率",
    "downside_risk": "年化下行波动率",
    "tracking_error": "年化跟踪误差",
    "sortino": "索提诺比率",
    "volatility": "年化波动率",
    "max_drawdown": "最大回撤",
    "total_value": "总权益",
    "cash": "可用资金",
    "total_returns": "回测收益",
    "annualized_returns": "年化回测收益",
    "unit_net_value": "组合单位净值",
    "units": "组合份额",
    "benchmark_total_returns": "基准收益",
    "benchmark_annualized_returns": "年化基准收益"
}
Backtest_Fields_reverse = {v: k for k, v in Backtest_Fields_forward.items()}

# 可用货币符号转换
Vaild_Currency_forward = {
    'CNY': '￥',
    'USD': '$',
}
Vaild_Currency_reverse = {v: k for k, v in Vaild_Currency_forward.items()}

# 可用周期转换
Vaild_Frequency_forward = {0: '1d', 1: '1m', 2: 'tick'}
Vaild_Frequency_reverse = {v: k for k, v in Vaild_Frequency_forward.items()}

# 可选撮合方式转换
Vaild_Matching_Type = {0: ['当前bar收盘'], 1: ['当前bar收盘', '下一bar开盘'], 2: ['己方最优', '对手方最优', '最新成交价']}

# 表头字段转换
Vaild_Fields_forward = {
    "_id": "ID",
    "name": "名称",
    "type": "类型",
    "last_modify_time": "最新修改时间",
    # "task_id": "ID",
    "state": "状态",
    "operate": "操作",
    "total_equity": "总权益",
    "available_funds": "可用资金",
    "today_income": "当日盈亏",
    "total_income": "累计收益",
    "start_time": "开始时间",
    "end_time": "结束时间",
    "stop_reason": "原因",
    "trade_name": "名称",
    "account": "资金账户",
    "broker": "经纪商",
    "comment": "备注",
    "enabled": "是否启用",
    "connect_state": "连接状态",
    "message": "消息",
    "backtest_time": "回测时间",
    "frequency": "频率",
    "code&param": "代码与参数",
    "income": "收益"
}
Vaild_Fields_reverse = {v: k for k, v in Vaild_Fields_forward.items()}

# 百分比字段
Percent_Fields = ("total_returns", "annualized_returns", "benchmark_total_returns", "benchmark_annualized_returns",
                  "max_drawdown", "profit")

# 可编辑字段
Editable_Fields = ("comments")
