import json
import struct
import sys
import re
from PyQt5 import QtWidgets, QtCore, QtGui
from pymodbus.client.sync import ModbusTcpClient

import config
from db.db_mysql import DB_MySQL
from qss.qss import btn_css


class ModbusTCPWorker(QtCore.QObject):
    """
    ModbusTCPWorker是一个用于执行Modbus TCP通信的类。
    它继承自QtCore.QObject，并提供了与Modbus服务器进行异步通信的能力。

    信号:
    - connected: 当与Modbus服务器的连接状态改变时触发，传递一个布尔值表示连接状态。
    - read_result: 当寄存器读取操作完成时触发，传递寄存器地址和读取结果。
    - error_occurred: 当遇到错误时触发，传递错误信息字符串。
    """

    connected = QtCore.pyqtSignal(bool)
    read_result = QtCore.pyqtSignal(int, str)
    read_results = QtCore.pyqtSignal(str,list,list)
    update_switch = QtCore.pyqtSignal(list,list)
    error_occurred = QtCore.pyqtSignal(str)

    def __init__(self, ip, port):
        """
        构造函数: 初始化ModbusTCPWorker对象。

        参数:
        - ip: Modbus服务器的IP地址。
        - port: Modbus服务器的端口号。
        """
        super().__init__()
        self.ip = ip
        self.port = port
        self.client = ModbusTcpClient(self.ip, self.port)
        self.running = True
        # 获取传感器信息
        self.sensors = config.get_sensors()

    def connect_to_server(self):
        """
        连接到Modbus服务器。
        如果连接成功，触发connected信号并传递True，否则传递False。
        如果连接过程中出现异常，触发error_occurred信号并传递错误信息。
        """
        try:
            if self.client.connect():
                self.connected.emit(True)
            else:
                self.connected.emit(False)
        except Exception as e:
            self.error_occurred.emit(f"连接失败: {e}")

    def disconnect_from_server(self):
        """
        从Modbus服务器断开连接。
        """
        if self.client:
            self.client.close()

    def stop(self):
        """
        停止ModbusTCPWorker对象的运行并断开与服务器的连接。
        """
        self.running = False
        if self.client:
            self.client.close()


    def emit_results(self, sensor_name,status_list, results):
        """
        发送读取结果信号。

        参数:
        - sensor_name: 传感器名称。
        - status_list: 参数列表
        - results: 读取结果字符串。
        """
        self.read_results.emit(sensor_name,status_list, results)
    def convert_data(self, value, data_type):
        if data_type == 'uint16':
            if value >= 32768:
                value -= 65536
            return value
        elif data_type == 'uint32':
            return (value[0] << 16) | value[1]
        elif data_type == 'float32':
           if isinstance(value, list) and len(value) == 2:
                combined_value = (value[0] << 16) | value[1]
                return struct.unpack('!f', struct.pack('!I', combined_value))[0]
        elif data_type == 'bool':
            return bool(value)
        else:
            return value
    def read_registers(self):
        try:
            addresses = 0
            # 读取数值传感器数据
            for sensor in config.get_sensors('数值传感器'):
                results = []
                sensor_name = sensor['sensor_name']
                param_names = sensor['param_name']
                status_list = sensor['status_list']
                addresses = sensor['address']
                data_types = json.loads(sensor['data_type'])
                results = []
                for i, address in enumerate(addresses):
                    results.append(self.read_register(address,data_types[i]))
                self.emit_results(sensor_name, param_names, results)

            # 读取开关传感器状态
            sensor_names = []
            status = []
            for sensor in config.get_sensors('开关传感器'):
                sensor_name = sensor['sensor_name']
                address = sensor['address']
                data_type = sensor['data_type']
                status.append(self.read_register(address,data_type))
                sensor_names.append(sensor_name)
            self.update_switch.emit(sensor_names,status)
        except (ConnectionError, TimeoutError) as e:
            self.error_occurred.emit(f"采集地址连接或超时错误: {e}")
        except ValueError as e:
            self.error_occurred.emit(f"采集地址数据类型错误: {e}")
        except Exception as e:
            self.error_occurred.emit(f"采集地址其他错误: {e}")

    def read_register(self, address, data_type='uint16'):
        try:
            address = int(address)

            if data_type == 'bool':
                # 使用 01 功能码读取布尔值
                response = self.client.read_coils(address, 1, unit=1)
                if response.isError():
                    return False
                else:
                    try:
                        response = response.bits[0]
                        return response
                    except:
                        return False
            else:
                count = 2 if '32' in data_type else 1
                response = self.client.read_holding_registers(address, count, unit=1)
                if response.isError():
                    return 'N/A'
                else:
                    if '32' in data_type:
                        value = response.registers
                    else:
                        value = response.registers[0]
                    result = self.convert_data(value, data_type)
                    return '{:.2f}'.format(result)
        except:
            return 'N/A'


class ModbusTCPFrame(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.worker = None
        self.thread = None
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



        self.init_ui()
        self.load_config_from_db()  # 从数据库加载配置

    def init_ui(self):
        self.setWindowTitle("Modbus TCP 通信助手")


        self.labels = []

        # 左侧布局
        # 创建一个 QGroupBox 并设置标题
        group_box = QtWidgets.QGroupBox("Modbus TCP 通讯助手", self)
        left_layout = QtWidgets.QVBoxLayout(group_box)


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
        btn_css(self.connect_button,3)

        # 断开连接按钮
        self.disconnect_button = QtWidgets.QPushButton("断开连接")
        self.disconnect_button.clicked.connect(self.disconnect_from_server)
        self.disconnect_button.setEnabled(False)
        left_layout.addWidget(self.disconnect_button)
        btn_css(self.disconnect_button,2)

        # 提示信息
        self.status_label = QtWidgets.QLabel("")
        left_layout.addWidget(self.status_label)

        # 左侧边栏容器
        verSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        left_layout.addItem(verSpacer)

        # 创建一个主布局管理器
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(group_box)
        left_layout.setContentsMargins(0, 20, 0, 0)
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout)
        # self.setLayout(left_layout)
        self.setFixedWidth(200)

    def connect_to_server(self):
        """连接"""
        # 清理之前的线程和工作器对象
        self.cleanup_worker_and_thread()

        # 获取用户输入的IP地址、端口和间隔时间
        ip = self.ip_input.text()
        port = self.port_input.text()
        interval = self.interval_input.text()

        # 验证IP地址格式
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
            self.status_label.setText("错误: 无效的IP地址")
            return
        # 验证端口号
        if not port.isdigit() or not 1 <= int(port) <= 65535:
            self.status_label.setText("错误: 无效的端口号")
            return
        # 验证间隔时间
        if not interval.isdigit() or not 1 <= int(interval) <= 60:
            self.status_label.setText("错误: 无效的定时采集时间")
            return

        # 创建ModbusTCPWorker实例，用于处理Modbus TCP通信
        self.worker = ModbusTCPWorker(ip, int(port))
        # 创建QThread实例，用于在单独的线程中执行ModbusTCPWorker的操作
        self.thread = QtCore.QThread()
        # 将ModbusTCPWorker对象移动到新创建的线程中，以实现异步通信
        self.worker.moveToThread(self.thread)
        # 当线程启动时，自动调用connect_to_server方法连接到Modbus服务器
        self.thread.started.connect(self.worker.connect_to_server)
        # 当成功连接到Modbus服务器时，触发connected信号，调用on_connected处理连接成功逻辑
        self.worker.connected.connect(self.on_connected)
        # 当读取到Modbus数据时，触发read_result信号，调用父类的on_read_result处理读取结果
        self.worker.read_results.connect(self.parent.on_read_results)
        self.worker.update_switch.connect(self.parent.update_switch)
        # 当Modbus通信发生错误时，触发error_occurred信号，调用on_error处理错误
        self.worker.error_occurred.connect(self.on_error)
        # 启动线程，开始执行ModbusTCPWorker的操作
        self.thread.start()

    def save_config_to_db(self):
        # 将配置数据保存到数据库
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
        # 从数据库加载配置数据
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

    def on_error(self, error_message):
        # 更新状态标签以显示错误信息
        self.status_label.setText(f"错误: {error_message}")

    def on_connected(self, success):
        # 根据连接结果更新状态标签，并启用或禁用按钮
        if success:
            self.status_label.setText(f"连接成功: {self.ip_input.text()}:{self.port_input.text()}")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            btn_css(self.disconnect_button, 3)
            btn_css(self.connect_button, 2)
            interval = int(self.interval_input.text())
            self.parent.timer_sensors.start(interval * 1000)
            self.save_config_to_db()  # 保存配置到数据库
        else:
            self.status_label.setText(f"连接失败: {self.ip_input.text()}:{self.port_input.text()}")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)

    def cleanup_worker_and_thread(self):
        # 断开工作器和线程的连接，并清理资源
        if self.worker and self.thread:
            self.worker.disconnect_from_server()
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.worker.deleteLater()
            self.thread.deleteLater()
            self.worker = None
            self.thread = None
    def disconnect_from_server(self):
        # 断开与服务器的连接，并清理资源
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
            btn_css(self.disconnect_button, 2)
            btn_css(self.connect_button, 3)
            self.parent.timer_sensors.stop()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ModbusTCPFrame()
    window.show()
    sys.exit(app.exec_())