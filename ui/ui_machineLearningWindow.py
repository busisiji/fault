import threading

import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QGroupBox, QHeaderView, \
    QButtonGroup, QRadioButton
from PyQt5.QtCore import Qt, QSize
from matplotlib import pyplot as plt

import config
from ui.others.ui_fun import MyFigure
from ui.Base.baseWindow import BaseWindow


class MachineLearningWindow(BaseWindow):
    '''机器学习窗口'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle('机器学习')
        self.setbox_1()
        self.setbox_2()
        # self.setbox_3()
        # self.setbox_4()
        self.mainVLayout = QVBoxLayout(self)
        # self.groupbox_1.setMaximumSize(QSize(self.width(), self.height() * 0.7))
        self.groupbox_2.setMinimumSize(QSize(self.width(), self.height() * 0.3))
        # self.mainVLayout.addWidget(self.groupbox_3)
        self.mainVLayout.addWidget(self.groupbox_1)
        self.mainVLayout.addWidget(self.groupbox_2)
        # self.mainVLayout.addWidget(self.groupbox_4)
        self.setLayout(self.mainVLayout)

    def setbox_1(self):
        # 容器1
        self.groupbox_1 = QGroupBox()
        self.groupbox_1.setTitle('机器学习统计')
        self.groupbox_1.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_1.setFont(font)
        self.groupbox_1.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_1 = QVBoxLayout(self)
        self.VLayout_1.setContentsMargins(0, 0, 0, 0)
        self.VLayout_1.setSpacing(0)

        self.table = QTableWidget(0,9)
        self.table.setHorizontalHeaderLabels(['预测结果',"Z轴振动速度", "X轴振动速度", "Z轴加速度峰值", "X轴加速度峰值", "Z轴峰值速度分量频率 Hz", "X轴峰值速度分量频率 Hz","Z轴加速度均方根","X轴加速度均方根"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 宽高自动分配
        # self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 行高自动分配
        font.setPointSize(18)
        self.table.setFont(font)
        font.setPointSize(14)
        self.table.horizontalHeader().setFont(font)
        self.table.verticalHeader().setFont(font)
        self.table.setStyleSheet("color:black;")
        threading.Thread(target=self.set_tabel_start).start()

        # 将控件放入布局中
        self.VLayout_1.addWidget(self.table)
        self.groupbox_1.setLayout(self.VLayout_1)

    def setbox_2(self):
        # 容器2
        self.groupbox_2 = QGroupBox()
        self.groupbox_2.setTitle('选择机器学习算法')
        self.groupbox_2.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_2.setFont(font)
        self.groupbox_2.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_2 = QHBoxLayout(self)
        self.VLayout_2.setContentsMargins(0, 0, 0, 0)
        self.VLayout_2.setSpacing(0)

        # 按钮组
        self.btn_group = QButtonGroup()
        btn_size = 30
        # 按钮1
        self.model_names = ["逻辑回归", "支持向量机", "感知机", "K近邻算法", "随机森林", "决策树"]
        self.btn_1 = QRadioButton()
        self.btn_1.clicked.connect(self.btn_fun_1)
        # self.btn_1.setMaximumSize(100, btn_size)
        self.btn_1.setMinimumSize(100, btn_size)

        # 按钮2
        self.btn_2 = QRadioButton()
        self.btn_2.clicked.connect(self.btn_fun_2)
        # self.btn_2.setMaximumSize(100, btn_size)
        self.btn_2.setMinimumSize(100, btn_size)

        # 按钮3
        self.btn_3 = QRadioButton()
        self.btn_3.clicked.connect(self.btn_fun_3)
        # self.btn_3.setMaximumSize(100, btn_size)
        self.btn_3.setMinimumSize(100, btn_size)

        # 按钮4
        self.btn_4 = QRadioButton()
        self.btn_4.clicked.connect(self.btn_fun_4)
        # self.btn_4.setMaximumSize(100, btn_size)
        self.btn_4.setMinimumSize(100, btn_size)

        # 按钮5
        self.btn_5 = QRadioButton()
        self.btn_5.clicked.connect(self.btn_fun_5)
        # self.btn_5.setMaximumSize(100, btn_size)
        self.btn_5.setMinimumSize(100, btn_size)

        # 按钮6
        self.btn_6 = QRadioButton()
        self.btn_6.clicked.connect(self.btn_fun_6)
        # self.btn_6.setMaximumSize(100, btn_size)
        self.btn_6.setMinimumSize(100, btn_size)

        self.btn_1.setText(self.model_names[0])
        self.btn_2.setText(self.model_names[1])
        self.btn_3.setText(self.model_names[2])
        self.btn_4.setText(self.model_names[3])
        self.btn_5.setText(self.model_names[4])
        self.btn_6.setText(self.model_names[5])
        self.btns = [self.btn_1, self.btn_2, self.btn_3, self.btn_4, self.btn_5, self.btn_6]
        for i in self.btns:
            font.setPointSize(23)
            i.setFont(font)
            # i.setStyleSheet("background-color:SkyBlue;color:black;")
            i.setStyleSheet(
                "QRadioButton::indicator{\n"
                "width: 20px;\n"
                "height: 20px;\n"
                "}"
                "QRadioButton:enabled:checked{\n"
                "color: red;\n"
                "}"
                "QRadioButton:enabled:hover{\n"
                "color: rgb(0, 200, 0);\n"
                "}"
            )
        self.btn_app()

        self.VLayout_2.addWidget(self.btn_1)
        self.VLayout_2.addWidget(self.btn_2)
        self.VLayout_2.addWidget(self.btn_3)
        self.VLayout_2.addWidget(self.btn_4)
        self.VLayout_2.addWidget(self.btn_5)
        self.VLayout_2.addWidget(self.btn_6)
        # self.VLayout_2.addWidget(self.btn_group)
        self.groupbox_2.setLayout(self.VLayout_2)

    def setbox_3(self):
        # 容器3
        self.groupbox_3 = QGroupBox()

        # 将控件填入布局中
        self.VLayout_3 = QVBoxLayout(self)
        self.VLayout_3.setContentsMargins(0, 0, 0, 0)
        self.VLayout_3.setSpacing(0)

        self.groupBox = QGroupBox()
        # self.plotother()
        self.F1 = MyFigure(width=100, height=100, dpi=100)
        self.F1.axes1 = self.F1.fig.add_subplot(335, projection='3d')

        # 将控件放入布局中
        self.VLayout_3.addWidget(self.F1)
        self.groupbox_3.setLayout(self.VLayout_3)

    def plotother(self, feature):
        # 3D图绘制
        for csv_path in config.train_csv_path:
            df = pd.read_csv(csv_path)
            self.F1.axes1.scatter(df[feature[0]].values, df[feature[1]].values, df[feature[2]].values)
        self.F1.axes1.set_xlabel(feature[0])
        self.F1.axes1.set_ylabel(feature[1])
        self.F1.axes1.set_zlabel(feature[2])
        # plt.legend(labels=folders)
        self.F1.draw()

    def center(self):
        '''窗口居中'''
        size = self.geometry()
        height = (config.screen.height() - size.height()) / 2
        width = (config.screen.width() - size.width()) / 2
        if height <= 50:
            height = 0
        if width <= 50:
            width = 0
        self.move(width, height)

    def set_led(self,n):
        # 设置指示灯状态
        for i in range(len(self.leds)):
            if n == i:
                if not self.leds[i].isChecked():
                    self.leds[i].toggle()
            else:
                if self.leds[i].isChecked():
                    self.leds[i].toggle()

    def set_tabel_start(self):
        data_save = [0]
        while data_save != window.datas:
            # lock.acquire()
            data_save = window.datas
            count_tabel = self.table.rowCount()
            if count_tabel < len(data_save):
                self.table.setRowCount(len(data_save))
                self.set_tabel_text(data_save,-1)
            # lock.release()
            data_save = [0]

    def set_tabel_row(self,n):
        # lock.acquire()
        data_save = window.datas
        count_tabel = self.table.rowCount()
        if count_tabel < len(data_save):
            self.table.setRowCount(len(data_save))
        # lock.release()
        # threading.Thread(target=self.set_tabel_text, args=(data_save,n)).start()
        self.set_tabel_text(data_save,n)
        # lock.release()

    def set_tabel_text(self, data_save,n):
        for i in range(len(data_save)):
            item = QTableWidgetItem('第' + str(i+1) + '条')
            self.table.setVerticalHeaderItem(i, item)
            if n != -1:
                model_dic = str(window.model_dics[i][self.model_names[n]])
                item = QTableWidgetItem(model_dic)
                # if model_dic == '正常':
                #     self.set_led(0)
                # elif model_dic == '电流过载':
                #     self.set_led(1)
                # elif model_dic == '离心':
                #     self.set_led(2)
                # elif model_dic == '螺丝松动':
                #     self.set_led(3)
            self.table.setItem(i, 0, item)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            for j in range(1,9):
                item = QTableWidgetItem(str(data_save[i][0][j-1]))
                self.table.setItem(i, j, item)
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.table.viewport().update()

    def btn_app(self):
        # 按钮组设置
        for i in self.btns:
            self.btn_group.addButton(i)

    def btn_fun_1(self):
        # self.btn_set(0)
        threading.Thread(target=self.set_tabel_row,args=(0,)).start()
        # self.set_tabel_row(0)

    def btn_fun_2(self):
        # self.btn_set(1)
        threading.Thread(target=self.set_tabel_row, args=(1,)).start()
        # self.set_tabel_row(1)

    def btn_fun_3(self):
        # self.btn_set(2)
        threading.Thread(target=self.set_tabel_row, args=(2,)).start()
        # self.set_tabel_row(2)

    def btn_fun_4(self):
        # self.btn_set(3)
        threading.Thread(target=self.set_tabel_row, args=(3,)).start()
        # self.set_tabel_row(3)

    def btn_fun_5(self):
        # self.btn_set(4)
        threading.Thread(target=self.set_tabel_row, args=(4,)).start()
        # self.set_tabel_row(4)

    def btn_fun_6(self):
        # self.btn_set(5)
        threading.Thread(target=self.set_tabel_row, args=(5,)).start()
        # self.set_tabel_row(5)

    def closeEvent(self,event):
        # 关闭窗口事件
        self.setAttribute(Qt.WA_AttributeCount)
        plt.close()