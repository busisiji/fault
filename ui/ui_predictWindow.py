import os
import datetime

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QDoubleValidator, QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox, QHeaderView, QAbstractItemView, QFileDialog, QDialog, QLineEdit, QToolTip, QTabWidget
from PyQt5.QtCore import Qt, QSize, pyqtSignal

import config
from ui.others.ui_fun import TableWidgetWithAverages
from qss.qss import btn_css
from ui.Base.baseWindow import BaseWindow


class PredictWindow(BaseWindow):

    '''采集数据窗口'''
    _single_update_data = pyqtSignal(str,list,list)
    def __init__(self,parent=None,menuIndex=2):
        super().__init__(parent)

        self.table_name = config.toname['预测数据']
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle('预测数据')
        # 获取传感器信息
        self.flag = 0
        self.fig = 0
        self.exit = 0
        self.tCN = 4 # 表格上面固定的行列数
        # 设置默认保存路径
        self.default_save_path = os.path.join(config.get_root_dir(), 'model')

        self.setbox_1()
        self.setbox_3()
        self.mainVLayout = QVBoxLayout(self)
        self.groupbox_1.setMinimumSize(QSize(self.width(), self.height() * 0.4))
        self.groupbox_3.setMinimumSize(QSize(self.width(), self.height() * 0.3))
        self.mainVLayout.addWidget(self.groupbox_1)
        self.mainVLayout.addWidget(self.groupbox_3)
        self.setLayout(self.mainVLayout)

        self._single_update_data.connect(self.update_data)

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

        # 创建表
        self.create_sensor_tables()

        self.groupbox_1.setLayout(self.VLayout_1)



    def setbox_3(self):
        # 设置容器3
        self.groupbox_3 = QGroupBox()
        self.groupbox_3.setStyleSheet("background-color:white;")

        # 创建主垂直布局
        self.VLayout_3 = QVBoxLayout(self)

        # 创建两个水平布局，分别放置上一行和下一行的按钮
        other_layout = QHBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()


        # 保存路径输入框
        self.save_path_label = QLabel('模型目录')
        self.save_path_label.setFont(config.font)
        self.save_path_lineedit = QLineEdit()
        self.save_path_lineedit.setFont(config.font)
        self.save_path_lineedit.setText(self.default_save_path)
        self.save_path_lineedit.setReadOnly(True)
        # self.select_path_button = QPushButton('选择路径')
        # btn_css(self.select_path_button)
        # self.select_path_button.setFont(config.font)
        # self.select_path_button.clicked.connect(self.select_save_path)

        other_layout.addWidget(self.save_path_label)
        other_layout.addWidget(self.save_path_lineedit)

        # 定义按钮及其对应的槽函数
        buttons = [
            ('手动添加', self.add_row_manually),
            ('导入表格', self.import_table),
            ('导出表格', self.export_table),
            ('清空表格', self.clear_table),
            ('刷新表格', self.refresh_table),
            ('开始预测' , self.start_prediction),
        ]
        # 辅助函数：创建并设置按钮
        def create_button(text, callback):
            btn = QPushButton()
            btn.setText(text)
            btn.clicked.connect(lambda checked, cb=callback: self.safe_call(cb,text))
            btn_css(btn)
            btn.setMinimumSize(200, 30)
            return btn


        # 将按钮添加到相应的布局中
        for i, (text, callback) in enumerate(buttons):
            btn = create_button(text, callback)
            if i < 3:
                top_layout.addWidget(btn)
            else:
                bottom_layout.addWidget(btn)

        # 将两个水平布局添加到主垂直布局中
        self.VLayout_3.addLayout(other_layout)
        self.VLayout_3.addLayout(top_layout)
        self.VLayout_3.addLayout(bottom_layout)

        self.groupbox_3.setLayout(self.VLayout_3)
    def create_sensor_tables(self):
        for sensor in self.sensors:
            sensor_name = sensor['sensor_name']

            widget = self.add_table(sensor)

            # 将 QWidget 添加到标签页
            self.tab_widget.addTab(widget, sensor_name)
    def add_table(self,sensor):
        # 创建表格
        sensor_name = sensor['sensor_name']
        param_names = sensor['param_name']
        status_list = sensor['status_list']

        table = TableWidgetWithAverages()
        table.init_averages_table([])
        self.tRN = 0
        table.setColumnCount(len(param_names) +self.tCN)  # 增加三列用于编辑、删除按钮和更新时间
        table.setHorizontalHeaderLabels(param_names + ['预测结果','更新时间', '编辑', '删除'])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 宽高自动分配
        table.horizontalHeader().setSectionResizeMode(table.columnCount() - self.tCN, QHeaderView.Fixed)

        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 当需要时显示垂直滚动条

        # 禁止编辑
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 禁止选择单元格
        table.setSelectionMode(QAbstractItemView.NoSelection)
        # 固定表头
        # table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        table.setStyleSheet(self.table_style)
        table.setObjectName(sensor_name)

        # 设置平均值行的背景颜色为绿色
        for column in range(table.columnCount()):
            item = QTableWidgetItem()
            item.setBackground(QColor(0, 255, 0))
            table.setItem(0, column, item)

        # 创建 groupbox_4
        # groupbox_4 = QGroupBox()
        # groupbox_4.setTitle('保存采集数据')
        # groupbox_4.setAlignment(Qt.AlignHCenter)  # 标题居中
        # font = QFont()
        # font.setPointSize(23)
        # groupbox_4.setFont(font)
        # groupbox_4.setStyleSheet("background-color:white;")
        #
        # # 将控件填入布局中
        # VLayout_4 = QHBoxLayout()
        # label_4 = QLabel()
        # label_4.setText('选择要采集的数据类型为')
        # label_4.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中
        # cb_4 = QComboBox(maximumWidth=300)
        # cb_4.addItems(status_list)
        # cb_4.setObjectName('cb_4')
        # label_4.setMaximumSize(groupbox_4.width() * 0.7, groupbox_4.height())
        # label_4.setMinimumSize(groupbox_4.width() * 0.1, 100)
        #
        # VLayout_4.addWidget(label_4)
        # VLayout_4.addWidget(cb_4)
        #
        # VLayout_5 = QHBoxLayout()
        # label_5 = QLabel()
        # label_5.setText('选择保存数据的方式为')
        # label_5.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中
        # label_5.setMaximumSize(groupbox_4.width() * 0.7, groupbox_4.height())
        # label_5.setMinimumSize(groupbox_4.width() * 0.5, 100)
        # cb_5 = QComboBox(maximumWidth=300)
        # cb_5.addItems(['不保存','追加', '覆盖'])
        # cb_5.setObjectName('cb_5')
        # for i in [label_4, label_5, cb_4, cb_5]:
        #     font.setPointSize(23)
        #     i.setFont(font)
        #     i.setStyleSheet("color:black;")
        #
        # VLayout_5.addWidget(label_5)
        # VLayout_5.addWidget(cb_5)
        #
        # mainVLayout_4 = QVBoxLayout()
        # mainVLayout_4.addLayout(VLayout_4)
        # mainVLayout_4.addLayout(VLayout_5)
        # groupbox_4.setLayout(mainVLayout_4)

        # 创建垂直布局
        VLayout = QVBoxLayout()
        VLayout.addWidget(table)
        # VLayout.addWidget(groupbox_4)

        # 创建一个 QWidget 作为标签页的内容
        widget = QWidget()
        widget.setLayout(VLayout)
        # 为表格添加鼠标点击事件
        table.viewport().installEventFilter(self)

        # 为表格添加右键菜单
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)
        return widget

    """ ---------------表格操作 - --------------------"""
    # def setup_table_headers(self, table):
    #     """设置表格列名"""
    #     headers = ['状态', '更新时间']
    #     columns = self.get_unique_columns()
    #     for column in columns:
    #         original_column_name = column[0]
    #         headers.append(original_column_name)
    #
    #     table.setHorizontalHeaderLabels(headers)

    def eventFilter(self, source, event):
        """悬浮显示"""
        if event.type() == event.MouseButtonPress:
            if source is self.tab_widget.currentWidget().findChild(QTableWidget).viewport():
                index = self.tab_widget.currentWidget().findChild(QTableWidget).indexAt(event.pos())
                if index.isValid():
                    item = self.tab_widget.currentWidget().findChild(QTableWidget).item(index.row(), index.column())
                    if item:
                        if index.column() == self.tab_widget.currentWidget().findChild(QTableWidget).columnCount() - 4:
                            QToolTip.showText(event.globalPos(), item.toolTip())
                        else:
                            QToolTip.showText(event.globalPos(), item.text())
                    else:
                        QToolTip.hideText()
                else:
                    QToolTip.hideText()
            elif source is self.tab_widget.currentWidget().findChild(QTableWidget).horizontalHeader():
                # 处理表头点击事件
                logical_index = self.tab_widget.currentWidget().findChild(QTableWidget).horizontalHeader().logicalIndexAt(event.pos())
                header_item = self.tab_widget.currentWidget().findChild(QTableWidget).horizontalHeaderItem(logical_index)
                if header_item:
                    QToolTip.showText(event.globalPos(), header_item.text())
                else:
                    QToolTip.hideText()
        return super().eventFilter(source, event)



    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QtWidgets.QMenu(self)
        sort_asc_action = menu.addAction("正序排序")
        sort_desc_action = menu.addAction("逆序排序")

        action = menu.exec_(self.tab_widget.currentWidget().findChild(QTableWidget).viewport().mapToGlobal(pos))

        if action == sort_asc_action:
            self.sort_table(True, pos)
        elif action == sort_desc_action:
            self.sort_table(False, pos)

    def update_data(self, sensor_name, param_names, results):
        """
        将数据添加到对应传感器的表格中。

        :param sensor_name: 传感器名称
        :param param_names: 参数列表
        :param results: 值列表
        """
        if self.auto_collect_switch.state:
            # 查找对应传感器的标签页
            for index in range(self.tab_widget.count()):
                current_tab = self.tab_widget.widget(index)
                if self.tab_widget.tabText(index) == sensor_name:
                    break
            else:
                raise ValueError(f"未找到名为 {sensor_name} 的传感器标签页")

            # 获取表格
            table = current_tab.findChild(QTableWidget)

            # 插入新行
            row_index = table.rowCount()
            table.insertRow(row_index)
            table.setRowHeight(row_index, 40)

            # 填充参数值
            for column, param_name in enumerate(param_names):
                value = results[column]
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_index, column, item)

            # 添加更新时间列
            update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item = QTableWidgetItem(update_time)
            item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
            table.setItem(row_index, table.columnCount() - 3, item)

            # 添加编辑和删除按钮
            self.add_edit_button(table, row_index)
            self.add_delete_button(table, row_index)

            self.refresh_table_form_time()

    def sort_table(self, ascending=True, pos=None,column=None):
        """根据列排序表格"""
        table = self.tab_widget.currentWidget().findChild(QTableWidget)
        if column is None:
            column = table.columnAt(pos.x())

        # 获取所有行的数据
        rows = []
        for row_index in range(self.tRN,table.rowCount()):
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
        table.setRowCount(self.tRN)

        # 重新加载数据
        for row_index, row_data in enumerate(rows):
            new_row_index = row_index + self.tRN
            table.insertRow(new_row_index)
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
                table.setItem(new_row_index, col_index, item)

            # 添加编辑按钮
            self.add_edit_button(table, new_row_index)

            # 添加删除按钮
            self.add_delete_button(table, new_row_index)

        QMessageBox.information(None, "提示", "表格已排序")

    def get_unique_columns(self):
        """获取所有传感器的参数，并加上传感器名称前缀"""
        columns = []
        sensors = config.get_sensors()

        for sensor in sensors:
            sensor_name = sensor['sensor_name']
            features = config.get_feature_default()

            for feature in features:
                column_name = f"{sensor_name}_{feature}"
                columns.append((column_name, 'TEXT'))

        return columns


    def add_row_manually(self):
        """手动添加一行数据"""
        table = self.tab_widget.currentWidget().findChild(QTableWidget)
        column_count = table.columnCount() - self.tCN  # 排除编辑、删除按钮和更新时间列

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


        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(
            lambda: self.confirm_add_row(dialog, table, row_data, layout))
        layout.addWidget(confirm_button)

        dialog.setLayout(layout)
        dialog.exec_()
        self.refresh_tables_form_time()

    def confirm_add_row(self, dialog, table, row_data, layout):
        """确认添加的数据"""
        new_data = []
        for i in range(len(row_data)):
            line_edit = layout.itemAt(i * 2 + 1).widget()
            new_data.append(line_edit.text())

        row_index = table.rowCount()
        table.insertRow(row_index)
        table.setRowHeight(row_index, 40)
        for column, value in enumerate(new_data):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
            table.setItem(row_index, column, item)

        # 添加更新时间列
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = QTableWidgetItem(update_time)
        item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
        table.setItem(row_index, table.columnCount() - 3, item)

        # 添加编辑和删除按钮
        self.add_edit_button(table, row_index)
        self.add_delete_button(table, row_index)

        dialog.accept()



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
        for column in range(table.columnCount() -self.tCN):  # 排除编辑、删除按钮和更新时间列
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


        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(
            lambda: self.confirm_edit_row(dialog, table, row_index, row_data, layout))
        layout.addWidget(confirm_button)

        dialog.setLayout(layout)
        dialog.exec_()
        self.refresh_table_form_time()
        QMessageBox.information(None, "提示", "数据已更新在最下一行")


    def confirm_edit_row(self, dialog, table, row_index, row_data, layout):
        """确认编辑后的数据"""
        new_data = []
        for i in range(len(row_data)):
            line_edit = layout.itemAt(i * 2 + 1).widget()
            new_data.append(line_edit.text())

        for column, value in enumerate(new_data):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
            table.setItem(row_index, column, item)

        # 更新时间
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = QTableWidgetItem(update_time)
        item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
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
            self.tab_widget.currentWidget().findChild(QTableWidget).removeRow(row_index)
            # 刷新表格以确保行数正确
            self.refresh_tables_form_time()
            QMessageBox.information(None, "删除成功", "已删除这一行数据")

    def refresh_table(self):
        """刷新表格"""
        self.refresh_tables_form_time()
        QMessageBox.information(None, "提示", "表格已刷新")

    def refresh_table_form_time(self,table=None):
        """按时间顺序重新排列表格"""
        try:
            if table is None:
                table = self.tab_widget.currentWidget().findChild(QTableWidget)
            # 获取所有行的数据
            rows = []
            for row_index in range(self.tRN,table.rowCount()):
                row_data = []
                for column_index in range(table.columnCount()):
                    item = table.item(row_index, column_index)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                rows.append(row_data)

            # 按更新时间排序
            if len(rows) <= self.tRN:
                return
            elif len(rows) > self.tRN:
                rows.sort(key=lambda x: x[table.columnCount() - self.tCN])

            # 清空表格
            table.setRowCount(self.tRN)

            # 重新加载数据
            for row_index, row_data in enumerate(rows):
                new_row_index = row_index + self.tRN
                table.insertRow(new_row_index)
                for column_index, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
                    table.setItem(new_row_index, column_index, item)

                # 添加编辑按钮
                self.add_edit_button(table,new_row_index)

                # 添加删除按钮
                self.add_delete_button(table,new_row_index)

            table.refresh_table()
        except Exception as e:
            print(e)
            # QMessageBox.critical(None, "错误", f"刷新表格时发生错误：{str(e)}")

    def refresh_tables_form_time(self):
        """按时间顺序重新排列表格"""
        try:
            for index in range(self.tab_widget.count()):
                current_tab = self.tab_widget.widget(index)
                table = current_tab.findChild(QTableWidget)
                self.refresh_table_form_time(table)
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
            table = self.tab_widget.currentWidget().findChild(QTableWidget)
            table.setRowCount(self.tRN)
            QMessageBox.information(None, "清空成功", "已清空当前表格中的所有数据")

    def get_tab_by_name(self, name):
        """获取名字为 name 的标签页"""
        # 遍历所有标签页
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.findChild(QTableWidget).objectName() == name:
                return tab
        return None

    """ ----------------CSV操作---------------------"""


    def select_save_path(self):
        # 弹出文件对话框选择保存路径
        directory = QFileDialog.getExistingDirectory(self, "选择模型路径")
        if directory:
            self.save_path_lineedit.setText(directory)



    def update_ui(self):
        # 获取最新的传感器信息
        old_sensors = self.sensors
        new_sensors = config.get_sensors()
        self.sensors = new_sensors

        # 提取旧的和新的传感器名称
        old_sensor_names = {sensor['sensor_name'] for sensor in old_sensors}
        new_sensor_names = {sensor['sensor_name'] for sensor in new_sensors}

        # 找出新增的传感器和删除的传感器
        added_sensors = new_sensor_names - old_sensor_names
        removed_sensors = old_sensor_names - new_sensor_names

        # 删除不再存在的传感器表格
        for i in range(self.tab_widget.count() - 1, -1, -1):
            tab = self.tab_widget.widget(i)
            table = tab.findChild(QTableWidget)
            if table and table.objectName() in removed_sensors:
                self.tab_widget.removeTab(i)

        # 添加新的传感器表格
        for sensor_name in added_sensors:
            sensor = self.get_sensor_by_name(sensor_name)
            if sensor:
                widget = self.add_table(sensor)
                self.tab_widget.addTab(widget, sensor_name)

        # 更新现有传感器表格的列
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            table = tab.findChild(QTableWidget)
            if table:
                sensor_name = table.objectName()
                sensor = self.get_sensor_by_name(sensor_name)
                if sensor:
                    new_headers = sensor['param_name']
                    new_headers.extend(table.horizontalHeaderItem(col).text() for col in
                                       range(table.columnCount() - 4, table.columnCount()))

                    # 获取当前表格的列名
                    current_headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]

                    # 删除不再存在的列
                    for col in range(table.columnCount() - 1, -1, -1):
                        if table.horizontalHeaderItem(col).text() not in new_headers:
                            table.removeColumn(col)

                    # 添加新列
                    for header in new_headers:
                        if header not in current_headers:
                            table.insertColumn(table.columnCount() - 4)  # 在倒数第4列之前插入新列
                            item = QTableWidgetItem(header)
                            table.setHorizontalHeaderItem(table.columnCount() - 4 - 1, item)  # 设置新列的标题
