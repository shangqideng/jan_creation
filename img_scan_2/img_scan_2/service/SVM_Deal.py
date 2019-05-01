import cv2
from sklearn.externals import joblib
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

def Get_Content():
    '''
    返回菜品的列表
    :return: 
    '''
    f = open('./First_Page.txt')
    temp = []
    data = []
    for line in f.readlines():
        line = line.strip()
        line = line.split('\t')
        temp.append(line)
    data.append(temp[0:9])
    data.append(temp[9:12])
    data.append(temp[12:20])
    data.append(temp[20:52])
    data.append(temp[52:74])
    data.append(temp[74:82])
        # print(line[0:2])

    # print(len(data))
    return data  #分成六个区域
# 图片预测
def SVM_Deal(img_list):
    """
    SVM预测
    :param img_list_split: 六个区域的img
    :param content_list: 与标记点对应的文本内容
    :param Checked_Content: 返回内容
    :return: 
    """

    # 模型启用
    new_svm = joblib.load('./SVM_data/svm.pkl')
    content_list = Get_Content() #菜品的列表

    # 把六个区域的合在一起
    # img_list = []
    # for i in range(len(img_list_split)):
    #     img_list.extend(img_list_split[i])

    # 进行识别
    Checked_Content = []
    for j in range(6):
        for i in range(len(img_list[j])):
            # 存储图片
            if not os.path.exists('e:/train/'):
                os.makedirs('e:/train/')
            start = len(os.listdir('e:/train/'))
            img = Image.fromarray(img_list[j][i])
            img.save('e:/train/%s.jpg' % start)

            gray = cv2.cvtColor(img_list[j][i], cv2.COLOR_BGR2GRAY)  # 转化为灰度图

            # 更改图片大小
            # img_resize = cv2.resize(gray, (30, 30))
            # im_normalization = np.array(img_resize) / np.max(img_resize)  # 读取归一化数组
            # im = np.round(im_normalization.reshape(1, 900))  # 将数组中的元素四舍五入
            # img_final = np.reshape(im, (1, -1))  # 1 * 900矩阵，转换成2类：对应1或-1


            changeimg = cv2.resize(gray, (30, 30))
            binary = cv2.adaptiveThreshold(changeimg, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 85,
                                           30)  # 局部二值化
            im = binary.reshape(1, 900)/255  # 将数组中的元素四舍五入
            # print(np.shape(im))
            img_final = np.reshape(im, (1, -1))  # 1 * 900矩阵，转换成2类：对应1或-1

            prediction = new_svm.predict(img_final)[0]
            if abs(prediction) >= abs(prediction-1):
                Checked_Content.append(content_list[j][i])
                # cv2.namedWindow("%s-%sy" % (j, i), 0)
                # cv2.imshow("%s-%sy" % (j, i), changeimg)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    return Checked_Content

# Get_Content()