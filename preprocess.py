# coding=UTF-8

import nibabel as ni
from PyQt5.QtCore import QCoreApplication, Qt, QThread, pyqtSignal, QRect
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QLineEdit, QRadioButton, QPushButton, QGridLayout, QFileDialog, QMessageBox, QCheckBox, QGroupBox, QVBoxLayout, QProgressBar

# from progress_pve import *
from display import *
import os, platform
import subprocess

#################################################################################

class window_coreg(QMainWindow):
    def __init__(self, parent, lan = 0):
        super(window_coreg, self).__init__(parent)
        self.temp = parent
        self.setGeometry(303,304,500,350) # 设置子窗口的尺寸
        self.setMinimumSize(200,130) # 设置子窗口的最小尺寸
        self.lan = lan
        self.method = "NiftyReg"
        self.path_input = ""
        self.path_ref = ""
        self.path_pd = ""
        self.idx_file = 0
        self.initUI()

    def initUI(self):
        if self.lan == 0:
            self.setWindowTitle("Coregister")
            self.label_input = QLabel("Directory of Input Image:", self)
            self.label_reference = QLabel("Directory of Reference Image:", self)
            self.label_highres = QLabel("Directory of PD Image(Optional):", self)
            self.button_operate = QPushButton("Operate", self)
            self.label_method = QLabel("Method", self)
        elif self.lan == 1:
            self.setWindowTitle("配准")
            self.label_input = QLabel("待配准图像路径:", self)
            self.label_reference = QLabel("参考模板图像路径:", self)
            self.label_highres = QLabel("对应PD像路径(可选):", self)
            self.button_operate = QPushButton("开始计算", self)
            self.label_method = QLabel("配准方法", self)

        self.combox_t = QComboBox(self)
        self.le_input = QLineEdit(self)
        self.le_reference = QLineEdit(self)
        self.le_highres = QLineEdit(self)
        self.button_input = QPushButton("...", self)
        self.button_reference = QPushButton("...", self)
        self.button_highres = QPushButton("...", self)

        self.grid_full = QGridLayout()
        self.grid_checkbox = QGridLayout()
        self.grid_input = QGridLayout()
        self.grid_ref = QGridLayout()
        self.grid_pd = QGridLayout()
        self.grid_button = QGridLayout()

        self.grid_checkbox.addWidget(self.label_method, 0, 0)
        self.grid_checkbox.addWidget(self.combox_t, 0, 1)

        self.grid_input.addWidget(self.label_input, 0, 0)
        self.grid_input.addWidget(self.le_input, 0, 1)
        self.grid_input.addWidget(self.button_input, 0, 2)

        self.grid_ref.addWidget(self.label_reference, 0, 0)
        self.grid_ref.addWidget(self.le_reference, 0, 1)
        self.grid_ref.addWidget(self.button_reference, 0, 2)

        self.grid_pd.addWidget(self.label_highres, 0, 0)
        self.grid_pd.addWidget(self.le_highres, 0, 1)
        self.grid_pd.addWidget(self.button_highres, 0, 2)

        self.grid_button.addWidget(self.button_operate, 0, 0)

        self.grid_full.addLayout(self.grid_input, 0, 0)
        self.grid_full.addLayout(self.grid_ref, 1, 0)
        self.grid_full.addLayout(self.grid_pd, 2, 0)
        self.grid_full.addLayout(self.grid_checkbox, 3, 0)
        self.grid_full.addLayout(self.grid_button, 4, 0)

        self.grid_full.setGeometry(QRect(50, 50, 400, 250))
        self.grid_full.setAlignment(Qt.AlignCenter)

        self.resizeEvent = self.adjustSize


        method = ['NiftyReg', 'SPM', 'Flirt', 'Fnirt']

        self.combox_t.addItems(method)

        self.combox_t.activated.connect(self.switch_method)
        self.button_operate.clicked.connect(self.operate)
        self.button_input.clicked.connect(self.select_dir_input)
        self.button_reference.clicked.connect(self.select_dir_ref)
        self.button_highres.clicked.connect(self.select_dir_pd)

    def adjustSize(self, event):
        self.grid_full.setGeometry(QRect(50, 50, (self.width() - 100), (self.height() - 100))) # 将组件全部显示后调整尺寸

    def switch_method(self, text):
        self.method = text

    def select_dir_input(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_input = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_input = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_input = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_input = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_input = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_input = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.le_input.setText(str(self.path_input))

    def select_dir_ref(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_ref = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_ref = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_ref = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_refpath_ref = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_ref = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_ref = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.le_reference.setText(str(self.path_ref))

    def select_dir_pd(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_pd = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_pd = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_pd = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_refpath_ref = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_pd = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_pd = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        if self.path_pd == []:
            self.path_pd = ""
        self.le_highres.setText(str(self.path_pd))

    def operate(self):
        # self.path_ref = self.le_reference.text()
        # self.path_input = self.le_input.text()
        print(self.method)
        if self.method == "NiftyReg":
            print("NiftiReg Start:")
            self.start_niftyreg()
        elif self.method == "Flirt":
            self.start_flirt()
        elif self.method == "Fnirt":
            self.start_fnirt()

    def start_niftyreg(self):
        self.thread_aladin = AladinThread(self, self.lan)
        self.thread_aladin.start()
        self.thread_aladin.iteration.connect(self.get_num_file)
        self.thread_aladin.progress.connect(self.update_status)
        self.thread_aladin.trigger.connect(self.niftyreg_second_step)

    def niftyreg_second_step(self):
        self.thread_affine = UseAffineThread(self, self.lan)
        self.thread_affine.start()
        self.thread_affine.iteration.connect(self.get_num_file)
        self.thread_affine.progress.connect(self.update_status)
        self.thread_affine.trigger.connect(self.niftyreg_done)

    def niftyreg_done(self):
        print("done")

    def start_flirt(self):
        self.statusBar().showMessage("Working...Using Flirt")
        self.thread_flirt = FlirtThread(self, self.lan)
        self.thread_flirt.start()
        self.thread_flirt.iteration.connect(self.get_num_file)
        self.thread_flirt.progress.connect(self.update_status)

    def start_fnirt(self):
        pass

    def get_num_file(self, int_iteration):
        self.idx_file = int_iteration

    def update_status(self, float_progress):
        if self.lan == 0:
            self.statusBar().showMessage("Working: " + str(float_progress) + "%, File: " + str(self.idx_file) + "/" + str(len(self.path_input)))
        elif self.lan == 1:
            self.statusBar().showMessage("正忙: " + str(float_progress) + "%, 文件: " + str(self.idx_file) + "/" + str(len(self.path_input)))

class FlirtThread(QThread):
    progress = pyqtSignal(float)
    iteration = pyqtSignal(int)
    trigger = pyqtSignal()
    def __init__(self, parent, lan = 0):
        super(FlirtThread, self).__init__(parent)
        self.temp = parent
        self.lan = lan
        self.path_ref = self.temp.path_ref
        self.path_input = self.temp.path_input
        self.path_pd = self.temp.path_pd
        # self.path_local = os.path.realpath(__file__)

    def __del__(self):
        self.wait()

    def run(self):
        try:
            if (len(self.path_ref) != len(self.path_input)) and (len(self.path_ref) != 1):
                if self.lan == 0:
                    warn_msg(self.temp, "Number of Input Image and Reference Image Should be the Same.")
                elif self.lan == 1:
                    warn_msg(self.temp, "输入图像与参考图像数量应该一致")
            elif len(self.path_ref) == 1:
                for i in range(len(self.path_input)):
                    if " " in self.path_input[i]:
                        self.path_input[i] = '"%s" "%s"' % (self.path_input[i], "-h")
                    # nii_input = ni.load(path)
                    if ".gz" in self.path_input[i]:
                        path_aff = self.path_input[i].replace(".nii.gz", "_affine.mat")
                        path_temppd = self.path_input[i].replace(".nii.gz", "_pd.nii")
                        path_save = self.path_input[i].replace(".nii.gz", "_coreg.nii")
                    elif ".nii" in self.path_input[i]:
                        path_aff = self.path_input[i].replace(".nii", "_affine.mat")
                        path_temppd = self.path_input[i].replace(".nii", "_pd.nii")
                        path_save = self.path_input[i].replace(".nii", "_coreg.nii")

                    print('flirt -in %s -ref %s -out %s -omat %s -interp trilinear' %  (self.path_input[i],self.path_ref[0],path_save,path_aff))

                    task = subprocess.Popen('flirt -in %s -ref %s -out %s -omat %s -interp trilinear' %  (self.path_input[i],self.path_ref[0],path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    msg = ""
                    for line in task.stdout.readlines():
                        msg += line.decode("gb2312")
                    status = task.wait()
                    print(msg)
                    task = subprocess.Popen('flirt -in %s -ref %s -out %s -applyxfm -init %s -interp trilinear' % (self.path_input[i],self.path_ref[0],path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    percent_progress = float(i + 1) / float(len(self.path_input)) * 100
                    self.iteration.emit(i + 1)
                    self.progress.emit(percent_progress)
                self.trigger.emit()
            else:
                for i in range(len(self.path_input)):
                    if " " in self.path_input[i]:
                        self.path_input[i] = '"%s" "%s"' % (self.path_input[i], "-h")
                    # nii_input = ni.load(path)
                    if ".gz" in self.path_input[i]:
                        path_aff = self.path_input[i].replace(".nii.gz", "_affine.mat")
                        path_temppd = self.path_input[i].replace(".nii.gz", "_pd.nii")
                        path_save = self.path_input[i].replace(".nii.gz", "_coreg.nii")
                    elif ".nii" in self.path_input[i]:
                        path_aff = self.path_input[i].replace(".nii", "_affine.mat")
                        path_temppd = self.path_input[i].replace(".nii", "_pd.nii")
                        path_save = self.path_input[i].replace(".nii", "_coreg.nii")

                    print('flirt -in %s -ref %s -out %s -omat %s -interp trilinear' %  (self.path_input[i],self.path_ref[i],path_save,path_aff))

                    task = subprocess.Popen('flirt -in %s -ref %s -out %s -omat %s -interp trilinear' %  (self.path_input[i],self.path_ref[i],path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    msg = ""
                    for line in task.stdout.readlines():
                        msg += line.decode("gb2312")
                    status = task.wait()
                    print(msg)
                    task = subprocess.Popen('flirt -in %s -ref %s -out %s -applyxfm -init %s -interp trilinear' % (self.path_input[i],self.path_ref[i],path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    percent_progress = float(i + 1) / float(len(self.path_input)) * 100
                    self.iteration.emit(i + 1)
                    self.progress.emit(percent_progress)
                self.trigger.emit()

        except FileNotFoundError:
            if self.lan == 0:
                warn_msg(self.temp, "You Need to Install FSL to Use This Function.")
            elif self.lan == 1:
                warn_msg(self.temp, "需要安装FSL")

class UseAffineThread(QThread):
    progress = pyqtSignal(float)
    iteration = pyqtSignal(int)
    trigger = pyqtSignal()
    def __init__(self, parent, lan = 0):
        super(UseAffineThread, self).__init__(parent)
        self.temp = parent
        self.lan = lan
        self.path_ref = self.temp.path_ref
        self.path_input = self.temp.path_input
        self.path_pd = self.temp.path_pd
        self.path_local = os.path.realpath(__file__)

    def __del__(self):
        self.wait()

    def run(self):
        if " " in self.path_local:
            path_bin = '"%s" "%s"' % (path_bin, "-h")
        if "/" in self.path_local:
            path_bin = self.path_local.replace(self.path_local.split('/')[-1], "Utils/reg_resample.exe")

        elif '\\' in self.path_local:
            path_bin = self.path_local.replace(self.path_local.split('\\')[-1], "Utils\\reg_resample.exe")

        if (len(self.path_ref) != len(self.path_input)) and (len(self.path_ref) != 1):
            if self.lan == 0:
                warn_msg(self.temp, "Number of Input Image and Reference Image Should be the Same.")
            elif self.lan == 1:
                warn_msg(self.temp, "输入图像与参考图像数量应该一致")
        elif len(self.path_ref) == 1:
            # nii_ref = ni.load(self.path_ref[0])
            for i in range(len(self.path_input)):
                if " " in self.path_input[i]:
                    self.path_input[i] = '"%s" "%s"' % (self.path_input[i], "-h")
                # nii_input = ni.load(path)
                if ".gz" in self.path_input[i]:
                    path_aff = self.path_input[i].replace(".nii.gz", "_affine.txt")
                    path_temppd = self.path_input[i].replace(".nii.gz", "_pd.nii")
                    path_save = self.path_input[i].replace(".nii.gz", "_coreg.nii")
                elif ".nii" in self.path_input[i]:
                    path_aff = self.path_input[i].replace(".nii", "_affine.txt")
                    path_temppd = self.path_input[i].replace(".nii", "_pd.nii")
                    path_save = self.path_input[i].replace(".nii", "_coreg.nii")

                task = subprocess.Popen('%s -ref %s -flo %s -res %s -trans %s' %  (path_bin,self.path_ref[0],self.path_input[i],path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                msg = ""
                for line in task.stdout.readlines():
                    msg += line.decode("gb2312")
                status = task.wait()
                print(msg)
                percent_progress = float(i + 1) / float(len(self.path_input)) * 100
                self.iteration.emit(i + 1)
                self.progress.emit(percent_progress)
            self.trigger.emit()

        else:
            for i in range(len(self.path_input)):
                if " " in self.path_input[i]:
                    self.path_input[i] = '"%s" "%s"' % (self.path_input[i], "-h")
                # nii_input = ni.load(path)
                if ".gz" in self.path_input[i]:
                    path_aff = self.path_input[i].replace(".nii.gz", "_affine.txt")
                    path_temppd = self.path_input[i].replace(".nii.gz", "_pd.nii")
                    path_save = self.path_input[i].replace(".nii.gz", "_coreg.nii")
                elif ".nii" in self.path_input[i]:
                    path_aff = self.path_input[i].replace(".nii", "_affine.txt")
                    path_temppd = self.path_input[i].replace(".nii", "_pd.nii")
                    path_save = self.path_input[i].replace(".nii", "_coreg.nii")

                task = subprocess.Popen('%s -ref %s -flo %s -res %s -trans %s' %  (path_bin,self.path_ref[i],self.path_input[i],path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                msg = ""
                for line in task.stdout.readlines():
                    msg += line.decode("gb2312")
                status = task.wait()
                print(msg)
                percent_progress = float(i + 1) / float(len(self.path_input)) * 100
                self.iteration.emit(i + 1)
                self.progress.emit(percent_progress)
            self.trigger.emit()


class AladinThread(QThread):
    progress = pyqtSignal(float)
    iteration = pyqtSignal(int)
    trigger = pyqtSignal()
    def __init__(self, parent, lan = 0):
        super(AladinThread, self).__init__(parent)
        self.temp = parent
        self.lan = lan
        self.path_ref = self.temp.path_ref
        self.path_input = self.temp.path_input
        self.path_pd = self.temp.path_pd
        self.path_local = os.path.realpath(__file__)

    def __del__(self):
        self.wait()

    def run(self):
        if_pd = 0
        if " " in self.path_local:
            path_bin = '"%s" "%s"' % (path_bin, "-h")
        if "/" in self.path_local:
            path_bin = self.path_local.replace(self.path_local.split('/')[-1], "Utils/reg_aladin.exe")

        elif '\\' in self.path_local:
            path_bin = self.path_local.replace(self.path_local.split('\\')[-1], "Utils\\reg_aladin.exe")

        if (len(self.path_ref) != len(self.path_input)) and (len(self.path_ref) != 1):
            if self.lan == 0:
                warn_msg(self.temp, "Number of Input Image and Reference Image Should be the Same.")
            elif self.lan == 1:
                warn_msg(self.temp, "输入图像与参考图像数量应该一致")
        elif len(self.path_ref) == 1:
            # nii_ref = ni.load(self.path_ref[0])
            for i in range(len(self.path_input)):
                if " " in self.path_input[i]:
                    self.path_input[i] = '"%s" "%s"' % (self.path_input[i], "-h")
                # nii_input = ni.load(path)
                if ".gz" in self.path_input[i]:
                    path_aff = self.path_input[i].replace(".nii.gz", "_affine.txt")
                    path_save = self.path_input[i].replace(".nii.gz", "_coreg.nii")
                elif ".nii" in self.path_input[i]:
                    path_aff = self.path_input[i].replace(".nii", "_affine.txt")
                    path_save = self.path_input[i].replace(".nii", "_coreg.nii")
                if self.path_pd == "":
                    task = subprocess.Popen('%s -ref %s -flo %s -res %s -aff %s' %  (path_bin,self.path_ref[0],self.path_input[i],path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                elif len(self.path_pd) != len(self.path_input):
                    if self.lan == 0:
                        warn_msg(self.temp, "Number of Input Image and PD Image Should be the Same.")
                    elif self.lan == 1:
                        warn_msg(self.temp, "输入图像与PD像数量应该一致")
                else:
                    if_pd = 1
                    task = subprocess.Popen('%s -ref %s -flo %s -res %s -aff %s' %  (path_bin,self.path_ref[0],self.path_pd[i],path_save.replace("_coreg.nii", "_pd.nii"),path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                msg = ""
                for line in task.stdout.readlines():
                    msg += line.decode("gb2312")
                status = task.wait()
                print(msg)
                percent_progress = float(i + 1) / float(len(self.path_input)) * 100
                self.iteration.emit(i + 1)
                self.progress.emit(percent_progress)
            if if_pd == 1:
                self.trigger.emit()

        else:
            for i in range(len(self.path_input)):
                if " " in self.path_input[i]:
                    self.path_input[i] = '"%s" "%s"' % (self.path_input[i], "-h")
                if ".gz" in self.path_input[i]:
                    path_aff = self.path_input[i].repalce(".nii.gz", "_affine.txt")
                    path_save = self.path_input[i].replace("nii.gz", "_coreg.nii")
                elif ".nii" in self.path_input[i]:
                    path_aff = self.path_input[i].replace(".nii", "_affine.txt")
                    path_save = self.path_input[i].replace(".nii", "_coreg.nii")
                if self.path_pd == "":
                    task = subprocess.Popen('%s -ref %s -flo %s -res %s -aff %s' %  (path_bin,self.path_ref[i],self.path_input[i],path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                elif len(self.path_pd) != len(self.path_input):
                    if self.lan == 0:
                        warn_msg(self.temp, "Number of Input Image and PD Image Should be the Same.")
                    elif self.lan == 1:
                        warn_msg(self.temp, "输入图像与PD像数量应该一致")
                else:
                    if_pd = 1
                    task = subprocess.Popen('%s -ref %s -flo %s -res %s -aff %s' %  (path_bin,self.path_ref[i],self.path_pd[i],path_save.replace("_coreg.nii", "_pd.nii"),path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                msg = ""
                for line in task.stdout.readlines():
                    msg += line.decode("gb2312")
                status = task.wait()
                print(msg)
                percent_progress = float(i + 1) / float(len(self.path_input)) * 100
                self.iteration.emit(i + 1)
                self.progress.emit(percent_progress)
            if if_pd == 1:
                self.trigger.emit()


################################################################################

class window_seg(QMainWindow):
    def __init__(self, parent, lan = 0):
        super(window_seg, self).__init__(parent)
        self.temp = parent
        self.setGeometry(303,304,500,350) # 设置子窗口的尺寸
        self.setMinimumSize(200,130) # 设置子窗口的最小尺寸
        self.lan = lan
        self.method = "NiftyReg"
        self.path_input = ""
        self.path_local = os.path.realpath(__file__)
        if " " in self.path_local:
            self.path_template = '"%s" "%s"' % (self.path_template, "-h")
        if "/" in self.path_local:
            self.path_template = self.path_local.replace(self.path_local.split('/')[-1], "Utils/Template_4_IXI555_MNI152_GS.nii")

        elif '\\' in self.path_local:
            self.path_template = self.path_local.replace(self.path_local.split('\\')[-1], "Utils\\Template_4_IXI555_MNI152_GS.nii")
        self.initUI()

    def initUI(self):
        if self.lan == 0:
            self.setWindowTitle("Segmentation")
            self.label_input = QLabel("Directory of Input Image:", self)
            self.label_template = QLabel("Directory of Template:", self)
            self.button_operate = QPushButton("Operate", self)
            self.label_method = QLabel("Method", self)
        elif self.lan == 1:
            self.setWindowTitle("分割")
            self.label_input = QLabel("待分割图像路径:", self)
            self.label_template = QLabel("分割模板路径:", self)
            self.button_operate = QPushButton("开始计算", self)
            self.label_method = QLabel("分割方法", self)

        self.combox_t = QComboBox(self)
        self.le_input = QLineEdit(self)
        self.le_template = QLineEdit(self)
        self.le_template.setText(str(self.path_template))
        self.button_input = QPushButton("...", self)
        self.button_template = QPushButton("...", self)

        self.grid_full = QGridLayout()
        self.grid_checkbox = QGridLayout()
        self.grid_input = QGridLayout()
        self.grid_template = QGridLayout()
        self.grid_button = QGridLayout()

        self.grid_checkbox.addWidget(self.label_method, 0, 0)
        self.grid_checkbox.addWidget(self.combox_t, 0, 1)

        self.grid_input.addWidget(self.label_input, 0, 0)
        self.grid_input.addWidget(self.le_input, 0, 1)
        self.grid_input.addWidget(self.button_input, 0, 2)

        self.grid_template.addWidget(self.label_template, 0, 0)
        self.grid_template.addWidget(self.le_template, 0, 1)
        self.grid_template.addWidget(self.button_template, 0, 2)

        self.grid_button.addWidget(self.button_operate, 0, 0)

        self.grid_full.addLayout(self.grid_input, 0, 0)
        self.grid_full.addLayout(self.grid_template, 1, 0)
        self.grid_full.addLayout(self.grid_checkbox, 2, 0)
        self.grid_full.addLayout(self.grid_button, 3, 0)

        self.grid_full.setGeometry(QRect(50, 50, 400, 250))
        self.grid_full.setAlignment(Qt.AlignCenter)

        self.resizeEvent = self.adjustSize


        method = ['NiftyReg']

        self.combox_t.addItems(method)

        self.combox_t.activated.connect(self.switch_method)
        self.button_operate.clicked.connect(self.operate)
        self.button_input.clicked.connect(self.select_dir_input)
        self.button_template.clicked.connect(self.select_dir_tmp)

    def adjustSize(self, event):
        self.grid_full.setGeometry(QRect(50, 50, (self.width() - 100), (self.height() - 100))) # 将组件全部显示后调整尺寸

    def switch_method(self, text):
        self.method = text

    def select_dir_input(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_input = QFileDialog.getOpenFileNames(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_input = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
            else:
                self.path_input = QFileDialog.getOpenFileNames(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_input = QFileDialog.getOpenFileNames(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_input = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
            else:
                self.path_input = QFileDialog.getOpenFileNames(self, '选择文件', './')[0]
        self.le_input.setText(str(self.path_input))

    def select_dir_tmp(self):
        if self.lan == 0:
            if platform.system() == "Windows":
                self.path_template = QFileDialog.getOpenFileName(self, 'Select File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_template = QFileDialog.getOpenFileName(self, 'Select File', './')[0]
            else:
                self.path_template = QFileDialog.getOpenFileName(self, 'Select File', './')[0]
        elif self.lan == 1:
            if platform.system() == "Windows":
                self.path_template = QFileDialog.getOpenFileName(self, '选择文件', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
            elif platform.system() == "Linux":
                self.path_template = QFileDialog.getOpenFileName(self, '选择文件', './')[0]
            else:
                self.path_template = QFileDialog.getOpenFileName(self, '选择文件', './')[0]
        self.le_template.setText(str(self.path_template))

    def operate(self):
        if self.method == "NiftyReg":
            self.seg_niftyreg()

    def seg_niftyreg(self):
        if self.method == "NiftyReg":
            thread = thread_seg_reg(self, self.lan)
            thread.start()

class thread_seg_reg(QThread):
    progress = pyqtSignal(float)
    iteration = pyqtSignal(int)
    trigger = pyqtSignal()
    def __init__(self, parent, lan = 0):
        super(thread_seg_reg, self).__init__(parent)
        self.temp = parent
        self.lan = lan
        self.path_template = self.temp.path_template
        self.path_input = self.temp.path_input
        self.path_local = os.path.realpath(__file__)

    def __del__(self):
        self.wait()

    def run(self):
        if " " in self.path_local:
            path_bin = '"%s" "%s"' % (path_bin, "-h")
        if "/" in self.path_local:
            path_bin = self.path_local.replace(self.path_local.split('/')[-1], "Utils/reg_aladin.exe")

        elif '\\' in self.path_local:
            path_bin = self.path_local.replace(self.path_local.split('\\')[-1], "Utils\\reg_aladin.exe")

        for item in self.path_input:
            print(item)
            self.path_input_single = item
            if self.temp.method == 'NiftyReg':
                if " " in item:
                    self.path_input_single = '"%s" "%s"' % (self.path_input_single, "-h")
                if ".gz" in self.path_input_single:
                    path_aff = self.path_input_single.repalce(".nii.gz", "_affine.txt")
                    path_save = self.path_input_single.replace("nii.gz", "_seg.nii")
                elif ".nii" in self.path_input_single:
                    path_aff = self.path_input_single.replace(".nii", "_affine.txt")
                    path_save = self.path_input_single.replace(".nii", "_seg.nii")
                task = subprocess.Popen('%s -ref %s -flo %s -res %s -aff %s' %  (path_bin,self.path_input_single,self.path_template,path_save,path_aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                msg = ""
                for line in task.stdout.readlines():
                    msg += line.decode("gb2312")
                status = task.wait()
                print(msg)
