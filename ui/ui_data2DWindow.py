import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QSizePolicy, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt, QSize
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties

import config
from qss.qss import btn_css
from ui.others.ui_fun import MyFigure
from ui.Base.baseWindow import BaseWindow


class Data2DWindow(BaseWindow):
    '''2D数据图参数选择窗口'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle('2D数据图')

        self.setbox_1()
        self.setbox_2()
        self.setbox_3()
        self.groupbox_2.setMinimumSize(QSize(self.width(), self.height() * 0.7))
        self.mainVLayout = QVBoxLayout(self)
        self.mainVLayout.addWidget(self.groupbox_2)
        self.mainVLayout.addWidget(self.groupbox_1)
        self.mainVLayout.addWidget(self.groupbox_3)
        self.setLayout(self.mainVLayout)

    def setbox_1(self):
        # 容器1
        self.groupbox_1 = QGroupBox()
        self.groupbox_1.setTitle('选择xy轴参数')
        self.groupbox_1.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_1.setFont(font)
        self.groupbox_1.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_1 = QVBoxLayout(self)
        self.VLayout_1_1 = QHBoxLayout()
        self.VLayout_1_2 = QHBoxLayout()
        self.btn_1 = QCheckBox()
        self.btn_2 = QCheckBox()
        self.btn_3 = QCheckBox()
        self.btn_4 = QCheckBox()
        self.btn_5 = QCheckBox()
        self.btn_6 = QCheckBox()
        self.btn_7 = QCheckBox()
        self.btn_8 = QCheckBox()
        self.btns = [self.btn_1, self.btn_2, self.btn_3, self.btn_4, self.btn_5, self.btn_6, self.btn_7, self.btn_8]
        for i in range(0, 8):
            if i % 2:
                self.set_btn(self.btns[i], self.VLayout_1_2)
            else:
                self.set_btn(self.btns[i], self.VLayout_1_1)
            self.btns[i].setStyleSheet("color: red;")
            font.setPointSize(23)
            self.btns[i].setFont(font)
            self.btns[i].setStyleSheet(
                "QCheckBox::indicator{"
                "width: 20px;"
                "height: 20px;"
                "}"
                "QCheckBox:enabled:checked{"
                "color: red;"
                "}"
                "QCheckBox:enabled:hover{"
                "color: rgb(0, 200, 0);"
                "}"
            )
        self.btn_1.setText('Z 轴振动速度')
        self.btn_2.setText('X 轴振动速度')
        self.btn_3.setText('Z 轴加速度峰值')
        self.btn_4.setText('X 轴加速度峰值')
        self.btn_5.setText('Z 轴峰值速度分量频率 Hz')
        self.btn_6.setText('X 轴峰值速度分量频率 Hz')
        self.btn_7.setText('Z 轴加速度均方根')
        self.btn_8.setText('X 轴加速度均方根')

        self.VLayout_1.addLayout(self.VLayout_1_1)
        self.VLayout_1.addLayout(self.VLayout_1_2)
        self.groupbox_1.setLayout(self.VLayout_1)

    def setbox_2(self):
        # 容器2
        self.groupbox_2 = QGroupBox()

        # 将控件填入布局中
        self.VLayout_2 = QVBoxLayout(self)
        self.VLayout_2.setContentsMargins(0, 0, 0, 0)
        self.VLayout_2.setSpacing(0)

        self.fig = MyFigure(width=100, height=100, dpi=100)


        self.VLayout_2.addWidget(self.fig )
        self.groupbox_2.setLayout(self.VLayout_2)

    def setbox_3(self):
        # 容器3
        self.groupbox_3 = QGroupBox()
        self.groupbox_3.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_3 = QHBoxLayout(self)
        self.VLayout_3.setContentsMargins(0, 0, 0, 0)
        self.VLayout_3.setSpacing(0)

        self.btn_show = QPushButton()

        # 设置按钮的大小策略
        self.btn_show.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.btn_show.setMaximumSize(self.groupbox_2.width(), 100)
        self.btn_show.setText('2D数据图')
        font = QFont()
        font.setPointSize(23)
        self.btn_show.setFont(font)
        btn_css(self.btn_show)
        self.btn_show.clicked.connect(self.btn_fun)

        # 将控件放入布局中
        self.VLayout_3.addWidget(self.btn_show)
        self.groupbox_3.setLayout(self.VLayout_3)

    def plotother(self, features):
        # 2D图绘制
        self.fig.axes.clear()
        for path in config.train_csv_path:
            df = pd.read_csv(path)
            self.fig.axes.scatter(df[features[0]].values, df[features[1]].values)
        font = FontProperties(fname=config.ttf_SsimHei)  # 指定字体文件路径
        self.fig.axes.set_xlabel(features[0], fontproperties=font)
        self.fig.axes.set_ylabel(features[1], fontproperties=font)
        self.fig.axes.legend(labels=config.train_csv, prop=font)
        self.fig.draw()

    def set_btn(self, btn, VLayout):
        btn.setChecked(False)
        btn.toggled.connect(self.buttonState)
        VLayout.addWidget(btn)

    def btn_fun(self):
        # 按钮事件
        num_btn = 0
        btn_texts = []
        for i in self.btns:
            if i.isChecked() == True:
                num_btn += 1
                btn_texts.append(i.text())
        if num_btn == 2:
            self.plotother(btn_texts)
        else:
            # 弹窗
            msg_box = QMessageBox(QMessageBox.Information, '警告', '请选择2个参数！')
            msg_box.exec_()

    def buttonState(self):
        radioButton = self.sender()
        if radioButton.isChecked() == True:
            print('<' + radioButton.text() + '> 被选中')
        else:
            print('<' + radioButton.text() + '> 被取消选中状态')

    def closeEvent(self, event):
        # 关闭窗口事件
        self.setAttribute(Qt.WA_DeleteOnClose)
        plt.close()
