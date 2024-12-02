import json
import os
import re
import sys
import threading
import logging

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDesktopWidget

from db.db_mysql import DB_MySQL

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

time_format = "%Y-%m-%d %H:%M:%S"

font = QFont()
font.setPointSize(46)
font.setBold(True)
font.setItalic(True)

ROOT_DIR = get_root_dir()  # 项目根目录
train_path = os.path.join(ROOT_DIR, 'data', 'train')
test_path = os.path.join(ROOT_DIR, 'data', 'test')
title_class = ['故障诊断', '边缘计算']
model_path = os.path.join(ROOT_DIR, 'model')
train_class = ['正常', '偏轴', '静止']
train_csv = [name + '.csv' for name in train_class]
train_csv_path = [os.path.join(train_path, name) for name in train_csv]
ico = os.path.join(ROOT_DIR, 'icons', '1.ico')
ttf_SsimHei = os.path.join(ROOT_DIR, 'fonts', 'SimHei.ttf')
ttf_my = os.path.join(ROOT_DIR, 'fonts', 'my.ttf')
features = [["Z 轴加速度均方根", "X 轴加速度均方根"],
            ["Z 轴加速度峰值", "X 轴加速度峰值"],
            ["Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz"],
            ["Z 轴加速度均方根", "Z 轴加速度峰值", "X 轴加速度峰值"],
            ["X 轴振动速度", "Z 轴振动速度", "X 轴加速度峰值", "Z 轴加速度峰值"],
            ["Z 轴振动速度", "X 轴振动速度"]]
feature_default = ["Z 轴振动速度", "X 轴振动速度", "Z 轴加速度峰值", "X 轴加速度峰值", "Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz",
                   "Z 轴加速度均方根",
                   "X 轴加速度均方根"]

sensor_class = {'温度传感器': ['温度'],
                '湿度传感器': ['湿度'],
                '震动传感器': feature_default}  # 传感器类型
toname = {'用户账号': 'Login', '数据采集': 'DataAcquisition', 'ModbusRtu通讯': 'DataModbusRtu', 'ModbusTcp通讯': 'DataModbusTcp',
          '传感器配置': 'SensorConfig', '数值传感器': 'SensorConfigNum', '开关传感器': 'SensorConfigSwitch', "历史报警": "warning_message",
          '预测数据': 'PredictData'}  # 图名-表名
sensors = [
    {"sensor_name": "震动传感器", "status_list": ["正常", "故障", "静止"], "params": {"Z 轴振动速度": 0, "X 轴振动速度": 1, "Z 轴加速度峰值": 2, "X 轴加速度峰值": 3, "Z 轴峰值速度分量频率 Hz": 4, "X 轴峰值速度分量频率 Hz": 5, "Z 轴加速度均方根": 6, "X 轴加速度均方根": 7}, "data_type": ["uint16"] * 8},
    {"sensor_name": "温度传感器", "status_list": ["正常", "警告", "故障"], "params": {"温度": 8}, "data_type": ["uint16"]},
    {"sensor_name": "湿度传感器", "status_list": ["正常", "故障", "警告"], "params": {"湿度": 9}, "data_type": ["uint16"]},
    {"sensor_name": "门传感器", "on_value": 1, "off_value": 0, "data_type": ["bool"]}
]

lock = threading.Lock()

def get_title_index(title):
    """获取标题索引"""
    if title not in title_class:
        return 0
    return title_class.index(title)

def convert_to_db_columns(feature_defaults):
    """数据库列名列表"""
    try:
        new_feature_defaults = []
        for fd in feature_defaults:
            # 替换空格和中文字符
            clean_fd = re.sub(r'[\s]+', '', fd)
            # 确保列名以字母或下划线或中文开头
            if not re.match(r'^[a-zA-Z\u4e00-\u9fff_]', clean_fd):
                clean_fd = '_' + clean_fd
            new_feature_defaults.append(clean_fd)
        return new_feature_defaults  # 将集合转换为列表
    except Exception as e:
        logging.error(f"发生错误: {e}")
        return []

def get_feature_default(index=2):
    """使有参数列表"""
    if not isinstance(index, int):
        index = get_title_index(index) + 1
    # 震动传感器
    if index == 1:
        return ["Z 轴振动速度", "X 轴振动速度", "Z 轴加速度峰值",
                "X 轴加速度峰值", "Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz",
                "Z 轴加速度均方根", "X 轴加速度均方根"]
    # 多传感器
    elif index == 2:
        try:
            feature_defaults = []
            db = DB_MySQL()
            table_name = toname['数值传感器']
            with db:
                data = db.select_data(table_name, columns='*')
            for row in data:
                params = json.loads(row['params'])
                feature_default = list(params.keys())
                feature_defaults.extend(feature_default)
            return convert_to_db_columns(feature_defaults)
        except Exception as e:
            logging.error(f"发生错误: {e}")
            return []

def initialize_sensors():
    """传感器配置 参数分开"""
    try:
        db = DB_MySQL()
        table_name = toname['数值传感器']
        with db:
            data = db.select_data(table_name, columns='*')
        if data:
            sensors = []
            for item in data:
                sensor_name = item['sensor_name']
                status_list = json.loads(item['status_list'])
                params = json.loads(item['params'])
                data_types = item['data_type']  # 新增数据类型字段
                for param_name, address in params.items():
                    sensors.append({
                        "param_name": param_name,
                        "sensor_name": sensor_name,
                        "status_list": status_list,
                        "address": address,
                        "data_type": data_types  # 默认数据类型为 uint16
                    })
        else:
            sensors = [
                {"param_name": "", "sensor_name": "", "address": None, "data_type": "uint16"}
            ]
        return sensors
    except Exception as e:
        logging.error(f"发生错误: {e}")
        return [{"param_name": "", "sensor_name": "", "address": None, "data_type": "uint16"}]

def get_sensors(name='数值传感器'):
    """传感器配置 参数列表"""
    db = DB_MySQL()
    sensors = []
    if name == '数值传感器':
        table_name = toname['数值传感器']
        try:
            with db:
                data = db.select_data(table_name, columns='*')
            if data:
                for item in data:
                    status_list = json.loads(item['status_list'])
                    params = json.loads(item['params'])
                    data_types = item['data_type']  # 新增数据类型字段
                    sensor_config = {
                        "param_name": convert_to_db_columns(list(params.keys())),
                        "sensor_name": item['sensor_name'],
                        "address": list(params.values()),
                        "status_list": status_list,
                        "data_type": data_types ,  # 默认数据类型为 uint16
                    }
                    sensors.append(sensor_config)
                return sensors
            else:
                return [
                    {"param_name": [], "sensor_name": "", "address": [], "status_list": [], "data_type": []},
                ]
        except Exception as e:
            logging.error(f"发生错误: {e}")
            return [{"param_name": [], "sensor_name": "", "address": [], "status_list": [], "data_type": []}]

    elif name == '开关传感器':
        table_name = toname['开关传感器']
        with db:
            data = db.select_data(table_name, columns='*')
            if data:
                for sensor in data:
                    if sensor['on_value'] == 1:
                        on_value = True
                    elif sensor['on_value'] == 0:
                        on_value = False
                    else:
                        on_value = sensor['on_value']
                    if sensor['off_value'] == 1:
                        off_value = True
                    elif sensor['off_value'] == 0:
                        off_value = False
                    else:
                        off_value = sensor['off_value']
                    sensors.append({
                        'sensor_name': sensor['sensor_name'],
                        'on_value': on_value,
                        'off_value': off_value,
                        'address': sensor['address'],  # 获取地址，默认为空字符串
                        'data_type': 'bool',
                    })
                return sensors
            else:
                return [{"sensor_name": "", "address": "", "on_value": True, "off_value": False,'data_type': 'bool'}]

# 动态变量
screen = None

def get_screen():
    return screen

def set_screen(value):
    global screen
    screen = value
