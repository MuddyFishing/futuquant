# pip3 install requests
import requests
import json
import time
from Config import Config
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
            return RET_ERROR, "Incorrect config, please check appid and secret."

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
            data=bytes(json.dumps(body, ensure_ascii=False), encoding='utf-8')
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

    def send_template_msg(self, openid, msg):

        ret, access_token = self.get_access_token()
        if ret != RET_OK:
            return ret, access_token

        body = {
            "touser": openid,
            "template_id":config.template_id,
            "data": {
                    "first": {
                       "value":(msg['echo_type']),
                       "color":"#173177"
                    },
                    "keyword1":{
                       "value":msg['code'],
                       "color":"#173177"
                    },
                     "keyword2": {
                         "value": msg['price'],
                         "color": "#173177"
                     },
                    "keyword3": {
                       "value":msg['total_deal_price'],
                       "color":"#173177"
                    },
                    "keyword4": {
                       "value":msg['quantity'],
                       "color":"#173177"
                    },
                    "keyword5":{
                       "value":msg['time'],
                       "color":"#173177"
                    },
                    "remark":{
                       "value":"请及时前往查看，谢谢！",
                       "color":"#173177"
                    }
               }
        }
        response = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/message/template/send",
            params={
                'access_token': access_token
            },
            data=bytes(json.dumps(body, ensure_ascii=False), encoding='utf-8')
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
    # sendmsg('','Hello!')
    # msg =
    msg = {
        'echo_type': 'Warning',
        'code':str(10000),
        'price': str(101.1),
        'total_deal_price':str(200),
        'quantity': str(20000),
        'time': str(123)
    }
    text_msg = 'Hello'

    # print(get_template_id(get_access_token()))
    wp = WechatPush()  # test号
    print(wp.get_access_token())
    # wp.send_text_msg(text_msg)
    print(wp.sent_template_msg_to_users(msg))

    # nickname
    all_user_openid = wp.get_user_openid_list()
    if all_user_openid:
        for user in all_user_openid:
            print(wp.get_user_nickname(user), user)