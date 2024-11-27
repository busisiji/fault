# coding: utf-8
import re
import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from qt_material import apply_stylesheet

import config
from db.db_mysql import DB_MySQL
from lib.faultDiagnosis_model import faultDiagnosisModel
from ui.ui_calulateWindow import OrderInventoryApp
from ui.ui_configWindow import ConfigWindow
from ui.ui_predictWindow import PredictWindow
from ui.ui_sensorWindow import SensorWindow
from ui.qss import btn_css, stylesheet
from ui.ui_data2DWindow import Data2DWindow
from ui.ui_data3DWindow import Data3DWindow
from ui.ui_dataCollectionAllWindow import DataCollectionAllWindow
from ui.ui_dataCollectionWindow import DataCollectionWindow
from ui.ui_ensembleWindow import EnsembleWindow
from ui.ui_foldLineWindow import  FoldLineWindow
from ui.others.ui_led import MyLed
from ui.ui_modbusFrame import ModbusTCPFrame
from ui.ui_start import MySplashScreen, Form
from ui.ui_trainWindow import TrainWindow
# from ui.ui_warningMessageWindow import WarningMessageWindow
from utils.data_load import check_and_create_csv_files


class MainWindow(QMainWindow):
    _single_update_ui = pyqtSignal()
    _single_update_led = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.resize(config.main_weight, config.main_height)  # 设置窗口大小
        self.setWindowIcon(QIcon(config.ROOT_DIR + '/icons/1.ico'))
        # 设置固定高度
        self.setFixedHeight( QApplication.desktop().screenGeometry().height())

        # 初始化操作
        # 创建数据集
        check_and_create_csv_files()

        self.fualt_model = faultDiagnosisModel()


        self.leds = []
        self.led_labels = []
        self.led_label_texts = []
        self.IsRun = False # 运行状态
        self.IsOnlyUse2 = True

        self.initUI()
        self.center()

        self.timer_sensors_num = 0 # 采集时间
        self.timer_sensors = QtCore.QTimer(self)
        self.timer_sensors.timeout.connect(self.update_sensors)

        self._single_update_ui.connect(self.update_ui)
        self._single_update_led.connect(self.setbox_switch)

        # 隐藏切换菜单按钮
        self.toggle_button.hide()

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

        self.switcher_1 = {
            0: 1,  # ensembleWindow
            1: 2,  # data2DWindow
            2: 3,  # data3DWindow
            3: 4,  # dataCollectionWindow
        }
        menu_items2 = [
            ('传感器配置', config.ROOT_DIR + '/icons/传感器.png'),
            # ('通讯助手', config.ROOT_DIR + '/icons/通讯.png'),
            ('图表显示', config.ROOT_DIR + '/icons/数据视图.png'),
            ('数据运维', config.ROOT_DIR + '/icons/数据采集.png'),
            ('模型训练', config.ROOT_DIR + '/icons/机器学习.png'),
            ('模型预测', config.ROOT_DIR + '/icons/集成.png'),
            ('历史报警', config.ROOT_DIR + '/icons/条型图.png'),
            ('物料统计', config.ROOT_DIR + '/icons/数据统计.png'),
        ]
        self.switcher_2 = {
            0: 0,
            # 1: 7,  # ensembleWindow
            1: 6,  # foldLineWindow
            2: 5,  # dataCollectionAllWindow
            3: 8,  # trainWindow
            4: 9,  # predictWindow
            5: 10,
            #6:11, # warningMessageWindow
        }

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
        self.configWindow = ConfigWindow(self)
        ensembleWindow = EnsembleWindow(self)
        self.trainWindow = TrainWindow(self)
        data2DWindow = Data2DWindow(self)
        data3DWindow = Data3DWindow(self)
        dataCollectionWindow = DataCollectionWindow(self,1)
        self.dataCollectionAllWindow = DataCollectionAllWindow(self,2) # 多传感器采集
        self.foldLineWindow = FoldLineWindow(self)
        self.serialWindow = SensorWindow(self)
        self.predictWindow = PredictWindow(self)
        self.orderInventoryApp = OrderInventoryApp(self)
        #         self.warningMessageWindow = WarningMessageWindow(self)

        self.pages = [self.configWindow, ensembleWindow, data2DWindow, data3DWindow, dataCollectionWindow,
                      self.dataCollectionAllWindow, self.foldLineWindow, self.serialWindow, self.trainWindow,
                      self.predictWindow,self.orderInventoryApp]

        # 将子界面添加到堆叠窗口
        for page in self.pages:
            self.stacked_widget.addWidget(page)

        # 创建切换按钮
        self.toggle_button = QPushButton('切换菜单', self)
        btn_css(self.toggle_button)
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        # 创建主布局
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar1)
        sidebar_layout.addWidget(self.sidebar2)
        sidebar_layout.addWidget(self.toggle_button)

        # modbus侧边栏
        self.left_frame = ModbusTCPFrame(self)


        main_layout = QHBoxLayout()
        main_layout.addLayout(sidebar_layout)
        main_layout.addWidget(self.left_frame)
        main_layout.addWidget(self.stacked_widget)

        self.setbox_led()
        main_layout.addWidget(self.groupbox_led)

        # 初始化
        self.setWindowTitle(config.title_class[1])
        self.sidebar1.hide()
        self.current_sidebar = self.sidebar2
        # self.groupbox_led.hide()  # 初始隐藏groupbox_led

        # 设置主窗口的中央部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


    def on_menu_clicked(self, item, type):
        index = self.current_sidebar.row(item)
        if type == 1:
            self.stacked_widget.setCurrentIndex(self.switcher_1.get(index, 0))

        elif type == 2:

            self.stacked_widget.setCurrentIndex(self.switcher_2.get(index, 0))

    def toggle_sidebar(self):
        """切换菜单"""
        # 第二个菜单显示
        if self.current_sidebar == self.sidebar1:
            self.sidebar1.hide()
            self.sidebar2.show()
            self.left_frame.show()
            self.current_sidebar = self.sidebar2
            self.setWindowTitle(config.title_class[1])
            self.groupbox_led.show()  # 显示groupbox_led
        # 第一个菜单显示
        else:
            self.sidebar2.hide()
            self.sidebar1.show()
            self.left_frame.hide()
            self.current_sidebar = self.sidebar1
            self.setWindowTitle(config.title_class[0])
            self.groupbox_led.hide()  # 隐藏groupbox_led

    def setbox_led(self, Is_update=False):
        if not hasattr(self, 'groupbox_led'):
            self.groupbox_led = QWidget()

            font = QFont()
            font.setPointSize(23)
            self.groupbox_led.setFont(font)

        if not hasattr(self, 'VLayout_led'):
            self.VLayout_led = QVBoxLayout(self.groupbox_led)
            self.VLayout_led.setContentsMargins(0, 0, 0, 0)

        self.setbox_new()
        self.setbox_switch()
        self.VLayout_led.addWidget(self.groupbox_new)
        self.VLayout_led.addWidget(self.groupbox_switch)

        # 将主布局设置到父窗口或容器中
        self.groupbox_led.setLayout(self.VLayout_led)

    def setbox_switch(self,Is_update=False):
        if not hasattr(self, 'groupbox_switch'):
            self.groupbox_switch = QGroupBox('传感器状态')
            font = QFont()
            font.setPointSize(23)
            self.groupbox_switch.setFont(font)

        if not hasattr(self, 'VLayout_switch'):
            self.VLayout_switch = QGridLayout(self.groupbox_switch)

        try:
            self.db = DB_MySQL()
            with self.db:
                sensor_class = self.db.select_data(config.toname['开关传感器'], 'sensor_name')
        except Exception as e:
            print('开关传感器error', 2)
            sensor_class = []

        num_classes = len(sensor_class)

        # 获取当前已存在的控件
        current_leds = {led.text(): led for led in self.led_labels}
        current_labels = {label.text(): label for label in self.led_labels}

        # 删除不在数据库中的控件
        for name in list(current_leds.keys()):
            if name not in [list(sensor.values())[0] for sensor in sensor_class]:
                index = self.led_labels.index(current_labels[name])
                self.leds[index].deleteLater()
                self.led_labels[index].deleteLater()
                del self.leds[index]
                del self.led_labels[index]

        # 创建新的控件
        for i, sensor in enumerate(sensor_class):
            name = list(sensor.values())[0]
            if name not in current_labels:
                ledSingle = MyLed(self.groupbox_led)
                ledSingle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.leds.append(ledSingle)

                label_led = QLabel(name)
                label_led.setStyleSheet("color:black;border: 0px;")
                label_led.setFont(QFont())
                label_led.setWordWrap(True)
                label_led.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.led_labels.append(label_led)

                # 计算行和列
                row = i % 6
                col = i // 6

                # 将控件放入布局中
                self.VLayout_switch.addWidget(label_led, row * 2 + 1, col * 2 + 1)
                self.VLayout_switch.addWidget(ledSingle, row * 2 + 1, col * 2)

        # 设置布局
        self.groupbox_switch.setLayout(self.VLayout_switch)
        if Is_update:
            self.groupbox_switch.update()

    def setbox_new(self):
        if not hasattr(self, 'groupbox_new'):
            self.groupbox_new = QGroupBox('系统状态')
            font = QFont()
            font.setPointSize(23)
            self.groupbox_new.setFont(font)

        if not hasattr(self, 'VLayout_new'):
            self.VLayout_new = QVBoxLayout(self.groupbox_new)

        self.new_led = MyLed(self.groupbox_new)
        self.new_label = QLabel('无任务')
        self.new_label.setStyleSheet("color:black;border: 0px;")
        self.new_label.setFont(QFont())
        self.new_label.setWordWrap(True)
        self.new_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.VLayout_new.addWidget(self.new_led)
        self.VLayout_new.addWidget(self.new_label)

        # 设置布局
        self.groupbox_new.setLayout(self.VLayout_new)


    def on_toggled(self, checked):
        if checked:
            self.toggle_button.setText("折叠")
            self.groupbox_led.show()
        else:
            self.toggle_button.setText("展开")
            self.groupbox_led.hide()
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

    def setRun(self,IsRun=False):
        """系统状态更新"""
        if IsRun:
            self.IsRun = True
            self.new_led.setChecked(True)
            self.new_label.setText(IsRun)
        else:
            self.new_led.setChecked(False)
            self.new_label.setText('无任务')
            self.IsRun = False

    def on_read_results(self, sensor_name, param_names,results):
        """采集数据"""
        if len(param_names) == len(results) and len(results) > 0:
            self.dataCollectionAllWindow._single_update_data.emit(sensor_name, param_names,results)
            # self.foldLineWindow.sensor_pages[sensor_name]._single_update_data.emit(param_names,results )
            self.foldLineWindow.sensor_pages[sensor_name].update_data(param_names,results)
        else:
            QMessageBox.information(self, "错误", "数据采集失败")

    def update_switch(self, sensor_names, status):
        """更新开关传感器状态"""
        # 确保 sensor_names 和 status 的长度一致
        if len(sensor_names) != len(status):
            return
        # 遍历 sensor_names 和 status
        for i, name in enumerate(sensor_names):
            # 查找对应的 LED
            for j, label in enumerate(self.led_labels):
                if label.text() == name:
                    # 更新 LED 状态
                    self.leds[j].setChecked(status[i] is True)
                    break



    def update_sensors(self):
        """定时采集数据后更新传感器地址参数"""
        if self.left_frame.worker:
            # for sensor in config.initialize_sensors():
                # self.left_frame.worker.read_register(sensor["address"])
            self.left_frame.worker.read_registers()

    def update_ui(self):
        """更新界面"""
        try:
            # 重新加载传感器状态
            self._single_update_led.emit(True)

            indices = list(self.switcher_2.values())
            # 使用列表推导式提取指定索引的元素
            pages = [self.pages[i] for i in indices]
            for page in pages:
                page._single_update_ui.emit()
        finally:
            # 更新完成
             self.setRun()


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
