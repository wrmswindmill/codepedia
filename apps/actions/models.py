from django.db import models
from users.models import User
from operations.models import Question, Answer, Article, Annotation, Issue, IssueAnswer
from operations.models import QuestionComment, AnswerComment, ArticleComment, AnnotationComment, IssueComment

# Create your models here.


# class Vote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     TYPE_CHOICE = [
#         ('question', '问题'),
#         ('answer', '回答'),
#         ('article', '文章'),
#         ('annotation', '注释'),
#         ('issue', 'issue'),
#         ('issue_answer', 'issue回答'),
#         ('question_comment', '问题评论'),
#         ('answer_comment', '回答评论'),
#         ('article_comment', '文章评论'),
#         ('annotation_comment', '注释评论'),
#         ('file', '代码文件'),
#     ]
#
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     vote_type = models.CharField(choices=TYPE_CHOICE, default='', verbose_name='点赞对象名称')
#     vote_type_id = models.IntegerField(default=0, verbose_name='点赞对象id')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote'
#         verbose_name = u"点赞"
#         verbose_name_plural = verbose_name


# class QuestionVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     question = models.ForeignKey(Question, verbose_name='问题', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Question'
#         verbose_name = u"问题点赞"
#         verbose_name_plural = verbose_name
#
#
# class IssueVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     issue = models.ForeignKey(Issue, verbose_name='issue', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Issue'
#         verbose_name = u"问题点赞"
#         verbose_name_plural = verbose_name
#
#
# class AnswerVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     answer = models.ForeignKey(Answer, verbose_name='答案', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Answer'
#         verbose_name = u"回答点赞"
#         verbose_name_plural = verbose_name
#
#
# class AnnotationVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     annotation = models.ForeignKey(Annotation, verbose_name='注释', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Annotation'
#         verbose_name = u"注释点赞"
#         verbose_name_plural = verbose_name
#
#
# class ArticleVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     article = models.ForeignKey(Article, verbose_name='文章', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Article'
#         verbose_name = u"问题点赞"
#         verbose_name_plural = verbose_name
#
#
# class ArticleCommentVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     comment = models.ForeignKey(ArticleComment, verbose_name='文章评论', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Article_Comment'
#         verbose_name = u"文章评论点赞"
#         verbose_name_plural = verbose_name
#
#
# class QuestionCommentVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     comment = models.ForeignKey(QuestionComment, verbose_name='问题评论', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Question_Comment'
#         verbose_name = u"问题评论点赞"
#         verbose_name_plural = verbose_name
#
#
# class IssueCommentVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     comment = models.ForeignKey(IssueComment, verbose_name='issue评论', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Issue_Comment'
#         verbose_name = u"Issue评论点赞"
#         verbose_name_plural = verbose_name
#
#
# class AnswerCommentVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     comment = models.ForeignKey(AnswerComment, verbose_name='回答评论', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Answer_Comment'
#         verbose_name = u"回答评论点赞"
#         verbose_name_plural = verbose_name
#
#
# class AnnotationCommentVote(models.Model):
#     VALUE_CHOICE = [
#         (1, '点赞'),
#         (-1, '点踩')
#     ]
#     user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.CASCADE)
#     comment = models.ForeignKey(AnnotationComment, verbose_name='注释评论', on_delete=models.CASCADE)
#     value = models.IntegerField(choices=VALUE_CHOICE, default=0, verbose_name='点赞类型')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'Vote_Annotation_Comment'
#         verbose_name = u"注释评论点赞"
#         verbose_name_plural = verbose_name