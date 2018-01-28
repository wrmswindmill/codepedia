import os
# import json
#
#
# abspath = '/Users/yujie/workspace/opengrok/source/Notes/AndroidManifest.xml'
# import requests
#
# file_url = 'http://localhost:8080/myservlet/'
# navigation_url = 'http://localhost:8080/navigation/'
# project_path = 'Notes'
# file_path = '/src/net/micode/notes/data/NotesProvider.java'
#
# # response = requests.get(file_url+ project_path +file_path).text
# response = requests.get(navigation_url + project_path + file_path ).text
# all_symbols = []
# for symbol in response.split('|'):
#
#     symbol = json.loads(symbol)
#     all_symbols.append(symbol)
# print(all_symbols)

path = '/src/net/micode/notes/ui/DateTimePickerDialog.java'
path = path.split('/')
for i in range(1,len(path)):
    print(path[i], 'Notes'+'/'.join(path[:i+1]))