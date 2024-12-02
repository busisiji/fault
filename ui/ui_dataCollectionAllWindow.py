import os
import datetime
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QGroupBox, QSizePolicy, QMessageBox, QHeaderView, QComboBox, QAbstractItemView, \
    QDialog, QLineEdit, QToolTip, QTabWidget, QApplication, QSpacerItem, QScrollArea, QStackedWidget
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QSignalBlocker, QTimer

import config
from db.db_mysql import DB_MySQL
from qss.qss import btn_css
from ui.others.ui_fun import TableWidgetWithAverages, SwitchButton
from ui.Base.baseWindow import BaseWindow


def prompt_overwrite(file_path,mode):
    if os.path.exists(file_path):
        if mode == '覆盖':
            response = QMessageBox.question(None, "文件已存在", f"文件 {file_path} 已存在，是否覆盖？",
                                           QMessageBox.Yes | QMessageBox.No)
            return response == QMessageBox.Yes
    return True

class DataCollectionAllWindow(BaseWindow):

    '''采集数据窗口'''
    _single_update_data = pyqtSignal(str,list,list)
    _single_update_groupbox = pyqtSignal(dict)
    def __init__(self,parent=None,menuIndex=2):
        super().__init__(parent)

        self.table_name = config.toname['数据采集']
        self.db = DB_MySQL()
        # 创建表
        with self.db:
            self.db.create_table(self.table_name,
                                 [('status', 'TEXT'),
                                  ('update_time', 'DATETIME'),
                                  ('sensor_name', 'TEXT'),
                                  ('params', 'TEXT')])  # 状态 ：0 正常 1 异常

        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle('采集数据')
        # 获取传感器信息
        self.flag = 0
        self.fig = 0
        self.exit = 0
        self.tRN = 3 # 表格上面固定的行数 平均行、最大行、最小行
        # 阙值控件
        self.threshold_inputs = {}
        self.column_weigets = {}
        self.show_count = {}
        self.groupbox_threshold = {}


        self.setbox_1()
        self.setbox_3()
        self.mainVLayout = QVBoxLayout(self)
        self.groupbox_1.setMinimumSize(QSize(self.width(), int(self.height() * 0.4)))
        self.groupbox_3.setMinimumSize(QSize(self.width(), int(self.height() * 0.3)))
        self.mainVLayout.addWidget(self.groupbox_1)
        self.mainVLayout.addWidget(self.groupbox_3)
        self.setLayout(self.mainVLayout)

        self._single_update_data.connect(self.update_data)
        # self._single_update_groupbox.connect(self.update_groupbox_threshold)

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


        # 定义按钮及其对应的槽函数
        buttons = [
            ('超最大阈值次数统计', lambda: self.show_threshold_count_for_current_tab('max')),
            ('超最小阈值次数统计', lambda: self.show_threshold_count_for_current_tab('min')),
            # ('采集数据', self.collect_data),
            ('数据写入', self.save_data),
            ('数据读取', self.load_to_db),
            ('手动添加', self.add_row_manually),
            ('导入表格', self.import_table),
            ('导出表格', self.export_table),
            ('清空表格', self.clear_table),
            ('刷新表格', self.refresh_table),
        ]

        # 辅助函数：创建并设置按钮
        def create_button(text, callback):
            btn = QPushButton()
            btn.setText(text)
            btn.clicked.connect(lambda checked, cb=callback: self.safe_call(cb, text))
            btn_css(btn)
            btn.setMinimumSize(200, 30)

            return btn


        # 创建两个水平布局，分别放置上一行和下一行的按钮
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # 创建标签和开关按钮
        auto_collect_label = QLabel('自动采集')
        auto_collect_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.auto_collect_switch = SwitchButton()
        # 将标签和time按钮添加到 top_layout 中
        top_layout.addWidget(auto_collect_label)
        top_layout.addWidget(self.auto_collect_switch)

        # 将按钮添加到相应的布局中
        for i, (text, callback) in enumerate(buttons):
            btn = create_button(text, callback)
            if i < 4:
                top_layout.addWidget(btn)
            else:
                bottom_layout.addWidget(btn)

        # 将两个水平布局添加到主垂直布局中
        self.VLayout_3.addLayout(top_layout)
        self.VLayout_3.addLayout(bottom_layout)

        self.groupbox_3.setLayout(self.VLayout_3)
    def create_sensor_tables(self):
        for sensor in self.sensors:
            sensor_name = sensor['sensor_name']

            widget = self.add_table(sensor)

            # 将 QWidget 添加到标签页
            self.tab_widget.addTab(widget, sensor_name)

    def add_table(self, sensor):
        # 创建表格
        sensor_name = sensor['sensor_name']
        param_names = sensor['param_name']
        status_list = sensor['status_list']

        table = TableWidgetWithAverages()
        table.init_averages_table()
        self.tRN = table.heiRowNum
        table.setColumnCount(len(param_names) + 3)  # 增加三列用于编辑、删除按钮和更新时间
        table.setHorizontalHeaderLabels(param_names + ['更新时间', '编辑', '删除'])
        table.horizontalHeader().setSectionResizeMode(table.columnCount() - 3, QHeaderView.Fixed)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 当需要时显示垂直滚动条
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setStyleSheet(self.table_style)
        table.setObjectName(sensor_name)

        # 创建 groupbox_4
        groupbox_4 = QGroupBox()
        groupbox_4.setTitle('保存采集数据')
        groupbox_4.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        groupbox_4.setFont(font)
        groupbox_4.setStyleSheet("background-color:white;")

        # 将控件填入布局中
        VLayout_4 = QHBoxLayout()
        label_4 = QLabel()
        label_4.setText('选择要采集的数据标签为')
        label_4.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中
        cb_4 = QComboBox(maximumWidth=300)
        cb_4.addItems(status_list)
        cb_4.setObjectName('cb_4')
        label_4.setMaximumSize(int(groupbox_4.width() * 0.7), 100)
        label_4.setMinimumSize(int(groupbox_4.width() * 0.2), 20)

        VLayout_4.addWidget(label_4)
        VLayout_4.addWidget(cb_4)

        VLayout_5 = QHBoxLayout()
        label_5 = QLabel()
        label_5.setText('选择保存数据的方式为')
        label_5.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中
        label_5.setMaximumSize(int(groupbox_4.width() * 0.7), 100)
        label_5.setMinimumSize(int(groupbox_4.width() * 0.2), 20)
        cb_5 = QComboBox(maximumWidth=300)
        cb_5.addItems(['不保存', '追加', '覆盖'])
        cb_5.setObjectName('cb_5')
        for i in [label_4, label_5, cb_4, cb_5]:
            font.setPointSize(23)
            i.setFont(font)
            i.setStyleSheet("color:black;")

        VLayout_5.addWidget(label_5)
        VLayout_5.addWidget(cb_5)

        mainVLayout_4 = QVBoxLayout()
        mainVLayout_4.addLayout(VLayout_4)
        mainVLayout_4.addLayout(VLayout_5)
        groupbox_4.setLayout(mainVLayout_4)

        # 创建 QGroupBox 用于显示超阈值次数
        self.groupbox_threshold[sensor_name] = QGroupBox()
        self.groupbox_threshold[sensor_name].setObjectName(sensor_name)
        self.groupbox_threshold[sensor_name].setTitle('超阈值统计')
        self.groupbox_threshold[sensor_name].setAlignment(Qt.AlignHCenter)  # 标题居中
        self.groupbox_threshold[sensor_name].setFont(font)
        self.groupbox_threshold[sensor_name].setStyleSheet("background-color:white;")

        # 创建输入框
        threshold_layout = QHBoxLayout()
        self.threshold_inputs[sensor_name] = {}
        self.column_weigets[sensor_name] = {}
        self.show_count[sensor_name] = {}
        for param_name in param_names:
            column_weiget = self.add_columnlayout(sensor_name,param_name)

            threshold_layout.addWidget(column_weiget)


        self.groupbox_threshold[sensor_name].setLayout(threshold_layout)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.groupbox_threshold[sensor_name])

        # 创建垂直布局
        VLayout = QVBoxLayout()
        VLayout.addWidget(table)
        VLayout.addWidget(groupbox_4)
        VLayout.addWidget(scroll_area)

        # 创建一个 QWidget 作为标签页的内容
        widget = QWidget()
        widget.setLayout(VLayout)
        widget.setObjectName(sensor_name)
        # 为表格添加鼠标点击事件
        table.viewport().installEventFilter(self)

        # 为表格添加右键菜单
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)
        return widget

    def add_columnlayout(self,sensor_name,param_name):
        """添加阙值控件"""
        horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        column_weiget = QWidget()
        column_layout = QVBoxLayout()
        max_label = QLabel(f"{param_name} 最大阈值:")
        max_input = QLineEdit()
        max_count_text = QLabel("超最大阙值次数：")
        max_count_lable = QLabel("-1")  # 超最大阈值次数显示
        min_label = QLabel(f"{param_name} 最小阈值:")
        min_count_text = QLabel("超最小阙值次数：")
        min_count_lable = QLabel("-1")  # 超最小阈值次数显示
        min_input = QLineEdit()

        column_layout.addWidget(max_label)
        column_layout.addWidget(max_input)
        column_layout.addSpacerItem(horizontalSpacer)
        column_layout.addWidget(max_count_text)
        column_layout.addWidget(max_count_lable)
        column_layout.addSpacerItem(horizontalSpacer)
        column_layout.addWidget(min_label)
        column_layout.addWidget(min_input)
        column_layout.addSpacerItem(horizontalSpacer)
        column_layout.addWidget(min_count_text)
        column_layout.addWidget(min_count_lable)

        column_weiget.setLayout(column_layout)

        self.column_weigets[sensor_name][param_name] = column_weiget
        self.threshold_inputs[sensor_name][param_name] = {'max': max_input, 'min': min_input}
        self.show_count[sensor_name][param_name] = [max_count_lable, min_count_lable]
        return column_weiget

    def del_columnlayout(self, sensor_name, param_name):
        """删除阈值控件"""
        try:
            # 从 threshold_inputs 中删除输入控件
            if sensor_name in self.threshold_inputs and param_name in self.threshold_inputs[sensor_name]:
                del self.threshold_inputs[sensor_name][param_name]

            # 从 show_count 中删除计数标签
            if sensor_name in self.show_count and param_name in self.show_count[sensor_name]:
                del self.show_count[sensor_name][param_name]

            # 从 column_weigets 中删除控件
            if sensor_name in self.column_weigets and param_name in self.column_weigets[sensor_name]:
                column_weiget = self.column_weigets[sensor_name][param_name]
                if column_weiget and isinstance(column_weiget, QWidget):
                    try:
                        # # 从布局中移除 column_weiget
                        # layout = column_weiget.parent().layout()
                        # if layout:
                        #     layout.removeWidget(column_weiget)
                        # # 删除 column_weiget
                        # column_weiget.deleteLater()
                        del self.column_weigets[sensor_name][param_name]
                    except Exception as e:
                        print(f"Error removing widget: {e}")
        except Exception as e:
            self.show_message("删除阙值控件发生错误：",e)

    """ ---------------阙值统计 - --------------------"""

    def get_current_sensor_name(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            return current_tab.objectName()
        return None

    def show_threshold_count_for_current_tab(self, threshold_type):
        try:
            sensor_name = self.get_current_sensor_name()
            if sensor_name:
                self.show_threshold_count(sensor_name, threshold_type)
        except Exception as e:
            self.show_message(f"发生错误: {e}")

    def show_threshold_count(self, sensor_name, threshold_type):
        for param_name, inputs in self.threshold_inputs[sensor_name].items():
            if param_name not in self.show_count[sensor_name]:
                continue
            if threshold_type == 'max':
                count_label = self.show_count[sensor_name][param_name][0]
                threshold_value = inputs['max'].text()
            elif threshold_type == 'min':
                count_label = self.show_count[sensor_name][param_name][1]
                threshold_value = inputs['min'].text()
            else:
                return

            if threshold_value:
                threshold_value = float(threshold_value)
                data = self.get_table_data()
                if len(data) <= 3:
                    count_label.setText("-1")
                else:
                    data = data[3:]
                    if threshold_type == 'max':
                        count = sum(1 for row in data if float(row[param_name]) > threshold_value)
                    else:
                        count = sum(1 for row in data if float(row[param_name]) < threshold_value)
                    count_label.setText(str(count))
            else:
                count_label.setText("-1")

    """ ---------------表格操作 - --------------------"""

    def get_table_data(self):
        # 获取当前选中的标签页
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return {}

        # 获取当前标签页中的表格
        table = current_tab.findChild(QTableWidget)
        if not table:
            return {}

        # 获取表格的列名
        headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]

        # 存储数据的字典
        data = []

        # 遍历表格的每一行
        for row in range(table.rowCount()):
            row_data = {}
            for col, header in enumerate(headers):
                item = table.item(row, col)
                if item:
                    row_data[header] = item.text()
                else:
                    row_data[header] = ""
            data.append(row_data)

        return data

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
            if source is self.tab_widget.currentWidget().findChild(QTableWidget).viewport():
                index = self.tab_widget.currentWidget().findChild(QTableWidget).indexAt(event.pos())
                if index.isValid():
                    item = self.tab_widget.currentWidget().findChild(QTableWidget).item(index.row(), index.column())
                    if item:
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
            update_time = datetime.datetime.now().strftime(config.time_format)
            item = QTableWidgetItem(update_time)
            item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
            table.setItem(row_index, table.columnCount() - 3, item)

            # 添加编辑和删除按钮
            self.add_edit_button(table, row_index)
            self.add_delete_button(table, row_index)

            table.refresh_table()
            # self.refresh_table_form_time()

            # 确保表格显示到最后一行
            last_item = table.item(row_index, 0)
            table.scrollToItem(last_item)

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
        update_time = datetime.datetime.now().strftime(config.time_format)
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
        update_time = datetime.datetime.now().strftime(config.time_format)
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
            rows.sort(key=lambda x: x[table.columnCount() - 3])

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
            table.refresh_table()
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
    def import_table(self):
        super().import_table()

    def export_table(self):
        super().export_table('运维')
    # def export_table(self):
    #     """将表格中的数据导出为 XLSX 文件"""
    #     try:
    #         directory = QFileDialog.getExistingDirectory(self, "选择导出目录")
    #         if directory:
    #             try:
    #                 validate_directory(directory)
    #             except ValueError as e:
    #                 QMessageBox.critical(None, "错误", str(e))
    #                 return
    #
    #             for i in range(self.tab_widget.count()):
    #                 current_tab = self.tab_widget.widget(i)
    #                 table = current_tab.findChild(QTableWidget)
    #                 sensor_name = self.tab_widget.tabText(i)
    #                 cb_4 = current_tab.findChild(QComboBox, "cb_4")  # 获取当前标签页的 cb_4
    #                 cb_5 = current_tab.findChild(QComboBox, "cb_5")  # 获取当前标签页的 cb_5
    #
    #                 flodr_path = os.path.join(directory, sensor_name)
    #                 exists_path(flodr_path)
    #                 file_path = os.path.join(flodr_path, f"{cb_4.currentText()}.xlsx")
    #                 mode = cb_5.currentText()
    #                 if mode == "不保存":
    #                     continue
    #                 if not prompt_overwrite(file_path, cb_5.currentText()):
    #                     continue
    #
    #                 if mode == '覆盖':
    #                     data = []
    #                     for row in range(self.tRN, table.rowCount()):
    #                         for col in range(table.columnCount() - 3):  # 假设前几列为参数
    #                             item = table.item(row, col)
    #                             if item is not None:
    #                                 data.append({
    #                                     'id': row + 1,
    #                                     'name': table.horizontalHeaderItem(col).text(),
    #                                     'value': item.text(),
    #                                     'Time': table.item(row, table.columnCount() - 3).text()
    #                                 })
    #
    #                     df = pd.DataFrame(data, columns=['id', 'name', 'value', 'Time'])
    #                     df.to_excel(file_path, index=False)
    #                 elif mode == '追加':
    #                     existing_df = pd.read_excel(file_path)
    #                     new_data = []
    #                     df_row = 0
    #                     for row in range(self.tRN, table.rowCount()):
    #                         now_time = get_time_now(row)
    #                         for col in range(table.columnCount() - 3):  # 假设前几列为参数
    #                             item = table.item(row, col)
    #                             update_time_str = table.item(row, table.columnCount() - 3).text()
    #                             try:
    #                                 update_time = datetime.strptime(update_time_str, "%d/%m/%Y %H:%M:%S")
    #                             except:
    #                                 update_time = now_time
    #                             if item is not None:
    #                                 new_data.append({
    #                                     'id': df_row,
    #                                     'name': table.horizontalHeaderItem(col).text(),
    #                                     'value': item.text(),
    #                                     'Time': update_time
    #                                 })
    #                                 df_row += 1
    #
    #                     new_df = pd.DataFrame(new_data, columns=['id', 'name', 'value', 'Time'])
    #                     combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    #                     combined_df.to_excel(file_path, index=False)
    #
    #             QMessageBox.information(None, "导出成功", f"已将表格中的数据导出到指定目录")
    #     except Exception as e:
    #         QMessageBox.critical(None, "错误", f"导出文件时发生错误: {str(e)}")


    """ ----------------数据库操作---------------------"""
    def load_to_db(self):
        super().load_to_db()
        self.solt_table.refresh_table()
    def save_data(self):
        '''槽：保存数据'''
        # 请求用户确认
        reply = QMessageBox.question(
            None,
            "确认保存",
            f"您确定要将表格内容保存到数据库中吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return
        for index in range(self.tab_widget.count()):
            current_tab = self.tab_widget.widget(index)
            cb_5 = current_tab.findChild(QComboBox, "cb_5")
            if cb_5.currentText() == '不保存':
                continue
            elif cb_5.currentText() == '覆盖':
                self.save_to_db('覆盖', current_tab)
            elif cb_5.currentText() == '追加':
                self.save_to_db('追加', current_tab)
            else:
                # 清空
                pass
        QMessageBox.information(None, "保存成功", f"已将表格内容保存到数据库中")

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
                                       range(table.columnCount() - 3, table.columnCount()))

                    # 获取当前表格的列名
                    current_headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]

                    # 删除不再存在的列
                    for col in range(table.columnCount() - 1, -1, -1):
                        if table.horizontalHeaderItem(col).text() not in new_headers:
                            table.removeColumn(col)
                            # 删除对应的 column_layout
                            self.remove_threshold_layout(sensor_name, col)

                    # 添加新列
                    for header in new_headers:
                        if header not in current_headers:
                            table.insertColumn(table.columnCount() - 3)  # 在倒数第三列之前插入新列
                            item = QTableWidgetItem(header)
                            table.setHorizontalHeaderItem(table.columnCount() - 4, item)  # 设置新列的标题
                            # 添加对应的 column_layout
                            self.add_threshold_layout(sensor_name, header)

                    # 更新状态列表 cb_4
                    cb_4 = tab.findChild(QComboBox, 'cb_4')
                    if cb_4:
                        cb_4.clear()
                        cb_4.addItems(sensor['status_list'])

                    # self.update_threshold_controls(sensor_name, new_headers)

    def remove_threshold_layout(self, sensor_name, index):
        if sensor_name in self.groupbox_threshold:
            if isinstance(self.column_weigets[sensor_name], dict)  and index < len(self.column_weigets[sensor_name]):
                param_name = list(self.column_weigets[sensor_name].keys())[index]
                self.del_columnlayout(sensor_name,param_name)

    def add_threshold_layout(self, sensor_name, param_name):
        if sensor_name in self.groupbox_threshold:
            groupbox = self.groupbox_threshold[sensor_name]
            layout = groupbox.layout()
            column_weiget = self.add_columnlayout(sensor_name,param_name)

            layout.addWidget(column_weiget)

def main():
    app = QApplication(sys.argv)
    ex = DataCollectionAllWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
