import csv
import os
import threading

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QStackedWidget, QSizePolicy, QFrame, QMessageBox, QCheckBox, \
    QHeaderView, QComboBox, QAbstractItemView, QFileDialog
from PyQt5.QtCore import Qt, QSize, QRect
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties

import config
from db.db_mysql import DB_MySQL
from ui.qss import btn_css
from ui.ui_dataCollectionWindow import DataCollectionWindow
from ui.ui_fun import BaseWindow, MyFigure
from utils.mongo import start_draw_final


class DataCollectionAllWindow(DataCollectionWindow):

    '''采集数据窗口'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_name = config.toname['数据采集']
        self.db = DB_MySQL()
     # 创建表
        with self.db:
            self.db.create_table(self.table_name , [('状态', 'TEXT'),]+config.get_feature_default(self.menuIndex)) # 状态 ：0 正常 1 异常

    def setbox_3(self):
        # 设置容器3
        self.groupbox_3 = QGroupBox()
        self.groupbox_3.setStyleSheet("background-color:white;")

        # 创建主垂直布局
        self.VLayout_3 = QVBoxLayout(self)

        # 定义按钮及其对应的槽函数
        buttons = [
            ('采集数据', self.collect_data),
            ('数据写入', self.save_data),
            ('数据读取', self.load_data),
            ('导入表格', self.import_table),
            ('导出表格', self.export_table),
            ('清空表格', self.clear_table)
        ]

        # 辅助函数：创建并设置按钮
        def create_button(text, callback):
            btn = QPushButton()
            btn.setText(text)
            btn.clicked.connect(lambda: self.safe_call(callback))
            btn_css(btn)
            btn.setMinimumSize(200, 30)

            return btn

        # 创建两个水平布局，分别放置上一行和下一行的按钮
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # 将按钮添加到相应的布局中
        for i, (text, callback) in enumerate(buttons):
            btn = create_button(text, callback)
            if i < 3:
                top_layout.addWidget(btn, alignment=Qt.AlignCenter)
            else:
                bottom_layout.addWidget(btn, alignment=Qt.AlignCenter)

        # 将两个水平布局添加到主垂直布局中
        self.VLayout_3.addLayout(top_layout)
        self.VLayout_3.addLayout(bottom_layout)

        self.groupbox_3.setLayout(self.VLayout_3)

    # 辅助函数：安全调用槽函数
    def safe_call(self, func):
        try:
            func()
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")

    def save_data(self):
        '''槽：保存数据'''
        if self.cb_5.currentText() == '覆盖':
            self.save_to_db('覆盖')
        elif self.cb_5.currentText() == '追加':
            self.save_to_db('追加')
        else:
            # 清空
            pass

    def save_to_db(self, mode='覆盖'):
        """
        将表格内容保存到数据库表中。

        :param mode: 模式
        """
        # 请求用户确认
        reply = QMessageBox.question(
            None,
            "确认保存",
            f"您确定要将表格内容保存到数据库中吗？\n模式: {mode}",
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
        current_status = self.cb_4.currentText()
        for row in range(row_count):
            row_data = []
            for column in range(column_count):  # 限制列数
                # 获取单元格中的文本并添加到当前行数据列表中
                item = self.table.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")  # 如果单元格为空，则添加空字符串
            # 添加状态字段
            row_data.append(current_status)
            data.append(row_data)

        # 连接到数据库
        with DB_MySQL() as db:
            # 根据模式决定是插入还是更新数据
            if mode == '覆盖':
                # 只删除与当前状态相同的行
                db.delete_data(self.table_name, f"状态 = '{current_status}'")

            # 插入数据
            for row in data:
                db.insert_data(self.table_name, dict(zip(config.get_feature_default(self.menuIndex) + ['状态'], row)))

        QMessageBox.information(None, "保存成功", f"已将表格内容保存到数据库中")

    def load_data(self):
        """从数据库中读取数据"""
        # 获取当前状态
        current_status = self.cb_4.currentText()

        # 获取表头列名
        columns = config.get_feature_default(self.menuIndex)

        # 连接到数据库
        with DB_MySQL() as db:
            # 读取数据
            data = db.select_data(self.table_name, columns, f"状态 = '{current_status}'")

        # 清空表格
        self.table.setRowCount(0)

        # 将数据加载到表格中
        for row_index, row_data in enumerate(data):
            self.table.insertRow(row_index)
            for column_index, value in enumerate(row_data.values()):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_index, column_index, item)

            # 添加删除按钮
            self.add_delete_button(row_index)


    def import_table(self):
        """从 CSV 文件中导入数据到表格"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 CSV 文件", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)  # 读取表头

                # 清空表格
                self.table.setRowCount(0)
                self.table.setColumnCount(len(headers) + 1)  # 增加一列用于删除按钮
                self.table.setHorizontalHeaderLabels(headers + ['操作'])

                # 读取数据并加载到表格中
                for row_index, row_data in enumerate(reader):
                    self.table.insertRow(row_index)
                    for column_index, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        self.table.setItem(row_index, column_index, item)

                    # 添加删除按钮
                    self.add_delete_button(row_index)

            QMessageBox.information(None, "导入成功", "数据已成功导入到表格中")


    def export_table(self):
        """将表格中的数据导出到 CSV 文件"""
        file_name = self.cb_4.currentText()
        if not file_name:
            QMessageBox.warning(None, "警告", "请选择一个有效的文件名")
            return

        # 确保文件名以 .csv 结尾
        if not file_name.endswith('.csv'):
            file_name += '.csv'

        file_path, _ = QFileDialog.getSaveFileName(self, "保存 CSV 文件", file_name, "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # 写入表头，忽略最后一列
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount() - 1)]
                writer.writerow(headers)

                # 写入数据，忽略最后一列
                for row_index in range(self.table.rowCount()):
                    row_data = []
                    for column_index in range(self.table.columnCount() - 1):  # 排除最后一列操作
                        item = self.table.item(row_index, column_index)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    writer.writerow(row_data)

            QMessageBox.information(None, "导出成功", f"数据已成功导出到 {file_path}")




