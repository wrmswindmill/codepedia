import os
import sys
pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd+"../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Codepedia2.settings")
import django
django.setup()


source_path = '/Users/yujie/workspace/opengrok/source/'
rel_path = 'Notes'
root_path = os.path.join(source_path, rel_path)
files = os.listdir(root_path)
from projects.models import File


def gci(path, depth):
    parents = os.listdir(path)
    for parent in parents:
        child = os.path.join(path, parent)
        # 文件名
        file = File()
        file.name = child.split('/')[-1]
        print(child.split('/')[-1])
        # 文件相对路径
        file.path = child.replace(root_path, '')
        file.owner = 1

        print(child.replace(root_path, ''))
        # 处理首层目录]
        super_path = '' if depth == 0 else path.replace(root_path, '')
        print(super_path)
        super_file = File.objects.filter(path=super_path , project_id = 1).first()
        file.super_path_id = super_file.id
        file.project_id = 1
        # 处理类型
        if os.path.isdir(child):
            print('1')
            file.type = 1
            file.save()
            gci(child, depth + 1)
        else:
            print('0')
            file.type = 0
            file.save()


if __name__ == '__main__':
    # file = File()
    # file.name = rel_path
    # file.owner = 1
    # file.type = 1
    # file.project_id = 1
    # file.save()
    # gci(root_path, 0)
    import datetime
    print(datetime.datetime.now())
