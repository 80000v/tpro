#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-09-03 21:38:25
@LastEditTime: 2019-09-14 22:49:16
@Description: 自定义Qt基础组件
'''

import os
import csv
import datetime
from typing import Any

import qtawesome
from PyQt5 import QtCore, QtGui, QtWidgets

from tpro.utils import Icon_Map

COLOR_LONG = QtGui.QColor("red")
COLOR_SHORT = QtGui.QColor("green")


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
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 背景色透明
        self.setContent(content, data)

    def setContent(self, content: Any, data: Any):
        """
        Set cell content.
        """
        self._data = data

        lyt = QtWidgets.QHBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(10)
        lyt.setAlignment(QtCore.Qt.AlignCenter)

        for item in content:
            _lbl = QtWidgets.QLabel(item)
            _lbl.setFixedSize(QtCore.QSize(40, 24))
            _lbl.setAlignment(QtCore.Qt.AlignCenter)
            _pixmap = QtGui.QPixmap(Icon_Map['.'.join([item, 'png'])])
            _lbl.setPixmap(_pixmap)
            _lbl.setScaledContents(True)
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
    opt_signal = QtCore.pyqtSignal(QtCore.QPoint, str)

    opt_icon = {
        "rename": ['fa5s.pencil-alt', '重命名'],
        "delete": ['fa5s.trash-alt', '删除'],
        "pause": ['fa5s.pause', '暂停'],
        "resume": ['fa5s.play', '恢复'],
        "stop": ['fa5s.stop', '停止'],
        "paper": ['fa5s.chart-line', '模拟交易'],
        "link": ['fa5s.link', '连接'],
        "edit": ['fa5s.pencil-alt', '编辑']
    }

    def __init__(self, content: Any, data: Any):
        super(OptCell, self).__init__()
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 背景色透明
        self.setContent(content, data)

    def setContent(self, content: Any, data: Any):
        """
        Set cell content
        """
        self._data = data

        lyt = QtWidgets.QHBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(5)
        lyt.setAlignment(QtCore.Qt.AlignCenter)

        for item in content:
            _ico, _tip = self.opt_icon[item]
            _btn = QtWidgets.QPushButton(qtawesome.icon(_ico, color='gray', color_active='orange'), '')
            _btn.setStyleSheet("QPushButton{background-color: transparent;border: 0px;}")
            _btn.setToolTip(_tip)
            _btn.clicked.connect(self._signal_emit)
            lyt.addWidget(_btn)

        self.setLayout(lyt)

    def _signal_emit(self):
        self.opt_signal.emit(self.pos(), self.sender().toolTip())

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
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 背景色透明
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

    def __init__(self, parent: Any = None):
        super(BaseTable, self).__init__(parent)
        self.parent = parent
        self._datas = []
        self._opt_row = None

        self.init_ui()

    def init_ui(self):
        """
        Initialize table ui
        """
        self.setColumnCount(len(self.headers))

        self._labels = [d['display'] for d in self.headers.values()]
        self.setHorizontalHeaderLabels(self._labels)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setEditTriggers(self.NoEditTriggers)

        self.setMouseTracking(True)
        self.cellEntered[int, int].connect(self.cell_entered)

    def set_datas(self, datas: list):
        """
        Set table data, param 'datas' format is '[{}, {}, ...]'
        """
        self.clearContents()
        self.setRowCount(0)

        if datas:
            for data in datas:
                self.insert_new_row(data, 'bottom')
            self._datas = datas
            return

        self.insertRow(0)
        self.setItem(0, 0, BaseCell('很抱歉，暂无数据', ''))
        self.setSpan(0, 0, self.rowCount(), self.columnCount())

    def insert_new_row(self, data: dict, dirction: str = 'top'):
        """
        Insert a new row at the top/bottom of table
        """
        self.setSortingEnabled(False)  # 插入数据前必须关闭排序，否则插入新的数据会变乱

        if not self._datas:
            self.clearContents()
            self.setRowCount(0)

        row_num = 0 if dirction == 'top' else self.rowCount()
        self.insertRow(row_num)

        for column, header in enumerate(self.headers.keys()):
            setting = self.headers[header]

            content = data.get(header, '')
            _cell_data = {header: content}  # 每个单元格只需保存其对应的字段数据即可
            cell = setting['cell'](content, _cell_data)

            if isinstance(cell, QtWidgets.QTableWidgetItem):
                if setting['update']:
                    cell.setFlags(QtCore.Qt.ItemIsEditable)
                self.setItem(row_num, column, cell)
            else:
                self.setCellWidget(row_num, column, cell)
                if isinstance(cell, OptCell):
                    cell.opt_signal.connect(self.operate_row)

        self._datas.append(data)
        self.setSortingEnabled(True)  # 重新打开排序

    def update_old_row(self, data):
        """
        Update an old row in table
        """
        for key, value in data.items():
            _column = self._labels.index([v['display'] for k, v in self.headers.items() if k == key].pop())
            cell = self.item(self._opt_row, _column)
            _cell_data = cell.get_data()
            _cell_data[key] = value

            cell.set_content(value, _cell_data)

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

    @QtCore.pyqtSlot(int, int)
    def cell_entered(self, row: int, _):
        """
        Handling mouse move-in cell events, select the current row
        """
        self.selectRow(row)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        """
        Handling mouse click events, open strategy edit window
        """
        # TODO: 完成打开策略编辑窗口的操作
        try:
            _strategy = self._datas[self.indexAt(e.pos()).row()]
            print('打开 {} 策略'.format(_strategy['name']))
        except IndexError:
            pass

    def operate_row(self, point: QtCore.QPoint, opt: str):
        """
        Perform specified actions, implemented after subclass inheritance
        """
        raise NotImplementedError


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

    def operate_row(self, point: QtCore.QPoint, opt: str):
        """
        Operate strategy table data
        """
        self._opt_row = self.indexAt(point).row()
        _data = self._datas[self._opt_row]

        if opt == '模拟交易':
            print('执行策略 “%s” 的模拟交易' % _data.get('name', '未知'))
        elif opt == '重命名':
            rn_dialog = RenameDialog()
            rn_dialog.setPlaceholderText(_data.get('name', ''))
            rn_dialog.ok_signal.connect(self.rename)
            rn_dialog.exec_()
        elif opt == '删除':
            del_dialog = DeleteDialog()
            del_dialog.setText('确定删除策略：%s？' % _data.get('name', ''), '已删除的策略无法恢复，请慎重选择。')
            del_dialog.ok_signal.connect(self.delete)
            del_dialog.exec_()
        else:
            raise ValueError('The operate type %s is invaild!' % opt)

    def rename(self, new_data: dict, _):
        """
        Rename strategy
        """
        if new_data:
            _data = self._datas[self._opt_row]
            _data['name'] = new_data.get('name', '')
            self._datas[self._opt_row] = _data

            self.parent.perform_operate(_data, {'_id': _data.pop('_id')}, 'update')
            self.update_old_row(new_data)

    def delete(self, *_):
        _data = self._datas[self._opt_row]
        self.parent.perform_operate({}, {'_id': _data.pop('_id')}, 'delete')

        self._datas.pop(self._opt_row)
        if self._datas:
            self.removeRow(self._opt_row)
        else:
            self.set_datas(self._datas)

    def paper(self, parameter_list):
        pass


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

    def operate_row(self, point: QtCore.QPoint, opt: str):
        """
        Operate paper-trading strategy
        """
        self._opt_row = self.indexAt(point).row()
        _data = self._datas[self._opt_row]

        raise ValueError('The operate type %s is invaild!' % opt)


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

    def operate_row(self, point: QtCore.QPoint, opt: str):
        """
        Operate real-trading strategy
        """
        self._opt_row = self.indexAt(point).row()
        _data = self._datas[self._opt_row]

        raise ValueError('The operate type %s is invaild!' % opt)


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

    def operate_row(self, point: QtCore.QPoint, opt: str):
        """
        Operate funds-account
        """
        self._opt_row = self.indexAt(point).row()
        _data = self._datas[self._opt_row]

        raise ValueError('The operate type %s is invaild!' % opt)


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

    def operate_row(self, point: QtCore.QPoint, opt: str):
        """
        Operate backtest history records
        """
        self._opt_row = self.indexAt(point).row()
        _data = self._datas[self._opt_row]

        raise ValueError('The operate type %s is invaild!' % opt)


########################################################################
class TipLabel(QtWidgets.QLabel):
    """
    Label with icon for tooltip
    """
    def addToolTip(self, tip: str):
        """
        Add icon for tooltip
        """
        self.setToolTip(tip)
        self.setFont(qtawesome.font('fa', 13))
        self.setText(self.text() + ' ' + chr(0xf059))


########################################################################
class BuddyFrame(QtWidgets.QFrame):
    """
    Combined widgets, it can include a label and a Qt functional widget
    """
    def __init__(self, label: str, widget: Any, tip: str = None, parent: Any = None):
        super(BuddyFrame, self).__init__(parent)
        self._lbl = TipLabel(label, minimumWidth=160)
        self._wgt = widget(minimumWidth=160)

        if tip:
            self._lbl.addToolTip(tip)

        lyt = QtWidgets.QVBoxLayout(self)
        lyt.setContentsMargins(2, 0, 0, 0)
        lyt.setSpacing(2)

        lyt.addWidget(self._lbl)
        lyt.addWidget(self._wgt)

    @property
    def buddy(self):
        """
        Get functional widget object
        """
        return self._wgt


########################################################################
class BaseDialog(QtWidgets.QDialog):
    """
    Custom base QDialog widget
    """
    ok_signal = QtCore.pyqtSignal(dict, str)

    def __init__(self, parent: Any = None):
        super(BaseDialog, self).__init__(parent)
        self.parent = parent

        self.setModal(True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.init_ui()
        self.center()

    def init_ui(self):
        """
        Initialization interface, implemented by subclass inheritance
        """
        raise NotImplementedError

    def center(self):
        """
        Locate in the center of the screen
        """
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)


class NewStrategy(BaseDialog):
    """
    New-built strategy dialog box
    """
    def init_ui(self):
        self.name = BuddyFrame('策略名称', QtWidgets.QLineEdit)

        self.frequency = BuddyFrame('频率', QtWidgets.QComboBox)
        self.frequency.buddy.addItems(['每日', '分钟'])

        self.initial_funds = BuddyFrame('初始资金', QtWidgets.QSpinBox)
        self.initial_funds.buddy.setRange(100000, 99999999)
        self.initial_funds.buddy.setValue(1000000)

        self.stock_checker = QtWidgets.QCheckBox('股票')
        self.stock_checker.stateChanged.connect(self._check_state)

        self.future_checker = QtWidgets.QCheckBox('期货')
        self.future_checker.stateChanged.connect(self._check_state)

        self.btn_ok = QtWidgets.QPushButton('确定')
        self.btn_ok.clicked.connect(self.add)
        self.btn_ok.setEnabled(False)

        _btn_cancel = QtWidgets.QPushButton('取消')
        _btn_cancel.clicked.connect(self.close)

        self.name.buddy.textChanged.connect(self._check_state)
        self.stock_checker.setCheckState(QtCore.Qt.Checked)
        self.future_checker.setCheckState(QtCore.Qt.Checked)

        lyt = QtWidgets.QVBoxLayout(self)
        lyt.addWidget(QtWidgets.QLabel('新建策略'))

        _lyt_input = QtWidgets.QHBoxLayout()
        _lyt_input.addWidget(self.name)
        _lyt_input.addWidget(self.frequency)
        _lyt_input.addWidget(self.initial_funds)
        lyt.addLayout(_lyt_input)

        _lyt_checker = QtWidgets.QHBoxLayout()
        _lyt_checker.addWidget(QtWidgets.QLabel('策略类别：'))
        _lyt_checker.addWidget(self.stock_checker)
        _lyt_checker.addWidget(self.future_checker)
        _lyt_checker.addStretch(1)
        lyt.addLayout(_lyt_checker)

        lyt.addWidget(QtWidgets.QLabel('注意：交易品种在策略创建成功后将不能修改！'))

        _lyt_btn = QtWidgets.QHBoxLayout()
        _lyt_btn.addStretch(1)
        _lyt_btn.addWidget(self.btn_ok)
        _lyt_btn.addWidget(_btn_cancel)
        lyt.addLayout(_lyt_btn)

    def add(self):
        """
        Add new strategy
        """
        def _template(template_name: str = 'template.py'):
            url = os.path.join(os.getcwd(), 'resource', template_name)

            if os.path.exists(url):
                with open(url, 'r', encoding='utf-8') as f:
                    return f.read()
            return ''

        d = {}

        d['name'] = self.name.buddy.text()
        d['frequency'] = self.frequency.buddy.currentText()
        d['initial_funds'] = self.initial_funds.buddy.value()
        d['mode'] = []

        if self.stock_checker.isChecked():
            d['mode'].append('stock')
        if self.future_checker.isChecked():
            d['mode'].append('future')

        if ('stock' in d['mode']) and ('future' in d['mode']):
            d['code'] = _template()
        else:
            d['code'] = _template('TPL_Stock.py') if 'stock' in d['mode'] else _template('TPL_Future.py')

        d['last_modify'] = datetime.datetime.now()
        d['operate'] = ['paper', 'rename', 'delete']

        self.ok_signal.emit(d, 'last_modify')
        self.close()

    def _check_state(self):
        """
        Check whether strategy fields is vaild
        """
        if (self.stock_checker.isChecked() or self.future_checker.isChecked()) and self.name.buddy.text():
            self.btn_ok.setEnabled(True)
            self.btn_ok.setDefault(True)
        else:
            self.btn_ok.setEnabled(False)


class NewRealTrading(BaseDialog):
    """
    New-built real trading dialog box
    """
    def init_ui(self):
        pass

    def add(self):
        """
        Add new real-trading
        """
        d = {}

        self.ok_signal.emit(d, 'name')

    def _check_config(self):
        """
        Check real-trading environment configuration
        """


class NewAccount(BaseDialog):
    """
    New-built transaction account dialog box
    """
    def init_ui(self):
        pass

    def add(self):
        """
        Add new transaction account
        """
        d = {}

        self.ok_signal.emit(d, 'account')

    def _check_config(self):
        """
        Check account configuration
        """


class RenameDialog(BaseDialog):
    """
    Rename strategy record
    """
    def init_ui(self):
        title = QtWidgets.QLabel('策略重命名')
        description = QtWidgets.QLabel('请输入新的策略名称')

        self.new_name = QtWidgets.QLineEdit(minimumWidth=200)

        self.btn_ok = QtWidgets.QPushButton('确定')
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self.rename)

        _btn_cancel = QtWidgets.QPushButton('取消')
        _btn_cancel.clicked.connect(self.close)

        lyt = QtWidgets.QVBoxLayout(self)
        lyt.addWidget(title)
        lyt.addWidget(description)
        lyt.addWidget(self.new_name)

        _btn_lyt = QtWidgets.QHBoxLayout()
        _btn_lyt.addStretch(1)
        _btn_lyt.addWidget(self.btn_ok)
        _btn_lyt.addWidget(_btn_cancel)

        lyt.addLayout(_btn_lyt)

    def setPlaceholderText(self, text: str):
        """
        Set line edit's placeholder text
        """
        if text:
            self.new_name.setPlaceholderText(text)

    def rename(self):
        """
        Emit rename signal
        """
        d = {}

        if self.new_name.text():
            d['name'] = self.new_name.text()

        self.ok_signal.emit(d, 'rename')
        self.close()


class DeleteDialog(BaseDialog):
    """
    Delete current record
    """
    def init_ui(self):
        self.title = QtWidgets.QLabel()
        self.description = QtWidgets.QLabel()

        self.btn_ok = QtWidgets.QPushButton('确定')
        self.btn_ok.clicked.connect(self.delete)

        _btn_cancel = QtWidgets.QPushButton('取消')
        _btn_cancel.clicked.connect(self.close)
        _btn_cancel.setDefault(True)

        lyt = QtWidgets.QVBoxLayout(self)
        lyt.addWidget(self.title)
        lyt.addWidget(self.description)

        _btn_lyt = QtWidgets.QHBoxLayout()
        _btn_lyt.addStretch(1)
        _btn_lyt.addWidget(self.btn_ok)
        _btn_lyt.addWidget(_btn_cancel)

        lyt.addLayout(_btn_lyt)

    def setText(self, title: str, description: str):
        """
        Set dialog title and description
        """
        self.title.setText(title)
        self.description.setText(description)

    def delete(self):
        """
        Emit delete signal
        """
        self.ok_signal.emit({}, 'delete')
        self.close()
