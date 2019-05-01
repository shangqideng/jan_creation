import cv2
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
from sklearn.cluster import KMeans


def contours_filter(contours, hierarchy, series, area):
    # 寻找轮廓级数等于series的轮廓
    contours_index = []  # 轮廓索引列表
    for i in range(len(hierarchy[0])):  # 寻找轮廓级数等于series的轮廓

        count = 0
        a = hierarchy[0][i][3]
        while a != -1:
            count += 1
            a = hierarchy[0][a][3]
        if count == series:
            if cv2.contourArea(contours[i]) >= area:
                contours_index.append(i)

    return contours_index

def Outlier_KMeans(data):
    samples = [[i] for i in data]
    model = KMeans(n_clusters=3)
    model.fit(samples)

    norm = np.where(model.cluster_centers_ == min(model.cluster_centers_))[0][0]
    crest_index_list = []
    for i in range(len(model.labels_)):
        if model.labels_[i] != norm:
            plt.plot(i, data[i], '.r')
            crest_index_list.append(i)
        else:
            plt.plot(i, data[i], '.b')

    return crest_index_list


def Rects_Grouping(rect_list):
    """
    对所有矩形框进行分组
    :param rect_list: 需要分组的rect的列表rect_list[rect[x,y,w,h],[x,y,w,h],...]
    :return: 
    """
    ys = np.array([rect[1] for rect in rect_list])  # 提取出所有rect的纵坐标为分组做准备
    ys_index = np.argsort(ys)  # 存储ys经过排序过后的索引
    rect_list_sorted = np.array(rect_list)[ys_index]  # 排序过后的rect
    ys_sorted = ys[ys_index]  # 经过排序过后的ys(从小到大)
    interval = ys_sorted[-1] - ys_sorted[0]  # 组距
    ys_sorted_standard = (ys_sorted - ys_sorted[0]) / interval  # 标准化
    ys_sorted_standard_diff = np.diff(ys_sorted_standard)  # 进行差分，即求导

    # # 显示波峰
    x = [i for i in range(len(ys_sorted_standard_diff))]
    plt.plot(x, ys_sorted_standard_diff)


    # 根据波峰分组
    rect_list_grouped = []
    crest_index_list = Outlier_KMeans(ys_sorted_standard_diff)  # 波峰顶点的坐标
    print("crest_index_list", crest_index_list)

    # plt.show()
    start = 0
    print("crest_index_list", crest_index_list)
    print("length", len(rect_list_sorted))
    for index in crest_index_list:
        print(start, "->", index+1)
        if len(rect_list_sorted[start:index+1]) > 1:  # 确保分组里面不只包含波峰本身
            rect_list_grouped.append(rect_list_sorted[start:index+1])
        start = index + 1
    if len(rect_list_sorted[start:]) > 1:  # 最后一组加入
        rect_list_grouped.append(rect_list_sorted[start:])


    # 将每一组的区域找到
    mark_group_list = []
    group_area_rect = []  # 每一组的区域rect存储[pt1, pt2]
    for group in rect_list_grouped:
        x_min_index = np.where(group[:, 0] == np.min(group[:, 0]))[0][0]  # 找出最小x所在坐标
        x_max_index = np.where(group[:, 0] == np.max(group[:, 0]))[0][0]  # 找出最大x所在坐标
        mark_group_list.append(group[x_min_index])  # 将第一个框作为mark的默认框添加
        x_min = group[x_min_index][0]  # 一个组中x的最小值
        y_min = group[x_max_index][1]  # 一个组中最大值x对应的y
        x_max = group[x_max_index][0] + group[x_max_index][2]  # 一个组中x的最大值
        y_max = y_min + group[x_max_index][3]
        group_area_rect.append([[x_min, y_min], [x_max, y_max]])
        # cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)


    # 校正所有区域
    group_area_rect = np.array(group_area_rect)
    x_min = np.min(group_area_rect[:, 0, 0])
    x_max = np.max(group_area_rect[:, 1, 0])
    for i in range(len(group_area_rect)):
        group_area_rect[i][0][0] = x_min
        group_area_rect[i][1][0] = x_max
        # cv2.rectangle(img, tuple(group_area_rect[i][0]), tuple(group_area_rect[i][1]), (0, 255, 0), 2)
    # plt.imshow(img)
    # plt.show()

    # print(ys_sorted_standard)
    # print(ys_sorted_standard_diff)
    # print(sorted(ys_sorted_standard_diff))



    return group_area_rect


def Submenu_Deal_Padding(menu, Position_index, Mark_Position_List):
    menu_copy = deepcopy(menu)
    # menu_copy = cv2.resize(menu_copy, (int(np.shape(menu_copy)[0]*0.5), int(np.shape(menu_copy)[1]*0.5)))
    gray = cv2.cvtColor(menu_copy, cv2.COLOR_BGR2GRAY)

    # 采用局部二值化
    block_size = 85
    const_value = 30
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size,
                                   const_value) # 局部二值化

    # 利用形态学操作找到定位
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=4)  # 闭操作
    # opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)  # 开操作
    # closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)  # 闭操作
    # opened = cv2.dilate(edges, kernel, iterations=3)

    # plt.subplot(1, 2, 1)
    # plt.imshow(edges, cmap="Greys")
    # plt.title('Canny')
    # plt.subplot(1, 2, 2)
    # plt.imshow(closed, cmap="Greys")
    # plt.title('Closed')
    # plt.show()


    # 进行间距填充
    for i in range(np.shape(closed)[0]):
        if np.count_nonzero(closed[i]) / np.shape(closed)[1] > 0.15:
            closed[i] = 255
        else:
            closed[i] = 0

    # plt.imshow(closed, cmap="Greys")
    # plt.title('Closed')
    # plt.show()
    binary, contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    filtered_contours = contours_filter(contours, hierarchy, 0, 3*np.shape(binary)[1])  # 过滤轮廓
    # color_list = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    # for index in filtered_contours:
    #     cv2.drawContours(menu_copy, contours, index, color_list[index % 3], 2)
    # plt.title('Closed1')
    # plt.imshow(menu_copy)
    # plt.show()


    horizontal_mat_dict = {}  # 存储每一行的mat
    for i in range(1, len(filtered_contours)-1):  # 提取文字所在行rect
        epsilon = 0.001 * cv2.arcLength(contours[filtered_contours[i]], True)
        approx = cv2.approxPolyDP(contours[filtered_contours[i]], epsilon, True)
        rect = cv2.boundingRect(approx)  # 矩形补齐
        bias = 5
        top = int(rect[1]-bias)
        bottom = int(rect[1]+rect[3]+bias)
        left = int(rect[0])
        right = int(rect[0]+rect[2])
        mat = deepcopy(menu_copy[top:bottom, left:right])
        horizontal_mat_dict[(rect[0], rect[1])] = mat
    horizontal_dict_sorted = sorted(horizontal_mat_dict.items(), key=lambda x: x[0][1])  # 根据y值进行排序
    horizontal_mat_list = [item[1] for item in horizontal_dict_sorted]

    # # 显示水平切割区域
    # for i in range(len(horizontal_mat_list)):
    #     cv2.namedWindow("%s" % (i+1), 0)
    #     cv2.imshow("%s" % (i+1), horizontal_mat_list[i])
    #
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    mark_mat_list = []
    for i in range(len(horizontal_mat_list)):
        # 进列间距填充
        h_gray = cv2.cvtColor(horizontal_mat_list[i], cv2.COLOR_BGR2GRAY)
        # 采用Canny算子滤波并提取边缘
        # h_binary = cv2.Canny(h_gray, 100, 100, apertureSize=3)
        # plt.imshow(h_binary)
        # plt.show()
        h_block_size = 155
        h_const_value = 25
        h_binary = cv2.adaptiveThreshold(h_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, h_block_size,
                                         h_const_value)  # 局部二值化
        h_closed = cv2.morphologyEx(h_binary, cv2.MORPH_CLOSE, kernel, iterations=4)  # 闭操作

        for j in range(np.shape(h_closed)[1]):
            if np.count_nonzero(h_closed[:, j]) / np.shape(h_closed)[0] > 0.5:
                h_closed[:, j] = 255
            else:
                h_closed[:, j] = 0
        # if Position_index != 4:
        #     pass
        # else:
        #     plt.subplot(1, 2, 1)
        #     plt.title('binary')
        #     plt.imshow(h_binary)
        #     plt.subplot(1, 2, 2)
        #     plt.title('h_closed')
        #     plt.imshow(h_closed)
        #     plt.show()

        _, h_contours, h_hierarchy = cv2.findContours(h_closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(horizontal_mat_list[i], h_contours, len(h_contours)-1, (0, 255, 0), 2)
        # print("h_contours", h_contours)
        rect = cv2.boundingRect(h_contours[-1])
        x_min = rect[0]

        mark_x1 = int(x_min + Mark_Position_List[Position_index][0])
        mark_y1 = rect[1]
        mark_x2 = int(x_min + Mark_Position_List[Position_index][1])
        mark_y2 = int(rect[1]+rect[3])
        # cv2.rectangle(horizontal_mat_list[i], (mark_x1, mark_y1), (mark_x2, mark_y2), (255, 0, 0), 2)
        #
        # cv2.namedWindow("%s" % i, 0)
        # cv2.imshow("%s" % i, horizontal_mat_list[i])
        mark_mat = deepcopy(horizontal_mat_list[i][mark_y1:mark_y2, mark_x1:mark_x2])
        mark_mat_list.append(mark_mat)

        # cv2.imshow("%s" % i, mark_mat)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return horizontal_mat_list, mark_mat_list

