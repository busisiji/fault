import datetime
import logging
import threading
import time
from collections import Counter

import numpy as np
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QLabel
from pandas import DataFrame

import config
from utils.collect import get_new_datas

class Worker(QThread):
    finished = pyqtSignal()

    def run(self):
        # 这里执行耗时操作
        # 例如：数据库查询、网络请求等
        self.finished.emit()

class MyThread(QThread):
    '''自定义线程类'''
    _signal = pyqtSignal()
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)
        self._signal.emit()

    def get_result(self):
        threading.Thread.join(self) # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None

class NewMyThread(QThread):
    '''自定义线程类'''
    _signal = pyqtSignal(str)
    def __init__(self, func, args=()):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            self.result = self.func(*self.args)
        except Exception as e:
            self._signal.emit(e)
        else:
            self._signal.emit('OK')

    def get_result(self):
        self.wait()  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None


class DataProcessingThread(QThread):
    data_processed = pyqtSignal(list, list)

    def __init__(self, param_names, results, param_checkboxes, lines, axes, param_positions, time_axis, data):
        super().__init__()
        """绘图"""
        self.param_names = param_names
        self.results = results
        self.param_checkboxes = param_checkboxes
        self.lines = lines
        self.axes = axes
        self.param_positions = param_positions
        self.time_axis = time_axis
        self.data = data

    def run(self):
        current_time = datetime.datetime.now()
        processed_params = []
        processed_results = []

        for param, value in zip(self.param_names, self.results):
            if self.param_checkboxes.get(param) and self.param_checkboxes[param].isChecked():
                try:
                    param = config.convert_to_db_columns([param])[0]
                except Exception as e:
                    logging.error(f"转换参数时发生错误: {e}")
                    continue

                if value is not None:
                    try:
                        value = float(value)
                    except ValueError as e:
                        logging.error(f"转换值时发生错误: {e}")
                        continue

                    self.data[param].append(value)
                    self.time_axis[param].append(current_time)
                    if param in self.lines:
                        positions = self.param_positions[param]
                        if positions in self.axes:
                            processed_params.append(param)
                            processed_results.append((positions, self.time_axis[param], self.data[param]))

        self.data_processed.emit(processed_params, processed_results)


class DataTableThread(QThread):
    _signal_message = pyqtSignal(str)
    _signal_led = pyqtSignal(int)
    _signal_table_data = pyqtSignal(DataFrame)
    _signal_label_data = pyqtSignal(str)
    _signal_finish = pyqtSignal()

    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        self.max_num = 1000
        self.time_sleep = 3

    def load_models(self):
        """加载模型"""
        self.get_selected_models()
        # 串口赋权
        self.parent.usetimefun()

        self.parent.parent.fualt_model.run()
        start_time = time.time()
        self.parent.parent.fualt_model.load_models()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"耗时: {elapsed_time} 秒")

    def set_max_num(self,max_num):
        self.max_num = max_num

    def set_sleep_time(self,time_sleep):
        self.time_sleep = time_sleep

    def reset_data(self):
        """数据重置"""
        self.date = ''
        self.parent.parent.fualt_model.run()
        # self.parent.parent.fualt_model.Models = []

    def get_selected_models(self):
        """选择模型"""
        self.old_model_names = self.parent.parent.fualt_model.model_names
        self.selected_model_names = [btn.text() for btn in self.parent.btns if btn.isChecked()]

        self.parent.parent.fualt_model.model_names = self.selected_model_names

    def get_data_aggregation(self,all_predict_count):
        """获取数据汇总"""
        # 找到每列的最大值索引
        max_indices = all_predict_count.idxmax(axis=0)

        # 创建一个新的 DataFrame 用于存储结果
        result = pd.DataFrame(0, index=all_predict_count.index, columns=all_predict_count.columns)

        # 将最大值所在位置设为 1
        for col in max_indices.index:
            result.loc[max_indices[col], col] = 1
        return result

    def most_common_element(self,label_indexs):
        # 使用Counter统计每个元素出现的次数
        count = Counter(label_indexs)
        # 找到出现次数最多的元素
        most_common = count.most_common(1)
        if most_common:
            return most_common[0][0]
        else:
            return None  # 如果label_indexs为空，则返回None
    def run(self):
        '''采集数据'''
        num = 0
        self.date = ''
        datas,pre_datas, label_indexs, model_dics = [], [], [], []
        label_indexs = []
        try:
            self.get_selected_models()

            # 加载模型
            if not self.parent.parent.fualt_model.Models or self.parent.parent.fualt_model.model_names != self.old_model_names:
                self.load_models()

            for data in get_new_datas(self.max_num, filter_repeating_data=True, time_sleep=self.time_sleep):
                if not self.parent.is_data_join:
                    return
                if len(data) < 8:
                    self._signal_message.emit("串口获取数据,请检查串口连接是否正常")
                    return

                label_index, all_predict_count, model_dic, pre_label = self.parent.parent.fualt_model.predict_models(
                    data)
                label_index = config.train_class.index(pre_label)
                self.date += (
                    f'\n获取到第{num+1}条数据\n'
                    f'Z轴振动速度{" " * 40}X轴振动速度 \n'
                    f'{" " * 8}{data[0]}{" " * 54}{data[1]}\n'
                    f'Z轴加速度峰值{" " * 36}X轴加速度峰值\n'
                    f'{" " * 8}{data[2]}{" " * 58}{data[3]}\n'
                    f'Z轴峰值速度分量频率Hz{" " * 20}X轴峰值速度分量频率Hz\n'
                    f'{" " * 8}{data[4]}{" " * 54}{data[5]}\n'
                    f'Z轴加速度均方根{" " * 30}X轴加速度均方根\n'
                    f'{" " * 8}{data[6]}{" " * 60}{data[7]}\n'
                    f'\n集成模型预测的结果统计：\n'
                    f'{model_dic}\n'
                    f'{self.parent.parent.fualt_model.integrated_model_dic}\n'
                    f'{pre_label}\n'
                )
                # pre_data = self.parent.parent.fualt_model.get_pre_data(
                #     pd.DataFrame([data], columns=self.parent.parent.fualt_model.use_features))
                datas.append([data, pre_label])
                label_indexs.append(label_index)
                num += 1

                self._signal_label_data.emit(self.date)

                # 手动诊断只发最后汇总的数据
                if self.parent.is_toggled == '手动':
                    if num >= self.max_num :
                        all_predict_count = all_predict_count.T
                        all_predict_count = self.get_data_aggregation(all_predict_count)
                        self._signal_table_data.emit(all_predict_count)
                        index = self.most_common_element(label_indexs)
                        self._signal_led.emit(int(index))  # 信号灯显示
                else:
                    self._signal_table_data.emit(all_predict_count.T)
                    self._signal_led.emit(int(label_index)) # 信号灯显示
                if num >= self.max_num:
                    break
            self.parent.is_data_join = False
            self._signal_finish.emit()
        except Exception as e:
            self._signal_message.emit(str(e))
            return False
