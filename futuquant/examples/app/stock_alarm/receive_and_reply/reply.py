# -*- coding: utf-8 -*-
# filename: reply.py
import time

'''
该文件的类是发送体模型，传参数进来即返回要发送的xml信息
'''
class Msg(object):
    def __init__(self):
        pass

    def send(self):
        return "success"


class TextMsg(Msg):
    def __init__(self, to_user_name, from_user_name, content):
        self.__dict = dict()
        self.__dict['ToUserName'] = to_user_name
        self.__dict['FromUserName'] = from_user_name
        self.__dict['CreateTime'] =int(time.time())
        self.__dict['Content'] = content

    def send(self):
        xml_form = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return xml_form.format(**self.__dict)


class ImageMsg(Msg):
    def __init__(self, to_user_name, from_user_name, media_id):
        self.__dict = dict()
        self.__dict['ToUserName'] = to_user_name
        self.__dict['FromUserName'] = from_user_name
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = media_id

    def send(self):
        xml_form = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Image>
        </xml>
        """
        return xml_form.format(**self.__dict)
