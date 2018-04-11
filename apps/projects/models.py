from django.db import models
from users.models import User
# Create your models here.


class Language(models.Model):
    name = models.CharField(max_length=50, verbose_name='编程语言')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    src = models.CharField(max_length=50,verbose_name="编程语言源代码",null=True)

    class Meta:
        db_table = 'Source_Language'
        verbose_name = "编程语言"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Project(models.Model):
    STATE_CHOICE = [
        ('1', '正常'),
        ('2', '删除'),
        ('3', '即将上线'),
    ]

    name = models.CharField(max_length=255, verbose_name='工程名称')
    desc = models.TextField(verbose_name='描述')
    path = models.CharField(max_length=200, verbose_name='工程路径')
    language = models.ForeignKey(Language, null=True, verbose_name='编程语言', on_delete=models.SET_NULL)
    github = models.URLField(max_length=100, verbose_name='Github网址')
    ossean = models.URLField(max_length=100, verbose_name='Ossean网址')
    files = models.IntegerField(default=0, verbose_name='文件数量')
    views = models.IntegerField(default=0, verbose_name='点击数量')
    uploader = models.ForeignKey(User, verbose_name="上传者", default="1", null=True, on_delete=models.SET_NULL)
    state = models.CharField(max_length=3, choices=STATE_CHOICE, default='1')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Source_Project'
        verbose_name = "工程"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['views', ]),
            models.Index(fields=['create_time', ]),
            models.Index(fields=['uploader', ]),
        ]

    def __str__(self):
        return self.name


class File(models.Model):
    TYPE_CHOICE = [
        ('0', '目录'),
        ('1', '文件'),
    ]

    STATE_CHOICE = [
        ('1', '正常'),
        ('2', '删除'),
        ('3', '即将上线'),
    ]
    name = models.CharField(max_length=255, verbose_name='文件名称')
    path = models.CharField(max_length=200, verbose_name='文件路径')
    super_path = models.ForeignKey("self", null=True, blank=True, verbose_name='上级目录', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name='工程名称', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TYPE_CHOICE, default='0')
    state = models.CharField(max_length=3, choices=STATE_CHOICE, default='1')
    views = models.IntegerField(default=0, verbose_name='点击数量')
    vote = models.IntegerField(default=0, verbose_name='点赞数量')
    has_summary = models.BooleanField(default=False, verbose_name='是否有有摘要')
    has_note = models.BooleanField(default=False, verbose_name='是否有首行注释')
    has_question = models.BooleanField(default=False, verbose_name='是否添加0行问题')
    has_sonar = models.BooleanField(default=False, verbose_name='是否通过sonar获取问题')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    anno_num = models.IntegerField(default=0, verbose_name='注释数量')
    issue_num = models.IntegerField(default=0, verbose_name='注释数量')

    class Meta:
        db_table = 'Source_File'
        verbose_name = "文件"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['views', ]),
            models.Index(fields=['create_time', ]),

        ]

    def __str__(self):
        return '文件{0}_{1}'.format(self.id, self.name)


class FileInfo(models.Model):
    file = models.ForeignKey(File, verbose_name='文件', on_delete=models.CASCADE)
    summary = models.CharField(max_length=300, default='', verbose_name='摘要')
    note = models.TextField(default='',  verbose_name='首行注释')


    class Meta:
        db_table = 'Source_FileInfo'
        verbose_name = "文件信息"
        verbose_name_plural = verbose_name


class Watch(models.Model):
    user = models.ForeignKey(User, verbose_name="用户", default="1", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name="工程", on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Source_Watch'
        verbose_name = "源码关注"
        verbose_name_plural = verbose_name






