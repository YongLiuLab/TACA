# coding=UTF-8
import numpy as np
import nibabel as ni
from PyQt5.QtCore import QCoreApplication, Qt, QThread, pyqtSignal
# from progress_pve import *
from display import *
import time

class LRThread(QThread):
    progress = pyqtSignal(float)
    trigger = pyqtSignal()
    file = pyqtSignal(int)
    def __init__(self, parent, lan = 0):
        super(LRThread, self).__init__(parent)
        self.temp = parent
        self.data_cbf = ""
        self.data_gm = ""
        self.data_wm = ""
        self.data_csf = ""
        self.fwhm = [5,5,1]
        self.lan = lan
        self.data_result = ""

    def __del__(self):
        self.wait()

    def get_value(self, index = 0):
        self.data_cbf = ni.load(self.temp.path_cbf[index]).get_fdata()
        self.data_gm = ni.load(self.temp.path_gm[index]).get_fdata()
        self.data_wm = ni.load(self.temp.path_wm[index]).get_fdata()
        if self.temp.path_csf != "":
            self.data_csf = ni.load(self.temp.path_csf[index]).get_fdata()
        else:
            pass


    def run(self):
        for idx in range(len(self.temp.path_cbf)):
            self.get_value(idx)
            self.linearegress(self.data_cbf, self.data_gm, self.data_wm, self.data_csf, self.fwhm)
            self.file.emit(idx)
            ni.save(ni.Nifti1Image(self.data_result, ni.load(self.temp.path_cbf[idx]).affine, ni.load(self.temp.path_cbf[idx]).header), "D:/test_lr_gui.nii")
        self.trigger.emit()


    def linearegress(self, data_cbf, data_gm, data_wm, data_csf, fwhm = [5,5,1]):
        if fwhm[0] * fwhm[1] * fwhm[2] <= 3:
            fwhm = [5, 5, 1]
        ker_x = int((fwhm[0] - 1) / 2)
        ker_y = int((fwhm[1] - 1) / 2)
        ker_z = int((fwhm[2] - 1) / 2)

        if data_cbf.shape != data_gm.shape:
            if self.lan == 0:
                warn_msg(self, "Make Sure the Segment Image has the same shape as the CBF/ASL Image!")
            elif self.lan == 1:
                warn_msg(self, "请确认分割后图像的尺寸是否与灌注图像一致")
            return data_cbf

        if self.data_csf == "":
            mask = (data_gm + data_wm) > 0.2
        else:
            mask = (data_gm + data_wm + data_csf) > 0.2
        data_cbf = data_cbf * mask

        save_gm = np.copy(data_cbf)
        save_wm = np.copy(data_cbf)
        if self.data_csf != "":
            save_csf = np.copy(data_cbf)
        else:
            pass

        x, y, z = data_cbf.shape[0], data_cbf.shape[1], data_cbf.shape[2]
        for i in range(x):
            for j in range(y):
                if j % 10 == 0:
                    self.progress.emit(round((j + y * i) / (x * y) * 100, 2))
                for k in range(z):
                    if data_cbf[i,j,k] > 0:
                        temp_magneti = []
                        temp_gm = []
                        temp_wm = []
                        temp_csf = []
                        for size_x in range(fwhm[0]):
                            for size_y in range(fwhm[1]):
                                for size_z in range(fwhm[2]):
                                    try:
                                        if data_cbf[i - ker_x + size_x, j - ker_y + size_y, k - ker_z + size_z] != 0:
                                            temp_magneti.append(data_cbf[i - ker_x + size_x, j - ker_y + size_y, k - ker_z + size_z])
                                            temp_gm.append(data_gm[i - ker_x + size_x, j - ker_y + size_y, k - ker_z + size_z])
                                            temp_wm.append(data_wm[i - ker_x + size_x, j - ker_y + size_y, k - ker_z + size_z])
                                            if self.data_csf != "":
                                                temp_csf.append(data_csf[i - ker_x + size_x, j - ker_y + size_y, k - ker_z + size_z])
                                            else:
                                                pass
                                    except IndexError:
                                        print("Index Error")
                        if len(temp_magneti) > 3:
                            temp_magneti = np.mat(temp_magneti)
                            if self.data_csf == "":
                                temp_indiv = np.mat([temp_gm, temp_wm])
                            else:
                                temp_indiv = np.mat([temp_gm, temp_wm, temp_csf])
                            try:
                                temp_result = ((temp_indiv.I).T * temp_magneti.T).T
                                if self.data_csf == "":
                                    save_gm[i,j,k], save_wm[i,j,k] = temp_result[0,0], temp_result[0,1]
                                else:
                                    save_gm[i,j,k], save_wm[i,j,k], save_csf[i,j,k] = temp_result[0,0], temp_result[0,1], temp_result[0,2]

                            except np.linalg.linalg.LinAlgError:
                                print("NP Error")

        # nii_gm = ni.Nifti1Image(save_gm * (data_gm > 0.5), ni.load(path_pwi).affine, ni.load(path_pwi).header)
        # ni.save(nii_gm, path_save)
        # nii_wm = ni.Nifti1Image(save_wm * (data_wm > 0.5), ni.load(path_pwi).affine, ni.load(path_pwi).header)
        # ni.save(nii_wm, path_save.replace("gm","wm"))
        # nii_csf = ni.Nifti1Image(save_csf * (data_csf > 0.5), ni.load(path_pwi).affine, ni.load(path_pwi).header)
        # ni.save(nii_csf, path_save.replace("gm","csf"))
        # nii_full = ni.Nifti1Image(save_gm * (data_gm > 0.5) + save_wm * (data_wm > 0.5) + save_csf * (data_csf > 0.1) * (data_gm <=0.5) * (data_wm <= 0.5), ni.load(path_pwi).affine, ni.load(path_pwi).header)
        # ni.save(nii_full, path_save.replace("gm","full"))
        if self.data_csf == "":
            self.data_result = save_gm + save_wm
        else:
            self.data_result = save_gm + save_wm + save_csf
