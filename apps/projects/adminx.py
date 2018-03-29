from django.contrib import admin
import xadmin

from .models import Language, Project, File

class LanguageAdmin(object):
    pass

class ProjectAdmin(object):
    pass


class FileAdmin(object):
    pass



xadmin.site.register(Language, LanguageAdmin)
xadmin.site.register(Project, ProjectAdmin)
xadmin.site.register(File, FileAdmin)
