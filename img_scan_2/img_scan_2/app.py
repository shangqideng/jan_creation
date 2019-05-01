import os
from flask import Flask,render_template, request, redirect,url_for
import json
from Menu_Recognition import Menu_Recognition
app = Flask(__name__)
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


@app.route('/')
def hello_world():
    return 'Hello World!'


def create_full_name(file_name):
    """
    :param file_name: 上传的文件名
    :return: 存储在本地的绝对路径
    """
    base_path = os.path.dirname(__file__)  # 当前文件所在路径
    upload_path = os.path.join(base_path, 'static', 'uploads')
    if not os.path.exists(upload_path):
        os.mkdir(upload_path)
    full_name = os.path.join(upload_path, file_name)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路

    return full_name


@app.route('/img_upload', methods=['get', 'post'])
def img_upload():
    resp = {'status': True, 'data': None, 'msg': None}
    if request.method == 'POST':
        f = request.files['file']
        image = Image.open(f)
        img = np.array(image)
        print("图片大小", np.shape(img))
        # plt.imshow(img)
        # plt.show()
        # full_name = create_full_name(f.filename)
        # f.save(full_name)  # 保存上传的文件
        # ----这里调用你的服务-----
        resp['data'] = Menu_Recognition(img)
        # -----------------------
    # 返回结果
    else:
        resp['status'] = False
        resp['msg'] = '不支持get提交！请使用post'
    print(resp)


    return json.dumps(resp)


# 测试页面转发
@app.route('/test')
def test_render():
    return render_template('img_upload.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)


# 说明：
# 1.启动：
# 先安装requirements.txt里的依赖库， 在服务器端可以使用 pip3 -r requirements.txt 进行批量安装
# 运行app.py
# 2.调用脚本：
# 脚本里的代码需要再封装一下： 入参是图片绝对路径， 返回是处理的结果， 返回结果建议用字典存储，在使用json.dumps()转为字符串返回给app
# app对返回的json数据进行解析，在展示
# 然后在上面的注释里面调用你的脚本就好了

# 注意：
# 这里没有对上传的文件进行限制。。。 如需要请自行添加哈