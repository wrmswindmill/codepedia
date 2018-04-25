from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.db.models import Count
import os
import logging
from datetime import datetime

from .task import import_project
from .models import Project, File
from .forms import NewProjectForm
from operations.models import Article, Annotation, Issue, QuestionAnswer
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from utils import get_project_tree

logger = logging.getLogger('django')
sourcepath = settings.SOURCEPATH


class NewProjectView(View):
    def get(self, request):
        project_form = NewProjectForm()
        return render(request, 'projects/new.html', locals())

    def post(self, request):
        project_form = NewProjectForm(request.POST)
        if project_form.is_valid():
            # logging.info('开始尝试导入工程')
            project = project_form.save(commit=False)
            project.save()
            project_form.save_m2m()
            project_id = project.id
            root_path = project.path
            try:
                # logging.info(str(datetime.now()) + '准备导入工程')
                import_project(project_id, root_path)
                # logging.info(str(datetime.now()) + '导入工程完成')
                all_projects = Project.objects.all()
                return render(request, 'projects/list.html', locals())
            except Exception as e:
                # logging.error(str(datetime.now()) + ' 导入' + str(project.name) + '失败，错误原因是：' + str(e) + '准备删除工程')
                # logging.info(str(datetime.now()) + '开始删除导入本工程，稍后重新导入')
                project.delete()
                # logging.info(str(datetime.now()) + '删除完成稍后重新导入')
                error_msg = '导入失败，请查看日志发现错误后重新导入'
                return render(request, 'projects/new.html', locals())


class ProjectListView(View):
    def get(self, request):
        all_projects = Project.objects.all()
        # 工程排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == '':
                all_projects = all_projects.order_by('-created')
            elif sort == 'hot':
                all_projects = all_projects.order_by('-views')
        # return render(request, 'projects/project-list.html', {'all_projects': all_projects,
        #                                                       'sort': sort,
        #                                                       })
        return render(request, 'projects/project-list.html', locals())


class ProjectInfoView(View):
    def get(self, request, name):
        project = Project.objects.filter(name=name).first()
        articles = Article.objects.filter(project_id=project.id)
        return render(request, 'projects/info.html', locals())

# FIXME
# 每一行问题的数量有待修复
# 目前做的是总数/3,但是对于问答题而言，应该是全部都要算上的
# class ProjectSourceView_Before(View):
#     def get(self, request, name, path):
#         project = Project.objects.filter(name=name).first()
#         # 判断是否是根目录

#         #parent_dir保存了上一级目录
#         if path=='/':
#             file = File.objects.filter(path='', project=project).first()
#             parent_dir = None
#         else:
#             file = File.objects.filter(path=path, project=project).first()
#             parent_dir = path[:path.rindex("/")]
        
#         #默认会进入当前文件夹的第一个文件，如果当前文件夹没有任何的文件，那么进入指定的文件
#         enter_project_url = "/src/net/micode/notes/gtask/data/TaskList.java"
       
#         # 判断当前文件是否是文件夹
#         # 获取目录
#         path = file.path.split('/')        
#         path_dict = {}
#         for i in range(1, len(path)):
#             path_dict[path[i]] = '/'.join(path[:i + 1])
            
#         #file.type=1 means it's a dir
#         #file.type=0 means it's a file
#         if file.type == '1':
            
#             #enter_flag如果当前文件夹下有文件，
#             #那么将它设置为False，并将enter_project_url改为第一个文件的path
#             enter_flag = True
#             files = File.objects.filter(super_path=file, project=project)
            
#             annos_count = {}
#             for file in files:
#                 if enter_flag and file.type=='0':
#                     enter_project_url = file.path;
#                     enter_flag = False
#                 # 取出每个文件的注释数量
#                 anno_count = Annotation.objects.filter(file=file).count()
#                 # print("%s:%i"%(file.name,anno_count))
#                 if anno_count > 0:
#                     annos_count[file.name] = str(anno_count)
#             return render(request, 'projects/directory.html', locals())
        
#         else:
#             print(11111111)
#             print(request.user)
#             # 按linenum取出注释数目 返回结果是 <QuerySet [{'linenum': 0, 'nums': 1}, {'linenum': 1, 'nums': 2}, {'linenum': 2, 'nums': 2}]>
#             # 因此需要进行一个转化
#             # 这是django中分组的一种写法
#             annos = Annotation.objects.filter(file=file).values('linenum').annotate(nums=Count('linenum'))
#             annos_count = {}
#             for i in annos:
#                 annos_count[str(i['linenum'])] = i['nums']
#             # 两种问题，一种是问答题一种是选择题
#             # 对于选择题而言，是从三种问题中随机选择一个的
#             # 对于问答题而言，目前应该是全部选择
#             #  issue_type=1对应选择题，issue_type=2对应这问答题
#             issues=choose_issue_type_1(file)
            
#             question_count = {}
#             for key in issues:
#                 question_count[key]=len(issues[key])//2

#             project_tree = get_project_tree.getHtml(settings.SOURCEPATH+project.path)

#             return render(request, 'projects/source.html', locals())           


class ProjectSourceView(View):
    def get(self, request, name, path):
        project = Project.objects.filter(name=name).first()
        # 判断是否是根目录      
        print(request.user)
        project_tree = get_project_tree.getHtml(settings.SOURCEPATH+project.path)
        return render(request, 'projects/source.html', locals())

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



#文件列表页
class FileListlView(View):
    def get(self, request):
        all_files = File.objects.all()
        hot_blobs = File.objects.order_by('-views')[:5]

        sort = request.GET.get('sort', '')
        if sort=='' or sort=="hot":
            all_files = all_files.order_by('-anno_num')
        else:
            all_files = all_files.order_by('-create_time')
        #分页功能
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_files, 10,  request=request)
        files = p.page(page)

        return render(request, 'projects/file-list.html', {
            'all_files': files,
            'hot_objs': hot_blobs,
        })




#获取工程树形结构
# def tree_method(request, project_id):
#     project = Project.objects.get(id=project_id)
#     client = Client('http://localhost:7777/pro?wsdl')
#     response = client.service.getTree(project.path)
#     response = json.loads(response)
#     return JsonResponse(response)


