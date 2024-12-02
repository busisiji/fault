import csv
import os
import threading

import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QGroupBox, QSizePolicy, QMessageBox, QHeaderView, QComboBox, QAbstractItemView
from PyQt5.QtCore import Qt, QSize
from matplotlib import pyplot as plt

import config
from qss.qss import btn_css
from ui.Base.baseWindow import BaseWindow
from utils.collect import get_new_data
from utils.mongo import start_draw_final


class DataCollectionWindow(BaseWindow):

    '''采集数据窗口'''
    def __init__(self, parent=None,menuIndex=1):
        super().__init__(parent)

        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle('采集数据')
        self.menuIndex = menuIndex
        self.flag = 0
        self.fig = 0
        self.exit = 0

        self.setbox_1()
        # self.setbox_5()
        self.setbox_3()
        self.setbox_4()
        self.mainVLayout = QVBoxLayout(self)
        self.groupbox_1.setMinimumSize(QSize(self.width(), self.height() * 0.4))
        self.groupbox_4.setMinimumSize(QSize(self.width(), self.height() * 0.3))
        self.groupbox_3.setMinimumSize(QSize(self.width(), self.height() * 0.3))
        self.mainVLayout.addWidget(self.groupbox_1)
        # self.mainVLayout.addWidget(self.groupbox_5)
        self.mainVLayout.addWidget(self.groupbox_4)
        self.mainVLayout.addWidget(self.groupbox_3)
        self.setLayout(self.mainVLayout)

    def setbox_1(self):
        # 容器1
        self.groupbox_1 = QGroupBox()
        self.groupbox_1.setTitle('统计采集数据')
        self.groupbox_1.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_1.setFont(font)
        self.groupbox_1.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_1 = QVBoxLayout(self)
        self.VLayout_1.setContentsMargins(0, 0, 0, 0)
        self.VLayout_1.setSpacing(0)

        self.table = QTableWidget()
        # 设置水平滚动条策略
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setColumnCount(len(config.get_feature_default(self.menuIndex))+1) # 表格列数
        self.table.setHorizontalHeaderLabels( config.get_feature_default(self.menuIndex)+["操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 宽高自动分配
        # self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 行高自动分配
        # 固定最后一列的宽度固定
        self.table.horizontalHeader().setSectionResizeMode(self.table.columnCount() - 1, QHeaderView.Fixed)

        font.setPointSize(18)
        self.table.setFont(font)
        font.setPointSize(14)
        self.table.horizontalHeader().setFont(font)
        self.table.verticalHeader().setFont(font)
        self.table.setStyleSheet("color:black;")
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许表格根据内容扩展
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 当需要时显示垂直滚动条

        self.table.setStyleSheet(self.table_style )

        # 禁止编辑
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 禁止选择单元格
        self.table.setSelectionMode(QAbstractItemView.NoSelection)

        # 将控件放入布局中
        self.VLayout_1.addWidget(self.table)
        self.groupbox_1.setLayout(self.VLayout_1)

    def setbox_2(self):
        # 容器2
        self.groupbox_2 = QGroupBox()

        # 将控件填入布局中
        self.VLayout_2 = QHBoxLayout(self)
        self.VLayout_2.setContentsMargins(0, 0, 0, 0)
        self.VLayout_2.setSpacing(0)

        # self.cb.set
        self.label_1 = QLabel()
        self.label_1.setText('选择要采集的数据范围为')
        self.label_1.setWordWrap(True)
        self.label_1.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label_1.setFont(QFont('Mcorsoft YaHei', 11, 30))
        self.label_1.setStyleSheet("color:rgb(130,130,130); padding:10px;")
        # self.label_1.setMinimumSize(QSize(self.groupbox_2.width()*0.2, self.groupbox_2.height() ))
        self.cb_2 = QComboBox(maximumWidth=100)
        # self.cb_2.setMaxVisibleItems(3)
        self.label_2 = QLabel()
        self.label_2.setText('到')
        self.label_2.setWordWrap(True)
        self.label_2.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label_2.setFont(QFont('Mcorsoft YaHei', 11, 30))
        self.label_2.setStyleSheet("color:rgb(130,130,130); padding:10px;")
        self.cb_3 = QComboBox(maximumWidth=100)
        # self.cb_3.setMaxVisibleItems(3)
        self.cb2_text()
        self.cb3_text()
        # 信号
        self.cb_2.highlighted[int].connect(self.cb2_text)  # 在下拉列表中，鼠标移动到某个条目时发出信号，传递条目索引
        self.cb_2.currentIndexChanged[str].connect(self.set_tabel_row)  # 条目发生改变，发射信号，传递条目索引
        self.cb_3.currentIndexChanged[str].connect(self.set_tabel_row)  # 条目发生改变，发射信号，传递条目索引
        self.cb_3.highlighted[int].connect(self.cb3_text)  # 在下拉列表中，鼠标移动到某个条目时发出信号，传递条目索引

        # 将控件放入布局中
        # self.VLayout_2.addWidget(self.cb)
        self.VLayout_2.addWidget(self.label_1)
        self.VLayout_2.addWidget(self.cb_2)
        self.VLayout_2.addWidget(self.label_2)
        self.VLayout_2.addWidget(self.cb_3)

        self.groupbox_2.setLayout(self.VLayout_2)

    def setbox_3(self):

        # 设置容器3
        self.groupbox_3 = QGroupBox()
        self.groupbox_3.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_3 = QHBoxLayout(self)
        # self.VLayout_3.setContentsMargins(0, 0, 0, 0)
        # self.VLayout_3.setSpacing(0)

        self.btn_show = QPushButton()
        btn_size = 30
        # self.btn_show.setMinimumSize(100, btn_size)
        self.btn_show.setText('采集数据')
        self.btn_show.clicked.connect(self.collect_data)

        self.btn_view = QPushButton()
        self.btn_view.setText('数据写入')
        self.btn_view.clicked.connect(self.save_data)

        self.btn_del = QPushButton()
        self.btn_del.setText('清空表格')
        self.btn_del.clicked.connect(self.clear_table)

        self.btn_load = QPushButton()
        self.btn_load.setText('数据读取')
        self.btn_load.clicked.connect(self.load_data)

        btn_css(self.btn_show)
        btn_css(self.btn_view)
        btn_css(self.btn_del)
        btn_css(self.btn_load)


        # 将控件放入布局中
        self.VLayout_3.addWidget(self.btn_show)
        self.VLayout_3.addWidget(self.btn_view)
        self.VLayout_3.addWidget(self.btn_load)
        self.VLayout_3.addWidget(self.btn_del)
        self.groupbox_3.setLayout(self.VLayout_3)

    def setbox_4(self):
        # 容器4
        self.groupbox_4 = QGroupBox()
        self.groupbox_4.setTitle('保存采集数据')
        self.groupbox_4.setAlignment(Qt.AlignHCenter)  # 标题居中
        font =QFont()
        font.setPointSize(23)
        self.groupbox_4.setFont(font)
        self.groupbox_4.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        self.VLayout_4 = QHBoxLayout()
        # self.VLayout_4.setContentsMargins(0, 0, 0, 0)
        # self.VLayout_4.setSpacing(0)

        self.label_4 = QLabel()
        self.label_4.setText('选择要采集的数据类型为')
        self.label_4.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 文本居中
        self.cb_4 = QComboBox(maximumWidth=300)
        self.cb_4.addItems(config.train_class)
        self.label_4.setMaximumSize(self.groupbox_4.width() * 0.7, self.groupbox_4.height())
        self.label_4.setMinimumSize(self.groupbox_4.width() * 0.1, 100)

        # 将控件放入布局中
        self.VLayout_4.addWidget(self.label_4)
        self.VLayout_4.addWidget(self.cb_4)
        # self.VLayout_4.addWidget(self.cb_5)
        # self.groupbox_4.setLayout(self.VLayout_4)
    # def setbox_5(self):
    #     # 容器5
    #     self.groupbox_5 = QGroupBox()

        # 将控件填入布局中
        self.VLayout_5 = QHBoxLayout()
        # self.VLayout_5.setContentsMargins(0, 0, 0, 0)
        # self.VLayout_5.setSpacing(0)

        self.label_5 = QLabel()
        self.label_5.setText('选择保存数据的方式为')
        self.label_5.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 文本居中
        self.label_5.setMaximumSize(self.groupbox_4.width()*0.7,self.groupbox_4.height())
        self.label_5.setMinimumSize(self.groupbox_4.width() * 0.5, 100)
        self.cb_5 = QComboBox(maximumWidth=300)
        self.cb_5.addItems(['覆盖','追加'])
        for i in [self.label_4,self.label_5,self.cb_4,self.cb_5]:
            font.setPointSize(23)
            i.setFont(font)
            i.setStyleSheet("color:black;")

        # 将控件放入布局中
        self.VLayout_5.addWidget(self.label_5)
        self.VLayout_5.addWidget(self.cb_5)
        self.mainVLayout_4 = QVBoxLayout()
        self.mainVLayout_4.addLayout(self.VLayout_4)
        self.mainVLayout_4.addLayout(self.VLayout_5)
        self.groupbox_4.setLayout(self.mainVLayout_4)

    def add_delete_button(self,rowCount):
        delete_button = QPushButton("删除")
        btn_css(delete_button)
        delete_button.clicked.connect(lambda _, button=delete_button: self.delete_row(button))
        self.table.setCellWidget(rowCount, self.table.columnCount() - 1, delete_button)

    def load_data(self):
        """从 CSV 文件读取数据并写入表格"""
        try:
            data_path = self.cb_4.currentText()
            file_path = os.path.join(config.train_path, data_path + '.csv')

            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)

                # 跳过表头行
                next(reader)

                # 清空现有数据
                self.table.setRowCount(0)

                for row_data in reader:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)

                    for col_number, col_data in enumerate(row_data):
                        self.table.setItem(row_position, col_number, QTableWidgetItem(col_data))

                    # 添加删除按钮，并设置点击事件
                    self.add_delete_button(row_position)
        except Exception as e:
            print(f"Error occurred while loading data from CSV: {e}")

    def clear_table(self):
        """清空表格"""
        self.table.setRowCount(0)

    def save_to_csv(self, file_path, headers, mode='w'):
        """
        将表格内容保存到 CSV 文件中。

        :param file_path: 文件路径
        :param mode: 文件打开模式 ('w' 表示覆盖，'a' 表示追加，默认为 'w')
        """
        # 请求用户确认
        reply = QMessageBox.question(
            None,
            "确认保存",
            f"您确定要将表格内容保存到 {file_path} 吗？\n模式: {mode}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        # 获取表格的行数和列数
        row_count = self.table.rowCount()
        column_count = len(config.get_feature_default(self.menuIndex))

        # 创建一个空列表来存储表格中的所有数据
        data = []
        for row in range(row_count):
            row_data = []
            for column in range(column_count):  # 限制列数
                # 获取单元格中的文本并添加到当前行数据列表中
                item = self.table.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")  # 如果单元格为空，则添加空字符串
            data.append(row_data)

        # 写入 CSV 文件
        with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if mode == 'w':
                writer.writerow(headers[:column_count])  # 写入表头，也只取前几列
            writer.writerows(data)

        QMessageBox.information(None, "保存成功", f"已将表格内容保存到 {file_path}")

    def collect_data(self):
        """数据写入表格"""
        try:
            data = get_new_data()
            if data is not None:
                # 获取当前表格的最后一行索引
                current_row_count = self.table.rowCount()

                # 在最后一行之后插入新行
                self.table.insertRow(current_row_count)

                # 写入数据
                for column_number, value in enumerate(data):
                    # 确保 value 是 int64 类型时转换为 int
                    if isinstance(value, np.int64):
                        value = int(value)
                    # 确保 value 是 int、float 或 str 类型
                    if isinstance(value, (int, float, str)):
                        self.table.setItem(current_row_count, column_number, QTableWidgetItem(str(value)))
                    else:
                        raise ValueError(f"Unsupported data type: {type(value)}")

                # 添加删除按钮
                self.add_delete_button(current_row_count)

                # 选中最后一行
                last_row_index = self.table.rowCount() - 1
                self.table.selectRow(last_row_index)
                self.table.viewport().update()
        except Exception as e:
            print(f"Error occurred while collecting data: {e}")

    def handle_cell_clicked(self, row, column):
        """处理单元格点击事件"""
        if column == self.table.columnCount() - 1:
            # 获取当前单元格的按钮
            button = self.table.cellWidget(row, column)
            if button and isinstance(button, QPushButton):
                button.click()

    def delete_row(self, button):
        """根据按钮对象删除对应的行"""
        index = self.table.indexAt(button.pos())
        if not index.isValid():
            return

        row_position = index.row()
        if row_position < 0:
            return

        reply = QMessageBox.question(self, 'Message', f"确定删除第{row_position+1}行吗?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.table.removeRow(row_position)


    def save_data(self):
        '''槽：保存数据'''
        data_path = self.cb_4.currentText()
        path = os.path.join(config.train_path , data_path + '.csv')
        # header = ('Z 轴振动速度', 'X 轴振动速度', 'Z 轴加速度峰值', 'X 轴加速度峰值', 'Z 轴峰值速度分量频率 Hz', 'X 轴峰值速度分量频率 Hz', 'Z 轴加速度均方根', "X 轴加速度均方根")
        data_old = []
        if self.cb_5.currentText() == '覆盖':
            self.save_to_csv(path, config.get_feature_default(self.menuIndex),'w')
        elif self.cb_5.currentText() == '追加':
            self.save_to_csv(path, config.get_feature_default(self.menuIndex),'a+')
        else:
            self.write_csv(path, config.get_feature_default(self.menuIndex), 'w')

    def btn_fun_2(self):
        '''槽：显示数据'''
        if not self.flag:
            threading.Thread(target=self.fun_1).start()
        start_draw_final()
        self.flag = 1


    def setbtn(self, btn):
        btn.setChecked(False)
        btn.toggled.connect(self.buttonState)
        self.VLayout_1.addWidget(btn)

    def buttonState(self):
        radioButton = self.sender()
        if radioButton.isChecked() == True:
            print('<' + radioButton.text() + '> 被选中')
        else:
            print('<' + radioButton.text() + '> 被取消选中状态')

    def closeEvent(self,event):
        # 关闭窗口事件
        self.setAttribute(Qt.WA_AttributeCount)
        self.exit = 1
        plt.close()