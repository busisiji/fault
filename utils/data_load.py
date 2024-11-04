import os
import pandas as pd
from sklearn.preprocessing import StandardScaler

import config
feature = ["Z 轴振动速度","X 轴振动速度","Z 轴加速度峰值","X 轴加速度峰值","Z 轴峰值速度分量频率 Hz","X 轴峰值速度分量频率 Hz","Z 轴加速度均方根","X 轴加速度均方根"]
def get_datas_from_csv(features=None, path=config.train_path):
    # from sklearn.preprocessing import StandardScaler
    res =[]
    file_names = []
    for train_csv_path in config.train_csv_path:
        file_names.append(os.path.basename(train_csv_path))

        df = pd.read_csv(train_csv_path)
        if(features!=None):
            df = df[features]
        res.append(df)

    sc = StandardScaler()
    sc.fit(pd.concat(res))
    for i in range(len(res)):
        # 归一化
        res[i] = pd.DataFrame(sc.transform(res[i]),columns=features)

    return res,[l.replace(".csv", "") for l in file_names],sc

def get_lable_datas_from_csv(need_lable):
    # from sklearn.preprocessing import StandardScaler
    res =[]
    paths = [config.train_path, config.test_path]
    lables = []
    for path in paths:
        data_type = "训练集"
        if(path.endswith("test")):
            data_type="测试集"
        for train_csv_path in config.train_csv_path:
            file_name = os.path.basename(train_csv_path)
            lable = file_name.replace(".csv", "")
            if(need_lable!= lable):
                continue
            lables.append(f"{data_type}:{lable}")
            df = pd.read_csv(train_csv_path)
            res.append(df)
    sc = StandardScaler()
    sc.fit(pd.concat(res))
    for i in range(len(res)):
        res[i] = pd.DataFrame(sc.transform(res[i]),columns=feature)
    return res,lables,sc


def data_balance():
    '''设置数据相同行数'''
    # train四文件保存相同行数
    total_p = 100000
    filenames = config.train_csv_path
    # 确定最小行数
    try:
        for filename in filenames:
            with open(filename, 'r', encoding='utf-8') as file:
                total = sum(1 for line in file)
                if total < total_p:
                    total_p = total
    except Exception as e:
        print(f'处理文件 {filename} 时发生错误: {e}')
        raise e

    if total_p == 0:
        print('训练数据不能为空')
        raise Exception("训练数据不能为空")
    # 调整文件行数
    try:
        for filename in filenames:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            if len(lines) > total_p:
                new_lines = lines[:total_p]
                with open(filename, 'w', encoding='utf-8') as file:
                    file.writelines(new_lines)
    except Exception as e:
        print(f'处理文件 {filename} 时发生错误: {e}')
        raise e


def check_and_create_csv_files(file_names = ["偏轴.csv", "正常.csv"]):
    """创建训练集"""
    base_path = config.train_path
    os.makedirs(base_path, exist_ok=True)

    headers = ["Z 轴振动速度", "X 轴振动速度", "Z 轴加速度峰值", "X 轴加速度峰值",
               "Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz",
               "Z 轴加速度均方根", "X 轴加速度均方根"]

    for file_name in file_names:
        file_path = os.path.join(base_path, file_name)
        if not os.path.exists(file_path):
            df = pd.DataFrame(columns=headers)
            df.to_csv(file_path, index=False)

