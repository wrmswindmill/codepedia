from operations.models import Annotation,Issue
from projects.models import File,Project
from django.db.models import Count
from projects.models import FileAnnoIssueSummary
import os


project_name=""
fileid_anno_sum = {}
fileid_issue_sum = {}
fileid_parentpath = {}
filepath_id, fileid_annonum,fileid_issuenum=None,None,None


def get_anno_issue_summary(project_path,project_id):
    global project_name, filepath_id, fileid_annonum, fileid_issuenum
    
    project_name = project_path[project_path.rfind('/')+1:]
    print(project_name)

    filepath_id = getPathFileIdInfo(project_id)
    fileid_annonum = getFileAnnoInfo(project_id)
    fileid_issuenum = getFileIssueInfo(project_id)

    # print(filepath_id)
    projectAnnoNum,projectIssueNum=deepSearch(project_path)
    root_fileid = filepath_id[""]
    fileid_anno_sum[root_fileid]=projectAnnoNum
    fileid_issue_sum[root_fileid]=projectIssueNum 
    fileid_parentpath[root_fileid]="self"

    save(project_id)


def save(project_id):
    for file_id in filepath_id.values():
        print(file_id)
        obj = FileAnnoIssueSummary()
        obj.file = File.objects.get(pk=file_id)
        obj.project = Project.objects.get(pk=project_id)

        if file_id not in fileid_anno_sum:
            continue
        obj.anno_num = fileid_anno_sum[file_id]
        obj.isuue_num = fileid_issue_sum[file_id]
        obj.parent_path = fileid_parentpath[file_id]

        obj.save()


def deepSearch(current_path):
    global fileid_anno_sum,fileid_issue_sum

    index=current_path.find(project_name)
    files = os.listdir(current_path)
    currentAnnoNum = 0
    currentIssueNum = 0

    for i in range(len(files)):
        filePath = current_path + os.path.sep + files[i]
        # print(filePath)
        relative_path = filePath[index+len(project_name):]
        #相对路径是否在filepath_id中，可能会有这样的情况，
        #路径没有对应的file_id，也就是当前路劲没有收录
        if relative_path not in filepath_id:
            continue
        file_id = filepath_id[relative_path]

        #获取当前文件/文件夹的父路径
        if index+len(project_name)>=len(current_path):
            fileid_parentpath[file_id]=""
        else:
            fileid_parentpath[file_id]=current_path[index+len(project_name):]  

        #获取当前文件/文件夹下的问题和注释总数
        if os.path.isdir(filePath):

            annoNum,issueNum= deepSearch(filePath)
            #还要加上自己本身的问题和注释总数：
            if file_id in fileid_annonum:
                fileid_anno_sum[file_id] = annoNum + fileid_annonum[file_id]
            else:
                fileid_anno_sum[file_id] = annoNum
            
            if file_id in fileid_issuenum:
                fileid_issue_sum[file_id] = issueNum + fileid_issuenum[file_id]
            else:
                fileid_issue_sum[file_id] = issueNum
                         
            currentAnnoNum += fileid_anno_sum[file_id]
            currentIssueNum += fileid_issue_sum[file_id]
            
        else:
            if file_id in fileid_annonum:
                fileid_anno_sum[file_id] = fileid_annonum[file_id]
            else:
                fileid_anno_sum[file_id] = 0
            currentAnnoNum += fileid_anno_sum[file_id]

            if file_id in fileid_issuenum:
                fileid_issue_sum[file_id] = fileid_issuenum[file_id]
            else:
                fileid_issue_sum[file_id] = 0
            currentIssueNum += fileid_issue_sum[file_id]          
    
    return currentAnnoNum,currentIssueNum


def getPathFileIdInfo(project_id):
    files = File.objects.filter(project_id=project_id)
    filepath_id = {}
    for file in files:
        filepath_id[file.path]=file.pk
    return filepath_id

def getFileAnnoInfo(project_id):
    annos = Annotation.objects.filter(project_id=project_id)
    fileid_annonum={}
    for anno in annos:
        if anno.file_id in fileid_annonum:
            fileid_annonum[anno.file_id]+=1
        else:
            fileid_annonum[anno.file_id]=1
    return fileid_annonum

def getFileIssueInfo(project_id):
    issues = Issue.objects.filter(project_id=project_id)
    fileid_issuenum = {}
    for issue in issues:
        if issue.file_id in fileid_issuenum:
            fileid_issuenum[issue.file_id] += 1
        else:
            fileid_issuenum[issue.file_id] = 1
    return fileid_issuenum
