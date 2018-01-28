"""Codepedia2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import ShowQuestionView, ShowAnnotationView, ShowNavigationView
from .views import AddAnnotationView, AddArticleView, AddQuestionView, AddAnswerView, AddCommentView
from .views import UpdateAnnotationView, UpdateArticleView, UpdateQuestionView, UpdateAnswerView, UpdateCommentView
from .views import AddVoteView, AcceptAnswerView

app_name = "operations"
urlpatterns = [
    path('add_annotation/', AddAnnotationView.as_view(), name='new_annotation'),
    path('update_annotation/', UpdateAnnotationView.as_view(), name='update_annotation'),
    path('add_article/', AddArticleView.as_view(), name='new_article'),
    path('update_article/', UpdateArticleView.as_view(), name='update_article'),
    path('add_question/', AddQuestionView.as_view(), name='new_question'),
    path('update_question/',  UpdateQuestionView.as_view(), name='update_question'),
    path('add_answer/', AddAnswerView.as_view(), name='new_answer'),
    path('update_answer/',  UpdateAnswerView.as_view(), name='update_answer'),
    path('add_comment/', AddCommentView.as_view(), name='new_comment'),
    path('update_comment/',  UpdateCommentView.as_view(), name='update_comment'),
    path('show_annotation/', ShowAnnotationView.as_view(), name='show_annotation'),
    path('show_navigation/', ShowNavigationView.as_view(), name='show_navigation'),
    path('show_question/', ShowQuestionView.as_view(), name='show_question'),
    path('show_question/', ShowQuestionView.as_view(), name='show_question'),
    path('accept_answer/', AcceptAnswerView.as_view(), name='accept_answer'),
    path('add_vote/', AddVoteView.as_view(), name='add_vote'),
]
