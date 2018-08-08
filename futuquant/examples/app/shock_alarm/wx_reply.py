# -*- coding: utf-8 -*-
# filename:
from flask import Flask, request, make_response
import time, hashlib
from receive_and_reply import reply
from receive_and_reply import receive
from mysql_interface import mysql_interface
import common_parameter

mi = mysql_interface()

app = Flask(__name__)

@app.route('/wx_flask', methods=['GET', 'POST'])
def wechat():
    # 微信验证token
    if request.method == 'GET':
        token = common_parameter.token
        query = request.args
        signature = query.get('signature', '')
        timestamp = query.get('timestamp', '')
        nonce = query.get('nonce', '')
        echostr = query.get('echostr', '')
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        if hashlib.sha1(s).hexdigest() == signature:
            return make_response(echostr)
    else:
        rec_msg = receive.parse_xml(request.stream.read())

        if rec_msg.MsgType == 'text':
            content = rec_msg.Content.decode('utf-8')
            if content.startswith(u"设置", 0, 2):
                mi.update_threshold(rec_msg.FromUserName, content)
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName, rec_msg.ToUserName,("设置成功 \n %s"%getTime()))
                return rep_text_msg.send()
            elif content.startswith(u"订阅", 0, 3):
                mi.update_stockid()    # 未设置
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName, rec_msg.ToUserName, ("订阅成功 \n %s" % getTime()))
                return rep_text_msg.send()
            else:
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName,rec_msg.ToUserName,"我来学你说：%s \n %s"%(content,getTime()))
                return rep_text_msg.send()
        elif  rec_msg.MsgType =="image":
            rep_img_msg = reply.ImageMsg(rec_msg.FromUserName,rec_msg.ToUserName,rec_msg.MediaId)
            return rep_img_msg.send()
        else:
            return "success"

#获取时间戳
def getTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

app.run(host='0.0.0.0', port=80, debug=True)
