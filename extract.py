#coding=utf-8
import platform
import nibabel as ni
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QLabel, QMessageBox, QComboBox, QMainWindow, QApplication, QMenu, QLineEdit, QPushButton, QGridLayout
from PyQt5.QtCore import QCoreApplication, Qt, QRect
import pandas as pd

################################################################################


################################################################################

class ui_extract(QMainWindow):
    def __init__(self, parent, lan = 0):
        super(ui_extract, self).__init__(parent)
        self.temp = parent
        self.lan = lan

        self.path_cbf = ""
        self.path_template = ""
        self.path_save = ""
        self.index_roi = []

        self.setGeometry(307,309,500,250) # 设置子窗口的尺寸
        self.setMinimumSize(200,130) # 设置子窗口的最小尺寸

        self.initUI()

    def initUI(self):
        if self.lan == 0:
            self.setWindowTitle("Extract ROIs")
            self.label_cbf = QLabel("Directory of CBF:", self)
            self.label_template = QLabel("Directory of Template:", self)
            self.label_index = QLabel("Index of ROIs to extract:", self)
            self.label_output = QLabel("Directory of Output Fils:", self)

        elif self.lan == 1:
            self.setWindowTitle("区域值提取")
            self.label_cbf = QLabel("CBF图像路径:", self)
            self.label_template = QLabel("模板图像路径:", self)
            self.label_index = QLabel("待提取区域编号:", self)
            self.label_output = QLabel("文件存储路径:", self)

        self.le_cbf =  QLineEdit(self)
        self.le_tmp = QLineEdit(self)
        self.le_index = QLineEdit(self)
        self.le_output = QLineEdit(self)

        self.bt_cbf = QPushButton("...", self)
        self.bt_tmp = QPushButton("...", self)
        self.bt_output = QPushButton("...", self)
        if self.lan == 0:
            self.bt_ok = QPushButton("Run", self)
        elif self.lan == 1:
            self.bt_ok = QPushButton("运行", self)

        self.grid_dir = QGridLayout()
        self.grid_dir.addWidget(self.label_cbf, 0, 0)
        self.grid_dir.addWidget(self.le_cbf, 0, 1)
        self.grid_dir.addWidget(self.bt_cbf, 0, 2)
        self.grid_dir.addWidget(self.label_template, 1, 0)
        self.grid_dir.addWidget(self.le_tmp, 1, 1)
        self.grid_dir.addWidget(self.bt_tmp, 1, 2)
        self.grid_dir.addWidget(self.label_index, 2, 0)
        self.grid_dir.addWidget(self.le_index, 2, 1)
        self.grid_dir.addWidget(self.label_output, 3, 0)
        self.grid_dir.addWidget(self.le_output, 3, 1)
        self.grid_dir.addWidget(self.bt_output, 3, 2)
        self.grid_dir.addWidget(self.bt_ok, 4, 1)

        self.bt_cbf.clicked.connect(self.select_file_cbf)
        self.bt_tmp.clicked.connect(self.select_file_tmp)
        self.bt_output.clicked.connect(self.select_file_output)
        self.bt_ok.clicked.connect(self.make_extract)

        self.resizeEvent = self.adjustSize

    def select_file_cbf(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system() == "Linux":
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        temp_text = ""
        self.le_cbf.setText(str(self.path_cbf).replace('[','').replace(']',''))

    def select_file_tmp(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_template = QFileDialog.getOpenFileName(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_template = QFileDialog.getOpenFileName(self, 'Select File', './')[0]
            else:
                self.path_template = QFileDialog.getOpenFileName(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_template = QFileDialog.getOpenFileName(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system() == "Linux":
                self.path_template = QFileDialog.getOpenFileName(self, '选择文件', './')[0]
            else:
                self.path_template = QFileDialog.getOpenFileName(self, '选择文件', './')[0]
        temp_text = ""
        self.le_tmp.setText(str(self.path_template).replace('[','').replace(']',''))

    def select_file_output(self):
        if self.lan == 0:
            self.path_save = QFileDialog.getSaveFileName(self, 'Select File', './', "CSV Files(*.csv);;All Files(*)")[0]
        elif self.lan == 1:
            self.path_save = QFileDialog.getSaveFileName(self, '选择文件', './', "CSV文件(*.csv);;所有文件(*)")[0]
        temp_text = ""
        self.le_output.setText(str(self.path_save).replace('[','').replace(']',''))

    def adjustSize(self, event):
        self.grid_dir.setGeometry(QRect(50, 50, (self.width() - 100), (self.height() - 100)))

    def make_extract(self):
        template = ni.load(self.path_template)
        data_template = template.get_fdata()
        data_template[np.isnan(data_template)] = 0
        data_template[np.isinf(data_template)] = 0
        result = {}
        for item in self.path_cbf:
            cbf = ni.load(item)
            data = cbf.get_fdata()
            index = []
            mean = []
            std = []
            if self.le_index.text() == "":
                max_template = data_template.max()
                for i in range(max_template):
                    temp = data * (data_template == (i + 1))
                    mean.append(temp[temp > 0].mean())
                    std.append(temp[temp > 0].std())
                    index.append(i + 1)
            elif ":" in self.le_index.text():
                text = self.le_index.text()
                temp_text = text.split(":")
                if len(temp_text) == 2:
                    for i in range(range(temp_text[0], temp_text[1])):
                        temp = data * (data_template == (i + 1))
                        mean.append(temp[temp > 0].mean())
                        std.append(temp[temp > 0].std())
                        index.append(i + 1)

                elif len(temp_text) == 3:
                    for i in range(range(temp_text[0], temp_text[1], temp_text[2])):
                        temp = data * (data_template == (i + 1))
                        mean.append(temp[temp > 0].mean())
                        std.append(temp[temp > 0].std())
                        index.append(i + 1)

            elif "," in self.le_index.text():
                text = self.le_index.text()
                temp_text = text.split(",")
                for index_text in temp_text:
                    temp = data * (data_template == (int(index_text)))
                    mean.append(temp[temp > 0].mean())
                    std.append(temp[temp > 0].std())
                    index.append(index_text)
            else:
                if self.lan == 0:
                    warn_msg(self, "Input the index in the form of 1:5:2 or 1:5 or 1,2,3")
                elif self.lan == 1:
                    warn_msg(self, "请以1:5:2或1:5或1,2,3的格式输入序号")
            result[item] = mean

        df = pd.DataFrame(data = result, index = index)
        df.to_csv(self.path_save)
