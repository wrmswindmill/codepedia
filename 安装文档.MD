Django 文档大纲:https://docs.djangoproject.com/en/2.0/contents/
Django 详细文档：https://docs.djangoproject.com/en/2.0/

#### 把项目现在本地跑起来   
1.  在本地配置好所需要的package：

(1)然后安装对应的模块：
因为pip库中有些三个包找不到，所以事先将这几个包下载好。详情见补充
然后执行：
```shell
pip install -r requirements.txt
```

2.  配置好数据库

如果需要导入大文件，按照以下链接操作后并重启数据库：http://azureyu.com/LargeSqlFile/
(1)将sql文件导入数据库
```shell
mysql -u username -p database_name < file.sql
```
(2)修改settings.py中”DATABASES“块的内容

3.  启动项目:(进入项目的根路径，运行)
```python
python manage.py runserver
```

#### Django文档

一般的web流程：在浏览器输入url，
后台对应的servlet处理（url与Servlet的映射）(url.py)
在servlet中与数据库交互（获取到数据库中的数据）(view.py)
将数据库数据插入到html页面中，将html页面的数据返回。(view.py)

所以重要的地方：Servlet
(1)映射
(2)
```python 
polls/templates/polls/index.html
{% if latest_question_list %}
    <ul>
    {% for question in latest_question_list %}
        <li><a href="/polls/{{ question.id }}/">{{ question.question_text }}</a></li>
    {% endfor %}
    </ul>
{% else %}
    <p>No polls are available.</p>
{% endif %}

polls/views.py
from django.shortcuts import render
from .models import Question
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)
```


### 补充

#### 安装xadmin:
如果Django版本低于2.0:直接执行
```
pip install xadmin
```
如果Django高于或等于2.0的版本，需要安装xadmin项目django2分支的代码。 
```
pip install git+git://github.com/sshwsfc/xadmin.git@django2
```
另外，上述方法有时候速度非常慢，下面是一种替代方法：
打开xadmin的GitHub页面并切换到django2分支（点击进入django2分支）；
点击右边的“Clone or download”绿色按钮，选择“Download ZIP”,下载zip包到本地；
执行以下命令安装：
```
wget https://github.com/sshwsfc/xadmin/archive/django2.zip
pip install --cache-dir . django2.zip
rm django2.zip
```
#### 安装django-suit==2.0a1
```
pip install https://github.com/darklow/django-suit/tarball/v2
```
#### 安装mysql-client:
apt-get install libmysqlclient-dev
pip install mysqlclient==1.3.12


