# 实现消息转发
import os
import time
from re import search
import itchat
from itchat.content import *
import platform

# 需要安装itchat-uos 版本为1.5.0.dev0
# AttributeError: module 'itchat' has no attribute 'content' 解决：from itchat.content import *

msg_info = {}
isTransport = False #是否转发消息
receiver = None
# 调用platform库判断操作系统，用于登陆操作
# if platform.platform()[:7] == 'Windows':
#     itchat.login(enableCmdQR=False)
# else:
#     itchat.login(enableCmdQR=True)


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    return


@itchat.msg_register([itchat.content.TEXT, itchat.content.PICTURE, itchat.content.FRIENDS, itchat.content.CARD,
                      itchat.content.MAP, itchat.content.SHARING, itchat.content.RECORDING], isFriendChat=True,
                     isMpChat=False, isGroupChat=True)
def handleRmsg(msg):
    # 获取接收消息的时间并将时间字符串格式化
    msg_time_receive = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 获取发信人信息
    try:
        msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']
    except:
        msg_from = 'WeChat Official Accounts'
    # 获取发信时间
    msg_time_send = msg['CreateTime']
    # 获取信息ID
    msg_id = msg['MsgId']
    # 消息内容 置空
    msg_content = None
    # link 置空
    msg_link = None
    if msg['Type'] == 'Text' or msg['Type'] == 'Friends':
        msg_content = msg['Text']
    elif msg['Type'] == 'Attachment' or msg['Type'] == 'Video' or msg['Type'] == 'Picture' or msg[
        'Type'] == 'Recording':
        msg_content = msg['FileName']
        msg['Text'](str(msg_content))
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_link = msg['Url']
    else:
        msg_content = 'others'
    msg_info.update(
        {
            msg_id: {
                "msg_from": msg_from,
                "msg_time_send": msg_time_send,
                "msg_time_receive": msg_time_receive,
                "msg_type": msg["Type"],
                "msg_content": msg_content,
                "msg_link": msg_link
            }
        }
    )
    if isTransport:
        print(isTransport)
        recall_msg = msg_info.get(msg_id)
        msg_prime = '---' + recall_msg.get('msg_from') + '发送：' + '消息类型：' + recall_msg.get('msg_type') + '\n' \
            '时间：' + recall_msg.get(
            'msg_time_receive') + '\n' \
            '内容：' + recall_msg.get('msg_content')
        if recall_msg['msg_type'] == 'Sharing':
            msg_prime += '\n链接：' + recall_msg.get('msg_link')
        itchat.send_msg(msg_prime, toUserName=itchat.search_friends(name=receiver)[0]['UserName'])
        print(receiver)


# 再次注册NOTE即通知类型
@itchat.msg_register(itchat.content.NOTE, isFriendChat=True, isGroupChat=True, isMpChat=True)
def monitor(msg):
    if '撤回了一条消息' in msg['Content']:
        # 此处\<msgid\>(.*?)\<\/msgid\>的原因是，如果将msg['Content']打印出来，会在其中得到含有\<msgid\> \<\/msgid\>的一段信息
        # 而（.*?）则是正则表达式，用于匹配其中的任意字符串
        # 同时，group(1)表示从第一个左括号处开始匹配
        recall_msg_id = search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
        recall_msg = msg_info.get(recall_msg_id)
        print('[Recall]: %s' % recall_msg)
        msg_prime = '---' + recall_msg.get('msg_from') + '撤回了一条消息---\n' \
                                                         '消息类型：' + recall_msg.get('msg_type') + '\n' \
                                                                                                    '时间：' + recall_msg.get(
            'msg_time_receive') + '\n' \
                                  '内容：' + recall_msg.get('msg_content')
        if recall_msg['msg_type'] == 'Sharing':
            msg_prime += '\n链接：' + recall_msg.get('msg_link')
        # 向文件助手发送消息
        itchat.send_msg(msg_prime, toUserName='filehelper')
        if recall_msg['msg_type'] == 'Attachment' or recall_msg['msg_type'] == "Video" or recall_msg[
            'msg_type'] == 'Picture' or recall_msg['msg_type'] == 'Recording':
            file = '@fil@%s' % (recall_msg['msg_content'])
            itchat.send(msg=file, toUserName='filehelper')
            os.remove(recall_msg['msg_content'])# 删除本地暂存的撤回文件
        msg_info.pop(recall_msg_id)

def set_receiver(text):
    global receiver
    receiver = text

def start_app(callback):
    # print("开始登陆...")
    itchat.auto_login()
    # print("登陆成功！")
    callback("success")  # 向前端发送状态
    itchat.run()
    # print("已经开始运行 WeChat Helper 后端...")


def set_transport():
    global isTransport
    isTransport = not isTransport
