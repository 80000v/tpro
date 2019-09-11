#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-08-23 14:16:41
@LastEditTime: 2019-09-10 06:55:01
@Description: Analog clock class
'''

from time import localtime

import ntplib
from PyQt5.QtCore import QPoint, Qt, QTime, QTimer
from PyQt5.QtGui import QColor, QPainter, QPaintEvent, QPolygon
from PyQt5.QtWidgets import QFrame

# import os
# from time import strftime


########################################################################
class AnalogClock(QFrame):
    """模拟时钟，每次启动时首先校准系统时间"""
    # TODO: 实现异步时钟

    def __init__(self, parent=None):
        super(AnalogClock, self).__init__(parent)
        self.setFixedSize(150, 150)
        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(1000)

    # ------------------------------------------------------------------
    def paintEvent(self, _: QPaintEvent):
        hourHand = [QPoint(0, 10), QPoint(3, 6), QPoint(0, -40), QPoint(-3, 6)]
        minuteHand = [QPoint(0, 15), QPoint(3, 4), QPoint(0, -70), QPoint(-3, 4)]
        secondHand = [QPoint(0, 20), QPoint(2, 3), QPoint(0, -90), QPoint(-2, 3)]
        hourColor = QColor(255, 0, 0)
        minuteColor = QColor(0, 255, 0, 191)
        secondColor = QColor(255, 127, 0, 191)

        side = min(self.width(), self.height())
        # time = self._get_ntp_time()
        time = QTime.currentTime()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(hourColor)

        painter.save()
        painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        painter.drawConvexPolygon(QPolygon(hourHand))
        painter.restore()

        painter.setPen(hourColor)

        for _ in range(12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(minuteColor)

        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(QPolygon(minuteHand))
        painter.restore()

        painter.setPen(minuteColor)

        for j in range(60):
            if (j % 5) != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(secondColor)

        painter.save()
        painter.rotate(6.0 * time.second())
        painter.drawConvexPolygon(QPolygon(secondHand))
        painter.restore()

    # ------------------------------------------------------------------
    @staticmethod
    def _get_ntp_time(ntp_url: str = 'ntp5.aliyun.com'):
        """
        通过ntp server 获取网络时间
        :param str ntp_url: 传入的服务器地址，默认为阿里云
        :return QtCore::QTime
        """
        ntp_stats = ntplib.NTPClient().request(ntp_url)
        time = localtime(ntp_stats.tx_time)
        return QTime(time.tm_hour, time.tm_min, time.tm_sec)

        # 校准本地时间，需管理员权限
        # os.system('time {}'.format(strftime('%X', time)))


# 测试代码------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    clock = AnalogClock()
    clock.show()

    sys.exit(app.exec_())
