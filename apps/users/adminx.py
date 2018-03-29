from django.contrib import admin
import xadmin
from xadmin import views
from .models import School, Grade, User


class BaseSetting(object):

    enable_themes = True # 主题
    use_bootswatch = True


class GlobalSettings(object):
    #管理页头 和底部
    site_title = "Codepedia"
    site_footer = "Trustie-Group"
    menu_style = "accordion" #折叠菜单


class SchoolAdmin(object):
    pass


class GradeAdmin(object):
    pass


class UserAdmin(object):
    pass


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(School, SchoolAdmin)
#xadmin.site.register(User, UserAdmin)
xadmin.site.register(Grade, GradeAdmin)