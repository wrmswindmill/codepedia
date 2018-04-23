from django.contrib import admin
import xadmin
from .models import Annotation, AnnotationComment, QuestionAnswer, QuestionAnswerComment
from .models import Article, ArticleComment, Question, QuestionComment
# Register your models here.


class ArticleAdmin(object):
    readonly_fields = ['views', 'vote', 'weight']


class ArticleCommentAdmin(object):
    readonly_fields = ['vote']


class QuestionAdmin(object):
    readonly_fields = ['vote']


class QuestionCommentAdmin(object):
    readonly_fields = ['vote']


class AnswerAdmin(object):
    readonly_fields = ['vote']


class AnswerCommentAdmin(object):
    readonly_fields = ['vote']


class AnnotationAdmin(object):
    readonly_fields = ['vote']


class AnnotationCommentAdmin(object):
    readonly_fields = ['vote']


xadmin.site.register(Article,  ArticleAdmin)
xadmin.site.register(ArticleComment,  ArticleCommentAdmin)
xadmin.site.register(Question, QuestionAdmin)
xadmin.site.register(QuestionComment, QuestionCommentAdmin)
xadmin.site.register(QuestionAnswer, AnswerAdmin)
xadmin.site.register(QuestionAnswerComment, AnswerCommentAdmin)
xadmin.site.register(Annotation, AnnotationAdmin)
xadmin.site.register(AnnotationComment, AnnotationCommentAdmin)
