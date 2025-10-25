from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.user.models import User

class Tag(models.Model):
    # 标签类型选择
    TAG_TYPE_CHOICES = [
        ('skill', '技能标签'),
        ('interest', '兴趣标签'),
        ('system', '系统标签'),
        ('custom', '自定义标签'),
    ]

    # 标签主键
    tag_id = models.AutoField(primary_key=True, verbose_name='标签ID')

    # 标签类型字段
    tag_type = models.CharField(
        max_length=20,
        choices=TAG_TYPE_CHOICES,
        default='custom',
        verbose_name='标签类型'
    )

    # 标签名称
    tag_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='标签名称',
        help_text='请输入标签名称，最多100个字符'
    )

    # 创建时间（自动）
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    # 标签描述
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='标签描述',
        help_text='可选，最多500个字符'
    )

    # 是否激活
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否激活'
    )

    class Meta:
        db_table = 'user_tags'
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['-created_time']
        indexes = [
            models.Index(fields=['tag_type', 'is_active']),
            models.Index(fields=['tag_name']),
        ]

    def __str__(self):
        return f"{self.tag_name} ({self.get_tag_type_display()})"


class UserTagRelationship(models.Model):

    # 关联主键
    relation_id = models.AutoField(primary_key=True, verbose_name='关联ID')

    # 用户外键 - 假设您的用户模型名为User
    user = models.ForeignKey(
        User,  # 请根据您的实际用户模型名称调整
        on_delete=models.CASCADE,
        related_name='user_tags',
        verbose_name='用户'
    )

    # 标签外键
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tagged_users',
        verbose_name='标签'
    )

    # 关联时间
    relation_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='关联时间'
    )

    # 关联权重（0-1之间的小数）
    weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='关联权重',
        help_text='0-1之间的数值，表示关联强度'
    )

    # 关联状态
    status =models.BooleanField(
        default=True,
        verbose_name='是否激活'
    )

    # 关联描述
    relation_description = models.TextField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='关联描述',
        help_text='可选，描述用户与此标签的具体关系'
    )

    class Meta:
        db_table = 'user_tag_relationships'
        verbose_name = '用户-标签关联'
        verbose_name_plural = '用户-标签关联'
        unique_together = ['user', 'tag']  # 防止重复关联
        ordering = ['-relation_time']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['tag', 'status']),
            models.Index(fields=['relation_time']),
        ]

    def __str__(self):
        return f"{self.user} - {self.tag} ({self.status})"