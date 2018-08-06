# -*- coding: utf-8 -*-
# filename:
from flask import Flask, request, make_response
import time, hashlib
from receive_and_reply import reply
from receive_and_reply import receive
from mysql_interface import MysqlInterface
import common_parameter

mi = MysqlInterface()

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
        if hashlib.sha1(s.encode('utf-8')).hexdigest() == signature:
            return make_response(echostr)
    else:
        rec_msg = receive.parse_xml(request.stream.read())

        if rec_msg.MsgType == 'text':
            content = rec_msg.Content.decode('utf-8')
            if content.startswith(u"设置", 0, 2):
                mi.update_threshold(rec_msg.FromUserName, content)
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName, rec_msg.ToUserName, ("设置成功 \n %s" % get_time()))
                return rep_text_msg.send()
            else:
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName, rec_msg.ToUserName, ("回复格式（设置 越价率 越价大单值 大单值 一分钟内提醒次数上限），如：\n设置 0.005 1000000 4000000 10\n\n %s" % get_time()))
                return rep_text_msg.send()

        elif rec_msg.MsgType =="image":
            rep_img_msg = reply.ImageMsg(rec_msg.FromUserName,rec_msg.ToUserName,rec_msg.MediaId)
            return rep_img_msg.send()
        else:
            return "success"


# 获取时间戳
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


app.run(host='0.0.0.0', port=80, debug=True)
