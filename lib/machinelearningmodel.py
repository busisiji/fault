import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score
import matplotlib.pyplot as plt

from utils.data_load import get_datas_from_csv


class MachineLearningModel():
    def __init__(self,model=None,datas=None,lables=None,sc = None,feature=None,model_name=None):
        self.model = model
        self.datas = datas
        self.lables = lables
        self.sc =sc
        self.feature = feature
        self.model_name = model_name
    def get_data(self):
        # if(self.datas == None):
        self.datas, self.lables, self.sc = get_datas_from_csv(features=self.feature)
        class_num = len(self.lables)
        target = np.repeat(range(class_num), self.datas[0].shape[0])
        res = pd.concat(self.datas)
        return res, target
    def get_data_and_split(self):
        self.x, self.y = self.get_data()
        return train_test_split(self.x, self.y, test_size=0.25, random_state=7)

    def train(self,name):
        import joblib
        train_x, test_x, train_y, test_y = self.get_data_and_split()
        # print(len(train_x),len(test_x),len(train_y),len(test_y))
        rf = self.model.fit(train_x, train_y)
        joblib.dump(rf, 'model/' + name + '.model')
        y_pred = self.model.predict(test_x)
        # print(len(y_pred),len(test_y))
        self.precision = precision_score(test_y, y_pred, average='micro')
        # print(test_y,y_pred)
        print(self.model_name," 预测的精度是：",self.precision)
        # print(self.model_name," 模型评价结果是：")
        # print(classification_report(test_y, y_pred))

    def load(self,name):
        import joblib
        train_x, test_x, train_y, test_y = self.get_data_and_split()
        self.model = joblib.load('model/' + name + '.model')
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

    def get_leble_name(self,leble_index):
        return self.lables[leble_index].replace(".csv", "")
    def plot_decision_boundary(self):
        # clf.fit(X, y)
        x_min, x_max = self.x.values[:, 0].min() - .5, self.x.values[:, 0].max() + .5
        y_min, y_max = self.x.values[:, 1].min() - .5,self.x.values[:, 1].max() + .5
        h = 0.01

        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
        z = self.model.predict(np.c_[xx.ravel(), yy.ravel()])
        z = z.reshape(xx.shape)

        plt.contourf(xx, yy, z, cmap=plt.cm.Spectral)
        cnt=int(len(self.x)/len(self.lables))

        for i in range(len(self.lables)):
            start = i*cnt
            end  = (i+1)*cnt
            plt.scatter(self.x.values[start:end, 0], self.x.values[start:end, 1], cmap=plt.cm.Spectral)
        plt.show()