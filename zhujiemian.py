# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import QThread, QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow
from zhujiemian_ui import *
from clickme import paURL
from clickme import pachong

class Thread(QThread):
    def __init__(self, keyword, num):
        super(Thread, self).__init__()
        self.keyword = keyword
        self.num = num

    def run(self):
        paURL(self.keyword, self.num)


qmut_1 = QMutex()
class Thread_2(QThread):  # 线程2
    def __init__(self, deepth):
        super(Thread_2,self).__init__()
        self.deepth = deepth

    def run(self):
        qmut_1.lock()
        pachong(self.deepth)
        qmut_1.unlock()


class MainWindow(QMainWindow, Ui_start):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(sys.exit)
        self.pushButton.clicked.connect(self.start)
        self.pushButton_3.clicked.connect(self.start_2)

    def start(self):
        keyword = self.lineEdit.text()
        num = self.lineEdit1.text()
        num = int(num)
        self.do = Thread(keyword, num)
        self.do.start()

    def start_2(self):
        deepth = self.lineEdit2.text()
        deepth = int(deepth)
        self.do = Thread_2(deepth)
        self.do.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
