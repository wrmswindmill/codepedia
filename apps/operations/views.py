from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.conf import settings

import json
import requests
from django.core import serializers
# Create your views here.


from .models import Annotation, Question, Answer, Article, Issue, IssueAnswer, IssueStandardAnswers
from .models import AnnotationComment, QuestionComment, AnswerComment, ArticleComment, IssueComment
from .models import Vote
from .forms import NewArticleForm
from projects.models import File


class ShowAnnotationView(View):
    """
    获取某一行代码所有的注释
    """
    def post(self, request):
        # if not request.user.is_authenticated:
        #     return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        file_id = int(request.POST.get('file_id', ''))
        line_num = int(request.POST.get('line_num', ''))

        annotations = Annotation.objects.filter(file_id=file_id, linenum=line_num)
        annotations = serializers.serialize("json", annotations)
        return HttpResponse(json.dumps({"status": "success", "msg": annotations}), content_type='application/json')
        # return JsonResponse(annotations, safe=False)


class ShowQuestionView(View):
    """
       获取某一行代码所有的提问
    """
    def post(self, request):
        file_id = int(request.POST.get('file_id', ''))
        line_num = int(request.POST.get('line_num', ''))
        questions = Question.objects.filter(file_id=file_id, linenum=line_num)
        questions = serializers.serialize("json", questions)
        return HttpResponse(json.dumps({"status": "success", "msg": questions}), content_type='application/json')


class ShowNavigationView(View):
    """
       获取当前文件的Structure，也就是Package,Class，Method信息。
    """
    def post(self, request):
        navigation_url = settings.OPENGROK_NAVIGATION_URL
        project_path = request.POST.get('project_path', '')
        file_path = request.POST.get('file_path', '')
        navigation_url = navigation_url +project_path + file_path
        response = requests.get(navigation_url).text
        
        #deal response
        response = response.replace("]],[","]]|[")
        if response:
            all_symbols = []
            for symbol in response.split("|"):
                symbol = json.loads(symbol)
                del symbol[1]
                all_symbols.append(symbol)
            print(all_symbols)
            return HttpResponse(json.dumps({"status": "success", "msg": all_symbols}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({"status": "failed", "msg": 'null'}), content_type='application/json')

class ShowMethodInfo(View):
    """
        获取当前方法的具体信息
    """
    pass
    # def post(self ,request):
    #     search_url = settings.


class AddAnnotationView(View):
    """
       为某行代码添加注释
    """
    def post(self, request):
        # if not request.user.is_authenticated():
        #     return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        content = request.POST.get('content', '')
        file_id = int(request.POST.get('file_id', ''))
        linenum = int(request.POST.get('linenum', ''))
        if int(file_id) > 0 and content:
            # 看用户是否已经添加过注释
            # exist_record = Annotation.objects.filter(file_id=file_id, linenum=linenum, user_id=request.user.id)
            exist_record = Annotation.objects.filter(file_id=file_id, linenum=linenum, user_id=1)
            if exist_record:
                return HttpResponse('{"status":"success","msg":"你已经添加过注释，无法再次添加"}', content_type='application/json')
            else:
                try:
                    annotation = Annotation()
                    file = File.objects.get(id=file_id)
                    annotation.file_id = file_id
                    annotation.linenum = linenum
                    annotation.project_id = file.project_id
                    annotation.content = content
                    # annotation.user = request.user
                    annotation.user_id = 1
                    annotation.save()
                    return HttpResponse('{"status":"success","msg":"注释成功"}', content_type='application/json')
                except Exception as e:
                    return HttpResponse('{"status":"fail","msg":"参数传递错误，注释失败"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"注释失败"}', content_type='application/json')


class UpdateAnnotationView(View):
    """
       更新注释
    """
    def post(self, request):
        content = request.POST.get('content', '')
        annotation_id = int(request.POST.get('annotation_id', ''))
        annotation = Annotation.objects.get(id=annotation_id)
        annotation.content = content
        annotation.update_nums +=1
        annotation.save()
        return HttpResponse('{"status":"success","msg":"修改成功"}', content_type='application/json')


class AddQuestionView(View):
    def post(self, request):
        # if not request.user.is_authenticated():
        #     return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        content = request.POST.get('content', '')
        file_id = request.POST.get('file_id', '')
        linenum = request.POST.get('linenum', '')
        if int(file_id) > 0 and content:
            question = Question()
            question.content = content
            # question.user = request.user
            question.user_id = 1
            question.linenum = linenum
            question.file_id = file_id
            file = File.objects.filter(id=file_id)
            if file[0]:
                question.project_id = file[0].project_id
            else:
                return HttpResponse('{"status":"fail","msg":"参数错误，提问失败"}', content_type='application/json')
            question.save()
            return HttpResponse('{"status":"success","msg":"提问成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"提问失败"}', content_type='application/json')


class UpdateQuestionView(View):
    def post(self, request):
        try:
            content = request.POST.get('content', '')
            question_id = int(request.POST.get('question_id', ''))
            question = Question.objects.get(id=question_id)
            question.content = content
            question.save()
            return HttpResponse('{"status":"success","msg":"修改成功"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"fail","msg":"参数传递错误，更新失败"}', content_type='application/json')


class AddAnswerView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        content = request.POST.get('content', '')
        question_id = request.POST.get('question_id', '')
        if int(question_id) > 0 and content:
            try:
                answer = Answer()
                question = Question.objects.get(id=question_id)
                answer.question_id = question.id
                answer.content = content
                answer.user = request.user
                answer.save()
                answer = serializers.serialize("json", [answer, ])
                return HttpResponse(json.dumps({"status": "success", "answer": answer}),
                                content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"fail","msg":"参数传递错误，回答失败"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"回答失败，请重新回答"}', content_type='application/json')


class UpdateAnswerView(View):
    def post(self, request):
        try:
            content = request.POST.get('content', '')
            answer_id = int(request.POST.get('answer_id', ''))
            answer = Answer.objects.get(id=answer_id)
            answer.content = content
            answer.save()
            return HttpResponse('{"status":"success","msg":"修改成功"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"fail","msg":"参数传递错误，更新回答失败"}', content_type='application/json')


class AddArticleView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        article_form = NewArticleForm(request.POST)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.save()
            article.save_m2m()

            return render(request, 'projects/article.html', locals())


class UpdateArticleView(View):
    def post(self, request):
        try:
            article = Article.objects.get(pk=id)
            form = NewArticleForm(request.POST, instance=article)
            form.save()
            return HttpResponse('{"status":"success","msg":"更新成功"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"fail","msg":"参数传递错误，更新失败"}', content_type='application/json')


class AddCommentView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        content = request.POST.get('content', '')
        type = request.POST.get('type', '')
        object_id = int(request.POST.get('object_id', ''))
        if object_id > 0 and content:
            try:
                if type == 'annotation':
                    comment = AnnotationComment()
                    annotation = Annotation.objects.get(id=object_id)
                    comment.annotation_id = annotation.id
                elif type == 'question':
                    comment = QuestionComment()
                    question = Question.objects.get(id=object_id)
                    comment.question_id = question.id
                elif type == 'issue':
                    comment = IssueComment()
                    issue = Issue.objects.get(id=object_id)
                    comment.issue_id = issue.id
                elif type == 'answer':
                    comment = AnswerComment()
                    answer = Answer.objects.get(id=object_id)
                    comment.answer_id = answer.id
                elif type == 'article':
                    comment = ArticleComment()
                    article = Article.objects.get(id=object_id)
                    comment.article_id = article.id
                else:
                    return HttpResponse('{"status":"fail","msg":"参数传递错误，无法找到评论对象"}', content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"fail","msg":"参数传递错误，评论失败"}', content_type='application/json')
            comment.content = content
            comment.user = request.user
            comment.save()
            return HttpResponse('{"status":"success","msg":"评论成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"评论失败"}', content_type='application/json')


class UpdateCommentView(View):
    def post(self, request):
        content = request.POST.get('content', '')
        type = request.POST.get('type', '')
        object_id = request.POST.get('object_id', '')
        if int(object_id) > 0 and content:
            try:
                if type == 'annotation':
                    comment = AnnotationComment.objects.get(id=object_id)
                elif type == 'question':
                    comment = QuestionComment.objects.get(id=object_id)
                elif type == 'issue':
                    comment = IssueComment.objects.get(id=object_id)
                elif type == 'answer':
                    comment = AnswerComment.objects.get(id=object_id)
                elif type == 'article':
                    comment = ArticleComment.objects.get(id=object_id)
                else:
                    return HttpResponse('{"status":"fail","msg":"参数传递错误，评论失败"}', content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"fail","msg":"参数传递错误，评论失败"}', content_type='application/json')
            comment.content = content
            comment.save()
        return HttpResponse('{"status":"success","msg":"修改成功"}', content_type='application/json')


class AnswerOptionIssueView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        choices = request.POST.get('choices', '')
        issue_id = int(request.POST.get('issue_id', ''))
        if issue_id > 0 and choices:
            exist_records = IssueAnswer.objects.filter(user_id=request.user.id, issue_id=issue_id)
            if exist_records:
                return HttpResponse('{"status":"success","msg":"你已经回答过这个issue"}', content_type='application/json')
            try:
                answer = IssueAnswer()
                issue_standard_choices = IssueStandardAnswers.objects.get(issue_id=issue_id).choice_position
                answer.issue_id = issue_id
                answer.content = choices
                answer.user = request.user
                if choices != issue_standard_choices:
                    answer.correct = False
                    answer.save()
                    return HttpResponse(json.dumps({"status": "success", "msg": "答案错误", "answer": issue_standard_choices}), content_type='application/json')
                answer.save()
                return HttpResponse(json.dumps({"status": "success", "msg": "答案正确", "answer": issue_standard_choices}), content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"fail","msg":"参数传递错误，回答失败"}', content_type='application/json')

        else:
            return HttpResponse('{"status":"fail","msg":"回答失败"}', content_type='application/json')
        pass


class AnswerQuestionIssueView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        content = request.POST.get('content', '')
        issue_id = int(request.POST.get('issue_id', ''))
        if issue_id > 0 and content:
            answer = IssueAnswer()
            answer.issue_id = issue_id
            answer.content = content
            answer.user = request.user
            answer.save()
            answer = serializers.serialize("json", [answer,])
            return HttpResponse(json.dumps({"status": "success", "msg": "回答成功", "answer": answer}),
                                content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"回答失败，请重新回答"}', content_type='application/json')


class AddVoteView(View):
    def post(self, request):
        type = request.POST.get('type', 0)
        object_id = int(request.POST.get('object_id', ''))
        vote_value = request.POST.get('vote_value', 0)
        # if not request.user.is_authenticated():
        #     return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        exist_records = Vote.objects.filter(user=request.user, vote_type_id=object_id, vote_type=type)
        # exist_records = Vote.objects.filter(user_id=1, vote_type_id=object_id, vote_type=type)
        try:
            if type == 'question':
                object = Question.objects.get(id=object_id)
            elif type == 'answer':
                object = Answer.objects.get(id=object_id)
            elif type == 'article':
                object = Article.objects.get(id=object_id)
            elif type == 'annotation':
                object = Annotation.objects.get(id=object_id)
            elif type == 'issue':
                object = Issue.objects.get(id=object_id)
            elif type == 'issue_answer':
                object = IssueComment.objects.get(id=object_id)
            elif type == 'question_comment':
                object = QuestionComment.objects.get(id=object_id)
            elif type == 'answer_comment':
                object = AnswerComment.objects.get(id=object_id)
            elif type == 'article_comment':
                object = ArticleComment.objects.get(id=object_id)
            elif type == 'annotation_comment':
                object = AnnotationComment.objects.get(id=object_id)
            elif type == 'file':
                object = File.objects.get(id=object_id)
            else:
                return HttpResponse('{"status":"fail","msg":"类型传递错误"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"fail","msg":"参数传递错误"}', content_type='application/json')
        if exist_records:
            exist_records.delete()
            object.vote -= 1
            object.save()
            return HttpResponse('{"status":"success", "info":"cancel","value":"-1","msg": "取消成功"}',
                                content_type='application/json')
        else:
            vote = Vote()
            if object_id > 0 and type is not '':
                vote.user = request.user

                vote.vote_type = type
                vote.vote_type_id = object_id
                vote.value = vote_value
                vote.save()
                object.vote += 1
                object.save()
                return HttpResponse('{"status":"success","value":"1","msg":"点赞成功"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail","msg":"参数传递错误"}', content_type='application/json')


class AcceptAnswerView(View):
    def post(self, request):
        question_id = int(request.POST.get('question_id', ''))
        answer_id = int(request.POST.get('answer_id', ''))
        if question_id > 0 and answer_id > 0:
            try:
                question = Question.objects.get(id=question_id)
                answer = Answer.objects.get(id=answer_id)
                question_state = question.state
                if question_state == '2':
                    question.state = '6'
                elif question_state == '6':
                    return HttpResponse('{"status":"fail","msg":"问题已经解决"}', content_type='application/json')
                elif question_state == '4':
                    return HttpResponse('{"status":"fail","msg":"问题已经关闭"}', content_type='application/json')
                else:
                    return HttpResponse('{"status":"fail","msg":"问题已经锁定"}', content_type='application/json')
                question.save()
                answer.accept = True
                answer.save()
                return HttpResponse('{"status":"success","msg":"已成功采纳答案"}', content_type='application/json')
            except Exception as e:
                return HttpResponse('{"status":"fail","msg":"没有找到对象"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"参数传递错误"}', content_type='application/json')
