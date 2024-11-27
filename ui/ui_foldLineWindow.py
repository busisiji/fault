import datetime
import logging
import random
import sys
import time

import matplotlib.pyplot as plt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic.properties import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
import matplotlib.dates as mdates  # 导入 matplotlib.dates 模块
import config
from ui.others.ui_fun import BaseWindow, SwitchButton
from ui.qss import btn_css
from utils.my_thread import DataProcessingThread


# 模拟传感器数据
def simulate_sensor_data(sensor_name, param):
    """
    模拟传感器数据。

    根据传感器名称和参数生成模拟数据。如果参数为特定类型，返回随机生成的数值；否则返回 None。

    参数:
        sensor_name (str): 传感器名称。
        param (str): 参数名称。

    返回:
        float or None: 模拟的传感器数据或 None。
    """
    if random.random() < 0.2:  # 10% 的概率模拟传感器未连接
        return None
    else:
        if param == '温度':
            return random.uniform(20, 30)
        elif param == '湿度':
            return random.uniform(40, 60)
        elif param == 'Z 轴振动速度':
            return random.uniform(0, 10)
        elif param == 'X 轴振动速度':
            return random.uniform(0, 10)
        elif param == 'Z 轴加速度峰值':
            return random.uniform(0, 100)
        elif param == 'X 轴加速度峰值':
            return random.uniform(0, 100)
        elif param == 'Z 轴峰值速度分量频率 Hz':
            return random.uniform(0, 50)
        elif param == 'X 轴峰值速度分量频率 Hz':
            return random.uniform(0, 50)
        elif param == 'Z 轴加速度均方根':
            return random.uniform(0, 50)
        elif param == 'X 轴加速度均方根':
            return random.uniform(0, 50)
        else:
            return None


class SensorPage(QWidget):
    _single_update_data = pyqtSignal(list, list)

    def __init__(self, sensor_name, params, parent=None):
        super().__init__(parent)
        self.sensor_name = sensor_name
        self.params = params
        self.data = {param: [] for param in params}
        self.time_axis = {param: [] for param in params}
        self.param_positions = {param: 0 for param in params}
        self.figure_num = 4  # 固定图表数量


        self._single_update_data.connect(self.update_data)
        self.init_ui()

    def init_ui(self):
        self.figure = plt.figure()
        self.canvas = FC(self.figure)

        self.param_checkboxes = {}
        self.param_comboboxes = {}
        self.param_layout = QGridLayout()
        row = 0
        column = 0
        self.spacer = QSpacerItem(20, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        for param in self.params:
            checkbox = QCheckBox(param)
            combobox = QComboBox()
            combobox.addItems([f'图表 {i}' for i in range(self.figure_num)])
            combobox.currentIndexChanged.connect(lambda index, p=param: self.set_param_position(p, index))
            checkbox.stateChanged.connect(lambda state, p=param: self.update_plots())
            self.param_layout.addItem(self.spacer, row, column)
            self.param_layout.addWidget(checkbox, row, column + 1)
            self.param_layout.addWidget(combobox, row, column + 2)
            self.param_layout.addItem(self.spacer, row, column + 3)
            self.param_checkboxes[param] = checkbox
            self.param_comboboxes[param] = combobox
            column += 4
            if column >= 5:
                row += 1
                column = 0

        self.axes = {}
        self.axes_x = {}
        self.lines = {}
        self.current_page = 0

        self.page_buttons = QHBoxLayout()
        # 创建标签和开关按钮
        # auto_collect_label = QLabel('显示数据')
        # auto_collect_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # self.auto_collect_switch = SwitchButton()
        # # 将标签和time按钮添加到 top_layout 中
        # self.page_buttons.addWidget(auto_collect_label)
        # self.page_buttons.addWidget(self.auto_collect_switch)
        # spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.page_buttons.addItem(spacer)
        # self.prev_button = QPushButton('上一页')
        # self.next_button = QPushButton('下一页')
        # btn_css(self.prev_button)
        # btn_css(self.next_button)
        # self.page_label = QLabel("1 / 1")
        # spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.page_buttons.addItem(spacer)
        # self.page_buttons.addWidget(self.prev_button)
        # self.page_buttons.addItem(spacer)
        # self.page_buttons.addWidget(self.page_label)
        # self.page_buttons.addItem(spacer)
        # self.page_buttons.addWidget(self.next_button)
        # self.page_buttons.addItem(spacer)

        # self.prev_button.clicked.connect(self.prev_page)
        # self.next_button.clicked.connect(self.next_page)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.param_layout)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(self.page_buttons)
        self.setLayout(main_layout)

        self.update_plots()

    def set_param_position(self, param, position):
        self.param_positions[param] = position
        self.update_plots()

    def update_plots(self):
        if not self.axes:
            num_plots_per_page = 4
            num_pages = (self.figure_num + num_plots_per_page - 1) // num_plots_per_page

            start_index = self.current_page * num_plots_per_page
            end_index = min(start_index + num_plots_per_page, self.figure_num)
            for i in range(start_index, end_index):
                ax = self.figure.add_subplot(2, 2, i - start_index + 1)
                ax.set_xlabel('时间')
                ax.set_ylabel('值')
                self.axes[i] = ax
                self.axes_x[i] = 0
        start_index = self.current_page * 4

        for param, position in self.param_positions.items():
            if self.param_checkboxes[param].isChecked():
                plot_index = position
                if plot_index in self.axes:
                    ax = self.axes[plot_index]
                    ax.set_title(f'图表 {plot_index - start_index + 1}')
                    if param not in self.lines:
                        # 使用 matplotlib 的颜色循环功能
                        line, = ax.plot([], [], label=param, color=f'C{len(self.lines) % 10}')
                        # color = f'C{len(self.lines) % 10}'
                        # line, = ax.plot([], [], label=param, color=color)
                        self.lines[param] = line
                    else:
                        line = self.lines[param]
                        line.set_label(param)
                        line.set_color(f'C{list(self.lines).index(param)}')
                    ax.legend()

                    # 设置时间轴格式
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        self.canvas.draw_idle()
        # self.update_page_label()

    # def update_data(self, param_names, results):
    #     current_time = datetime.datetime.now()  # 获取当前时间
    #     for param, value in zip(param_names, results):
    #         try:
    #             if self.param_checkboxes.get(param) and self.param_checkboxes[param].isChecked():
    #                 try:
    #                     param = config.convert_to_db_columns([param])[0]
    #                 except Exception as e:
    #                     logging.error(f"转换参数时发生错误: {e}")
    #                     continue
    #
    #                 if value is not None:
    #                     try:
    #                         value = float(value)  # 将值转换为浮点数
    #                     except ValueError as e:
    #                         logging.error(f"转换值时发生错误: {e}")
    #                         continue
    #
    #                     self.data[param].append(value)
    #                     self.time_axis[param].append(current_time)
    #                     if param in self.lines:
    #                         positions = self.param_positions[param]
    #                         if positions in self.axes:
    #                             line = self.lines[param]
    #                             line.set_data(self.time_axis[param], self.data[param])
    #                             ax = self.axes[positions]
    #                             ax.relim()
    #                             ax.autoscale_view()
    #         except Exception as e:
    #             logging.error(f"处理数据时发生错误: {e}")
    #     self.canvas.draw_idle()
    def update_data(self, param_names, results):
        self.thread = DataProcessingThread(
            param_names, results, self.param_checkboxes, self.lines, self.axes, self.param_positions, self.time_axis, self.data
        )
        self.thread.data_processed.connect(self.update_plots_from_thread)
        self.thread.start()

    def update_plots_from_thread(self, processed_params, processed_results):
        for param, (positions, time_axis, data) in zip(processed_params, processed_results):
            if positions in self.axes:
                line = self.lines[param]
                line.set_data(time_axis, data)
                ax = self.axes[positions]
                ax.relim()
                ax.autoscale_view()
        self.canvas.draw_idle()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_plots()

    def next_page(self):
        num_plots_per_page = 4
        num_pages = (self.figure_num + num_plots_per_page - 1) // num_plots_per_page
        if self.current_page < num_pages - 1:
            self.current_page += 1
            self.update_plots()

    def update_page_label(self):
        num_plots_per_page = 4
        num_pages = (self.figure_num + num_plots_per_page - 1) // num_plots_per_page
        self.page_label.setText(f"{self.current_page + 1} / {num_pages}")

    def add_param(self, param):
        self.data[param] = []
        self.time_axis[param] = []
        self.param_positions[param] = 0

        checkbox = QCheckBox(param)
        combobox = QComboBox()
        combobox.addItems([f'图表 {i}' for i in range(self.figure_num)])
        combobox.currentIndexChanged.connect(lambda index, p=param: self.set_param_position(p, index))
        checkbox.stateChanged.connect(lambda state, p=param: self.update_plots())

        self.add_param_widgets(checkbox, combobox)

        self.param_checkboxes[param] = checkbox
        self.param_comboboxes[param] = combobox

        self.update_plots()

    def remove_param(self, param):
        if param in self.param_checkboxes:
            self.param_checkboxes[param].deleteLater()
            del self.param_checkboxes[param]

        if param in self.param_comboboxes:
            self.param_comboboxes[param].deleteLater()
            del self.param_comboboxes[param]

        if param in self.data:
            del self.data[param]

        if param in self.time_axis:
            del self.time_axis[param]

        if param in self.param_positions:
            del self.param_positions[param]

        if param in self.lines:
            del self.lines[param]

        self.remove_param_widgets(param)
        self.update_plots()

    def add_param_widgets(self, checkbox, combobox):
        row = (len(self.param_positions) - 1) // 2
        column = (len(self.param_positions) + 1) % 2
        self.param_layout.addItem(self.spacer, row, column * 4)
        self.param_layout.addWidget(checkbox, row, column * 4 + 1)
        self.param_layout.addWidget(combobox, row, column * 4 + 2)
        self.param_layout.addItem(self.spacer, row, column * 4 + 3)

    def remove_param_widgets(self, param):
        checkbox = self.param_checkboxes.pop(param, None)
        combobox = self.param_comboboxes.pop(param, None)
        if checkbox:
            checkbox.deleteLater()
        if combobox:
            combobox.deleteLater()


class FoldLineWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.sensor_pages = {}
        self.load_sensors()

    def initUI(self):
        self.setWindowTitle('多传感器检测')
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def load_sensors(self):
        try:
            sensors = config.get_sensors()
        except Exception as e:
            print(f"加载传感器配置时发生错误: {e}")
            return

        for sensor in sensors:
            sensor_name = sensor['sensor_name']
            params = sensor['param_name']
            page = SensorPage(sensor_name, params)
            self.sensor_pages[sensor_name] = page
            self.tab_widget.addTab(page, sensor_name)

    def update_data(self):
        for sensor in self.sensors:
            sensor_name = sensor['sensor_name']
            params = sensor['param_name']
            try:
                data = {param: simulate_sensor_data(sensor_name, param) for param in params}
            except Exception as e:
                print(f"获取传感器数据时发生错误: {e}")
                continue
            self.sensor_pages[sensor_name].update_data(data)

    def update_ui(self):
        try:
            old_sensors = self.sensors
            new_sensors = config.get_sensors()
            self.sensors = new_sensors
        except Exception as e:
            print(f"更新传感器配置时发生错误: {e}")
            return

        old_sensor_names = {sensor['sensor_name'] for sensor in old_sensors}
        new_sensor_names = {sensor['sensor_name'] for sensor in new_sensors}

        for sensor_name in old_sensor_names - new_sensor_names:
            if sensor_name in self.sensor_pages:
                self.tab_widget.removeTab(self.tab_widget.indexOf(self.sensor_pages[sensor_name]))
                del self.sensor_pages[sensor_name]

        for sensor_name in new_sensor_names - old_sensor_names:
            params = [param['param_name'] for param in new_sensors if param['sensor_name'] == sensor_name][0]
            page = SensorPage(sensor_name, params)
            self.sensor_pages[sensor_name] = page
            self.tab_widget.addTab(page, sensor_name)

        for sensor in new_sensors:
            sensor_name = sensor['sensor_name']
            param_name = sensor['param_name']
            old_sensor = next((s for s in old_sensors if s['sensor_name'] == sensor_name), None)
            page = self.sensor_pages[sensor_name]

            if old_sensor:
                for param in set(old_sensor['param_name']) - set(param_name):
                    page.remove_param(param)

                for param in set(param_name) - set(old_sensor['param_name']):
                    page.add_param(param)
            else:
                for param in param_name:
                    page.add_param(param)

            page.update_plots()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FoldLineWindow()
    ex.show()
    sys.exit(app.exec_())
