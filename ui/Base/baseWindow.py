import datetime
import json
import os
import time

import pandas as pd
from PyQt5.QtCore import pyqtSignal, QMutex, QMetaObject, Q_ARG, pyqtSlot, QThreadPool, QRunnable, Qt, QEventLoop, \
    QObject
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QFileDialog, QTableWidget, QComboBox

import config
from utils.frozen_dir import exists_path
from utils.utils import get_time_now

class ImportTask(QRunnable):
    class Signals(QObject):
        task_completed = pyqtSignal()
    def __init__(self, chunk, headers, start_row_index, base_window ,type):
        '''导入表格线程池'''
        super(ImportTask, self).__init__()
        self.chunk = chunk
        self.headers = headers
        self.start_row_index = start_row_index
        self.base_window = base_window
        self.type = type
        self.signals = self.Signals()
    def run(self):
        row_data_list = []
        row_data = []
        for _, row in self.chunk.iterrows():
            row_data = [str(row[header]) for header in self.headers[:-3] if header in row]
            if row_data:
                row_data_list.append((row, row_data))
        if self.type == 'import_table_batch':
            QMetaObject.invokeMethod(self.base_window, "import_table_batch", Qt.QueuedConnection,
                                 Q_ARG(list, row_data_list), Q_ARG(int, self.start_row_index))
        self.signals.task_completed.emit()

class PredictionTask(QRunnable):
    class Signals(QObject):
        prediction_completed = pyqtSignal(list, list, int)

    def __init__(self, chunk, headers, start_row_index, base_window, model, use_features):
        """模型预测线程池"""
        super(PredictionTask, self).__init__()
        self.chunk = chunk
        self.headers = headers
        self.start_row_index = start_row_index
        self.base_window = base_window
        self.model = model
        self.use_features = use_features
        self.signals = self.Signals()

    def run(self):
        try:
            preds = self.base_window.parent.fualt_model.predict_models(self.chunk)

            if preds:
                predictions = [pred[3] for pred in preds]
                # print(f'第{self.base_window.completed_tasks}轮：',predictions)
                Allpredictions = [pred[2] for pred in preds]
                QMetaObject.invokeMethod(self.base_window, "update_prediction_results", Qt.QueuedConnection,
                                         Q_ARG(list, predictions),Q_ARG(list, Allpredictions), Q_ARG(int, self.start_row_index))
                # self.signals.prediction_completed.emit(predictions, Allpredictions, self.start_row_index)
            else:
                self.base_window.error_tasks_return('模型预测为空：')
        except Exception as e:
            self.base_window.error_tasks_return('模型预测失败：',e)


class BaseWindow(QWidget):
    _single_update_ui = pyqtSignal()  # 更新UI
    _all_tasks_completed = pyqtSignal()  # 所有任务完成信号

    _mutex_import_table = QMutex()

    def __init__(self, parent=None):
        super(BaseWindow, self).__init__(parent)
        self.parent = parent
        self.thread = None
        self.chunk_size = 300  # 每次读取的行数
        self.sensors = config.get_sensors()
        self.total_tasks = 0  # 总任务数
        self.completed_tasks = 0  # 已完成任务数
        self.type = '导入'

        self.thread_pool = QThreadPool()
        self._all_tasks_completed.connect(self.all_tasks_completed)
        self._single_update_ui.connect(self.update_ui)

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

    def update_ui(self):
        pass

    # 更新传感器配置
    def get_sensor_by_name(self, sensor_name):
        return next((s for s in self.sensors if s['sensor_name'] == sensor_name), None)
    def show_message(self, text):
        QMessageBox.critical(self, "错误", text)

    def check_file_size(self, filenames):
        '''检查文件大小是否小于30行'''
        for filename in filenames:
            with open(filename, 'r', encoding='utf-8') as file:
                total = sum(1 for line in file)
                if total < 30:
                    raise Exception(f'文件行数不足,{filename} 中只有 {total} 行的数据，请至少采集 30 行数据')
        return True

    def init_table(self, table):
        # 初始化表格内容为0
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = QTableWidgetItem('0')
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                table.setItem(row, col, item)
    def delete_empty_rows(self, table):
        """删除空行"""
        # 获取表格的行数和列数
        row_count = table.rowCount()
        col_count = table.columnCount()

        # 从最后一行开始向前遍历，避免删除行后索引变化的问题
        for row in range(row_count - 1, self.tRN - 1, -1):
            is_empty = True
            for col in range(col_count):
                item = table.item(row, col)
                if item and item.text().strip():
                    is_empty = False
                    break
            if is_empty:
                table.removeRow(row)
    def error_tasks_return(self,e):
        if self.completed_tasks >= self.total_tasks:
            self.show_message(e)
            self.parent.setRun()
    def check_tasks_completed(self):
        """一个线程结束"""
        self.completed_tasks = self.completed_tasks + 1
        # 强制刷新
        self.repaint()
        self.update()
        # 检查所有任务是否完成
        if self.thread_pool.activeThreadCount() != 0:
            return
        if self.completed_tasks >= self.total_tasks :
            self._all_tasks_completed.emit()
        # elif self.completed_tasks >= self.total_tasks :
        #     self._all_tasks_completed.emit('预测')
    def all_tasks_completed(self):
        """所有线程结束"""
        print('------线程结束------')
        if self.type == '导入':
            self.solt_table.refresh_table()
        # self.delete_empty_rows(self.solt_table)
        self.parent.setRun()
    def safe_call(self, func, text):
        try:
            self.threadFun = ['开始预测','数据读取','导入表格','开始训练']
            if self.parent and self.parent.IsRun:
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
    """--------------------表格操作-----------------------"""

    @pyqtSlot(list, int)
    def import_table_batch(self, row_data_list, start_row_index):
        table = self.solt_table
        time_name = 'Time'
        if not table:
            return

        if not row_data_list and self.completed_tasks >= self.total_tasks - 1:
            self.delete_empty_rows(self.solt_table)
            self.show_message("没有对应的列可以导入")
            return

        items = []
        for row_index, (row, row_data) in enumerate(row_data_list, start=start_row_index):
            table.setRowHeight(row_index, 40)
            values = []
            for column, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                items.append((row_index, column, item))
                values.append(value)

            if time_name in row:
                time_value = str(row[time_name])
                item = QTableWidgetItem(time_value)
                item.setTextAlignment(Qt.AlignCenter)
                items.append((row_index, table.columnCount() - 3, item))

            # print(f"第{row_index}行: {values}, {time_value}")

        # 批量设置表格项
        for row, col, item in items:
            table.setItem(row, col, item)

        for row_index in range(start_row_index, start_row_index + len(row_data_list)):
            self.add_edit_button(table, row_index)
            self.add_delete_button(table, row_index)

        # self._mutex_import_table.unlock()
        # if start_row_index + self.chunk_size >= self.reader_nums:
        #     self.solt_table.refresh_table()
        #     self.parent.setRun()

    def import_table(self):
        try:
            self.type = '导入'
            Is_run = False
            self.Is_import = True
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)

            if not file_path:
                self.parent.setRun()
                return

            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                self.parent.setRun()
                QMessageBox.warning(self, "错误", "不支持的文件类型")
                return

            current_tab = self.tab_widget.currentWidget()
            if not current_tab:
                self.parent.setRun()
                QMessageBox.warning(self, "错误", "没有选中的标签页")
                return

            self.solt_table = current_tab.findChild(QTableWidget)
            if not self.solt_table:
                self.parent.setRun()
                QMessageBox.warning(self, "错误", "没有找到表格")
                return

            headers = [self.solt_table.horizontalHeaderItem(col).text() for col in range(self.solt_table.columnCount())]

            # # 检查当前行数
            # current_row_count = self.solt_table.rowCount()
            # if current_row_count > 3000:
            #     reply = QMessageBox.question(self, "提示", "表格当前行数过高，是否清空再导入？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            #     if reply == QMessageBox.Yes:
            #         self.solt_table.setRowCount(self.tRN)

            if file_path.endswith('.csv'):
                reader = pd.read_csv(file_path, chunksize=self.chunk_size)
            elif file_path.endswith('.xlsx'):
                reader = pd.read_excel(file_path, chunksize=self.chunk_size)
            else:
                self.parent.setRun()
                QMessageBox.warning(self, "错误", "不支持的文件类型")
                return

            self.reader_nums = 0
            self.add_nums = 0
            self.total_tasks = 0
            self.completed_tasks = 0

            for chunk in reader:
                self.total_tasks += 1
                row_index = self.solt_table.rowCount()
                self.solt_table.setRowCount(row_index+len(chunk))

                if 'Time' in chunk.columns:
                    chunk['Time'] = pd.to_datetime(chunk['Time'], errors='coerce').dt.strftime("%Y-%m-%d %H:%M:%S").fillna('')

                task = ImportTask( chunk, headers, row_index, self , "import_table_batch")
                task.signals.task_completed.connect(self.check_tasks_completed)
                self.thread_pool.start(task)
                Is_run = True
                self.reader_nums += len(chunk)
            if not Is_run:
                self.parent.setRun()
            # self.thread_pool.waitForDone()
        except Exception as e:
            self.parent.setRun()
            self.show_message(str(e))
        # finally:
        #     self.parent.setRun()

    def export_table(self,type='预测'):
        file_name = '预测结果'
        start_index = 0

        # 获取当前选中的表格
        current_tab = self.tab_widget.currentWidget()
        sensor_name = self.tab_widget.tabText(self.tab_widget.currentIndex())
        if not current_tab:
            QMessageBox.warning(self, "警告", "没有选中的表格")
            return
        table = current_tab.findChild(QTableWidget)
        if not table:
            QMessageBox.warning(self, "警告", "当前标签页中没有表格")
            return
        if type == '运维':
            cb_4 = current_tab.findChild(QComboBox, "cb_4")
            if not cb_4:
                self.show_message("获取当前标签页的状态失败")
                return
            file_name = cb_4.currentText()
            start_index = self.tRN

        # 获取表格数据

        data = []
        for row in range(start_index,table.rowCount()):
            row_data = []
            for col in range(table.columnCount() - 2):  # 跳过最后两列
                item = table.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")  # 如果单元格为空，则添加空字符串
            data.append(row_data)

        # 获取列名
        headers = []
        for col in range(table.columnCount() - 2):  # 跳过最后两列
            headers.append(table.horizontalHeaderItem(col).text())

        # 创建 DataFrame
        df = pd.DataFrame(data, columns=headers)

        # 选择保存目录
        directory = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if not directory:
            return

        exists_path(os.path.join(directory, sensor_name))
        # 构建完整的文件路径
        file_path = os.path.join(directory, sensor_name,file_name+'.xlsx')

        # 检查文件是否存在
        if os.path.exists(file_path):
            reply = QMessageBox.question(self, '文件已存在', '文件已存在，是否覆盖？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # 将 DataFrame 写入 XLSX 文件
        try:

            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "提示", "数据已成功导出到 {}".format(file_path))
        except Exception as e:
            QMessageBox.critical(self, "错误", "导出数据时发生错误：{}".format(str(e)))
    """--------------------数据库操作-----------------------"""
    def load_to_db(self):
        try:
            self.type = '导入'
            Is_run = False
            current_index = self.tab_widget.currentIndex()
            if current_index >= 0:
                current_tab = self.tab_widget.widget(current_index)
                sensor_name = self.tab_widget.tabText(current_index)
                current_status = current_tab.findChild(QComboBox, "cb_4").currentText()

                condition = f"sensor_name = '{sensor_name}' AND status = '{current_status}'"

                with self.db:
                    self.filtered_data = self.db.select_data(self.table_name, condition=condition)

                current_tab = self.tab_widget.widget(current_index)

                self.solt_table = current_tab.findChild(QTableWidget)
                current_row_count = self.solt_table.rowCount()
                headers = [self.solt_table.horizontalHeaderItem(col).text() for col in
                           range(self.solt_table.columnCount())]

                # 检查当前行数
                # if current_row_count > 3000:
                #     reply = QMessageBox.question(self, "提示", "表格当前行数过高，是否清空再导入？",
                #                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                #     if reply == QMessageBox.Yes:
                #         self.solt_table.setRowCount(self.tRN)

                self.reader_nums = 0
                self.add_nums = 0
                self.total_tasks = int(len(self.filtered_data) / self.chunk_size) + 1
                self.completed_tasks = 0

                for i in range(0, len(self.filtered_data), self.chunk_size):
                    row_index = self.solt_table.rowCount()
                    batch = self.filtered_data[i:i + self.chunk_size]

                    # 将 params 列中的数据解析为单独的列
                    chunk = pd.DataFrame(batch)
                    # 将 params 列从字符串转换为字典
                    chunk['params'] = chunk['params'].apply(eval)
                    # 提取 update_time 列并重命名为 Time
                    chunk['Time'] = chunk['update_time']
                    # 动态生成新的列
                    params_df = pd.json_normalize(chunk['params'])
                    chunk = pd.concat([chunk[['Time']], params_df], axis=1)

                    self.solt_table.setRowCount(row_index+len(chunk))

                    task = ImportTask(chunk, headers, row_index, self , "import_table_batch")
                    task.signals.task_completed.connect(self.check_tasks_completed)
                    self.thread_pool.start(task)
                    Is_run = True
                    self.reader_nums += len(batch)
                # self.thread_pool.waitForDone()
                if not Is_run:
                    self.parent.setRun()
            else:
                self.parent.setRun()
                QMessageBox.warning(None, "警告", "请选择一个传感器标签页")
        except Exception as e:
            self.parent.setRun()
            self.show_message(str(e))
    def save_to_db(self, mode='覆盖', current_tab=None):
        if mode == '不保存':
            return
        if current_tab is None:
            current_tab = self.tab_widget.currentWidget()

        cb_4 = current_tab.findChild(QComboBox, "cb_4")
        cb_5 = current_tab.findChild(QComboBox, "cb_5")

        try:
            with self.db:
                data = []
                table = current_tab.findChild(QTableWidget)
                row_count = table.rowCount()
                column_count = table.columnCount() - 3  # 排除编辑、删除按钮和更新时间列
                sensor_name = self.tab_widget.tabText(self.tab_widget.indexOf(current_tab))

                for row in range(self.tRN,row_count):
                    row_data = {}
                    params = {}
                    for column in range(column_count):
                        item = table.item(row, column)
                        if item is not None:
                            params[table.horizontalHeaderItem(column).text()] = item.text()
                        else:
                            params[table.horizontalHeaderItem(column).text()] = ""

                    if not all(value == "" for value in params.values()):
                        update_time_str = table.item(row, table.columnCount() - 3).text()
                        update_time = datetime.datetime.strptime(update_time_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        row_data['status'] = cb_4.currentText()  # 状态
                        row_data['update_time'] = update_time  # 更新时间
                        row_data['sensor_name'] = sensor_name  # 传感器名称
                        row_data['params'] = json.dumps(params)  # 参数
                        data.append(row_data)

                if mode == '覆盖':
                    self.db.delete_data(self.table_name, f"status = '{cb_4.currentText()}' AND sensor_name = '{sensor_name}'")

                self.db.bulk_insert_data(self.table_name, data)
        except Exception as e:
            if mode == '覆盖':
                self.db.delete_data(self.table_name,
                                    f"status = '{cb_4.currentText()}' AND sensor_name = '{sensor_name}'")

            self.db.bulk_insert_data(self.table_name, data)
        except Exception as e:
            QMessageBox.critical(None, "错误", f"保存数据时发生错误: {str(e)}")

    """--------------------模型操作-----------------------"""
    def start_prediction(self):
        try:
            Is_run = False
            model_directory = self.save_path_lineedit.text()

            # 获取当前选中的传感器标签页
            current_tab = self.tab_widget.currentWidget()
            if current_tab:
                self.solt_table = current_tab.findChild(QTableWidget)
                sensor_name = self.tab_widget.tabText(self.tab_widget.currentIndex())

                # 加载模型
                model_path = os.path.join(model_directory, sensor_name)
                if not os.path.exists(model_path):
                    QMessageBox.warning(self, "警告", f"模型目录 {model_path} 不存在")
                    self.parent.setRun()
                    return


                # 初始化故障诊断模型
                self.parent.fualt_model.load_train_info(model_path)


                # 加载的模型
                self.parent.fualt_model.load_models(model_path)
                if not self.parent.fualt_model.Models:
                    self.parent.setRun()
                    QMessageBox.warning(self, "警告", "没有加载模型")
                    return

                # 获取表头
                headers = [self.solt_table.horizontalHeaderItem(col).text() for col in range(self.solt_table.columnCount() - self.tCN)]

                # 获取数据
                data = []
                for row in range(self.tRN, self.solt_table.rowCount()):
                    row_data = {}
                    for col in range(self.solt_table.columnCount() - self.tCN):  # 排除编辑、删除按钮和更新时间列
                        item = self.solt_table.item(row, col)
                        if item:
                            row_data[headers[col]] = float(item.text())
                    if row_data:
                        data.append(row_data)

                if not data:
                    QMessageBox.warning(self, "警告", "表格中没有数据")
                    self.parent.setRun()
                    return

                # 过滤数据，只保留 训练 列的数据
                filtered_data = []
                for row_data in data:
                    filtered_row = [row_data.get(feature, None) for feature in self.parent.fualt_model.use_features]
                    if all(x is not None and x != '' for x in filtered_row):  # 确保没有空值或空字符串，允许 0.0 存在
                        filtered_data.append(filtered_row)

                if not filtered_data:
                    QMessageBox.warning(self, "警告", "没有有效的数据用于预测")
                    self.parent.setRun()
                    return

                # 分批次处理数据
                self.total_tasks = 0
                self.completed_tasks = 0
                chunk_size = 3

                # df = pd.DataFrame(data)
                start_row_index = self.tRN

                # 检查当前行数
                if len(filtered_data) > 300:
                    reply = QMessageBox.question(self, "提示", "预测数据时间较长，请耐心等待",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No:
                        QMessageBox.question(self, "提示", "已取消预测")
                        self.parent.setRun()

                        return

                for i in range(0, len(filtered_data), chunk_size):
                    print(f'-------------第{self.total_tasks}轮---------------')
                    # chunk = df.iloc[i:i + chunk_size]
                    chunk_data = filtered_data[i:i + chunk_size]
                    self.total_tasks += 1

                    task = PredictionTask(chunk_data, headers, start_row_index, self, self.parent.fualt_model, self.parent.fualt_model.use_features)
                    task.signals.prediction_completed.connect(self.update_prediction_results)
                    self.thread_pool.start(task)
                    Is_run = True
                    start_row_index = start_row_index + len(chunk_data)
                # self.thread_pool.waitForDone()
                if not Is_run:
                    self.parent.setRun()
        except Exception as e:
            self.parent.setRun()
            self.show_message(str(e))

    @pyqtSlot(list, list, int)
    def update_prediction_results(self, predictions, Allpredictions, start_row_index):
        items = []
        for j, pred in enumerate(predictions):
            item = QTableWidgetItem(str(pred))
            item.setTextAlignment(Qt.AlignCenter)
            item.setToolTip(str(Allpredictions[j]))  # 设置单元格的提示信息
            items.append((j + start_row_index, self.solt_table.columnCount() - self.tCN, item))
        print(f'第{self.completed_tasks}轮预测结果')

        # 批量设置表格项
        for row, col, item in items:
            self.solt_table.setItem(row, col, item)
        self.completed_tasks = self.completed_tasks + 1
        # self.check_tasks_completed()
        if self.thread_pool.activeThreadCount() != 0:
            return
        if self.completed_tasks >= self.total_tasks :
            self._all_tasks_completed.emit()
