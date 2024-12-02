# coding: utf-8
import json
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

import config
from utils.data_load import get_lable_datas_from_csv,get_datas_from_csv
from lib.machinelearningmodel import MachineLearningModel
from utils.frozen_dir import exists_path

class faultDiagnosisModel():
    """集成模型"""
    def __init__(self):
        self.use_features = config.feature_default
        self.model_names = ["逻辑回归", "支持向量机", "感知机", "K近邻算法", "随机森林", "决策树"]
        self.Models = []
        self.precisions = []
        self.integrated_model_dic = {}

    def run(self, is_by_lable=False,need_lable="正常"):
        if(is_by_lable):
            self.datas, self.labels, self.sc = get_lable_datas_from_csv(need_lable=need_lable)
        else:
            self.datas, self.labels, self.sc = get_datas_from_csv(features=self.use_features)

        # self.train_models()
        # 集成模型预测结果统计
        self.integrated_model_dic = {k: v for k, v in zip(self.labels, np.zeros(len(self.labels), dtype=np.int32))}
        self.all_predict_count = pd.DataFrame(index=self.model_names,columns=self.labels,data=np.zeros((len(self.model_names),len(self.labels)),dtype=np.int32))

    def run_res(self,res,labels):
            # 检查 res 是否为空列表
        if not res:
            # print("错误: res 为空列表")
            return

        # 检查 res 中的每个 DataFrame 是否有行数
        for df in res:
            if df.empty:
                # print("错误: res 中的 DataFrame 行数为 0")
                return
        sc = StandardScaler() # 标准化
        sc.fit(pd.concat(res))
        for i in range(len(res)):
            # 归一化
            res[i] = pd.DataFrame(sc.transform(res[i]), columns=self.use_features)

        self.datas, self.labels, self.sc = res, labels, sc

        # 集成模型预测结果统计
        self.integrated_model_dic = {k: v for k, v in zip(self.labels, np.zeros(len(self.labels), dtype=np.int32))}
        self.all_predict_count = pd.DataFrame(index=self.model_names, columns=self.labels,
                                              data=np.zeros((len(self.model_names), len(self.labels)), dtype=np.int32))

    def train_model(self,model,name=None,path='model',epochs=30):

        m = MachineLearningModel(model, datas=self.datas, labels=self.labels, sc=self.sc, feature=self.use_features, model_name=name)
        precision = m.train(name,path)
        print(name, " 预测的精度是：", precision)
        self.precisions.append(f'{name}'+' : '+f'{precision}')
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
            m2 = SVC(kernel='linear', C=1.0,random_state=42)
            # m2 = SVC()
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

    # def build_models(self):
    #     from sklearn.linear_model import LogisticRegression
    #     from sklearn.svm import SVC
    #     from sklearn.neural_network import MLPClassifier
    #     from sklearn.neighbors import KNeighborsClassifier
    #     from sklearn import tree
    #     from sklearn.ensemble import RandomForestClassifier
    #
    #     # 读取配置文件
    #     config_file = os.path.join(config.get_root_dir(), 'algorithm_params.json')
    #     if os.path.exists(config_file):
    #         with open(config_file, 'r') as f:
    #             params = json.load(f)
    #     else:
    #         self.build_models_none()
    #         return
    #
    #     models = []
    #     if "逻辑回归" in self.model_names:
    #         m1 = LogisticRegression(C=params.get("逻辑回归", {}).get("C", 1.0),
    #                                 penalty=params.get("逻辑回归", {}).get("penalty", "l2"))
    #         models.append(m1)
    #     if "支持向量机" in self.model_names:
    #         m2 = SVC(C=params.get("支持向量机", {}).get("C", 1.0),
    #                  kernel=params.get("支持向量机", {}).get("kernel", "linear"), random_state=42)
    #         models.append(m2)
    #     if "感知机" in self.model_names:
    #         m3 = MLPClassifier(solver='adam', alpha=1e-5,
    #                            hidden_layer_sizes=params.get("感知机", {}).get("hidden_layer_sizes", (64,)),
    #                            random_state=1, max_iter=params.get("感知机", {}).get("max_iter", 3000))
    #         models.append(m3)
    #     if "K近邻算法" in self.model_names:
    #         knn = KNeighborsClassifier(n_neighbors=params.get("K近邻算法", {}).get("n_neighbors", 10))
    #         models.append(knn)
    #     if "随机森林" in self.model_names:
    #         rfc = RandomForestClassifier(n_estimators=params.get("随机森林", {}).get("n_estimators", 100),
    #                                      random_state=0)
    #         models.append(rfc)
    #     if "决策树" in self.model_names:
    #         decision_tree = tree.DecisionTreeClassifier(criterion=params.get("决策树", {}).get("criterion", "entropy"))
    #         models.append(decision_tree)
    #
    #     return models, self.model_names

    def train_models(self, path='model', epochs=30):
        try:
            self.precisions = []
            models, model_names = self.build_models()
            self.Models = []
            for i in range(len(models)):
                model = self.train_model(model=models[i], name=model_names[i], path=path, epochs=epochs)
                self.Models.append(model)

            # 提取 StandardScaler 的参数
            sc_params = {
                'mean_': self.sc.mean_.tolist(),
                'scale_': self.sc.scale_.tolist(),
                'var_': self.sc.var_.tolist()
            }

            # 保存训练信息到 train.json
            train_info = {
                'labels': self.labels,
                'use_features': self.use_features,
                'model_names': self.model_names,
                # 'all_predict_count': self.all_predict_count.to_dict(),
                'sc_params': sc_params,
                'precisions' : self.precisions,
            }
            with open(os.path.join(path, 'train.json'), 'w') as f:
                json.dump(train_info, f, ensure_ascii=False, indent=4)

            # 单独保存 self.datas 中的每个 DataFrame
            data_path = os.path.join(path, 'data')
            os.makedirs(data_path, exist_ok=True)
            for i, df in enumerate(self.datas):
                df.to_csv(os.path.join(data_path, f'data_{i}.csv'), index=False)

            return self.precisions
        except Exception as e:
            raise e

    def load_train_info(self, path):
        """预处理"""
        with open(os.path.join(path, 'train.json'), 'r') as f:
            train_info = json.load(f)
        self.labels = train_info['labels']
        self.use_features = train_info['use_features']
        self.model_names = train_info['model_names']
        # self.all_predict_count = pd.DataFrame(train_info['all_predict_count'])
        self.all_predict_count = pd.DataFrame(index=self.model_names, columns=self.labels,
                     data=np.zeros((len(self.model_names), len(self.labels)), dtype=np.int32))
        # 从 train_info 中提取 StandardScaler 的参数
        sc_params = train_info['sc_params']

        # 创建新的 StandardScaler 对象并设置其参数
        self.sc = StandardScaler()
        self.sc.mean_ = np.array(sc_params['mean_'])
        self.sc.scale_ = np.array(sc_params['scale_'])
        self.sc.var_ = np.array(sc_params['var_'])

        # 单独加载 self.datas 中的每个 DataFrame
        data_path = os.path.join(path, 'data')
        self.datas = []
        for filename in sorted(os.listdir(data_path)):
            if filename.endswith('.csv'):
                df = pd.read_csv(os.path.join(data_path, filename))
                self.datas.append(df)


    def load_models(self,model_path=None):
        try:
            if not model_path:
                model_path = config.model_path
            if self.sc:
                import joblib
                models, model_names = self.build_models()
                file_counts = 0
                for dirpath, dirnames, filenames in os.walk(model_path):
                    for filename in filenames:
                        if filename.endswith('.model'):
                            file_counts += 1
                # if file_counts != len(models):
                #     self.train_models()
                #     print(self.Models)
                # else:
                self.Models = []
                for i in range(len(models)):
                    m = MachineLearningModel(models[i], datas=self.datas, labels=self.labels, sc=self.sc,
                                             feature=self.use_features, model_name=model_names[i])
                    m.load(model_names[i],model_path)
                    self.Models.append(m)
                    # print(self.Models)
            return self.Models
        except Exception as e:
            print(e)
    def get_pre_data(self,data):
        data = data[self.use_features]
        return self.sc.transform(data.values)[0]

    # def predict_models(self, data):
    #     try:
    #         # 集成模型预测结果统计
    #         integrated_model_dic = {k: v for k, v in zip(self.labels, np.zeros(len(self.labels), dtype=np.int32))}
    #         result = []
    #
    #         if not isinstance(data, list):
    #             datas = [data]
    #         else:
    #             datas = data
    #
    #         # 预处理所有数据
    #         pre_datas = [self.get_pre_data(pd.DataFrame([d], columns=self.use_features)) for d in datas]
    #
    #         # 将预处理后的数据转换为 DataFrame
    #         pre_data_df = pd.DataFrame(pre_datas, columns=self.use_features)
    #
    #         for pre_data in pre_data_df.iterrows():
    #             pre_data = pre_data[1]  # 获取行数据
    #
    #             # 每个分类预测的结果统计
    #             labels_dic = {}
    #             # 每个模型预测结果统计
    #             model_dic = {}
    #             all_predict_count = pd.DataFrame(index=self.model_names, columns=self.labels,
    #                                              data=np.zeros((len(self.model_names), len(self.labels)),
    #                                                            dtype=np.int32))
    #
    #             for m, name in zip(self.Models, self.model_names):
    #                 try:
    #                     lable_index = m.predict(pd.DataFrame([pre_data], columns=self.use_features))
    #                     lable = m.get_leble_name(lable_index)
    #                     model_dic[name] = lable
    #                     all_predict_count.loc[[name], [lable]] += 1
    #                     if lable in labels_dic:
    #                         labels_dic[lable] += 1
    #                     else:
    #                         labels_dic[lable] = 1
    #                 except Exception as e:
    #                     model_dic[name] = 'error'
    #
    #             labels_dic = sorted(labels_dic.items(), key=lambda x: x[1])
    #             pre_lable = labels_dic[-1][0]
    #
    #             integrated_model_dic[pre_lable] += 1
    #
    #             result.append((lable_index, all_predict_count, model_dic, pre_lable))
    #
    #         return result
    #     except Exception as e:
    #         raise e

    def predict_single_model(self, pre_data):
        # 每个分类预测的结果统计
        labels_dic = {}
        # 每个模型预测结果统计
        model_dic = {}
        all_predict_count = pd.DataFrame(index=self.model_names, columns=self.labels,
                                         data=np.zeros((len(self.model_names), len(self.labels)), dtype=np.int32))

        for m, name in zip(self.Models, self.model_names):
            try:
                lable_index = m.predict(pd.DataFrame([pre_data], columns=self.use_features))
                lable = m.get_leble_name(lable_index)
                model_dic[name] = lable
                all_predict_count.loc[[name], [lable]] += 1
                if lable in labels_dic:
                    labels_dic[lable] += 1
                else:
                    labels_dic[lable] = 1
            except Exception as e:
                model_dic[name] = 'error'

        labels_dic = sorted(labels_dic.items(), key=lambda x: x[1])
        pre_lable = labels_dic[-1][0]

        return (lable_index, all_predict_count, model_dic, pre_lable)

    def predict_models(self, data):
        try:
            # 集成模型预测结果统计
            integrated_model_dic = {k: v for k, v in zip(self.labels, np.zeros(len(self.labels), dtype=np.int32))}
            result = []

            if not isinstance(data, list):
                datas = [data]
            else:
                datas = data

            # 预处理所有数据
            pre_datas = [self.get_pre_data(pd.DataFrame([d], columns=self.use_features)) for d in datas]

            with ThreadPoolExecutor() as executor:
                results = list(executor.map(self.predict_single_model, pre_datas))

            for lable_index, all_predict_count, model_dic, pre_lable in results:
                integrated_model_dic[pre_lable] += 1
                result.append((lable_index, all_predict_count, model_dic, pre_lable))

            return result
        except Exception as e:
            raise e

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
        show_data(self.datas, self.labels, self.fig, self.subs)
    def show_data_new(self):
        '''
        读取CSV的数据，进行可视化
        '''
        from visualization import show_data_new
        import matplotlib.pyplot as plt
        self.fig, self.subs = plt.subplots(2, 2)
        show_data_new(self.datas, self.labels, self.fig, self.subs)
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

