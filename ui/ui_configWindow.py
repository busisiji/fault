import sys
import json

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, \
    QPushButton, QComboBox, QLineEdit, QMessageBox, QDialog, QLabel, QInputDialog, QTabWidget, QHBoxLayout, \
    QDialogButtonBox, QSizePolicy, QHeaderView, QFormLayout, QSpinBox
from PyQt5.QtCore import Qt

import config
from db.db_mysql import DB_MySQL
from ui.Base.baseWindow import BaseWindow
from qss.qss import btn_css

# 假设 DB_Mysql 类已经定义好了

numeric_schema = [
    ('sensor_name', 'VARCHAR(100) NOT NULL UNIQUE'),
    ('status_list', 'TEXT'),  # 存储 JSON 格式的状态列表
    ('params', 'TEXT'),  # 存储 JSON 格式的参数
    ('data_type', 'TEXT')  # 新增数据类型列
]

switch_schema = [
    ('sensor_name', 'VARCHAR(100) NOT NULL UNIQUE'),
    ('on_value', 'INT NOT NULL'),
    ('off_value', 'INT NOT NULL'),
    ('address', 'VARCHAR(100)'),
    ('data_type', 'TEXT')  # 新增数据类型列
]


class ConfigWindow(BaseWindow):
    """传感器配置界面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("传感器管理")
        self.setGeometry(100, 100, 800, 600)

        self.db = DB_MySQL()
        self.numeric_table_name = config.toname['数值传感器']
        self.switch_table_name = config.toname['开关传感器']
        with self.db:
            self.db.create_table(self.numeric_table_name, numeric_schema)
            self.db.create_table(self.switch_table_name, switch_schema)

        self.numeric_sensors = self.load_numeric_sensors_from_db()
        self.switch_sensors = self.load_switch_sensors_from_db()
        self.tables = {}

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.init_numeric_sensors_tab()
        self.init_switch_sensors_tab()

        button_layout = QVBoxLayout()
        self.init_buttons(button_layout)

        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.tab_widget.currentChanged.connect(self.tab_changed)

    def init_numeric_sensors_tab(self):
        numeric_sensors_tab = QWidget()
        numeric_sensors_layout = QVBoxLayout()
        numeric_sensors_subtabs = QTabWidget()
        numeric_sensors_layout.addWidget(numeric_sensors_subtabs)
        numeric_sensors_tab.setLayout(numeric_sensors_layout)

        self.tab_widget.addTab(numeric_sensors_tab, "数值型传感器")
        self.load_numeric_sensors(numeric_sensors_subtabs)

    def init_switch_sensors_tab(self):
        self.switch_table = QTableWidget()
        self.switch_table.setColumnCount(7)  # 增加两列
        self.switch_table.setHorizontalHeaderLabels(['传感器名称', '开启值', '关闭值', '地址','数据类型', '编辑', '删除'])
        self.switch_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.switch_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.switch_table.verticalHeader().setDefaultSectionSize(40)

        # 设置列宽度自动扩展
        header = self.switch_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(self.switch_table.columnCount() - 2, QHeaderView.Fixed)
        header.setSectionResizeMode(self.switch_table.columnCount() - 1, QHeaderView.Fixed)

        self.load_switch_table()
        self.tab_widget.addTab(self.switch_table, "开关型传感器")

    def init_buttons(self, layout):
        buttons = [
            ('修改传感器', self.modify_sensor),
            ('添加传感器', self.add_sensor),
            ('删除传感器', self.delete_sensor),
            ('修改状态', self.modify_status),
            ('添加状态', self.add_status_to_selected_sensor),
            ('删除状态', self.delete_status_from_selected_sensor),
            ('添加参数', self.add_param_to_selected_sensor),
            ('保存配置', self.save_configuration),
        ]

        # 辅助函数：创建并设置按钮
        def create_button(text, callback):
            btn = QPushButton()
            btn.setText(text)
            btn_css(btn)
            btn.clicked.connect(lambda checked, cb=callback: self.safe_call(cb, text))
            # btn.setMinimumSize(200, 30)
            return btn

        # 创建按钮布局
        button_layouts = [
            QHBoxLayout(),
            QHBoxLayout(),
            QHBoxLayout()
        ]

        # 添加按钮到布局
        for i, (text, callback) in enumerate(buttons):
            button_layouts[i // 3].addWidget(create_button(text, callback))

        for button_layout in button_layouts:
            layout.addLayout(button_layout)

    def add_button(self, text, callback, layout):
        button = QPushButton(text)
        btn_css(button)
        button.clicked.connect(callback)
        layout.addWidget(button)
        button.setMinimumSize(200, 30)
        return button

    def add_button_to_table(self, text, callback, table, row, column):
        button = QPushButton(text)
        btn_css(button)
        button.clicked.connect(callback)
        table.setCellWidget(row, column, button)
        return button

    def add_button_to_switch_table(self, text, callback, table, row, column, sensor_name):
        button = QPushButton(text)
        btn_css(button)
        button.clicked.connect(lambda: callback(row, sensor_name))
        table.setCellWidget(row, column, button)
        return button

    def show_error_message(self, title, message):
        QMessageBox.warning(self, title, message)

    def load_numeric_sensors_from_db(self):
        sensors = []
        try:
            with self.db:
                for sensor in self.db.select_data(self.numeric_table_name, columns='*'):
                    sensors.append({
                        'sensor_name': sensor['sensor_name'],
                        'status_list': json.loads(sensor['status_list']),
                        'params': json.loads(sensor['params']),
                        'data_type': json.loads(sensor['data_type']) if sensor['data_type'] else 'unit16',
                    })
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误: {e}")
        return sensors

    def load_switch_sensors_from_db(self):
        sensors = config.get_sensors('开关传感器')
        return sensors

    def find_sensor_by_name(self, sensor_name, sensor_type='numeric'):
        if sensor_type == 'numeric':
            return next((s for s in self.numeric_sensors if s['sensor_name'] == sensor_name), None)
        elif sensor_type == 'switch':
            return next((s for s in self.switch_sensors if s['sensor_name'] == sensor_name), None)

    def update_numeric_sensor_table(self, sensor_name):
        """读取数据库写入数值传感器参数表格配置"""
        sensor = self.find_sensor_by_name(sensor_name, 'numeric')
        if sensor:
            params_table = self.tables.get(sensor_name, QTableWidget())
            params_table.setRowCount(0)
            for row, (param, value) in enumerate(sensor['params'].items()):
                params_table.insertRow(row)
                param_item = QTableWidgetItem(param)
                param_item.setTextAlignment(Qt.AlignCenter)
                params_table.setItem(row, 0, param_item)

                value_item = QTableWidgetItem(str(value))
                value_item.setTextAlignment(Qt.AlignCenter)
                params_table.setItem(row, 1, value_item)

                # 添加数据类型列
                data_type_combobox = QComboBox()
                data_type_combobox.addItems(['uint16', 'uint32', 'float32', 'bool'])
                data_type_combobox.setCurrentText(sensor['data_type'][row] if row < len(sensor['data_type']) else 'uint16')
                params_table.setCellWidget(row, 2, data_type_combobox)

                self.add_button_to_table("编辑", lambda _, r=row, sn=sensor_name: self.edit_param(r, sn), params_table, row, 3)
                self.add_button_to_table("删除", lambda _, r=row, sn=sensor_name: self.delete_param(r, sn), params_table, row, 4)
        else:
            QMessageBox.critical(self, "错误", "未找到指定传感器。")

    def load_numeric_sensors(self, subtabs):
       """读取数据库写入数值传感器配置"""
       current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
       selected_tab_index = current_tab.currentIndex()

       subtabs.clear()
       for item in self.numeric_sensors:
           if 'status_list' in item and 'params' in item:
               sensor_name = item['sensor_name']
               tab = QWidget()
               layout = QVBoxLayout()
               params_table = QTableWidget()
               params_table.setColumnCount(5)  # 增加一列
               params_table.setHorizontalHeaderLabels(["参数", "地址", "数据类型", "编辑", "删除"])
               params_table.setEditTriggers(QTableWidget.NoEditTriggers)
               params_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
               params_table.verticalHeader().setDefaultSectionSize(40)

               # 设置列宽度自动扩展
               header = params_table.horizontalHeader()
               header.setSectionResizeMode(QHeaderView.Stretch)
               # 设置最后三列的大小模式为固定
               header.setSectionResizeMode(params_table.columnCount() - 3, QHeaderView.Fixed)
               header.setSectionResizeMode(params_table.columnCount() - 2, QHeaderView.Fixed)
               header.setSectionResizeMode(params_table.columnCount() - 1, QHeaderView.Fixed)

               layout.addWidget(params_table)

               for row, (param, value) in enumerate(item['params'].items()):
                   params_table.insertRow(row)
                   param_item = QTableWidgetItem(param)
                   param_item.setTextAlignment(Qt.AlignCenter)
                   params_table.setItem(row, 0, param_item)

                   value_item = QTableWidgetItem(str(value))
                   value_item.setTextAlignment(Qt.AlignCenter)
                   params_table.setItem(row, 1, value_item)

                   # 添加数据类型列
                   data_type_combobox = QComboBox()
                   data_type_combobox.addItems(['uint16', 'uint32', 'float32', 'bool'])
                   data_type_combobox.setCurrentText(item['data_type'][row] if row < len(item['data_type']) else 'uint16')
                   params_table.setCellWidget(row, 2, data_type_combobox)

                   self.add_button_to_table("编辑", lambda _, r=row, sn=sensor_name: self.edit_param(r, sn), params_table, row, 3)
                   self.add_button_to_table("删除", lambda _, r=row, sn=sensor_name: self.delete_param(r, sn), params_table, row, 4)

               status_layout = QHBoxLayout()
               status_label = QLabel("状态列表:")
               status_combo = QComboBox()
               status_combo.addItems(item['status_list'])
               status_layout.addWidget(status_label)
               status_layout.addWidget(status_combo)
               layout.addLayout(status_layout)

               tab.setLayout(layout)
               subtabs.addTab(tab, sensor_name)
               self.tables[sensor_name] = params_table
       current_tab.setCurrentIndex(selected_tab_index)

    def load_switch_table(self):
       self.switch_table.setRowCount(0)
       for item in self.switch_sensors:
           if 'on_value' in item and 'off_value' in item:
               row = self.switch_table.rowCount()
               self.switch_table.insertRow(row)
               param_item = QTableWidgetItem(item['sensor_name'])
               param_item.setTextAlignment(Qt.AlignCenter)
               self.switch_table.setItem(row, 0, param_item)

               on_value_item = QTableWidgetItem(str(item['on_value']))
               on_value_item.setTextAlignment(Qt.AlignCenter)
               self.switch_table.setItem(row, 1, on_value_item)

               off_value_item = QTableWidgetItem(str(item['off_value']))
               off_value_item.setTextAlignment(Qt.AlignCenter)
               self.switch_table.setItem(row, 2, off_value_item)

               address_value_item = QTableWidgetItem(str(item['address']))
               address_value_item.setTextAlignment(Qt.AlignCenter)
               self.switch_table.setItem(row, 3, address_value_item)

               # 添加数据类型列
               data_type_combobox = QComboBox()
               data_type_combobox.addItems(['bool'])
               data_type_combobox.setCurrentText('bool')
               self.switch_table.setCellWidget(row, 4, data_type_combobox)

               self.add_button_to_switch_table("编辑", self.edit_switch_sensor, self.switch_table, row, 5, item['sensor_name'])
               self.add_button_to_switch_table("删除", self.delete_switch_sensor, self.switch_table, row, 6, item['sensor_name'])



    def add_sensor(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            self.add_numeric_sensor()
        elif current_tab_index == 1:
            self.add_switch_sensor()

    def add_numeric_sensor(self):
        """添加数值传感器"""
        sensor_name, ok = QInputDialog.getText(self, "添加数值型传感器", "请输入传感器名称:")
        if not ok or not sensor_name.strip():
            QMessageBox.warning(self, "警告", "传感器名称已存在或输入为空。")
            return

        if any(s['sensor_name'] == sensor_name for s in self.numeric_sensors):
            QMessageBox.warning(self, "警告", "传感器名称已存在。")
            return

        dialog = ModifyNumericSensorDialog(self)
        dialog.sensor_name.setText(sensor_name)
        if dialog.exec_() == QDialog.Accepted:
            new_sensor = {
                'status_list': [status.strip() for status in dialog.status_list.text().split(',') if status.strip()],
                'params': dialog.params,
                'data_type': list(dialog.get_data_type())  # 调用 get_data_type 方法获取数据类型
            }
            new_sensor['sensor_name'] = sensor_name
            self.numeric_sensors.append(new_sensor)
            self.update_sensor_list()
            QMessageBox.information(self, "成功", f"数值型传感器 {sensor_name} 已成功添加。")


    def add_switch_sensor(self):
        """添加开关传感器"""
        dialog = ModifySwitchSensorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            sensor_name = dialog.sensor_name.text()
            address = dialog.address.value()  # 获取 QSpinBox 的值
            if sensor_name:
                # 检查传感器名称是否已存在
                sensor_name_exists = any(s['sensor_name'] == sensor_name for s in self.switch_sensors)
                # 检查地址是否已存在
                address_exists = any(str(s['address']) == str(address) for s in self.switch_sensors if 'address' in s)
                if not sensor_name_exists and not address_exists:
                    new_sensor = {
                        'sensor_name': sensor_name,
                        'on_value': dialog.on_value.currentText() == 'True',
                        'off_value': dialog.off_value.currentText() == 'True',
                        'address': address,
                    }
                    self.switch_sensors.append(new_sensor)
                    self.load_switch_table()  # 重新加载表格以显示新添加的传感器
                    QMessageBox.information(self, "成功", f"开关型传感器 {sensor_name} 已成功添加。")
                else:
                    if sensor_name_exists:
                        QMessageBox.warning(self, "警告", "传感器名称已存在。")
                    if address_exists:
                        QMessageBox.warning(self, "警告", "地址已存在。")
            else:
                QMessageBox.warning(self, "警告", "请输入传感器名称。")






    def modify_sensor(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            self.modify_numeric_sensor_name()
        elif current_tab_index == 1:
            self.modify_switch_sensor_name()


    def modify_numeric_sensor_name(self):
        current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
        selected_tab_index = current_tab.currentIndex()
        if selected_tab_index >= 0:
            sensor_name = current_tab.tabText(selected_tab_index)
            sensor = self.find_sensor_by_name(sensor_name, 'numeric')
            if sensor:
                new_sensor_name, ok = QInputDialog.getText(self, "修改传感器名称", "请输入新的传感器名称:", text=sensor_name)
                if ok and not any(s['sensor_name'] == new_sensor_name for s in self.numeric_sensors):
                    sensor['sensor_name'] = new_sensor_name
                    self.load_numeric_sensors(current_tab)
                    QMessageBox.information(self, "成功", f"传感器 {sensor_name} 的名称已成功修改为 {new_sensor_name}。")
                else:
                    QMessageBox.warning(self, "警告", "新传感器名称已存在或输入为空。")
            else:
                QMessageBox.critical(self, "错误", "未找到指定传感器。")
        else:
            QMessageBox.warning(self, "警告", "请选择一个传感器进行修改。")


    def modify_switch_sensor_name(self):
        selected_row = self.switch_table.currentRow()
        if selected_row >= 0:
            sensor_name = self.switch_table.item(selected_row, 0).text()
            sensor = self.find_sensor_by_name(sensor_name, 'switch')
            if sensor:
                new_sensor_name, ok = QInputDialog.getText(self, "修改传感器名称", "请输入新的传感器名称:",
                                                           text=sensor_name)
                if ok and not any(s['sensor_name'] == new_sensor_name for s in self.switch_sensors):
                    sensor['sensor_name'] = new_sensor_name
                    self.load_switch_table()
                    QMessageBox.information(self, "成功", f"传感器 {sensor_name} 的名称已成功修改为 {new_sensor_name}。")
                else:
                    QMessageBox.warning(self, "警告", "新传感器名称已存在或输入为空。")
            else:
                QMessageBox.critical(self, "错误", "未找到指定传感器。")
        else:
            QMessageBox.warning(self, "警告", "请选择一个传感器进行修改。")


    def edit_switch_sensor(self, row, sensor_name):
        sensor = next((s for s in self.switch_sensors if s['sensor_name'] == sensor_name), None)
        if sensor:
            dialog = ModifySwitchSensorDialog(self)
            dialog.sensor_name.setText(sensor['sensor_name'])
            dialog.on_value.setCurrentText(str(sensor['on_value']))  # 使用 setCurrentText 方法
            dialog.off_value.setCurrentText(str(sensor['off_value']))  # 使用 setCurrentText 方法
            dialog.address.setValue(int(sensor['address']))  # 使用 setValue 方法
            if dialog.exec_() == QDialog.Accepted:
                sensor['sensor_name'] = dialog.sensor_name.text()
                sensor['on_value'] = dialog.on_value.currentText() == 'True'  # 使用 currentText 方法
                sensor['off_value'] = dialog.off_value.currentText() == 'True'  # 使用 currentText 方法
                sensor['address'] = str(dialog.address.value())  # 更新地址
                self.load_switch_table()
                QMessageBox.information(self, "成功", f"开关型传感器 {sensor_name} 已成功修改。")
        else:
            QMessageBox.critical(self, "错误", "未找到指定传感器。")



    def delete_sensor(self):
        reply = QMessageBox.question(
            None,
            "确认删除",
            f"您确定要删除该传感器吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            current_tab_index = self.tab_widget.currentIndex()
            if current_tab_index == 0:
                self.delete_numeric_sensor()
            elif current_tab_index == 1:
                self.delete_switch_sensor()

    def delete_numeric_sensor(self):
        current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
        selected_tab_index = current_tab.currentIndex()
        if selected_tab_index >= 0:
            sensor_name = current_tab.tabText(selected_tab_index)
            sensor = self.find_sensor_by_name(sensor_name, 'numeric')
            if sensor:
                self.numeric_sensors.remove(sensor)
                self.load_numeric_sensors(current_tab)
                QMessageBox.information(self, "成功", f"数值型传感器 {sensor_name} 已成功删除。")
            else:
                QMessageBox.critical(self, "错误", "未找到指定传感器。")
        else:
            QMessageBox.warning(self, "警告", "请选择一个传感器进行删除。")


    def delete_switch_sensor(self, row, sensor_name):
        sensor = self.find_sensor_by_name(sensor_name, 'switch')
        if sensor:
            self.switch_sensors.remove(sensor)
            self.load_switch_table()
            QMessageBox.information(self, "成功", f"开关型传感器 {sensor_name} 已成功删除。")
        else:
            QMessageBox.critical(self, "错误", "未找到指定传感器。")

    def add_param_to_selected_sensor(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
            selected_tab_index = current_tab.currentIndex()
            if selected_tab_index >= 0:
                sensor_name = current_tab.tabText(selected_tab_index)
                sensor = next((s for s in self.numeric_sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    param_name, ok = QInputDialog.getText(self, "添加参数", "参数名称:")
                    if ok:
                        param_value, ok = QInputDialog.getInt(self, "添加参数", "参数地址:")
                        if ok and param_name not in sensor['params'] and param_value not in sensor['params'].values():
                            sensor['params'][param_name] = param_value
                            self.load_numeric_sensors(current_tab)
                            # QMessageBox.information(self, "成功",
                                                    # f"参数 {param_name} 已成功添加到传感器 {sensor_name}。")
                        else:
                            QMessageBox.warning(self, "警告", "参数名称或地址已存在或输入为空。")
                    else:
                        QMessageBox.critical(self, "错误", "未找到指定传感器。")
                else:
                    QMessageBox.warning(self, "警告", "请选择一个传感器进行操作。")
            else:
                QMessageBox.warning(self, "警告", "当前选项卡不支持此操作。")
        elif current_tab_index == 1:
            self.add_switch_sensor()

    def edit_param(self, row, sensor_name):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
            selected_tab_index = current_tab.currentIndex()
            if selected_tab_index >= 0:
                sensor = next((s for s in self.numeric_sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    param_name = self.tables[sensor_name].item(row, 0).text()
                    param_value = int(self.tables[sensor_name].item(row, 1).text())

                    # 编辑参数名称
                    new_param_name, ok_name = QInputDialog.getText(self, "编辑参数名称", "参数名称:", text=param_name)
                    if ok_name and new_param_name:
                        # 检查新参数名称是否已存在
                        if new_param_name in sensor['params']:
                            QMessageBox.warning(self, "警告", "参数名称已存在。")
                            return

                        # 更新传感器数据
                        sensor['params'][new_param_name] = sensor['params'].pop(param_name)

                        # 更新表格
                        self.tables[sensor_name].setItem(row, 0, QTableWidgetItem(new_param_name))

                    # 编辑参数值
                    new_param_value, ok_value = QInputDialog.getInt(self, "编辑参数", "参数地址:", value=param_value)
                    if ok_value:
                        sensor['params'][new_param_name] = new_param_value
                        self.tables[sensor_name].setItem(row, 1, QTableWidgetItem(str(new_param_value)))

                    self.load_numeric_sensors(current_tab)
                    QMessageBox.information(self, "成功", f"参数 {new_param_name} 已成功更新。")
                else:
                    QMessageBox.critical(self, "错误", "未找到指定传感器。")
            else:
                QMessageBox.warning(self, "警告", "请选择一个传感器进行操作。")
        else:
            QMessageBox.warning(self, "警告", "当前选项卡不支持此操作。")


    def delete_param(self, row, sensor_name):
        """删除数值传感器"""
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
            selected_tab_index = current_tab.currentIndex()
            if selected_tab_index >= 0:
                sensor = next((s for s in self.numeric_sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    param_name = self.tables[sensor_name].item(row, 0).text()
                    del sensor['params'][param_name]
                    self.load_numeric_sensors(current_tab)
                    QMessageBox.information(self, "成功", f"参数 {param_name} 已成功删除。")
                else:
                    QMessageBox.critical(self, "错误", "未找到指定传感器。")
            else:
                QMessageBox.warning(self, "警告", "请选择一个传感器进行操作。")
        else:
            QMessageBox.warning(self, "警告", "当前选项卡不支持此操作。")

    def add_status_to_selected_sensor(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
            selected_tab_index = current_tab.currentIndex()
            if selected_tab_index >= 0:
                sensor_name = current_tab.tabText(selected_tab_index)
                sensor = next((s for s in self.numeric_sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    status, ok = QInputDialog.getText(self, "添加状态", "状态名称:")
                    if ok:
                        # 检查状态名称是否为空
                        if not status.strip():
                            QMessageBox.warning(self, "警告", "状态名称不能为空。")
                            return

                        # 检查状态名称是否已存在
                        if status not in sensor['status_list']:
                            sensor['status_list'].append(status)
                            self.load_numeric_sensors(current_tab)
                            QMessageBox.information(self, "成功", f"状态 {status} 已成功添加到传感器 {sensor_name}。")
                        else:
                            QMessageBox.warning(self, "警告", "状态已存在。")
                    else:
                        QMessageBox.warning(self, "警告", "取消添加状态。")
                else:
                    QMessageBox.critical(self, "错误", "未找到指定传感器。")
            else:
                QMessageBox.warning(self, "警告", "请选择一个传感器进行操作。")
        else:
            QMessageBox.warning(self, "警告", "当前选项卡不支持此操作。")


    def delete_status_from_selected_sensor(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
            selected_tab_index = current_tab.currentIndex()
            if selected_tab_index >= 0:
                sensor_name = current_tab.tabText(selected_tab_index)
                sensor = next((s for s in self.numeric_sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    status, ok = QInputDialog.getItem(self, "删除状态", "选择要删除的状态:",
                                                      sensor['status_list'], editable=False)
                    if ok:
                        sensor['status_list'].remove(status)
                        self.load_numeric_sensors(current_tab)
                        QMessageBox.information(self, "成功", f"状态 {status} 已成功删除。")
                else:
                    QMessageBox.critical(self, "错误", "未找到指定传感器。")
            else:
                QMessageBox.warning(self, "警告", "请选择一个传感器进行操作。")
        else:
            QMessageBox.warning(self, "警告", "当前选项卡不支持此操作。")

    def modify_status(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
            selected_tab_index = current_tab.currentIndex()
            if selected_tab_index >= 0:
                sensor_name = current_tab.tabText(selected_tab_index)
                sensor = next((s for s in self.numeric_sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    status, ok = QInputDialog.getItem(self, "修改状态", "选择要修改的状态:",
                                                      sensor['status_list'], editable=False)
                    if ok:
                        new_status, ok = QInputDialog.getText(self, "修改状态", "新的状态名称:",
                                                              text=status)
                        if ok and new_status not in sensor['status_list']:
                            sensor['status_list'].remove(status)
                            sensor['status_list'].append(new_status)
                            self.load_numeric_sensors(current_tab)
                            QMessageBox.information(self, "成功",
                                                    f"状态 {status} 已成功修改为 {new_status}。")
                        else:
                            QMessageBox.warning(self, "警告", "新状态已存在或输入为空。")
                else:
                    QMessageBox.critical(self, "错误", "未找到指定传感器。")
            else:
                QMessageBox.warning(self, "警告", "请选择一个传感器进行操作。")
        else:
            QMessageBox.warning(self, "警告", "当前选项卡不支持此操作。")

    def update_sensor_list(self):
        self.load_numeric_sensors(self.tab_widget.widget(0).layout().itemAt(0).widget())
        self.load_switch_table()

    def tab_changed(self, index):
        pass
        # if index == 0:
        #     self.modify_sensor_button.show()
        #     self.add_sensor_button.show()
        #     self.delete_sensor_button.show()
        #     self.modify_status_button.show()
        #     self.add_status_button.show()
        #     self.delete_status_button.show()
        # elif index == 1:
        #     self.modify_sensor_button.hide()
        #     self.add_sensor_button.hide()
        #     self.delete_sensor_button.hide()
        #     self.modify_status_button.hide()
        #     self.add_status_button.hide()
        #     self.delete_status_button.hide()

    def save_configuration(self):
        """保存当前界面的传感器配置到数据库"""
        try:
            with self.db:
                # 开始事务
                self.db.begin_transaction()

                # 获取数据库中所有传感器的名称
                numeric_sensors_in_db = {row['sensor_name'] for row in self.db.select_data(self.numeric_table_name, columns=['sensor_name'])}
                switch_sensors_in_db = {row['sensor_name'] for row in self.db.select_data(self.switch_table_name, columns=['sensor_name'])}

                # 从界面上获取当前的传感器配置
                current_numeric_sensors = self.get_numeric_sensors_from_ui()
                current_switch_sensors = self.get_switch_sensors_from_ui()

                # 计算不再存在的传感器名称
                numeric_sensors_to_delete = numeric_sensors_in_db - {sensor['sensor_name'] for sensor in current_numeric_sensors}
                switch_sensors_to_delete = switch_sensors_in_db - {sensor['sensor_name'] for sensor in current_switch_sensors}

                # 删除不再存在的数值型传感器
                for sensor_name in numeric_sensors_to_delete:
                    self.db.delete_data(self.numeric_table_name, f"sensor_name = '{sensor_name}'")

                # 删除不再存在的开关型传感器
                for sensor_name in switch_sensors_to_delete:
                    self.db.delete_data(self.switch_table_name, f"sensor_name = '{sensor_name}'")

                # 保存数值型传感器配置
                for sensor in current_numeric_sensors:
                    sensor_name = sensor['sensor_name']
                    status_list = json.dumps(sensor['status_list'])
                    params = json.dumps(sensor['params'])
                    data_type = json.dumps(sensor['data_type'])

                    # 检查传感器是否存在，如果存在则更新，否则插入
                    if self.db.select_data(self.numeric_table_name, condition=f"sensor_name = '{sensor_name}'"):
                        self.db.update_data(self.numeric_table_name,
                                            {'status_list': status_list, 'params': params, 'data_type': data_type},
                                            f"sensor_name = '{sensor_name}'")
                    else:
                        self.db.insert_data(self.numeric_table_name,
                                            {'sensor_name': sensor_name, 'status_list': status_list, 'params': params, 'data_type': data_type})

                # 保存开关型传感器配置
                for sensor in current_switch_sensors:
                    sensor_name = sensor['sensor_name']
                    on_value = sensor['on_value']
                    off_value = sensor['off_value']
                    address = sensor['address']
                    data_type = 'bool'  # 开关型传感器的数据类型固定为 bool

                    # 检查传感器是否存在，如果存在则更新，否则插入
                    if self.db.select_data(self.switch_table_name, condition=f"sensor_name = '{sensor_name}'"):
                        self.db.update_data(self.switch_table_name,
                                            {'on_value': on_value, 'off_value': off_value, 'address': address, 'data_type': data_type},
                                            f"sensor_name = '{sensor_name}'")
                    else:
                        self.db.insert_data(self.switch_table_name,
                                            {'sensor_name': sensor_name, 'on_value': on_value, 'off_value': off_value, 'address': address, 'data_type': data_type})
                # 提交事务
                self.db.commit_transaction()
                self.parent._single_update_ui.emit()

                QMessageBox.information(self, "成功", "配置已成功保存。")
        except Exception as e:
            # 回滚事务
            self.parent.setRun()
            self.db.rollback_transaction()
            QMessageBox.critical(self, "错误", f"保存配置时发生错误：{str(e)}")

    def get_numeric_sensors_from_ui(self):
        """从界面上获取数值型传感器配置"""
        numeric_sensors = []

        # 获取数值传感器的主标签页
        numeric_sensors_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()

        if isinstance(numeric_sensors_tab, QTabWidget):
            # 遍历数值传感器主标签页中的每个子标签页
            for j in range(numeric_sensors_tab.count()):
                subtab = numeric_sensors_tab.widget(j)
                if isinstance(subtab, QWidget):
                    params_table = subtab.findChild(QTableWidget)
                    status_layout = subtab.findChild(QHBoxLayout)

                    if params_table and status_layout:
                        sensor_name = numeric_sensors_tab.tabText(j)
                        status_combo = status_layout.itemAt(1).widget()
                        status_list = [status.strip() for i in range(status_combo.count()) for status in status_combo.itemText(i).split(',') if status.strip()]
                        params = {}
                        data_type = []
                        for row in range(params_table.rowCount()):
                            param = params_table.item(row, 0).text()
                            value = params_table.item(row, 1).text()
                            data_type_combobox = params_table.cellWidget(row, 2)
                            data_type.append(data_type_combobox.currentText())
                            params[param] = value

                        numeric_sensors.append({
                            'sensor_name': sensor_name,
                            'status_list': status_list,
                            'params': params,
                            'data_type': data_type
                        })

        return numeric_sensors


    def get_switch_sensors_from_ui(self):
        """从界面上获取开关型传感器配置"""
        switch_sensors = []
        for row in range(self.switch_table.rowCount()):
            sensor_name = self.switch_table.item(row, 0).text()
            on_value =1 if self.switch_table.item(row, 1).text() == 'True' else 0
            off_value = 1 if self.switch_table.item(row, 2).text() == 'True' else 0
            address = self.switch_table.item(row, 3).text()

            switch_sensors.append({
                'sensor_name': sensor_name,
                'on_value': on_value,
                'off_value': off_value,
                'address': address,
                'data_type': 'bool'
            })
        return switch_sensors





class ModifyNumericSensorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.sensor_name = QLineEdit(self)
        layout.addWidget(QLabel("传感器名称:"))
        layout.addWidget(self.sensor_name)

        self.status_list = QLineEdit(self)
        layout.addWidget(QLabel("状态列表 (逗号分隔):"))
        layout.addWidget(self.status_list)

        self.params = {}
        self.data_types = {}
        self.param_layout = QVBoxLayout()
        layout.addWidget(QLabel("参数:"))
        layout.addLayout(self.param_layout)

        self.add_param_button = QPushButton("添加参数")
        self.add_param_button.clicked.connect(self.add_param)
        layout.addWidget(self.add_param_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def add_param(self):
        param_name, ok = QInputDialog.getText(self, "添加参数", "请输入参数名称:")
        if ok:
            param_value, ok = QInputDialog.getInt(self, "添加参数", f"请输入 {param_name} 的值:")
            if ok:
                data_type, ok = QInputDialog.getItem(self, "选择数据类型", "请选择数据类型:", ['uint16', 'uint32', 'float32', 'bool'], 0, False)
                if ok:
                    self.params[param_name] = param_value
                    self.data_types[param_name] = data_type
                    label = QLabel(f"{param_name}: {param_value} ({data_type})")
                    self.param_layout.addWidget(label)

    def get_params(self):
        return self.params

    def get_data_type(self):
        return self.data_types



class ModifySwitchSensorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改开关型传感器")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.form_layout = QFormLayout()

        self.sensor_name = QLineEdit(self)
        self.form_layout.addRow(QLabel("传感器名称:"), self.sensor_name)

        self.on_value = QComboBox(self)
        self.on_value.addItems(['False', 'True'])
        self.on_value.setCurrentText('True')
        self.form_layout.addRow(QLabel("开启值:"), self.on_value)

        self.off_value = QComboBox(self)
        self.off_value.addItems(['False', 'True'])
        self.off_value.setCurrentText('False')
        self.form_layout.addRow(QLabel("关闭值:"), self.off_value)

        self.address = QSpinBox(self)
        self.address.setRange(0, 9999)  # 设置地址的合理范围
        self.form_layout.addRow(QLabel("地址:"), self.address)

        layout.addLayout(self.form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)


    def update_off_value(self, index):
        on_value = self.on_value.currentText()
        if on_value == 'True':
            self.off_value.setCurrentText('False')
        else:
            self.off_value.setCurrentText('True')

    def update_on_value(self, index):
        off_value = self.off_value.currentText()
        if off_value == 'True':
            self.on_value.setCurrentText('False')
        else:
            self.on_value.setCurrentText('True')

    def accept(self):
        on_value = self.on_value.currentText().strip()
        off_value = self.off_value.currentText().strip()

        # 检查开启值和关闭值不能相同
        if on_value == off_value:
            QMessageBox.warning(self, "警告", "开启值和关闭值不能相同。")
        if not self.sensor_name.text():
            QMessageBox.warning(self, "警告", "请输入传感器名称。")

        super().accept()






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())
