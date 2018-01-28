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
logger = logging.getLogger('django')

sourcepath = settings.SOURCEPATH


class NewProjectView(View):
    def get(self, request):
        project_form = NewProjectForm()
        return render(request, 'projects/new.html', locals())

    def post(self, request):
        project_form = NewProjectForm(request.POST)
        if project_form.is_valid():
            logging.info('开始尝试导入工程')
            project = project_form.save(commit=False)
            project.save()
            project_form.save_m2m()
            project_id = project.id
            root_path = project.path
            try:
                logging.info(str(datetime.now()) + '准备导入工程')
                import_project(project_id, root_path)
                logging.info(str(datetime.now()) + '导入工程完成')
                all_projects = Project.objects.all()
                return render(request, 'projects/list.html', locals())
            except Exception as e:
                logging.error(str(datetime.now()) + ' 导入' + str(project.name) + '失败，错误原因是：' + str(e) + '准备删除工程')
                logging.info(str(datetime.now()) + '开始删除导入本工程，稍后重新导入')
                project.delete()
                logging.info(str(datetime.now()) + '删除完成稍后重新导入')
                error_msg = '导入失败，请查看日志发现错误后重新导入'
                return render(request, 'projects/new.html', locals())


class ProjectListView(View):
    def get(self, request):
        all_projects = Project.objects.all()
        return render(request, 'projects/list.html', locals())


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
        print(path_dict)
        if file.type == '1':
            files = File.objects.filter(super_path=file, project=project)
            # 取出每个文件或文件夹的的注释
            annos_count = {}
            for file in files:
                # 取出每个文件的注释数量
                anno_count = Annotation.objects.filter(file=file).count()
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

            return render(request, 'projects/source.html', locals())

