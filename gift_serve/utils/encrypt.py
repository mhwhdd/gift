# utils/encrypt.py
import hashlib
from django.conf import settings





class PasswordEncryptor:
    """密码加密工具类"""

    @staticmethod
    def set_password(password, salt=None):
        """
        MD5加密密码
        :param password: 明文密码
        :param salt: 盐值，增强安全性
        :return: 加密后的密码
        """
        if salt is None:
            salt = settings.SECRET_KEY  # 使用Django的SECRET_KEY作为盐值[11](@ref)

        md5_hash = hashlib.md5()
        # 密码加盐处理
        salted_password = f"{password}{salt}"
        md5_hash.update(salted_password.encode('utf-8'))
        return md5_hash.hexdigest()

    def check_password(input_password, encrypted_password):
        """
        校验密码工具方法
        :param input_password: 用户输入的明文密码
        :param encrypted_password: 数据库中存储的加密密码
        :return: Boolean
        """
        # 对输入密码进行相同的 MD5 加密
        input_encrypted = PasswordEncryptor.set_password(input_password, salt=None)
        # 比较加密后的密码
        return input_encrypted == encrypted_password
    @staticmethod
    def verify_password(input_password, encrypted_password, salt=None):
        """
        验证密码
        :param input_password: 输入的密码
        :param encrypted_password: 加密后的密码
        :param salt: 盐值
        :return: 是否匹配
        """
        return PasswordEncryptor.set_password(input_password, salt) == encrypted_password