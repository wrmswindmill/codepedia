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
from operations.models import Article, Annotation, Question, Answer
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


class ProjectSourceView(View):
    def get(self, request, name, path):
        project = Project.objects.filter(name=name).first()
        # 判断是否是根目录
        if path=='/':
            file = File.objects.filter(path='', project=project).first()
        else:
            file = File.objects.filter(path=path, project=project).first()
        # 判断当前文件是否是文件夹
        # 获取目录
        path = file.path.split('/')
        path_dict = {}
        for i in range(1, len(path)):
            path_dict[path[i]] = '/'.join(path[:i + 1])
            # path_dict[path[i]] = 'projects/'+project.path+'/xref/'.join(path[:i + 1])

        #file.type=1 means it's a dir
        #file.type=0 means it's a file
        if file.type == '1':
            # get all files in current dir
            files = File.objects.filter(super_path=file, project=project)
            annos_count = {}
            for file in files:
                # 取出每个文件的注释数量
                anno_count = Annotation.objects.filter(file=file).count()
                print("%s:%i"%(file.name,anno_count))
                if anno_count > 0:
                    annos_count[file.name] = str(anno_count)
            return render(request, 'projects/directory.html', locals())
        
        else:
            # 按linenum取出注释数目 返回结果是 <QuerySet [{'linenum': 0, 'nums': 1}, {'linenum': 1, 'nums': 2}, {'linenum': 2, 'nums': 2}]>
            # 因此需要进行一个转化
            annos = Annotation.objects.filter(file=file).values('linenum').annotate(nums=Count('linenum'))
            annos_count = {}
            for i in annos:
                annos_count[str(i['linenum'])] = i['nums']
            
            # 按linenum取出问题数目 返回结果是 <QuerySet [{'linenum': 0, 'nums': 1}, {'linenum': 1, 'nums': 2}, {'linenum': 2, 'nums': 2}]>
            questions = Question.objects.filter(file=file).values('linenum').annotate(nums=Count('linenum'))
            question_count = {}
            for i in questions:
                question_count[str(i['linenum'])] = i['nums']

            project_tree = get_project_tree.getHtml(settings.SOURCEPATH+project.path)
            # project_tree=None
            # print(project.path)
            # project_tree = tree_method(request,project.path)
            # print(project_tree)

            return render(request, 'projects/source.html', locals())

#文件列表页
class FileListlView(View):
    def get(self, request):
        all_files = File.objects.all()
        # hot_blobs = File.objects.order_by('-views')[:5]
        #分页功能
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_files, 10,  request=request)
        files = p.page(page)

        return render(request, 'projects/file-list.html', {
            'all_files': files,
            # 'hot_objs': hot_blobs,
        })


from suds.client import Client
import json
from django.http import JsonResponse, HttpResponse

#获取工程树形结构
# def tree_method(request, project_id):
#     project = Project.objects.get(id=project_id)
#     client = Client('http://localhost:7777/pro?wsdl')
#     response = client.service.getTree(project.path)
#     response = json.loads(response)
#     return JsonResponse(response)


