from Menu_Split import *
from SVM_Deal import *
import shutil
from Submenu_Deal_padding import *
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import os
import re

def Save_Image(img_list, save_path):
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    file_list = os.listdir(save_path)
    start_index = len(file_list)
    for img in img_list:
        cv2.imwrite(save_path + '/%s.jpg' % start_index, img)
        start_index += 1

def findnum(string):
    comp=re.compile(r'\d+')
    list_str=comp.findall(string)
    list_num=[]
    for item in list_str:
        item=int(item)
        list_num.append(item)
    price= int(list_num[0])
    return price

def Menu_Recognition(img):

    # img = cv2.imread('./data/020.jpg')  # 读取图片

    start_time = time.time()
    rot_dist = Find_Content(img)  # 找到菜单部分


    if isinstance(rot_dist, int):  # 如果返回值是数字
        print("\033[31mError: the length of filtered_contours is %d, not 3.\033[0m" % rot_dist)
        return "Not Found The Position"
    else:
        print("Original Shape", np.shape(rot_dist))  # 将图片固定到1200*900的大小
        width = 1500
        rot_dist = cv2.resize(rot_dist, (int(width * np.shape(rot_dist)[1] / np.shape(rot_dist)[0]), width))
        print("Image Shape", np.shape(rot_dist))
        end_time = time.time()
        print("rot_dist time------>", end_time-start_time)

        start_time = time.time()
        Menu_List = Menu_Split(rot_dist)  # 进行区域划分Menu_List[mat1, mat2, mat3, mat4. mat5, mat6]
        end_time = time.time()
        print("Menu_Split time------>", end_time - start_time)

        if len(Menu_List) != 6:
            print("\033[31mWarning:Menu should be divided 6 but just return %s.\033[0m" % len(Menu_List))  # 提示信息
            return "Submenu Lose: Should be 6 but only return %s" % len(Menu_List)
        else:
            start_time = time.time()
            Horizontal_Mat_List = []  # 存取每一个区域的List
            Mark_Mat_List = []
            Mark_Position_List = [[22, 65], [32, 75], [22, 65], [22, 58], [22, 58], [22, 62]]  # 6个区域的坐标
            Mark_Num_List = [9, 3, 8, 32, 22, 8]
            Sum = 0
            for i in range(len(Menu_List)):
                Horizontal_Mat, Mark_Mat = Submenu_Deal_Padding(Menu_List[i], i, Mark_Position_List)
                Horizontal_Mat_List.append(Horizontal_Mat)  # [h1_list, h2_list,.....]
                Mark_Mat_List.append(Mark_Mat)  # [mark1_list, mark2_list,.....]
                print("Mat Length---->", len(Mark_Mat))
                Sum += len(Mark_Mat)
                if len(Mark_Mat) != Mark_Num_List[i]:
                    print("\033[31mData Lose Warning: There Should be %s pieces, but find %s\033[0m" % (Mark_Num_List[i], len(Mark_Mat)))
            print("Sum ---------->", Sum)
            end_time = time.time()
            print("Horizontal_Mat time----------->", end_time-start_time)
            Checked_Content = SVM_Deal(Mark_Mat_List)
            print(len(Checked_Content))
            # for item in Checked_Content:
            #     print(item)
            print('################################################')
            sumprice = 0
            for item in Checked_Content:
                sumprice += findnum(item[2])
            Checked_Content.append('总计%s道菜,总价为%s元'%(len(Checked_Content),sumprice))
            return Checked_Content

if __name__ == '__main__':
    start_time = time.time()
    file_name = './data/018.jpg'
    img = cv2.imread(file_name)  # 读取图片
    Checked_Content = Menu_Recognition(img)
    end_time = time.time()
    print("Total Time--------->", end_time-start_time)

