#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@Author: freemoses
@Since: 2019-09-15 14:35:54
@LastEditTime: 2019-09-19 22:16:54
@Description: The strategy edit and simple test
'''

import qtawesome
from PyQt5.Qsci import QsciLexerPython, QsciScintilla
from PyQt5.QtCore import QDate, QObject, Qt, pyqtSignal, QPropertyAnimation, QPoint, QAbstractAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QDoubleValidator, QFont, QIntValidator
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QSplitter, QVBoxLayout, QWidget)

from tpro.core.ui.baseWidget import (BuddyFrame, DateEdit, LineTable, LogView, SingleEcharts)
from tpro.utils import get_dict_value, set_dict_value
from tpro.utils.conversion import translate_field, Frequency, Matching_Type, Matching_Type_Options, Slippape_Model


class QsciEditor(QsciScintilla):
    """
    The strategy editor base on Qsci
    """
    def init(self):
        """
        Initialize editor
        """
        self._font = QFont('Hack', 11)
        self._font.setFixedPitch(True)

        # base setting
        self.setUtf8(True)
        self.setFont(self._font)
        self.setMarginsFont(self._font)

        # set line number width
        self.setMarginWidth(0, str(self.lines()) + '0')
        self.setMarginLineNumbers(0, True)
        self.linesChanged.connect(lambda: self.setMarginWidth(0, str(self.lines()) + '0'))

        # brace match
        self.setBraceMatching(self.StrictBraceMatch)

        # current line color
        self.setCaretWidth(2)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor('#272727'))
        self.setCaretForegroundColor(QColor('#FFFF00'))

        # selection color
        self.setSelectionBackgroundColor(QColor('#606060'))
        self.setSelectionForegroundColor(QColor('#FFFFFF'))

        # tab relative
        self.setIndentationsUseTabs(True)
        self.setIndentationWidth(4)
        self.setTabIndents(True)
        self.setAutoIndent(True)
        self.setBackspaceUnindents(True)
        self.setTabWidth(4)

        # indentation guides
        self.setIndentationGuides(True)

        # line number margin color
        self.setMarginsBackgroundColor(QColor('#0E131A'))
        self.setMarginsForegroundColor(QColor('#CCCCCC'))

        # folding margin
        self.setFolding(self.PlainFoldStyle)
        self.setMarginWidth(2, 12)

        # marker
        self.markerDefine(self.Minus, self.SC_MARKNUM_FOLDEROPEN)
        self.markerDefine(self.Plus, self.SC_MARKNUM_FOLDER)
        self.markerDefine(self.Minus, self.SC_MARKNUM_FOLDEROPENMID)
        self.markerDefine(self.Plus, self.SC_MARKNUM_FOLDEREND)

        # marker define color
        self.setMarkerBackgroundColor(QColor("#FFFFFF"), self.SC_MARKNUM_FOLDEREND)
        self.setMarkerForegroundColor(QColor("#272727"), self.SC_MARKNUM_FOLDEREND)
        self.setMarkerBackgroundColor(QColor("#FFFFFF"), self.SC_MARKNUM_FOLDEROPENMID)
        self.setMarkerForegroundColor(QColor("#272727"), self.SC_MARKNUM_FOLDEROPENMID)
        # self.setMarkerBackgroundColor(QColor("#FFFFFF"),self.SC_MARKNUM_FOLDERMIDTAIL)
        # self.setMarkerForegroundColor(QColor("#272727"),self.SC_MARKNUM_FOLDERMIDTAIL)
        # self.setMarkerBackgroundColor(QColor("#FFFFFF"),self.SC_MARKNUM_FOLDERTAIL)
        # self.setMarkerForegroundColor(QColor("#272727"),self.SC_MARKNUM_FOLDERTAIL)
        self.setMarkerBackgroundColor(QColor("#FFFFFF"), self.SC_MARKNUM_FOLDERSUB)
        self.setMarkerForegroundColor(QColor("#272727"), self.SC_MARKNUM_FOLDERSUB)
        self.setMarkerBackgroundColor(QColor("#FFFFFF"), self.SC_MARKNUM_FOLDER)
        self.setMarkerForegroundColor(QColor("#272727"), self.SC_MARKNUM_FOLDER)
        self.setMarkerBackgroundColor(QColor("#FFFFFF"), self.SC_MARKNUM_FOLDEROPEN)
        self.setMarkerForegroundColor(QColor("#272727"), self.SC_MARKNUM_FOLDEROPEN)
        self.setFoldMarginColors(QColor("#191F28"), QColor("#191F28"))

        # whitespace
        self.setWhitespaceVisibility(self.WsInvisible)
        self.setWhitespaceSize(2)

        # the default margin is:
        # 0: line number,width is not zero
        # 1: width is zero
        # 2: folding, width is not zero

        self.setMarginWidth(1, 0)

        # set lexer
        _lexer = QsciLexerPython()
        _lexer.setFont(self._font)
        self.setLexer(_lexer)

        # high light code
        _lexer.setColor(QColor("#FFFFFF"))
        _lexer.setPaper(QColor("#191919"))
        _lexer.setColor(QColor("#A6E22B"), QsciLexerPython.ClassName)
        _lexer.setColor(QColor("#FF0B66"), QsciLexerPython.Keyword)
        _lexer.setColor(QColor("#686868"), QsciLexerPython.Comment)
        _lexer.setColor(QColor("#BD4FE8"), QsciLexerPython.Number)
        _lexer.setColor(QColor("#FFFF00"), QsciLexerPython.SingleQuotedString)
        _lexer.setColor(QColor("#FFFF00"), QsciLexerPython.DoubleQuotedString)
        _lexer.setColor(QColor("#686868"), QsciLexerPython.TripleSingleQuotedString)
        _lexer.setColor(QColor("#686868"), QsciLexerPython.TripleDoubleQuotedString)
        _lexer.setColor(QColor("#A6E22B"), QsciLexerPython.FunctionMethodName)
        _lexer.setColor(QColor("#FFFFFF"), QsciLexerPython.Operator)
        _lexer.setColor(QColor("#FFFFFF"), QsciLexerPython.Identifier)
        _lexer.setColor(QColor("#686868"), QsciLexerPython.CommentBlock)
        _lexer.setColor(QColor("#F1E607"), QsciLexerPython.UnclosedString)
        _lexer.setColor(QColor("#F1E607"), QsciLexerPython.HighlightedIdentifier)
        _lexer.setColor(QColor("#F1E607"), QsciLexerPython.Decorator)

        # register signal event
        self.linesChanged.connect(lambda: self.setMarginWidth(0, str(self.lines()) + '0'))


########################################################################
class Editor(QWidget):
    """
    Widget for edit strategy
    """
    operate_signal = pyqtSignal(str, str, dict, dict)

    def __init__(self, _document: dict, parent: QObject = None):
        super(Editor, self).__init__(parent)
        self._document = _document
        self._config = _document['config']

        self.ok_to_continue = True  # whether current tab can be close

        self.init_ui()

    def init_ui(self):
        """
        Initialize user interface
        """
        self._config_frame = self._init_config(self._config)

        self._extra_frame = self._init_extra(self._config)
        self._extra_frame.setVisible(False)

        self._feedback_frame = self._init_feedback()

        frm_edge = QFrame()
        lyt_edge = QVBoxLayout(frm_edge)
        lyt_edge.setContentsMargins(0, 0, 0, 0)
        lyt_edge.addWidget(self._config_frame, alignment=Qt.AlignTop)
        lyt_edge.addWidget(self._extra_frame)
        lyt_edge.addWidget(self._feedback_frame)

        hsplitter = QSplitter()

        hsplitter.addWidget(self._init_edit())
        hsplitter.addWidget(frm_edge)
        hsplitter.setStretchFactor(0, 4)
        hsplitter.setStretchFactor(1, 1)

        lyt_main = QVBoxLayout(self)
        lyt_main.setContentsMargins(0, 0, 0, 0)
        lyt_main.setSpacing(0)

        lyt_main.addWidget(self._init_top())
        lyt_main.addWidget(hsplitter)

    def _init_top(self):
        """
        init top region
        """
        lbl_title = QLabel(self.tr("<h3> %s </h3>" % self._document['name']))

        _mode = ''
        if 'stock' in self._document['mode']:
            _mode += self.tr("<font style = 'font-size:12px; color:#FF8B00;'> 股票 </font>")
        if 'future' in self._document['mode']:
            _mode += self.tr("<font style = 'font-size:13px; color:#008BFF;'> 期货 </font>")
        lbl_mode = QLabel(_mode)

        btn_history = QPushButton('历史回测')

        btn_compile = QPushButton('编译策略')

        btn_backtest = QPushButton('运行回测')
        btn_backtest.setDefault(True)

        frm = QFrame()
        frm.setFixedHeight(80)
        lyt = QHBoxLayout(frm)
        lyt.addWidget(lbl_title)
        lyt.addWidget(lbl_mode)
        lyt.addStretch(1)
        lyt.addWidget(btn_history)
        lyt.addWidget(btn_compile)
        lyt.addWidget(btn_backtest)

        return frm

    def _init_edit(self):
        """
        init editor region
        """
        btn_save = QPushButton('保存')
        btn_save.setDisabled(True)
        btn_save.clicked.connect(self.save_code)
        btn_save.setObjectName('btn_save')

        self.editor = QsciEditor()
        self.editor.init()
        self.editor.setText(self._document['code'])
        self.editor.modificationChanged.connect(self._is_modified)

        frm = QFrame()
        lyt = QVBoxLayout(frm)

        lyt.addWidget(btn_save, alignment=Qt.AlignRight)
        lyt.addWidget(self.editor)

        return frm

    def _init_config(self, _config: dict):
        """
        init common options region
        """
        frm = QFrame()
        frm.setFixedHeight(60)
        lyt = QHBoxLayout(frm)

        start_date = DateEdit()
        start_date.setDate(QDate.fromString(get_dict_value(_config, 'start_date'), Qt.ISODate))
        start_date.dateChanged.connect(self._start_date_changed)

        lyt.addWidget(start_date)
        lyt.addWidget(QLabel('至'))

        end_date = DateEdit()
        end_date.setDate(QDate.fromString(get_dict_value(_config, 'end_date'), Qt.ISODate))
        end_date.dateChanged.connect(self._end_date_changed)

        lyt.addWidget(end_date)

        if 'stock' in self._document['mode']:
            stock_currency = QLabel('<font style = "font-size: 9px; color: #FF8B00>股票￥</font>')

            stock_funds = QLineEdit(maximumWidth=90)
            stock_funds.setText(str(get_dict_value(_config, 'stock')))
            stock_funds.setValidator(QIntValidator())
            stock_funds.editingFinished.connect(self._stock_funds_changed)

            lyt.addWidget(stock_currency)
            lyt.addWidget(stock_funds)

        if 'future' in self._document['mode']:
            future_currency = QLabel('<font style = "font-size: 9px; color: #008BFF>期货￥</font>')

            future_funds = QLineEdit(maximumWidth=90)
            future_funds.setText(str(get_dict_value(_config, 'future')))
            future_funds.setValidator(QIntValidator())
            future_funds.editingFinished.connect(self._future_funds_changed)

            lyt.addWidget(future_currency)
            lyt.addWidget(self.future_funds)

        frequency = QComboBox(maximumWidth=20)
        frequency.addItems(['每日', '分钟'])
        frequency.currentIndexChanged.connect(self._frequency_changed)

        lyt.addWidget(frequency)
        lyt.addStretch(1)

        btn_extra = QPushButton('更多')
        btn_extra.clicked.connect(self._show_extra)
        lyt.addWidget(btn_extra)

        return frm

    def _init_extra(self, _config: dict):
        """
        init extra-options frame
        """
        frm = QFrame()
        lyt = QGridLayout(frm)

        benchmark = BuddyFrame('基准合约', QLineEdit)
        benchmark.buddy.setText(get_dict_value(_config, 'benchmark'))
        benchmark.buddy.editingFinished.connect(self._benchmark_changed)

        lyt.addWidget(benchmark, 0, 0, 1, 3)

        commission_multiplier = BuddyFrame(
            '佣金倍率', QLineEdit, '实际佣金是基础佣金乘以佣金倍率之后的结果。\n \
                                            股票默认费率为万8，期货默认费率请参考文档。')
        commission_multiplier.buddy.setText(str(get_dict_value(_config, 'commission_multiplier')))
        commission_multiplier.buddy.setValidator(QDoubleValidator())
        commission_multiplier.buddy.editingFinished.connect(self._commission_changed)

        lyt.addWidget(commission_multiplier, 0, 3, 1, 3)

        if 'future' in self._document['mode']:
            margin_multiplier = BuddyFrame(
                '保证金倍率', QLineEdit, '实际保证金率是合约最低保证金率乘以保证金倍率之后的结果。\n \
                                            合约最低保证金率可以通过instruments函数获取到。')
            margin_multiplier.buddy.setText(str(get_dict_value(_config, 'margin_multiplier')))
            margin_multiplier.buddy.setValidator(QDoubleValidator())
            margin_multiplier.buddy.editingFinished.connect(self._margin_changed)

            lyt.addWidget(margin_multiplier, 0, 6, 1, 3)

        matching_type = BuddyFrame('撮合方式', QComboBox)
        matching_type.buddy.addItem('当前bar收盘')
        matching_type.buddy.currentTextChanged.connect(self._matching_type_changed)

        lyt.addWidget(matching_type, 1, 0, 1, 2)

        slippage_model = BuddyFrame('滑点类型', QComboBox)
        slippage_model.buddy.addItems(['百分比', '跳/手'])
        slippage_model.buddy.currentTextChanged.connect(self._slippage_model_changed)
        slippage_model.buddy.setCurrentText(
            translate_field(Slippape_Model, get_dict_value(_config, 'slippage_model')))

        lyt.addWidget(slippage_model, 1, 2, 1, 2)

        slippage = BuddyFrame(
            '滑点', QDoubleSpinBox, '滑点类型为百分比时，0.2代表20%当前价；为跳/手时，2代表每手加两跳价格')
        slippage.buddy.setValue(float(get_dict_value(_config, 'slippage')))
        slippage.buddy.valueChanged[float].connect(self._slippage_changed)
        slippage.setObjectName('slippage')

        lyt.addWidget(slippage, 1, 4, 1, 2)

        volume_limit = QCheckBox(' '.join(['限制成交量', chr(0xf059)]))
        volume_limit.setFont(qtawesome.font('fa', 12))
        volume_limit.setToolTip('如果开启，则策略发单成交量不能超过bar成交量的一定比例。\n例如0.2代表不能超过bar成交量的20%。')
        volume_limit.setChecked(get_dict_value(_config, 'volume_limit'))
        volume_limit.stateChanged.connect(self._volume_limit_changed)

        lyt.addWidget(volume_limit, 2, 0, 1, 2)

        volume_percent = BuddyFrame('成交量比例', QDoubleSpinBox)
        volume_percent.buddy.setRange(0, 1)
        volume_percent.buddy.setSingleStep(0.01)
        volume_percent.buddy.setValue(get_dict_value(_config, 'volume_percent'))
        volume_percent.buddy.valueChanged[float].connect(self._volume_percent_changed)
        volume_percent.setVisible(False)
        volume_percent.setObjectName('volume_percent')

        volume_limit.stateChanged.connect(volume_percent.setVisible)

        lyt.addWidget(volume_percent, 2, 3, 1, 2)

        profiler = QCheckBox(' '.join(['性能分析', chr(0xf059)]))
        profiler.setFont(qtawesome.font('fa', 12))
        profiler.setToolTip('性能分析用于展示策略运行时的性能状况，通常用于优化策略的执行效率。\n开启这一功能会影响策略的执行效率。')
        profiler.setChecked(get_dict_value(_config, 'enable_profiler'))
        profiler.stateChanged.connect(self._profiler_changed)

        lyt.addWidget(profiler, 4, 0, 1, 2)

        short_sale = QCheckBox('股票卖空')
        short_sale.setChecked(get_dict_value(_config, 'validate_stock_position'))
        short_sale.stateChanged.connect(self._short_sale_changed)

        lyt.addWidget(short_sale, 4, 3, 1, 2)

        reinvestment = QCheckBox(' '.join(['分红再投资', chr(0xf059)]))
        reinvestment.setFont(qtawesome.font('fa', 12))
        reinvestment.setToolTip('勾选后，基金分红将按照当日净值折算成基金份额。')
        reinvestment.setChecked(get_dict_value(_config, 'dividend_reinvestment'))
        reinvestment.stateChanged.connect(self._reinvestment_changed)

        lyt.addWidget(reinvestment, 4, 6, 1, 2)

        return frm

    def _init_feedback(self):
        """
        init feedback infomation region
        """
        _fileds = [
            'total_returns', 'annualized_returns', 'benchmark_total_returns', 'benchmark_annualized_returns', 'sharpe',
            'max_drawdown'
        ]
        feedback_table = LineTable(_fileds)
        feedback_table.set_columns_color({0: '#FF8B00', 1: '#008BFF'})

        feedback_chart = SingleEcharts("single_chart.html")
        feedback_chart.setVisible(False)

        feedback_log = LogView()
        feedback_log.setVisible(False)

        frm = QFrame(minimumHeight=600)
        lyt = QVBoxLayout(frm)
        lyt.addWidget(feedback_table)
        lyt.addWidget(feedback_chart)
        lyt.addWidget(feedback_log)
        lyt.addStretch()

        return frm

    def save_code(self):
        """
        Save the modified code
        """
        self._document['code'] = self.editor.text()
        self.editor.setModified(False)

    def _is_modified(self, _state: bool):
        """
        Change editor editing state
        """
        self.findChild(QPushButton, 'btn_save').setEnabled(_state)
        self.ok_to_continue = not _state

    def gather_config(self):
        """
        Gather current strategy setting, prepare next edit
        """
        self._document['config'] = self._config
        self.operate_signal.emit('my_strategy', 'update', {'_id': self._document['_id']}, self._document)

    def _show_extra(self, model):
        """
        Contral show/hide extra-options frame
        """
        source = self.sender()
        source.setEnabled(False)

        anim = QPropertyAnimation(self._feedback_frame, b'pos', self)
        anim.setDuration(800)

        if self._extra_frame.isHidden():
            if not model:
                self._extra_frame.setHidden(False)
                pos_y = self._extra_frame.y() + self._extra_frame.height() + 6
                anim.setStartValue(QPoint(0, self._extra_frame.y()))
                anim.setEndValue(QPoint(0, pos_y))
                anim.setEasingCurve(QEasingCurve.OutQuart)
                anim.start(QAbstractAnimation.DeleteWhenStopped)
        else:
            anim.setStartValue(QPoint(0, self._feedback_frame.y()))
            anim.setEndValue(QPoint(0, self._extra_frame.y()))
            anim.setEasingCurve(QEasingCurve.OutQuart)
            anim.start(QAbstractAnimation.DeleteWhenStopped)
            anim.finished.connect(lambda: self._extra_frame.setHidden(True))

        source.setEnabled(True)

    def _start_date_changed(self, _date: QDate):
        """
        Change config option -- 'base/start_date'
        """
        set_dict_value(self._config, 'start_date', _date.toString(Qt.ISODate))
        # self._config['base']['start_date'] = _date.toString(Qt.ISODate)

    def _end_date_changed(self, _date: QDate):
        """
        Change config option -- 'base/end_date'
        """
        set_dict_value(self._config, 'start_date', _date.toString(Qt.ISODate))
        # self._config['base']['end_date'] = _date.toString(Qt.ISODate)

    def _stock_funds_changed(self):
        """
        Change config option -- 'base/accounts/stock'
        """
        self._config['base']['accounts']['stock'] = int(self.sender().text())

    def _future_funds_changed(self):
        """
        Change config option -- 'base/accounts/future'
        """
        self._config['base']['accounts']['future'] = int(self.sender().text())

    def _frequency_changed(self, _idx: int):
        """
        Change config option -- 'base/frequency'
        """
        self._config['base']['frequency'] = translate_field(Frequency, self.sender().currentText())

        _matching_type = self.findChild(BuddyFrame, 'matching_type')
        _matching_type.buddy.clear()
        _matching_type.buddy.addItems(Matching_Type_Options[_idx])

    def _benchmark_changed(self):
        """
        Change config option -- 'base/benchmark'
        """
        set_dict_value(self._config, 'benchmark', self.sender().text())
        # self._config['base']['benchmark'] = self.sender().text()

    def _commission_changed(self):
        """
        Change config option -- 'mod/sys_simulation/commission_multiplier'
        """
        self._config['mod']['sys_simulation']['commission_multiplier'] = float(self.sender().text())

    def _margin_changed(self):
        """
        Change config option -- 'base/margin_multiplier'
        """
        self._config['base']['margin_multiplier'] = float(self.sender().text())

    def _matching_type_changed(self, _text: str):
        """
        Change config option -- 'mod/sys_simulation/matching_type'
        """
        set_dict_value(self._config, 'matching_type', translate_field(Matching_Type, _text))

    def _slippage_model_changed(self, _text: str):
        """
        Change config option -- 'mod/sys_simulation/slippage_model'
        """
        set_dict_value(self._config, 'slippage_model', translate_field(Slippape_Model, _text))

        _slippage = self.findChild(BuddyFrame, 'slippage')

        if self.sender().currentIndex():
            _slippage.buddy.setRange(0, 10)
            _slippage.buddy.setSingleStep(1)
        else:
            _slippage.buddy.setRange(0, 1)
            _slippage.buddy.setSingleStep(0.01)

        _slippage.buddy.setValue(0)

    def _slippage_changed(self, _value: float):
        """
        Change config option -- 'mod/sys_simulation/slippage'
        """
        self._config['mod']['sys_simulation']['slippage'] = _value

    def _volume_limit_changed(self, _state: bool):
        """
        Change config option -- 'mod/sys_simulation/volume_limit'
        """
        set_dict_value(self._config, 'volume_limit', _state)
        # self._config['mod']['sys_simulation']['volume_limit'] = _state

    def _volume_percent_changed(self, _value: float):
        """
        Change config option -- 'mod/sys_simulation/volume_percent'
        """
        self._config['mod']['sys_simulation']['volume_percent'] = _value

    def _profiler_changed(self, _state: bool):
        """
        Change config option -- 'extra/enable_profiler'
        """
        self._config['extra']['enable_profiler'] = _state

    def _short_sale_changed(self, _state: bool):
        """
        Change config option -- 'mod/sys_risk/validate_stock_position'
        """
        self._config['mod']['sys_risk']['validate_stock_position'] = _state

    def _reinvestment_changed(self, _state: bool):
        """
        Change config option -- 'mod/sys_accounts/dividend_reinvestment'
        """
        self._config['mod']['sys_accounts']['dividend_reinvestment'] = _state
