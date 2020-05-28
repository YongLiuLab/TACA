#coding=utf-8

import nibabel as ni
import numpy as np
# from nilearn.image import smooth_img
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QLineEdit, QRadioButton, QPushButton, QGridLayout, QFileDialog, QMessageBox, QCheckBox, QGroupBox, QVBoxLayout, QProgressBar
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import QCoreApplication, Qt, QRect
from nilearn.image import resample_to_img
from skimage import filters
# import qimage2ndarray as q2n
import sys, platform
# import pypreprocess
from settings import *
from display import *
from thread_pve import *

################################################################################

class ui_cbf(QMainWindow):
    def __init__(self, parent, lan = 0):
        super(ui_cbf, self).__init__(parent)
        # print(parent.fname)
        self.temp = parent
        self.setGeometry(303,304,500,350) # 设置子窗口的尺寸
        self.setMinimumSize(200,130) # 设置子窗口的最小尺寸
        self.lan = lan
        self.path_single = self.temp.fname
        self.path_dwi = ""
        self.path_ref = ""
        self.path_pre = ""
        self.path_lat = ""
        self.display_type = 0
        # 设置计算cbf图像的输入情况，0：输入单幅图像，其中不同volume对应dwi和ref像(GE)，1：输入DWI像和REF像，2：输入两次采样的ASL像和REF像self.display_type = 0 # 用于确认输入nii的模式，与calculation的ui_cbf.display_type一致

        self.display_asl = 0 # 用于确认ASL的不同形式，0代表PCASL，1代表QUIPSS II PASL，两者计算CBF使用的参数有区别
        self.lamda = 0.9
        """ brain/blood partition coefficient,单位为ml/g,使用What Is the Correct Value for the Brain-Blood Partition Coefficient
for Water?中的结论"""
        self.PLD = 2000 / 1000
        """ post labeling delay,单位为秒,使用Recommended Implementation of Arterial Spin Labeled Perfusion MRI for Clinical
Applications: A consensus of the ISMRM Perfusion Study Group and the European Consortium for ASL in Dementia给出的参考值
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
        ┃ PCASL Labeling Duration              ┃     1800ms    ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ PCASL PLD - Neonates                 ┃     2000ms    ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ PCASL PLD - Children                 ┃     1500ms    ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ PCASL PLD - Healthy subjects < 70 yrs┃     1800ms    ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ PCASL PLD - Healthy subjects > 70 yrs┃     2000 ms   ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ PCASL PLD - Adult clinical patients  ┃     2000 ms   ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ PASL TI1                             ┃      800 ms   ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ PASL TI                              ┃ Use PCASL PLD ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ λ (blood-brain partition coefficient)┃     0.9 ml/g  ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ T1, blood at 3.0 Tesla               ┃     1650 ms   ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ T1, blood at 1.5 Tesla               ┃     1350 ms   ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ α (labeling efficiency) for PCASL    ┃     0.85      ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━┫
        ┃ α (labeling efficiency) for PASL     ┃     0.98      ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━┛
        """
        self.T1_blood = 1650 / 1000 # 3T为1650ms， 1.5T为1350ms
        # longitudinal relaxation time of blood,单位为秒
        self.alpha = 0.85 # PCASL为0.85, PASL为0.98
        # labeling efficiency
        self.tau = 1800 / 1000
        # label duration,单位为秒
        self.TI =  2000 / 1000
        # inversion time,单位是秒
        self.TI_1 = 800 / 1000
        # bolus duration,单位为秒
        self.ratio = 1
        # 通过参数计算出的系数，默认是1(但通常不是)

        self.initUI()

    def initUI(self):
        if self.lan == 0:
            self.setWindowTitle("CBF Calculation")
            self.button_settings = QPushButton("Details...", self)
            self.button_operate = QPushButton("Operate", self)
        elif self.lan == 1:
            self.setWindowTitle("CBF计算")
            self.button_settings = QPushButton("参数设置...", self)
            self.button_operate = QPushButton("开始计算", self)
        self.button_settings.setSizePolicy(150,50)

        self.button_operate.setSizePolicy(150,50)
        self.button_operate.clicked.connect(self.calcCBF)
        self.button_settings.clicked.connect(self.createSetting)

        if self.lan == 0:
            self.label_radio = QLabel("Input Mode", self)
            self.button_type_single = QRadioButton("Single", self)
            self.button_type_dwi = QRadioButton("PWI and Ref", self)
            self.button_type_asl = QRadioButton("ASLs and Ref", self)
            self.label_name_dir_single = QLabel("The whole Image:", self)
            self.label_name_dir_dwi = QLabel("PWI Image:", self)
            self.label_name_dir_preasl = QLabel("Control ASL:", self)
            self.label_name_dir_lateasl = QLabel("Label ASL:", self)
            self.label_name_dir_ref = QLabel("Reference Image:", self)
            self.cb_autothr = QCheckBox("Auto Threshold", self)
            self.cb_autosave = QCheckBox("Auto Save", self)
        elif self.lan == 1:
            self.label_radio = QLabel("输入模式", self)
            self.button_type_single = QRadioButton("单张nii", self)
            self.button_type_dwi = QRadioButton("灌注差及参考像", self)
            self.button_type_asl = QRadioButton("不同ASL及参考像", self)
            self.label_name_dir_single = QLabel("图像路径:", self)
            self.label_name_dir_dwi = QLabel("ASL差值路径:", self)
            self.label_name_dir_preasl = QLabel("ASL控制像路径:", self)
            self.label_name_dir_lateasl = QLabel("ASL标记像路径:", self)
            self.label_name_dir_ref = QLabel("参考像路径:", self)
            self.cb_autothr = QCheckBox("自动阈值处理", self)
            self.cb_autosave = QCheckBox("自动保存", self)

        self.button_type_single.clicked.connect(self.radiobutton_clicked)
        self.button_type_dwi.clicked.connect(self.radiobutton_clicked)
        self.button_type_asl.clicked.connect(self.radiobutton_clicked)
        self.cb_autothr.setChecked(True)
        self.cb_autosave.setChecked(True)

        # 使用单选框选择ASL图像的输入模式，对应不同的display_type

        self.grid_radiobutton = QGridLayout()
        self.grid_dir = QGridLayout()
        self.grid_operate = QGridLayout()
        self.grid_full = QGridLayout()
        self.grid_ui = QGridLayout()
        self.grid_cb = QGridLayout()

        self.label_val_dir_single = QLineEdit(self)
        self.label_val_dir_dwi = QLineEdit(self)
        self.label_val_dir_preasl = QLineEdit(self)
        self.label_val_dir_lateasl = QLineEdit(self)
        self.label_val_dir_ref = QLineEdit(self)


        if type(self.path_single) == str:
            self.label_val_dir_single.setText(self.path_single)
        else:
            self.path_single = ""
            self.label_val_dir_single.setText(self.path_single)

        self.button_dir_single = QPushButton("...", self)
        self.button_dir_dwi = QPushButton("...", self)
        self.button_dir_preasl = QPushButton("...", self)
        self.button_dir_lateasl = QPushButton("...", self)
        self.button_dir_ref = QPushButton("...", self)

        self.button_dir_single.setSizePolicy(50, 50)
        self.button_dir_dwi.setSizePolicy(50,50)
        self.button_dir_preasl.setSizePolicy(50,50)
        self.button_dir_lateasl.setSizePolicy(50,50)
        self.button_dir_ref.setSizePolicy(50,50)

        self.button_dir_single.clicked.connect(self.select_file_single)
        self.button_dir_dwi.clicked.connect(self.select_file_dwi)
        self.button_dir_ref.clicked.connect(self.select_file_ref)
        self.button_dir_preasl.clicked.connect(self.select_file_pre)
        self.button_dir_lateasl.clicked.connect(self.select_file_lat)

        self.grid_cb.addWidget(self.cb_autothr, 0, 0)
        self.grid_cb.addWidget(self.cb_autosave, 0, 1)

        self.grid_dir.addWidget(self.label_name_dir_single, 0, 0)
        self.grid_dir.addWidget(self.label_val_dir_single, 0, 1)
        self.grid_dir.addWidget(self.button_dir_single, 0, 2)

        self.grid_dir.addWidget(self.label_name_dir_dwi, 0, 0)
        self.grid_dir.addWidget(self.label_val_dir_dwi, 0, 1)
        self.grid_dir.addWidget(self.button_dir_dwi, 0, 2)

        self.grid_dir.addWidget(self.label_name_dir_preasl, 0, 0)
        self.grid_dir.addWidget(self.label_val_dir_preasl, 0, 1)
        self.grid_dir.addWidget(self.button_dir_preasl, 0, 2)

        self.grid_dir.addWidget(self.label_name_dir_lateasl, 1, 0)
        self.grid_dir.addWidget(self.label_val_dir_lateasl, 1, 1)
        self.grid_dir.addWidget(self.button_dir_lateasl, 1, 2)

        self.grid_dir.addWidget(self.label_name_dir_ref, 2, 0)
        self.grid_dir.addWidget(self.label_val_dir_ref, 2, 1)
        self.grid_dir.addWidget(self.button_dir_ref, 2, 2)

        self.grid_dir.addLayout(self.grid_cb, 3, 0)

        self.grid_radiobutton.addWidget(self.label_radio, 0, 0)
        self.grid_radiobutton.addWidget(self.button_type_single, 1, 0)
        self.grid_radiobutton.addWidget(self.button_type_dwi, 2, 0)
        self.grid_radiobutton.addWidget(self.button_type_asl, 3, 0)
        # self.grid_radiobutton.addWidget(self.cb_directory, 4, 0)
        self.grid_radiobutton.setSpacing(10)

        self.grid_operate.addWidget(self.button_operate, 0, 0)
        self.grid_operate.addWidget(self.button_settings, 0, 1)
        self.grid_operate.setSpacing(10)

        self.grid_full.addLayout(self.grid_dir, 0, 0)
        self.grid_full.addLayout(self.grid_operate, 1, 0)

        self.grid_ui.addLayout(self.grid_radiobutton, 0, 0)
        self.grid_ui.addLayout(self.grid_full, 0, 1)
        self.grid_ui.setGeometry(QRect(50, 50, 400, 250))

        self.set_hiden(self.display_type)

        self.resizeEvent = self.adjustSize

    def set_hiden(self, index):
        # index0-2对应display_type的0-2，其他值时将所有模块设为可见以便调节
        if index == 0:
            self.label_name_dir_single.setHidden(False)
            self.label_val_dir_single.setHidden(False)
            self.button_dir_single.setHidden(False)
            self.label_name_dir_dwi.setHidden(True)
            self.label_val_dir_dwi.setHidden(True)
            self.button_dir_dwi.setHidden(True)
            self.label_name_dir_preasl.setHidden(True)
            self.label_val_dir_preasl.setHidden(True)
            self.button_dir_preasl.setHidden(True)
            self.label_name_dir_lateasl.setHidden(True)
            self.label_val_dir_lateasl.setHidden(True)
            self.button_dir_lateasl.setHidden(True)
            self.label_name_dir_ref.setHidden(True)
            self.label_val_dir_ref.setHidden(True)
            self.button_dir_ref.setHidden(True)
            self.button_type_single.setChecked(True)
            self.button_type_dwi.setChecked(False)
            self.button_type_asl.setChecked(False)
        elif index == 1:
            self.label_name_dir_single.setHidden(True)
            self.label_val_dir_single.setHidden(True)
            self.button_dir_single.setHidden(True)
            self.label_name_dir_dwi.setHidden(False)
            self.label_val_dir_dwi.setHidden(False)
            self.button_dir_dwi.setHidden(False)
            self.label_name_dir_preasl.setHidden(True)
            self.label_val_dir_preasl.setHidden(True)
            self.button_dir_preasl.setHidden(True)
            self.label_name_dir_lateasl.setHidden(True)
            self.label_val_dir_lateasl.setHidden(True)
            self.button_dir_lateasl.setHidden(True)
            self.label_name_dir_ref.setHidden(False)
            self.label_val_dir_ref.setHidden(False)
            self.button_dir_ref.setHidden(False)
            self.button_type_single.setChecked(False)
            self.button_type_dwi.setChecked(True)
            self.button_type_asl.setChecked(False)
        elif index == 2:
            self.label_name_dir_single.setHidden(True)
            self.label_val_dir_single.setHidden(True)
            self.button_dir_single.setHidden(True)
            self.label_name_dir_dwi.setHidden(True)
            self.label_val_dir_dwi.setHidden(True)
            self.button_dir_dwi.setHidden(True)
            self.label_name_dir_preasl.setHidden(False)
            self.label_val_dir_preasl.setHidden(False)
            self.button_dir_preasl.setHidden(False)
            self.label_name_dir_lateasl.setHidden(False)
            self.label_val_dir_lateasl.setHidden(False)
            self.button_dir_lateasl.setHidden(False)
            self.label_name_dir_ref.setHidden(False)
            self.label_val_dir_ref.setHidden(False)
            self.button_dir_ref.setHidden(False)
            self.button_type_single.setChecked(False)
            self.button_type_dwi.setChecked(False)
            self.button_type_asl.setChecked(True)
        else:
            self.label_name_dir_single.setHidden(False)
            self.label_val_dir_single.setHidden(False)
            self.button_dir_single.setHidden(False)
            self.label_name_dir_dwi.setHidden(False)
            self.label_val_dir_dwi.setHidden(False)
            self.button_dir_dwi.setHidden(False)
            self.label_name_dir_preasl.setHidden(False)
            self.label_val_dir_preasl.setHidden(False)
            self.button_dir_preasl.setHidden(False)
            self.label_name_dir_lateasl.setHidden(False)
            self.label_val_dir_lateasl.setHidden(False)
            self.button_dir_lateasl.setHidden(False)
            self.label_name_dir_ref.setHidden(False)
            self.label_val_dir_ref.setHidden(False)
            self.button_dir_ref.setHidden(False)

    def select_file_single(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_single = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_single = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_single = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_single = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system() == "Linux":
                self.path_single = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_single = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        temp_text = ""
        self.label_val_dir_single.setText(str(self.path_single).replace('[','').replace(']',''))

    def select_file_dwi(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_dwi = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_dwi = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_dwi = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_dwi = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system() == "Linux":
                self.path_dwi = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_dwi = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.label_val_dir_dwi.setText(str(self.path_dwi).replace('[','').replace(']',''))

    def select_file_ref(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_ref = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_ref = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_ref = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]

        elif self.lan == 1:
            self.path_ref = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
        self.label_val_dir_ref.setText(str(self.path_ref).replace('[','').replace(']',''))

    def select_file_pre(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_pre = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_pre = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_pre = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_pre = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system() == "Linux":
                self.path_pre = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_pre = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.label_val_dir_preasl.setText(str(self.path_pre).replace('[','').replace(']',''))

    def select_file_lat(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_lat = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_lat = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_lat = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_lat = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system() == "Linux":
                self.path_lat = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_lat = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.label_val_dir_lateasl.setText(str(self.path_lat).replace('[','').replace(']',''))

    def radiobutton_clicked(self):
        if self.button_type_single.isChecked() == True:
            self.display_type = 0
        elif self.button_type_dwi.isChecked() == True:
            self.display_type = 1
        elif self.button_type_asl.isChecked() == True:
            self.display_type = 2
        self.set_hiden(self.display_type)

    def createSetting(self):
        # 创建设置面板，包含对CBF计算参数的选择和输入
        settings = ui_setting(self, self.lan)
        # settings.set_value(self.display_asl, lamda, self.PLD, self.T1_blood, self.alpha, self.tau, self.TI, self.TI_1)
        settings.show()

    def adjustSize(self, event):
        self.set_hiden(10086) # 只要是else里的值就行
        self.grid_ui.setGeometry(QRect(50, 50, (self.width() - 100), (self.height() - 100))) # 将组件全部显示后调整尺寸
        self.set_hiden(self.display_type) # 设置组件隐藏状态

    def get_value(self):
        return self.display_asl, self.lamda, self.PLD, self.T1_blood, self.alpha, self.tau, self.TI, self.TI_1

    def set_value(self, display_asl, lamda, PLD, T1_blood, alpha, tau, TI, TI_1):
        self.display_asl = display_asl
        self.lamda = lamda
        self.PLD = PLD
        self.T1_blood = T1_blood
        self.alpha = alpha
        self.tau = tau
        self.TI = TI
        self.TI_1 = TI_1

    def calcCBF(self):
        if self.display_type == 0:
            self.calcbf_simple()
        elif self.display_type == 1:
            self.calcbf_dwi()
        elif self.display_type == 2:
            self.calcbf_asl()

    def make_cbf(self, data_dwi, data_ref, nii):
        data = self.ratio * data_dwi / data_ref
        data[np.isnan(data)] = 0
        data[np.isinf(data)] = 0

        if self.cb_autothr.isChecked():
            thr = 1.5 * np.median(data[data.nonzero()])
            print(thr)
            nii_save = ni.Nifti1Image(data * (data <= thr), nii.affine, nii.header)
        else:
            nii_save = ni.Nifti1Image(data, nii.affine, nii.header)
        return nii_save

    def get_cbfrom_asl(self, path_1, path_2, path_3):
        nii_output = []
        if path_3 == "":
            if path_2 == "":
                # path_2, path_3均为空，认为读取了calcbf_simple的路径信息
                # getOpenFileNames返回值为路径的list,而非路径对应的str
                self.temp.fname = [item.replace(".nii", "_cbf.nii") for item in path_1]
                for path in path_1:
                    nii = ni.load(path)
                    if len(nii.get_fdata().shape) == 4:
                        if nii.get_fdata().shape[3] == 2:
                            nii_output.append(self.make_cbf(nii.get_fdata()[:,:,:,0], nii.get_fdata()[:,:,:,1], nii))
                        else:
                            if self.lan == 0:
                                warn_msg(self, "The Nifti File does not contain PWI Image and PD Image.")
                            elif self.lan == 1:
                                warn_msg(self, "单幅NII图像并未正确包含PWI和PD信息")
                    else:
                        if self.lan == 0:
                            warn_msg(self, "The Nifti File does not contain PWI Image and PD Image.")
                        elif self.lan == 1:
                            warn_msg(self, "单幅NII图像并未正确包含PWI和PD信息")
                self.temp.set_nii(nii_output)


            elif path_1 != "":
                # path_3为空，认为读取了calcbf_dwi的路径信息
                # 如果其中一个路径只有一项，则认为是对应所有另一个路径(可能导致其他问题，可以考虑进行warning)
                if len(path_1) != len(path_2) and len(path_1) != 1 and len(path_2) != 1:
                    if self.lan == 0:
                        warn_msg(self, "DWI series and PD series have different components.")
                    elif self.lan == 1:
                        warn_msg(self, "DWI与PD像数量不一致")
                elif len(path_1) == 1:
                    self.temp.fname = [item.replace(".nii", "_cbf.nii") for item in path_2]
                    nii_dwi = ni.load(path_1[0])
                    for path in path_2:
                        nii_ref = ni.load(path)
                        if len(nii_ref.get_fdata().shape) >= 3:
                            nii_output.append(self.make_cbf(nii_dwi.get_fdata(), nii_ref.get_fdata(), nii_dwi))
                        else:
                            if self.lan == 0:
                                warn_msg(self, "The Nifti File does not contain proper Image.")
                            elif self.lan == 1:
                                warn_msg(self, "NII图像存在问题")
                elif len(path_2) == 1:
                    self.temp.fname = [item.replace(".nii", "_cbf.nii") for item in path_1]
                    nii_ref = ni.load(path_2[0])
                    for path in path_1:
                        nii_dwi = ni.load(path)
                        if len(nii_ref.get_fdata().shape) >= 3:
                            nii_output.append(self.make_cbf(nii_dwi.get_fdata(), nii_ref.get_fdata(), nii_dwi))
                        else:
                            if self.lan == 0:
                                warn_msg(self, "The Nifti File does not contain proper Image.")
                            elif self.lan == 1:
                                warn_msg(self, "NII图像存在问题")
                else:
                    self.temp.fname = [item.replace(".nii", "_cbf.nii") for item in path_2]
                    for index in range(len(path_1)):
                        nii_dwi = ni.load(path_1[index])
                        nii_ref = ni.load(path_2[index])
                        if len(nii_ref.get_fdata().shape) >= 3:
                            nii_output.append(self.make_cbf(nii_dwi.get_fdata(), nii_ref.get_fdata(), nii_dwi))
                        else:
                            if self.lan == 0:
                                warn_msg(self, "The Nifti File does not contain proper Image.")
                            elif self.lan == 1:
                                warn_msg(self, "NII图像存在问题")
                self.temp.set_nii(nii_output)
            else:
                if self.lan == 0:
                    warn_msg(self, "Input Directory of PWI Images.")
                elif self.lan == 1:
                    warn_msg(self, "输入ASL差异像路径")

        elif path_1 != "" and path_2 != "":
            # 输入三个路径list时，认为是两次时间的ASL和一次PD
            if len(nii_lat) != len(nii_pre):
                if self.lan == 0:
                    warn_msg(self, "ASL series have different components after delay.")
                elif self.lan == 1:
                    warn_msg(self, "延迟前后ASL图像的数量不一致")
            elif len(nii_lat) != len(nii_ref):
                if self.lan == 0:
                    warn_msg(self, "DWI series and PD series have different components.")
                elif self.lan == 1:
                    warn_msg(self, "DWI与PD像数量不一致")
            else:
                self.temp.fname = [item.replace(".nii", "_cbf.nii") for item in path_3]
                for index in range(len(path_1)):
                    nii_lat = ni.load(path_1[index])
                    nii_pre = ni.load(path_2[index])
                    nii_ref = ni.load(path_3[index])
                    if len(nii_ref.get_data(shape)) >= 3:
                        nii_output.append(self.make_cbf(nii_lat.get_fdata() - nii_pre.get_fdata(), nii_ref.get_fdata(), nii_lat))
                    else:
                        if self.lan == 0:
                            warn_msg(self, "The Nifti File does not contain proper Image.")
                        elif self.lan == 1:
                            warn_msg(self, "NII图像存在问题")
                self.temp.set_nii(nii_output)


        else:
            if self.lan == 0:
                warn_msg(self, "Input Directory of ASL Images.")
            elif self.lan == 1:
                warn_msg(self, "输入ASL像路径")

        if self.temp.niilist != []:
            self.nii_display = nii2display(self.temp, self.temp.display_vol, self.temp.niilist[0].get_fdata(), self.temp.display_min, self.temp.display_max, self.temp.lan)
            self.temp.idx_fname = len(self.temp.fname) - 1
            self.temp.PrevFile()
            if self.cb_autosave.isChecked():
                for i in range(len(nii_output)):
                    ni.save(nii_output[i], self.temp.fname[i])
        self.close()

    def calcbf_dwi(self):
        if self.display_asl == 0:
            self.ratio = 100 * self.lamda * np.exp(self.PLD/self.T1_blood) / (2 * self.alpha * self.T1_blood * (1 - np.exp(-self.tau/self.T1_blood)))
        elif self.display_asl == 1:
            self.ratio = 100 * self.lamda * np.exp(self.TI/self.T1_blood) / (2 * self.alpha * self.TI_1)
        try:
            self.get_cbfrom_asl(self.path_dwi, self.path_ref, "")
        except FileNotFoundError:
            if self.lan == 0:
                warn_msg(self, "Ensure your directory is correct.")
            elif self.lan == 1:
                warn_msg(self, "文件路径错误")

    def calcbf_asl(self):
        if self.display_asl == 0:
            self.ratio = 100 * self.lamda * np.exp(self.PLD/self.T1_blood) / (2 * self.alpha * self.T1_blood * (1 - np.exp(-self.tau/self.T1_blood)))
        elif self.display_asl == 1:
            self.ratio = 100 * self.lamda * np.exp(self.TI/self.T1_blood) / (2 * self.alpha * self.TI_1)
        try:
            self.get_cbfrom_asl(self.path_lat, self.path_pre, self.path_ref)
        except FileNotFoundError:
            if self.lan == 0:
                warn_msg(self, "Ensure your directory is correct.")
            elif self.lan == 1:
                warn_msg(self, "文件路径错误")

    def calcbf_simple(self):
        if self.display_asl == 0:
            self.ratio = 100 * self.lamda * np.exp(self.PLD/self.T1_blood) / (2 * self.alpha * self.T1_blood * (1 - np.exp(-self.tau/self.T1_blood)))
        elif self.display_asl == 1:
            self.ratio = 100 * self.lamda * np.exp(self.TI/self.T1_blood) / (2 * self.alpha * self.TI_1)
        try:
            self.get_cbfrom_asl(self.path_single, "", "")
        except FileNotFoundError:
            if self.lan == 0:
                warn_msg(self, "Ensure your directory is correct.")
            elif self.lan == 1:
                warn_msg(self, "文件路径错误")


################################################################################

class ui_pve(QMainWindow):
    def __init__(self, parent, lan = 0):
        super(ui_pve, self).__init__(parent)
        self.temp = parent
        self.setGeometry(303,304,500,350) # 设置子窗口的尺寸
        self.setMinimumSize(200,130) # 设置子窗口的最小尺寸
        self.lan = lan
        self.initUI()
        self.path_cbf = ""
        self.path_gm = ""
        self.path_wm = ""
        self.path_csf = ""
        self.bul_autoreg = 1
        self.index_method = 0 # 0:PET校正，1:线性回归
        self.data_temp = []
        self.idx_file = 0
        self.bul_autosave = 1

    def initUI(self):
        self.setWindowTitle("PVE")
        if self.lan == 0:
            self.label_name_cbf = QLabel("Directory of CBF:", self)
            self.label_name_gm = QLabel("Directory of GM:", self)
            self.label_name_wm = QLabel("Directory of WM:", self)
            self.label_name_csf = QLabel("Directory of CSF:", self)
            self.bt_ok = QPushButton("Operate", self)
            self.checkbox_autoreg = QCheckBox("Auto Coregister", self)
            self.checkbox_autoreg.setChecked(1)
            self.radio_pet = QRadioButton("PET's Correlation", self)
            self.radio_lr = QRadioButton("Linear Regression", self)
            self.radio_pet.setChecked(1)
            self.gb_method = QGroupBox("Method:", self)
            self.checkbox_autosave = QCheckBox("Auto Save", self)
            self.checkbox_autosave.setChecked(1)
        elif self.lan == 1:
            self.label_name_cbf = QLabel("CBF文件路径:", self)
            self.label_name_gm = QLabel("灰质分割结果路径:", self)
            self.label_name_wm = QLabel("白质分割结果路径:", self)
            self.label_name_csf = QLabel("脑脊液分割结果路径:", self)
            self.bt_ok = QPushButton("计算", self)
            self.checkbox_autoreg = QCheckBox("自动配准", self)
            self.checkbox_autoreg.setChecked(1)
            self.radio_pet = QRadioButton("传统PET校正", self)
            self.radio_pet.setChecked(1)
            self.radio_lr = QRadioButton("线性回归校正", self)
            self.gb_method = QGroupBox("校正方法:", self)
            self.checkbox_autosave = QCheckBox("自动保存", self)
            self.checkbox_autosave.setChecked(1)
        self.label_val_cbf = QLineEdit(self)
        self.label_val_gm = QLineEdit(self)
        self.label_val_wm = QLineEdit(self)
        self.label_val_csf = QLineEdit(self)
        self.bt_getcbf = QPushButton("...", self)
        self.bt_getcbf.setFixedWidth(30)
        self.bt_getgm = QPushButton("...", self)
        self.bt_getgm.setFixedWidth(30)
        self.bt_getwm = QPushButton("...", self)
        self.bt_getwm.setFixedWidth(30)
        self.bt_getcsf = QPushButton("...", self)
        self.bt_getcsf.setFixedWidth(30)
        self.bt_ok.setFixedWidth(65)
        self.bt_ok.clicked.connect(self.calc_pve)
        self.bt_getcbf.clicked.connect(self.get_cbf)
        self.bt_getgm.clicked.connect(self.get_gm)
        self.bt_getwm.clicked.connect(self.get_wm)
        self.bt_getcsf.clicked.connect(self.get_csf)
        self.checkbox_autoreg.stateChanged.connect(self.set_autoreg)
        self.checkbox_autosave.stateChanged.connect(self.set_autosave)

        self.radiobox = QVBoxLayout()
        self.radiobox.addWidget(self.radio_pet)
        self.radiobox.addWidget(self.radio_lr)
        self.radiobox.addStretch(1)
        self.gb_method.setLayout(self.radiobox)
        self.radio_pet.clicked.connect(self.switch_method)
        self.radio_lr.clicked.connect(self.switch_method)

        self.grid_label = QGridLayout()
        self.grid_upper = QGridLayout()
        self.grid_all = QGridLayout()

        self.grid_label.addWidget(self.label_name_cbf, 0, 0)
        self.grid_label.addWidget(self.label_val_cbf, 0, 1)
        self.grid_label.addWidget(self.bt_getcbf, 0, 2)
        self.grid_label.addWidget(self.label_name_gm, 1, 0)
        self.grid_label.addWidget(self.label_val_gm, 1, 1)
        self.grid_label.addWidget(self.bt_getgm, 1, 2)
        self.grid_label.addWidget(self.label_name_wm, 2, 0)
        self.grid_label.addWidget(self.label_val_wm, 2, 1)
        self.grid_label.addWidget(self.bt_getwm, 2, 2)
        self.grid_label.addWidget(self.label_name_csf, 3, 0)
        self.grid_label.addWidget(self.label_val_csf, 3, 1)
        self.grid_label.addWidget(self.bt_getcsf, 3, 2)
        self.grid_label.addWidget(self.checkbox_autoreg, 4, 0)
        self.grid_label.addWidget(self.checkbox_autosave, 5, 0)

        self.grid_upper.addWidget(self.gb_method, 0, 0)
        self.grid_upper.addLayout(self.grid_label, 0, 1)

        self.grid_all.addLayout(self.grid_upper, 0, 0)
        self.grid_all.addWidget(self.bt_ok, 1, 0)
        self.grid_all.setGeometry(QRect(50, 50, 400, 250))
        self.grid_all.setAlignment(Qt.AlignCenter)

        self.resizeEvent = self.adjustSize

    def switch_method(self):
        if self.radio_pet.isChecked() == True:
            self.index_method = 0
        elif self.radio_lr.isChecked() == True:
            self.index_method = 1


    def calc_pve(self):
        if self.bt_ok.text() == ("Operate" or "计算"):
            try:
                if self.lan == 0:
                    self.bt_ok.setText("Cancel")
                elif self.lan == 1:
                    self.bt_ok.setText("取消")
                if self.index_method == 0:
                    for idx in range(len(self.path_cbf)):
                        nii_cbf = ni.load(self.path_cbf[idx])
                        nii_gm = ni.load(self.path_gm[idx])
                        nii_wm = ni.load(self.path_wm[idx])
                        if nii_cbf.shape != nii_gm.shape:
                            if self.bul_autoreg == 1:
                                # 预留将结构像与CBF自动配准的功能,用resample代替
                                nii_cbf = resample_to_img(nii_cbf, nii_gm)
                            else:
                                if self.lan == 0:
                                    warn_msg(self, "Shape of CBF and T1 are different.")
                                elif self.lan == 1:
                                    warn_msg(self, "CBF与结构像大小不一致")
                                continue
                        data_cbf = nii_cbf.get_fdata()
                        data_gm = nii_gm.get_fdata()
                        data_wm = nii_wm.get_fdata()

                        data_temp =  (data_cbf * ((data_gm + data_wm) > 0.1)) / (((data_gm) + 0.4 * (data_wm)) * ((data_gm + 0.4 * data_wm) > 0.1))

                        data_temp[np.isnan(data_temp)] = 0
                        data_temp[np.isinf(data_temp)] = 0
                        self.data_temp.append(ni.Nifti1Image(data_temp, nii_gm.affine, nii_gm.header))

                    self.temp.set_nii(self.data_temp)
                    if self.lan == 0:
                        self.bt_ok.setText("Operate")
                    elif self.lan == 1:
                        self.bt_ok.setText("计算")
                    self.temp.fname = [item.replace(".nii", "_pve.nii") for item in self.path_cbf]
                    if self.checkbox_autosave == 1:
                        ni.save(ni.Nifti1Image(data_temp, nii_gm.affine, nii_gm.header), item.replace(".nii", "_pve.nii"))

                    self.close()
                elif self.index_method == 1:
                    data_temp = 0
                    self.lr_thread = LRThread(self, self.lan)
                    self.lr_thread.start()
                    self.lr_thread.progress.connect(self.update_progress)
                    self.lr_thread.trigger.connect(self.get_data_thread)
                    self.lr_thread.file.connect(self.get_data_each)
                else:
                    pass # 预留其他方法

            except FileNotFoundError:
                if self.lan == 0:
                    warn_msg(self, "File not existed.")
                elif self.lan == 1:
                    warn_msg(self, "选择的文件不存在")
            except ni.filebasedimages.ImageFileError:
                if self.lan == 0:
                    warn_msg(self, "Selected file is not an nii file.")
                elif self.lan == 1:
                    warn_msg(self, "选择的文件格式错误")
        elif self.bt_ok.text() == ("Cancel" or "取消"):
            self.lr_thread.stop()
            self.lr_thread.quit()
            self.lr_thread.wait()
            del self.lr_thread
            if self.lan == 0:
                self.bt_ok.setText("Operate")
            elif self.lan == 1:
                self.bt_ok.setText("计算")



    def update_progress(self, float_progress):
        if self.lan == 0:
            self.statusBar().showMessage("Working: " + str(float_progress) + "%, File: " + str(self.idx_file + 1) + "/" + str(len(self.path_cbf)))
        elif self.lan == 1:
            self.statusBar().showMessage("正忙: " + str(float_progress) + "%, 文件: " + str(self.idx_file + 1) + "/" + str(len(self.path_cbf)))

    def get_data_each(self, int_file):
        self.idx_file = int_file
        data_temp = self.lr_thread.data_result
        self.data_temp.append(ni.Nifti1Image(data_temp, ni.load(self.path_cbf[self.idx_file]).affine, ni.load(self.path_cbf[self.idx_file]).header))

    def get_data_thread(self):
        self.temp.fname = [item.replace(".nii", "_pve.nii") for item in self.path_cbf]
        if self.lan == 0:
            warn_msg(self, str(time.localtime().tm_hour) + ":" + str(time.localtime().tm_min) + ":" + str(time.localtime().tm_sec) + " Done!", 1)
        elif self.lan == 1:
            warn_msg(self, str(time.localtime().tm_hour) + ":" + str(time.localtime().tm_min) + ":" + str(time.localtime().tm_sec) + "计算完成", 1)
        self.temp.set_nii(self.data_temp)
        self.temp.idx_fname = len(self.temp.fname) - 1
        self.temp.PrevFile()
        if self.lan == 0:
            self.bt_ok.setText("Operate")
        elif self.lan == 1:
            self.bt_ok.setText("计算")
        if self.bul_autosave == 1:
            for i in range(len(self.data_temp)):
                ni.save(self.data_temp[i], self.temp.fname[i])
        self.lr_thread.deleteLater()
        self.close()

    def get_cbf(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]

        self.label_val_cbf.setText(str(self.path_cbf))

    def get_gm(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_gm = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_gm = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_gm = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_gm = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_gm = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_gm = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.label_val_gm.setText(str(self.path_gm))

    def get_wm(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_wm = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_wm = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_wm = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_wm = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_wm = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_wm = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.label_val_wm.setText(str(self.path_wm))

    def get_csf(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_csf = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_csf = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_csf = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_csf = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_csf = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_csf = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.label_val_csf.setText(str(self.path_csf))

    def set_autoreg(self, int):
        if self.checkbox_autoreg.isChecked():
            self.bul_autoreg = 1
        else:
            self.bul_autoreg = 0

    def set_autosave(self, int):
        if self.checkbox_autosave.isChecked():
            self.bul_autosave = 1
        else:
            self.bul_autosave = 0

    def adjustSize(self, event):
        self.grid_all.setGeometry(QRect(50, 50, (self.width() - 100), (self.height() - 100))) # 将组件全部显示后调整尺寸

    def closeEvent(self, event):
        try:
            if self.lr_thread.isRunning():
                self.lr_thread.quit()
                del self.lr_thread
        except NameError:
            pass
        except AttributeError:
            pass
        super(ui_pve, self).closeEvent(event)
