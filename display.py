#coding=utf-8

import nibabel as ni
import numpy as np
# from nilearn.image import smooth_img
from PyQt5.QtWidgets import QLabel, QMessageBox, QComboBox, QMainWindow, QApplication, QMenu
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QPalette, QBrush
from PyQt5.QtCore import QCoreApplication, Qt
import qimage2ndarray as q2n
import sys

################################################################################

class AxialLabel(QLabel):
    def __init__(self, parent = None):
        super(AxialLabel, self).__init__(parent = parent)
        self.temp = parent
        self.update_pm()

    def update_pm(self):
        if self.temp.pixmap_a != "":
            self.setPixmap(self.temp.pixmap_a)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.temp.nii == "":
            self.point = 0, 0
        else:
            self.point = self.temp.display_x / self.temp.nii.get_fdata().shape[0] * self.width(), self.temp.display_z / self.temp.nii.get_fdata().shape[2] * self.height()
        if self.temp.pixmap_a != "":
            if self.temp.bul_displaych == 1:
                self.painter = QPainter(self)
                self.painter.begin(self)
                self.pen = QPen(self.temp.colorch, self.temp.thicknessch, Qt.SolidLine)
                self.painter.setPen(self.pen)
                self.painter.drawLine(self.point[0], self.point[1] - self.temp.gapsizech, self.point[0], 0)
                self.painter.drawLine(self.point[0], self.point[1] + self.temp.gapsizech, self.point[0], self.height())
                self.painter.drawLine(self.point[0] - self.temp.gapsizech, self.point[1], 0, self.point[1])
                self.painter.drawLine(self.point[0] + self.temp.gapsizech, self.point[1], self.width(), self.point[1])
                self.painter.end()

################################################################################

class SagittalLabel(QLabel):
    def __init__(self, parent = None):
        super(SagittalLabel, self).__init__(parent = parent)
        self.temp = parent
        self.update_pm()

    def update_pm(self):
        if self.temp.pixmap_s != "":
            self.setPixmap(self.temp.pixmap_s)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.temp.nii == "":
            self.point = 0, 0
        else:
            self.point = self.temp.display_x / self.temp.nii.get_fdata().shape[0] * self.width(), self.height() - self.temp.display_y / self.temp.nii.get_fdata().shape[1] * self.height()
        if self.temp.pixmap_s != "":
            if self.temp.bul_displaych == 1:
                self.painter = QPainter(self)
                self.painter.begin(self)
                self.pen = QPen(self.temp.colorch, self.temp.thicknessch, Qt.SolidLine)
                self.painter.setPen(self.pen)
                self.painter.drawLine(self.point[0], self.point[1] - self.temp.gapsizech, self.point[0], 0)
                self.painter.drawLine(self.point[0], self.point[1] + self.temp.gapsizech, self.point[0], self.height())
                self.painter.drawLine(self.point[0] - self.temp.gapsizech, self.point[1], 0, self.point[1])
                self.painter.drawLine(self.point[0] + self.temp.gapsizech, self.point[1], self.width(), self.point[1])
                self.painter.end()



################################################################################


class CoronalLabel(QLabel):
    def __init__(self, parent = None):
        super(CoronalLabel, self).__init__(parent = parent)
        self.temp = parent
        self.update_pm()

    def update_pm(self):
        if self.temp.pixmap_c!= "":
            self.setPixmap(self.temp.pixmap_c)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.temp.nii == "":
            self.point = 0, 0
        else:
            self.point = self.temp.display_y / self.temp.nii.get_fdata().shape[1] * self.width(), self.temp.display_z / self.temp.nii.get_fdata().shape[2] * self.height()
        if self.temp.pixmap_c != "":
            if self.temp.bul_displaych == 1:
                self.painter = QPainter(self)
                self.painter.begin(self)
                self.pen = QPen(self.temp.colorch, self.temp.thicknessch, Qt.SolidLine)
                self.painter.setPen(self.pen)
                self.painter.drawLine(self.point[0], self.point[1] - self.temp.gapsizech, self.point[0], 0)
                self.painter.drawLine(self.point[0], self.point[1] + self.temp.gapsizech, self.point[0], self.height())
                self.painter.drawLine(self.point[0] - self.temp.gapsizech, self.point[1], 0, self.point[1])
                self.painter.drawLine(self.point[0] + self.temp.gapsizech, self.point[1], self.width(), self.point[1])
                self.painter.end()


################################################################################

def nii2display(mainwindow, volume, data_input, min, max, index_lan = 0):
    if len(data_input.shape) == 4:
        if data_input.shape[3] > 1 and volume == -1:
            # if index_lan == 0:
            #     warn_msg(mainwindow, "This nii file contains more than one time series, only the first one will be displayed.")
            # elif index_lan == 1:
            #     warn_msg(mainwindow, "Nii文件包括了超过一个序列，默认显示第一个")
            data = data_input[:,:,:,0] # 默认将第一幅volume作为显示值
        elif data_input.shape[3] >= 1 and volume >= 0:
            data = data_input[:,:,:,volume]
    else:
        data = data_input
    if max == min:
        data = np.rot90(data) # 一般用于针对单区域Label图像等体素数值非常集中情况的显示问题
    else:
        data = (np.rot90(data) - min) * ( 255 / (max - min)) # 正常情况下，将对应的体素数值转化为对应的灰度值，范围为0-255
    data = (data * (data >= 0)) * (data <= 255) + 255 * (data > 255)
    mainwindow.refreshInfo()
    return data

################################################################################

def gray2color(data):
    data_rgb = np.zeros((data.shape[0], data.shape[1], 3))
    r = (data > 128) * (data < 192) * (data - 128) * 255 / 64 + (data >= 192) * 255
    g = (data < 64) * data * 255 / 64 + (data >= 64) * (data < 192) * 255 + (255 - (data >= 192) * 255 / 63 * (data - 192))
    b = (data < 64) * 255 + (data >= 64) * (data < 128) * (510 - 255 / 64 * (data)) + 0 * (data >= 128)
    data_rgb[:,:,2] = b
    data_rgb[:,:,0] = r
    data_rgb[:,:,1] = g
    return data_rgb

################################################################################

def display_nii(mainwindow, data, x, y, z, volume, min, max, label_axial, label_coronal, label_sagittal, index_lan = 0, color_type = 0):
    # 将data中的某点对应的slice进行显示
    # slice_x = data[x,:,:]
    # slice_y = data[:,y,:]
    # slice_z = data[:,:,z]
    slice_x = np.rot90(data[-1-y,:,:])
    slice_y = np.rot90(data[:,-1-x,:])
    slice_z = (data[:,:,-1-z]) # 我也不知道为什么读出来的data要这么转换，但这样的显示是对的
    ######伪彩色图像测试###########
    if color_type == 1:
        slice_x_rgb = gray2color(slice_x)
        slice_y_rgb = gray2color(slice_y)
        slice_z_rgb = gray2color(slice_z)
        img_x = q2n.array2qimage(slice_x_rgb)
        img_y = q2n.array2qimage(slice_y_rgb)
        img_z = q2n.array2qimage(slice_z_rgb) # 将灰度值转化为pyqt可以处理的qimage格式(使用包qimage2ndarray)

    elif color_type == 0:
        img_x = q2n.gray2qimage(slice_x)
        img_y = q2n.gray2qimage(slice_y)
        img_z = q2n.gray2qimage(slice_z) # 将灰度值转化为pyqt可以处理的qimage格式(使用包qimage2ndarray)

    #########测试结束#############

    img_x = QPixmap.fromImage(QImage.mirrored(img_x, True, False))
    img_y = QPixmap.fromImage(QImage.mirrored(img_y, True, False))
    img_z = QPixmap.fromImage(QImage.mirrored(img_z, True, False)) # 将qimage转换为qpixmap，同时进行镜像处理

    # # data = np.rot90(data, -1, (2, 1))
    # # data = np.rot90(data, 1, (0, 2))
    # # data = np.rot90(data, 1, (0, 1))
    # # data = np.transpose(data)
    # slice_x = data[y, :, :]
    # slice_y = data[:, x, :]
    # slice_z = data[:, :, z]
    # img_x = QPixmap.fromImage(q2n.gray2qimage(slice_x))
    # img_y = QPixmap.fromImage(q2n.gray2qimage(slice_y))
    # img_z = QPixmap.fromImage(q2n.gray2qimage(slice_z))
    label_axial.clear()
    label_coronal.clear()
    label_sagittal.clear()
    # label_axial.setPixmap(img_x)
    # label_coronal.setPixmap(img_y)
    # label_sagittal.setPixmap(img_z) # 将三个方向的slice分别显示在对应的label中
    return img_x, img_y, img_z

################################################################################

def warn_msg(mainwindow, message, type = 0):
    # 用于显示(type=0)警告或(type=1)信息，message需要为str格式
    msg = QMessageBox(mainwindow)
    if type == 0:
        msg.setWindowTitle("Attention")
        msg.setIcon(QMessageBox.Warning)
    elif type == 1:
        msg.setWindowTitle("Notice")
        msg.setIcon(QMessageBox.Information)
    msg.setText(message) # 将输入的message输出到文本框中
    msg.setStandardButtons(QMessageBox.Ok) # pyqt默认的ok键
    msg.show()

################################################################################

class subWindow(QMainWindow):
# 显示单幅图片的子窗口
    def __init__(self, index, title, lan = 0, parent=None):
        super(subWindow, self).__init__(parent)
        self.setGeometry(200,200,500,500) # 设置子窗口的尺寸
        self.setMinimumSize(200,200) # 设置子窗口的最小尺寸
        self.resizeEvent = self.adjustSize # 当子窗口的尺寸变化时，自动调整label的大小
        self.setMouseTracking(False) # 只有鼠标任意键被按下时才会捕捉鼠标轨迹
        self.pos_xy = [] # 初始化鼠标轨迹点
        self.mousePressEvent = self.mouse_press # 捕捉鼠标点击的动作
        self.mouseMoveEvent = self.mouse_tracking # 捕捉鼠标点击后移动的动作(通过setMouseTracking(False)实现点击后才会捕捉)
        self.mouseReleaseEvent = self.mouse_release # 捕捉鼠标松开按键的动作
        self.mouseDoubleClickEvent = self.mouse_double # 捕捉鼠标双击的动作
        self.paintEvent = self.painton # 捕捉画笔动作
        self.lan = lan
        if index == 0:
            self.pixmap = parent.pixmap_a
        elif index == 1:
            self.pixmap = parent.pixmap_c
        elif index == 2:
            self.pixmap = parent.pixmap_s
        self.setWindowTitle(title)

    def set_pic(self, mainwindow, index):
    #用于显示某个单独视图，index = 0:Axial, 1:Coronal, 2:Sagittal
        if index == 0:
            self.palette = QPalette() # 设置背景画布
            # self.pixmap = mainwindow.label_axial.pixmap() # 设置pixmap图像
            self.palette.setBrush(QPalette.Background,QBrush(self.pixmap.scaled(self.width(), self.height(), transformMode=Qt.SmoothTransformation)))
            # 将图像平滑缩放为窗口大小并作为背景
            self.setPalette(self.palette) # 设置背景
            if self.lan == 0:
                self.setWindowTitle("DISPLAY AXIAL") # 修改标题
            elif self.lan == 1:
                self.setWindowTitle("显示轴向切片")
        elif index == 1:
            self.palette = QPalette()
            self.pixmap = mainwindow.label_coronal.pixmap()
            self.palette.setBrush(QPalette.Background,QBrush(self.pixmap.scaled(self.width(), self.height(), transformMode=Qt.SmoothTransformation)))
            self.setPalette(self.palette)
            if self.lan == 0:
                self.setWindowTitle("DISPLAY CORONAL")
            elif self.lan == 1:
                self.setWindowTitle("显示冠状切片")
        elif index == 2:
            self.palette = QPalette()
            self.pixmap = mainwindow.label_sagittal.pixmap()
            self.palette.setBrush(QPalette.Background,QBrush(self.pixmap.scaled(self.width(), self.height(), transformMode=Qt.SmoothTransformation)))
            self.setPalette(self.palette)
            if self.lan == 0:
                self.setWindowTitle("DISPLAY SAGITTAL")
            elif self.lan == 1:
                self.setWindowTitle("显示矢状切片")

    def adjustSize(self, event):
    # 调节图像大小，与窗口大小相适应；调节绘制点位置，与窗口大小相适应
        # print(self.pixmap)
        self.palette = QPalette() # 设置背景画布
        self.palette.setBrush(QPalette.Background,QBrush(self.pixmap.scaled(self.width(), self.height(), transformMode=Qt.SmoothTransformation)))
        self.setPalette(self.palette)

    def painton(self, event):
    # 在子窗口绘制鼠标拖曳轨迹
        self.painter = QPainter()
        self.painter.begin(self)
        self.pen = QPen(Qt.red, 2, Qt.SolidLine) # 设置画笔颜色
        self.painter.setPen(self.pen)
        if len(self.pos_xy) != 0: # 排除可能出现的单击左键
            for item in self.pos_xy:
                point_start = item[0]
                for points in item:
                    if points != point_start:
                        point_end = points
                        self.painter.drawLine(point_start[0] / 500 * self.width(), point_start[1] / 500 * self.height(), point_end[0] / 500 * self.width(), point_end[1] / 500 * self.height())
                        point_start = point_end
        self.painter.end()

    def mouse_press(self, event):
    # 左键按下，新建这次鼠标轨迹对应的部分，保存时将位置统一转化为初始窗口大小对应的位置；右键按下，显示菜单
        # print("tic")
        if event.button() == 1:
            self.pos_xy.append([]) # 新建一个轨迹
            self.pos_xy[-1].append([(event.pos().x()) / self.width() * 500, (event.pos().y()) / self.height() * 500]) # 将鼠标的轨迹点存储到最近新建的pos_xy部分
        elif event.button() == 2:
            self.rightmenu = QMenu(self)
            if self.lan == 0:
                autocloseAction = self.rightmenu.addAction("Autoclose")
                withdrawAction = self.rightmenu.addAction("Withdraw")
                saveAction = self.rightmenu.addAction("Save")
            elif self.lan == 1:
                autocloseAction = self.rightmenu.addAction("自动闭合")
                withdrawAction = self.rightmenu.addAction("撤销")
                saveAction = self.rightmenu.addAction("保存")
            withdrawAction.triggered.connect(self.withdraw)
            saveAction.triggered.connect(self.save)
            autocloseAction.triggered.connect(self.autoclose)
            action = self.rightmenu.exec_(self.mapToGlobal(event.pos()))
            self.rightmenu.show()

    def mouse_double(self, event):
    # 双击界面，自动填充鼠标位置直至充满闭合区域(undone)
        pass

    def save(self):
    # 还没做的保存功能，不知道存什么东西好
        # nii_save = ni.Nifti1Image()
        pass

    def autoclose(self):
        if len(self.pos_xy[-1]) != 1:
            self.pos_xy[-1].append(self.pos_xy[0][0])
        if len(self.pos_xy) >= 2:
            self.pos_xy[-2].append(self.pos_xy[-1][0])
        self.update()


    def withdraw(self):
        try:
            self.pos_xy.pop(-1)
        except IndexError:
            pass
        self.update()

    def mouse_tracking(self, event):
    # 捕捉鼠标运动轨迹，将对应点保存到self.pos_xy，保存时将位置统一转化为初始窗口大小对应的位置
        try:
            self.pos_xy[-1].append([(event.pos().x()) / self.width() * 500, (event.pos().y()) / self.height() * 500]) # 将鼠标的轨迹点存储到最近新建的pos_xy部分
            self.update() # 更新显示
        except IndexError:
            print("Right Click")

    def mouse_release(self, event):
    # 预留鼠标键松开的事件，用于删除只有一个孤立点的无用轨迹
        if len(self.pos_xy[-1]) <= 1:
            self.pos_xy.pop(-1)
