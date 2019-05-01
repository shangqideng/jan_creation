import matplotlib.pyplot as plt
from PIL import Image
import pytesseract
import re
# import easygui
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def Area_Split(img, start_index, end_index, alpha=2, interval=2, ax=0):
    """
    :param img: 化成矩阵格式的图片
    :param start_index: 开始位置
    :param end_index: 结束为止
    :param alpha: 阈值分割
    :param ax: 0为按行,1为按列
    :return: 分割索引列表
    """
    index_list = []
    flag = 0
    start = 0
    for i in range(start_index, end_index):
        if ax == 1:  # 按列
            line = img[:, i:i + interval]
        else:
            line = img[i:i + interval, :]
        count = np.count_nonzero(line)
        if count >= alpha and flag == 0:  # 开始
            start = i
            flag = 1
        elif count < alpha and flag == 1:  # 结束
            end = i
            flag = 0
            index_list.append((start + end) / 2)

    return index_list
def exmatch(str1,str2):  #初步匹配
        n=0
        for i in range(len(str1)):
            for j in range(len(str2)):
                if str1[i]==str2[j]:
                    n +=1
        return n

def match(str1,list1):  #匹配
    t=0
    index = 0
    for i in range(len(list1)):
        if(exmatch(str1,list1[i])>t):
            t=exmatch(str1,list1[i])
            index=i
    return list1[index]

def cutter(list):
    img = Image.open(str)  # 打开当前路径图像
    box1 = (int(list[0]), int(list[1]),int(list[2]) ,int(list[3] ))  # 设置图像裁剪区域
    img1 = img.crop(box1)  # 图像裁剪
    return img1   #返回裁剪好的图片

def connect(list1):
    list=[]
    list.append(list1[0][0])
    list.append(list1[0][1])
    list.append(list1[2][0])
    list.append(list1[2][1])
    return list

def findnum(string):
    comp=re.compile(r'\d+')
    list_str=comp.findall(string)
    list_num=[]
    for item in list_str:
        item=int(item)
        list_num.append(item)
    price= int(list_num[0])
    return price

def scan(str_1):

    image = Image.open(str_1)
    h, w = image.size
    while h * w / 1024 / 1024 > 1:
        h, w = h * 0.9, w * 0.9
        size = h, w
        image.thumbnail(size, Image.ANTIALIAS)

    img = np.array(image, dtype='float')
    print(np.shape(img))

    # plt.imshow(img)
    # plt.show()

    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2]

    # 标准差
    x_ = (r + g + b) / 3
    std = (r - x_) * (r - x_) + (g - x_) * (g - x_) + (b - x_) * (b - x_)
    std = np.sqrt(std/3)
    mask_std = std > 7

    mask_1 = g > b
    mask_2 = g > r
    mask_3 = g > 0
    mask_color = np.logical_and(mask_1, mask_2)
    mask_color = np.logical_and(mask_color, mask_3)
    mask_color_std = np.logical_and(mask_color, mask_std)
    mask_not_color_std = np.logical_not(mask_color_std)

    img[:, :, 0][mask_not_color_std] = 0
    img[:, :, 1][mask_not_color_std] = 0
    img[:, :, 2][mask_not_color_std] = 0

    img[:, :, 0][mask_color_std] = 0
    img[:, :, 1][mask_color_std] = 255
    img[:, :, 2][mask_color_std] = 0

    new_img = img[:, :, 1]
    new_img = new_img / 255
    rows, cols = np.shape(new_img)

    # plt.imshow(new_img, cmap='Greys')
    # plt.show()

    vertical_index = Area_Split(new_img, 0, cols, alpha=100, interval=50, ax=1)
    # horizontal_index = Area_Split(new_img, 0, rows, alpha=20, interval=10, ax=0)

    # 垂直划分测试
    # for index in vertical_index:
    #     # plt.axvline(index, color='green')
    #     plt.axvline(index-40)
    #     plt.axvline(index+40)

    dot_list = []
    for v_index in vertical_index:
        start_index = v_index - 60
        end_index = v_index + 60
        # plt.imshow(new_img, cmap='Greys')
        # plt.axvline(start_index)
        # plt.axvline(end_index)
        horizontal_index = Area_Split(new_img[:, int(start_index):int(end_index)], 0, rows, alpha=20, interval=20, ax=0)
        for h_index in horizontal_index:
            # plt.axhline(h_index, color='blue')
            dot_list.append([v_index, h_index])
        # plt.show()

    v_bias = 40
    h_bias = 400
    border_list = []
    for dot in dot_list:
        plt.plot(dot[0], dot[1], '.r')
        p1 = [dot[0], dot[1]-v_bias]
        p2 = [dot[0], dot[1]+v_bias]
        p3 = [dot[0]+h_bias, dot[1]+v_bias]
        p4 = [dot[0]+h_bias, dot[1]-v_bias]
        p_list = [p1, p2, p3, p4]
        border_list.append(p_list)
        for i in range(len(p_list)):
            plt.plot([p_list[i-1][0], p_list[i][0]], [p_list[i-1][1], p_list[i][1]], 'b')
    plt.imshow(image)
    plt.show()
    print(border_list)


    # f = open('菜单.txt','r', encoding='UTF-8')
    list1=["牛油鸳鸯锅48元/份", "清油鸳鸯锅48元/份", "菌汤锅48元/份", "大骨汤百味锅48元/份",
                        "番茄锅48元/份", "清油红锅48元/份","牛油红锅48元/份","香油碟5元/份","香辣干碟3元/份",
                        "原汤碟4元/份", "金牌脆毛肚32元/份", "草原千层肚29/份", "麻辣牛肉26元/份", "鲜红苕粉8元/份",
                        "安格斯肥牛22元/份", "麻辣小郡肝22元/份", "荷包肉22元/份", "鲜鸭血8元/份", "果蔬鲜肉丸18元/份",
                        "五香郡把15元/份", "鸡翅尖6元/份", "鹌鹑蛋12元/份", "金牌牛黄喉26元/份", "精品猪黄喉28元/份",
                        "嫩滑牛肉24元/份", "霸王牛肉26元/份", "虾滑28元/份", "鲜鸭舌16元/份", "鸭郡花18元/份",
                        "去骨鸭掌18元/份", "宜宾小香肠16元/份", "鲜脑花8元/个", "鲜毛肚25元/份", "极品鳕鱼18元/份",
                        "肥肠节子3元/节", "极品耗儿鱼28元/份", "正大午餐肉12元/份", "海霸王虾饺12元/份", "三秒乌鱼片28元/份",
                        "黄辣丁15元/份", "雪花牛肉38元/份", "羊肉卷22元/份", "精选五花肉15元/份", "红酒腰片25元/份",
                        "霸王排骨28元/份", "美好火腿肠8元/份", "脆皮肠8元/份", "盐焗肚条24元/份", "无刺巴沙鱼26元/份",
                        "卤肥肠25元/份", "水晶土豆片", "藕片", "萝卜", "306冬瓜", "307黄瓜", "308豌豆尖", "309生菜",
                        "310大白菜", "311凤尾", "312折耳根", "313黄豆芽", "314豆皮", "315山药", "316鲜豆腐", "317木耳",
                        "318金针菇", "319香菇", "320青菜头", "321竹海笋片王", "322后切土豆", "501红糖糍粑", "502什锦蛋炒饭",
                        "503酿糟小汤圆", "504现炸酥肉", "505红糖冰粉", "506印度飞饼", "507八宝粥", "508酱油炒饭"]
    list_result=[]
    # for each_lines in f:
    #     line1=each_lines.replace('\n','')
    #     line2=line1.replace(' ','')
    #     list1.append(line2)

    for line in border_list:
        list2=connect(line)
        img = Image.open(str_1)  # 打开当前路径图像
        box1 = (int(list2[0]), int(list2[1]), int(list2[2]), int(list2[3]))  # 设置图像裁剪区域
        img1 = img.crop(box1)  # 图像裁剪
        aa=img1

        plt.imshow(aa)
        str3 = str(pytesseract.image_to_string(aa, lang='chi_sim'))
        str1 = str3.replace(' ', '')
        str4='识别结果:'+str1+'     匹配结果:'+match(str1, list1)+'\n'
        list_result.append(str4)
    print('识别结果', 'demo', list_result)
    return  list_result
