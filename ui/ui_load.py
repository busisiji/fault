import sys

from PyQt5.Qt import *
# 加载动画的窗口
class Loading_Win(QWidget):
    def __init__(self,mainWin):
        super(Loading_Win, self).__init__()
        # 获取主窗口的坐标
        self.m_winX = mainWin.x()
        self.m_winY = mainWin.y()
        self.initUI()
    def initUI(self):
        # 设置窗口基础类型
        self.resize(500,500)	# 设置加载界面的大小
        self.move(self.m_winX+340,self.m_winY+155)	# 移动加载界面到主窗口的中心
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint) # 设置窗口无边框|对话框|置顶模式
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.Dialog)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 设置背景透明
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # 加载动画画面
        self.loading_gif = QMovie('../icons/logo.gif')
        self.loading_label = QLabel(self)
        self.loading_label.setMovie(self.loading_gif)
        self.loading_gif.start()
