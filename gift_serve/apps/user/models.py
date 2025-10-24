from django.db import models
from django.utils import timezone


class User(models.Model):
    # 自定义主键user_id，从10000开始自增
    user_id = models.AutoField(primary_key=True, verbose_name='用户ID', default=10000)
    # 基本信息字段
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    user_icon = models.TextField(null=True, blank=True, verbose_name='用户头像')

    age = models.IntegerField(verbose_name='用户年龄', null=True, blank=True)
    birthday = models.DateField(verbose_name='用户生日', null=True, blank=True)
    # 性别选择
    GENDER_CHOICES = (
        (1, '男'),
        (2, '女'),
        (0, '未知')
    )
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=0, verbose_name='用户性别')
    # 自动生成创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 删除标识
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='电话号码')
    # 新增密码字段 - 使用Django内置加密
    password = models.CharField(max_length=128, verbose_name='密码')  # 长度128用于存储哈希值

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户列表'
        ordering = ['-create_time']

    def __str__(self):
        return f"{self.username} (ID: {self.user_id})"