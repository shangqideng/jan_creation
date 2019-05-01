import cv2
from Dot_Affine_Trans import *


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def Find_Content(img):
    """
    寻找目标区域
    :param img: cv2格式导入的图片
    :return: 目标区域的矩阵(numpy.ndarray)
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转化为灰度图
    # 高斯去噪
    gray = cv2.GaussianBlur(gray, (9, 9), 2)  # 高斯去噪
    # ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # otsu滤波，二值化
    block_size = 85
    const_value = 30
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size,
                                 const_value)  # 局部二值化
    # plt.title("binary")
    # plt.imshow(binary, cmap='Greys')
    # plt.show()
    # 寻找轮廓,binary为二值图，contours为轮廓列表，hierarchy为轮廓关系
    binary, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 寻找轮廓深度等于2的轮廓
    contours_index = []  # 轮廓索引列表
    for i in range(len(hierarchy[0])):  # 寻找子轮廓深度等于2的轮廓

        count = 0
        a = hierarchy[0][i][2]
        while a != -1:
            count += 1
            a = hierarchy[0][a][2]
        if count >= 2:
            contours_index.append(i)
    print("contours index", contours_index)  # 轮廓索引

    # cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    # for index in contours_index:
    #     cv2.drawContours(img, contours, index, (255, 0, 0), 2)
    # plt.imshow(img)
    # plt.show()


    # 对于轮廓等于3的轮廓进行过滤，找出需要识别的轮廓
    filtered_contours_index = []
    fiter_delta = 1
    d_delta = 10
    print("|------------------------------进行轮廓过滤------------------------------|")
    print("在比例误差小于%s的情况下，应满足 1级:2级=%.4f，2级:3级=%.4f" % (fiter_delta, 7/5, 5/3))
    for index in contours_index:  # 检测轮廓是否为二维码轮廓
        rect1 = cv2.minAreaRect(contours[index])  # 最小矩阵包围
        index2 = hierarchy[0][index][2]
        rect2 = cv2.minAreaRect(contours[index2])  # 第二级轮廓
        index3 = hierarchy[0][index2][2]
        rect3 = cv2.minAreaRect(contours[index3])  # 第三级轮廓

        distance1 = caculate_distance(rect1[0], rect2[0])
        distance2 = caculate_distance(rect2[0], rect3[0])
        distance3 = caculate_distance(rect1[0], rect3[0])
        d_error = (distance1 + distance2 + distance3) / 3
        try:
            ration_1 = rect1[1][0] / rect2[1][0]
            ration_2 = rect2[1][0] / rect3[1][0]
            result = "12级不符合"
            if abs(ration_1 - float(7 / 5)) <= fiter_delta:  # 如果一二级轮廓满足比例误差不超过0.2
                result = "23级不符合"
                if abs(ration_2 - float(5 / 3)) <= fiter_delta:  # 如果二三级轮廓满足比例误差不超过0.2
                    if d_error < d_delta:
                        filtered_contours_index.append(index)  # 确认为二维码轮廓并添加进过滤轮廓索引列表中
                        cv2.drawContours(img, contours, index, (255, 0, 0), 2)
                        cv2.drawContours(img, contours, index2, (0, 255, 0), 2)
                        cv2.drawContours(img, contours, index3, (0, 0, 255), 2)
                        result = "符合"
            print("索引为", index, "3级轮廓边长为：", "1:", rect1[1][0], "2:", rect2[1][0], "3:", rect3[1][0],
                  "比例分别为 1级:2级=", rect1[1][0] / rect2[1][0], "2级:3级=", rect2[1][0] / rect3[1][0], result,
                  "中心平均距离为", d_error)
        except:
            print("Index %s Error: there are some contours's length equal to zero" % index, "1:", rect1[1][0], "2:", rect2[1][0], "3:", rect3[1][0])
        # print("3:", rect3[1][0])
    print("filtered contours ", filtered_contours_index)
    # plt.imshow(img)
    # plt.show()

    print("|------------------------------进行仿射变换------------------------------|")
    if len(filtered_contours_index) == 3:  # 如果最终定位点满足所需定位点要求

        box_list = []  # 分别存储三个定位矩形的四个顶点
        Src_List = []  # 存储三个定位矩形的中心
        max_x = 0  # x最大偏移量，用以修正仿射变换后图片的位置
        max_y = 0  # y最大偏移量，用以修正仿射变换后图片的位置
        for index in filtered_contours_index:  # 获得定位处矩形
            rect = cv2.minAreaRect(contours[index])
            if rect[1][0] > max_x:
                max_x = rect[1][0]
            if rect[1][1] > max_y:
                max_y = rect[1][1]
            box = cv2.boxPoints(rect)
            box_list.append(box)
            # for item in box:
            #     plt.plot(item[0], item[1], '.r')
            # plt.plot(np.mean(box, 0)[0], np.mean(box, 0)[1], '.g')
            Src_List.append([np.mean(box, 0)[0], np.mean(box, 0)[1]])
        print("Src_List", Src_List)
        Dst_List, angle, P3 = Triangle_Affine_Trans(Src_List)  # 仿射变换目标点以及角度以及第四个点
        print("Dst_List", Dst_List)
        print("Angel", angle)
        print("max_x", max_x, "max_y", max_y)

        # 根据三个定位点将矩形包围起来
        Max_rect_point_list = [Dst_List[0], Dst_List[1], Dst_List[2], P3]
        Max_rect = cv2.minAreaRect(np.array(Max_rect_point_list))  # 得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
        # # 画图最最小包围矩形
        Max_box = cv2.boxPoints(Max_rect)
        # Max_box = np.int0(Max_box)
        # cv2.drawContours(img, [Max_box], 0, (255, 0, 0), 3)
        # plt.imshow(img)
        # plt.show()

        x_min = np.min(np.array(Max_box)[:, 0]) - np.float32(max_x / 2) - np.float32(5)  # x_min用以修正放射变换图片水平位置（值越大，图像向左移）
        y_min = np.min(np.array(Max_box)[:, 1]) - np.float32(max_y / 2) - np.float32(5)  # y_min用以修正放射变换图片垂直位置（值越大，图像向上移）

        Dst_List_shifft = [[item[0] - x_min, item[1] - y_min] for item in Dst_List]  # 修正仿射变换终点信息
        print("Dst_List_shifft", Dst_List_shifft)

        # cutter_width = int(Max_rect[1][1] + max_x) + 10  # 菜单的宽
        # cutter_height = int(Max_rect[1][0] + max_y) + 10
        cutter_width = int(np.max(np.array(Max_box)[:, 0]) - np.min(np.array(Max_box)[:, 0]) + max_x) + 10  # 菜单的宽
        cutter_height = int(np.max(np.array(Max_box)[:, 1]) - np.min(np.array(Max_box)[:, 1]) + max_y) + 10  # 菜单的高
        print(Max_rect)
        print("width: %.4f, height: %.4f" % (cutter_width, cutter_height))

        # 进行仿射变换
        warp_mat = cv2.getAffineTransform(np.array(Src_List), np.array(Dst_List_shifft))
        warp_dist = cv2.warpAffine(img, warp_mat, tuple([cutter_width, cutter_height]))  # 经过仿射变换后的图像

        # 对图像进行旋转
        rot_dist = rotate_bound(warp_dist, angle)

        # plt.subplot(1, 2, 1)
        # plt.imshow(img)
        # plt.title('original')
        # plt.subplot(1, 2, 2)
        # plt.imshow(rot_dist)
        # plt.title('find QRcode')
        # cv2.waitKey(0)
        # plt.show()

        return rot_dist
    else:
        return len(filtered_contours_index)

# img = cv2.imread('./data/007.jpg')  # 读取图片
# rot_dist = Find_Content(img)