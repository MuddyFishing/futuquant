# -*- coding: utf-8 -*-
# filename:
from flask import Flask, request, make_response
import time, hashlib
from receive_and_reply import reply
from receive_and_reply import receive
from sqlite_interface import SqliteInterface
from Config import Config

sqlite = SqliteInterface()
config = Config()
app = Flask(__name__)

# 存储openid: [new_parameter_list, active_time]
new_setting_cache = {}


def make_sure(openid, content):
    global new_setting_cache
    now_time = time.time()
    if now_time <= new_setting_cache[openid][1]:
        if content.lower() == 'y':
            parameter_list = new_setting_cache[openid][0]
            sqlite.update_setting(openid, parameter_list)
            new_setting_cache.pop(openid)

            parameter_list_str = ''
            for p in parameter_list:
                parameter_list_str += str(p) + ' '

            return "确认成功，您的设置为：\n{0}".format(parameter_list_str)
        elif content.lower() == 'n':
            new_setting_cache.pop(openid)
            return "新设置申请已取消."
        else:
            return "请正确回复y/Y/n/N，谢谢"
    else:
        new_setting_cache.pop(openid)
        return "上次设置申请已超过1分钟有效期，已经注销。请重新设置。"


@app.route('/wx_flask', methods=['GET', 'POST'])
def wechat():
    # 微信验证token
    if request.method == 'GET':
        token = config.token
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
        global new_setting_cache
        rec_msg = receive.parse_xml(request.stream.read())

        if rec_msg.MsgType == 'text':
            content = rec_msg.Content.decode('utf-8')
            content = content.rstrip()
            if content.startswith(u"设置", 0, 2):
                ret, msg, parameter_list = sqlite.check_setting_parameter(rec_msg.FromUserName, content)
                if ret:
                    active_time = time.time() + 60
                    new_setting_cache.update({rec_msg.FromUserName: [parameter_list, active_time]})
                    msg += "\n\n确认更新输入y或Y，取消请输入n或N（请在一分钟内完成此操作）."
                else:  # 输入错误，或者与上次设置相同，都无需做
                    pass
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName, rec_msg.ToUserName,
                                             ("{0}\n{1}".format(msg, get_time())))
                return rep_text_msg.send()
            elif rec_msg.FromUserName in new_setting_cache:
                # 进入设置确认逻辑
                msg = make_sure(rec_msg.FromUserName, content)
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName, rec_msg.ToUserName, (
                    "{0}\n\n{1}".format(msg, get_time())))
                return rep_text_msg.send()
            elif content.startswith(u"查询", 0, 2):
                msg = ''
                old_parameter_tuple = sqlite.get_values_by_id('setting', 'openid', rec_msg.FromUserName)
                if not old_parameter_tuple:  # 如果数据库没有存在这个
                    msg += "您未设置任何参数."
                else:
                    msg += "您之前的设置为：\n"
                    msg += sqlite.change_tuple_to_string(old_parameter_tuple[0])
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName, rec_msg.ToUserName, (
                            "{0}\n\n{1}".format(msg, get_time())))
                return rep_text_msg.send()
            else:
                rep_text_msg = reply.TextMsg(rec_msg.FromUserName, rec_msg.ToUserName, (
                        "回复格式（设置 越价率 越价大单值 大单值 一分钟内提醒次数上限），如：\n设置 0.005 1000000 4000000 10"
                        "\n\n如需查询之前的设置，回复“查询”\n\n%s" % get_time()))
                return rep_text_msg.send()

        elif rec_msg.MsgType == "image":
            rep_img_msg = reply.ImageMsg(rec_msg.FromUserName,rec_msg.ToUserName,rec_msg.MediaId)
            return rep_img_msg.send()
        else:
            return "success"


# 获取时间戳
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


app.run(host='0.0.0.0', port=80, debug=True)
