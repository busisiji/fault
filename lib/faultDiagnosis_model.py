import os

import numpy as np
import pandas as pd

import config
from utils.data_load import get_lable_datas_from_csv,get_datas_from_csv
from lib.machinelearningmodel import MachineLearningModel

class faultDiagnosisModel():
    """集成模型"""
    def __init__(self):
        self.use_features = config.feature_default
        self.model_names = ["逻辑回归", "支持向量机", "感知机", "K近邻算法", "随机森林", "决策树"]
        self.Models = []
        self.integrated_model_dic = {}

    def run(self, is_by_lable=False,need_lable="正常"):
        if(is_by_lable):
            self.datas, self.lables, self.sc = get_lable_datas_from_csv(need_lable=need_lable)
        else:
            self.datas, self.lables, self.sc = get_datas_from_csv(features=self.use_features)

        # self.train_models()
        # 集成模型预测结果统计
        self.integrated_model_dic = {k: v for k, v in zip(self.lables, np.zeros(len(self.lables), dtype=np.int32))}
        self.all_predict_count = pd.DataFrame(index=self.model_names,columns=self.lables,data=np.zeros((len(self.model_names),len(self.lables)),dtype=np.int32))

    def train_model(self,model,name):

        m = MachineLearningModel(model, datas=self.datas, lables=self.lables, sc=self.sc, feature=self.use_features, model_name=name)
        m.train(name)
        return m
    def sorted_key(e):
        return e.precision

    def build_models(self):
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
        from sklearn.neural_network import MLPClassifier
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn import tree
        from sklearn.ensemble import RandomForestClassifier
        models = []
        if "逻辑回归" in self.model_names:
            m1 = LogisticRegression()
            models.append(m1)
        if "支持向量机" in self.model_names:
            m2 = SVC()
            models.append(m2)
        if "感知机" in self.model_names:
            m3 = MLPClassifier(solver='adam', alpha=1e-5, hidden_layer_sizes=(64,), random_state=1, max_iter=3000)
            models.append(m3)
        if "K近邻算法" in self.model_names:
            knn = KNeighborsClassifier(10)
            models.append(knn)
        if "随机森林" in self.model_names:
            rfc = RandomForestClassifier(random_state=0)
            models.append(rfc)
        if "决策树" in self.model_names:
            decision_tree = tree.DecisionTreeClassifier(criterion="entropy")
            models.append(decision_tree)
        return models,self.model_names
    def train_models(self):
        try:
            models,model_names=self.build_models()
            self.Models = []
            for i in range(len(models)):
                model = self.train_model(model=models[i],name=model_names[i])
                self.Models.append(model)
        except Exception as e:
            print(e)
    def load_models(self):
        try:
            if self.sc:
                import joblib
                models, model_names = self.build_models()
                file_counts = 0
                for dirpath, dirnames, filenames in os.walk(config.model_path):
                    for filename in filenames:
                        if filename.endswith('.model'):
                            file_counts += 1
                if file_counts != len(models):
                    self.train_models()
                    print(self.Models)
                else:
                    self.Models = []
                    for i in range(len(models)):
                        m = MachineLearningModel(models[i], datas=self.datas, lables=self.lables, sc=self.sc,
                                                 feature=self.use_features, model_name=model_names[i])
                        m.load(model_names[i])
                        self.Models.append(m)
                        print(self.Models)
        except Exception as e:
            print(e)
    def get_pre_data(self,data):
        print(self.use_features)
        data = data[self.use_features]
        return self.sc.transform(data.values)[0]
    def predict_models(self,data):
        # 每个分类预测的结果统计
        self.labels_dic = {}
        # 每个模型预测结果统计
        self.model_dic = {}
        # # 集成模型预测结果统计
        # self.integrated_model_dic = {k: v for k, v in zip(self.lables, np.zeros(len(self.lables), dtype=np.int32))}
        # self.all_predict_count = pd.DataFrame(index=self.model_names,columns=self.lables,data=np.zeros((len(self.model_names),len(self.lables)),dtype=np.int32))
        pre_data = self.get_pre_data(pd.DataFrame([data], columns=config.feature_default))
        # print(pre_data)
        for m,name in zip(self.Models,self.model_names):
            lable_index = m.predict(pd.DataFrame([pre_data], columns=self.use_features))
            lable = m.get_leble_name(lable_index)
            self.model_dic[name] = lable
            self.all_predict_count.loc[[name],[lable]] +=1
            print(lable)
            if (lable in self.labels_dic):
                self.labels_dic[lable] += 1
            else:
                self.labels_dic[lable] = 1
        self.labels_dic = sorted(self.labels_dic.items(), key=lambda x: x[1])
        pre_lable = self.labels_dic[-1][0]


        self.integrated_model_dic[pre_lable]+=1

        return lable_index,self.all_predict_count,self.model_dic,pre_lable
    def show_data_from_csv(self):
        '''
        读取CSV的数据，进行可视化
        '''
        # lock.acquire()
        # plt.close()
        from visualization import show_data
        import matplotlib.pyplot as plt
        self.fig, self.subs = plt.subplots(2, 2)
        # lock.release()
        show_data(self.datas, self.lables, self.fig, self.subs)
    def show_data_new(self):
        '''
        读取CSV的数据，进行可视化
        '''
        from visualization import show_data_new
        import matplotlib.pyplot as plt
        self.fig, self.subs = plt.subplots(2, 2)
        show_data_new(self.datas, self.lables, self.fig, self.subs)
        return self.fig
    def show_add_data(self,data,lable_index=-1):
        '''
        可视化新增的数据
        :param data:
        :param lable_index:
        :return:
        '''
        #self.fig, self.subs = plt.subplots(2, 2)
        from visualization import add_new_data
        add_new_data(self.subs,data,lable_index)