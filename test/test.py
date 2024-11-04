import sys
import re
from PyQt5 import QtWidgets, QtCore, QtGui
from pymodbus.client.sync import ModbusTcpClient

# 假设 config 模块中有 initialize_sensors 函数
import config

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
        self.worker = None
        self.thread = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_sensors)
        self.sensors = config.initialize_sensors()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Modbus TCP 通讯助手")

        # 设置样式表
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #fff;
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
                color: #ccc;
            }
            QFrame {
                background-color: #444;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QFrame#sensor_frame {
                background-color: #555;
                border: 1px solid #666;
                border-radius: 5px;
            }
            QLineEdit {
                background-color: #555;
                border: 1px solid #666;
                color: #fff;
                padding: 5px;
            }
        """)

        # 左侧布局
        left_layout = QtWidgets.QVBoxLayout()

        # IP地址输入框
        self.ip_label = QtWidgets.QLabel("IP 地址:")
        self.ip_input = QtWidgets.QLineEdit("127.0.0.1")
        left_layout.addWidget(self.ip_label)
        left_layout.addWidget(self.ip_input)

        # 端口号输入框
        self.port_label = QtWidgets.QLabel("端口号:")
        self.port_input = QtWidgets.QLineEdit("502")
        left_layout.addWidget(self.port_label)
        left_layout.addWidget(self.port_input)

        # 定时采集时间输入框
        self.interval_label = QtWidgets.QLabel("定时采集时间 (秒):")
        self.interval_input = QtWidgets.QLineEdit("5")
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
        left_frame.setFixedWidth(200)
        left_frame.setLayout(left_layout)

        # 右侧布局
        right_layout = QtWidgets.QVBoxLayout()

        # 传感器信息网格布局
        self.sensor_grid = QtWidgets.QGridLayout()
        self.sensor_widgets = []

        # 分栏头
        header_labels = ["Z 轴", "X 轴", "其他"]
        for i, header in enumerate(header_labels):
            label = QtWidgets.QLabel(header)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("background-color: #666; color: #fff; padding: 5px;")
            self.sensor_grid.addWidget(label, 0, i * 2, 1, 2)

        for i, sensor in enumerate(self.sensors):
            name_label = QtWidgets.QLabel(sensor["name"])
            value_label = QtWidgets.QLabel("0")
            address_label = QtWidgets.QLabel(f"地址: {sensor['address']}")
            widget = QtWidgets.QWidget()
            widget.setObjectName("sensor_frame")
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(name_label)
            layout.addWidget(value_label)
            layout.addWidget(address_label)
            widget.setLayout(layout)
            self.sensor_grid.addWidget(widget, (i // 4) + 1, (i % 4) // 2 * 2, 1, 2)
            self.sensor_widgets.append((value_label, address_label))

        right_layout.addLayout(self.sensor_grid)

        # 右侧容器
        right_frame = QtWidgets.QFrame()
        right_frame.setLayout(right_layout)

        # 主布局
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)
        self.setLayout(main_layout)

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
        else:
            self.status_label.setText(f"连接失败: {self.ip_input.text()}:{self.port_input.text()}")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)

    def disconnect_from_server(self):
        if self.worker and self.thread:
            self.worker.disconnect_from_server()
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.status_label.setText("已断开连接")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.timer.stop()

    def update_sensors(self):
        for sensor in self.sensors:
            self.worker.read_register(sensor["address"])

    def on_read_result(self, address, result):
        for i, sensor in enumerate(self.sensors):
            if sensor["address"] == address:
                value_label, _ = self.sensor_widgets[i]
                value_label.setText(result.split(": ")[1])
                break

    def on_error(self, error):
        self.status_label.setText(f"错误: {error}")

    def closeEvent(self, event):
        self.cleanup_worker_and_thread()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = ModbusTCPWindow()
    myshow.show()
    sys.exit(app.exec_())
