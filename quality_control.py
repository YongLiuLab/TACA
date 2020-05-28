#coding=utf-8

import nibabel as ni
import numpy as np
import os,sys, platform
import scipy.io as scio
from PyQt5.QtWidgets import QButtonGroup, QRadioButton, QPushButton, QCheckBox, QFileDialog, QMainWindow, QLabel, QLineEdit, QGridLayout, QApplication, QAction, qApp, QToolTip, QSpinBox, QComboBox
from PyQt5.QtCore import QCoreApplication, pyqtSignal, QRect, QThread
import subprocess
import scipy.stats as scst
from skimage import filters, morphology

################################################################################

class MaskThread(QThread):
    trigger = pyqtSignal()
    result = pyqtSignal(np.ndarray)
    def __init__(self, parent, path_wb, lan = 0):
        super(MaskThread, self).__init__(parent)
        self.temp = parent
        self.lan = lan

    def __del__(self):
        self.wait()

    def run(self):
        nii = ni.load(path_wb).get_fdata()
        threshold = filters.threshold_otsu(nii)
        temp_mask = nii >= threshold
        times = 5
        for i in range(times):
            temp_mask = morphology.dilation(temp_mask, selem=None, out=None, shift_x=False, shift_y=False)
        temp_mask = morphology.remove_small_holes(temp_mask, area_threshold = 20000, connectivity = 1)
        for j in range(times):
            temp_mask = morphology.erosion(temp_mask, selem=None, out=None, shift_x=False, shift_y=False)
        self.result.emit(temp_mask)
        self.trigger.emit()


################################################################################

class RegThread(QThread):
    trigger = pyqtSignal()
    process = pyqtSignal(int)
    file = pyqtSignal(list)
    def __init__(self, parent, lan = 0):
        super(RegThread, self).__init__(parent)
        self.temp = parent
        self.lan = lan

    def __del__(self):
        self.wait()

    def run(self):
        path_file = []
        if "/" in self.temp.path_local:
            path_bin = self.temp.path_local.replace(self.temp.path_local.split('/')[-1], "Utils/reg_aladin.exe")
            path_tem = self.temp.path_local.replace(self.temp.path_local.split('/')[-1], 'Utils/Template_4_IXI555_MNI152_GS.nii')

        elif '\\' in self.temp.path_local:
            path_bin = self.temp.path_local.replace(self.temp.path_local.split('\\')[-1], "Utils\\reg_aladin.exe")
            path_tem = self.temp.path_local.replace(self.temp.path_local.split('\\')[-1], 'Utils\\Template_4_IXI555_MNI152_GS.nii')

        for i in range(len(self.temp.path_cbf)):
            if ".gz" in self.temp.path_cbf[i]:
                path_aff = self.temp.path_cbf[i].replace(".nii.gz", "_affine.txt")
            elif ".nii" in self.temp.path_cbf[i]:
                path_aff = self.temp.path_cbf[i].replace(".nii", "_affine.txt")
            path_save = self.temp.path_cbf[i].replace(".nii", "_seg.nii")
            task = subprocess.Popen('%s -ref %s -flo %s -aff %s -res %s' %  (path_bin,self.temp.path_cbf[i],path_tem,path_aff,path_save), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            msg = ""
            for line in task.stdout.readlines():
                msg += line.decode("gb2312")
            status = task.wait()
            print(msg)
            self.process.emit(i + 1)
            path_file.append(path_save)

        self.file.emit(path_file)
        self.trigger.emit()

################################################################################

class Qualityratio(object):
    def __init__(data_cbf, data_gm, data_wm, data_noise, threshold = 0.2):
        # data应为np.narray的格式
        # threshold为将分割结果识别为灰质/白质的阈值
        try:
            if data_cbf.shape != data_gm.shape:
                print("Warning: data_cbf and data_gm should have same size.")
            self.data_cbf = data_cbf
            self.data_gm = data_gm
            self.data_wm = data_wm
            self.data_noise = data_noise
            self.threshold = threshold
            self.calculation()
        except AttributeError:
            print("Error: Input should be a numpy array.")

    def snr(self, input_type = 0, method_type = 0):
        # input_type 用于辨识需要使用哪个数据作为信号,0:全脑,1:灰质,2:白质
        # method_type 用于辨识使用哪种信噪比定义,0:噪声均值,1:噪声标准差,2:信号标准差/噪声标准差
        if input_type == 0:
            signal = self.data_cbf
        elif input_type == 1:
            signal = self.data_gm
        elif input_type == 2:
            signal = self.data_wm
        else:
            print("Warning: input_type should in range 0 to 2, set it to 0.")
            signal = self.data_cbf
            input_type = 0
        if method_type == 0:
            snr = np.average(signal[signal.nonzero()]) / np.average(self.data_noise[self.data_noise.nonzero()])
        elif method_type == 1:
            snr = np.average(signal[signal.nonzero()]) / np.std(self.data_noise[self.data_noise.nonzero()])
        elif method_type == 2:
            snr = np.std(signal[signal.nonzero()]) / np.std(self.data_noise[self.data_noise.nonzero()])
        return snr

    def cnr(self, method_type = 0):
        # method_type 用于辨识使用哪种定义,0:噪声均值,1:噪声标准差
        gm = self.data_gm * (self.data_gm > self.threshold) * (self.data_gm > self.data_wm)
        wm = self.data_wm * (self.data_wm > self.threshold) * (self.data_wm > self.data_gm)
        cnr = abs(np.average(gm[gm.nonzero()]) - np.average(wm[wm.nonzero()]))
        if method_type == 0:
            cnr /= np.average(self.data_noise[self.data_noise.nonzero()])
        elif method_type == 1:
            cnr /= np.std(self.data_noise[self.data_noise.nonzero()])
        return cnr

    def fber(self, input_type = 0):
        snr = self.snr(input_type, 2)
        return snr*snr

    def cjv(self):
        gm = self.data_gm * (self.data_gm > self.threshold) * (self.data_gm > self.data_wm)
        wm = self.data_wm * (self.data_wm > self.threshold) * (self.data_wm > self.data_gm)
        gm = gm[gm.nonzero()]
        wm = wm[wm.nonzero()]
        cjv = (np.std(gm) + np.std(wm)) / abs(np.average(gm) - np.average(wm))
        return cjv

    def efc(self):
        signal = self.data_cbf
        signal_max = np.max(signal)
        signal /= signal_max
        efc = scst.entropy(signal[signal.nonzero()])
        return efc

    def wm2max(self):
        signal = self.data_cbf[self.data_cbf.nonzero()]
        wm = self.data_wm *(self.data_wm > self.threshold) * (self.data_wm > self.data_gm)
        max = np.percentile(signal,[95])
        median = np.median(wm[wm.nonzero()])
        return (median / max)

################################################################################

class window_qc(QMainWindow):
    def __init__(self, parent, lan = 0):
        super(window_qc, self).__init__(parent)
        self.temp = parent
        self.setGeometry(303,304,500,350) # 设置子窗口的尺寸
        self.setMinimumSize(200,130) # 设置子窗口的最小尺寸
        self.lan = lan
        self.path_cbf = ""
        self.path_gm = ""
        self.path_wm = ""
        self.path_noise = ""
        self.path_local = os.path.realpath(__file__)

        self.initUI()

    def initUI(self):
        if self.lan == 0:
            self.label_dir = QLabel("Directory:", self)
            self.label_cbf = QLabel("Whole Brain", self)
            self.label_gm = QLabel("Gray Matter(Optional)", self)
            self.label_wm = QLabel("White Matter(Optional)", self)
            self.label_noise = QLabel("Noise(Optional)", self)
            self.label_mode = QLabel("Mode:", self)
            self.rb_mode_quick = QRadioButton("Quick", self)
            self.rb_mode_detail = QRadioButton("Detail", self)
            # self.label_snr = QLabel("SNR:", self)
            # self.cb_snr_full = QCheckBox("Whole Image", self)
            # self.cb_snr_gm = QCheckBox("Grey Matter", self)
            # self.cb_snr_wm = QCheckBox("White Matter", self)
            # self.cb_cnr = QCheckBox("CNR", self)
            # self.cb_fber = QCheckBox("FBER", self)
            # self.cb_cjv = QCheckBox("CJV", self)
            # self.cb_efc = QCheckBox("EFC", self)
            # self.cb_wm2max = QCheckBox("WM/Max", self)
        elif self.lan == 1:
            self.label_dir = QLabel("路径:", self)
            self.label_cbf = QLabel("全脑", self)
            self.label_gm = QLabel("灰质(可选)", self)
            self.label_wm = QLabel("白质(可选)", self)
            self.label_noise = QLabel("噪声(可选)", self)
            self.label_mode = QLabel("模式:", self)
            self.rb_mode_quick = QRadioButton("快速", self)
            self.rb_mode_detail = QRadioButton("全面", self)
            # self.label_snr = QLabel("信噪比:", self)
            # self.cb_snr_full = QCheckBox("完整图像", self)
            # self.cb_snr_gm = QCheckBox("灰质", self)
            # self.cb_snr_wm = QCheckBox("白质", self)
            # self.cb_cnr = QCheckBox("对比噪声比", self)
            # self.cb_fber = QCheckBox("频带能量比", self)
            # self.cb_cjv = QCheckBox("联合变异系数", self)
            # self.cb_efc = QCheckBox("熵集聚系数", self)
            # self.cb_wm2max = QCheckBox("白质/最大值比", self)
        self.value_dir_cbf = QLineEdit(self)
        self.value_dir_gm = QLineEdit(self)
        self.value_dir_wm = QLineEdit(self)
        self.bt_dir_cbf = QPushButton("...", self)
        self.bt_dir_gm = QPushButton("...", self)
        self.bt_dir_wm = QPushButton("...", self)
        self.bt_operate = QPushButton("OK", self)

        self.group_mode = QButtonGroup(self)
        self.group_mode.addButton(self.rb_mode_quick, 1)
        self.group_mode.addButton(self.rb_mode_detail, 2)

        self.grid_full = QGridLayout()
        self.grid_dir = QGridLayout()
        self.grid_opt = QGridLayout()
        self.rb_mode_detail.setChecked(True)

        self.grid_opt.addWidget(self.label_mode, 0, 0)
        self.grid_opt.addWidget(self.rb_mode_quick, 1, 0)
        self.grid_opt.addWidget(self.rb_mode_detail, 1, 1)

        self.grid_dir.addWidget(self.label_dir, 0, 0)
        self.grid_dir.addWidget(self.label_cbf, 0, 1)
        self.grid_dir.addWidget(self.value_dir_cbf, 0, 2)
        self.grid_dir.addWidget(self.bt_dir_cbf, 0, 3)
        self.grid_dir.addWidget(self.label_gm, 1, 1)
        self.grid_dir.addWidget(self.value_dir_gm, 1, 2)
        self.grid_dir.addWidget(self.bt_dir_gm, 1, 3)
        self.grid_dir.addWidget(self.label_wm, 2, 1)
        self.grid_dir.addWidget(self.value_dir_wm ,2, 2)
        self.grid_dir.addWidget(self.bt_dir_wm, 2, 3)

        self.grid_full.addLayout(self.grid_dir, 0, 0)
        self.grid_full.addLayout(self.grid_opt, 1, 0)
        self.grid_full.addWidget(self.bt_operate, 2, 0)


        self.resizeEvent = self.adjustSize

        self.bt_dir_cbf.clicked.connect(self.select_dir_cbf)
        self.bt_dir_gm.clicked.connect(self.select_dir_gm)
        self.bt_dir_wm.clicked.connect(self.select_dir_wm)
        self.bt_operate.clicked.connect(self.pipeline)

    def adjustSize(self, event):
        self.grid_full.setGeometry(QRect(50, 50, (self.width() - 100), (self.height() - 100)))

    def select_dir_cbf(self):
        if self.lan == 0:
            if platform.system == "Windows":
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system == "Linux":
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_cbf = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system == "Windows":
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system == "Linux":
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_cbf = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        if self.path_cbf == []:
            self.path_cbf = ""
        self.value_dir_cbf.setText(str(self.path_cbf))

    def select_dir_gm(self):
        if self.lan == 0:
            if platform.system == "Windows":
                self.path_gm = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system == "Linux":
                self.path_gm = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_gm = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system == "Windows":
                self.path_gm = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system == "Linux":
                self.path_gm = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_gm = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        if self.path_gm == []:
            self.path_gm = ""
        self.value_dir_gm.setText(str(self.path_gm))

    def select_dir_wm(self):
        if self.lan == 0:
            if platform.system == "Windows":
                self.path_wm = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system == "Linux":
                self.path_wm = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_wm = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system == "Windows":
                self.path_wm = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system == "Linux":
                self.path_wm = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_wm = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        if self.path_wm == []:
            self.path_wm = ""
        self.value_dir_wm.setText(str(self.path_wm))

    def select_dir_noise(self):
        if self.lan == 0:
            if platform.system == "Windows":
                self.path_noise = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system == "Linux":
                self.path_noise = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_noise = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system == "Windows":
                self.path_noise = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii文件(*.nii;*.nii.gz);;所有文件(*)")[0]
            elif platform.system == "Linux":
                self.path_noise = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_noise = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        if self.path_noise == []:
            self.path_noise = ""
        self.value_dir_noise.setText(str(self.path_noise))

    def reg_gw(self):
        self.thread_qc = RegThread(self, self.lan)
        self.thread_qc.start()
        if self.lan == 0:
            self.statusBar().showMessage("Working...")
        elif self.lan == 1:
            self.statusBar().showMessage("正忙...")
        self.thread_qc.process.connect(self.update_process)
        self.thread_qc.trigger.connect(self.definition)
        self.thread_qc.file.connect(self.updata_path)

    def definition(self):
        if self.path_noise == "":
            if self.path_cbf != "":
                for item in self.path_cbf:
                    self.thread_mask = MaskThread(self, item, self.lan)
                    self.thread_mask.result.connect(self.calculate)


    def calculate(self):
        self.qc = Qualityratio(data_wb, data_gm, data_wm, data_noise, threshold = 0.7)

    def update_process(self, int_process):
        if self.lan == 0:
            self.statusBar().showMessage("File: " + str(int_process) + "/" + str(len(self.path_cbf)))
        elif self.lan == 1:
            self.statusBar().showMessage("文件: " + str(int_process) + "/" + str(len(self.path_cbf)))

    def updata_path(self, list_path):
        self.path_gm = list_path

    def pipeline(self):
        if self.rb_mode_detail.isChecked():
            if self.path_gm == "" or self.path_wm == "":
                self.reg_gw()
                data_gm = [ni.load(item.replace(".nii", "_seg.nii")).get_fdata()[:,:,:,0] for item in self.path_gm]
                data_wm = [ni.load(item.replace(".nii", "_seg.nii")).get_fdata()[:,:,:,1] for item in self.path_wm]

            else:
                self.definition()
