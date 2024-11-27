import time

from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QSplashScreen, QMainWindow, qApp


class MySplashScreen(QSplashScreen):
    def __init__(self):
        super(MySplashScreen, self).__init__()

        # 新建动画
        self.movie = QMovie(r'icons/logo.gif')
        self.movie.frameChanged.connect(lambda: self.setPixmap(self.movie.currentPixmap()))
        self.movie.start()

    def mousePressEvent(self, QMouseEvent):
        pass
class LoadDataWorker(QObject):
    finished = pyqtSignal()
    message_signal = pyqtSignal(str)

    def __init__(self):
        super(LoadDataWorker, self).__init__()

    def run(self):
        for i in range(10):
            time.sleep(0.1)
            self.message_signal.emit(f'加载中...{str(i * 10)}%')
        self.finished.emit()

class Form(QMainWindow):
    def __init__(self, splash):
        super(Form, self).__init__()
        self.resize(800, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # 置顶

        self.splash = splash

        self.load_thread = QThread()
        self.load_worker = LoadDataWorker()
        self.load_worker.moveToThread(self.load_thread)
        self.load_thread.started.connect(self.load_worker.run)
        self.load_worker.message_signal.connect(self.set_message)
        self.load_worker.finished.connect(self.load_worker_finished)
        self.load_thread.start()

        while self.load_thread.isRunning():
            qApp.processEvents()  # 不断刷新，保证动画流畅

        self.load_thread.deleteLater()

    def load_worker_finished(self):
        self.load_thread.quit()
        self.load_thread.wait()

    def set_message(self, message):
        self.splash.showMessage(message, Qt.AlignLeft | Qt.AlignBottom, Qt.white)