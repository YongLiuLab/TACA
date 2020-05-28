#TACA#

TACA全称为Toolkit for Analysis on CBF and ASL，是基于python进行计算及相关代码编写，利用PyQt库进行图形界面编写的ASL-CBF数据处理软件，可以用于ASL数据的配准、简单分割、CBF计算及相关的局部空间校正和基于图谱的数据提取。

##安装##

TACA在Windows平台上运行良好，在Linux平台上可以实现大部分功能。目前未进行安装脚本的编写，可以直接将对应的.py文件及`/source`、`/Utils`文件夹下载后使用。路径下同时提供了requirement.txt文件，可以使用`pip install –r requirement.txt`(对应的requirement.txt文件所在路径)进行TACA需要使用的python依赖库的快速安装。

其中，配准功能所需要使用的NiftyReg工具以集成在软件中，但Flirt/Fnirt功能需要自行进行FSL的安装。

这里推荐使用Anaconda进行python环境的配置，需要的操作如下：

- 如果没有Anaconda，可以从[anaconda官网](https://www.anaconda.com)进行下载。
- 通过`Win+R`打开运行窗口，输入`cmd`，或从对应的系统文件夹中调用`CMD.exe`。
- 在CMD中输入`conda create –n taca python=3.7`以创建对应的python环境(`taca`为对应的环境名，可以自行更改)
- 然后通过输入`conda activate taca`进行环境激活
- 调用软件路径下的`requirement.txt`文件进行相应的python库安装，在CMD中输入`pip install –r requirement.txt`即可，若提示`No such file or directory`，则需要将CMD中路径调整到软件路径，或将requirement.txt更改为对应的软件所在文件夹所在路径，如`install –r D:/TACA/requirement.txt`
- 等待对应的python库安装完成后，在CMD中输入`python tca_pyqt.py`即可打开TACA的主界面

主要功能

图像输入及显示：

- 读取nii格式文件
- 显示nii图像
- 自动读取和显示文件部分参数
- 进行区域勾画（未完成）
- 图像保存

图像预处理：

- 图像配准(使用NiftyReg工具；提供FSL的Flirt和Fnirt接口，需自行安装)
- 图像分割(使用NiftyReg工具)

图像计算：

- 通过ASL图像计算对应的CBF图像
- CBF的局部空间校正
- 通过脑图谱提取部分区域的平均CBF值(`/source`文件夹下附带2mm分辨率的脑网络组图谱)

##

TACA is the short form of Toolkit for Analysis on CBF and ASL， a toolkit with its calculation code based on python and GUI based on PyQt library. It can be used for coregistering and simple segmentation on ASL data, CBF calculation, Partial Volume Correlation and extraction of CBF on brain atlas.

##Installation##

TACA can work well on Windows platform, most of its function also run well on Linux platform. The installation script is still undone, you can download the python scripts and folders named source and Utils to use TACA. There is a `requirement.txt file` in the toolkit for quick installation of python libraries used in TACA.

The NiftyReg toolkit for coregister function is contained in TACA, but if you want to use Flirt/Fnirt function to coregister, you have to install FSL by yourself.

Anoconda is recommended to use for enviroment configuration, you can follow the steps bellow for installion:

- If you don't have conda environment, you can download it from [here](https://www.anaconda.com).
- Open CMD window by using `Win+R` and input `cmd`, or just find where `CMD.exe` is.
- Create a new environment: `conda create –n taca python=3.7`, `taca` here is the name of the environment, you can modify it as you want.
- Activate the environment created above: `conda activate taca`.
- Use the `requirement.txt` file for installation of dependency python libraries used in TACA: `pip install –r requirement.txt`. If you see the error:`No such file or directory`, switch the directory to where TACA files are, or replace requirement.txt to its directory, i.e. `install –r D:/TACA/requirement.txt`.
- Wait for installation of dependency python libraries, then use `python tca_pyqt.py` to open the main interface of TACA.

Function

Input and Display:

- Read Nifti files
- Display Nifti images
- Display parameters of the file
- Draw ROI (Incomplete)
- Save images

Preprocessing:

- Image coregister (Use NiftyReg, have interface for Flirt/Fnirt which have to install FSL by yourself)
- Image segmentation (Use NiftyReg)

Calculation:

- Calculate CBF image by ASL image
- Partial Volume Correlation for CBF
- Extract mean CBF for different ROIs in a brain template (with 2mm Brainnetome Atlas file in `/source` folder)

