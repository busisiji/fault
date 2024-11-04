import os
import sys
import threading

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDesktopWidget


def get_root_dir():
    """获取项目根目录"""
    if getattr(sys, 'frozen', False):
        # 打包后的程序
        root_dir = sys._MEIPASS
    else:
        # 正常的脚本运行
        root_dir = os.path.dirname(os.path.abspath(__file__))
    return root_dir


# 静态变量
main_weight = 1200
main_height = 800

font = QFont()
font.setPointSize(46)
font.setBold(True)
font.setItalic(True)

ROOT_DIR = get_root_dir() # 项目根目录
train_path = os.path.join(ROOT_DIR, 'data', 'train')
test_path = os.path.join(ROOT_DIR, 'data', 'test')
title_class = ['故障诊断','边缘计算']
model_path = os.path.join(ROOT_DIR, 'model')
train_class = ['正常','偏轴', '静止']
train_csv = [ name + '.csv' for name in train_class]
train_csv_path = [os.path.join(train_path, name) for name in train_csv]
ico = os.path.join(ROOT_DIR, 'icons', '1.ico')
ttf_SsimHei = os.path.join(ROOT_DIR, 'fonts', 'SimHei.ttf')
ttf_my = os.path.join(ROOT_DIR, 'fonts', 'my.ttf')
feature_default = ["Z 轴振动速度", "X 轴振动速度", "Z 轴加速度峰值", "X 轴加速度峰值", "Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz",
                           "Z 轴加速度均方根",
                           "X 轴加速度均方根"]
features = [["Z 轴加速度均方根", "X 轴加速度均方根"],
                         ["Z 轴加速度峰值", "X 轴加速度峰值"],
                         ["Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz"],
                         ["Z 轴加速度均方根", "Z 轴加速度峰值", "X 轴加速度峰值"],
                         ["X 轴振动速度", "Z 轴振动速度", "X 轴加速度峰值", "Z 轴加速度峰值"],
                         ["Z 轴振动速度", "X 轴振动速度"]]
sensor_class = {'温度传感器':['温度'],
                '湿度传感器':['湿度'],
                '震动传感器':feature_default} # 传感器类型
toname = { '用户账号': 'Login','数据采集':'DataAcquisition','ModbusRtu通讯':"DataModbusRtu",'ModbusTcp通讯':"DataModbusTcp"}  # 图名-表名

lock = threading.Lock()

def get_title_index(title):
    if title not in title_class:
        return 0
    return title_class.index(title)
def get_feature_default(index=2):
    if not isinstance(index, int):
        index = get_title_index(index) + 1
    if index == 1:
        return ["Z 轴振动速度", "X 轴振动速度", "Z 轴加速度峰值",
                "X 轴加速度峰值", "Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz",
                "Z 轴加速度均方根", "X 轴加速度均方根"]
    elif index == 2:
        return ["温度", "湿度"]

def initialize_sensors():
    sensors = [
        {"param_name": "Z 轴振动速度", "sensor_name": "震动传感器", "address": 0},
        {"param_name": "X 轴振动速度", "sensor_name": "震动传感器", "address": 1},
        {"param_name": "Z 轴加速度峰值", "sensor_name": "震动传感器", "address": 2},
        {"param_name": "X 轴加速度峰值", "sensor_name": "震动传感器", "address": 3},
        {"param_name": "Z 轴峰值速度分量频率 Hz", "sensor_name": "震动传感器", "address": 4},
        {"param_name": "X 轴峰值速度分量频率 Hz", "sensor_name": "震动传感器", "address": 5},
        {"param_name": "Z 轴加速度均方根", "sensor_name": "震动传感器", "address": 6},
        {"param_name": "X 轴加速度均方根", "sensor_name": "震动传感器", "address": 7},
        {"param_name": "温度", "sensor_name": "温度传感器", "address": 8},
        {"param_name": "湿度", "sensor_name": "湿度传感器", "address": 9}
    ]
    return sensors


# 动态变量
screen = None
def get_screen():
    return screen
def set_screen(value):
    global screen
    screen = value




