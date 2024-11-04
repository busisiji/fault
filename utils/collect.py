import numpy as np
import pandas as pd
from utils.modbus import *
import datetime
from lib.visualization import init
import warnings
from utils.gettty import main
warnings.filterwarnings("ignore")
feature = ["Z 轴振动速度","X 轴振动速度","Z 轴加速度峰值","X 轴加速度峰值","Z 轴峰值速度分量频率 Hz","X 轴峰值速度分量频率 Hz","Z 轴加速度均方根","X 轴加速度均方根"]
def is_repeating_data(new_data,datas):
    is_repeating = False
    for d in datas:
        if ((d == new_data).all()):
            is_repeating = True
            break
    return is_repeating
def get_new_data():
    '''
    获取数据

    :param n: 获取多少条数据
    :param filter_repeating_data: 是否过滤重复数据
    :param time_sleep: 等待时间（秒）
    '''

    regnums = 12
    send_data = mmodbus03or04(address=2, startregadd=5200, regnum=regnums)
    cnt = 0
    data = []

    try:
        com = serial.Serial(main(), 9600, timeout=0.8)
        com.write(send_data)
        print(send_data)
        recv_data = com.read(regnums * 2 + 5)
        if not recv_data:
            return []
        res = smodbus03or04(recv_data, 1)
        if (res is None or len(res) == 0 or all(_ >= 65535 for _ in res)):
            raise Exception("数据异常,请检查串口连接")

        res = np.array(res)
        res = res[[1, 5, 6, 7, 8, 9, 10, 11]]
        com.close()
        return res
    except Exception as e:
        print(f"发生异常：{e}")
        raise e


def get_new_datas(n, filter_repeating_data=False, time_sleep=3):
    '''
    获取数据

    :param n: 获取多少条数据
    :param filter_repeating_data: 是否过滤重复数据
    :param time_sleep: 等待时间（秒）
    '''

    regnums = 12
    send_data = mmodbus03or04(address=2, startregadd=5200, regnum=regnums)
    cnt = 0
    data = []

    try:
        com = serial.Serial(main(), 9600, timeout=0.8)

        while True:
            com.write(send_data)
            recv_data = com.read(regnums * 2 + 5)
            if not recv_data:
                yield []
            res = smodbus03or04(recv_data, 1)
            if (res is None or len(res) == 0 or all(_ >= 65535 for _ in res)):
                break

            res = np.array(res)
            res = res[[1, 5, 6, 7, 8, 9, 10, 11]]

            # 过滤重复数据
            if filter_repeating_data and is_repeating_data(res, data):
                time.sleep(time_sleep)
                continue

            data.append(res)
            print(f"获取到第{cnt}条数据：", res)
            yield res
            cnt += 1

            if cnt == n:
                break

            time.sleep(time_sleep)
        com.close()
    except Exception as e:
        print(f"发生异常：{e}")
        raise e
        return


def collect_data_to_csv(n,file_path,filter_repeating_data=False):
    datas = []
    start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for data in get_new_datas(n, filter_repeating_data):
        print(data)
        datas.append(data.tolist())
    df=pd.DataFrame(datas,columns=feature)
    df.to_csv(file_path, index=False)
    print("开始采集时间", start)
    print("结束采集时间", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def collect_data_to_csv_visible(n, file_path, filter_repeating_data=False):
    from lib.faultDiagnosis_model import faultDiagnosisModel
    init()
    fualt_model = faultDiagnosisModel()
    # fualt_model.show_data_from_csv()
    datas = []
    start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for data in get_new_datas(n, filter_repeating_data):
        datas.append(data.tolist())
        pre_data = fualt_model.get_pre_data(pd.DataFrame([data], columns=fualt_model.feature_default))
        fualt_model.show_add_data(pre_data)
    df = pd.DataFrame(datas, columns=feature)
    df.to_csv(file_path, index=False)
    print("开始采集时间", start)
    print("结束采集时间", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
if __name__ == '__main__':
    collect_data_to_csv_visible(200, "/data/train/正常.csv")
