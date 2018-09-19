# pip3 install requests
import requests
import json
import time
from Config import Config
from futuquant.common import bytes_utf8


RET_ERROR = -1
RET_OK = 0
config = Config()


class WechatPush(object):
    def __init__(self):
        self.app_id = config.appid
        self.secret = config.secrect
        self.access_generate_time = 0
        self.access_token = None

    # 获取accessToken
    def get_access_token_from_wechat(self):
        access_token_json = requests.get(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": self.app_id,
                "secret": self.secret
            }
        ).json()

        if 'errmsg' in access_token_json:
            print(access_token_json)
            return RET_ERROR, "Incorrect config, please check appid and secret. Or your ip did not add to whitelist."

        return RET_OK, access_token_json['access_token']

    def get_access_token(self):
        if self.access_generate_time == 0 or time.time() - self.access_generate_time > 7200 - 5:
            ret, self.access_token = self.get_access_token_from_wechat()
            if ret != RET_OK:
                return ret, self.access_token
            self.access_generate_time = time.time()
            print("Generate access token.")
        return RET_OK, self.access_token

    def send_msg_to_users_customer_service_news(self, openid, msg):

        ret, access_token = self.get_access_token()
        if ret != RET_OK:
            return ret, access_token
        body = {
            "touser": openid,
            "msgtype": "text",
            "text": {
                "content": msg
            }
        }
        response = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
            params={
                'access_token': access_token
            },
            data=bytes_utf8(json.dumps(body, ensure_ascii=False))
        )

        result = response.json()
        if result['errmsg'] != 'ok':
            return RET_ERROR, result
        return RET_OK, result

    def get_template_id(self):
        template_id = requests.get(
            url="https://api.weixin.qq.com/cgi-bin/template/api_add_template",
            params={
                'access_token': self.access_token
            }
        ).json()
        return template_id

    def list_to_template(self, openid, raw_msg_list):
        if len(raw_msg_list) != 7:
            print("Number of the list is wrong, you must set 7 params.")
        msg_list = []
        for item in raw_msg_list:
            if isinstance(item, float):
                msg_list.append(str(float('%.4f' % item)))
            else:
                msg_list.append(str(item))

        title_list = ["first", "keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "remark"]
        data = {}
        for i in range(len(title_list)):
            title_dict = {}
            title_dict.update({"value": msg_list[i]})
            title_dict.update({"color": "#173177"})
            data.update({title_list[i]: title_dict})

        body = {
            "touser": openid,
            "template_id": config.template_id,
            "data": data
        }
        return body

    def send_template_msg(self, openid, msg_list):

        ret, access_token = self.get_access_token()
        if ret != RET_OK:
            return ret, access_token

        body = self.list_to_template(openid, msg_list)

        response = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/message/template/send",
            params={
                'access_token': access_token
            },
            data=bytes_utf8(json.dumps(body, ensure_ascii=False))
        )
        result = response.json()
        if result['errmsg'] != 'ok':
            return RET_ERROR, result
        return RET_OK, result

    def get_user_openid_list(self):
        ret, access_token = self.get_access_token()
        if ret != RET_OK:
            return ret, access_token
        user_list_result = requests.get(
            url="https://api.weixin.qq.com/cgi-bin/user/get",
            params={
                'access_token': access_token
            }
        ).json()

        if user_list_result.get("total"):
            user_openid_list = user_list_result.get('data').get('openid')
        else:
            user_openid_list = None
        return RET_OK, user_openid_list

    def get_user_nickname(self, openid):
        ret, access_token = self.get_access_token()
        if ret != RET_OK:
            return ret, access_token
        user_info_json = requests.get(
            url="https://api.weixin.qq.com/cgi-bin/user/info",
            params={
                'access_token': access_token,
                'openid': openid,
                'lang': 'zh_CN'
            }
        ).json()
        user_nickname = user_info_json['nickname']
        # print(user_info_json['openid'], user_info_json['nickname'])
        return RET_OK, user_nickname

    def get_openid_by_nickname(self, nickname):
        ret, user_openid_list = self.get_user_openid_list()
        if ret != RET_OK:
            return ret, user_openid_list

        if user_openid_list:
            for openid in user_openid_list:
                ret, user_nickname = self.get_user_nickname(openid)
                if ret != RET_OK:
                    return ret, user_nickname

                if user_nickname == nickname:
                    return ret, openid
        return RET_ERROR, "please check your nickname."

    def send_text_msg(self, msg):
        ret, user_openid_list = self.get_user_openid_list()
        if ret != RET_OK:
            return ret, user_openid_list

        if user_openid_list:
            for openid in user_openid_list:
                ret, user_nickname = self.get_user_nickname(openid)
                if ret != RET_OK:
                    return ret, user_nickname

                if user_nickname in config.test_user_nickname:
                    ret, msg = self.send_msg_to_users_customer_service_news(openid, msg)
                    if ret != RET_OK:
                        return ret, msg

    def sent_template_msg_to_users(self, msg):
        ret, user_openid_list = self.get_user_openid_list()
        if ret != RET_OK:
            return ret, user_openid_list

        if user_openid_list:
            for openid in user_openid_list:
                ret, user_nickname = self.get_user_nickname(openid)
                if ret != RET_OK:
                    return ret, user_nickname

                if user_nickname in config.test_user_nickname:
                    ret, msg = self.send_template_msg(openid, msg)
                    if ret != RET_OK:
                        return ret, msg
        return RET_OK, "Send template msg successfully."


# ---- 单元测试代码
if __name__ == '__main__':
    msg = ["测试消息", 10000, 101.000456, 200, 20000, 123, "请及时查看，谢谢！"]
    wp = WechatPush()  # test号

    import sys
    ret, my_openid = wp.get_openid_by_nickname('lpt')
    if ret != RET_OK:
        sys.exit(1)
    print(my_openid)
    # my_openid = ''
    print(wp.send_template_msg(my_openid, msg))
