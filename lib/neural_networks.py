import tensorflow as tf
from tensorflow import keras
# import matplotlib.pyplot as plt
from lib.machinelearningmodel import MachineLearningModel
from utils.collect import get_new_datas
import numpy as np
from keras.models import load_model
import pandas as pd
f = ["Z 轴振动速度", "X 轴振动速度", "Z 轴加速度峰值", "X 轴加速度峰值", "Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz",
                                   "Z 轴加速度均方根", "X 轴加速度均方根"]
f2 = ["Z 轴振动速度", "X 轴振动速度"]
m = MachineLearningModel(feature=f2)
train_x, test_x, train_y, test_y=m.get_data_and_split()
def get_model(need_train):
    if need_train:
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Normalization(axis=None),
            keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Normalization(axis=None),
            keras.layers.Dense(4)
        ])
        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])
        print(train_x)
        model.fit(train_x, train_y, epochs=30)
        test_loss, test_acc = model.evaluate(test_x,  test_y, verbose=2)

        print('\nTest accuracy:', test_acc)
        model.save('model_MLP.h5')
    else:
        model = load_model('model_MLP.h5')
    return model


if __name__ == '__main__':
    model = get_model(need_train=True)
    for data in get_new_datas(1000, filter_repeating_data=False):
        df=pd.DataFrame([data], columns=f)
        pre_data = m.sc.transform(df[f2])[0]
        pre_y=model.predict(np.array([pre_data]))
        print(pre_y[0])
        leble_index = np.argmax(pre_y[0])
        print(m.get_leble_name(leble_index))