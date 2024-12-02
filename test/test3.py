import csv
import datetime

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox, QHeaderView, QAbstractItemView, QFileDialog, QDialog, QLineEdit, QToolTip, QTabWidget
from PyQt5.QtCore import Qt

import config
from db.db_mysql import DB_MySQL
from qss.qss import btn_css
from ui.ui_dataCollectionWindow import DataCollectionWindow


class DataCollectionAllWindow(DataCollectionWindow):

    '''采集数据窗口'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_name = config.toname['数据采集']
        self.db = DB_MySQL()
        # 创建表
        with self.db:
            self.db.create_table(self.table_name,
                                 [('status', 'TEXT'),
                                  ('update_time', 'DATETIME')] + self.get_unique_columns())  # 状态 ：0 正常 1 异常

        # 添加手动添加按钮
        self.add_button = QPushButton("手动添加")
        self.add_button.clicked.connect(self.add_row_manually)
        btn_css(self.add_button)
        self.add_button.setMinimumSize(200, 30)
        self.VLayout_3.addWidget(self.add_button)

        # 添加刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_table)
        btn_css(self.refresh_button)
        self.refresh_button.setMinimumSize(200, 30)
        self.VLayout_3.addWidget(self.refresh_button)

        # 为表格添加鼠标移动事件
        self.tab_widget.currentWidget().viewport().installEventFilter(self)

        # 为表格添加右键菜单
        self.tab_widget.currentWidget().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.currentWidget().customContextMenuRequested.connect(self.show_context_menu)

    def create_sensor_tables(self):
        for sensor in self.sensors:
            sensor_name = sensor['sensor_name']
            param_names = sensor['param_name']

            # 创建表格
            table = QTableWidget()
            table.setColumnCount(len(param_names) + 3)  # 增加三列用于编辑、删除按钮和更新时间
            table.setHorizontalHeaderLabels(param_names + ['更新时间', '编辑', '删除'])
            table.horizontalHeader().setSectionResizeMode(table.columnCount() - 3, QHeaderView.Fixed)

            # 禁止编辑
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            # 禁止选择单元格
            table.setSelectionMode(QAbstractItemView.NoSelection)

            # 将表格添加到标签页
            self.tab_widget.addTab(table, sensor_name)

            # 为表格添加鼠标移动事件
            table.viewport().installEventFilter(self)

            # 为表格添加右键菜单
            table.setContextMenuPolicy(Qt.CustomContextMenu)
            table.customContextMenuRequested.connect(self.show_context_menu)

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

        # 创建标签栏
        self.tab_widget = QTabWidget()
        self.VLayout_1.addWidget(self.tab_widget)

        # 获取传感器信息
        self.sensors = config.get_sensors()
        self.create_sensor_tables()

        self.groupbox_1.setLayout(self.VLayout_1)

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
                top_layout.addWidget(btn)
            else:
                bottom_layout.addWidget(btn)

        # 将两个水平布局添加到主垂直布局中
        self.VLayout_3.addLayout(top_layout)
        self.VLayout_3.addLayout(bottom_layout)

        self.groupbox_3.setLayout(self.VLayout_3)

    def setup_table_headers(self, table):
        """设置表格列名"""
        headers = ['状态', '更新时间']
        columns = self.get_unique_columns()
        for column in columns:
            original_column_name = column[0]
            headers.append(original_column_name)

        table.setHorizontalHeaderLabels(headers)

    def eventFilter(self, source, event):
        """悬浮显示"""
        if event.type() == event.MouseButtonPress:
            if source is self.tab_widget.currentWidget().viewport():
                index = self.tab_widget.currentWidget().indexAt(event.pos())
                if index.isValid():
                    item = self.tab_widget.currentWidget().item(index.row(), index.column())
                    if item:
                        QToolTip.showText(event.globalPos(), item.text())
                    else:
                        QToolTip.hideText()
                else:
                    QToolTip.hideText()
            elif source is self.tab_widget.currentWidget().horizontalHeader():
                # 处理表头点击事件
                logical_index = self.tab_widget.currentWidget().horizontalHeader().logicalIndexAt(event.pos())
                header_item = self.tab_widget.currentWidget().horizontalHeaderItem(logical_index)
                if header_item:
                    QToolTip.showText(event.globalPos(), header_item.text())
                else:
                    QToolTip.hideText()
        return super().eventFilter(source, event)

    # 辅助函数：安全调用槽函数
    def safe_call(self, func):
        try:
            func()
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")

    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QtWidgets.QMenu(self)
        sort_asc_action = menu.addAction("正序排序")
        sort_desc_action = menu.addAction("逆序排序")

        action = menu.exec_(self.tab_widget.currentWidget().viewport().mapToGlobal(pos))

        if action == sort_asc_action:
            self.sort_table(True, pos)
        elif action == sort_desc_action:
            self.sort_table(False, pos)

    def sort_table(self, ascending, pos):
        """根据列排序表格"""
        table = self.tab_widget.currentWidget()
        column = table.columnAt(pos.x())

        # 获取所有行的数据
        rows = []
        for row_index in range(table.rowCount()):
            row_data = []
            for col_index in range(table.columnCount()):
                item = table.item(row_index, col_index)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            rows.append(row_data)

        # 按选定列排序
        def sort_key(row):
            try:
                value = float(row[column])
            except ValueError:
                value = float('inf')  # 非数值或空值排到最后
            return (value, row[-3])  # 按数值和更新时间排序

        rows.sort(key=sort_key, reverse=not ascending)

        # 清空表格
        table.setRowCount(0)

        # 重新加载数据
        for row_index, row_data in enumerate(rows):
            table.insertRow(row_index)
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row_index, col_index, item)

            # 添加编辑按钮
            self.add_edit_button(table, row_index)

            # 添加删除按钮
            self.add_delete_button(table, row_index)

        QMessageBox.information(None, "提示", "表格已排序")

    def get_unique_columns(self):
        """获取所有传感器的参数，并加上传感器名称前缀，转换为英文列名"""
        columns = []
        sensors = config.get_sensors()

        for sensor in sensors:
            sensor_name = sensor['sensor_name']
            features = config.get_feature_default(self.menuIndex)

            for feature in features:
                column_name = f"{sensor_name}_{feature}"
                columns.append((column_name, 'TEXT'))

        return columns


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

        with DB_MySQL() as db:
            for i in range(self.tab_widget.count()):
                table = self.tab_widget.widget(i)
                row_count = table.rowCount()
                column_count = table.columnCount() - 3  # 排除编辑、删除按钮和更新时间列
                data = []

                for row in range(row_count):
                    row_data = []
                    for column in range(column_count):
                        item = table.item(row, column)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append("")
                    row_data.append(self.cb_4.currentText())  # 状态
                    row_data.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # 更新时间
                    data.append(row_data)

                if mode == '覆盖':
                    backup_data = db.select_data(self.table_name, f"状态 = '{self.cb_4.currentText()}'")
                    db.delete_data(self.table_name, f"状态 = '{self.cb_4.currentText()}'")

                for row in data:
                    db.insert_data(self.table_name, dict(zip(config.get_feature_default(self.menuIndex) + ['状态', '更新时间'], row)))

        QMessageBox.information(None, "保存成功", f"已将表格内容保存到数据库中")

    def load_data(self):
        """从数据库中读取数据"""
        current_status = self.cb_4.currentText()
        columns = config.get_feature_default(self.menuIndex)

        with DB_MySQL() as db:
            data = db.select_data(self.table_name, condition=f"状态 = '{current_status}'")

        for i in range(self.tab_widget.count()):
            table = self.tab_widget.widget(i)
            table.setRowCount(0)
            for row_index, row_data in enumerate(data):
                table.insertRow(row_index)
                for column_index, column_name in enumerate(columns):
                    value = row_data.get(column_name)
                    if value is not None:
                        item = QTableWidgetItem(str(value))
                        table.setItem(row_index, column_index, item)
                update_time = row_data.get('更新时间')
                if update_time is not None:
                    item = QTableWidgetItem(str(update_time))
                    table.setItem(row_index, len(columns), item)
                self.add_edit_button(table, row_index)
                self.add_delete_button(table, row_index)

    def import_table(self):
        """从 CSV 文件中导入数据到表格"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 CSV 文件", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = config.convert_to_db_columns(next(reader))  # 读取表头

                for i in range(self.tab_widget.count()):
                    table = self.tab_widget.widget(i)
                    table.setRowCount(0)
                    table.setColumnCount(len(headers) + 3)
                    self.table.setHorizontalHeaderLabels(headers + ['更新时间', '编辑', '删除'])

                    # 读取数据并填充表格
                    for row_index, row_data in enumerate(reader):
                        table.insertRow(row_index)
                        for column_index, value in enumerate(row_data):
                            item = QTableWidgetItem(str(value))
                            table.setItem(row_index, column_index, item)
                        # 添加更新时间列
                        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        item = QTableWidgetItem(update_time)
                        table.setItem(row_index, len(headers), item)
                        # 添加编辑和删除按钮
                        self.add_edit_button(table, row_index)
                        self.add_delete_button(table, row_index)

                QMessageBox.information(None, "导入成功", f"已将数据从 {file_path} 导入到表格中")

    def export_table(self):
        """导出当前表格中的数据到 CSV 文件"""
        file_path, _ = QFileDialog.getSaveFileName(self, "保存 CSV 文件", "", "CSV Files (*.csv)")
        if file_path:
            table = self.tab_widget.currentWidget()
            row_count = table.rowCount()
            column_count = table.columnCount() - 3  # 排除编辑、删除按钮和更新时间列

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                headers = [table.horizontalHeaderItem(i).text() for i in range(column_count)]
                writer.writerow(headers)

                for row in range(row_count):
                    row_data = []
                    for column in range(column_count):
                        item = table.item(row, column)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append("")
                    writer.writerow(row_data)

            QMessageBox.information(None, "导出成功", f"已将表格数据导出到 {file_path}")



    def confirm_add(self, dialog, table, row_data, layout):
        """确认添加的数据"""
        new_data = []
        for i in range(len(row_data)):
            line_edit = layout.itemAt(i * 2 + 1).widget()
            new_data.append(line_edit.text())

        row_index = table.rowCount()
        table.insertRow(row_index)
        for column, value in enumerate(new_data):
            item = QTableWidgetItem(value)
            table.setItem(row_index, column, item)

        # 添加更新时间列
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = QTableWidgetItem(update_time)
        table.setItem(row_index, table.columnCount() - 3, item)

        # 添加编辑和删除按钮
        self.add_edit_button(table, row_index)
        self.add_delete_button(table, row_index)

        dialog.accept()

    def add_row_manually(self):
        """手动添加一行数据"""
        table = self.tab_widget.currentWidget()
        column_count = table.columnCount() - 3  # 排除编辑、删除按钮和更新时间列

        dialog = QDialog(self)
        dialog.setWindowTitle("手动添加数据")
        layout = QVBoxLayout()

        row_data = [''] * column_count  # 初始化为空字符串

        for i in range(column_count):
            label = QLabel(table.horizontalHeaderItem(i).text())
            line_edit = QLineEdit()
            # 设置输入验证器，只允许输入小数
            validator = QDoubleValidator()
            line_edit.setValidator(validator)
            layout.addWidget(label)
            layout.addWidget(line_edit)

            layout.addWidget(label)
            layout.addWidget(line_edit)

        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(
            lambda: self.confirm_add(dialog, table, row_data, layout))
        layout.addWidget(confirm_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def add_edit_button(self, table, row_index):
        """添加编辑按钮"""
        edit_button = QPushButton("编辑")
        edit_button.clicked.connect(lambda: self.edit_row(table, row_index))
        btn_css(edit_button)
        table.setCellWidget(row_index, table.columnCount() - 2, edit_button)

    def add_delete_button(self, table, row_index):
        """添加删除按钮"""
        delete_button = QPushButton("删除")
        delete_button.clicked.connect(lambda: self.delete_row(table, row_index))
        btn_css(delete_button)
        table.setCellWidget(row_index, table.columnCount() - 1, delete_button)

    def edit_row(self, table, row_index):
        """编辑某一行的数据"""
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑数据")
        layout = QVBoxLayout()

        row_data = []
        for column in range(table.columnCount() - 3):  # 排除编辑、删除按钮和更新时间列
            item = table.item(row_index, column)
            if item is not None:
                row_data.append(item.text())
            else:
                row_data.append("")

        for i, value in enumerate(row_data):
            label = QLabel(table.horizontalHeaderItem(i).text())
            line_edit = QLineEdit(value)
            # 设置输入验证器，只允许输入小数
            validator = QDoubleValidator()
            line_edit.setValidator(validator)
            layout.addWidget(label)
            layout.addWidget(line_edit)

            layout.addWidget(label)
            layout.addWidget(line_edit)

        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(
            lambda: self.confirm_edit(dialog, table, row_index, row_data, layout))
        layout.addWidget(confirm_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def confirm_edit(self, dialog, table, row_index, row_data, layout):
        """确认编辑后的数据"""
        new_data = []
        for i in range(len(row_data)):
            line_edit = layout.itemAt(i * 2 + 1).widget()
            new_data.append(line_edit.text())

        for column, value in enumerate(new_data):
            item = QTableWidgetItem(value)
            table.setItem(row_index, column, item)

        # 更新时间
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = QTableWidgetItem(update_time)
        table.setItem(row_index, table.columnCount() - 3, item)

        dialog.accept()

    def delete_row(self, table, row_index):
        """删除某一行的数据"""
        reply = QMessageBox.question(
            None,
            "确认删除",
            "您确定要删除这一行数据吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            table.removeRow(row_index)
            QMessageBox.information(None, "删除成功", "已删除这一行数据")

    def refresh_table(self):
        """按时间顺序重新排列表格"""
        try:
            # 获取所有行的数据
            rows = []
            for row_index in range(self.table.rowCount()):
                row_data = []
                for column_index in range(self.table.columnCount()):
                    item = self.table.item(row_index, column_index)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                rows.append(row_data)

            # 按更新时间排序
            rows.sort(key=lambda x: x[self.table.columnCount() - 3])

            # 清空表格
            self.table.setRowCount(0)

            # 重新加载数据
            for row_index, row_data in enumerate(rows):
                self.table.insertRow(row_index)
                for column_index, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_index, column_index, item)

                # 添加编辑按钮
                self.add_edit_button(row_index)

                # 添加删除按钮
                self.add_delete_button(row_index)

            QMessageBox.information(None, "提示", "表格已刷新")
        except Exception as e:
            QMessageBox.critical(None, "错误", f"刷新表格时发生错误：{str(e)}")

    def clear_table(self):
        """清空当前表格中的数据"""
        reply = QMessageBox.question(
            None,
            "确认清空",
            "您确定要清空当前表格中的所有数据吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            table = self.tab_widget.currentWidget()
            table.setRowCount(0)
            QMessageBox.information(None, "清空成功", "已清空当前表格中的所有数据")