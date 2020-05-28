#coding=utf-8

import nibabel as ni
import numpy as np
import pydicom
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QLineEdit, QRadioButton, QPushButton, QGridLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import QCoreApplication, Qt, QRect
from calculation import *

################################################################################

class ui_setting(QMainWindow):
    def __init__(self, parent, lan = 0):
        super(ui_setting, self).__init__(parent)
        self.lan = lan
        self.temp = parent
        self.setGeometry(206,208,750,300) # 设置子窗口的尺寸
        self.setMinimumSize(250, 250) # 设置子窗口的最小尺寸
        self.display_type = 0 # 用于确认输入nii的模式，与calculation的ui_cbf.display_type一致

        self.display_asl, self.lamda, self.PLD, self.T1_blood, self.alpha, self.tau, self.TI, self.TI_1 = parent.get_value()

        self.initUI()


    def initUI(self):
        if self.lan == 0:
            self.setWindowTitle("Settings for CBF Calculation")
            self.label_name_lamda = QLabel("Brain/blood Partition Coefficient(λ):", self)
            self.label_name_pld = QLabel("Post Label Delay(PLD):", self)
            self.label_name_t1blood = QLabel("Longitudinal Relaxation Time of Blood(T1_blood):", self)
            self.label_name_alpha = QLabel("Labeling Efficiency(α):", self)
            self.label_name_tau = QLabel("Label Duration(τ):", self)
            self.label_name_ti = QLabel("Inversion Time(TI):", self)
            self.label_name_ti1 = QLabel("Bolus Duration(TI1):", self)
        elif self.lan == 1:
            self.setWindowTitle("CBF计算相关设置")
            self.label_name_lamda = QLabel("脑/血分配系数(λ):", self)
            self.label_name_pld = QLabel("标记后延时(PLD):", self)
            self.label_name_t1blood = QLabel("血液纵向松弛时间(T1_blood):", self)
            self.label_name_alpha = QLabel("标记效率(α):", self)
            self.label_name_tau = QLabel("标记持续时间(τ):", self)
            self.label_name_ti = QLabel("反转时间(TI):", self)
            self.label_name_ti1 = QLabel("二次标记持续时间(TI1):", self)

        self.label_val_lamda = QLineEdit(self)
        self.label_val_pld = QLineEdit(self)
        self.label_val_t1blood = QLineEdit(self)
        self.label_val_alpha = QLineEdit(self)
        self.label_val_tau = QLineEdit(self)
        self.label_val_ti = QLineEdit(self)
        self.label_val_ti1 = QLineEdit(self)

        self.label_val_lamda.setText(str(self.lamda))
        self.label_val_pld.setText(str(self.PLD))
        self.label_val_t1blood.setText(str(self.T1_blood))
        self.label_val_alpha.setText(str(self.alpha))
        self.label_val_tau.setText(str(self.tau))
        self.label_val_ti.setText(str(self.TI))
        self.label_val_ti1.setText(str(self.TI_1))

        self.label_val_lamda.editingFinished.connect(self.modify_display)
        self.label_val_pld.editingFinished.connect(self.modify_display)
        self.label_val_t1blood.editingFinished.connect(self.modify_display)
        self.label_val_alpha.editingFinished.connect(self.modify_display)
        self.label_val_tau.editingFinished.connect(self.modify_display)
        self.label_val_ti.editingFinished.connect(self.modify_display)
        self.label_val_ti1.editingFinished.connect(self.modify_display)

        if self.lan == 0:
            self.button_ok = QPushButton("OK", self)
            self.button_reset = QPushButton("Reset", self)
            self.button_cancel = QPushButton("Cancel", self)
            self.button_help = QPushButton("?", self)
            self.button_getdcm = QPushButton("Get Parameters from Dicom file", self)
        elif self.lan == 1:
            self.button_ok = QPushButton("确认", self)
            self.button_reset = QPushButton("重置", self)
            self.button_cancel = QPushButton("取消", self)
            self.button_help = QPushButton("???", self)
            self.button_getdcm = QPushButton("通过Dicom文件读取变量", self)

        self.button_ok.clicked.connect(self.bt_ok)
        self.button_cancel.clicked.connect(self.bt_cancel)
        self.button_help.clicked.connect(self.bt_help)
        self.button_reset.clicked.connect(self.bt_reset)
        self.button_getdcm.clicked.connect(self.bt_getdcm)

        self.grid_radiobutton = QGridLayout()
        self.grid_full = QGridLayout()
        self.grid_button = QGridLayout()
        self.grid_ui = QGridLayout()

        if self.lan == 0:
            self.label_asltype = QLabel("ASL Type:", self)
            self.button_type_pcasl = QRadioButton("PCASL", self)
            self.button_type_pasl = QRadioButton("PASL", self)
        elif self.lan == 1:
            self.label_asltype = QLabel("ASL类型:", self)
            self.button_type_pcasl = QRadioButton("伪连续ASL", self)
            self.button_type_pasl = QRadioButton("脉冲ASL", self)

        self.button_type_pcasl.clicked.connect(self.radiobutton_clicked)
        self.button_type_pasl.clicked.connect(self.radiobutton_clicked)
        self.button_type_pcasl.setChecked(True)

        self.grid_button.addWidget(self.button_ok, 0, 0)
        self.grid_button.addWidget(self.button_cancel, 0, 1)
        self.grid_button.addWidget(self.button_reset, 1, 0)
        self.grid_button.addWidget(self.button_help, 1, 1)
        self.grid_button.setSpacing(30)

        self.grid_radiobutton.addWidget(self.label_asltype, 0, 0)
        self.grid_radiobutton.addWidget(self.button_type_pcasl, 1, 0)
        self.grid_radiobutton.addWidget(self.button_type_pasl, 2, 0)

        self.grid_full.addWidget(self.label_name_lamda, 0, 0)
        self.grid_full.addWidget(self.label_val_lamda, 0, 1)
        self.grid_full.addWidget(self.label_name_t1blood, 1, 0)
        self.grid_full.addWidget(self.label_val_t1blood, 1, 1)
        self.grid_full.addWidget(self.label_name_alpha, 2, 0)
        self.grid_full.addWidget(self.label_val_alpha, 2, 1)

        self.grid_full.addWidget(self.label_name_pld, 0, 2)
        self.grid_full.addWidget(self.label_val_pld, 0, 3)
        self.grid_full.addWidget(self.label_name_tau, 1, 2)
        self.grid_full.addWidget(self.label_val_tau, 1, 3)

        self.grid_full.addWidget(self.label_name_ti, 0, 2)
        self.grid_full.addWidget(self.label_val_ti, 0, 3)
        self.grid_full.addWidget(self.label_name_ti1, 1, 2)
        self.grid_full.addWidget(self.label_val_ti1, 1, 3)

        self.grid_full.setSpacing(15)

        self.grid_ui.addLayout(self.grid_radiobutton, 0, 0)
        self.grid_ui.addLayout(self.grid_full, 0, 1)
        self.grid_ui.addWidget(self.button_getdcm, 1, 0)
        self.grid_ui.addLayout(self.grid_button, 1, 1)
        self.grid_ui.setGeometry(QRect(50, 50, 350, 200))
        self.grid_ui.setSpacing(50)

        self.set_hiden(self.display_asl)

        self.resizeEvent = self.adjustSize

    def set_hiden(self, index):
        if index == 0:
            self.label_name_pld.setHidden(False)
            self.label_val_pld.setHidden(False)
            self.label_name_tau.setHidden(False)
            self.label_val_tau.setHidden(False)
            self.label_name_ti.setHidden(True)
            self.label_val_ti.setHidden(True)
            self.label_name_ti1.setHidden(True)
            self.label_val_ti1.setHidden(True)
            self.button_type_pcasl.setChecked(True)
            self.button_type_pasl.setChecked(False)
        elif index == 1:
            self.label_name_pld.setHidden(True)
            self.label_val_pld.setHidden(True)
            self.label_name_tau.setHidden(True)
            self.label_val_tau.setHidden(True)
            self.label_name_ti.setHidden(False)
            self.label_val_ti.setHidden(False)
            self.label_name_ti1.setHidden(False)
            self.label_val_ti1.setHidden(False)
            self.button_type_pcasl.setChecked(False)
            self.button_type_pasl.setChecked(True)
        else:
            self.label_name_pld.setHidden(False)
            self.label_val_pld.setHidden(False)
            self.label_name_tau.setHidden(False)
            self.label_val_tau.setHidden(False)
            self.label_name_ti.setHidden(False)
            self.label_val_ti.setHidden(False)
            self.label_name_ti1.setHidden(False)
            self.label_val_ti1.setHidden(False)

    def modify_display(self):
        self.lamda = float(self.label_val_lamda.text())
        self.PLD = float(self.label_val_pld.text())
        self.T1_blood = float(self.label_val_t1blood.text())
        self.alpha = float(self.label_val_alpha.text())
        self.tau = float(self.label_val_tau.text())
        self.TI = float(self.label_val_ti.text())
        self.TI_1 = float(self.label_val_ti1.text())

    def radiobutton_clicked(self):
        if self.button_type_pcasl.isChecked() == True:
            self.alpha = 0.85
            self.label_val_alpha.setText(str(self.alpha))
            self.display_asl = 0
        elif self.button_type_pasl.isChecked() == True:
            self.alpha = 0.98
            self.label_val_alpha.setText(str(self.alpha))
            self.display_asl = 1
        self.set_hiden(self.display_asl)

    def bt_getdcm(self):
        # 读取DCM文件中的相关信息
        if self.lan == 0:
            path_temp = QFileDialog.getOpenFileName(self, 'Select File', './', "DICOM Files (*.dcm);;All Files (*)")[0]
        elif self.lan == 1:
            path_temp = QFileDialog.getOpenFileName(self, '选择文件', './', "DICOM Files (*.dcm);;All Files (*)")[0]
        try:
            dcm = pydicom.dcmread(path_temp)
            if 'pulsed continuous' in str(dcm['0043','10a4'].value) == True:
                self.display_asl = 0
            elif 'pulsed' in str(dcm['0043','10a4'].value) == True and 'continuous' in str(dcm['0043','10a4'].value) == False:
                self.display_asl = 1
            if dcm.MagneticFieldStrength == 3:
                self.T1_blood = 1.65
            elif dcm.MagneticFieldStrength == 1.5:
                self.T1_blood = 1.35
            self.T1 = dcm.InversionTime / 1000
            self.tau = int(dcm['0043', '10a5'].value) / 1000
            self.modify_display()

        except FileNotFoundError:
            pass

    def bt_ok(self):
        # 传递修改后的参数到calculation中
        self.temp.set_value(self.display_asl, self.lamda, self.PLD, self.T1_blood, self.alpha, self.tau, self.TI, self.TI_1)
        self.close()

    def bt_cancel(self):
        self.close()

    def bt_reset(self):
        self.display_asl = 0
        self.lamda = 0.9
        self.PLD = 2000 / 1000
        self.T1_blood = 1650 / 1000
        self.alpha = 0.85
        self.tau = 1800 / 1000
        self.TI =  2000 / 1000
        self.TI_1 = 800 / 1000
        self.label_val_lamda.setText(str(self.lamda))
        self.label_val_pld.setText(str(self.PLD))
        self.label_val_t1blood.setText(str(self.T1_blood))
        self.label_val_alpha.setText(str(self.alpha))
        self.label_val_tau.setText(str(self.tau))
        self.label_val_ti.setText(str(self.TI))
        self.label_val_ti1.setText(str(self.TI_1))

    def bt_help(self):
        msg = QMessageBox(self)
        if self.lan == 0:
            msg.setWindowTitle("HELP")
            msg.setText("The meaning and recommended value of each variable can be found in Alsop's \
    Recommended Implementation of Arterial Spin Labeled Perfusion MRI for Clinical Applications: A consensus \
    of the ISMRM Perfusion Study Group and the European Consortium for ASL in Dementia: \n\
        PCASL Labeling Duration: 1800ms\n\
        PCASL PLD - Neonates: 2000ms\n\
        PCASL PLD - Children: 1500ms\n\
        PCASL PLD - Healthy subjects < 70 yrs: 1800ms\n\
        PCASL PLD - Healthy subjects > 70 yrs: 2000ms\n\
        PCASL PLD - Adult clinical patients: 2000ms\n\
        PASL TI1: 800ms\n\
        PASL T1: Use PCASL PLD\n\
        λ (blood-brain partition coefficient): 0.9mL/g\n\
        T1, blood at 3.0 Tesla: 1650ms\n\
        T1, blood at 1.5 Tesla: 1350ms\n\
        α (labeling efficiency) for PCASL: 0.85\n\
        α (labeling efficiency) for PASL: 0.98")
        elif self.lan == 1:
            msg.setWindowTitle("帮助")
            msg.setText("计算使用的不同变量的含义和参考值可以参考Alsop的\
    Recommended Implementation of Arterial Spin Labeled Perfusion MRI for Clinical Applications: A consensus \
    of the ISMRM Perfusion Study Group and the European Consortium for ASL in Dementia一文: \n\
        PCASL Labeling Duration: 1800ms\n\
        PCASL PLD - 新生儿: 2000ms\n\
        PCASL PLD - 儿童: 1500ms\n\
        PCASL PLD - 70岁以下健康人: 1800ms\n\
        PCASL PLD - 70岁以上健康人: 2000ms\n\
        PCASL PLD - 成年临床患者: 2000ms\n\
        PASL TI1: 800ms\n\
        PASL T1: Use PCASL PLD\n\
        λ (blood-brain partition coefficient): 0.9mL/g\n\
        T1, blood at 3.0 Tesla: 1650ms\n\
        T1, blood at 1.5 Tesla: 1350ms\n\
        α (labeling efficiency) for PCASL: 0.85\n\
        α (labeling efficiency) for PASL: 0.98")
        msg.setIcon(QMessageBox.Information)

        msg.setStandardButtons(QMessageBox.Ok) # pyqt默认的ok键
        msg.show()

    def adjustSize(self, event):
        self.set_hiden(10086) # 只要是else里的值就行
        self.grid_ui.setGeometry(QRect(50, 50, (self.width() - 100), (self.height() - 100))) # 将组件全部显示后调整尺寸
        self.set_hiden(self.display_asl) # 设置组件隐藏状态
