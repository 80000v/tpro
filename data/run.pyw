"""
数据下载管理器：
    根据配置中所选数据源，可自动或手动更新数据
"""
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import ctypes
import datetime
import qdarkstyle

from PyQt5 import QtCore, QtGui, QtWidgets

from QuanTrader.data import QuantOS
from QuanTrader.utils import load_icon


########################################################################
class DataManager(QtWidgets.QWidget):
    """数据下载管理"""
    _manager = None

    # ------------------------------------------------------------------
    def __init__(self, parent=None):
        """Constructor"""
        super(DataManager, self).__init__(parent)
        DataManager._manager = self

        # 数据源实例
        self.sourceDict = {}
        self.sourceDetailList = []

        # 当前数据源实例
        self.currentSource = None

        self.initUi()

    # ------------------------------------------------------------------
    @classmethod
    def get_instance(cls):
        """
        返回已经创建的 DataManager 对象
        """
        if DataManager._manager is None:
            raise RuntimeError("DataManager has not been created.")
        return DataManager._manager

    # ------------------------------------------------------------------
    @property
    def active(self):
        """当前下载服务运行状态"""
        if self.currentSource:
            return self.currentSource.active
        else:
            return False

    # ------------------------------------------------------------------
    def addSource(self, sourceModule):
        """添加数据源"""
        sourceName = sourceModule.sourceName

        # 创建数据源实例
        self.sourceDict[sourceName] = sourceModule.sourceClass()

        # 保存数据源详细信息
        d = {
            'sourceName': sourceModule.sourceName,
            'sourceDisplayName': sourceModule.sourceDisplayName,
            'sourceIcon': sourceModule.sourceIcon
        }
        self.sourceDetailList.append(d)
        self.refreshMenu()

    # ------------------------------------------------------------------
    def getSource(self, sourceName):
        """获取数据源"""
        if sourceName in self.sourceDict:
            return self.sourceDict[sourceName]
        else:
            self.updateLog('数据源 %s 不存在！' % sourceName)
            return None

    # ------------------------------------------------------------------
    def connect(self, sourceName):
        """连接特定名称的数据源"""
        source = self.getSource(sourceName)

        if source:
            if source.active:
                self.setWindowTitle('数据下载管理')
                self.currentSource = None
                source.active = False
            else:
                self.setWindowTitle('数据下载管理 - 当前数据源： %s' % sourceName)
                self.currentSource = source
                self.currentSource.digitSignal.connect(self.updateDigit)
                self.currentSource.msgSignal.connect(self.updateLog)
                source.active = True

    # ------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle('数据下载管理')
        self.setWindowIcon(load_icon('download.ico'))
        self.setMinimumSize(900, 500)

        # 日志监控
        self.logMonitor = QtWidgets.QTextBrowser()
        self.logMonitor.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        # 进度条
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximum(100)
        self.progressBar.setVisible(False)

        self.symbol = QtWidgets.QLabel()
        self.symbol.setVisible(False)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.progressBar)
        hbox.addWidget(self.symbol)
        hbox.addStretch(1)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.logMonitor)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # 托盘设置
        self.tray = QtWidgets.QSystemTrayIcon()
        self.tray.setToolTip('数据更新管理器')
        self.tray.setIcon(load_icon('download.ico'))

        # 右键弹出菜单
        menu = QtWidgets.QMenu(QtWidgets.QApplication.desktop())

        # 数据源子菜单只显示添加的源
        self.subMenu = menu.addMenu('数据源')
        self.subMenu.setToolTipsVisible(True)

        self.viewStatus = QtWidgets.QAction('隐藏')
        self.viewStatus.triggered.connect(self.showManager)

        menu.addAction(self.viewStatus)
        menu.addAction(QtWidgets.QAction('退出', self, triggered=self.exit))

        self.tray.setContextMenu(menu)
        self.tray.show()

    # ------------------------------------------------------------------
    def refreshMenu(self):
        """刷新数据源子菜单"""
        # 清除现有子选项
        self.subMenu.clear()

        if self.sourceDetailList:
            for d in self.sourceDetailList:
                action = QtWidgets.QAction(d['sourceName'], self, triggered=self.changeSource)
                action.setIcon(load_icon(d['sourceIcon']))
                action.setToolTip(d['sourceDisplayName'])
                self.subMenu.addAction(action)

    # ------------------------------------------------------------------
    def updateDigit(self, rate, symbol):
        """当前更新进度"""
        if symbol == 'finish':
            self.progressBar.setVisible(False)
            self.symbol.setVisible(False)
            return
        elif not self.progressBar.isVisible():
            self.progressBar.setVisible(True)
            self.symbol.setVisible(True)

        self.progressBar.setValue(rate)
        self.symbol.setText(symbol)

    # ------------------------------------------------------------------
    def updateLog(self, msg):
        """更新日志"""
        dt = format(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        msg = '%s    %s' % (dt, msg)
        self.logMonitor.append(msg)

    # ------------------------------------------------------------------
    def showManager(self, reason):
        """显示界面"""
        sender = self.sender()
        if self.isHidden():
            self.show()
            sender.setText('隐藏')
        else:
            self.hide()
            sender.setText('显示')

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        """窗体关闭事件"""
        self.hide()
        self.viewStatus.setText('显示')
        event.ignore()

    # ------------------------------------------------------------------
    def exit(self):
        """退出程序前调用，保证正常退出"""
        if self.currentSource:
            self.currentSource.close()
        QtWidgets.qApp.quit()

    # ------------------------------------------------------------------
    def changeSource(self):
        """更改数据源"""
        sender = self.sender()

        if self.currentSource and self.currentSource.dataSource != sender.text():
            self.currentSource.exit()
            self.currentSource = None

        self.connect(sender.text())


########################################################################
if __name__ == '__main__':
    import sys

    font = QtGui.QFont(u'微软雅黑', 11)

    app = QtWidgets.QApplication([])
    app.setFont(font)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('DownloadMonitor')

    manager = DataManager()
    manager.addSource(QuantOS)
    # manager.addSource(TusharePro)

    manager.show()

    sys.exit(app.exec_())
