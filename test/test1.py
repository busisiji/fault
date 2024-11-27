import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, \
    QPushButton, QComboBox, QLineEdit, QMessageBox, QDialog, QLabel, QInputDialog, QTabWidget, QHBoxLayout, \
    QDialogButtonBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

import config
from db.db_mysql import DB_MySQL

# 假设 DB_Mysql 类已经定义好了

numeric_schema = [
    ('sensor_name', 'VARCHAR(100) NOT NULL UNIQUE'),
    ('status_list', 'TEXT'),  # 存储 JSON 格式的状态列表
    ('params', 'TEXT')  # 存储 JSON 格式的参数
]

switch_schema = [
    ('sensor_name', 'VARCHAR(100) NOT NULL UNIQUE'),
    ('on_value', 'INT NOT NULL'),
    ('off_value', 'INT NOT NULL'),
    ('address', 'VARCHAR(100)')  # 新增地址字段
]

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("传感器管理")
        self.setGeometry(100, 100, 800, 600)

        self.db = DB_MySQL()
        self.numeric_table_name = config.toname['数值传感器']
        self.switch_table_name = config.toname['开关传感器']
        with self.db:
            self.db.create_table(self.numeric_table_name, numeric_schema)
            self.db.create_table(self.switch_table_name, switch_schema)

        self.sensors = self.load_sensors_from_db()
        self.tables = {}

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.init_numeric_sensors_tab()
        self.init_switch_sensors_tab()

        button_layout = QVBoxLayout()
        self.init_buttons(button_layout)

        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(button_layout)

        central_widget.setLayout(main_layout)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.tab_changed(0)

    def init_numeric_sensors_tab(self):
        numeric_sensors_tab = QWidget()
        numeric_sensors_layout = QVBoxLayout()
        numeric_sensors_subtabs = QTabWidget()
        numeric_sensors_layout.addWidget(numeric_sensors_subtabs)
        numeric_sensors_tab.setLayout(numeric_sensors_layout)

        self.load_numeric_sensors(numeric_sensors_subtabs)
        self.tab_widget.addTab(numeric_sensors_tab, "数值型传感器")

    def init_switch_sensors_tab(self):
        self.switch_table = QTableWidget()
        self.switch_table.setColumnCount(6)  # 增加两列
        self.switch_table.setHorizontalHeaderLabels(['传感器名称', '开启值', '关闭值', '地址', '编辑', '删除'])
        self.load_switch_table()
        self.tab_widget.addTab(self.switch_table, "开关型传感器")

    def init_buttons(self, layout):
        add_delete_sensor_layout = QHBoxLayout()
        self.modify_sensor_button = self.add_button("修改传感器", self.modify_sensor, add_delete_sensor_layout)
        self.add_sensor_button =self.add_button("添加传感器", self.add_sensor, add_delete_sensor_layout)
        self.delete_sensor_button = self.add_button("删除传感器", self.delete_sensor, add_delete_sensor_layout)
        layout.addLayout(add_delete_sensor_layout)

        add_delete_status_layout = QHBoxLayout()
        self.modify_status_button = self.add_button("修改状态", self.modify_status, add_delete_status_layout)
        self.add_status_button = self.add_button("添加状态", self.add_status_to_selected_sensor, add_delete_status_layout)
        self.delete_status_button = self.add_button("删除状态", self.delete_status_from_selected_sensor, add_delete_status_layout)
        layout.addLayout(add_delete_status_layout)

        other_buttons_layout = QHBoxLayout()
        self.add_param_button = self.add_button("添加参数", self.add_param_to_selected_sensor, other_buttons_layout)
        self.save_config_button = self.add_button("保存配置", self.save_configuration, other_buttons_layout)
        layout.addLayout(other_buttons_layout)

    def add_button(self, text, callback, layout):
        button = QPushButton(text)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def add_button_to_table(self, text, callback, table, row, column):
        button = QPushButton(text)
        button.clicked.connect(callback)
        table.setCellWidget(row, column, button)
        return button

    def add_button_to_switch_table(self, text, callback, table, row, column, sensor_name):
        button = QPushButton(text)
        button.clicked.connect(lambda: callback(row, sensor_name))
        table.setCellWidget(row, column, button)
        return button

    def show_error_message(self, title, message):
        QMessageBox.warning(self, title, message)

    def load_sensors_from_db(self):
        sensors = []
        with self.db:
            for table_name, schema in [(self.numeric_table_name, numeric_schema), (self.switch_table_name, switch_schema)]:
                for sensor in self.db.select_data(table_name, columns='*'):
                    if any(column[0] == 'status_list' for column in schema) and any(column[0] == 'params' for column in schema):
                        sensors.append({
                            'sensor_name': sensor['sensor_name'],
                            'status_list': json.loads(sensor['status_list']),
                            'params': json.loads(sensor['params'])
                        })
                    elif any(column[0] == 'on_value' for column in schema) and any(column[0] == 'off_value' for column in schema):
                        sensors.append({
                            'sensor_name': sensor['sensor_name'],
                            'on_value': sensor['on_value'],
                            'off_value': sensor['off_value'],
                            'address': sensor.get('address', '')  # 获取地址，默认为空字符串
                        })
        return sensors

    def load_numeric_sensors(self, subtabs):
        subtabs.clear()
        for item in self.sensors:
            if 'status_list' in item and 'params' in item:
                sensor_name = item['sensor_name']
                tab = QWidget()
                layout = QVBoxLayout()
                params_table = QTableWidget()
                params_table.setColumnCount(4)
                params_table.setHorizontalHeaderLabels(["参数", "地址", "编辑", "删除"])
                params_table.setEditTriggers(QTableWidget.NoEditTriggers)
                layout.addWidget(params_table)

                for row, (param, value) in enumerate(item['params'].items()):
                    params_table.insertRow(row)
                    params_table.setItem(row, 0, QTableWidgetItem(param))
                    params_table.setItem(row, 1, QTableWidgetItem(str(value)))
                    self.add_button_to_table("编辑", lambda _, r=row, sn=sensor_name: self.edit_param(r, sn), params_table, row, 2)
                    self.add_button_to_table("删除", lambda _, r=row, sn=sensor_name: self.delete_param(r, sn), params_table, row, 3)

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

    def load_switch_table(self):
        self.switch_table.setRowCount(0)
        for item in self.sensors:
            if 'on_value' in item and 'off_value' in item:
                row = self.switch_table.rowCount()
                self.switch_table.insertRow(row)
                self.switch_table.setItem(row, 0, QTableWidgetItem(item['sensor_name']))
                self.switch_table.setItem(row, 1, QTableWidgetItem(str(item['on_value'])))
                self.switch_table.setItem(row, 2, QTableWidgetItem(str(item['off_value'])))
                self.switch_table.setItem(row, 3, QTableWidgetItem(item['address']))  # 设置地址
                self.add_button_to_switch_table("编辑", self.edit_switch_sensor, self.switch_table, row, 4, item['sensor_name'])
                self.add_button_to_switch_table("删除", self.delete_switch_sensor, self.switch_table, row, 5, item['sensor_name'])

    def save_configuration(self):
        try:
            with self.db:
                for table_name, schema in [(self.numeric_table_name, numeric_schema), (self.switch_table_name, switch_schema)]:
                    # 开始事务
                    self.db.begin_transaction()
                    self.db.truncate_table(table_name)
                    for sensor in self.sensors:
                        if all(key[0] in sensor for key in schema):
                            data = {key[0]: json.dumps(sensor[key[0]]) if isinstance(sensor[key[0]], list) or isinstance(sensor[key[0]], dict) else sensor[key[0]] for key in schema}
                            existing_sensor = self.db.select_data(table_name, columns='*', condition=f"sensor_name = '{sensor['sensor_name']}'")
                            if existing_sensor:
                                self.db.update_data(table_name, data, f"sensor_name = '{sensor['sensor_name']}'")
                            else:
                                self.db.insert_data(table_name, data)
                    # 提交事务
                    self.db.commit_transaction()
            QMessageBox.information(self, "保存成功", "配置已保存。")
        except Exception as e:
            # 回滚事务
            self.db.rollback_transaction()
            QMessageBox.critical(self, "保存失败", f"配置保存失败：{str(e)}")

    def add_sensor(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            self.add_numeric_sensor()
        elif current_tab_index == 1:
            self.add_switch_sensor()

    def add_numeric_sensor(self):
        sensor_name, ok = QInputDialog.getText(self, "添加数值型传感器", "请输入传感器名称:")
        if ok and not any(s['sensor_name'] == sensor_name for s in self.sensors):
            dialog = ModifyNumericSensorDialog(self)
            dialog.sensor_name.setText(sensor_name)
            if dialog.exec_() == QDialog.Accepted:
                new_sensor = {
                    'sensor_name': dialog.sensor_name.text(),
                    'status_list': [status.strip() for status in dialog.status_list.text().split(',')],
                    'params': dialog.params
                }
                if not any(s['sensor_name'] == new_sensor['sensor_name'] for s in self.sensors):
                    self.sensors.append(new_sensor)
                    self.update_sensor_list()
                    QMessageBox.information(self, "成功", f"数值型传感器 {sensor_name} 已成功添加。")
                else:
                    QMessageBox.warning(self, "警告", "传感器名称已存在。")
        else:
            QMessageBox.warning(self, "警告", "传感器名称已存在或输入为空。")

    def add_switch_sensor(self):
        dialog = ModifySwitchSensorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            sensor_name = dialog.sensor_name.text()
            address = dialog.address.text()
            if sensor_name and address:
                if not any(s['sensor_name'] == sensor_name for s in self.sensors) and ('address' in s and not any(
                        s['address'] == address ) for s in self.sensors):
                    new_sensor = {
                        'sensor_name': sensor_name,
                        'on_value': int(dialog.on_value.text()) if dialog.on_value.text() else 1,
                        'off_value': int(dialog.off_value.text()) if dialog.off_value.text() else 0,
                        'address': address,
                        'params': dialog.params
                    }
                    self.sensors.append(new_sensor)
                    self.update_sensor_list()
                    QMessageBox.information(self, "成功", f"开关型传感器 {sensor_name} 已成功添加。")
                else:
                    QMessageBox.warning(self, "警告", "传感器名称或地址已存在。")
            else:
                QMessageBox.warning(self, "警告", "请输入传感器名称和地址。")

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
            sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
            if sensor:
                new_sensor_name, ok = QInputDialog.getText(self, "修改传感器名称", "请输入新的传感器名称:", text=sensor_name)
                if ok and not any(s['sensor_name'] == new_sensor_name for s in self.sensors):
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
            sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
            if sensor:
                new_sensor_name, ok = QInputDialog.getText(self, "修改传感器名称", "请输入新的传感器名称:",
                                                           text=sensor_name)
                if ok and not any(s['sensor_name'] == new_sensor_name for s in self.sensors):
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
        sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
        if sensor:
            dialog = ModifySwitchSensorDialog(self)
            dialog.sensor_name.setText(sensor['sensor_name'])
            dialog.on_value.setText(str(sensor['on_value']))
            dialog.off_value.setText(str(sensor['off_value']))
            dialog.address.setText(sensor['address'])  # 设置地址
            if dialog.exec_() == QDialog.Accepted:
                sensor['sensor_name'] = dialog.sensor_name.text()
                sensor['on_value'] = int(dialog.on_value.text())
                sensor['off_value'] = int(dialog.off_value.text())
                sensor['address'] = dialog.address.text()  # 更新地址
                self.load_switch_table()
                QMessageBox.information(self, "成功", f"开关型传感器 {sensor_name} 已成功修改。")
        else:
            QMessageBox.critical(self, "错误", "未找到指定传感器。")

    def delete_sensor(self):
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
            sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
            if sensor:
                self.sensors.remove(sensor)
                self.load_numeric_sensors(current_tab)
                QMessageBox.information(self, "成功", f"数值型传感器 {sensor_name} 已成功删除。")
            else:
                QMessageBox.critical(self, "错误", "未找到指定传感器。")
        else:
            QMessageBox.warning(self, "警告", "请选择一个传感器进行删除。")

    def delete_switch_sensor(self, row, sensor_name):
        sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
        if sensor:
            self.sensors.remove(sensor)
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
                sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    param_name, ok = QInputDialog.getText(self, "添加参数", "参数名称:")
                    if ok:
                        param_value, ok = QInputDialog.getInt(self, "添加参数", "参数地址:")
                        if ok and param_name not in sensor['params'] and param_value not in sensor['params'].values():
                            sensor['params'][param_name] = param_value
                            self.load_numeric_sensors(current_tab)
                            QMessageBox.information(self, "成功",
                                                    f"参数 {param_name} 已成功添加到传感器 {sensor_name}。")
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
                sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    param_name = self.tables[sensor_name].item(row, 0).text()
                    param_value, ok = QInputDialog.getInt(self, "编辑参数", "参数地址:", value=int(
                        self.tables[sensor_name].item(row, 1).text()))
                    if ok:
                        sensor['params'][param_name] = param_value
                        self.load_numeric_sensors(current_tab)
                        QMessageBox.information(self, "成功", f"参数 {param_name} 已成功更新。")
                else:
                    QMessageBox.critical(self, "错误", "未找到指定传感器。")
            else:
                QMessageBox.warning(self, "警告", "请选择一个传感器进行操作。")
        else:
            QMessageBox.warning(self, "警告", "当前选项卡不支持此操作。")

    def delete_param(self, row, sensor_name):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:
            current_tab = self.tab_widget.widget(0).layout().itemAt(0).widget()
            selected_tab_index = current_tab.currentIndex()
            if selected_tab_index >= 0:
                sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
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
                sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
                if sensor:
                    status, ok = QInputDialog.getText(self, "添加状态", "状态名称:")
                    if ok and status not in sensor['status_list']:
                        sensor['status_list'].append(status)
                        self.load_numeric_sensors(current_tab)
                        QMessageBox.information(self, "成功",
                                                f"状态 {status} 已成功添加到传感器 {sensor_name}。")
                    else:
                        QMessageBox.warning(self, "警告", "状态已存在或输入为空。")
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
                sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
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
                sensor = next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
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
        if index == 0:
            self.modify_sensor_button.setEnabled(True)
            self.add_sensor_button.setEnabled(True)
            self.delete_sensor_button.setEnabled(True)
            self.modify_status_button.setEnabled(True)
            self.add_status_button.setEnabled(True)
            self.delete_status_button.setEnabled(True)
            # self.add_param_button.setEnabled(True)
        elif index == 1:
            self.modify_sensor_button.setEnabled(False)
            self.add_sensor_button.setEnabled(False)
            self.delete_sensor_button.setEnabled(False)
            self.modify_status_button.setEnabled(False)
            self.add_status_button.setEnabled(False)
            self.delete_status_button.setEnabled(False)
            # self.add_param_button.setEnabled(False)

class ModifyNumericSensorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改数值型传感器")
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
        self.param_layout = QVBoxLayout()
        layout.addLayout(self.param_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        self.params = {}
        for i in range(self.param_layout.count()):
            widget = self.param_layout.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                param_name = widget.objectName()
                param_value = widget.text()
                if param_value.isdigit():
                    self.params[param_name] = int(param_value)
                else:
                    QMessageBox.warning(self, "警告", f"参数 {param_name} 的地址必须是数字。")
                    return
        super().accept()

    def add_param(self, param_name, param_value):
        param_input = QLineEdit(self)
        param_input.setObjectName(param_name)
        param_input.setText(str(param_value))
        self.param_layout.addWidget(param_input)

class ModifySwitchSensorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改开关型传感器")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.sensor_name = QLineEdit(self)
        layout.addWidget(QLabel("传感器名称:"))
        layout.addWidget(self.sensor_name)

        self.on_value = QLineEdit(self)
        layout.addWidget(QLabel("开启值:"))
        layout.addWidget(self.on_value)

        self.off_value = QLineEdit(self)
        layout.addWidget(QLabel("关闭值:"))
        layout.addWidget(self.off_value)

        self.address = QLineEdit(self)
        layout.addWidget(QLabel("地址:"))
        layout.addWidget(self.address)

        self.params = {}
        self.param_layout = QVBoxLayout()
        layout.addLayout(self.param_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        self.params = {}
        for i in range(self.param_layout.count()):
            widget = self.param_layout.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                param_name = widget.objectName()
                param_value = widget.text()
                if param_value.isdigit():
                    self.params[param_name] = int(param_value)
                else:
                    QMessageBox.warning(self, "警告", f"参数 {param_name} 的地址必须是数字。")
                    return
        super().accept()

    def add_param(self, param_name, param_value):
        param_input = QLineEdit(self)
        param_input.setObjectName(param_name)
        param_input.setText(str(param_value))
        self.param_layout.addWidget(param_input)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())
