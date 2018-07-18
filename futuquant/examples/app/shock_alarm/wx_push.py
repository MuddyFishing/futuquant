# pip3 install requests
import requests
import json
import time
import common_parameter

class wechat_push(object):
    def __init__(self):
        self.appid = common_parameter.appid
        self.secrect = common_parameter.secrect
        self.access_generate_time = 0
        self.access_token = None

    # 获取accessToken
    def get_access_token_from_wechat(self):
        access_token_json = requests.get(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": self.appid,
                "secret": self.secrect
            }
        ).json()
        if(access_token_json):
            self.access_token = access_token_json['access_token']
        else:
            self.access_token = None
        return self.access_token

    def get_access_token(self):
        if(self.access_generate_time == 0 or time.time() - self.access_generate_time > 7200 - 5):
            self.access_token = self.get_access_token_from_wechat()
            self.access_generate_time = time.time()
            print("Generate access token.")
        return self.access_token

    def send_msg_to_users_customer_service_news(self, openid, msg):

        access_token = self.get_access_token()
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
        print(result)


    def get_template_id(access_token):
        template_id = requests.get(
            url="https://api.weixin.qq.com/cgi-bin/template/api_add_template",
            params={
                'access_token': access_token
            }
        ).json()
        return template_id

    def send_msg_to_users_template_news(self, openid, msg):

        access_token = self.get_access_token()
        body = {
            "touser": openid,
            "template_id":"jr67sFJ5w4ln_ty6e0BHSBLZNOUOgMXOC-ph9u6xWwQ",
             "data":{
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
        print(result)

    def get_user_openid_list(self):
        access_token = self.get_access_token()
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
        return user_openid_list

    def get_user_nickname(self, openid):
        access_token = self.get_access_token()
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
        return user_nickname

    def send_template_msg(self, openid, msg):
        self.send_msg_to_users_template_news(openid, msg)

    def send_text_msg(self, msg):
        user_openid_list = self.get_user_openid_list()
        if user_openid_list:
            for openid in user_openid_list:
                if (self.get_user_nickname(openid) in common_parameter.test_user_list):
                    self.send_msg_to_users_template_news(openid, msg)

    def sent_template_msg_to_users(self):
        user_openid_list = self.get_user_openid_list()
        if user_openid_list:
            for openid in user_openid_list:
                if (self.get_user_nickname(openid) in common_parameter.test_user_list):
                    self.send_msg_to_users_template_news(openid, msg)
        


# ---- 单元测试代码
if __name__ == '__main__':
    # sendmsg('','Hello!')
    # msg =
    msg = {
        'echo_type': 'Warning',
        'code':str(10000),
        'direction': 'SELL',
        'prev_price': str(100.2),
        'price': str(101.1),
        'total_deal_price':str(200),
        'time': str(123)
    }
    text_msg = 'Hello'

    # print(get_template_id(get_access_token()))
    wp = wechat_push()  # test号
    # wp = wechat_push('wxbe3ec6c53ff67a31', '')
    # print(wp.get_access_token())
    # wp.send_text_msg(text_msg)
    # wp.send_template_msg(msg)

    # 输出所有用户nickname
    all_user_openid =wp.get_user_openid_list()
    for user in all_user_openid:
        wp.get_user_nickname(user)