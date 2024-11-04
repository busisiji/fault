import random
import sys
import matplotlib.pyplot as plt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from PyQt5.QtCore import QTimer, Qt

# 模拟传感器数据
def simulate_sensor_data():
    if random.random() < 0.2:  # 10% 的概率模拟传感器未连接
        return None, None
    else:
        return random.uniform(20, 30), random.uniform(40, 60)


class TempHumidityWindow(QMainWindow):
    def __init__(self,prent=None):
        super().__init__(prent)
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # 每秒更新一次

        self.temperature_data = []
        self.humidity_data = []

    def initUI(self):
        self.setWindowTitle('温湿度检测')
        self.setGeometry(100, 100, 800, 600)

        # 创建传感器状态显示区域
        self.sensor_frame = QFrame(self)
        self.sensor_frame.setFrameShape(QFrame.StyledPanel)
        self.sensor_frame.setFrameShadow(QFrame.Raised)
        self.sensor_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        self.temp_label = QLabel('温度: --', self)
        self.humidity_label = QLabel('湿度: --', self)
        self.temp_progress = QProgressBar(self)
        self.temp_progress.setRange(0, 50)
        self.temp_progress.setValue(0)
        self.temp_progress.setStyleSheet("QProgressBar::chunk { background-color: #ff7f50; }")
        self.humidity_progress = QProgressBar(self)
        self.humidity_progress.setRange(0, 100)
        self.humidity_progress.setValue(0)
        self.humidity_progress.setStyleSheet("QProgressBar::chunk { background-color: #6495ed; }")

        sensor_layout = QVBoxLayout()
        sensor_layout.addWidget(self.temp_label)
        sensor_layout.addWidget(self.temp_progress)
        sensor_layout.addWidget(self.humidity_label)
        sensor_layout.addWidget(self.humidity_progress)
        self.sensor_frame.setLayout(sensor_layout)

        # 创建图表
        self.figure = plt.figure()
        self.canvas = FC(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('温湿度变化图')
        self.ax.set_xlabel('时间 (秒)')
        self.ax.set_ylabel('值')
        self.temperature_line, = self.ax.plot([], [], label='Temperature', color='r')
        self.humidity_line, = self.ax.plot([], [], label='Humidity', color='b')
        self.ax.legend()

        # 创建布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.sensor_frame)

        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        widget = QWidget()
        widget.setLayout(main_layout)
        splitter.addWidget(widget)
        splitter.addWidget(self.canvas)

        self.setCentralWidget(splitter)

    def update_data(self):
        humidity, temperature = simulate_sensor_data()
        if humidity is not None and temperature is not None:
            self.temp_label.setText(f'温度: {temperature:.1f}°C')
            self.humidity_label.setText(f'湿度: {humidity:.1f}%')
            self.set_labels_enabled(True)
            self.temperature_data.append(temperature)
            self.humidity_data.append(humidity)
            self.temp_progress.setValue(int(temperature))
            self.humidity_progress.setValue(int(humidity))
        else:
            self.temp_label.setText('温度: 未连接')
            self.humidity_label.setText('湿度: 未连接')
            self.set_labels_enabled(False)
            self.temp_progress.setValue(0)
            self.humidity_progress.setValue(0)

        # 更新图表
        self.temperature_line.set_data(range(len(self.temperature_data)), self.temperature_data)
        self.humidity_line.set_data(range(len(self.humidity_data)), self.humidity_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    def set_labels_enabled(self, enabled):
        palette = self.temp_label.palette()
        if enabled:
            palette.setColor(QPalette.WindowText, QColor('black'))
        else:
            palette.setColor(QPalette.WindowText, QColor('gray'))
        self.temp_label.setPalette(palette)
        self.humidity_label.setPalette(palette)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TempHumidityWindow()
    ex.show()
    sys.exit(app.exec_())
