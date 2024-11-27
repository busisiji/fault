import json
import sys
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QInputDialog, QAction, QMenu, QWidget, QTableWidgetItem, QPushButton, \
    QMessageBox, QHBoxLayout, QComboBox, QTableWidget, QVBoxLayout, QTabWidget, QMainWindow

import config
from db.db_mysql import DB_MySQL

sensors = [
    {"sensor_name": "震动传感器", "status_list": ["正常", "故障", "静止"], "params": {"Z 轴振动速度": 0, "X 轴振动速度": 1, "Z 轴加速度峰值": 2, "X 轴加速度峰值": 3, "Z 轴峰值速度分量频率 Hz": 4, "X 轴峰值速度分量频率 Hz": 5, "Z 轴加速度均方根": 6, "X 轴加速度均方根": 7}},
    {"sensor_name": "温度传感器", "status_list": ["正常", "警告", "故障"], "params": {"温度": 8}},
    {"sensor_name": "湿度传感器", "status_list": ["正常", "故障" , "警告"], "params": {"湿度": 9}},
    {"sensor_name": "门传感器", "on_value": 1, "off_value": 0}
]

class ConfigWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.sensor_types = {
            "数值": ["震动传感器", "温度传感器", "湿度传感器"],
            "开关": ["门传感器"]
        }

        self.db = DB_MySQL()
        self.numeric_table_name = config.toname['数值传感器']
        self.switch_table_name = config.toname['开关传感器']

        # 初始化 sensors 列表
        self.sensors = sensors

        numeric_schema = [
            ('sensor_name', 'VARCHAR(100) NOT NULL UNIQUE'),
            ('status_list', 'TEXT'),  # 存储 JSON 格式的状态列表
            ('params', 'TEXT')  # 存储 JSON 格式的参数
        ]

        switch_schema = [
            ('sensor_name', 'VARCHAR(100) NOT NULL UNIQUE'),
            ('on_value', 'INT NOT NULL'),
            ('off_value', 'INT NOT NULL')
        ]

        with self.db:
            self.db.create_table(self.numeric_table_name, numeric_schema)
            self.db.create_table(self.switch_table_name, switch_schema)

        self.load_sensor_config_from_db()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('传感器配置窗口')
        self.setGeometry(100, 100, 800, 600)

        # 创建主标签页
        self.main_tab_widget = QTabWidget()
        self.setCentralWidget(self.main_tab_widget)

        # 动态创建主标签页
        for sensor_category in self.sensor_types:
            category_tab = QTabWidget()
            self.main_tab_widget.addTab(category_tab, sensor_category)
            self.setup_category_tab(category_tab, sensor_category)

    def load_sensor_config_from_db(self):
        with self.db:
            numeric_results = self.db.select_data(self.numeric_table_name)
            switch_results = self.db.select_data(self.switch_table_name)

            if numeric_results:
                for result in numeric_results:
                    sensor_name = result['sensor_name']
                    status_list = result.get('status_list', '[]')
                    params = result.get('params', '{}')

                    # 将 JSON 字符串转换为列表和字典
                    status_list = eval(status_list)
                    params = eval(params)

                    # 更新 sensors 列表
                    sensor = {
                        "sensor_name": sensor_name,
                        "status_list": status_list,
                        "params": params
                    }
                    self.sensors.append(sensor)

            if switch_results:
                for result in switch_results:
                    sensor_name = result['sensor_name']
                    on_value = result['on_value']
                    off_value = result['off_value']

                    # 更新 sensors 列表
                    sensor = {
                        "sensor_name": sensor_name,
                        "on_value": on_value,
                        "off_value": off_value
                    }
                    self.sensors.append(sensor)


    def setup_category_tab(self, category_tab, sensor_category):
        # 动态创建子标签页
        for sensor_type in self.sensor_types[sensor_category]:
            tab = QWidget()
            category_tab.addTab(tab, sensor_type)
            self.setup_sensor_tab(tab, sensor_type, sensor_category)

        # 编辑传感器类型按钮
        edit_sensor_type_button = QPushButton("编辑传感器类型")
        edit_sensor_type_button.clicked.connect(lambda: self.edit_sensor_type(sensor_category, category_tab))
        category_tab.setCornerWidget(edit_sensor_type_button)  # 将按钮设置在标签栏的右下角

    def setup_sensor_tab(self, tab, sensor_type, sensor_category):
        layout = QVBoxLayout()

        # 表格
        table = QTableWidget()
        table.setColumnCount(4 if sensor_type in self.sensor_types["开关"] else 3)
        table.setHorizontalHeaderLabels(
            ["参数名称", "Modbus 地址", "操作", "开关状态"] if sensor_type in self.sensor_types["开关"] else [
                "参数名称", "Modbus 地址", "操作"])

        # 过滤出当前类型的传感器
        filtered_sensors = [sensor for sensor in sensors if sensor["sensor_name"] == sensor_type]
        if filtered_sensors:
            sensor = filtered_sensors[0]
            params = sensor.get("params", {})
            table.setRowCount(len(params))

            for i, (param_name, address) in enumerate(params.items()):
                param_name_item = QTableWidgetItem(param_name)
                address_item = QTableWidgetItem(str(address))
                edit_button = QPushButton("编辑")
                edit_button.clicked.connect(lambda _, row=i, s_type=sensor_type: self.edit_sensor(row, s_type))

                table.setItem(i, 0, param_name_item)
                table.setItem(i, 1, address_item)
                table.setCellWidget(i, 2, edit_button)

                if sensor_type in self.sensor_types["开关"]:
                    on_off_item = QTableWidgetItem(f"{sensor['on_value']} (开), {sensor['off_value']} (关)")
                    table.setItem(i, 3, on_off_item)

        layout.addWidget(table)

        # 状态配置控件
        if sensor_type in self.sensor_types["数值"]:
            status_layout = QHBoxLayout()

            # 确保 filtered_sensors 不为空
            if filtered_sensors:
                sensor = filtered_sensors[0]  # 假设所有同类型传感器的状态列表相同
                self.status_combo = QComboBox()
                self.status_combo.addItems(sensor.get("status_list", []))
                status_layout.addWidget(self.status_combo)

                status_manage_button = QPushButton("管理状态")
                status_manage_button.clicked.connect(
                    lambda: self.edit_status_list(sensor_type, sensor.get("status_list", []), self.status_combo))
                status_layout.addWidget(status_manage_button)

                layout.addLayout(status_layout)

        # 保存配置按钮
        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_configuration)
        layout.addWidget(save_button)

        tab.setLayout(layout)

    def edit_sensor(self, row, sensor_type):
        """
        编辑传感器的参数名称和Modbus地址。

        :param row: 当前选中的行号
        :param sensor_type: 传感器类型
        """
        try:
            # 找到对应的传感器
            filtered_sensors = [sensor for sensor in self.sensors if sensor["sensor_name"] == sensor_type]
            if not filtered_sensors:
                QMessageBox.warning(self, "警告", "未找到指定类型的传感器。")
                return

            sensor = filtered_sensors[0]
            params = sensor.get("params", {})

            # 获取当前行的参数名称和Modbus地址
            current_param_name = list(params.keys())[row]
            current_address = params[current_param_name]

            # 编辑参数名称
            new_param_name, ok = QInputDialog.getText(self, "编辑参数名称", "参数名称:", text=current_param_name)
            if ok and new_param_name.strip():
                if len(new_param_name) > 100:  # 调整最大长度
                    QMessageBox.warning(self, "输入错误", "参数名称过长，请输入不超过100个字符。")
                    return
                params[new_param_name] = params.pop(current_param_name)
                self.update_sensor_table(sensor_type)
                QMessageBox.information(self, "编辑成功", f"参数名称已更新为 {new_param_name}")

            # 编辑Modbus地址
            new_address, ok = QInputDialog.getInt(self, "编辑Modbus地址", "Modbus地址:", value=current_address, min=0,
                                                  max=65535)
            if ok:
                if new_address < 0 or new_address > 65535:
                    QMessageBox.warning(self, "输入错误", "Modbus地址必须在0到65535之间。")
                    return
                params[new_param_name] = new_address
                self.update_sensor_table(sensor_type)
                QMessageBox.information(self, "编辑成功", f"Modbus地址已更新为 {new_address}")

            # 如果是开关传感器，编辑开/关状态值
            if sensor_type in self.sensor_types["开关"]:
                on_value, ok = QInputDialog.getInt(self, "编辑开状态值", "开状态值:", value=sensor.get("on_value", 0),
                                                   min=0, max=65535)
                if ok:
                    if on_value < 0 or on_value > 65535:
                        QMessageBox.warning(self, "输入错误", "开状态值必须在0到65535之间。")
                        return
                    sensor["on_value"] = on_value
                    self.update_sensor_table(sensor_type)
                    QMessageBox.information(self, "编辑成功", f"开状态值已更新为 {on_value}")

                off_value, ok = QInputDialog.getInt(self, "编辑关状态值", "关状态值:", value=sensor.get("off_value", 0),
                                                    min=0, max=65535)
                if ok:
                    if off_value < 0 or off_value > 65535:
                        QMessageBox.warning(self, "输入错误", "关状态值必须在0到65535之间。")
                        return
                    sensor["off_value"] = off_value
                    self.update_sensor_table(sensor_type)
                    QMessageBox.information(self, "编辑成功", f"关状态值已更新为 {off_value}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生了一个意外错误: {str(e)}")

    def update_sensor_table(self, sensor_type):
        """
        更新指定传感器类型的表格。
        """
        # 找到对应的标签页
        for i in range(self.main_tab_widget.count()):
            if self.main_tab_widget.tabText(i) == sensor_type.split(":")[0]:  # 假设 sensor_category 是 sensor_type 的前缀
                category_tab = self.main_tab_widget.widget(i)
                for j in range(category_tab.count()):
                    if category_tab.tabText(j) == sensor_type:
                        tab = category_tab.widget(j)
                        layout = tab.layout()

                        # 表格
                        table = layout.itemAt(0).widget()
                        table.clearContents()  # 清空表格内容

                        # 过滤出当前类型的传感器
                        filtered_sensors = [sensor for sensor in sensors if sensor["sensor_name"] == sensor_type]
                        table.setRowCount(len(filtered_sensors))

                        for i, sensor in enumerate(filtered_sensors):
                            param_name_item = QTableWidgetItem(", ".join(sensor.get("params", {}).keys()))
                            address_item = QTableWidgetItem(", ".join(map(str, sensor.get("params", {}).values())))
                            edit_button = QPushButton("编辑")
                            edit_button.clicked.connect(
                                lambda _, row=i, s_type=sensor_type: self.edit_sensor(row, s_type))

                            table.setItem(i, 0, param_name_item)
                            table.setItem(i, 1, address_item)
                            table.setCellWidget(i, 2, edit_button)

                            if sensor_type in self.sensor_types["开关"]:
                                on_off_item = QTableWidgetItem(f"{sensor['on_value']} (开), {sensor['off_value']} (关)")
                                table.setItem(i, 3, on_off_item)

                        # 状态配置控件
                        if sensor_type in self.sensor_types["数值"]:
                            status_layout = layout.itemAt(1)
                            status_combo = status_layout.itemAt(0).widget()
                            status_manage_button = status_layout.itemAt(1).widget()

                            # 确保 filtered_sensors 不为空
                            if filtered_sensors:
                                sensor = filtered_sensors[0]  # 假设所有同类型传感器的状态列表相同
                                status_combo.clear()
                                status_combo.addItems(sensor.get("status_list", []))

                        break

    def edit_sensor_type(self, sensor_category, category_tab):
        """
        编辑传感器类型。
        """
        menu = QMenu(self)

        add_action = QAction("添加传感器类型", self)
        add_action.triggered.connect(lambda: self.add_sensor_type(sensor_category))

        delete_action = QAction("删除传感器类型", self)
        delete_action.triggered.connect(lambda: self.delete_sensor_type(sensor_category, category_tab))

        edit_action = QAction("编辑传感器类型", self)
        edit_action.triggered.connect(lambda: self.edit_sensor_type_internal(sensor_category, category_tab))

        menu.addAction(add_action)
        menu.addAction(delete_action)
        menu.addAction(edit_action)

        menu.exec_(QCursor.pos())

    def add_sensor_type(self, sensor_category):
        """
        添加新的传感器类型。
        """
        sensor_type, ok = QInputDialog.getText(self, "添加传感器类型", "传感器类型:")
        if ok and sensor_type.strip():
            if sensor_type not in self.sensor_types[sensor_category]:
                self.sensor_types[sensor_category].append(sensor_type)
                for i in range(self.main_tab_widget.count()):
                    if self.main_tab_widget.tabText(i) == sensor_category:
                        category_tab = self.main_tab_widget.widget(i)
                        tab = QWidget()
                        category_tab.addTab(tab, sensor_type)
                        self.setup_sensor_tab(tab, sensor_type, sensor_category)

    def edit_status_list(self, sensor_name, status_list, status_combo):
        """
        编辑数值传感器的状态列表，并更新传感器配置和组合框中的项目。

        :param sensor_name: 传感器名称
        :param status_list: 当前状态列表
        :param status_combo: 组合框对象
        """
        try:
            # 显示状态列表编辑对话框
            new_status_list, ok = QInputDialog.getText(self, "编辑状态列表", "状态列表 (逗号分隔):",
                                                       text=", ".join(status_list))
            if ok and new_status_list.strip():
                new_status_list = [status.strip() for status in new_status_list.split(",")]

                # 更新传感器配置
                for sensor in self.sensors:
                    if sensor["sensor_name"] == sensor_name:
                        sensor["status_list"] = new_status_list
                        break

                # 更新组合框中的项目
                status_combo.clear()
                status_combo.addItems(new_status_list)

                # 显示保存成功的消息
                QMessageBox.information(self, "保存成功", f"{sensor_name} 的状态列表已成功更新。")

        except Exception as e:
            # 显示错误消息
            QMessageBox.critical(self, "保存失败", f"更新 {sensor_name} 的状态列表时发生错误: {str(e)}")

    def delete_sensor(self, row, sensor_type):
        """
        删除指定行的传感器。
        """
        reply = QMessageBox.question(self, "确认删除", f"确定要删除此传感器吗？", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 从传感器列表中移除
            for i, sensor in enumerate(sensors):
                if sensor["sensor_name"] == sensor_type and row < len(sensor.get("params", {})):
                    del sensor["params"][list(sensor["params"].keys())[row]]
                    break

            # 更新表格
            self.update_sensor_table(sensor_type)

    def delete_sensor_type(self, sensor_category, category_tab):
        """
        删除传感器类型。
        """
        current_tab = category_tab.currentIndex()
        if current_tab is None or current_tab < 0:
            QMessageBox.warning(self, "选择错误", "请选择一个传感器类型进行删除。")
            return

        sensor_type = category_tab.tabText(current_tab)
        reply = QMessageBox.question(self, "确认删除", f"确定要删除传感器类型 '{sensor_type}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 从传感器类型列表中移除
            self.sensor_types[sensor_category].remove(sensor_type)
            # 从主标签页中移除
            for i in range(self.main_tab_widget.count()):
                if self.main_tab_widget.tabText(i) == sensor_category:
                    category_tab.removeTab(current_tab)
                    # 更新传感器配置
                    sensors[:] = [sensor for sensor in sensors if sensor["sensor_name"] != sensor_type]
                    self.update_sensor_table(sensor_category)

            # 如果这是最后一个传感器类型，保留 category_tab 和编辑按钮
            if category_tab.count() == 0:
                tab = QWidget()
                category_tab.addTab(tab, "无传感器类型")
                self.setup_sensor_tab(tab, "无传感器类型", sensor_category)

    def edit_sensor_type_internal(self, sensor_category, category_tab):
        """
        编辑传感器类型。
        """
        # 获取当前选中的子标签页
        current_tab = category_tab.currentIndex()
        if current_tab is None or current_tab < 0:
            QMessageBox.warning(self, "选择错误", "请选择一个传感器类型进行编辑。")
            return

        old_sensor_type = category_tab.tabText(current_tab)
        new_sensor_type, ok = QInputDialog.getText(self, "编辑传感器类型", "新的传感器类型:", text=old_sensor_type)
        if ok and new_sensor_type.strip():
            if new_sensor_type != old_sensor_type:
                # 检查新类型是否已存在
                if new_sensor_type in self.sensor_types[sensor_category]:
                    QMessageBox.warning(self, "输入错误", f"传感器类型 '{new_sensor_type}' 已经存在。")
                    return

                # 更新传感器类型列表
                index = self.sensor_types[sensor_category].index(old_sensor_type)
                self.sensor_types[sensor_category][index] = new_sensor_type

                # 更新主标签页中的子标签页名称
                for i in range(self.main_tab_widget.count()):
                    if self.main_tab_widget.tabText(i) == sensor_category:
                        category_tab.setTabText(current_tab, new_sensor_type)
                        # 更新传感器配置
                        for sensor in sensors:
                            if sensor["sensor_name"] == old_sensor_type:
                                sensor["sensor_name"] = new_sensor_type
                        self.update_sensor_table(new_sensor_type)

    def save_configuration(self):
        """
        保存传感器配置到数据库。
        """
        with self.db:
            # 清空现有数据
            self.db.truncate_table(self.numeric_table_name)
            self.db.truncate_table(self.switch_table_name)

            # 插入新的数据
            for sensor in sensors:
                if sensor["sensor_name"] in self.sensor_types["数值"]:
                    params_str = str(sensor.get('params', {}))  # 将字典转换为字符串
                    self.db.insert_data(self.numeric_table_name, {
                        'sensor_name': sensor['sensor_name'],
                        'status_list': str(sensor.get('status_list', [])),
                        'params': params_str
                    })
                elif sensor["sensor_name"] in self.sensor_types["开关"]:
                    self.db.insert_data(self.switch_table_name, {
                        'sensor_name': sensor['sensor_name'],
                        'on_value': sensor['on_value'],
                        'off_value': sensor['off_value']
                    })

        QMessageBox.information(self, "保存成功", "传感器配置已成功保存到数据库。")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())