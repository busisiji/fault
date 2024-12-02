import sys
import re
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import config
from db.db_mysql import DB_MySQL
from ui.Base.baseWindow import BaseWindow


class SensorWindow(BaseWindow):

    _single_update_data = pyqtSignal(dict,   str)
    def __init__(self, parent=None):
        super(SensorWindow, self).__init__(parent)

        self.sensor_map = {sensor["address"]: sensor for sensor in config.initialize_sensors()}

        self._single_update_data.connect(self.on_read_result)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("传感器参数表")

        # 设置样式表
        self.setStyleSheet("""
            QWidget {
                background-color: #fff;
                color: #000;
                font-size: 14px;
            }
            QPushButton {
                background-color: #555;
                border: 1px solid #444;
                padding: 5px 10px;
                color: #fff;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QLabel {
                font-size: 14px;
                color: #000;
                font-weight: bold; 
                margin-bottom: 5px;
            }
            
            QFrame {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QFrame#sensor_frame {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QLineEdit {
                font-size: 14px;
                background-color: #fff;
                border: 1px solid #ddd;
                color: #000;
                padding: 5px;
            }
            .sensor_name {
                color: #007BFF;
            }
            .sensor_value {
                color: #28A745;
            }
            .sensor_address {
                color: #DC3545;
            }
        """)
        self.labels = []

        # 右侧布局
        self.right_layout = QtWidgets.QVBoxLayout()

        # 按传感器类型分栏
        for sensor in  self.sensors:
            sensor_name = sensor["sensor_name"]
            self.type_layout = self.add_sensor_widget(sensor)

            self.type_layout.addLayout(self.grid_layout[sensor_name] )
            self.right_layout.addLayout(self.type_layout)

        # 右侧容器
        right_frame = QtWidgets.QFrame()
        verSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.right_layout.addItem(verSpacer)
        right_frame.setLayout(self.right_layout)

        # 主布局
        main_layout = QtWidgets.QHBoxLayout()
        # main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)
        self.setLayout(main_layout)

        self.set_labels()

    def add_sensor_widget(self,sensor):
        sensor_name = sensor["sensor_name"]
        param_names = sensor["param_name"]
        address_list = sensor["address"]
        type_layout = QtWidgets.QVBoxLayout()
        type_label = QtWidgets.QLabel(sensor_name)
        type_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        self.labels.append(type_label)
        type_layout.addWidget(type_label)

        self.grid_layout = {}
        self.grid_layout[sensor_name] = QtWidgets.QGridLayout()
        self.row, self.col = {}, {}
        self.row[sensor_name], self.col[sensor_name] = 0, 0
        for i in range(len(param_names)):
            param_name = param_names[i]
            address = address_list[i]
            widget = self.create_sensor_widget(param_name, address)
            self.grid_layout[sensor_name].addWidget(widget, self.row[sensor_name], self.col[sensor_name])
            self.col[sensor_name] += 1
            if self.col[sensor_name] == 4:
                self.col[sensor_name] = 0
                self.row[sensor_name] += 1
        return  type_layout

    def set_labels(self):
        for label in self.labels:
            label.setWordWrap(True)
            label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

    def create_sensor_widget(self, param_name,address):
        """
        创建传感器小部件。

        根据提供的传感器信息字典，生成一个包含传感器名称、值和地址的QWidget小部件。

        参数:
        - sensor (dict): 包含传感器信息的字典，必须包含'param_name'和'address'键。

        返回:
        - QtWidgets.QWidget: 一个包含传感器名称、值和地址标签的QWidget小部件。
        """
        # 创建并配置传感器参数标签

        # 创建传感器小部件的主容器和布局
        widget = QtWidgets.QWidget()
        widget.setObjectName("sensor_frame")
        sensor_layout = QtWidgets.QVBoxLayout()
        sensor_layout.setAlignment(QtCore.Qt.AlignTop)
        sensor_layout.setSpacing(5)


        name_label = QtWidgets.QLabel(param_name)
        name_label.setStyleSheet("color: #007BFF; margin-bottom: 5px;")
        name_label.setWordWrap(True)
        name_label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        # 创建并配置传感器值标签
        value_label = QtWidgets.QLabel("0")
        value_label.setStyleSheet("color: #28A745; margin-bottom: 5px;")
        value_label.setWordWrap(True)
        value_label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        value_label.setObjectName("value_label")  # 设置对象名称

        # 创建并配置传感器地址标签
        address_label = QtWidgets.QLabel(f"地址: {address}")
        address_label.setStyleSheet("color: #DC3545; margin-bottom: 5px;")
        address_label.setWordWrap(True)
        address_label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)


        sensor_layout.addWidget(name_label)
        sensor_layout.addWidget(value_label)
        sensor_layout.addWidget(address_label)
        widget.setLayout(sensor_layout)

        return widget

    def on_read_result(self, sensor, result):
        # 更新传感器的读取结果
        if sensor:
            for child in self.findChildren(QtWidgets.QLabel):
                if child.text().startswith(sensor["param_name"]):
                    value_label = child.parent().findChild(QtWidgets.QLabel, "value_label")
                    if value_label:
                        value_label.setText(result)

# 更新传感器配置

    def update_ui(self):
        try:
            # 获取最新的传感器信息
            old_sensors = self.sensors
            new_sensors = config.get_sensors()
            self.sensors = new_sensors

            # 提取旧的和新的传感器名称
            old_sensor_names = {sensor['sensor_name'] for sensor in old_sensors}
            new_sensor_names = {sensor['sensor_name'] for sensor in new_sensors}

            # 删除没有的传感器标签
            for old_sensor_name in [sensor for sensor in old_sensor_names if sensor not in new_sensor_names]:
                for label in self.labels:
                    if label.text() == old_sensor_name:
                        label.deleteLater()
                        self.labels.remove(label)

            # 增加新的传感器标签
            for new_sensor_name in [sensor for sensor in new_sensor_names if sensor not in old_sensor_names]:
                sensor = next(s for s in new_sensors if s['sensor_name'] == new_sensor_name)
                self.add_sensor_widget(sensor)

            # 删除没有的参数的传感器小部件
            for sensor in old_sensors:
                sensor_name = sensor['sensor_name']
                old_param_names = set(sensor['param_name'])
                new_param_names = set(
                    next((s['param_name'] for s in new_sensors if s['sensor_name'] == sensor['sensor_name']), []))
                for old_param_name in [param for param in old_param_names if param not in new_param_names]:
                    for child in self.findChildren(QtWidgets.QLabel):
                        if child.text().startswith(old_param_name):
                            widget = child.parent()
                            widget.deleteLater()
                            self.col[sensor_name] -= 1
                            if self.col[sensor_name] == 4:
                                self.col[sensor_name] = 0
                                self.row[sensor_name] -= 1

            # 增加新的参数的传感器小部件
            for sensor in new_sensors:
                sensor_name = sensor['sensor_name']
                new_param_names = set(sensor['param_name'])
                old_param_names = set(
                    next((s['param_name'] for s in old_sensors if s['sensor_name'] == sensor_name), []))
                for new_param_name in [param for param in new_param_names if param not in old_param_names]:
                    address = next(
                        (addr for addr, name in zip(sensor['address'], sensor_name) if name == new_param_name),
                        None)
                    if new_param_name:
                        widget = self.create_sensor_widget(new_param_name, address)
                        self.grid_layout[sensor_name] = QtWidgets.QGridLayout() if sensor_name not in self.grid_layout else self.grid_layout[sensor_name]
                        self.grid_layout[sensor_name].addWidget(widget,self.row[sensor_name],self.col[sensor_name])
                        self.col[sensor_name] += 1
                        if self.col[sensor_name] == 4:
                            self.col[sensor_name] = 0
                            self.row[sensor_name] += 1
                        # self.type_layout.addLayout(self.grid_layout[sensor_name])
        except Exception as e:
            print(e)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SensorWindow()
    window.show()
    sys.exit(app.exec_())
