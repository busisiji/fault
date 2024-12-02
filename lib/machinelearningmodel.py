# coding: utf-8
import os

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier

import config
from utils.data_load import get_datas_from_csv


class MachineLearningModel():
    def __init__(self,model=None,datas=None,labels=None,sc = None,feature=None,model_name=None):
        self.model = model
        self.datas = datas
        self.labels = labels
        self.sc =sc
        self.feature = feature
        self.model_name = model_name

    def get_data(self):
                # 确保 datas 和 labels 都不为空
        if not self.datas or not self.labels:
            raise ValueError("datas 和 labels 不能为空")

        # 获取所有 DataFrame 的行数
        row_counts = [df.shape[0] for df in self.datas]

        # 找到最小行数
        min_rows = min(row_counts)

        # 裁剪 DataFrame 以使其行数一致
        for i, df in enumerate(self.datas):
            self.datas[i] = df.head(min_rows)

        # if(self.datas == None):
        # self.datas, self.labels, self.sc = get_datas_from_csv(features=self.feature)
        class_num = len(self.labels)
        target = np.repeat(range(class_num), self.datas[0].shape[0])
        res = pd.concat(self.datas)
        return res, target
    def get_data_and_split(self):
        self.x, self.y = self.get_data()

        return train_test_split(self.x, self.y, test_size=0.25, random_state=7)

    def train(self,name=None,path=None):
        import joblib
        try:
            train_x, test_x, train_y, test_y = self.get_data_and_split()
        except Exception as e:
            print(e)
            raise Exception("部分标签数据缺失，请确认所有标签数据都存在")
        try:
            rf = self.model.fit(train_x, train_y)

            joblib.dump(rf, path+'/' + name + '.model')


            y_pred = self.model.predict(test_x)
            # print(len(y_pred),len(test_y))
            self.precision = precision_score(test_y, y_pred, average='micro')
            return self.precision
        except Exception as e:
            raise e

    def load(self,name,path='model'):
        import joblib
        train_x, test_x, train_y, test_y = self.get_data_and_split()
        self.model = joblib.load(os.path.join(path, name + '.model'))
        y_pred = self.model.predict(test_x)
        # print(len(y_pred),len(test_y))
        self.precision = precision_score(test_y, y_pred, average='micro')
        # print(test_y,y_pred)
        print(self.model_name, " 预测的精度是：", self.precision)

    def predict(self, x):
        if(self.feature != None):
            x = x[self.feature]
        pre_y = self.model.predict([x.iloc[0]])
        return pre_y[0]

    def get_leble_name(self,lebel_index):
        return self.labels[lebel_index].replace(".csv", "")
    def plot_decision_boundary(self):
        # clf.fit(X, y)
        x_min, x_max = self.x.values[:, 0].min() - .5, self.x.values[:, 0].max() + .5
        y_min, y_max = self.x.values[:, 1].min() - .5,self.x.values[:, 1].max() + .5
        h = 0.01

        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
        z = self.model.predict(np.c_[xx.ravel(), yy.ravel()])
        z = z.reshape(xx.shape)

        plt.contourf(xx, yy, z, cmap=plt.cm.Spectral)
        cnt=int(len(self.x)/len(self.labels))

        for i in range(len(self.labels)):
            start = i*cnt
            end  = (i+1)*cnt
            plt.scatter(self.x.values[start:end, 0], self.x.values[start:end, 1], cmap=plt.cm.Spectral)
        plt.show()