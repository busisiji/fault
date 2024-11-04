import os
import threading
import time
from tkinter import messagebox

import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QBrush, QFont, QIcon
from PyQt5.QtWidgets import *

import config
from config import font
from ui.qss import btn_css
from ui.ui_fun import setQMessageBox, BaseWindow, MyLabel
from ui.ui_led import MyLed
from utils.collect import get_new_datas, get_new_data
from utils.data_load import data_balance
from utils.gettty import main
from utils.my_thread import DataTableThread, MyThread


class EnsembleWindow(BaseWindow):
    '''集成学习窗口'''
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.initUI()

        #  模型训练线程
        self.trainModelsThread = MyThread(self.parent.fualt_model.train_models)
        self.trainModelsThread._signal.connect(self.theard_finished)

        #  模型加载线程
        self.loadModelsThread = MyThread(self.parent.fualt_model.load_models)
        self.loadModelsThread._signal.connect(self.theard_finished)

        # 数据采集和模型预测线程
        self.dataTableThread = DataTableThread(self)
        self.dataTableThread._signal_message.connect(self.show_message)
        self.dataTableThread._signal_led.connect(self.set_led)
        self.dataTableThread._signal_table_data.connect(self.set_tabel_text)
        self.dataTableThread._signal_label_data.connect(self.set_label_text)
        self.dataTableThread._signal_finish.connect(self.theard_finished)

    def initUI(self):
        self.is_data_join = False # 是否采集数据
        self.num = 1
        self.is_toggled = '' # 当前运行状态 '自动' '手动' '训练' '加载' ''

        self.setWindowTitle('集成学习')
        self.setFont(font)
        self.setWindowIcon(QIcon(os.path.join(config.ROOT_DIR , 'icons','1.ico')))
        # self.setWindowState(Qt.WindowMaximized) # 将窗口设置为最大化状态

        self.setbox_1()
        self.setbox_3()
        self.setbox_2()
        self.setbox_4()
        self.setbox_5()
        self.setbox_6()
        self.mainVLayout = QVBoxLayout(self)
        self.mainVLayout.setContentsMargins(0, 0, 0, 0)
        self.mainVLayout.setSpacing(0)
        self.mainVLayout.addWidget(self.groupbox_3)
        self.mainVLayout.addWidget(self.groupbox_1)
        self.mainVLayout.addWidget(self.groupbox_6)
        self.mainVLayout.addWidget(self.groupbox_2)
        self.mainVLayout.addWidget(self.groupbox_4)
        self.mainVLayout.addWidget(self.groupbox_5)
        # 设置高度比例为 7:3
        self.mainVLayout.setStretch(0, 2)  # groupbox_3 的高度比例
        self.mainVLayout.setStretch(1, 4)  # groupbox_1 的高度比例
        self.mainVLayout.setStretch(2, 1)  # groupbox_1 的高度比例
        self.mainVLayout.setStretch(3, 1)  # groupbox_1 的高度比例
        self.mainVLayout.setStretch(4, 1)  # groupbox_1 的高度比例
        self.mainVLayout.setStretch(5, 1)  # groupbox_1 的高度比例
        # 设置布局
        self.setLayout(self.mainVLayout)

    def setbox_1(self):
        # 容器1
        self.groupbox_1 = QGroupBox()

        # # 设置固定高度
        # self.groupbox_1.setFixedHeight(self.width()/5)  # 假设高度为200像素

        # 容器1_2 - 集成学习统计结果
        self.groupbox_1_2 = QGroupBox('集成学习统计结果')
        self.groupbox_1_2.setAlignment(Qt.AlignHCenter)
        self.groupbox_1_2.setFont(QFont('', 23))

        # 创建表格
        try:
            num_rows = len(config.train_class)
            if num_rows == 0:
                raise ValueError("config.train_class is empty")
        except TypeError:
            raise ValueError("config.train_class is not iterable")

        self.table = QTableWidget(num_rows, 6,self)
        self.table.setVerticalHeaderLabels(config.train_class)
        self.table.setHorizontalHeaderLabels(["逻辑回归", "支持向量机", "感知机", "K近邻算法", "随机森林", "决策树"])

        # 设置表格样式
        scrollbar_style = """
            QScrollBar::handle {{
                background: rgb(145, 145, 145);
                border: 0px solid grey;
                border-radius: 5px;
                width: 10px;
                height: 10px;
            }}
            QScrollBar {{
                padding: 40px 0px 0px 0px;
                background-color: rgb(56, 61, 93);
                border-style: solid;
                border-color: rgba(255, 255, 255, 10%);
                width: 12px;
                height: 12px;
            }}
            QScrollBar::add-page, QScrollBar::sub-page {{
                background: rgb(232, 232, 232);
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                background: transparent;
            }}
        """


        self.table.setStyleSheet(self.table_style )

        # 设置字体
        font = QFont('', 18)
        self.table.setFont(font)

        # 设置列宽和行高
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)


        # 禁止编辑
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 禁止选择单元格
        self.table.setSelectionMode(QAbstractItemView.NoSelection)

        self.init_table(self.table)

        # 布局1_2
        layout_1_2 = QHBoxLayout()
        layout_1_2.addWidget(self.table)
        # layout_1_2.setContentsMargins(10, 10, 10, 10)
        self.groupbox_1_2.setLayout(layout_1_2)

        # 容器1_1 - 设备数据
        self.groupbox_1_1 = QGroupBox('设备数据')
        self.groupbox_1_1.setAlignment(Qt.AlignHCenter)
        self.groupbox_1_1.setFont(QFont('', 23))

        # 文本内容
        self.label = MyLabel()
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignHCenter)
        self.label.setFont(QFont('', 14))
        self.label.setStyleSheet("color: black;")

        # 连接信号与槽
        self.label.textChanged.connect(self.on_text_changed)


        # 创建一个可滚动的区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 允许调整大小
        self.scroll_area.setWidget(self.label)  # 设置滚动区域中的小部件

        # 布局1_1
        layout_1_1 = QVBoxLayout()
        layout_1_1.addWidget(self.scroll_area)
        # layout_1_1.setContentsMargins(10, 10, 10, 10)
        self.groupbox_1_1.setLayout(layout_1_1)

        # 布局1
        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.groupbox_1_2)
        layout_1.addWidget(self.groupbox_1_1)
        # layout_1.setContentsMargins(10, 10, 10, 10)
        # layout_1.setSpacing(10)
        self.groupbox_1.setLayout(layout_1)


    def setbox_3(self):
        # 容器3
        self.groupbox_3 = QGroupBox()
        font = QFont()
        font.setPointSize(23)
        self.groupbox_3.setFont(font)



        # 初始化网格布局
        self.VLayout_3 = QGridLayout(self.groupbox_3)

        # 创建LED列表
        self.leds = []

        # 获取配置中的类别数量
        num_classes = len(config.train_class)

        # 创建LED和标签
        for i in range(num_classes):
            name = config.train_class[i]
            ledSingle = MyLed(self.groupbox_3)
            ledSingle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.leds.append(ledSingle)

            label_led = QLabel(name)
            label_led.setStyleSheet("color:black;border: 0px;")
            label_led.setFont(QFont())
            label_led.setWordWrap(True)
            label_led.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            # 将控件放入布局中
            self.VLayout_3.addWidget(label_led, 1, i + 1)
            self.VLayout_3.addWidget(ledSingle, 0, i + 1)

        # 创建分隔线
        separator = QFrame(self.groupbox_3)
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        # 添加分隔线列
        self.VLayout_3.addWidget(separator, 0, num_classes + 1, 2, 1)

        # 创建连接状态LED和标签
        self.led_join = MyLed(self.groupbox_3,allDefaultVal=[QColor(240, 0, 0), QColor(160, 0, 0), QColor(68, 0, 0), QColor(28, 0, 0),
                          QColor(140, 140, 140), QColor(100, 100, 100),
                          500, 450, 400])
        self.led_join.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_led_join = QLabel("当前无任务")
        self.label_led_join.setStyleSheet("color:black;border: 0px;")
        self.label_led_join.setFont(QFont())
        self.label_led_join.setWordWrap(True)
        self.label_led_join.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # 将控件放入布局中
        self.VLayout_3.addWidget(self.label_led_join, 1, num_classes + 2)
        self.VLayout_3.addWidget(self.led_join, 0, num_classes + 2)

        # 设置布局
        self.groupbox_3.setLayout(self.VLayout_3)

    def setbox_2(self):
        # 容器2
        self.groupbox_2 = QGroupBox('自动诊断')

        # 创建垂直布局并应用到groupbox
        self.VLayout_2 = QHBoxLayout(self.groupbox_2)
        self.VLayout_2.setContentsMargins(0, 0, 0, 0)
        self.VLayout_2.setSpacing(10)
        self.VLayout_2.setAlignment(Qt.AlignCenter)  # 设置垂直居中

        # 创建自动诊断按钮
        self.btn_toggle = QPushButton('自动诊断')
        self.btn_toggle.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # self.btn_toggle.setMaximumSize(self.groupbox_2.width(), 100)
        self.btn_toggle.setFont(QFont("Arial", 12))
        btn_css(self.btn_toggle)
        self.btn_toggle.clicked.connect(self.toggle_button)

        # 创建水平布局用于输入框和标签
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(10)

        # 创建输入框和标签
        self.label_interval = QLabel('采集时间间隔 (秒):')
        self.label_interval.setFont(QFont("Arial", 12))

        # 设置输入框验证器
        self.input_interval = QLineEdit()
        self.input_interval.setPlaceholderText('请输入时间间隔')
        self.input_interval.setFixedWidth(self.btn_toggle.width())
        self.input_interval.setText('3')  # 默认值设为3秒

        # 设置控件宽度
        self.btn_toggle.setFixedWidth(150)  # 假设宽度为150
        self.input_interval.setFixedWidth(150)


        # 将控件添加到水平布局中
        h_layout.addWidget(self.label_interval)
        h_layout.addWidget(self.input_interval)


        # 创建一个中央部件，用来容纳水平布局，并设置它的对齐方式为居中
        central_widget = QWidget()
        central_widget.setLayout(h_layout)

        # 创建一个新的水平布局，用于放置 `btn_toggle`, `btn_train` 和 `btn_manual`
        btn_h_layout = QHBoxLayout()
        btn_h_layout.setContentsMargins(0, 0, 0, 0)
        btn_h_layout.setSpacing(10)
        btn_h_layout.addWidget(self.btn_toggle)

        # 创建一个中央部件，用来容纳新的水平布局
        btn_central_widget = QWidget()
        btn_central_widget.setLayout(btn_h_layout)

        # 将控件添加到垂直布局中
        self.VLayout_2.addWidget(central_widget, alignment=Qt.AlignCenter)
        self.VLayout_2.addWidget(btn_central_widget)

        # 设置布局
        self.groupbox_2.setLayout(self.VLayout_2)

    def setbox_4(self):
        # 容器4
        self.groupbox_4 = QGroupBox('手动诊断')

        # 创建垂直布局并应用到groupbox
        self.VLayout_4 = QVBoxLayout(self.groupbox_4)
        self.VLayout_4.setContentsMargins(0, 0, 0, 0)
        self.VLayout_4.setSpacing(10)
        self.VLayout_4.setAlignment(Qt.AlignCenter)  # 设置垂直居中

        # 创建水平布局用于输入框和标签
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(10)

        # 创建输入框和标签
        self.label_predictions = QLabel('预测次数:')
        self.label_predictions.setFont(QFont("Arial", 12))

        # 设置输入框验证器
        self.input_predictions = QSpinBox()
        self.input_predictions.setRange(1, 100)  # 设置数值范围
        self.input_predictions.setValue(5)  # 设置默认值
        self.input_predictions.setSingleStep(1)  # 设置步长
        # self.input_predictions.setFixedWidth(100)  # 设置固定宽度

        # 创建输入框和标签
        self.label_interval = QLabel('采集时间间隔 (秒):')
        self.label_interval.setFont(QFont("Arial", 12))

        # 创建新输入框
        self.input_interval_4 = QLineEdit()
        self.input_interval_4.setPlaceholderText('请输入采集时间间隔（秒）')
        # self.input_interval_4.setFixedWidth(100)  # 设置固定宽度
        self.input_interval_4.setText('0')  # 默认值设为5秒

        # 控件添加到水平布局中
        h_layout.addWidget(self.label_interval)
        h_layout.addWidget(self.input_interval_4)
        h_layout.addWidget(self.label_predictions)
        h_layout.addWidget(self.input_predictions)

        # 创建一个中央部件，用来容纳水平布局，并设置它的对齐方式为居中
        central_widget = QWidget()
        central_widget.setLayout(h_layout)

        # 创建手动诊断按钮
        self.btn_manual = QPushButton('手动诊断')
        self.btn_manual.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # self.btn_manual.setMaximumSize(self.groupbox_4.width(), 100)
        self.btn_manual.setFont(QFont("Arial", 12))
        btn_css(self.btn_manual)
        self.btn_manual.clicked.connect(self.manual_diagnosis)

        # 设置控件宽度
        self.input_interval_4.setFixedWidth(150)
        self.input_predictions.setFixedWidth(150)

        # 创建一个新的水平布局，用于放置 `btn_manual` 和 `btn_load_model`
        btn_h_layout = QHBoxLayout()
        btn_h_layout.setContentsMargins(0, 0, 0, 0)
        btn_h_layout.setSpacing(10)
        btn_h_layout.addWidget(self.btn_manual)

        # 创建一个中央部件，用来容纳新的水平布局
        btn_central_widget = QWidget()
        btn_central_widget.setLayout(btn_h_layout)

        # 将控件添加到垂直布局中
        self.VLayout_4.addWidget(central_widget, alignment=Qt.AlignCenter)
        self.VLayout_4.addWidget(btn_central_widget)

        # 设置布局
        self.groupbox_4.setLayout(self.VLayout_4)

    def setbox_5(self):
        # 容器5
        self.groupbox_5 = QGroupBox()

        # 创建垂直布局并应用到groupbox
        self.VLayout_5 = QHBoxLayout(self.groupbox_5)
        self.VLayout_5.setContentsMargins(0, 0, 0, 0)
        self.VLayout_5.setSpacing(10)
        self.VLayout_5.setAlignment(Qt.AlignCenter)  # 设置垂直居中

        # 创建模型训练按钮
        self.btn_train = QPushButton('训练模型')
        self.btn_train.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_train.setFont(QFont("Arial", 12))
        btn_css(self.btn_train)
        self.btn_train.clicked.connect(self.train_models)

        # 创建加载模型按钮
        self.btn_load_model = QPushButton('加载模型')
        self.btn_load_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # self.btn_load_model.setMaximumSize(self.groupbox_4.width(), 100)
        self.btn_load_model.setFont(QFont("Arial", 12))
        btn_css(self.btn_load_model)
        self.btn_load_model.clicked.connect(self.load_models)

        # 创建数据重置按钮
        self.btn_reset = QPushButton('重置数据')
        self.btn_reset.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_reset.setFont(QFont("Arial", 12))
        btn_css(self.btn_reset)
        self.btn_reset.clicked.connect(self.reset_data)

        # 设置控件宽度
        self.btn_train.setFixedWidth(150)
        self.btn_load_model.setFixedWidth(150)
        self.btn_reset.setFixedWidth(150)

        # 将按钮添加到垂直布局中
        self.VLayout_5.addWidget(self.btn_train, alignment=Qt.AlignCenter)
        self.VLayout_5.addWidget(self.btn_load_model, alignment=Qt.AlignCenter)
        self.VLayout_5.addWidget(self.btn_reset, alignment=Qt.AlignCenter)

        # 设置布局
        self.groupbox_5.setLayout(self.VLayout_5)

    def setbox_6(self):
        # 容器6
        self.groupbox_6 = QGroupBox('算法选择')
        self.groupbox_6.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_6.setFont(font)

        # 将控件填入布局中
        self.VLayout_6 = QHBoxLayout(self)
        self.VLayout_6.setContentsMargins(0, 0, 0, 0)
        self.VLayout_6.setSpacing(0)

        # 按钮组
        self.btn_group = QButtonGroup()
        btn_size = 30

        # 模型名称列表
        self.model_names = ["逻辑回归", "支持向量机", "感知机", "K近邻算法", "随机森林", "决策树"]

        # 初始化复选框
        self.btns = []
        for name in self.model_names:
            btn = QCheckBox(name)
            btn.setChecked(True)  # 默认选中
            btn.setMinimumSize(100, btn_size)
            btn.setFont(font)
            btn.setStyleSheet(
                "QCheckBox::indicator{\n"
                "width: 20px;\n"
                "height: 20px;\n"
                "}"
                "QCheckBox:enabled:checked{\n"
                "color: red;\n"
                "}"
                "QCheckBox:enabled:hover{\n"
                "color: rgb(0, 200, 0);\n"
                "}"
            )
            # self.btn_group.addButton(btn)
            self.btns.append(btn)
            self.VLayout_6.addWidget(btn)

        self.groupbox_6.setLayout(self.VLayout_6)

    def usetimefun(self):
        """窜口赋权"""
        try:
            os.system(f'echo "123456" | sudo -S chmod -R 777 {main()}')
        except Exception as e:
            raise Exception("串口权限设置失败，请检查串口连接是否正常")
        # os.system(f'stty -F {main()} ispeed 9600 ospeed 9600 cs8')
    def manual_diagnosis(self):
        """手动诊断"""
        try:
            # 系统运行其他的线程时，不能再运行
            if self.is_toggled:
                QMessageBox.critical(self, "错误", self.label_led_join.text())
                return

            self.is_toggled = '手动'
            self.set_led_noChecked()
            self.set_label_led_join()

            self.reset_data()

            self.is_data_join = True
            self.dataTableThread.set_max_num(int(self.input_predictions.text()))
            self.dataTableThread.set_sleep_time(float(self.input_interval_4.text()))
            self.dataTableThread.start()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
            return False

    def toggle_button(self):
        """自动诊断"""
        try:
            # 系统运行其他的线程时，不能再运行
            if self.is_toggled and self.is_toggled != '自动':
                QMessageBox.critical(self, "错误", self.label_led_join.text())
                return

            self.reset_data()
            self.check_file_size(config.train_csv_path)
        except Exception as e:
            # 显示错误信息弹窗
            QMessageBox.critical(self, "错误", str(e))
        else:
            if self.is_toggled:
                self.is_data_join = False
                self.is_toggled = ''

                self.btn_toggle.setText('自动诊断')
                self.btn_toggle.setProperty('is_toggled', 'true')

            else:
                self.is_data_join = True
                self.is_toggled = '自动'
                self.set_led_noChecked()

                self.dataTableThread.set_max_num(1000)
                self.dataTableThread.set_sleep_time(float(self.input_interval.text()))
                self.dataTableThread.start()

                self.btn_toggle.setText('停止诊断')
                self.btn_toggle.setProperty('is_toggled', 'false')

            # 更新样式
            self.btn_toggle.style().unpolish(self.btn_toggle)
            self.btn_toggle.style().polish(self.btn_toggle)
            self.set_label_led_join()

    def set_label_led_join(self):
        if not self.is_toggled:
            self.label_led_join.setText("当前无任务")
            if self.led_join.isChecked():
                self.led_join.toggle()
        elif self.is_toggled == '自动':
            self.label_led_join.setText("自动诊断中")
            if not self.led_join.isChecked():
                self.led_join.toggle()
        elif self.is_toggled == '手动':
            self.label_led_join.setText("手动诊断中")
            if not self.led_join.isChecked():
                self.led_join.toggle()
        elif self.is_toggled == '训练':
            self.label_led_join.setText("模型训练中")
            if not self.led_join.isChecked():
                self.led_join.toggle()
        elif self.is_toggled == '加载':
            self.label_led_join.setText("模型加载中")
            if not self.led_join.isChecked():
                self.led_join.toggle()

    def set_led_noChecked(self):
        # 设置指示灯状态
        for i in range(len(self.leds)):
            if self.leds[i].isChecked():
                self.leds[i].toggle()

    def set_led(self,n):
        # 设置指示灯状态
        for i in range(len(self.leds)):
            if n == i:
                if not self.leds[i].isChecked():
                    self.leds[i].toggle()
            else:
                if self.leds[i].isChecked():
                    self.leds[i].toggle()
    def theard_finished(self):
        """线程完成"""
        if self.is_toggled == '自动':
            self.btn_toggle.setText('自动诊断')
            self.btn_toggle.setProperty('is_toggled', 'true')
            self.btn_toggle.style().unpolish(self.btn_toggle)
            self.btn_toggle.style().polish(self.btn_toggle)

        self.is_toggled = ''
        self.set_label_led_join()

    def load_models(self):
        # 系统运行其他的线程时，不能再运行
        if self.is_toggled:
            QMessageBox.critical(self, "错误", self.label_led_join.text())
            return

        self.is_toggled = '加载'
        self.set_label_led_join()

        self.parent.fualt_model.run()
        self.loadModelsThread.start()
        # self.dataTableThread.load_models()


    def reset_data(self):
        """数据重置"""
        self.dataTableThread.reset_data()
        self.label.setText('')
        self.init_table(self.table)

    def train_models(self):
        """训练模型"""
        try:
            # 系统运行其他的线程时，不能再运行
            if self.is_toggled:
                QMessageBox.critical(self, "错误", self.label_led_join.text())
                return

            self.is_toggled = '训练'
            self.set_label_led_join()

            self.check_file_size(config.train_csv_path)
            data_balance()

            self.parent.fualt_model.run()
            self.trainModelsThread.start()
            # self.parent.fualt_model.train_models()
            # # 显示成功消息
            # QMessageBox.information(self, "成功", "模型训练完成！")
        except Exception as e:
            # 显示错误信息弹窗
            QMessageBox.critical(self, "错误", f"模型训练失败: {str(e)}")


    def set_label_text(self,text):
        self.label.setText(text)

    def on_text_changed(self):
        """文本内容改变时让滚动区域自动滚动到最底部"""
        v_scroll_bar = self.scroll_area.verticalScrollBar()
        # 确保 UI 完全更新后再设置滚动条值
        QApplication.processEvents()
        v_scroll_bar.setValue(v_scroll_bar.maximum())


    def set_tabel_text(self, all_predict_count):
        """表格显示集成预测结果"""

        # 获取当前表格中的数据
        data = []  # 用于存储表格中的数据
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append(None)
            data.append(row_data)
        columns = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]
        index = [self.table.verticalHeaderItem(row).text() for row in range(self.table.rowCount())]
        old_data = pd.DataFrame(data, index=index, columns=columns)

        # 清空现有表格内容并设置颜色为白色
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = QTableWidgetItem('')
                color = QColor(255, 255, 255)  # 红色
                brush = QBrush(color)
                item.setForeground(brush)
                self.table.setItem(row, col, item)

        # 获取DataFrame的行和列
        rows = all_predict_count.columns.tolist()  # 行为列名
        cols = all_predict_count.index.tolist()  # 列为索引

        # 设置表格的行数和列数
        # self.table.setRowCount(len(rows))
        # self.table.setColumnCount(len(cols))

        # 填充表格内容并比较新旧数据
        for col_index, col_name in enumerate(index):
            for row_index, row_name in enumerate(columns):
                if row_name in rows:
                    new_value = all_predict_count.loc[col_name, row_name]  # 注意这里索引和列名的顺序
                else:
                    new_value = old_data.loc[col_name, row_name]
                old_value = old_data.loc[col_name, row_name]

                item = QTableWidgetItem(str(new_value))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                if int(new_value) > int(old_value):
                    color = QColor(255, 0, 0)  # 红色
                    brush = QBrush(color)
                    item.setForeground(brush)
                self.table.setItem( col_index,row_index, item)
        # # 选中最后一行
        # last_row_index = self.table.rowCount() - 1
        # self.table.selectRow(last_row_index)
        # self.table.viewport().update()
    def closeEvent(self, event):
        # 关闭窗口事件
        reply = setQMessageBox()
        if reply == QMessageBox.Yes:
            event.accept()
            QApplication.quit()
        else:
            event.ignore()

    def show_message(self, text):
        try:
            # 显示消息
            super().show_message(text)

            self.is_data_join = False
            self.btn_toggle.setText('自动诊断')
            self.btn_toggle.setProperty('is_toggled', 'true')
        except Exception as e:
            # 异常处理：记录日志或提示用户
            QMessageBox.critical(self, "错误", e)