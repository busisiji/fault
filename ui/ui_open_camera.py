# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'open_camera.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import math
import os
import threading

import pymsgbox as mb

from PyQt5.Qt import *
from PyQt5.QtWidgets import QWidget


def initbox(groupbox,controls,HorV='H',IsMargins=1,IScenter=0):
    """
    :param groupbox: Qroupbox对象
    :param controls: 放在Qroupbox对象的类
    :param HorV: H 水平发布 ; V 垂直发布
    :param IsMargins；间距是否设0
    :param IScenter；控件是否居中
    """
    if HorV=='H':
        mainVLayout = QHBoxLayout()
    else:
        mainVLayout = QVBoxLayout()
    if IScenter:
        mainVLayout.setAlignment(Qt.AlignCenter)
    if IsMargins:
        mainVLayout.setContentsMargins(0, 0, 0, 0)
        mainVLayout.setSpacing(0)
    for i in controls:
        mainVLayout.addWidget(i)
    groupbox.setLayout(mainVLayout)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.info = ''

        self.MainWindow = MainWindow
        self.MainWindow.resize(1600, 800)
        self.MainWindow.setWindowIcon(QIcon('../icons/1.ico'))
        self.center(MainWindow)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.setbox_1()
        self.setbox_2()
        # self.setbox_3()
        self.setbox_4()
        self.mainVLayout = QVBoxLayout()
        # self.groupbox_1.setMinimumSize(QSize(self.width(), self.height() * 0.7))
        self.groupbox_1.setMinimumSize(QSize(self.width(), self.height() * 0.5))
        self.groupbox_2.setMaximumSize(QSize(self.width(), self.height() * 0.15))
        self.groupbox_3.setMaximumSize(QSize(self.width(), self.height() * 0.15))
        self.groupbox_4.setMaximumSize(QSize(self.width(), self.height() * 0.15))
        self.mainVLayout.addWidget(self.groupbox_4)
        self.mainVLayout.addWidget(self.groupbox_1)
        self.mainVLayout.addWidget(self.groupbox_2)
        self.mainVLayout.addWidget(self.groupbox_3)
        self.centralwidget.setLayout(self.mainVLayout)

        self.MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(self.MainWindow)
        # QMetaObject.connectSlotsByName(self.MainWindow)

    def setbox_1(self):
        # 容器1
        self.groupbox_1 = QGroupBox()

        self.label = QLabel()
        self.label.setGeometry(QRect(30, 10, 571, 391))
        font = QFont()
        font.setPointSize(46)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setFrameShape(QFrame.Box)
        self.label.setFrameShadow(QFrame.Raised)
        self.label.setLineWidth(3)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QLabel()
        self.label_2.setGeometry(QRect(30, 410, 571, 391))
        font = QFont()
        font.setPointSize(46)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setFrameShape(QFrame.Box)
        self.label_2.setFrameShadow(QFrame.Raised)
        self.label_2.setLineWidth(3)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setObjectName("label_2")

        # 将控件放入布局1中
        initbox(self.groupbox_1,[self.label,self.label_2])

    def setbox_2(self):
        # 容器2
        self.groupbox_2 = QGroupBox()

        self.pushButton = QPushButton()
        self.pushButton.setGeometry(QRect(700, 110, 201, 81))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(40)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QPushButton()
        self.pushButton_2.setGeometry(QRect(700, 240, 201, 81))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(40)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QPushButton()
        self.pushButton_3.setGeometry(QRect(700, 370, 201, 81))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(40)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QPushButton()
        self.pushButton_4.setGeometry(QRect(700, 500, 201, 81))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(40)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")

        # # 将控件放入布局2中
        # initbox(self.groupbox_2, [self.pushButton, self.pushButton_2,self.pushButton_3,self.pushButton_4],IsMargins=0)
    # def setbox_3(self):
        # 容器3
        self.groupbox_3 = QGroupBox()

        self.pushButton_5 = QPushButton()
        self.pushButton_5.setGeometry(QRect(700, 110, 201, 81))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(40)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QPushButton()
        self.pushButton_6.setGeometry(QRect(700, 240, 201, 81))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(40)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QPushButton()
        self.pushButton_7.setGeometry(QRect(700, 240, 201, 81))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(40)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_8 = QPushButton()
        self.pushButton_8.setGeometry(QRect(700, 240, 201, 81))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(40)
        self.pushButton_8.setFont(font)
        self.pushButton_8.setObjectName("pushButton_8")

        # 将控件放入布局中
        initbox(self.groupbox_2, [self.pushButton, self.pushButton_2, self.pushButton_6, self.pushButton_7],
                IsMargins=0)
        initbox(self.groupbox_3, [self.pushButton_3, self.pushButton_5,self.pushButton_4],
                IsMargins=0)

    def setbox_4(self):
        # 容器4
        self.groupbox_4 = QGroupBox()

        self.label_3 = QLabel()
        self.label_3.setGeometry(QRect(30, 10, 571, 391))
        font = QFont()
        font.setPointSize(46)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setFrameShape(QFrame.Box)
        self.label_3.setFrameShadow(QFrame.Raised)
        self.label_3.setLineWidth(3)
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_4 = QLabel()
        self.label_4.setGeometry(QRect(30, 410, 571, 391))
        font = QFont()
        font.setPointSize(46)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setFrameShape(QFrame.Box)
        self.label_4.setFrameShadow(QFrame.Raised)
        self.label_4.setLineWidth(3)
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_4.setObjectName("label_4")

        # 将控件放入布局1中
        initbox(self.groupbox_4,[self.label_3,self.label_4])

    def center(self,MainWindow):
        '''窗口居中'''
        size = MainWindow.geometry()
        screen = QDesktopWidget().screenGeometry()
        height = (screen.height() - size.height()) / 2
        width = (screen.width() - size.width()) / 2
        if height <= 50:
            height = 0
        if width <= 50:
            width = 0
        MainWindow.move(width,height)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "故障诊断"))
        self.label.setText(_translate("MainWindow", "摄像头"))
        self.label_2.setText(_translate("MainWindow", "图片显示"))
        self.label_3.setText(_translate("MainWindow", "数据未采集"))
        self.label_4.setText(_translate("MainWindow", "设备未运行"))
        self.pushButton.setText(_translate("MainWindow", "获取相机信息"))
        self.pushButton_2.setText(_translate("MainWindow", "打开摄像机"))
        self.pushButton_3.setText(_translate("MainWindow", "图片采集"))
        self.pushButton_4.setText(_translate("MainWindow", "关闭摄像机"))
        self.pushButton_5.setText(_translate("MainWindow", "训练模型"))
        self.pushButton_6.setText(_translate("MainWindow", "开始分拣"))
        self.pushButton_7.setText(_translate("MainWindow", "结束分拣"))
        self.pushButton_8.setText(_translate("MainWindow", "训练中止"))

class RoundProgress(QWidget):
    '''环形进度条'''
    m_waterOffset = 0.05
    m_offset = 50
    bg_color = QColor(255, 0, 0)
    fsize = 10
    def __init__(self, t, parent=None):
        super(RoundProgress, self).__init__(parent)
        self.resize(*t)
        self.size = t
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.percent = 0
        self.pen = QPen()
        gradient = QConicalGradient(50, 50, 91)
        gradient.setColorAt(0, QColor(255, 10, 10))
        gradient.setColorAt(1, QColor(255, 201 ,14))
        #gradient.setColorAt(0.5, QColor(255, 201 ,14))
        self.pen.setBrush(gradient)  # 设置画刷渐变效果
        self.pen.setWidth(8)
        self.pen.setCapStyle(Qt.RoundCap)
        self.font = QFont()
        # self.font.setFamily("Consolas") #Share-TechMono
        self.font.setPointSize(self.size[0] // 4)

    def paintEvent(self, event):
        width, height = self.size
        rect = QRectF(self.fsize, self.fsize, width - self.fsize * 2, height - self.fsize * 2)

        # 创建QPainter对象并激活它
        painter = QPainter(self)
        painter.begin(self)

        rotateAngle = 360 * self.percent / 100

        # 绘制准备工作，启用反锯齿
        painter.setRenderHints(QPainter.Antialiasing, True)
        painter.setPen(self.pen)

        painter.drawArc(rect, (90 - 0) * 16, -rotateAngle * 16)  # 画圆环
        painter.setFont(self.font)
        painter.setPen(QColor(153 - 1.53 * self.percent,
                              217 - 0.55 * self.percent,
                              234 - 0.02 * self.percent))  # 渐变颜色
        painter.drawText(rect, Qt.AlignCenter, "%d%%" % self.percent)  # 显示进度条当前进度

        # 结束绘画
        painter.end()

        self.update()

    def update_percent(self, p):
        self.percent = p


import sys
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
def Animation(parent, type=b"windowOpacity", from_value=0, to_value=1, ms=1000, connect=None):
    anim = QPropertyAnimation(parent, type)
    anim.setDuration(ms)
    anim.setStartValue(from_value)
    anim.setEndValue(to_value)
    if connect:
        anim.finished.connect(connect)
    anim.start()
    return anim
class ProgressThread(QThread):
    signal = pyqtSignal()
    def run(self):
        # for p in range(100):
        self.signal.emit()
            # self.msleep(100)
class PainterThread(QThread):
    signal = pyqtSignal()
    def run(self):
        for p in range(99):
            if not istreading:
                return
            self.signal.emit()
            self.msleep(20)

class WaterProgress(QWidget):
    '''水波进度条'''
    fsize = 10
    def __init__(self,t,parent=None):
        super(WaterProgress, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.resize(*t)
        self.size = t
        self.layout = QGridLayout(self)

        #设置进度条颜色
        self.bg_color = QColor("#95BBFF")
        self.m_waterOffset = 0.005
        self.m_offset = 50
        self.m_borderwidth = 10
        self.percent = 0
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing,True)
        painter.setPen(Qt.NoPen)
        #获取窗口的宽度和高度
        width,height = self.size
        percentage = 1 - self.percent/100
        # 水波走向：正弦函数 y = A(wx+l) + k
        # w 表示 周期，值越大密度越大
        w = 2 * math.pi / (width)
        # A 表示振幅 ，理解为水波的上下振幅
        A = height * self.m_waterOffset
        # k 表示 y 的偏移量，可理解为进度
        k = height *percentage


        water1 = QPainterPath()
        water2 = QPainterPath()
        #起始点
        water1.moveTo(5,height)
        water2.moveTo(5,height)
        self.m_offset += 0.6

        if(self.m_offset >(width/2)):
            self.m_offset = 0
        i = 5

        rect = QRectF(self.fsize,self.fsize,width - self.fsize*2, height - self.fsize * 2)
        while(i < width-5):
            waterY1 = A*math.sin(w*i +self.m_offset ) + k
            waterY2 = A*math.sin(w*i + self.m_offset + width/2*w) + k

            water1.lineTo(i, waterY1)
            water2.lineTo(i, waterY2)
            i += 1

        water1.lineTo(width-5,height)
        water2.lineTo(width-5,height)

        totalpath = QPainterPath()
        #totalpath.addRect(rect)
        #painter.setBrush(Qt.gray)
        painter.drawRect(self.rect())
        painter.save()
        totalpath.addEllipse(rect)
        totalpath.intersected(water1)
        painter.setPen(Qt.NoPen)

        #设置水波的透明度
        watercolor1 =QColor(self.bg_color)
        watercolor1.setAlpha(100)
        watercolor2 = QColor(self.bg_color)
        watercolor2.setAlpha(150)
        path = totalpath.intersected(water1)
        painter.setBrush(watercolor1)
        painter.drawPath(path)


        path = totalpath.intersected(water2)
        painter.setBrush(watercolor2)
        painter.drawPath(path)
        painter.restore()
        painter.end()
        #self.update()
    def update_percent(self, p):
        self.percent = p
        if self.m_waterOffset < 0.05:
            self.m_waterOffset += 0.001
        return p

class Progress(QDialog):
    percent = 0
    def __init__(self, num=30,parent=None):
        super(Progress, self).__init__(parent)

    # def setupUi(self, num=30,parent=None):
        self.num = num
        Font = QFont()
        # Font.setFamily("Consolas")
        Font.setPointSize(12)
        self.setFont(Font)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去边框
        # self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.ProgressThread = ProgressThread() # 自动加载进度
        self.ProgressThread.signal.connect(self.percentUpdate)
        # self.ProgressThread.start()
        width, height = 460, 460
        self.resize(width, height)
        self.water = WaterProgress((width, height), self)
        self.round = RoundProgress((width, height), self)
        # self.label = QLabel(self)
        # self.label.setText(QCoreApplication.translate("Dialog", text))
        # print(self.label.width())
        # self.label.move(int((width-self.label.width())/2), int(height/3*2))
        # QMetaObject.connectSlotsByName(self)
        # self.anim = Animation(self, )
        self.label2_1 = QLabel(self)
        # self.label2_1.setAlignment(Qt.AlignCenter | Qt.AlignCenter)gray
        self.label2_1.setStyleSheet("color:red")
        self.label2_1.setText(QCoreApplication.translate("Dialog", f'模型训练轮次：0/{self.num}'))
        self.label2_2 = QLabel(self)
        # self.label2_2.setAlignment(Qt.AlignCenter | Qt.AlignCenter) #字体居中
        self.label2_2.setStyleSheet("color:red")
        self.label2_2.setText(QCoreApplication.translate("Dialog", 'acc：0.00'))
        self.label2_3 = QLabel(self)
        self.label2_3.setStyleSheet("color:red")
        # self.label2_3.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.label2_3.setText(QCoreApplication.translate("Dialog", 'loss：0.00'))
        self.label2_1.move(int((width - self.label2_1.width()) / 2 - 100), int(height / 4))
        self.label2_2.move(50, int(height / 3 * 2))
        self.label2_3.move(self.label2_2.width() + 150, int(height / 3 * 2))
        font = QFont()
        font.setPointSize(23)
        font.setBold(True)
        font.setItalic(True)
        self.label2_1.setFont(font)
        self.label2_2.setFont(font)
        self.label2_3.setFont(font)
        self.btn = QPushButton(self)
        self.btn.setText('训练中止')
        self.btn.move(int((width - self.btn.width()) / 2 - 25), int(height / 3 * 2 + 50))
        self.btn.clicked.connect(self.closeEvent)
        self.btn.setFont(font)

        self.label2_1.setFrameStyle(0)
        self.label2_2.setFrameStyle(0)
        self.label2_3.setFrameStyle(0)

        QMetaObject.connectSlotsByName(self)
        self.anim = Animation(self, )
        self.setWindowModality(Qt.ApplicationModal)# 设置主窗口不可操作
    # def connect(self, link):
    #     print(type(link))
    #     #self.setWindowFlags(Qt.WindowStaysOnTopHint) #置顶
    #     self.show()
    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None
    def percentUpdate(self):
        self.percent += int(100 / self.num)
        self.water.update_percent(self.percent)
        # self.water.paintEvent(None)
        self.water.repaint()
        self.round.update_percent(self.percent)
        if self.percent >= 100:
            self.setWindowModality(Qt.NonModal)  # 恢复正常模式
    def closeEvent(self, event):
        self.close()
        os._exit(0)

class Progress2(QDialog):
    '''加载动画'''
    percent = 0
    def __init__(self):
        super(Progress2, self).__init__()
        global istreading
        istreading = 1
        self.is_mainwin = 0
    # def setupUi(self, num=30,parent=None):
        Font = QFont()
        # Font.setFamily("Consolas")
        Font.setPointSize(12)
        self.setFont(Font)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去边框
        # self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.QCoreThread = ProgressThread()
        self.PainterThread = PainterThread()  # 自动加载进度
        self.PainterThread.signal.connect(self.startUpdate)
        # self.ProgressThread.start()
        width, height = 460, 460
        self.resize(width, height)
        self.water = WaterProgress((width, height), self)
        self.round = RoundProgress((width, height), self)
        font = QFont()
        font.setPointSize(23)
        font.setBold(True)
        font.setItalic(True)
        QMetaObject.connectSlotsByName(self)
        self.anim = Animation(self, )
    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None
    def startUpdate(self):
        self.percent += 1
        self.water.update_percent(self.percent)
        # self.water.paintEvent(None)
        self.water.repaint()
        self.round.update_percent(self.percent)
        if self.is_mainwin and self.percent >= 99:
            self.mainwinThread.start()
    def closeend(self):
        global istreading
        istreading = 0
        # self.close()
        self.done(0)
    def closeEvent(self, event):
        self.close()
        os._exit(0)
