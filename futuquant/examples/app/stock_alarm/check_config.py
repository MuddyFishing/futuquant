from Config import Config
import requests
from wx_push import WechatPush

config = Config()
wp = WechatPush()
RET_OK = 0
RET_ERROR = -1


class CheckConfig:

    def _check_template_id(self, openid):
        msg = {
            'echo_type': '*** This is test ***',
            'code': str(10000),
            'price': str(101.1),
            'total_deal_price': str(200),
            'quantity': str(20000),
            'time': str(123)
        }
        ret, msg = wp.send_template_msg(openid, msg)
        if ret != RET_OK:
            return ret, msg
        return RET_OK, msg

    def _check_test_nickname(self, test_nickname):
        nickname_openid = {}
        # nickname
        ret, all_user_openid = wp.get_user_openid_list()
        if ret != RET_OK:
            return ret, all_user_openid

        if all_user_openid:
            for user in all_user_openid:
                ret, nickname = wp.get_user_nickname(user)
                if ret != RET_OK:
                    return ret, nickname
                nickname_openid.update({nickname: user})

        res_nickname_openid = {}
        for name in test_nickname:
            if name not in nickname_openid:
                return RET_ERROR, name + ", this nickname is wrong."
            res_nickname_openid.update({name: nickname_openid[name]})

        return RET_OK, res_nickname_openid

    def _send_test_msg_to_test_nickname(self):
        print("Trying to send test msg to your nickname...")
        ret, nickname_openid = self._check_test_nickname(config.test_user_nickname)
        if ret != RET_OK:
            return ret, nickname_openid

        for name in nickname_openid:
            ret, msg = self._check_template_id(nickname_openid[name])
            if ret != RET_OK:
                return ret, msg
        return RET_OK, "Send test template massage successfully."

    def _check_wechat(self):
        msg = ''
        if config.appid == '':
            msg += 'Wechat appid is null.'
            return RET_ERROR, msg
        if config.secrect == '':
            msg += 'Wechat secret is null.'
            return RET_ERROR, msg
        print('Wechat appid and secret checked.')
        ret, access_token = wp.get_access_token_from_wechat()
        if ret != RET_OK:
            return ret, access_token

        if config.test_user_nickname == '':
            return RET_ERROR, "Please fill your nickname in Config.py"

        # ---- send test msg to tester.
        # else:
        #     if len(config.test_user_list) == 0 and len():
        #         return RET_ERROR, "Please fill the test_user_list correctly."
        #     else:
        #         for test_openid in config.test_user_list:
        #             ret, msg = self._check_template_id(test_openid)
        #             if ret != RET_OK:
        #                 return ret, msg
        #             print("Template_id is ready.")

        return RET_OK, "Connect wechat successfully."

    def _check_others(self):
        msg = ''
        if config.database == '':
            msg += 'Database name is null.\n'

        if config.host == '':
            msg += 'Host is null.\n'

        if config.port == '':
            msg += 'Port is null.\n'

        if config.token == '':
            msg += 'Token is null.\n'

        if config.template_id == '':
            msg += 'Template_id is null.\n'

        if msg != '':
            return RET_ERROR, msg

        return RET_OK, "Other parameter is ready."

    def check_all(self):
        print("+-------------------------------+")
        ret, msg = self._check_wechat()
        if ret != RET_OK:
            return ret, msg
        print(msg)

        ret, msg = self._check_others()
        if ret != RET_OK:
            return ret, msg
        print(msg)
        print("Check config successfully.")
        print("+-------------------------------+")
        return RET_OK, ""


# ---- test code
if __name__ == '__main__':
    cc = CheckConfig()
    ret, msg = cc.check_all()
    if ret != RET_OK:
        print(ret, msg)


