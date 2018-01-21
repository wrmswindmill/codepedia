from django.shortcuts import render
from django.views import View
# Create your views here.
from .forms import  NewProjectForm
from django.conf import  settings
import os



sourcepath = settings.SOURCEPATH


class NewProjectView(View):
    def get(self, request):
        project_form = NewProjectForm()
        return  render(request, 'projects/new.html', locals())

    def post(self, request):

        project_form = NewProjectForm(request.POST)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            project.save()
            project_form.save_m2m()
            project_id = project.id
            project_path = os.path.join(sourcepath, project.path)
            root_path = project.path
            


        print(1)

        pass