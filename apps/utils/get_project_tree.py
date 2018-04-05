import os

def getHtml(path):
    html_str = "<ul>"
    files = os.listdir(path)
    for i in range(len(files)):
        filePath = path + os.path.sep + files[i]

        if os.path.isdir(filePath):
            tag_html = '<li class = "parent-item">\n'
            tag_html += '<a href = "javascript:void(0)" class = "item" show = "0" > %s </a>\n' % (
                files[i])
            tag_html += getInnerHtml(filePath)
            tag_html += '</li>\n'
        else:
            tag_html = '<li><a href="javascript:void(0)" class = "item"> %s </a></li>\n' % (
                files[i])
        html_str += tag_html
    html_str += "</ul>"
    return html_str

#合并文件夹（将下级只有一个文件夹的连续文件夹拼接）
def getFiles(path):
    files = os.listdir(path)
    flag = False
    while len(files) == 1 and os.path.isdir(path + os.path.sep + files[0]):
        # print('-'*100)
        # print(path + os.path.sep + files[0])
        # print('-'*100)
        path = path + os.path.sep + files[0]
        files = os.listdir(path)
        flag = True

    return path, files, flag


def getInnerHtml(path):
    html_str = '<ul class = "item sub-item" >\n'
    # files = os.listdir(path)
    path_before = path
    path, files, flag = getFiles(path)

    for i in range(len(files)):
        filePath = path + os.path.sep + files[i]
        if os.path.isdir(filePath):
            tag_html = '<li>\n'
            if flag:
                tag_html += '<a href = "javascript:void(0)" class = "item" show = "0" > %s </a>\n' % (
                    path.replace(path_before, '')+"/"+files[i])
            else:
                tag_html += '<a href = "javascript:void(0)" class = "item" show = "0" > %s </a>\n' % (
                    files[i])
            tag_html += getInnerHtml(filePath)
            tag_html += '</li>\n'
        else:
            tag_html = '<li><a href="javascript:void(0)"> %s </a></li>\n' % (
                files[i])
        html_str += tag_html
    html_str += '</ul>\n'
    return html_str
