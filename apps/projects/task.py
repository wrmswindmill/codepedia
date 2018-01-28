import os
from projects.models import File

source_path = '/Users/yujie/workspace/opengrok/source/'
import logging
from datetime import  datetime
logger = logging.getLogger('django')


def gci(path, depth, project_id, root_path):
    parents = os.listdir(path)
    for parent in parents:
        child = os.path.join(path, parent)
        # 文件名
        try:
            logging.info(str(datetime.now()) + '准备导入工程子文件夹')
            file = File()
            # 处理文件名字
            file.name = child.split('/')[-1]
            # 处理文件相对路径
            file.path = child.replace(root_path, '')
            file.owner = 1
            # 判断是否是首层目录
            super_path = '' if depth == 0 else path.replace(root_path, '')
            # 处理文件的上级目录
            super_file = File.objects.filter(path=super_path, project_id=project_id).first()
            file.super_path_id = super_file.id
            # 处理文件所属工程
            file.project_id = project_id
            # 判断文件类型 若为文件夹，则类型为1 若为文件，则类型为0
            if os.path.isdir(child):
                file.type = 1
                file.save()
                logging.info(str(datetime.now()) + '导入' + str(file.path)+'成功')
                gci(child, depth + 1, project_id, root_path)
            else:
                file.type = 0
                file.save()
                logging.info(str(datetime.now()) + ' 导入' + str(file.path) + '成功')
        except Exception as e:
                logging.info(str(datetime.now()) + ' 导入' + str(child) + '失败，错误原因是：' + str(e))
                logging.info(str(datetime.now()) + '开始删除导入本工程文件，稍后重新导入')
                File.objects.filter(project_id=project_id).delete()
                logging.info(str(datetime.now()) + '删除完成稍后重新导入')


def import_project(project_id, rel_path):
    logging.info(str(datetime.now()) + '准备导入工程主文件夹')
    file = File()
    file.name = rel_path
    file.owner = 1
    file.type = 1
    file.project_id = project_id
    file.save()
    logging.info(str(datetime.now()) + '导入' + str(file.path) + '工程主文件夹成功，准备递归导入子文件夹')
    root_path = os.path.join(source_path, rel_path)
    gci(root_path, 0, project_id, root_path)