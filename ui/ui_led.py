import numpy as np
from PyQt5.Qt import *
from pyqt_led import Led


allLabelNames =   [ u'灯亮圆心颜色：', u'灯亮边缘颜色：', u'灯灭圆心颜色：', u'灯灭边缘颜色：', u'边框内测颜色：', u'边框外侧颜色：',
                     u'边框外侧半径：', u'边框内侧半径：', u'中间圆灯半径：']

class MyLed(QAbstractButton):
     def __init__(self, parent=None,allAttributes=['colorOnBegin', 'colorOnEnd', 'colorOffBegin', 'colorOffEnd', 'colorBorderIn',
                          'colorBorderOut',
                          'radiusBorderOut', 'radiusBorderIn', 'radiusCircle'],allDefaultVal = [QColor(0, 240, 0), QColor(0, 160, 0), QColor(0, 68, 0), QColor(0, 28, 0),
                          QColor(140, 140, 140), QColor(100, 100, 100),
                          500, 450, 400]):
         super(MyLed, self).__init__(parent)
         self.parent = parent
         self.allAttributes = allAttributes
         self.allDefaultVal = allDefaultVal
         self.setEnabled(False)  # 不可按下
         self.initUI()

     def initUI(self):

         self.setMinimumSize(24, self.parent.height()/5)
         self.setCheckable(True)
         self.scaledSize = 1000.0    #为方便计算，将窗口短边值映射为1000
         self.setLedDefaultOption()

     def setLedDefaultOption(self):
         for attr, val in zip(self.allAttributes, self.allDefaultVal):
             setattr(self, attr, val)
         self.update()

     def setLedOption(self, opt='colorOnBegin', val=QColor(0,240,0)):
         if hasattr(self, opt):
             setattr(self, opt, val)
             self.update()

     def resizeEvent(self, evt):
         self.update()

     def paintEvent(self, evt):
         painter = QPainter(self)
         painter.setRenderHint(QPainter.Antialiasing, True)
         painter.setPen(QPen(Qt.black, 1))

         realSize = min(self.width(), self.height())                         #窗口的短边
         painter.translate(self.width()/2.0, self.height()/2.0)              #原点平移到窗口中心
         painter.scale(realSize/self.scaledSize, realSize/self.scaledSize)   #缩放，窗口的短边值映射为self.scaledSize
         gradient = QRadialGradient(QPointF(0, 0), self.scaledSize/2.0, QPointF(0, 0))   #辐射渐变

         #画边框外圈和内圈
         for color, radius in [(self.colorBorderOut, self.radiusBorderOut),  #边框外圈
                                (self.colorBorderIn, self.radiusBorderIn)]:   #边框内圈
             gradient.setColorAt(1, color)
             painter.setBrush(QBrush(gradient))
             painter.drawEllipse(QPointF(0, 0), radius, radius)

         # 画内圆
         gradient.setColorAt(0, self.colorOnBegin if self.isChecked() else self.colorOffBegin)
         gradient.setColorAt(1, self.colorOnEnd if self.isChecked() else self.colorOffEnd)
         painter.setBrush(QBrush(gradient))
         painter.drawEllipse(QPointF(0, 0), self.radiusCircle, self.radiusCircle)

class Demo(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._shape = np.array(['capsule', 'circle', 'rectangle'])
        self._color = np.array(['blue', 'green', 'orange', 'purple', 'red',
                                'yellow'])
        self._layout = QGridLayout(self)
        self._create_leds()
        self._arrange_leds()
        self.resize(400, 200)
        self.setWindowTitle('pyqt-led Demo')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def _create_leds(self):
        for s in self._shape:
            for c in self._color:
                exec('self._{}_{} = Led(self, on_color=Led.{}, shape=Led.{}, build="debug")'
                     .format(s, c, c, s))
                exec('self._{}_{}.setFocusPolicy(Qt.NoFocus)'.format(s, c))
                exec('self._{}_{}.turn_on(True)'.format(s, c))

    def _arrange_leds(self):
        for r in range(3):
            for c in range(6):
                exec('self._layout.addWidget(self._{}_{}, {}, {}, 1, 1, \
                      Qt.AlignCenter)'
                     .format(self._shape[r], self._color[c], r, c))

# 定义颜色常量
green = np.array([0, 255, 0], dtype=np.uint8)  # RGB: (0, 255, 0)
red = np.array([255, 0, 0], dtype=np.uint8)    # RGB: (255, 0, 0)
black = np.array([0, 0, 0], dtype=np.uint8)    # RGB: (0, 0, 0)
circle = 1  # 假设圆形形状为 1

class LedWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QGridLayout(self)
        self._create_leds()
        self._arrange_leds()
        self.resize(400, 200)
        self.setWindowTitle('pyqt-led Demo')

    def _create_leds(self):
        # 创建正常圆形灯
        self._normal_circle = Led(self, on_color=green, shape=circle, build="debug")
        # self._normal_circle.turn_on(True)

        # 创建偏轴圆形灯
        self._offset_circle = Led(self, on_color=red, shape=circle, build="debug")
        # self._offset_circle.turn_on(True)

        # 创建 Label 文本
        self._label_normal = QLabel('正常')
        self._label_offset = QLabel('偏轴')

    def _arrange_leds(self):
        # 排列 LED 灯和 Label 文本
        self._layout.addWidget(self._normal_circle, 0, 0, 1, 1, Qt.AlignCenter)
        self._layout.addWidget(self._label_normal, 1, 0, 1, 1, Qt.AlignCenter)
        self._layout.addWidget(self._offset_circle, 0, 1, 1, 1, Qt.AlignCenter)
        self._layout.addWidget(self._label_offset, 1, 1, 1, 1, Qt.AlignCenter)