import os
from projects.models import Project


url_head = "/projects"
project_name = ""
project_id = ""

# 将叶子节点的href替换成url
# 传入一个工程根目录路径，返回一个project_tree对应的html代码
# 思路是基于递归的深度优先遍历
def getHtml(projectPath):
    global project_name,project_id
    project_name = projectPath[projectPath.rfind('/')+1:]
    project_id = str(Project.objects.get(name=project_name).pk)
    
    html_str = "<ul>"
    files = os.listdir(projectPath)
    
    for i in range(len(files)):
        filePath = projectPath + os.path.sep + files[i]

        if os.path.isdir(filePath):
            tag_html = '<li class = "parent-item">\n'
            tag_html += '<a href = "javascript:void(0)" onclick=add_tab("%s","/%s","/%s") class = "item" show = "0" ><i class = "fa fa-folder color-blue"></i> %s </a>\n' % (
                project_id,files[i], files[i], files[i])
            tag_html += getInnerHtml(projectPath, filePath)
            tag_html += '</li>\n'
        else:
            # 叶子节点，替换成绝对路径
            url = url_head+"/"+project_name+"/"+files[i]
            tag_html = '<li><a href="javascript:void(0)" onclick=add_tab("%s","/%s","/%s") class = "item"><i class = "fa fa-file-text-o color-blue"></i >  %s </a></li>\n' % (
                project_id,files[i], files[i], files[i])

        html_str += tag_html
    html_str += "</ul>"
    return html_str

# 合并文件夹（将下级只有一个文件夹的连续文件夹拼接）
# 例如，假设net目录下只有ui目录，ui目录下只有css目录，css下有1.css，2.css，
# 那么就将net,ui,css合并成net/ui/css/
def getFiles(path):
    files = os.listdir(path)
    flag = False
    while len(files) == 1 and os.path.isdir(path + os.path.sep + files[0]):
        path = path + os.path.sep + files[0]
        files = os.listdir(path)
        flag = True

    return path, files, flag


def getInnerHtml(projectPath, path):
    html_str = '<ul class = "item sub-item" >\n'
    # files = os.listdir(path)
    path_before = path
    path, files, flag = getFiles(path)
    # print(path)
    for i in range(len(files)):
        filePath = path + os.path.sep + files[i]

        index = path.find(project_name)
        relative_path = path[index+len(project_name):]+"/"+files[i]

        if os.path.isdir(filePath):
            tag_html = '<li>\n'
            # 如果有多级层叠的情况
            if flag:
                tag_html += '<a href = "javascript:void(0)" onclick=add_tab("%s","%s","/%s") class = "item" show = "0" ><i class = "fa fa-folder color-blue"></i> %s </a>\n' % (
                    project_id,relative_path, files[i], path.replace(path_before, '')+"/"+files[i])
            else:
                tag_html += '<a href = "javascript:void(0)" onclick=add_tab("%s","%s","/%s") class = "item" show = "0" ><i class = "fa fa-folder color-blue"></i> %s </a>\n' % (
                    project_id,relative_path, files[i], files[i])
            tag_html += getInnerHtml(projectPath, filePath)
            tag_html += '</li>\n'
        else:
            # 替换成绝对路径
            # index = path.find(project_name)
            # url = url_head+"/"+path[index:]+"/"+files[i]
            # tag_html = '<li><a href="%s"><i class = "fa fa-file-text-o color-blue"></i > %s </a></li>\n' % (
            #     url, files[i])
            tag_html = '<li><a href="javascript:void(0)" onclick=add_tab("%s","%s","%s")><i class = "fa fa-file-text-o color-blue"></i > %s </a></li>\n' % (
                project_id,relative_path, files[i], files[i])
        html_str += tag_html
    html_str += '</ul>\n'
    return html_str
