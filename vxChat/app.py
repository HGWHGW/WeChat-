from threading import Thread

from flask import Flask, render_template, request

import back
from back import start_app

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_receiver', methods=['POST'])
def set_receiver():
    receiver = request.form['receiver']
    back.set_receiver(receiver)
    # 在这里调用后端的函数，将receiver传递给后端
    return 'success set receiver:'+back.receiver  # 返回给前端的响应


@app.route('/toggle_transport', methods=['POST'])
def toggle_transport():
    # 在这里调用后端的函数，切换isTransport的值
    back.set_transport()
    return 'success toggle transport:'+str(back.isTransport)  # 返回给前端的响应

@app.route('/start_login', methods=['POST'])
def start_login():
    Thread(target=start_app, args=(login_callback,)).start()
    return '登录中...'

def login_callback(status):
    if status == "success":
        # print("接收到登陆成功状态！")
        return "登录成功！"
    elif status == "failed":
        return "登录失败，请重新登录！"

if __name__ == '__main__':
    app.run(debug=True)

# flask run --port 4999