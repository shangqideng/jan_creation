from IMG_GPS import *

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


def Menu_Split(rot_dist):
    rot_dist_copy = deepcopy(rot_dist)  # 图层拷贝
    gray = cv2.cvtColor(rot_dist_copy, cv2.COLOR_BGR2GRAY)  # 转化为灰度图
    gray = cv2.GaussianBlur(gray, (3, 3), 0)  # 高斯去噪

    # 局部二值化
    block_size = 25
    const_value = 10
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, const_value)  # 局部二值化

    # 寻找轮廓
    binary, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 树形递归寻找轮廓
    contours_index = contours_filter(contours, hierarchy, 1, 120*220)  # 得到过滤后符合条件的轮廓索引
    # print("contours_index", contours_index)
    # for index in contours_index:  # 显示符合条件的轮廓
    #     cv2.drawContours(rot_dist_copy, contours, index, (255, 0, 0), 2)
    # plt.imshow(rot_dist_copy)
    # plt.show()

    contours_rect = []  # 存储菜单的最小包围矩阵
    contours_box = []
    for index in contours_index:  # 获得分块区域的最小包围矩阵
        rect = cv2.minAreaRect(contours[index])  # 最小矩阵包围
        contours_box.append(cv2.boxPoints(rect))
        contours_rect.append(rect)

    # # 仿射变换
    # # src_list, dst_list = Square_Affine_Trans(contours_rect)
    # Menu_dict = {}  # {(x, y):mat,(x, y):mat,...}
    # for i in range(len(contours_box)):
    #     src_list = contours_box[i][0:3].tolist()
    #     dst_list, angle, P3 = Triangle_Affine_Trans(src_list)
    #
    #     Max_rect_point_list = [dst_list[0], dst_list[1], dst_list[2], P3]
    #     # Max_rect = cv2.minAreaRect(np.array(dst_list, np.float32))
    #     Max_rect = cv2.minAreaRect(np.array(Max_rect_point_list, np.float32))  # 得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
    #     Max_box = cv2.boxPoints(Max_rect)
    #     # Max_box = np.int0(Max_box)
    #     # cv2.drawContours(rot_dist_copy, [Max_box], -1, (0, 255, 0), 2)
    #     # plt.imshow(rot_dist_copy)
    #     # plt.show()
    #
    #     x_min = np.min(np.array(dst_list)[:, 0]) - np.float32(5)  # x_min用以修正放射变换图片水平位置（值越大，图像向左移）
    #     y_min = np.min(np.array(dst_list)[:, 1]) - np.float32(5)  # y_min用以修正放射变换图片垂直位置（值越大，图像向上移）
    #     dst_list_shifft = [[item[0] - x_min, item[1] - y_min] for item in dst_list]  # 修正仿射变换终点信息
    #
    #     cutter_width = int(np.max(np.array(Max_box)[:, 0]) - np.min(np.array(Max_box)[:, 0])) + 10  # 菜单的宽
    #     cutter_height = int(np.max(np.array(Max_box)[:, 1]) - np.min(np.array(Max_box)[:, 1])) + 10  # 菜单的高
    #     # warp_mat = cv2.getPerspectiveTransform(np.array(src_list[i], np.float32), np.array(dst_list_shifft, np.float32))
    #     # warp_dist = cv2.warpPerspective(rot_dist_copy, warp_mat, tuple([cutter_width, cutter_height]))  # 经过仿射变换后的图像
    #     warp_mat = cv2.getAffineTransform(np.array(src_list, np.float32), np.array(dst_list_shifft, np.float32))
    #     src_x = np.min(np.array(src_list)[:, 0])
    #     src_y = np.min(np.array(src_list)[:, 1])
    #     warp_dist = cv2.warpAffine(rot_dist_copy, warp_mat, tuple([cutter_width, cutter_height]))  # 经过仿射变换后的图像
    #     Menu_dict[(src_x, src_y)] = warp_dist
    #     # plt.imshow(warp_dist)
    #     # plt.show()
    # Menu_Dict_Sorted = sorted(Menu_dict.items(), key=lambda x: (x[0][0], x[0][1]))  # 根据键排序
    # Menu_List = [item[1] for item in Menu_Dict_Sorted]

    # 旋转变换
    Menu_dict = {}  # {(x, y):mat,(x, y):mat,...}
    for i in range(len(contours_box)):
        # rotate_box = rotate_bound(contours_box[i], 90+contours_rect[i][-1])
        xs = [item[0] for item in contours_box[i]]
        ys = [item[1] for item in contours_box[i]]
        x1 = int(min(xs))
        x2 = int(max(xs))
        y1 = int(min(ys))
        y2 = int(max(ys))
        cropImg = deepcopy(rot_dist_copy[y1:y2, x1:x2])
        # roate_img = rotate_bound(cropImg, 90+contours_rect[i][-1])
        # cropImg = rotate_bound(cropImg, 90+contours_rect[i][-1])
        # cropImg = roate_img[y1:y2, x1:x2]
        Menu_dict[(x1, y1)] = cropImg
        # plt.imshow(cropImg)
        # plt.show()
    Menu_Dict_Sorted = sorted(Menu_dict.items(), key=lambda x: (x[0][0], x[0][1]))  # 根据键排序
    print("菜单子区域为", len(Menu_Dict_Sorted))
    final_part = []

    # 第一部分
    first_part = sorted(Menu_Dict_Sorted[0:3], key=lambda x: x[0][1])
    final_part.extend(first_part)
    # 第二部分
    second_part = Menu_Dict_Sorted[3:4]
    final_part.extend(second_part)
    # 第三部分
    third_part = sorted(Menu_Dict_Sorted[4:], key=lambda x: x[0][1])
    final_part.extend(third_part)

    Menu_List = [item[1] for item in final_part]
    # print(Menu_List)
    # for menu in Menu_List:
    #     plt.imshow(menu)
    #     plt.show()

    # cv2.namedWindow('binary', 0)
    # cv2.imshow('binary', binary)
    # cv2.namedWindow('contours', 0)
    # cv2.imshow('contours', rot_dist_copy)
    # # cv2.namedWindow("img", 0)
    # plt.imshow(gray)
    # plt.show()
    # cv2.waitKey(0)
    return Menu_List



# img = cv2.imread('./data/010.jpg')  # 读取图片
# rot_dist = Find_Content(img)
# Menu_List = Menu_Split(rot_dist)