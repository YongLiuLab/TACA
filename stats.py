#coding=utf-8

import nibabel as ni
import numpy as np
import scipy.stats as scst

################################################################################

class ui_stats(QMainWindow):
    def __init__(self, group, language = 1, parent = None):
        self.grp = group
        self.lan = language
        self.parent = parent

        self.initUI()

    def initUI(self):



    def cal_dif(self):
        if len(self.group) == 2:
