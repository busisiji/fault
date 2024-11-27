import json
import logging
import os
import sys

import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QMainWindow, QPushButton, QSpinBox, QVBoxLayout, QWidget, QInputDialog, QMessageBox,
    QButtonGroup, QTabWidget, QFileDialog
)
from sklearn.preprocessing import StandardScaler

import config
from db.db_mysql import DB_MySQL
from lib.faultDiagnosis_model import faultDiagnosisModel
from ui.others.ui_fun import BaseWindow
from ui.qss import btn_css
from utils.data_load import data_balance
from utils.frozen_dir import app_path, exists_path
from utils.my_thread import MyThread, NewMyThread

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrainWindow(BaseWindow):
    '''集成学习窗口'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.db = DB_MySQL()
            # 设置默认保存路径
        self.default_save_path = os.path.join(config.get_root_dir(), 'model')


        self.initUI()

    def initUI(self):
        self.setWindowTitle('模型训练')
        self.setWindowState(Qt.WindowMaximized)

        self.setbox_6()  # 算法选择
        self.setbox_7()  # 标签管理
        # self.setbox_8()  # 参数设置
        self.setbox_9()  # 传感器参数选择
        self.setbox_10()  # 开始训练

        central_widget = QWidget()
        # self.setCentralWidget(central_widget)

        self.mainVLayout = QVBoxLayout(central_widget)
        self.mainVLayout.addWidget(self.groupbox_6)
        self.mainVLayout.addWidget(self.groupbox_7)
        # self.mainVLayout.addWidget(self.groupbox_8)
        self.mainVLayout.addWidget(self.groupbox_9)
        self.mainVLayout.addWidget(self.groupbox_10)

        self.setLayout(self.mainVLayout)

    def setbox_6(self):
        # 容器6
        self.groupbox_6 = QGroupBox('算法选择')
        self.groupbox_6.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_6.setFont(font)

        # 将控件填入布局中
        self.VLayout_6 = QHBoxLayout()
        self.VLayout_6.setContentsMargins(0, 0, 0, 0)
        self.VLayout_6.setSpacing(0)

        # 按钮组
        self.btn_group = QButtonGroup()
        btn_size = 30

        # 模型名称列表
        self.model_names = ["逻辑回归", "支持向量机", "感知机", "K近邻算法", "随机森林", "决策树"]

        # 初始化复选框
        self.btns = []
        for name in self.model_names:
            btn = QCheckBox(name)
            btn.setChecked(True)  # 默认选中
            btn.setMinimumSize(100, btn_size)
            btn.setFont(font)
            btn_css(btn)
            # self.btn_group.addButton(btn) # 单选
            self.btns.append(btn)
            self.VLayout_6.addWidget(btn)

        self.groupbox_6.setLayout(self.VLayout_6)

    def setbox_7(self):
        # 容器7
        self.groupbox_7 = QGroupBox('标签管理')
        self.groupbox_7.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_7.setFont(font)

        # 将控件填入布局中
        self.HLayout_7 = QHBoxLayout()
        self.VLayout_7_left = QVBoxLayout()
        self.VLayout_7_right = QVBoxLayout()

        # 初始化标签列表
        self.label_combobox = QComboBox()
        self.label_combobox.setFont(font)
        # self.label_combobox.addItems(config.get_sensors()[0]['status_list'])
        self.label_combobox.addItems(['加速','减速','静止','匀速'])

        # 操作下拉列表
        self.operation_combobox = QComboBox()
        self.operation_combobox.setFont(font)
        self.operation_combobox.addItems(['操作', '添加标签', '删除标签', '修改标签'])
        self.operation_combobox.currentIndexChanged.connect(self.perform_operation)

        self.VLayout_7_left.addWidget(self.label_combobox)
        self.VLayout_7_right.addWidget(self.operation_combobox)

        self.HLayout_7.addLayout(self.VLayout_7_left)
        self.HLayout_7.addLayout(self.VLayout_7_right)

        self.groupbox_7.setLayout(self.HLayout_7)

    def setbox_8(self):
        # 容器8
        self.groupbox_8 = QGroupBox('参数设置')
        self.groupbox_8.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_8.setFont(font)

        # 将控件填入布局中
        self.VLayout_8 = QVBoxLayout()
        self.VLayout_8.setContentsMargins(0, 0, 0, 0)
        self.VLayout_8.setSpacing(0)

        # 训练轮数
        self.train_rounds_label = QLabel('训练轮数')
        self.train_rounds_label.setFont(font)
        self.train_rounds_spinbox = QSpinBox()
        self.train_rounds_spinbox.setFont(font)
        self.train_rounds_spinbox.setMinimum(1)
        self.train_rounds_spinbox.setMaximum(1000)
        self.train_rounds_spinbox.setValue(30)

        self.VLayout_8.addWidget(self.train_rounds_label)
        self.VLayout_8.addWidget(self.train_rounds_spinbox)

        self.groupbox_8.setLayout(self.VLayout_8)

    def setbox_9(self):
        # 容器9
        self.groupbox_9 = QGroupBox('传感器参数选择')
        self.groupbox_9.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_9.setFont(font)

        # 将控件填入布局中
        self.VLayout_9 = QVBoxLayout()
        self.VLayout_9.setContentsMargins(0, 0, 0, 0)
        self.VLayout_9.setSpacing(0)

        # 初始化标签页
        self.tab_widget = QTabWidget()
        self.param_checkboxes = {}
        for sensor in self.sensors:
            tab = QWidget()
            VLayout = QVBoxLayout(tab)
            grid_layout = QGridLayout()
            grid_layout.setSpacing(10)

            self.param_checkboxes[sensor['sensor_name']] = []
            for i, param in enumerate(sensor['param_name']):
                checkbox = QCheckBox(param)
                # checkbox.setChecked(True)  # 默认选中
                checkbox.setChecked(False)  # 默认关闭
                checkbox.setFont(font)
                self.param_checkboxes[sensor['sensor_name']].append(checkbox)
                grid_layout.addWidget(checkbox, i // 4, i % 4)

            VLayout.addLayout(grid_layout)
            self.tab_widget.addTab(tab, sensor['sensor_name'])

        self.VLayout_9.addWidget(self.tab_widget)

        self.groupbox_9.setLayout(self.VLayout_9)

    def setbox_10(self):
        # 容器10
        self.groupbox_10 = QGroupBox('开始训练')
        self.groupbox_10.setAlignment(Qt.AlignHCenter)  # 标题居中
        font = QFont()
        font.setPointSize(23)
        self.groupbox_10.setFont(font)

        # 将控件填入布局中
        self.VLayout_10 = QVBoxLayout()

        # 保存路径输入框
        self.save_path_label = QLabel('模型目录')
        self.save_path_label.setFont(config.font)
        self.save_path_lineedit = QLineEdit()
        self.save_path_lineedit.setFont(config.font)
        self.save_path_lineedit.setText(self.default_save_path)
        self.save_path_lineedit.setReadOnly(True)
        # self.select_path_button = QPushButton('选择路径')
        # btn_css(self.select_path_button)
        # self.select_path_button.setFont(font)
        # self.select_path_button.clicked.connect(self.select_save_path)

        # 开始训练按钮
        self.start_training_button = QPushButton('开始训练')
        btn_css(self.start_training_button)
        self.start_training_button.setFont(font)
        self.start_training_button.clicked.connect(self.start_training)

        # 添加控件到布局
        self.VLayout_10.addWidget(self.save_path_label)
        self.VLayout_10.addWidget(self.save_path_lineedit)
#         self.VLayout_10.addWidget(self.select_path_button)
        self.VLayout_10.addWidget(self.start_training_button)

        self.groupbox_10.setLayout(self.VLayout_10)

    def select_save_path(self):
        # 弹出文件对话框选择保存路径
        directory = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if directory:
            self.save_path_lineedit.setText(directory)

    def perform_operation(self, index):
        operation = self.operation_combobox.currentText()
        if operation == '添加标签':
            self.add_label()
        elif operation == '删除标签':
            self.del_label()
        elif operation == '修改标签':
            self.edit_label()

        # 操作完成后将 operation_combobox 设置为第一个选项
        self.operation_combobox.setCurrentIndex(0)

    def add_label(self):
        text, ok = QInputDialog.getText(self, '添加标签', '请输入标签名称:')
        if ok and text:
            self.label_combobox.addItem(text)

    def del_label(self):
        current_index = self.label_combobox.currentIndex()
        if current_index >= 0:
            self.label_combobox.removeItem(current_index)

    def edit_label(self):
        current_index = self.label_combobox.currentIndex()
        if current_index >= 0:
            current_text = self.label_combobox.currentText()
            text, ok = QInputDialog.getText(self, '修改标签', '请输入新的标签名称:', text=current_text)
            if ok and text:
                self.label_combobox.setItemText(current_index, text)

    def start_training(self):
        # if self.parent.IsRun:
        #     QMessageBox.warning(self, "警告", "有任务运行中!")
        #     return
        # else:
        #     self.parent.setRun('模型训练中')

        # 获取保存路径
        save_path = self.save_path_lineedit.text()
        if not save_path:
            self.parent.setRun()
            QMessageBox.warning(self, '警告', '请选择保存路径')
            return
        sensor_name = ''
        try:
            # 获取选中的算法
            selected_models = [btn.text() for btn in self.btns if btn.isChecked()]

            # 获取训练轮数
            # train_rounds = self.train_rounds_spinbox.value()

            # 获取标签列表
            labels = [self.label_combobox.itemText(i) for i in range(self.label_combobox.count())]

            # 获取所有传感器信息
            sensors = config.get_sensors()

            # 遍历每个传感器
            for sensor in sensors:
                if not sensor['sensor_name']:
                    continue
                sensor_name = sensor['sensor_name']
                if not sensor['param_name']:
                    continue  # 跳过没有参数的传感器

                # 获取选中的参数
                selected_params = []
                for checkbox in self.param_checkboxes[sensor['sensor_name']]:
                    if checkbox.isChecked():
                        selected_params.append(checkbox.text())

                if not selected_params:
                    # QMessageBox.warning(self, '警告', f'请选择{sensor_name}的参数')
                    continue

                with self.db:
                    sensor_data = self.db.select_data(config.toname['数据采集'],
                                                      condition=f"sensor_name = '{sensor['sensor_name']}'")

                self.parent.fualt_model.model_names = selected_models

                # 解析 params 字段
                for data in sensor_data:
                    data['params'] = json.loads(data['params'])

                self.parent.fualt_model.use_features = selected_params

                # 遍历每个标签
                res = []
                for label in labels:
                    # 筛选状态与标签相同的数据
                    labeled_data = [data for data in sensor_data if data['status'] == label]

                    # 构建特征和标签
                    X = []
                    for data in labeled_data:
                        row = {param: data['params'].get(param, None) for param in selected_params}
                        if all(row.values()):  # 确保没有空值
                            X.append(list(row.values()))

                    if not X:
                        continue  # 没有数据则跳过

                    # 将 X 转换为 DataFrame 并设置表头
                    df_X = pd.DataFrame(X, columns=selected_params)
                    res.append(df_X)

                # 进行训练
                if not res:
                    continue
                # 检查 res 中的每个 DataFrame 是否有行数
                for df in res:
                    if df.empty:
                        continue
                path = os.path.join(save_path, sensor['sensor_name'])
                exists_path(path)
                self.parent.fualt_model.run_res(res, labels)
                try:
                    self.thread = NewMyThread(lambda : self.parent.fualt_model.train_models(path))
                    self.thread._signal.connect(self.theard_finished)
                    self.thread.start()
                    # self.parent.fualt_model.train_models(path)
                except Exception as e:
                    QMessageBox.critical(self, '错误', f'{sensor_name}模型训练失败: {str(e)}')
                    continue

        except Exception as e:
            self.parent.setRun()
            QMessageBox.critical(self, '错误', f'模型训练失败: {str(e)}')


    def theard_finished(self,e):
        self.parent.setRun()
        if e == 'OK':
            QMessageBox.information(self, '成功', f'模型训练完成')
        else:
            QMessageBox.critical(self, '错误', f'模型训练失败: {str(e)}')
    def update_ui(self):
        # 获取最新的传感器信息
        old_sensors = self.sensors
        new_sensors = config.get_sensors()
        self.sensors = new_sensors

        # 提取旧的和新的传感器名称
        old_sensor_names = {sensor['sensor_name'] for sensor in old_sensors}
        new_sensor_names = {sensor['sensor_name'] for sensor in new_sensors}

        # 创建一个字典来存储当前的标签页
        current_tabs = {self.tab_widget.tabText(i): self.tab_widget.widget(i) for i in range(self.tab_widget.count())}

        # 处理新增的传感器
        for sensor in new_sensors:
            if sensor['sensor_name'] not in old_sensor_names:
                tab = QWidget()
                VLayout = QVBoxLayout(tab)
                grid_layout = QGridLayout()
                grid_layout.setSpacing(10)

                param_checkboxes = []
                for i, param in enumerate(sensor['param_name']):
                    checkbox = QCheckBox(param)
                    checkbox.setChecked(True)  # 默认选中
                    checkbox.setFont(QFont('Arial', 12))
                    param_checkboxes.append(checkbox)
                    grid_layout.addWidget(checkbox, i // 4, i % 4)

                VLayout.addLayout(grid_layout)
                self.tab_widget.addTab(tab, sensor['sensor_name'])

        # 处理删除的传感器
        for sensor_name in old_sensor_names - new_sensor_names:
            if sensor_name in current_tabs:
                index = self.tab_widget.indexOf(current_tabs[sensor_name])
                self.tab_widget.removeTab(index)

        # 更新现有传感器的参数复选框
        for sensor in new_sensors:
            if sensor['sensor_name'] in current_tabs:
                tab = current_tabs[sensor['sensor_name']]
                VLayout = tab.layout()
                grid_layout = VLayout.itemAt(0).layout()

                # 清除现有的复选框
                for i in reversed(range(grid_layout.count())):
                    widget = grid_layout.itemAt(i).widget()
                    if widget:
                        widget.deleteLater()

                # 添加新的复选框
                param_checkboxes = []
                for i, param in enumerate(sensor['param_name']):
                    checkbox = QCheckBox(param)
                    checkbox.setChecked(True)  # 默认选中
                    checkbox.setFont(QFont('Arial', 12))
                    param_checkboxes.append(checkbox)
                    grid_layout.addWidget(checkbox, i // 4, i % 4)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TrainWindow()
    window.show()
    sys.exit(app.exec_())
