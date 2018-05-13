# -*- coding: utf-8 -*-
from futuquant.common.utils import *
from futuquant.common.constant import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1
from Crypto import Random


class SysConfig(object):
    # api通讯协议是否加密
    IS_PROTO_ENCRYPT = False

    # 初始连接协议用到的rsa private key file
    INIT_RSA_FILE = ''

    # ras加解密对象
    RSA_OBJ = None

    def __init__(self):
        pass

    @classmethod
    def set_init_rsa_file(cls, file):
        """
        :param file:  file path for init rsa private key
        :return:
        """
        SysConfig.INIT_RSA_FILE = str(file)
        pass

    @classmethod
    def get_init_rsa(cls):
        """
        :return: str , private key for init connect protocol
        """

        if not SysConfig.RSA_OBJ:
            SysConfig._read_rsa_keys()

        return SysConfig.RSA_OBJ

    @classmethod
    def is_proto_encrypt(cls):
        """
        :return: bool
        """
        return SysConfig.IS_PROTO_ENCRYPT

    @classmethod
    def enable_proto_encrypt(cls, is_encrypt):
        """
        :param is_encrypt: bool
        :return:
        """
        SysConfig.IS_PROTO_ENCRYPT = bool(is_encrypt)

    @classmethod
    def _read_rsa_keys(cls):
        file_path = SysConfig.INIT_RSA_FILE if SysConfig.INIT_RSA_FILE \
            else os.path.join(os.path.dirname(__file__), DEFAULT_INIT_PRI_KEY_FILE)

        try:
            f = open(file_path, 'rb')
            df = f.read()
            if type(df) is not str:
                df = str(df, encoding='utf8')

            rsa = RSA.importKey(df)
            pub_key = rsa.publickey().exportKey()
            if not pub_key:
                raise Exception("Illegal format of file content")

            SysConfig.RSA_OBJ = rsa

        except Exception as e:
            traceback.print_exc()
            err = sys.exc_info()[1]
            raise Exception("Fatal error occurred in getting proto key, detail:{}".format(err))


class RsaCrypt(object):
    RANDOM_GENERATOR = Random.new().read
    CHIPPER = None
    @classmethod
    def encrypt(cls, data):
        if RsaCrypt.CHIPPER is None:
            rsa = SysConfig.get_init_rsa()
            RsaCrypt.CHIPPER = Cipher_pkcs1.new(rsa)

        if type(data) is not bytes:
            data = bytes(str(data), encoding='utf8')

        # 单次加密串的长度最大为(key_size / 8) - 11
        # 1024 bit的证书用100， 2048 bit的证书用 200
        one_len = 100
        ret_data = b''
        for i in range(0, len(data), one_len):
            ret_data += RsaCrypt.CHIPPER.encrypt(data[i:i + one_len])
        return ret_data

    @classmethod
    def decrypt(cls, data):
        if RsaCrypt.CHIPPER is None:
            rsa = SysConfig.get_init_rsa()
            RsaCrypt.CHIPPER = Cipher_pkcs1.new(rsa)

        # 1024 bit的证书用128，2048 bit证书用256位
        one_len = 128
        ret_data = b''
        for i in range(0, len(data), one_len):
            ret_data += RsaCrypt.CHIPPER.decrypt(data[i:i + one_len], RsaCrypt.RANDOM_GENERATOR)
        return ret_data


"""
test_str = 'futu api' * 32
dt_encrypt = RsaCrypt.encrypt(test_str)
print(dt_encrypt)
dt_decrypt = RsaCrypt.decrypt(dt_encrypt)
print(dt_decrypt)
"""

"""
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

key = b'0123456789abcdef'
cryptor = AES.new(key, AES.MODE_ECB, key)

src = b'123'
len_src = len(src)
add = 16 - (len_src % 16)
src = src
src2 = src + (b'\0' * add)

dst = cryptor.encrypt(src2)
hex_dst = b2a_hex(dst)
print(hex_dst)

src3 = cryptor.decrypt(dst)
print("len={} decrypt={}".format(len(src3), src3))
"""





