from django import template
register = template.Library()
from django.conf import settings
import os
import time


import requests

source_path = settings.SOURCEPATH


#把时间戳转化为时间:
def timeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',timeStruct)


@register.filter
def keyValue(dict, key):
    return dict[key]


@register.filter
def getFileSize(project_name, path):
    abspath = source_path + str(project_name) + path
    fsize = os.path.getsize(abspath)
    return fsize


@register.filter
def getfileCTime(project_name, path):
    abspath = source_path + str(project_name) + path
    return timeStampToTime(os.path.getctime(abspath))


@register.filter
def getFileMTime(project_name, path):
    abspath = source_path + str(project_name) + path
    return timeStampToTime(os.path.getmtime(abspath))


# @register.simple_tag()
# def formatText2Line(project_name, path):
#     abspath = source_path + str(project_name) + path
#     lines = {}
#     with open(abspath, 'r') as f:
#         for index, line in enumerate(f.readlines()):
#             lines[str(index+1)]= line.strip('\n')
#     symbolList = lines[-1]
#     return lines

@register.simple_tag()
def formatText2Line(project_path, file_path):
    url = settings.OPENGROK_XREF_URL
    request_url = url + str(project_path) + file_path
    response = requests.get(request_url)
    lines = {}
    for index, line in enumerate(response.text.split('\n')):
        lines[str(index + 1)] = line
    # print(lines)
    return lines


