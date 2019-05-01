import numpy as np
import matplotlib.pyplot as plt
import math
from copy import deepcopy

def caculate_distance(v1, v2):
    vec1 = np.array(v1)
    vec2 = np.array(v2)
    return np.sqrt(np.sum((vec1 - vec2) * (vec1 - vec2)))

def Triangle_Affine_Trans(Triangle_dots_list):

    Triangle_dots_list_copy = deepcopy(Triangle_dots_list)
    # 寻找出最长边对应的顶点
    vertex_index0 = 0  # 最长边对应的顶点索引
    max_silde = 0  # 最长边长度
    for i in range(len(Triangle_dots_list_copy)):  # 循环遍历每个
        l = caculate_distance(Triangle_dots_list_copy[i-1], Triangle_dots_list_copy[i-2])
        print("索引：", i, "坐标点：", Triangle_dots_list_copy[i], "对应边长为：", l)
        if l > max_silde:
            max_silde = l
            vertex_index0 = i
    print("最长边索引为：", vertex_index0)

    # 根据角度选则变换的点
    vertex_index1 = Triangle_dots_list_copy.index(Triangle_dots_list_copy[vertex_index0 - 1])
    vertex_index2 = Triangle_dots_list_copy.index(Triangle_dots_list_copy[vertex_index0 - 2])

    P0 = Triangle_dots_list_copy[vertex_index0]
    P1 = Triangle_dots_list_copy[vertex_index1]
    P2 = Triangle_dots_list_copy[vertex_index2]

    d01 = caculate_distance(P0, P1)
    d02 = caculate_distance(P0, P2)

    theta1 = math.asin(abs(P0[1] - P1[1]) / d01)
    theta2 = math.asin(abs(P0[1] - P2[1]) / d02)

    if theta1 >= theta2:  # P1的角度大于P2的角度，则P2为竖直边
        # 进行变换,将P0P1竖直化
        P1[0] = P0[0]  # P1的横坐标与P0的横坐标相等
        P1[1] = P0[1] + (P1[1] - P0[1]) / abs((P1[1] - P0[1])) * d01

        P2[1] = P0[1]  # P2的纵坐标与P0的纵坐标相等
        P2[0] = P0[0] + (P2[0] - P0[0]) / abs((P2[0] - P0[0])) * d02

    else:
        # 进行变换,将P0P1竖直化
        P2[0] = P0[0]  # P1的横坐标与P0的横坐标相等
        P2[1] = P0[1] + (P2[1] - P0[1]) / abs((P2[1] - P0[1])) * d02

        P1[1] = P0[1]  # P2的纵坐标与P0的纵坐标相等
        P1[0] = P0[0] + (P1[0] - P0[0]) / abs((P1[0] - P0[0])) * d01

    # 进行旋转操作
    Center_Point = [(P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2]  # 矩形中心点
    P3 = [np.float32(2*Center_Point[0] - P0[0]), np.float32(2*Center_Point[1] - P0[1])]  # 矩形的另外一个点
    P0_Vec = [P0[0] - Center_Point[0], P0[1] - Center_Point[1]]  # P0与矩形中心点构成向量，用以检验位置

    angle = 0.0
    if P0_Vec[0] < 0 and P0_Vec[1] > 0:  # 顶点在第三象限，顺时针旋转90
        angle = -90.0
    elif P0_Vec[0] > 0 and P0_Vec[1] > 0:  # 顶点在第四象限，逆时针旋转90
        angle = 180.0
    elif P0_Vec[0] > 0 and P0_Vec[1] < 0:  # 顶点在第三象限，逆时针旋转90
        angle = 90.0

    return Triangle_dots_list_copy, angle, P3


def plot_data(dot_list):
    for i in range(len(dot_list)):
        plt.plot([dot_list[i][0], dot_list[i-1][0]],[dot_list[i][1], dot_list[i-1][1]], 'r')

    for item in dot_list:
        plt.text(item[0], item[1], "%s" % (item))


# dot_list = [[333.89777, 349.8475], [517.54877, 268.43903], [383.53424, 217.57533]]
# plt.subplot(1, 2, 1)
# plot_data(dot_list)
# new_dot_list, angle = Triangle_Affine_Trans(dot_list)
# plt.subplot(1, 2, 2)
# plot_data(new_dot_list)
# print(new_dot_list)
# plt.show()