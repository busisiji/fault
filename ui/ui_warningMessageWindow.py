import sys
import json
import time
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QInputDialog, QMessageBox, QSizePolicy
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import config
from db.db_mysql import DB_MySQL
from ui.others.ui_fun import BaseWindow
from ui.qss import btn_css

class WarningMessageWindow(BaseWindow):
    """传感器配置界面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("历史报警")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.db = DB_MySQL()
        # 创建表
        with self.db:
            self.db.create_table(config.toname.get('历史报警'),
                                 [('time', 'DATETIME'),
                                  ('name', 'VARCHAR(255)'),
                                  ('value', 'DOUBLE'),
                                  ('unit', 'VARCHAR(255)'),
                                  ('warning_time', 'DATETIME'),
                                  ('desc', 'TEXT')])  # 状态 ：0 正常 1 异常
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_data_and_plot)
        self.read_data_and_plot()  # 初始化时显示柱状图

    def init_ui(self):
        layout = QVBoxLayout()

        # 创建绘图区域
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # 添加绘图区域和工具栏到布局中
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # 添加一个按钮，点击后设置定时时间
        self.set_timer_button = QPushButton("设置定时时间")
        self.set_timer_button.clicked.connect(self.set_timer_interval)
        layout.addWidget(self.set_timer_button)

        self.setLayout(layout)

    def set_timer_interval(self):
        # 获取用户输入的定时时间（单位：秒）
        interval, ok = QInputDialog.getInt(self, "设置定时时间", "请输入定时时间（秒）:", 3600, 1, 86400)
        if ok:
            self.timer.start(interval * 1000)  # QTimer 的时间间隔单位是毫秒

    def read_data_and_plot(self):
        # 假设 config.toname 是一个字典
        table_name = config.toname.get('历史报警')
        if table_name:
            with self.db:
                # 读取数据
                data = self.db.select_data(table_name, columns=['name'])
        else:
            raise ValueError("表名 '历史报警' 在配置中未找到")

        # 清除之前的绘图
        self.figure.clear()

        # 统计每个 name 出现的次数
        from collections import Counter
        name_counts = Counter([row['name'] for row in data])

        # 提取 x 轴和 y 轴数据
        names = list(name_counts.keys())
        counts = list(name_counts.values())

        # 创建一个新的子图
        ax = self.figure.add_subplot(111)

        # 绘制柱状图
        ax.bar(names, counts)
        ax.set_xlabel('Name')
        ax.set_ylabel('Count')
        ax.set_title('Name Frequency')
        ax.set_xticklabels(names, rotation=45)  # 旋转 x 轴标签以避免重叠

        # 更新画布
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WarningMessageWindow()
    window.show()
    sys.exit(app.exec_())
