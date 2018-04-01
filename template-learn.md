## Template

作为一个web框架，django需要一种方便的方式来动态生成html。最常用的方法依赖于模板(Template)。一个模板包含所需html输出的静态部分以及一些描述动态内容将如何插入的特殊语法。而Django自身的模板系统叫做Django Template Language(dtl).

django定义了一个用于加载(load)和渲染(render)模板的标准API，加载包括为用户给定的标识符(identifier)查找模板并对模板进行预处理，通常将其编译到内存中。渲染意味着用上下文数据插入模板并返回结果字符串。

DTL语法:
**变量(Variable):** 如果向输出context中一个变量的值,用{{}}包围变量名,例如:{{var_name}}

**标签(Tag):** 标签在渲染过程中处理逻辑,Tag被{% %}包围.
标签可以输出内容,也可以作为控制结构,例如一个“if”语句或一个“for”循环，从数据库中获取内容，甚至允许访问其他模板标签。
```django
1.{% extends "base.html" %} 
#extends 告诉模板引擎,当前模板“扩展”了另一个模板。当模板引擎评估此模板时，首先找到它的父模板 - 在本例中为“base.html”。
#此时，模板引擎会注意到base.html中的所有的{% block %}标签，并将这些block替换为子模板的对应block的内容.如果子模板中没有对应的block,那么使用父模板中的block

2.{% include "name_snippet.html" with person="Jane" greeting="Hello" %} #可以使用with将额外的参数传递给模板的上下文.

{3.% url 'some-url-name' v1 v2 %} 
#返回与"给定View"和"可选参数"相匹配的"绝对路径引用"（也就是一个url,不过这个url不包含域名）。
#Exapmle1:
path('client/<int:id>/', app_views.client, name='app-views-client')
{% url 'app-views-client' client.id %}

#将{% url 'some-url-name' arg arg2 %}的值保存在the_url这个变量中 
#Example2:
{% url 'some-url-name' arg arg2 as the_url %}
{{ the_url }}

4.{% for o in some_list %}xxx{% endfor %}
```

具体可以查询:https://docs.djangoproject.com/en/2.0/ref/templates/builtins/#ref-templates-builtins-tags

**过滤器(Filter):** 过滤器用于转换标签参数或者变量的值。过滤器的写法为: {{ django|title }}
```django
1.{{ value|add:"2" }}  #value=4,output=6
2.{{ first|add second}} #first=[1,2],second=[3,4],output=[1,2,3,4]
3.{{ value|capfirst }} #将变量的首个字符转为大写,value=one,output=One
4.{{ value|date:"/d/m/Y" }} #根据给定的格式格式化日期。
5.{{ value|dictsort:"name" }}
#获取字典列表并返回按照参数中给定的键排序的列表。本例是按name排序,默认为升序,若想为降序,使用dictsortreversed
#value=[{'name': 'zed', 'age': 19},{'name': 'amy', 'age': 22},{'name': 'joe', 'age': 31},]
#output=[{'name': 'amy', 'age': 22},{'name': 'joe', 'age': 31},{'name': 'zed', 'age': 19},]
```
具体可以查询:https://docs.djangoproject.com/en/2.0/ref/templates/builtins/#ref-templates-builtins-filters

**注释(Comment):** 在DTL中,将需要注释的内容用{# #}包围,支持多行注释 