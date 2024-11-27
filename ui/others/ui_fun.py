import datetime
import json
import logging

import numpy as np
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib import pyplot as plt
# from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import config
from utils.my_thread import NewMyThread, MyThread

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
    _single_update_ui = pyqtSignal()
    _single_import_table = pyqtSignal(tuple)
    _single_import_table_db = pyqtSignal(tuple)
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
        self.thread = None
        self.sensors = config.get_sensors()
        self._single_update_ui.connect(self.update_ui)
        self._single_import_table.connect(self.import_table_thread)

        self._single_import_table_db.connect(self.db_to_table_thread)
    def update_ui(self):
        pass

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

    # 辅助函数：安全调用槽函数
    def safe_call(self, func,text):
        try:
            self.threadFun = ['开始预测','保存配置','导入表格']
            if self.parent:
                if self.parent.IsRun:
                    QMessageBox.warning(self, "警告", "有任务运行中!")
                    return
                else:
                    self.parent.setRun(text)
            func()
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            QMessageBox.warning(self, "错误", f"{e}")
            if self.parent and text not in self.threadFun:
                self.parent.setRun()
        else:
            if self.parent and text not in self.threadFun:
                self.parent.setRun()
    ''''''''''''''''''''''''
    def import_table(self):
        self.Is_import = True
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "CSV Files (*.csv);;Excel Files (*.xlsx)",options=options)

        if not file_path:
            self.parent.setRun()
            return

        # 读取文件
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            QMessageBox.warning(self, "错误", "不支持的文件类型")
            self.parent.setRun()
            return

        # 获取当前标签页的表格
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            QMessageBox.warning(self, "错误", "没有选中的标签页")
            self.parent.setRun()
            return

        table = current_tab.findChild(QTableWidget)
        if not table:
            QMessageBox.warning(self, "错误", "没有找到表格")
            self.parent.setRun()
            return

        # 获取表格的列名
        headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]

        # 分块读取文件
        self.chunk_size = 300  # 每次读取的行数

        if file_path.endswith('.csv'):
            reader = pd.read_csv(file_path, chunksize=self.chunk_size)
        elif file_path.endswith('.xlsx'):
            reader = pd.read_excel(file_path, chunksize=self.chunk_size)
        else:
            QMessageBox.warning(self, "错误", "不支持的文件类型")
            self.parent.setRun()
            return
        row_index = table.rowCount()
        self.reader_nums = 0
        self.add_nums = 0
        chunks = []
        for chunk in reader:
            chunks.append(chunk)
            # 处理时间列
            if 'Time' in chunk.columns:
                chunk['Time'] = pd.to_datetime(chunk['Time'], errors='coerce')
                chunk['Time'] = chunk['Time'].dt.strftime("%Y-%m-%d %H:%M:%S")
                chunk['Time'] = chunk['Time'].fillna('')

            # 导入数据
            for _, row in chunk.iterrows():
                row_data = []
                for header in headers[:-3]:  # 排除最后三列
                    if header in row:
                        row_data.append(str(row[header]))
                    # else:
                    #     row_data.append('')
                if not row_data:
                    continue

                # 添加新行
                table.insertRow(row_index)
                table.setRowHeight(row_index, 40)
            self.reader_nums = self.reader_nums + self.chunk_size
        for chunk in chunks:
            # 预测
            self._single_import_table.emit((chunk,headers,table,row_index))
            # thread = MyThread(lambda: self.import_table_thread((chunk, headers, table, row_index))).start()
            # thread = NewMyThread(lambda : self.import_table_thread(chunk,headers,table,row_index)).start()
            # self.thread._signal.connect(self.theard_finished_import)
            # thread.start()
            row_index = row_index + self.chunk_size
    def import_table_thread(self,s):
        try:
            chunk, headers, table, row_index = s
            # 处理时间列
            if 'Time' in chunk.columns:
                chunk['Time'] = pd.to_datetime(chunk['Time'], errors='coerce')
                chunk['Time'] = chunk['Time'].dt.strftime("%Y-%m-%d %H:%M:%S")
                chunk['Time'] = chunk['Time'].fillna('')

            # 导入数据
            for _, row in chunk.iterrows():
                row_data = []
                for header in headers[:-3]:  # 排除最后三列
                    if header in row:
                        row_data.append(str(row[header]))
                    # else:
                    #     row_data.append('')
                if not row_data:
                    continue
                #
                # # 添加新行
                # table.insertRow(row_index)
                # table.setRowHeight(row_index, 40)

                # 填充参数值
                for column, value in enumerate(row_data):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_index, column, item)

                # 添加时间列
                if 'Time' in row:
                    time_value = str(row['Time'])
                    item = QTableWidgetItem(time_value)
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_index, table.columnCount() - 3, item)

                # 添加编辑和删除按钮
                self.add_edit_button(table, row_index)
                self.add_delete_button(table, row_index)

                row_index = row_index + 1

        finally:
            self.add_nums = self.add_nums + self.chunk_size
            print(self.add_nums,self.reader_nums)
            if self.add_nums >= self.reader_nums:
                self.parent.setRun()
    def db_to_table_thread(self,s):
        try:
            batch,table = s
            for row_data in batch:
                update_time = row_data['update_time']
                params = json.loads(row_data['params'])

                row_index = table.rowCount()
                table.insertRow(row_index)
                table.setRowHeight(row_index, 40)

                # 填充数据
                for column, param_name in enumerate(
                        table.horizontalHeaderItem(j).text() for j in range(table.columnCount() - 3)):
                    value = params.get(param_name, "")
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_index, column, item)

                # 填充更新时间
                item = QTableWidgetItem(update_time.strftime(config.time_format))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_index, table.columnCount() - 3, item)

                # 添加编辑和删除按钮
                self.add_edit_button(table, row_index)
                self.add_delete_button(table, row_index)
        finally:

            self.batch_num = self.batch_num + self.load_batch_size
            print(self.batch_num,self.filtered_data)
            if self.batch_num >=  len(self.filtered_data):
                self.parent.setRun()
    # def theard_finished_import(self,e):
    #     try:
    #         if not self.Is_import:
    #             return
    #         print(self.add_nums , self.reader_nums)
    #         if self.add_nums >= self.reader_nums:
    #             self.parent.setRun()
    #             self.Is_import = False
    #             if e != 'OK':
    #                 QMessageBox.critical(self, '错误', f'模型预测失败: {str(e)}')
    #     except Exception as e:
    #         print(e)
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



class FixedHeaderTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建主表格
        self.main_table = QTableWidget()
        self.main_table.heiRowNum = 0

        # 创建固定表头
        self.fixed_header = QTableWidget()
        self.fixed_header.setColumnCount(self.main_table.columnCount())
        self.fixed_header.setRowCount(3)
        self.fixed_header.verticalHeader().setVisible(False)
        self.fixed_header.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 初始化固定表头
        self.name_list = ["平均值", "最大值", "最小值"]
        for i, name in enumerate(self.name_list):
            self.fixed_header.setVerticalHeaderItem(i, QTableWidgetItem(name))
            self.fixed_header.setRowHeight(i, 40)

        # 设置固定表头的列宽与主表格一致
        for column in range(self.main_table.columnCount()):
            self.fixed_header.setColumnWidth(column, self.main_table.columnWidth(column))

        # 连接滚动条信号
        self.main_table.verticalScrollBar().valueChanged.connect(self.sync_scroll)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.fixed_header)
        layout.addWidget(self.main_table)
        self.setLayout(layout)

    def sync_scroll(self, value):
        # 同步滚动条位置
        self.fixed_header.horizontalScrollBar().setValue(value)

    def display_averages(self, averages, max_values, min_values):
        for column, average in enumerate(averages):
            if column < self.fixed_header.columnCount() - 3:
                self.set_value(0, column, average)

        for column, max_value in enumerate(max_values):
            if column < self.fixed_header.columnCount() - 3:
                self.set_value(1, column, max_value)

        for column, min_value in enumerate(min_values):
            if column < self.fixed_header.columnCount() - 3:
                self.set_value(2, column, min_value)

        for i in range(3):
            self.update_time(i)

    def set_value(self, row, column, value):
        item = QTableWidgetItem(f"{value:.2f}")
        item.setTextAlignment(Qt.AlignCenter)
        item.setBackground(QColor(0, 0, 255))  # 设置背景颜色为蓝色
        self.fixed_header.setItem(row, column, item)

    def update_time(self, row):
        update_time_item = QTableWidgetItem(datetime.datetime.now().strftime(config.time_format))
        update_time_item.setTextAlignment(Qt.AlignCenter)
        update_time_item.setBackground(QColor(0, 255, 0))  # 设置背景颜色为绿色
        self.fixed_header.setItem(row, self.fixed_header.columnCount() - 3, update_time_item)

    def calculate_average_max_min(self):
        row_count = self.main_table.rowCount() - 3  # 减去平均值、最大值和最小值行
        column_count = self.main_table.columnCount()

        averages = [0] * (column_count - 3)  # 倒数三列不计算
        max_values = [float('-inf')] * (column_count - 3)  # 初始值为负无穷
        min_values = [float('inf')] * (column_count - 3)  # 初始值为正无穷

        for column in range(column_count - 3):  # 倒数三列不计算
            total = 0
            count = 0
            for row in range(3, row_count + 3):  # 从第四行开始计算
                item = self.main_table.item(row, column)
                if item and item.text():
                    try:
                        value = float(item.text())
                        total += value
                        count += 1
                        if value > max_values[column]:
                            max_values[column] = value
                        if value < min_values[column]:
                            min_values[column] = value
                    except ValueError:
                        pass
            if count > 0:
                averages[column] = total / count

        return averages, max_values, min_values

    def refresh_table(self):
        averages, max_values, min_values = self.calculate_average_max_min()
        self.display_averages(averages, max_values, min_values)

class TableWidgetWithAverages(QTableWidget):
    def __init__(self, parent=None):
        """参数表格"""
        super().__init__(parent)
        self.name_list = ["平均值", "最大值", "最小值"]
        self.heiRowNum = len(self.name_list)
        for i in range(self.heiRowNum):
            name = self.name_list[i]
            # 在初始化时插入三行用于显示平均值、最大值和最小值
            self.insertRow(i)
            self.setRowHeight(i, 40)

            # 设置行头显示
            self.setVerticalHeaderItem(i, QTableWidgetItem(name))

    def display_averages(self, averages, max_values, min_values):
        # 清除现有平均值、最大值和最小值行的内容
        # for row in range(3):
        #     for column in range(self.columnCount()):
        #         self.setItem(row, column, None)

        # 设置平均值
        for column, average in enumerate(averages):
            if column < self.columnCount() - 3:  # 倒数三列不计算
                self.set_value(0,column,average)

        # 设置最大值
        for column, max_value in enumerate(max_values):
            if column < self.columnCount() - 3:  # 倒数三列不计算
                self.set_value(1,column,max_value)
        # 设置最小值
        for column, min_value in enumerate(min_values):
            if column < self.columnCount() - 3:  # 倒数三列不计算
                self.set_value(2,column,min_value)

        for i in range(3):
            self.update_time(i)

    def set_value(self,row,column,value):
        item = QTableWidgetItem(f"{value:.2f}")
        item.setTextAlignment(Qt.AlignCenter)
        item.setBackground(QColor(0, 0, 255))  # 设置背景颜色为蓝色
        self.setItem(row, column, item)

    def update_time(self,row):
        # 倒数第三列显示更新时间
        update_time_item = QTableWidgetItem(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        update_time_item.setTextAlignment(Qt.AlignCenter)
        update_time_item.setBackground(QColor(0, 255, 0))  # 设置背景颜色为绿色
        self.setItem(row, self.columnCount() - 3, update_time_item)

    def calculate_average_max_min(self):
        row_count = self.rowCount() - 3  # 减去平均值、最大值和最小值行
        column_count = self.columnCount()

        averages = [0] * (column_count - 3)  # 倒数三列不计算
        max_values = [float('-inf')] * (column_count - 3)  # 初始值为负无穷
        min_values = [float('inf')] * (column_count - 3)  # 初始值为正无穷

        for column in range(column_count - 3):  # 倒数三列不计算
            total = 0
            count = 0
            for row in range(3, row_count + 3):  # 从第四行开始计算
                item = self.item(row, column)
                if item and item.text():
                    try:
                        value = float(item.text())
                        total += value
                        count += 1
                        if value > max_values[column]:
                            max_values[column] = value
                        if value < min_values[column]:
                            min_values[column] = value
                    except ValueError:
                        pass
            if count > 0:
                averages[column] = total / count

        return averages, max_values, min_values

    def refresh_table(self):
        # 计算平均值、最大值和最小值
        averages, max_values, min_values = self.calculate_average_max_min()
        # 显示平均值、最大值和最小值
        self.display_averages(averages, max_values, min_values)
#


class SwitchButton(QWidget):
    """开关按钮"""
    def __init__(self, parent=None):
        super(SwitchButton, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.resize(70, 30)
        # SwitchButtonstate：True is ON，False is OFF
        self.state = False
        self.setFixedSize(80, 40)

    def mousePressEvent(self, event):
        '''
        set click event for state change
        '''
        super(SwitchButton, self).mousePressEvent(event)
        self.state = False if self.state else True
        self.update()

    def paintEvent(self, event):
        '''Set the button'''
        super(SwitchButton, self).paintEvent(event)

        # Create a renderer and set anti-aliasing and smooth transitions
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # Defining font styles
        font = QFont("Arial")
        font.setPixelSize(self.height()//3)
        painter.setFont(font)
        # SwitchButton state：ON
        if self.state:
            # Drawing background
            painter.setPen(Qt.NoPen)
            brush = QBrush(QColor('#bd93f9'))
            painter.setBrush(brush)
            # Top left corner of the rectangle coordinate
            rect_x = 0
            rect_y = 0
            rect_width = self.width()
            rect_height = self.height()
            rect_radius = self.height()//2
            painter.drawRoundedRect(rect_x, rect_y, rect_width, rect_height, rect_radius, rect_radius)
            # Drawing slides circle
            painter.setPen(Qt.NoPen)
            brush.setColor(QColor('#ffffff'))
            painter.setBrush(brush)
            # Phase difference pixel point
            # Top left corner of the rectangle coordinate
            diff_pix = 3
            rect_x = self.width() - diff_pix - (self.height()-2*diff_pix)
            rect_y = diff_pix
            rect_width = (self.height()-2*diff_pix)
            rect_height = (self.height()-2*diff_pix)
            rect_radius = (self.height()-2*diff_pix)//2
            painter.drawRoundedRect(rect_x, rect_y, rect_width, rect_height, rect_radius, rect_radius)

            # ON txt set
            painter.setPen(QPen(QColor('#ffffff')))
            painter.setBrush(Qt.NoBrush)
            painter.drawText(QRect(int(self.height()/3), int(self.height()/3.5), 50, 20), Qt.AlignLeft, 'ON')
        # SwitchButton state：OFF
        else:
            # Drawing background
            painter.setPen(Qt.NoPen)
            brush = QBrush(QColor('#525555'))
            painter.setBrush(brush)
            # Top left corner of the rectangle coordinate
            rect_x = 0
            rect_y = 0
            rect_width = self.width()
            rect_height = self.height()
            rect_radius = self.height()//2
            painter.drawRoundedRect(rect_x, rect_y, rect_width, rect_height, rect_radius, rect_radius)

            # Drawing slides circle
            pen = QPen(QColor('#999999'))
            pen.setWidth(1)
            painter.setPen(pen)
            # Phase difference pixel point
            diff_pix = 3
            # Top left corner of the rectangle coordinate
            rect_x = diff_pix
            rect_y = diff_pix
            rect_width = (self.height()-2*diff_pix)
            rect_height = (self.height()-2*diff_pix)
            rect_radius = (self.height()-2*diff_pix)//2
            painter.drawRoundedRect(rect_x, rect_y, rect_width, rect_height, rect_radius, rect_radius)

            # OFF txt set
            painter.setBrush(Qt.NoBrush)
            painter.drawText(QRect(int(self.width()*1/2), int(self.height()/3.5), 50, 20), Qt.AlignLeft, 'OFF')


