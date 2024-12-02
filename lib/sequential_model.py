import time
start_1 = time.perf_counter()
# import tensorflow as tf
# from tensorflow import keras
# import matplotlib.pyplot as plt
# from machinelearningmodel import MachineLearningModel
# from collect import get_new_data
from utils import frozen_dir
import numpy as np
# from keras.models import load_model
import pandas as pd
print('导入库',time.perf_counter()-start_1)
f = ["Z 轴振动速度", "X 轴振动速度", "Z 轴加速度峰值", "X 轴加速度峰值", "Z 轴峰值速度分量频率 Hz", "X 轴峰值速度分量频率 Hz",
         "Z 轴加速度均方根", "X 轴加速度均方根"]
f2 = ["Z 轴振动速度", "X 轴振动速度"]
# m = MachineLearningModel(feature=f2)

def get_model(train_x, test_x, train_y, test_y,need_train):
    import tensorflow as tf
    from tensorflow import keras
    from keras.models import load_model
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
        history = model.fit(train_x, train_y, epochs=50)
        test_loss, test_acc = model.evaluate(test_x,  test_y, verbose=2)

        print('\nTest accuracy:', test_acc)
        model.save('model_MLP.h5')
        # plot_history(history)
    else:
        model = load_model(frozen_dir.app_path() + r'/model_MLP.h5')
        history = 0
    return model,history

# def plot_history(history):
#   hist = pd.DataFrame(history.history)
#   hist['epoch'] = history.epoch
#
#   plt.figure()
#   plt.xlabel('Epoch')
#   plt.ylabel('Model Train')
#   plt.plot(hist['loss'],
#            label='loss')
#   plt.plot(hist['accuracy'],
#            label = 'accuracy')
#   plt.xlim([0, 30])
#   plt.ylim([0,1])
#
#   plt.legend()
#   plt.show()


def start(need_train=True,btn_texts = ["Z 轴振动速度", "X 轴振动速度"]):
    try:
        from lib.machinelearningmodel import MachineLearningModel
        global m
        m = MachineLearningModel(feature=btn_texts)
        # m = MachineLearningModel(feature=f2)
        train_x, test_x, train_y, test_y = m.get_data_and_split()
        model,history = get_model(train_x, test_x, train_y, test_y,need_train=need_train)
        return model,history
        # for data in get_new_data(1000, filter_repeating_data=False):
    except Exception as e:
        print(e)
        return None,None

def get_result(data,model):
    # m = MachineLearningModel(feature=f2)
    df=pd.DataFrame([data], columns=f)
    pre_data = m.sc.transform(df[f2])[0]
    pre_y=model.predict(np.array([pre_data]))
    print(pre_y[0])
    leble_index = np.argmax(pre_y[0])
    print(m.get_leble_name(leble_index))
    return m.get_leble_name(leble_index)

if __name__ == '__main__':
    start()