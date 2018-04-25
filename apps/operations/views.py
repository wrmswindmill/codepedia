from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.conf import settings

import json
import requests
from django.core import serializers
from django.db.models import Count
# Create your views here.


from .models import Annotation, Question, QuestionAnswer, Article, Issue, IssueAnswer, IssueStandardAnswers, IssueChoices
from .models import AnnotationComment, QuestionComment, QuestionAnswerComment, ArticleComment, IssueComment
from .models import Vote
from users.models import User
from .forms import NewArticleForm
from projects.models import File
from projects.models import Language,Project
from django.template.loader import render_to_string


class ShowAnnotationView(View):
    """
    获取某一行代码所有的注释
    """
    def post(self, request):
        # if not request.user.is_authenticated:
            # return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        file_id = int(request.POST.get('file_id', ''))
        line_num = int(request.POST.get('line_num', ''))
        # file_id = 118
        # line_num = 1
        # annotations 
        annotations = Annotation.objects.filter(file_id=file_id, linenum=line_num)
        
        # users = set()
        anno_ids = []
        for anno in annotations:
            anno_ids.append(anno.id)
            # users.add(anno.user)

        anno_comments = AnnotationComment.objects.filter(annotation_id__in=anno_ids)
        anno_comments = sorted(anno_comments, key=lambda anno_comment: anno_comment.annotation_id)

        html_str = render_to_string('projects/filesub/annotation.html', {'linenum':line_num,'annos': annotations,"anno_comments":anno_comments})
        print(html_str)
        return HttpResponse(json.dumps({"status": "success","html_str":html_str}), content_type='application/json')

class ShowIssueView(View):
    """
       获取某一行代码所有的提问
    """
    def post(self, request):
        # file_id = int(request.POST.get('file_id', ''))
        line_num = request.POST.get('line_num', '')
        print(line_num)

        issue_id_type = request.POST.get('issue_id_type', '')
        issue_id_type = issue_id_type[1:len(issue_id_type)-1]

        list1 = issue_id_type.split(",")

        issue_ids = []
        for i in range(0, len(list1), 2):
            issue_ids.append(list1[i])

        issues = Issue.objects.filter(id__in=issue_ids)
        issueChoices = IssueChoices.objects.filter(issue__in=issues)
        issueAnswers = IssueAnswer.objects.filter(issue__in=issues, user_id=1)
        # print(issueAnswer)
        issueStandardAnswer = IssueStandardAnswers.objects.filter(
            issue__in=issues)

        comments = IssueComment.objects.filter(issue__in=issues)
        print(issueStandardAnswer)
        print(comments)
        # issues = serializers.serialize("json", issues)
        # issueChoices = serializers.serialize("json",issueChoices)

        html_str = render_to_string('projects/filesub/question.html', {'linenum': line_num, 'issues': issues, 'issueChoices': issueChoices,
                                                                       'issueAnswers': issueAnswers, 'issueStandardAnswer': issueStandardAnswer, 'comments': comments})
        print(html_str)
        return HttpResponse(json.dumps({"status": "success", "html_str": html_str}), content_type='application/json')

        # question_ids = []
        # for question in questions:
        #     question_ids.append(question.id)
        # question_comments = QuestionComment.objects.filter(
        #     question_id__in=question_ids)
        # question_comments = sorted(
        #     question_comments, key=lambda question_comment: question_comments.question_id)

        return HttpResponse(json.dumps({"status": "success", "issues": issues, "issueChoices": issueChoices}), content_type='application/json')


class ShowQuestionView(View):
    def post(self, request):
        line_num = request.POST.get('line_num', '')
        file_id = request.POST.get('file_id', '')

        questions = Question.objects.filters(file_id=file_id,line_num=line_num)
        answers =QuestionAnswer.objects.filters(question__in=questions)
        comments = QuestionAnswerComment.objects.filters(answer__in=answers)
        # issues = serializers.serialize("json", issues)
        # issueChoices = serializers.serialize("json",issueChoices)

        # html_str = render_to_string('projects/filesub/question.html', {'linenum': line_num, 'issues': issues, 'issueChoices': issueChoices,
                                                                        # 'issueAnswers': issueAnswers, 'issueStandardAnswer': issueStandardAnswer, 'comments': comments})
        # print(html_str)
        # return HttpResponse(json.dumps({"status": "success", "html_str": html_str}), content_type='application/json')

    
class ShowNavigationView(View):
    """
       获取当前文件的Structure，也就是Package,Class，Method信息。
    """
    def post(self, request):
        navigation_url = settings.OPENGROK_NAVIGATION_URL
        project_path = request.POST.get('project_path', '')
        file_path = request.POST.get('file_path', '')
        print(file_path)
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
            # print(all_symbols)
            return HttpResponse(json.dumps({"status": "success", "msg": all_symbols}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({"status": "failed", "msg": 'null'}), content_type='application/json')


class ShowMethodInfo(View):
    """
        获取当前方法的具体信息
        return 
    """
    def post(self, request):
        method_query_url = settings.OPENGROK_SEARCH_URL
        query_str = request.POST.get('args','')
        # query_str = "refs = Note & project = Notes"
        for arg_str in query_str.split("&"):
            para_value = arg_str.split("=")
            if len(para_value)==2 and para_value[0]=='project':
                project_name = para_value[1]
                project = Project.objects.filter(name=project_name).first()
                if project.language is None:
                    #发邮件通知我出问题了
                    pass
                else:
                    languageObj=Language.objects.filter(name=project.language).first()
                    if languageObj is not None:
                        query_str+= "&project="+languageObj.src
        print(query_str)
        url = method_query_url+query_str
        query_result = requests.get(url).text
        print(query_result)
        if query_result is not None:
            result_dict = json.loads(query_result)
            results = result_dict['results']
            print("--------------------------------------------------")
            print(results)
            if len(results)>0:
                return HttpResponse(json.dumps({"status": "success", "msg": results, "url": settings.OPENGROK_NAVIGATION_URL}), content_type='application/json')
        return HttpResponse(json.dumps({"status": "failed", "msg": []}), content_type='application/json')

# FIXME
# 还没有获取用户id，需要从request中获取用户id
class AddAnnotationView(View):
    """
       为某行代码添加注释
    """
    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        print(request)
        content = request.POST.get('content', '')
        print(content)
        file_id = int(request.POST.get('file_id', ''))
        linenum = int(request.POST.get('linenum', ''))
        if int(file_id) > 0 and content:
            # 看用户是否已经添加过注释
            # exist_record = Annotation.objects.filter(file_id=file_id, linenum=linenum, user_id=request.user.id)
            exist_record = Annotation.objects.filter(file_id=file_id, linenum=linenum, user_id=request.user.id)
            if exist_record:
                return HttpResponse('{"status":"fail","msg":"你已经添加过注释，无法再次添加"}', content_type='application/json')
            else:
                try:
                    annotation = Annotation()
                    file = File.objects.get(id=file_id)
                    annotation.file_id = file_id
                    annotation.linenum = linenum
                    annotation.project_id = file.project_id
                    annotation.content = content
                    annotation.user = request.user
                    # annotation.user_id = 1
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

#FIXME
class AddQuestionView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        
        content = request.POST.get('content', '')
        file_id = request.POST.get('file_id', '')
        linenum = request.POST.get('linenum', '')
        if int(file_id) > 0 and content:
            question = Question()
            question.content = content
            question.user = request.user
            # question.user_id = 1
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
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        content = request.POST.get('content', '')
        issue_id = request.POST.get('issue_id', '')

        if int(issue_id) > 0 and content:
            exist_record = IssueAnswer.objects.filter(issue_id=issue_id,user_id=1)
            if exist_record:
                 return HttpResponse('{"status":"fail","msg":"您已回到过问题了"}', content_type='application/json')
            try:
                answer = IssueAnswer()
                issue = Issue.objects.get(id=issue_id)
                answer.issue_id = issue.pk
                answer.content = content
                answer.user = request.user
                answer.save()
                answer = serializers.serialize("json", [answer,])
                return HttpResponse(json.dumps({"status": "success","msg":"回答成功", "answer": answer}),
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
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({"status": "fail", "msg": "用户未登录"}), content_type='application/json')
        # print(11111)
        content = request.POST.get('content', '')
        type = request.POST.get('type', '')        
        object_id = int(request.POST.get('object_id', ''))
        print(content,type,object_id)
        if object_id > 0 and content:
            try:
                if type == 'annotation':
                    comment = AnnotationComment()
                    annotation = Annotation.objects.get(id=object_id)
                    comment.annotation_id = annotation.id
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
            return HttpResponse(json.dumps({"status":"success","msg":"评论成功","username":comment.user.nick_name}), content_type='application/json')
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

#TODO
#目前Hotest问题是针对所有回答了的问题而言的
#如果回答数量不够，那么按照更新时间排序
#目前不针对所有的文件，就针对当前的文件
import operator
class GetHotestIssuesView(View):
    def post(self, request):
        num = int(request.POST.get("question_num"))
        path = request.POST.get("path")
        project_id = request.POST.get("project_id")
        file = File.objects.get(project_id=project_id,path=path)
        # 获取当前文件所有的问题
        issues_origin = Issue.objects.filter(file=file)
        # 获取当前文件所有的问题的回答数目
        issue_answernum={}
        issueAnswers = IssueAnswer.objects.filter(issue__in=issues_origin)
        for issueAnswer in issueAnswers:
            if issueAnswer.issue_id in issue_answernum:
                issue_answernum[issueAnswer.issue_id]+=1
            else:
                issue_answernum[issueAnswer.issue_id] = 1
        # 按照回答数将问题排序
        issues_num=[]
        for issue in issues_origin:
            if issue.pk in issue_answernum:
                issues_num.append((issue,issue_answernum[issue.pk]))
        sorted_issues=[]
        if len(issues_num)>0:
            tmp_issues = sorted(issues_num, key=lambda tuple1: tuple1[1])
            for i in range(len(tmp_issues)):
                sorted_issues.append(tmp_issues[i][0])
        #如果当前已经回答的问题比问题数目要多
        if len(sorted_issues)>=num:
            issues = sorted_issues[0:num]
        #如果当前回答的问题比总问题数目要少
        else:
            issues = sorted_issues
            count = len(sorted_issues)
            for i in range(len(issues_origin)):
                if count>=num:
                    break;
                if issues_origin[i].pk not in issue_answernum:
                    issues.append(issues_origin[i])
                    count += 1
        # print(issues)
        html_str = render_to_string('projects/filesub/hotest_issue.html', {'issues': issues})
        # print(html_str)
        return HttpResponse(json.dumps({"status": "success", "html_str": html_str}), content_type='application/json')

# Backup
# class GetHotestIssuesView(View):
#     def post(self, request):
#         num = request.POST.get("question_num");
#         file_id = request.POST.get("file_id")
#         # 根据file_id获取project_id以及path，并判断文件类型
#         project_id = request.POST.get("project_id")
#         file_type = request.POST.get("file_type")

#         #获取对应的问题
#         #如果是文件级别的，直接获取当前文件的即可
#         if file_type=='file':
#             file = File.objects.get(path="%s"%(path))
#             file_id =file.pk
#             issues = Issue.objects.filter(file_id=file_id)
#         # 如果是根目录级别的，也可以直接获取所有文件的
#         elif file_type=='rootdir':
#             issue = Issue.object.filter(project_id=project_id)
#         # 否则就是普通目录级别了
#         else:
#             # 根据path获取当前path下所有的文件的FileId
#             file_ids = set()
#             for file in File.objects.filter(path__startswith="%s"%(path)):
#                 file_ids.add(file.pk)
#             # 获取当前项目的所有问题
#             issues = Issue.objects.filter(file_id__in=file_ids)
        
#         # #获取当前项目所有回答过问题的题目
#         # #可能会有问题
#         # issue_answers = IssueAnswer.objects.filter(project_id=project_id).values('issue_id').annotate(nums=Count('issue_id')).order_by('nums')
#         # for issue in issue_answers:
#         #     if issue.issue_id in 

#         # 排序
#         if len(issues)>num:
#             issues = issues[0:num]
#         html_str = render_to_string('projects/filesub/hotest_issue.html', {'issues':issues})
#         print(html_str)
#         return HttpResponse(json.dumps({"status": "success", "html_str": html_str}), content_type='application/json')


def choose_issue_type_1(file):
    all_issues_origin = Issue.objects.filter(file=file, issue_type=1)

    issues = {}
    # 行号，对应的的问题id，以及问题的类型
    for issue in all_issues_origin:
        currentline = str(issue.linenum)
        if currentline in issues:
            issues[currentline].append(issue.id)
            issues[currentline].append(issue.issue_type)
        else:
            issues[currentline] = [issue.id, issue.issue_type]
    return issues


class Get_CodeReading_Content_View(View):
    def post(self,request):
        project_id = request.POST.get("project_id")
        path = request.POST.get("path")

        project = Project.objects.filter(id=project_id).first()
        file = File.objects.filter(path=path, project_id=project_id).first()

        annos = Annotation.objects.filter(file=file).values('linenum').annotate(nums=Count('linenum'))
        annos_count = {}
        for i in annos:
            annos_count[str(i['linenum'])] = i['nums']
        
        issues=choose_issue_type_1(file)
        question_count = {}
        for key in issues:
            question_count[key]=len(issues[key])//2

        html_str = render_to_string('projects/filesub/code-reading.html',locals())
        # print(html_str)
        return HttpResponse(json.dumps({"status": "success", "html_str": html_str}), content_type='application/json')
