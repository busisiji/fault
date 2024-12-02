import os
import time

import config

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from utils import frozen_dir


from utils.data_load import get_datas_from_csv,get_lable_datas_from_csv

font = font_manager.FontProperties(fname=config.ttf_my)
font_manager.fontManager.addfont(config.ttf_my)
prop = font_manager.FontProperties(fname=config.ttf_my)
plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['mathtext.fontset'] = 'cm'  # 'cm' (Computer Modern)
colors = ['b','g','r','c','m','y','k']

def init():
    # import matplotlib.pyplot as plt
    # plt.rcParams['font.family'] = prop.get_name()
    # plt.rcParams['mathtext.fontset'] = 'cm'  # 'cm' (Computer Modern)
    # plt.rcParams['font.family'] = 'FangSong'  # 设置字体为仿宋
    plt.rcParams['font.size'] = 10  # 设置字体的大小为10
    plt.rcParams['axes.unicode_minus'] = False  # 显示正、负的问题
    plt.rcParams['figure.figsize'] = (12.8, 7.2)
def show_data_by_dir(dir=frozen_dir.app_path() + r"/data/train", lable = None):
    # init()
    # import matplotlib.pyplot as plt
    # plt.rcParams['font.family'] = prop.get_name()
    # plt.rcParams['mathtext.fontset'] = 'cm'  # 'cm' (Computer Modern)
    if(lable == None):
        datas, lables, sc = get_datas_from_csv(path=dir)
    else:
        datas, lables, sc = get_lable_datas_from_csv(lable)
    fig, subs = plt.subplots(2, 2)
    show_data(datas, lables, fig, subs,0)
def show_data(datas,lables,fig,subs,time=10):
    # import matplotlib.pyplot as plt
    # plt.rcParams['font.family'] = prop.get_name()
    # plt.rcParams['mathtext.fontset'] = 'cm'  # 'cm' (Computer Modern)
    plt.ion()  # 开启交互模式
    i = 0
    for j in range(2):
        for k in range(2):
            color_index = 0
            print(datas)
            for df in datas:
                subs[j][k].scatter(df.iloc[:, i].values, df.iloc[:, i + 1].values,c=colors[color_index],alpha=0.3)
                color_index += 1
            subs[j][k].set_xlabel(df.columns[i],fontproperties=font)
            subs[j][k].set_ylabel(df.columns[i+1],fontproperties=font)
            subs[j][k].legend(labels=lables,prop=font)
            i += 2
    # fig.canvas.set_window_title('震传感器数据可视化')
    fig.tight_layout()
    plt.pause(time)
    # plt.show()
    # plt.close()

def show_data_new(datas,lables,fig,subs,time=10):
    # import matplotlib.pyplot as plt
    # plt.rcParams['font.family'] = prop.get_name()
    # plt.rcParams['mathtext.fontset'] = 'cm'  # 'cm' (Computer Modern)
    plt.ion()  # 开启交互模式
    i = 0
    for j in range(2):
        for k in range(2):
            color_index = 0
            print(datas)
            for df in datas:
                subs[j][k].scatter(None, None,c=colors[color_index],alpha=0.3)
                color_index += 1
            subs[j][k].set_xlabel(df.columns[i],fontproperties=font)
            subs[j][k].set_ylabel(df.columns[i+1],fontproperties=font)
            subs[j][k].legend(labels=lables,prop=font)
            i += 2
    fig.canvas.set_window_title('新增数据可视化')
    fig.tight_layout()
    plt.pause(time)
    # plt.ioff()
    # plt.show()

def add_new_data(subs,newdata=None,lable_index=0):
    # plt.ion()  # 开启交互模式
    # import matplotlib.pyplot as plt
    # plt.rcParams['font.family'] = prop.get_name()
    # plt.rcParams['mathtext.fontset'] = 'cm'  # 'cm' (Computer Modern)
    i = 0
    markers = ["*",]
    for j in range(2):
        for k in range(2):
            subs[j][k].scatter(newdata[i: i + 1], newdata[i + 1: i + 2], c=colors[lable_index],s=150, marker="*")
            i += 2
    plt.pause(3)
    # plt.show()

def show_data3D(feature):
    '''
    3参数可视化
    '''
    # import matplotlib.pyplot as plt
    # plt.rcParams['font.family'] = prop.get_name()
    # plt.rcParams['mathtext.fontset'] = 'cm'  # 'cm' (Computer Modern)
    path = '../data/train'
    folders = os.listdir(path)

    ax = plt.subplot(projection='3d')  # 创建一个三维的绘图工程
    for dir in folders:
        df = pd.read_csv(os.path.join(path, dir))
        print(df[feature[2]].values)
        ax.scatter(df[feature[0]].values,df[feature[1]].values,df[feature[2]].values)
    ax.set_xlabel(feature[0])
    ax.set_ylabel(feature[1])
    ax.set_zlabel(feature[2])
    plt.legend(labels=folders)
    # plt.show()