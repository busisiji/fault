import logging

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib import pyplot as plt
# from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

w = 1200
h = 800

def setQMessageBox(title='提示',text='确认退出吗'):
    '''弹窗'''
    box = QMessageBox()
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    reply = box.exec()
    return reply


class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100, parent=None):
        # 第一步：创建一个Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        # 第二步：在父类中激活Figure窗口
        super(MyFigure, self).__init__(self.fig)  # 使用 FigureCanvas 的初始化方法

        # 第三步：创建一个子图，用于绘制图形用，111表示子图编号
        self.axes = self.fig.add_subplot(111)

        self.draw()  # 这是关键

    # 第四步：就是画图
    def plotsin(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)
        self.axes.plot(t, s)

    def plotcos(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.cos(2 * np.pi * t)  # 修改为余弦函数
        self.axes.plot(t, s)


class BaseWindow(QWidget):
    '''基类窗口'''
    def __init__(self,parent=None):
        super(BaseWindow, self).__init__(parent)
        self.parent = parent
        self.table_style = """
            QTableWidget {
                alternate-background-color: rgba(219, 219, 225, 0.8);
                background-color: white;
                border-radius: 5px;
            }
            QTableWidget::item:selected {
                color: #FFFFFF;
                background-color: #131E2F;
            }
            QHeaderView::section {
                border: 0px;
                height: 40px;
                width: 28px;
                color: rgb(253, 253, 253);
                background-color: rgb(56, 61, 93);
                font: 14px "微软雅黑";
            }
        """


    def show_message(self,text):
        QMessageBox.critical(self, "错误", text)

    def check_file_size(self, filenames):
        '''检查文件大小是否小于30行'''
        for filename in filenames:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    total = sum(1 for line in file)
                    if total < 30:
                        raise Exception(f'文件行数不足,{filename} 中只有 {total} 行的数据，请至少采集 30 行数据')
            except Exception as e:
                raise e
        return True

    def init_table(self,table):
        # 初始化表格内容为0
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = QTableWidgetItem('0')
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                table.setItem(row, col, item)

class MyLabel(QLabel):
    # 自定义信号，在文本改变时发射
    textChanged = pyqtSignal()

    def setText(self, text):
        super().setText(text)
        self.textChanged.emit()

class CollapsibleBox(QGroupBox):
    def __init__(self, title,content_area, parent=None):
        super(CollapsibleBox, self).__init__(title, parent)

        self.setCheckable(True)
        self.setChecked(False)

        self.toggle_button = QPushButton("展开")
        self.toggle_button.clicked.connect(self.on_toggled)

        self.content_area = content_area
        # self.setLayout(self.content_area)

    def on_toggled(self, checked):
        if checked:
            self.toggle_button.setText("折叠")
            self.content_area.show()
        else:
            self.toggle_button.setText("展开")
            self.content_area.hide()

class CollapsibleSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent=None):
        super(CollapsibleSplitterHandle, self).__init__(orientation, parent)
        self.collapsed = False
        self.arrow_button_size = 16

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionButton()

        rect = self.rect()
        opt.rect = QRect(0, 0, self.arrow_button_size, self.arrow_button_size)
        opt.state = QStyle.State_Enabled | QStyle.State_Active | QStyle.State_Horizontal
        opt.iconSize = QSize(self.arrow_button_size, self.arrow_button_size)

        if self.collapsed:
            opt.icon = self.style().standardIcon(QStyle.SP_TitleBarUnshadeButton)
        else:
            opt.icon = self.style().standardIcon(QStyle.SP_TitleBarShadeButton)

        painter.drawControl(QStyle.CE_PushButton, opt)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.collapsed:
                self.collapsed = False
                self.parent().restoreState(self.parent().saved_state)
            else:
                self.collapsed = True
                self.parent().saved_state = self.parent().saveState()
                self.parent().setSizes([self.arrow_button_size, self.parent().sizes()[1]])

            self.update()


class CollapsibleSplitter(QWidget):
    def __init__(self, orientation, parent=None):
        super(CollapsibleSplitter, self).__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QSplitter(orientation)
        self.splitter.setHandleWidth(30)

        self.handle = CollapsibleSplitterHandle(orientation, parent=self.splitter)

        self.layout.addWidget(self.splitter)

        self.splitter.splitterMoved.connect(self.handle.updateGeometry)

        self.saved_state = None

        self.handle.mouseReleaseEvent = self.handle.mouseReleaseEvent

    def addWidget(self, widget):
        self.splitter.addWidget(widget)