import logging
import os.path
import sys

import numpy as np
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QStackedWidget, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, QSize, QRect

import config
# from ui.ui_led import MyLed
from pyqt_led import Led

from ui.ui_led import LedWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('故障诊断')
        self.setWindowIcon(QIcon(config.ROOT_DIR + '/icons/1.ico'))

        main_layout = QHBoxLayout()

        # 左侧菜单栏
        self.set_left_menu()

        # 右侧内容区域
        content_layout = QVBoxLayout()

        self.set_led()

        # 创建 QGroupBox 用于内容界面
        groupBox = QGroupBox("内容界面")
        groupBox_layout = QVBoxLayout()

        # 创建 StackedWidget 用于管理不同页面
        self.stacked_widget = QStackedWidget()

        # 创建集成学习页面
        page1 = QWidget()
        page1_layout = QVBoxLayout()

        # 上面为学习统计结果数据表
        table = QTableWidget()
        table.setColumnCount(4)
        table.setRowCount(6)
        table.setHorizontalHeaderLabels(['列1', '列2', '列3', '列4'])

        # 下面为长文本实时滚动采集的数据
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        # 组织页面1布局
        page1_layout.addWidget(table)
        page1_layout.addWidget(text_edit)
        page1.setLayout(page1_layout)

        # 添加页面到 StackedWidget
        self.stacked_widget.addWidget(page1)

        # 创建2D数据图页面
        page2 = Data2DWinodw()
        # page2_layout = QVBoxLayout()
        self.stacked_widget.addWidget(page2)

        # 创建3D数据图页面
        page3 = QWidget()
        page3_layout = QVBoxLayout()
        self.stacked_widget.addWidget(page3)

        # 创建数据采集页面
        page4 = QWidget()
        page4_layout = QVBoxLayout()
        self.stacked_widget.addWidget(page4)

        # 创建机器学习页面
        page5 = QWidget()
        page5_layout = QVBoxLayout()
        self.stacked_widget.addWidget(page5)

        # 创建深度学习页面
        page6 = QWidget()
        page6_layout = QVBoxLayout()
        self.stacked_widget.addWidget(page6)

        # 组织 QGroupBox 布局
        groupBox_layout.addWidget(self.stacked_widget)
        groupBox.setLayout(groupBox_layout)

        # 组织右侧布局
        content_layout.addLayout(self.weight_layout)
        content_layout.addWidget(groupBox)

        # 组织主布局
        main_layout.addLayout(self.leftMenuLayout)
        main_layout.addLayout(content_layout)

        # 创建中心部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 设置样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }

            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                margin: 5px;
                font-size: 16px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QLabel {
                background-color: #e0e0e0;
                padding: 10px;
                margin: 5px;
                font-size: 16px;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #ccc;
                padding: 10px;
                margin: 5px;
                font-size: 14px;
            }

            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                padding: 10px;
                margin: 5px;
                font-size: 14px;
            }

            QGroupBox {
                background-color: white;
                border: 1px solid #ccc;
                padding: 10px;
                margin: 5px;
                font-size: 16px;
            }

            QStackedWidget {
                background-color: white;
                border: 1px solid #ccc;
                padding: 10px;
                margin: 5px;
                font-size: 14px;
            }
        """)

        # 居中显示
        self.center()

        self.set_connections()


    @staticmethod
    def setup_button(button, height=45):
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy)
        button.setMinimumSize(QSize(0, height))
        button.setFont(config.font)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setLayoutDirection(Qt.LeftToRight)

    def add_button_to_layout(self, layout, text, height=45):
        btn = QPushButton(text)
        self.setup_button(btn, height)
        layout.addWidget(btn)
        return btn

    def setup_button(button, height=45):
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy)
        button.setMinimumSize(QSize(0, height))
        button.setFont(config.font)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setLayoutDirection(Qt.LeftToRight)

    def set_left_menu(self):
        """左侧菜单栏"""
        # 主布局
        self.leftMenuLayout = QVBoxLayout(self)
        self.leftMenuLayout.setSpacing(10)  # 增加按钮之间的间距
        self.leftMenuLayout.setContentsMargins(10, 10, 10, 10)  # 设置边距

        # 菜单按钮区域
        menuFrame = QFrame(self)
        menuFrame.setObjectName(u"menuFrame")
        menuFrame.setFrameShape(QFrame.NoFrame)
        menuFrame.setFrameShadow(QFrame.Raised)

        menuLayout = QVBoxLayout(menuFrame)
        menuLayout.setSpacing(0)
        menuLayout.setContentsMargins(0, 0, 0, 0)

        toggleBox = QFrame(menuFrame)
        toggleBox.setObjectName(u"toggleBox")
        toggleBox.setMaximumSize(QSize(16777215, 45))
        toggleBox.setFrameShape(QFrame.NoFrame)
        toggleBox.setFrameShadow(QFrame.Raised)

        toggleLayout = QVBoxLayout(toggleBox)
        toggleLayout.setSpacing(0)
        toggleLayout.setContentsMargins(0, 0, 0, 0)

        menuLayout.addWidget(toggleBox)

        topMenu = QFrame(menuFrame)
        topMenu.setObjectName(u"topMenu")
        topMenu.setFrameShape(QFrame.NoFrame)
        topMenu.setFrameShadow(QFrame.Raised)

        topMenuLayout = QVBoxLayout(topMenu)
        topMenuLayout.setSpacing(5)  # 增加按钮之间的垂直间距
        topMenuLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # 水平居中

        # 设置按钮高度为变量
        button_height = 45

        self.btn_ensemble_learning = self.add_button_to_layout(topMenuLayout, "集成学习", button_height)
        self.btn_2d_data = self.add_button_to_layout(topMenuLayout, "2D 数据图", button_height)
        self.btn_3d_data = self.add_button_to_layout(topMenuLayout, "3D 数据图", button_height)
        self.btn_data_collection = self.add_button_to_layout(topMenuLayout, "数据采集", button_height)
        self.btn_machine_learning = self.add_button_to_layout(topMenuLayout, "机器学习", button_height)
        self.btn_deep_learning = self.add_button_to_layout(topMenuLayout, "深度学习", button_height)

        # 设置按钮图标
        self.btn_ensemble_learning.setIcon(QIcon(os.path.join(config.ROOT_DIR,'icons/集成.png')))
        self.btn_2d_data.setIcon(QIcon(os.path.join(config.ROOT_DIR,'icons/2D.png')))
        self.btn_3d_data.setIcon(QIcon(os.path.join(config.ROOT_DIR,'icons/3D.png')))
        self.btn_data_collection.setIcon(QIcon(os.path.join(config.ROOT_DIR,'icons/数据采集.png')))
        self.btn_machine_learning.setIcon(QIcon(os.path.join(config.ROOT_DIR,'icons/机器学习.png')))
        self.btn_deep_learning.setIcon(QIcon(os.path.join(config.ROOT_DIR,'icons/深度学习.png')))

        # 将按钮添加到布局中
        topMenuLayout.addWidget(self.btn_ensemble_learning)
        topMenuLayout.addWidget(self.btn_2d_data)
        topMenuLayout.addWidget(self.btn_3d_data)
        topMenuLayout.addWidget(self.btn_data_collection)
        topMenuLayout.addWidget(self.btn_machine_learning)
        topMenuLayout.addWidget(self.btn_deep_learning)

        menuLayout.addWidget(topMenu)

        self.leftMenuLayout.addWidget(menuFrame)

    def set_led(self):
        # 假设 config 已经定义好，并且有 train_class 和 font 属性
        # 顶部信号灯
        self.weight_layout = QHBoxLayout()
        train_widget = LedWindow()
        self.weight_layout.addWidget(train_widget)

    def center(self):
        '''窗口居中'''
        size = self.geometry()
        screen = QApplication.desktop().screenGeometry()
        try:
            height = (screen.height() - size.height()) / 2
            width = (screen.width() - size.width()) / 2
        except (AttributeError, TypeError) as e:
            logging.error(f"Failed to get screen geometry: {e} - screen: {screen}, size: {size}")
            height = 0
            width = 0

        if height <= 50:
            height = 0
        if width <= 50:
            width = 0

        self.move(width, height)

    def set_connections(self):
        def handle_home_button_clicked():
            print("Home button clicked")

        def handle_button_clicked(index):
            self.stacked_widget.widget(index).initUI()
            self.stacked_widget.setCurrentIndex(index)

        self.btn_ensemble_learning.clicked.connect(lambda: handle_button_clicked(0))
        self.btn_2d_data.clicked.connect(lambda: handle_button_clicked(1))
        self.btn_3d_data.clicked.connect(lambda: handle_button_clicked(2))
        self.btn_data_collection.clicked.connect(lambda: handle_button_clicked(3))
        self.btn_machine_learning.clicked.connect(lambda: handle_button_clicked(4))
        self.btn_deep_learning.clicked.connect(lambda: handle_button_clicked(5))
