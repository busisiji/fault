import logging
import sys
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QStackedWidget, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, QSize, QRect

import config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('故障诊断')
        self.setWindowIcon(QIcon(config.ROOT_DIR + '/icons/1.ico'))

        main_layout = QHBoxLayout()

        # 左侧菜单栏
        leftMenuLayout = self.set_left_menu()

        # 右侧内容区域
        content_layout = QVBoxLayout()

        # 顶部信号灯
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel('正常'))
        weight_layout.addWidget(QLabel('偏轴'))

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
        page2 = QWidget()
        page2_layout = QVBoxLayout()
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
        content_layout.addLayout(weight_layout)
        content_layout.addWidget(groupBox)

        # 组织主布局
        main_layout.addLayout(leftMenuLayout)
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
    def setup_button(button, config, height=45):
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy)
        button.setMinimumSize(QSize(0, height))
        button.setFont(config.font)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setLayoutDirection(Qt.LeftToRight)

    def add_button_to_layout(self, layout, text, config, height=45):
        btn = QPushButton(text)
        self.setup_button(btn, config, height)
        layout.addWidget(btn)
        return btn

    def set_left_menu(self):
        self.leftMenuFrame = QFrame(self)
        self.leftMenuFrame.setObjectName(u"leftMenuFrame")
        self.leftMenuFrame.setFrameShape(QFrame.NoFrame)
        self.leftMenuFrame.setFrameShadow(QFrame.Raised)

        # 主布局
        leftMenuLayout = QVBoxLayout(self.leftMenuFrame)
        leftMenuLayout.setSpacing(0)
        leftMenuLayout.setContentsMargins(0, 0, 0, 0)

        # 菜单按钮区域
        menuFrame = QFrame(self.leftMenuFrame)
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

        toggleButton = QPushButton(toggleBox)
        toggleButton.setObjectName(u"toggleButton")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)


        self.setup_button(toggleButton, config)
        toggleButton.setStyleSheet(u"background-image: url(:/icons/images/icons/icon_menu.png);")

        toggleLayout.addWidget(toggleButton)

        menuLayout.addWidget(toggleBox)

        topMenu = QFrame(menuFrame)
        topMenu.setObjectName(u"topMenu")
        topMenu.setFrameShape(QFrame.NoFrame)
        topMenu.setFrameShadow(QFrame.Raised)

        topMenuLayout = QVBoxLayout(topMenu)
        topMenuLayout.setSpacing(0)
        topMenuLayout.setContentsMargins(0, 0, 0, 0)

        # 设置按钮高度为变量
        button_height = 45

        self.btn_home = self.add_button_to_layout(topMenuLayout, "Home", config, button_height)
        self.btn_ensemble_learning = self.add_button_to_layout(topMenuLayout, "集成学习", config, button_height)
        self.btn_2d_data = self.add_button_to_layout(topMenuLayout, "2D 数据图", config, button_height)
        self.btn_3d_data = self.add_button_to_layout(topMenuLayout, "3D 数据图", config, button_height)
        self.btn_data_collection = self.add_button_to_layout(topMenuLayout, "数据采集", config, button_height)
        self.btn_machine_learning = self.add_button_to_layout(topMenuLayout, "机器学习", config, button_height)
        self.btn_deep_learning = self.add_button_to_layout(topMenuLayout, "深度学习", config, button_height)

        # 将按钮添加到布局中
        topMenuLayout.addWidget(self.btn_home)
        topMenuLayout.addWidget(self.btn_ensemble_learning)
        topMenuLayout.addWidget(self.btn_2d_data)
        topMenuLayout.addWidget(self.btn_3d_data)
        topMenuLayout.addWidget(self.btn_data_collection)
        topMenuLayout.addWidget(self.btn_machine_learning)
        topMenuLayout.addWidget(self.btn_deep_learning)

        menuLayout.addWidget(topMenu)

        leftMenuLayout.addWidget(menuFrame)

        # 设置左侧菜单栏的固定宽度
        self.leftMenuFrame.setFixedWidth(200)

        return leftMenuLayout

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
            self.stacked_widget.setCurrentIndex(index)

        self.btn_home.clicked.connect(handle_home_button_clicked)
        self.btn_ensemble_learning.clicked.connect(lambda: handle_button_clicked(0))
        self.btn_2d_data.clicked.connect(lambda: handle_button_clicked(1))
        self.btn_3d_data.clicked.connect(lambda: handle_button_clicked(2))
        self.btn_data_collection.clicked.connect(lambda: handle_button_clicked(3))
        self.btn_machine_learning.clicked.connect(lambda: handle_button_clicked(4))
        self.btn_deep_learning.clicked.connect(lambda: handle_button_clicked(5))
