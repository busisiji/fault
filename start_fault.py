# coding: utf-8
import os.path
import sys
from tkinter import messagebox

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from qt_material import apply_stylesheet

import config
from lib.faultDiagnosis_model import faultDiagnosisModel
from mySerial.modbusRtu import SerialWindow
from mySerial.modbusTcp import ModbusTCPWindow
from ui.qss import btn_css, stylesheet
from ui.ui_data2DWinodw import Data2DWindow
from ui.ui_data3DWindow import Data3DWindow
from ui.ui_dataCollectionAllWindow import DataCollectionAllWindow
from ui.ui_dataCollectionWindow import DataCollectionWindow
from ui.ui_ensembleWindow import EnsembleWindow
from ui.ui_foldLineWindow import TempHumidityWindow
from ui.ui_fun import CollapsibleSplitter
from ui.ui_led import MyLed
from ui.ui_start import MySplashScreen, Form
from utils.data_load import check_and_create_csv_files




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(config.main_weight, config.main_height)  # 设置窗口大小
        self.setWindowIcon(QIcon(config.ROOT_DIR + '/icons/1.ico'))

        # 初始化操作
        # 创建数据集
        check_and_create_csv_files()

        self.fualt_model = faultDiagnosisModel()

        self.initUI()
        self.center()

    def initUI(self):
        # 创建两个菜单栏
        self.sidebar1 = QListWidget(self)
        self.sidebar1.setStyleSheet(stylesheet)
        self.sidebar2 = QListWidget(self)
        self.sidebar2.setStyleSheet(stylesheet)

        # 添加菜单项
        menu_items1 = [
            ('集成学习', config.ROOT_DIR + '/icons/集成.png'),
            ('2D 数据图', config.ROOT_DIR + '/icons/2D.png'),
            ('3D 数据图', config.ROOT_DIR + '/icons/3D.png'),
            ('数据采集', config.ROOT_DIR + '/icons/数据采集.png'),
        ]
        menu_items2 = [
            ('通讯助手', config.ROOT_DIR + '/icons/通讯.png'),
            ('数据视图', config.ROOT_DIR + '/icons/数据视图.png'),
            ('数据采集', config.ROOT_DIR + '/icons/数据采集.png'),
        ]

        for text, icon_path in menu_items1:
            item = QListWidgetItem(text)
            item.setIcon(QIcon(icon_path))
            self.sidebar1.addItem(item)

        for text, icon_path in menu_items2:
            item = QListWidgetItem(text)
            item.setIcon(QIcon(icon_path))
            self.sidebar2.addItem(item)

        # 为菜单项添加点击事件
        self.sidebar1.itemClicked.connect(lambda item: self.on_menu_clicked(item, 1))
        self.sidebar2.itemClicked.connect(lambda item: self.on_menu_clicked(item, 2))

        # 创建右侧堆叠窗口
        self.stacked_widget = QStackedWidget(self)
        # self.stacked_widget.setStyleSheet(stylesheet)

        # 初始化子界面
        self.pages = []
        ensembleWindow = EnsembleWindow(self)
        data2DWindow = Data2DWindow(self)
        data3DWindow = Data3DWindow(self)
        dataCollectionWindow = DataCollectionWindow(self,1)
        dataCollectionAllWindow = DataCollectionAllWindow(self,2) # 多传感器采集
        tempHumidityWindow = TempHumidityWindow(self)
        # serialWindow = SerialWindow(self)
        serialWindow = ModbusTCPWindow(self)
        # machineLearningWindow = MachineLearningWindow(self)
        # deepLearningWindow = DeepLearningWindow(self)

        # 将子界面添加到堆叠窗口
        self.stacked_widget.addWidget(ensembleWindow)
        self.stacked_widget.addWidget(data2DWindow)
        self.stacked_widget.addWidget(data3DWindow)
        self.stacked_widget.addWidget(dataCollectionWindow)
        self.stacked_widget.addWidget(dataCollectionAllWindow)
        self.stacked_widget.addWidget(tempHumidityWindow)
        self.stacked_widget.addWidget(serialWindow)
        # self.stacked_widget.addWidget(machineLearningWindow)
        # self.stacked_widget.addWidget(deepLearningWindow)

        # 创建切换按钮
        self.toggle_button = QPushButton('切换菜单', self)
        btn_css(self.toggle_button)
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        # 创建主布局
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar1)
        sidebar_layout.addWidget(self.sidebar2)
        sidebar_layout.addWidget(self.toggle_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(sidebar_layout)
        main_layout.addWidget(self.stacked_widget)
        self.setbox_3()
        main_layout.addWidget(self.groupbox_3)

        # 初始化
        self.setWindowTitle(config.title_class[1])
        self.sidebar1.hide()
        self.current_sidebar = self.sidebar2
        # self.groupbox_3.hide()  # 初始隐藏groupbox_3

        # 设置主窗口的中央部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def on_menu_clicked(self, item, type):
        index = self.current_sidebar.row(item)
        if type == 1:
            switcher = {
                0: 0,  # ensembleWindow
                1: 1,  # data2DWindow
                2: 2,  # data3DWindow
                3: 3,  # dataCollectionWindow
            }
            self.stacked_widget.setCurrentIndex(switcher.get(index, 0))

        elif type == 2:
            # 使用字典模拟 switch 语句
            switcher = {
                0: 6,  # ensembleWindow
                1: 5,  # tempHumidityWindow
                2: 4,  # dataCollectionAllWindow
            }
            self.stacked_widget.setCurrentIndex(switcher.get(index, 0))

    def toggle_sidebar(self):
        """切换菜单"""
        if self.current_sidebar == self.sidebar1:
            self.sidebar1.hide()
            self.sidebar2.show()
            self.current_sidebar = self.sidebar2
            self.setWindowTitle(config.title_class[1])
            self.groupbox_3.show()  # 显示groupbox_3
        else:
            self.sidebar2.hide()
            self.sidebar1.show()
            self.current_sidebar = self.sidebar1
            self.setWindowTitle(config.title_class[0])
            self.groupbox_3.hide()  # 隐藏groupbox_3

    def setbox_3(self):
        # 容器3
        # 创建groupbox_3并设置标题
        self.groupbox_3 = QGroupBox('传感器状态')
        font = QFont()
        font.setPointSize(23)
        self.groupbox_3.setFont(font)

        # 初始化网格布局
        self.VLayout_3 = QGridLayout(self.groupbox_3)

        # 创建LED列表
        self.leds = []

        # 获取配置中的类别数量
        num_classes = len(config.sensor_class)

        # 创建LED和标签
        for i in range(num_classes):
            name = list(config.sensor_class)[i]
            ledSingle = MyLed(self.groupbox_3)
            ledSingle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.leds.append(ledSingle)

            label_led = QLabel(name)
            label_led.setStyleSheet("color:black;border: 0px;")
            label_led.setFont(QFont())
            label_led.setWordWrap(True)
            label_led.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            # 将控件放入布局中
            self.VLayout_3.addWidget(label_led,  i + 1,1)
            self.VLayout_3.addWidget(ledSingle, i + 1,0)

        # 设置布局
        self.groupbox_3.setLayout(self.VLayout_3)

    def on_toggled(self, checked):
        if checked:
            self.toggle_button.setText("折叠")
            self.groupbox_3.show()
        else:
            self.toggle_button.setText("展开")
            self.groupbox_3.hide()
    def center(self):
        '''窗口居中'''
        size = self.geometry()
        screen = QApplication.desktop().screenGeometry()
        try:
            height = (screen.height() - size.height()) / 2
            width = (screen.width() - size.width()) / 2
        except (AttributeError, TypeError) as e:
            height = 0
            width = 0

        if height <= 50:
            height = 0
        if width <= 50:
            width = 0

        self.move(int(width), int(height))


class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r', encoding='UTF-8') as file:
            return file.read()


if __name__ == '__main__':

    app = QApplication(sys.argv)

    screen = app.primaryScreen()  # 获取主屏幕对象
    # 使用geometry()方法获取屏幕的矩形区域
    screen_geometry = screen.geometry()
    config.set_screen(screen_geometry)

    splash = MySplashScreen()
    # splash.setPixmap(QPixmap(r'D:\图标\28c932975ab836b2d1939979db0fd8b8.jpg'))  # 设置背景图片
    splash.setFont(QFont('微软雅黑', 10))  # 设置字体
    splash.show()

    app.processEvents()  # 处理主进程，不卡顿
    form = Form(splash)
    window = MainWindow()

    # # setup stylesheet
    # 调试时注释掉样式，不然可能闪退
    apply_stylesheet(app, theme='light_teal.xml')

    form.show()
    # splash.finish(form)  # 主界面加载完成后隐藏
    splash.movie.stop()  # 停止动画
    # 关闭并删除 form 界面
    form.close()
    form.deleteLater()
    splash.deleteLater()

    window.showMaximized()

    sys.exit(app.exec_())
