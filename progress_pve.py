import numpy as np
import nibabel as ni
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QPushButton, QGridLayout, QGroupBox, QVBoxLayout, QProgressBar, qApp
from PyQt5.QtCore import QCoreApplication, Qt
from display import *

################################################################################

class ProgressBar_pve(QMainWindow):
    def __init__(self, parent, max, lan = 0):
        super(ProgressBar_pve, self).__init__(parent)
        self.setGeometry(300,300,400,300) # 设置子窗口的尺寸
        self.setMinimumSize(200,100) # 设置子窗口的最小尺寸
        self.setWindowTitle("PVE Correlation Progress")
        self.resizeEvent = self.adjustSize # 当子窗口的尺寸变化时，自动调整label的大小
        self.lan = lan
        self.max = max
        self.initUI()

    def initUI(self):
        self.grid_ui = QGridLayout()
        self.label_pve = QLabel(self)
        self.pb_pve = QProgressBar(self)
        if self.lan == 0:
            self.bt_cancel = QPushButton('Cancel', self)
        elif self.lan == 1:
            self.bt_cancel = QPushButton('取消', self)
        self.grid_ui.addWidget(self.pb_pve, 0, 0)
        self.grid_ui.addWidget(self.label_pve, 0, 1)
        self.grid_ui.addWidget(self.bt_cancel, 0, 2)

        self.pb_pve.setMaximum(self.max)
        self.pb_pve.setValue(0)
        self.pb_pve.setFormat("%p")
        if self.lan == 0:
            self.label_pve.setText("Busy...")
        elif self.lan == 1:
            self.label_pve.setText("正在计算...")
        self.bt_cancel.clicked.connect(qApp.quit)

    def set_step(self, value):
        self.pb_pve.setValue(value)

    def adjustSize(self, event):
        self.grid_ui.setGeometry(QRect(50, 50, (self.width() - 100), (self.height() - 100))) # 将组件全部显示后调整尺寸
