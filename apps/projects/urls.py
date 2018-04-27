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
from .views import NewProjectView, ProjectListView, ProjectInfoView, ProjectSourceView, ScannerProjectView

app_name = "projects"
urlpatterns = [
    path('', ProjectListView.as_view(), name='list'),
    path('new/', NewProjectView.as_view(), name='new_project'),
    path('scanner_project/', ScannerProjectView.as_view(), name="scanner_project"),
    # path('<slug:name>/', ProjectInfoView.as_view(), name='info'),
    # path('<slug:name>/xref<path:path>', ProjectSourceView.as_view(), name='source')
    path('<str:name><path:path>', ProjectSourceView.as_view(), name='source')

]
