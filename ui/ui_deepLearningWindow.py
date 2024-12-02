import os
import threading

import pandas as pd
from PyQt5.QtGui import QFont, QIcon, QMovie
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox, QCheckBox, \
    QHeaderView, QStackedLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.uic.properties import QtCore

import config
from lib.sequential_model import get_result, start
from ui.others.ui_fun import MyFigure
from ui.Base.baseWindow import BaseWindow


class DeepLearningWindow(BaseWindow):
    '''深度学习窗口'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # data_balance()
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle('深度学习')

        self.setbox_1()
        self.setbox_2()
        self.setbox_3()
        self.setbox_4()
        self.groupbox2_1.setMinimumSize(QSize(self.width(), self.height() * 0.4))
        self.groupbox_1.setMinimumSize(QSize(self.width(), self.height() * 0.4))
        self.groupbox_3.setMinimumSize(QSize(self.width(), self.height() * 0.2))
        self.mainVLayout = QVBoxLayout(self)
        self.mainVLayout.addWidget(self.groupbox_1)
        self.mainVLayout.addWidget(self.groupbox2_1)
        # self.mainVLayout.addWidget(self.groupbox_4)
        self.mainVLayout.addWidget(self.groupbox_3)
        self.setLayout(self.mainVLayout)

    def setbox_1(self):
        # 容器1
        self.groupbox_1 = QGroupBox()
        self.groupbox_1.setTitle('深度学习统计')
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
        self.table.setHorizontalHeaderLabels(['预测结果',"Z 轴振动速度", "X 轴振动速度", "Z 轴加速度峰值", "X 轴加速度峰值", "Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz","Z 轴加速度均方根","X 轴加速度均方根"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

    def setbox_3(self):
        # 容器3
        self.groupbox_3 = QGroupBox()
        self.groupbox_3.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_3 = QHBoxLayout(self)
        # self.VLayout_3.setContentsMargins(0, 0, 0, 0)
        # self.VLayout_3.setSpacing(0)

        btn_size = 30
        font =QFont()
        self.btn3_1 = QPushButton()
        self.btn3_1.setMinimumSize(100, btn_size)
        self.btn3_1.clicked.connect(self.btn_fun_1)
        self.btn3_1.setText('训练模型')
        self.btn3_3 = QPushButton()
        self.btn3_3.setMinimumSize(100, btn_size)
        self.btn3_3.setText('采集数据')
        for i in [self.btn3_1,self.btn3_3]:
            i.setStyleSheet("background-color:SkyBlue;color:black;")
            font.setPointSize(23)
            i.setFont(font)

        # 将控件放入布局中
        self.VLayout_3.addWidget(self.btn3_3)
        self.VLayout_3.addWidget(self.btn3_1)
        self.groupbox_3.setLayout(self.VLayout_3)

    def setbox_2(self):
        self.groupbox2_1 = QGroupBox()
        # 容器2
        self.groupbox_2 = QGroupBox()
        self.groupbox_2.setTitle('模型训练历史')
        self.groupbox_2.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_2.setFont(font)
        self.groupbox_2.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_2 = QStackedLayout(self)
        # self.VLayout_2.setContentsMargins(0, 0, 0, 0)
        # self.VLayout_2.setSpacing(0)
        self.F1 = MyFigure(width=100, height=100, dpi=100)
        # 插入标签
        self.label_gif = QLabel()
        self.label_gif.setGeometry(QtCore.QRect((self.groupbox_2.width()-self.groupbox_2.height())/2,0,self.groupbox_2.width(),self.groupbox_2.height()))
        # 设置GIF图片源
        self.gif = QMovie("icons/test.gif")
        # 设置GIF位置以及大小---和label一致
        self.gif.setScaledSize(self.label_gif.size())
        # 使用label加载GIF
        self.label_gif.setMovie(self.gif)
        # 播放GIF
        self.gif.start()
        # self.label_gif.hide()

        # 将控件放入布局中
        self.VLayout_2.addWidget(self.F1)
        self.VLayout_2.addWidget(self.label_gif)
        self.groupbox_2.setLayout(self.VLayout_2)

    def setbox_4(self):
        # 容器4
        self.groupbox_4 = QGroupBox()
        self.groupbox_4.setTitle('选择模型参数')
        self.groupbox_4.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_4.setFont(font)
        self.groupbox_4.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_4 = QHBoxLayout(self)
        self.VLayout_4_1 = QVBoxLayout(self)
        self.VLayout_4_2 = QVBoxLayout(self)
        self.btn_1 = QCheckBox()
        self.btn_2 = QCheckBox()
        self.btn_3 = QCheckBox()
        self.btn_4 = QCheckBox()
        self.btn_5 = QCheckBox()
        self.btn_6 = QCheckBox()
        self.btn_7 = QCheckBox()
        self.btn_8 = QCheckBox()
        self.btns = [self.btn_1, self.btn_2, self.btn_3, self.btn_4, self.btn_5, self.btn_6, self.btn_7, self.btn_8]
        for i in range(0,8):
            if i % 2:
                self.set_btn(self.btns[i],self.VLayout_4_2)
            else:
                self.set_btn(self.btns[i], self.VLayout_4_1)
            self.btns[i].setStyleSheet("color: red;")
            font.setPointSize(18)
            self.btns[i].setFont(font)
            # self.btns[i].setStyleSheet("color:black;")
            self.btns[i].setStyleSheet(
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
        self.btn_1.setText('Z 轴振动速度')
        self.btn_2.setText('X 轴振动速度')
        self.btn_3.setText('Z 轴加速度峰值')
        self.btn_4.setText('X 轴加速度峰值')
        self.btn_5.setText('Z 轴峰值速度分量频率 Hz')
        self.btn_6.setText('X 轴峰值速度分量频率 Hz')
        self.btn_7.setText('Z 轴加速度均方根')
        self.btn_8.setText('X 轴加速度均方根')

        self.VLayout_4.addLayout(self.VLayout_4_1)
        self.VLayout_4.addLayout(self.VLayout_4_2)
        self.groupbox_4.setLayout(self.VLayout_4)

        self.mainVLayout_1 = QHBoxLayout(self)
        self.mainVLayout_1.addWidget(self.groupbox_4)
        self.mainVLayout_1.addWidget(self.groupbox_2)
        self.groupbox2_1.setLayout(self.mainVLayout_1)

    def plot_(self):
        self.F1.axes1 = self.F1.fig.add_subplot()
        hist = pd.DataFrame(self.history.history)
        hist['epoch'] = self.history.epoch
        # self.F1.fig.clf()
        self.F1.axes1.set_xlabel('Epoch')
        self.F1.axes1.set_ylabel('Model Train')
        self.F1.axes1.plot(hist['loss'],
                 label='loss')
        self.F1.axes1.plot(hist['accuracy'],
                 label='accuracy')
        self.F1.axes1.set_xlim(0, 50)
        self.F1.axes1.set_ylim(0, 1)
        self.F1.axes1.legend()
        self.F1.draw() # 刷新
        # plt.close()

    def set_tabel_start(self):
        # 设置表格行列数
        data_save = [0]
        while data_save != window.datas:
            # lock.acquire()
            data_save = window.datas
            count_tabel = self.table.rowCount()
            if count_tabel < len(data_save):
                self.table.setRowCount(len(data_save))
                self.set_tabel_text(data_save)
            data_save = [0]
            # lock.release()

    def set_tabel_text(self, data_save):
        # 设置表格内容
        for i in range(len(data_save)):
            item = QTableWidgetItem('第' + str(i+1) + '条')
            self.table.setVerticalHeaderItem(i, item)
            model_dic = str(get_result(data_save[i][0],self.model))
            item = QTableWidgetItem(model_dic)
            self.table.setItem(i, 0, item)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            for j in range(1,9):
                item = QTableWidgetItem(str(data_save[i][0][j-1]))
                self.table.setItem(i, j, item)
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.table.viewport().update()

    def set_btn(self,btn,VLayout):
        btn.setChecked(False)
        btn.toggled.connect(self.buttonState)
        VLayout.addWidget(btn)

    def btn_fun_1(self):
        # 按钮事件,加载动画替换控件
        # self.setWindowModality(Qt.ApplicationModal)  # 设置主窗口不可操作
        # self.setWindowModality(Qt.NonModal)  # 恢复正常模式
        num_btn = 0
        btn_texts = []
        for i in self.btns:
            if i.isChecked() == True:
                num_btn += 1
                btn_texts.append(i.text())
        if num_btn == 2:
            # show_data3D(btn_texts)
            self.VLayout_2.setCurrentIndex(1)
            # self.btn_train(btn_texts)
            threading.Thread(target=self.btn_train,args=(btn_texts,)).start()
        else:
            # 弹窗
            msg_box = QMessageBox(QMessageBox.Information, '警告', '请选择2个参数！')
            msg_box.setWindowIcon(QIcon(os.path.join(config.ROOT_DIR, 'icons', '1.ico')))
            msg_box.exec_()

    def start_train(self,btn_texts = ["Z 轴振动速度", "X 轴振动速度"]):
        # self.setWindowModality(Qt.ApplicationModal)  # 设置主窗口不可操作
        self.model, self.history = start(btn_texts = btn_texts)
        # self.setWindowModality(Qt.NonModal)  # 恢复正常模式
        self.VLayout_2.setCurrentIndex(0)
        self.F1.fig.clf()
        self.plot_()

    def btn_train(self,btn_texts):
        # self.gif.start()
        data_balance()
        mythreading = threading.Thread(target=self.start_train, args=(btn_texts,))
        mythreading.start()
        mythreading.join()

    def buttonState(self):
        radioButton = self.sender()
        if radioButton.isChecked() == True:
            print('<' + radioButton.text() + '> 被选中')
        else:
            print('<' + radioButton.text() + '> 被取消选中状态')

    def closeEvent(self,event):
        # 关闭窗口事件
        self.setAttribute(Qt.WA_AttributeCount)
        # plt.close()
