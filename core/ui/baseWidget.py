#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-09-03 21:38:25
@LastEditTime: 2019-09-10 12:25:40
@Description: 自定义Qt基础组件
'''

import csv
from typing import Any

import qtawesome
from PyQt5 import QtCore, QtGui, QtWidgets

COLOR_LONG = QtGui.QColor("red")
COLOR_SHORT = QtGui.QColor("green")

Mode_Color = {
    "stock": [QtGui.QColor(255, 139, 11), QtGui.QColor(255, 139, 11, 88)],
    "future": [QtGui.QColor(11, 139, 255), QtGui.QColor(11, 139, 255, 88)]
}


########################################################################
class BaseCell(QtWidgets.QTableWidgetItem):
    """
    General cell used in tablewidgets
    """
    def __init__(self, content: Any, data: Any):
        super(BaseCell, self).__init__()
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        self.set_content(content, data)

    def set_content(self, content: Any, data: Any):
        """
        Set text content.
        """
        self.setText(str(content))
        self._data = data

    def get_data(self):
        """
        Get data object.
        """
        return self._data


class EnumCell(BaseCell):
    """
    Cell used for showing enum data.
    """
    def __init__(self, content: str, data: Any):
        super(EnumCell, self).__init__(content, data)

    def set_content(self, content: Any, data: Any):
        """
        Set text using enum.constant.value.
        """
        if content:
            super(EnumCell, self).set_content(content.value, data)


class PnlCell(BaseCell):
    """
    Cell used for showing pnl data.
    """
    def set_content(self, content: Any, data: Any):
        """
        Cell color is set based on whether pnl is positive or negative.
        """
        super(PnlCell, self).set_content(content, data)

        if str(content).startswith("-"):
            self.setForeground(COLOR_SHORT)
        else:
            self.setForeground(COLOR_LONG)


class TimeCell(BaseCell):
    """
    Cell used for showing time string from datetime object.
    """
    def set_content(self, content: Any, data: Any):
        """
        Time format is xxxx-xx-xx 12:12:12.555
        """
        timestamp = content.strftime("%Y-%m-%d %H:%M:%S")

        millisecond = int(content.microsecond / 1000)
        if millisecond:
            timestamp = f"{timestamp}.{millisecond}"

        self.setText(timestamp)
        self._data = data


class MsgCell(BaseCell):
    """
    Cell used for showing msg data.
    """
    def __init__(self, content: Any, data: Any):
        """"""
        super(MsgCell, self).__init__(content, data)
        self.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)


class ModeCell(QtWidgets.QFrame):
    """
    Cell used for showing strategy mode
    """
    def __init__(self, content: Any, data: Any):
        super(ModeCell, self).__init__()
        self.setContent(content, data)

    def setContent(self, content: Any, data: Any):
        """
        Set cell content.
        """
        self._data = data

        lyt = QtWidgets.QHBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setAlignment(QtCore.Qt.AlignCenter)

        _pe = QtGui.QPalette()
        for item in content:
            _fore, _back = Mode_Color[item]
            _pe.setColor(QtGui.QPalette.Foreground, _fore)
            _pe.setColor(QtGui.QPalette.Background, _back)
            _lbl = QtWidgets.QLabel(item)
            _lbl.setForegroundRole(_pe.Foreground)
            _lbl.setBackgroundRole(_pe.Background)
            lyt.addWidget(_lbl)

        self.setLayout(lyt)

    def get_data(self):
        """
        Get data object
        """
        return self._data


class OptCell(QtWidgets.QFrame):
    """
    Cell used to show operate methods for current item
    """
    opt_signal = QtCore.pyqtSignal(str)

    opt_icon = {
        "rename": ['fa5s.pencil-alt', '重命名'],
        "delete": ['fa5s.trash-alt', '删除'],
        "pause": ['fa5s.pause', '暂停'],
        "stop": ['fa5s.stop', '停止'],
        "paper_trade": ['fa5s.chart-line', '模拟交易'],
        "link": ['fa5s.link', '连接']
    }

    def __init__(self, content: Any, data: Any):
        super(OptCell, self).__init__()
        self.setContent(content, data)

    def setContent(self, content: Any, data: Any):
        """
        Set cell content
        """
        self._data = data

        lyt = QtWidgets.QHBoxLayout()
        lyt.setAlignment(QtCore.Qt.AlignCenter)

        for item in content:
            _ico, _tip = self.opt_icon[item]
            _btn = QtWidgets.QPushButton(qtawesome.icon(_ico, color='gray', color_active='orange'), '')
            _btn.setToolTip(_tip)
            _btn.clicked.connect(lambda: self.opt_signal.emit(item))
            lyt.addWidget(_btn)

        self.setLayout(lyt)

    def get_data(self):
        """
        Get data object
        """
        return self._data


class DialogCell(QtWidgets.QFrame):
    """
    Cell used to show codes and params for the current strategy
    """
    def __init__(self, content: Any, data: Any):
        super(DialogCell, self).__init__()
        self.setContent(content, data)

    def setContent(self, content: Any, data: Any):
        """
        Set cell content
        """
        self._data = data

        _btn = QtWidgets.QPushButton('查看')
        _btn.setToolTip('查看策略代码及参数')
        _btn.clicked.connect(lambda: self._show_dialog(content))

        lyt = QtWidgets.QHBoxLayout()
        lyt.addWidget(_btn)
        self.setLayout(lyt)

    def _show_dialog(self, content: dict):
        """
        Open a dialog window to show codes and params
        """
        raise NotImplementedError

    def get_data(self):
        """Get data object"""
        return self._data


########################################################################
class BaseTable(QtWidgets.QTableWidget):
    """
    Base monitor for table data
    """
    headers = {}

    operate_signal = QtCore.pyqtSignal([dict], [str])

    def __init__(self, parent: Any = None):
        super(BaseTable, self).__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        """
        Initialize table ui
        """
        self.setColumnCount(len(self.headers))

        labels = [d['display'] for d in self.headers.values()]
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setEditTriggers(self.NoEditTriggers)

    def set_datas(self, datas: list):
        """
        Set table data, param 'datas' format is '[{}, {}, ...]'
        """
        self.clearContents()
        self.setRowCount(0)

        if datas:
            for data in datas:
                self.insert_new_row(data, 'bottom')
        else:
            self.insertRow(0)
            self.setItem(0, 0, BaseCell('很抱歉，暂无数据', ''))
            self.setSpan(0, 0, self.rowCount(), self.columnCount())

    def insert_new_row(self, data: dict, dirction: str = 'top'):
        """
        Insert a new row at the top/bottom of table
        """
        # 插入数据前必须关闭排序，否则插入新的数据会变乱
        self.setSortingEnabled(False)

        row_num = 0 if dirction == 'top' else self.rowCount()
        self.insertRow(row_num)

        for column, header in enumerate(self.headers.keys()):
            setting = self.headers[header]

            content = data.get(header, '')
            cell = setting['cell'](content, data)

            if isinstance(cell, QtWidgets.QTableWidgetItem):
                if setting['update']:
                    cell.setFlags(QtCore.Qt.ItemIsEditable)
                self.setItem(row_num, column, cell)
            else:
                self.setCellWidget(row_num, column, cell)

        # 重新打开排序
        self.setSortingEnabled(True)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def on_tablewidget_itemActivated(self, item):
        print('I am activated! %s' % item)

    def update_old_row(self, data):
        """
        Update an old row in table
        """
        key = data.__getattribute__(self.data_key)
        row_cells = self.cells[key]

        for header, cell in row_cells.items():
            content = data.__getattribute__(header)
            cell.set_content(content, data)

    def save_csv(self):
        """
        Save table data into a csv file
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, '保存数据', '', 'CSV(*.csv)')

        if not path:
            return

        with open(path, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')

            writer.writerow(self.headers.keys())

            for row in range(self.rowCount()):
                row_data = []
                for column in range(self.columnCount()):
                    item = self.item(row, column)
                    if item:
                        row_data.append(str(item.text()))
                    else:
                        row_data.append('')
                writer.writerow(row_data)


class StrategyTable(BaseTable):
    """
    Table for strategy library
    """
    headers = {
        'name': {
            'display': '名称',
            'cell': BaseCell,
            'update': False
        },
        'mode': {
            'display': '类型',
            'cell': ModeCell,
            'update': False
        },
        'last_modify': {
            'display': '最后修改时间',
            'cell': TimeCell,
            'update': False
        },
        'operate': {
            'display': '操作',
            'cell': OptCell,
            'update': False
        }
    }


class PaperTradingTable(BaseTable):
    """
    Table for paper trading strategy
    """
    headers = {
        'name': {
            'display': '名称',
            'cell': BaseCell,
            'update': False
        },
        '_id': {
            'display': 'ID',
            'cell': BaseCell,
            'update': False
        },
        'mode': {
            'display': '类型',
            'cell': ModeCell,
            'update': False
        },
        'state': {
            'display': '状态',
            'cell': BaseCell,
            'update': False
        },
        'operate': {
            'display': '操作',
            'cell': OptCell,
            'update': False
        },
        'total_equity': {
            'display': '总权益',
            'cell': PnlCell,
            'update': False
        },
        'available_funds': {
            'display': '可用资金',
            'cell': PnlCell,
            'update': False
        },
        'today_income': {
            'display': '当日盈亏',
            'cell': PnlCell,
            'update': False
        },
        'total_income': {
            'display': '累计收益',
            'cell': PnlCell,
            'update': False
        },
        'start_time': {
            'display': '开始时间',
            'cell': TimeCell,
            'update': False
        },
        'end_time': {
            'display': '结束时间',
            'cell': TimeCell,
            'update': False
        },
        'stop_reason': {
            'display': '原因',
            'cell': BaseCell,
            'update': True
        }
    }


class RealTradingTable(BaseTable):
    """
    Table for real trading strategy
    """
    headers = {
        'name': {
            'display': '名称',
            'cell': BaseCell,
            'update': False
        },
        '_id': {
            'display': 'ID',
            'cell': BaseCell,
            'update': False
        },
        'state': {
            'display': '状态',
            'cell': BaseCell,
            'update': False
        },
        'operate': {
            'display': '操作',
            'cell': OptCell,
            'update': False
        },
        'total_equity': {
            'display': '总权益',
            'cell': PnlCell,
            'update': False
        },
        'available_funds': {
            'display': '可用资金',
            'cell': PnlCell,
            'update': False
        },
        'today_income': {
            'display': '当日盈亏',
            'cell': PnlCell,
            'update': False
        },
        'total_income': {
            'display': '累计收益',
            'cell': PnlCell,
            'update': False
        },
        'start_time': {
            'display': '开始时间',
            'cell': TimeCell,
            'update': False
        }
    }


class AccountTable(BaseTable):
    """
    Table for account data
    """
    headers = {
        'account': {
            'display': '资金账户',
            'cell': BaseCell,
            'update': False
        },
        'broker': {
            'display': '经纪商',
            'cell': BaseCell,
            'update': False
        },
        'comment': {
            'display': '备注',
            'cell': MsgCell,
            'update': True
        },
        'enabled': {
            'display': '是否启用',
            'cell': BaseCell,
            'update': False
        },
        'connect_state': {
            'display': '连接状态',
            'cell': BaseCell,
            'update': False
        },
        'message': {
            'display': '消息',
            'cell': MsgCell,
            'update': False
        },
        'operate': {
            'display': '操作',
            'cell': OptCell,
            'update': False
        }
    }


class BacktestTable(BaseTable):
    """
    Table for history records with strategy backtest
    """
    headers = {
        '_id': {
            'display': 'ID',
            'cell': BaseCell,
            'update': False
        },
        'backtest_time': {
            'display': '回测时间',
            'cell': TimeCell,
            'update': False
        },
        'state': {
            'display': '状态',
            'cell': BaseCell,
            'update': False
        },
        'frequency': {
            'display': '频率',
            'cell': BaseCell,
            'update': False
        },
        'name': {
            'display': '名称',
            'cell': BaseCell,
            'update': False
        },
        'codes': {
            'display': '代码与参数',
            'cell': DialogCell,
            'update': False
        },
        'start_time': {
            'display': '开始时间',
            'cell': TimeCell,
            'update': False
        },
        'end_time': {
            'display': '结束时间',
            'cell': TimeCell,
            'update': False
        },
        'income': {
            'display': '收益',
            'cell': PnlCell,
            'update': False
        },
        'comment': {
            'display': '备注',
            'cell': MsgCell,
            'update': True
        },
        'operate': {
            'display': '操作',
            'cell': OptCell,
            'update': False
        }
    }
