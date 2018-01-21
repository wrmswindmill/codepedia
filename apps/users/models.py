from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class School(models.Model):
    name = models.CharField(max_length=50, verbose_name="学校", default="")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'School'
        verbose_name = "学校信息"
        verbose_name_plural = verbose_name


class Grade(models.Model):
    name = models.CharField(max_length=50, verbose_name="班级名称", default="")
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.CASCADE)
    college = models.CharField(max_length=50, verbose_name="学院", default="")
    year = models.IntegerField(null=True, verbose_name="年份")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Grade'
        verbose_name = "班级信息"
        verbose_name_plural = verbose_name


class User(AbstractUser):
    GENDER_CHOICE = [
        ("male", "男"),
        ("female", "女")
    ]

    ROLE_CHOICE = (
        ('1', '学生'),
        ('2', '老师'),
        ('3', '开发人员')
    )

    nick_name = models.CharField(max_length=50, verbose_name="昵称", default="")
    birthday = models.DateField(verbose_name="生日", null=True, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICE, default="female")
    address = models.CharField(max_length=100, default=u"")
    mobile = models.CharField(max_length=11, null=True, blank=True)
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.SET_NULL)
    grade = models.ManyToManyField(Grade, verbose_name='班级', blank=True)
    avatar = models.ImageField(upload_to="avatar/%Y/%m", default=u"avatar/users/default.png", max_length=100)
    role = models.CharField(max_length=3, choices=ROLE_CHOICE, default='1')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'User'
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name