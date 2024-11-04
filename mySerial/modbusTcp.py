import sys
import re
from PyQt5 import QtWidgets, QtCore, QtGui
from pymodbus.client.sync import ModbusTcpClient

import config
from db.db_mysql import DB_MySQL


class ModbusTCPWorker(QtCore.QObject):
    connected = QtCore.pyqtSignal(bool)
    read_result = QtCore.pyqtSignal(int, str)
    error_occurred = QtCore.pyqtSignal(str)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.client = ModbusTcpClient(self.ip, self.port)
        self.running = True

    def connect_to_server(self):
        try:
            if self.client.connect():
                self.connected.emit(True)
            else:
                self.connected.emit(False)
        except Exception as e:
            self.error_occurred.emit(f"连接失败: {e}")

    def disconnect_from_server(self):
        if self.client:
            self.client.close()

    def stop(self):
        self.running = False
        if self.client:
            self.client.close()

    def emit_result(self, address, result):
        self.read_result.emit(address, result)

    def read_register(self, address):
        try:
            response = self.client.read_holding_registers(address, 1, unit=1)
            if response.isError():
                self.emit_result(address, f"读取失败: {response}")
            else:
                self.emit_result(address, f"读取成功: {response.registers[0]}")
        except (ConnectionError, TimeoutError) as e:
            self.emit_result(address, f"连接或超时错误: {e}")
        except ValueError as e:
            self.emit_result(address, f"值错误: {e}")
        except Exception as e:
            self.emit_result(address, f"未知错误: {e}")


class ModbusTCPWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ModbusTCPWindow, self).__init__(parent)
        self.db = DB_MySQL()
        self.table_name = config.toname['ModbusTcp通讯']
        DataModbus = [
            ('ip', 'TEXT'),
            ('port', 'INT'),
            ('intervalTime', 'INT'),
        ]
        # 创建表
        with self.db:
            self.db.create_table(self.table_name, DataModbus)

        self.worker = None
        self.thread = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_sensors)
        self.sensors = config.initialize_sensors()
        self.sensor_map = {sensor["address"]: sensor for sensor in self.sensors}

        self.init_ui()
        self.load_config_from_db()  # 从数据库加载配置

    def init_ui(self):
        self.setWindowTitle("Modbus TCP 通讯助手")

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

        # 左侧布局
        left_layout = QtWidgets.QVBoxLayout()

        self.labels = []

        # IP地址输入框
        self.ip_label = QtWidgets.QLabel("IP 地址:")
        self.labels.append(self.ip_label)
        self.ip_input = QtWidgets.QLineEdit("127.0.0.1")
        ip_validator = QtGui.QRegExpValidator(QtCore.QRegExp(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"))
        self.ip_input.setValidator(ip_validator)
        left_layout.addWidget(self.ip_label)
        left_layout.addWidget(self.ip_input)

        # 端口号输入框
        self.port_label = QtWidgets.QLabel("端口号:")
        self.labels.append(self.port_label)
        self.port_input = QtWidgets.QLineEdit("502")
        port_validator = QtGui.QIntValidator(1, 65535)
        self.port_input.setValidator(port_validator)
        left_layout.addWidget(self.port_label)
        left_layout.addWidget(self.port_input)

        # 定时采集时间输入框
        self.interval_label = QtWidgets.QLabel("定时采集时间 (秒):")
        self.labels.append(self.interval_label)
        self.interval_input = QtWidgets.QLineEdit("5")
        interval_validator = QtGui.QIntValidator(1, 60)
        self.interval_input.setValidator(interval_validator)
        left_layout.addWidget(self.interval_label)
        left_layout.addWidget(self.interval_input)

        # 连接按钮
        self.connect_button = QtWidgets.QPushButton("连接")
        self.connect_button.clicked.connect(self.connect_to_server)
        left_layout.addWidget(self.connect_button)

        # 断开连接按钮
        self.disconnect_button = QtWidgets.QPushButton("断开连接")
        self.disconnect_button.clicked.connect(self.disconnect_from_server)
        self.disconnect_button.setEnabled(False)
        left_layout.addWidget(self.disconnect_button)

        # 提示信息
        self.status_label = QtWidgets.QLabel("")
        left_layout.addWidget(self.status_label)

        # 左侧边栏容器
        left_frame = QtWidgets.QFrame()
        verSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        left_layout.addItem(verSpacer)
        left_frame.setFixedWidth(200)
        left_frame.setLayout(left_layout)

        # 右侧布局
        right_layout = QtWidgets.QVBoxLayout()

        # 按传感器类型分栏
        for sensor_type, param_names in config.sensor_class.items():
            type_layout = QtWidgets.QVBoxLayout()
            type_label = QtWidgets.QLabel(sensor_type)
            type_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
            self.labels.append(type_label)
            type_layout.addWidget(type_label)

            grid_layout = QtWidgets.QGridLayout()
            row, col = 0, 0
            for sensor in self.sensors:
                if sensor["param_name"] in param_names:
                    widget = self.create_sensor_widget(sensor)
                    grid_layout.addWidget(widget, row, col)
                    col += 1
                    if col == 4:
                        col = 0
                        row += 1

            type_layout.addLayout(grid_layout)
            right_layout.addLayout(type_layout)

        # 右侧容器
        right_frame = QtWidgets.QFrame()
        verSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        right_layout.addItem(verSpacer)
        right_frame.setLayout(right_layout)

        # 主布局
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)
        self.setLayout(main_layout)

        self.set_labels()

    def set_labels(self):
        for label in self.labels:
            label.setWordWrap(True)
            label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

    def create_sensor_widget(self, sensor):
        name_label = QtWidgets.QLabel(sensor["param_name"])
        name_label.setStyleSheet("color: #007BFF; margin-bottom: 5px;")
        name_label.setWordWrap(True)
        name_label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        value_label = QtWidgets.QLabel("0")
        value_label.setStyleSheet("color: #28A745; margin-bottom: 5px;")
        value_label.setWordWrap(True)
        value_label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        value_label.setObjectName("value_label")  # 设置对象名称

        address_label = QtWidgets.QLabel(f"地址: {sensor['address']}")
        address_label.setStyleSheet("color: #DC3545; margin-bottom: 5px;")
        address_label.setWordWrap(True)
        address_label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        widget = QtWidgets.QWidget()
        widget.setObjectName("sensor_frame")
        sensor_layout = QtWidgets.QVBoxLayout()
        sensor_layout.setAlignment(QtCore.Qt.AlignTop)
        sensor_layout.setSpacing(5)
        sensor_layout.addWidget(name_label)
        sensor_layout.addWidget(value_label)
        sensor_layout.addWidget(address_label)
        widget.setLayout(sensor_layout)

        return widget

    def connect_to_server(self):
        # 清理之前的线程和工作器对象
        self.cleanup_worker_and_thread()

        ip = self.ip_input.text()
        port = self.port_input.text()
        interval = self.interval_input.text()

        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
            self.status_label.setText("错误: 无效的IP地址")
            return
        if not port.isdigit() or not 1 <= int(port) <= 65535:
            self.status_label.setText("错误: 无效的端口号")
            return
        if not interval.isdigit() or not 1 <= int(interval) <= 60:
            self.status_label.setText("错误: 无效的定时采集时间")
            return

        self.worker = ModbusTCPWorker(ip, int(port))
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.connect_to_server)
        self.worker.connected.connect(self.on_connected)
        self.worker.read_result.connect(self.on_read_result)
        self.worker.error_occurred.connect(self.on_error)
        self.thread.start()

    def cleanup_worker_and_thread(self):
        if self.worker and self.thread:
            self.worker.disconnect_from_server()
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.worker.deleteLater()
            self.thread.deleteLater()
            self.worker = None
            self.thread = None

    def on_connected(self, success):
        if success:
            self.status_label.setText(f"连接成功: {self.ip_input.text()}:{self.port_input.text()}")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            interval = int(self.interval_input.text())
            self.timer.start(interval * 1000)
            self.save_config_to_db()  # 保存配置到数据库
        else:
            self.status_label.setText(f"连接失败: {self.ip_input.text()}:{self.port_input.text()}")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)

    def on_read_result(self, address, result):
        sensor = self.sensor_map.get(address)
        if sensor:
            for child in self.findChildren(QtWidgets.QLabel):
                if child.text().startswith(sensor["param_name"]):
                    value_label = child.parent().findChild(QtWidgets.QLabel, "value_label")
                    if value_label:
                        value_label.setText(result)

    def on_error(self, error_message):
        self.status_label.setText(f"错误: {error_message}")

    def disconnect_from_server(self):
        if self.worker and self.thread:
            self.worker.disconnect_from_server()
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.worker.deleteLater()
            self.thread.deleteLater()
            self.worker = None
            self.thread = None
            self.status_label.setText("已断开连接")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.timer.stop()

    def update_sensors(self):
        if self.worker:
            for sensor in self.sensors:
                self.worker.read_register(sensor["address"])

    def save_config_to_db(self):
        config_data = {
            'ip': self.ip_input.text(),
            'port': int(self.port_input.text()),
            'intervalTime': int(self.interval_input.text())
        }
        with self.db:
            last_record = self.db.get_last_record(self.table_name)
            if last_record:
                # 更新最后一行数据
                condition = f"id = {last_record['id']}"
                self.db.update_data(self.table_name, config_data, condition)
            else:
                # 如果表为空，则插入新数据
                self.db.insert_data(self.table_name, config_data)

    def load_config_from_db(self):
        try:
            with self.db:
                config_data = self.db.select_data(self.table_name)
                if config_data:
                    config_data = config_data[0]  # 获取第一行数据
                    self.ip_input.setText(config_data['ip'])
                    self.port_input.setText(str(config_data['port']))
                    self.interval_input.setText(str(config_data['intervalTime']))
        except Exception as e:
            self.status_label.setText(f"错误: 从数据库读取配置失败 {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ModbusTCPWindow()
    window.show()
    sys.exit(app.exec_())
