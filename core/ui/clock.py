#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2019 Freemoses
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import ntplib
from time import localtime, strftime

from PyQt5 import QtCore, QtGui, QtWidgets


########################################################################
class AnalogClock(QtWidgets.QFrame):
    """模拟时钟，每次启动时首先校准系统时间"""
    # TODO: 实现异步时钟

    # ------------------------------------------------------------------
    def __init__(self, parent=None):
        super(AnalogClock, self).__init__(None)
        self.setFixedSize(150, 150)
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(1000)

    # ------------------------------------------------------------------
    def paintEvent(self, e):
        hourHand = [QtCore.QPoint(0, 10), QtCore.QPoint(3, 6), QtCore.QPoint(0, -40), QtCore.QPoint(-3, 6)]
        minuteHand = [QtCore.QPoint(0, 15), QtCore.QPoint(3, 4), QtCore.QPoint(0, -70), QtCore.QPoint(-3, 4)]
        secondHand = [QtCore.QPoint(0, 20), QtCore.QPoint(2, 3), QtCore.QPoint(0, -90), QtCore.QPoint(-2, 3)]
        hourColor = QtGui.QColor(255, 0, 0)
        minuteColor = QtGui.QColor(0, 255, 0, 191)
        secondColor = QtGui.QColor(255, 127, 0, 191)

        side = min(self.width(), self.height())
        time = QtCore.QTime.currentTime()
        # time = self._get_ntp_time()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(hourColor)

        painter.save()
        painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        painter.drawConvexPolygon(QtGui.QPolygon(hourHand))
        painter.restore()

        painter.setPen(hourColor)

        for i in range(12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(minuteColor)

        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(QtGui.QPolygon(minuteHand))
        painter.restore()

        painter.setPen(minuteColor)

        for j in range(60):
            if (j % 5) != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(secondColor)

        painter.save()
        painter.rotate(6.0 * time.second())
        painter.drawConvexPolygon(QtGui.QPolygon(secondHand))
        painter.restore()

    def _get_ntp_time(self, ntp_url='ntp5.aliyun.com'):
        """
        通过ntp server 获取网络时间
        :param str ntp_url: 传入的服务器地址，默认为阿里云
        :return QtCore.QTime
        """
        ntp_stats = ntplib.NTPClient().request(ntp_url)
        time = localtime(ntp_stats.tx_time)
        return QtCore.QTime(time.tm_hour, time.tm_min, time.tm_sec)

        # 校准本地时间，需管理员权限
        os.system('time {}'.format(strftime('%X', time)))


# 测试代码------------------------------------------------------------------
if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    clock = AnalogClock()
    clock.show()

    sys.exit(app.exec_())
