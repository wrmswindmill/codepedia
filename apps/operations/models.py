from django.db import models
from projects.models import Project, File
from users.models import User


class Article(models.Model):
    STATE_CHOICE = [
        ('2', '正常'),
        ('4', '关闭'),
        ('6', '删除'),
        ('8', '锁定'),
    ]
    project = models.ForeignKey(Project, verbose_name="工程", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="用户", default="1", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='文章标题')
    summary = models.TextField(verbose_name='文章摘要')
    content = models.TextField(verbose_name='文章内容')
    state = models.CharField(max_length=3, choices=STATE_CHOICE, default='2')
    weight = models.FloatField(max_length=3, default='0')
    views = models.IntegerField(default=0, verbose_name='点击数量')
    vote = models.IntegerField(default=0, verbose_name='点赞数量')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Article'
        verbose_name = "文章"
        verbose_name_plural = verbose_name


class Annotation(models.Model):
    STATE_CHOICE = [
        ('2', '正常'),
        ('4', '关闭'),
        ('6', '删除'),
        ('8', '锁定'),
    ]
    content = models.TextField(default='', verbose_name='内容')
    user = models.ForeignKey(User, verbose_name='用户',on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name='工程', null=True, related_name='project_anno',on_delete=models.CASCADE)
    file = models.ForeignKey(File, verbose_name='文件', null=True,  related_name='file_anno',on_delete=models.CASCADE)
    linenum = models.IntegerField(default=0, verbose_name='注释行号')
    state = models.CharField(max_length=3, choices=STATE_CHOICE, default='2')
    vote = models.IntegerField(default=0, verbose_name='点赞数量')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Annotation'
        verbose_name = "注释"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '注释{0}'.format(self.id)


class Question(models.Model):
    SOURCE_CHOICE = [
        ('1', '系统'),
        ('2', '用户')
    ]

    TYPE_CHOICE = [
        ('1', '选择题'),
        ('2', '问答题')
    ]

    INFO_CHOICE = [
        ('1', '错误程度'),
        ('2', '错误类型'),
        ('3', '存在错误')
    ]

    content = models.TextField(default='', verbose_name='问题内容')
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    question_source = models.CharField(choices=SOURCE_CHOICE, default='1', max_length=3, verbose_name='问题来源')
    question_type = models.CharField(choices=TYPE_CHOICE, default='1', max_length=3, verbose_name='问题类型')
    question_info = models.CharField(choices=INFO_CHOICE, null=True, max_length=3, verbose_name='问题信息')
    file = models.ForeignKey(File, verbose_name="文件", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name="工程", on_delete=models.CASCADE)
    vote = models.IntegerField(default=0, verbose_name='点赞数量')
    sonar_id = models.IntegerField(null=True, verbose_name='Sonar')
    linenum = models.IntegerField(null=True, verbose_name='问题行号')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Question"
        verbose_name = "问题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '问题{0}'.format(self.id)


class Answer(models.Model):
    content = models.TextField(default='', verbose_name='内容')
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name='问题', related_name='question_ans', on_delete=models.CASCADE)
    vote = models.IntegerField(default=0, verbose_name='点赞数量')
    correct = models.BooleanField(default=True, verbose_name='正确与否')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Answer'
        verbose_name = u"回答"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['question_id', 'user_id', ]),
        ]

    def __str__(self):
        return '回答{0}'.format(self.id)


class QuestionChoices(models.Model):
    question = models.ForeignKey(Question, verbose_name='问题', related_name='question_choices', on_delete=models.CASCADE)
    choice_text = models.TextField(default='', verbose_name='选项内容')
    choice_position = models.CharField(default='', max_length=10, verbose_name='选项位置')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Question_Choice"
        verbose_name = "选择题选项"
        verbose_name_plural = verbose_name


class QuestionStandardAnswers(models.Model):
    question = models.ForeignKey(Question, verbose_name='问题', related_name='question_standard_answers', on_delete=models.CASCADE)
    choice_position = models.CharField(default='', max_length=500,  verbose_name='正确选项位置')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Question_Standard_Answers"
        verbose_name = "标准答案"
        verbose_name_plural = verbose_name


class QuestionComment(models.Model):
    content = models.TextField(default='', verbose_name='内容')
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name='问题', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Question_Comment'
        verbose_name = u"问题评论"
        verbose_name_plural = verbose_name


class ArticleComment(models.Model):
    content = models.TextField(default='', verbose_name='内容')
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='文章', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Article_Comment'
        verbose_name = u"文章评论"
        verbose_name_plural = verbose_name


class AnnotationComment(models.Model):
    content = models.TextField(default='', verbose_name='内容')
    user = models.ForeignKey(User, verbose_name='用户',on_delete=models.CASCADE)
    annotation = models.ForeignKey(Annotation, verbose_name='注释', related_name='annotation_comment',on_delete=models.CASCADE)
    vote = models.IntegerField(default=0, verbose_name='点赞数量')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Annotation_Comment'
        verbose_name = u"注释评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '评论{0}'.format(self.id)


class AnswerComment(models.Model):
    content = models.TextField(default='', verbose_name='内容')
    user = models.ForeignKey(User, verbose_name='用户',on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, verbose_name='回答', related_name='answer_comment',on_delete=models.CASCADE)
    vote = models.IntegerField(default=0, verbose_name='点赞数量')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Answer_Comment'
        verbose_name = u"回答评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '评论{0}'.format(self.id)




