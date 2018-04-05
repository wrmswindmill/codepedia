原文链接:https://docs.djangoproject.com/en/2.0/topics/db/queries/#other-queryset-methods

一旦你创建了你的数据模型，django会自动为你提供一个数据库抽象API，可以让你创建，检索，更新和删除对象。

对于数据库操作而言,总离不开增删改查,我们从文档的目录结构能够大致的辨别出"增","删","改","查"的大概位置,从而快速地找到我们需要的东西.

### Django的一些基本概念
从数据库中检索对象，通过model类上的管理器(Manager)构建一个QuerySet。QuerySet代表数据库中的"对象"集合。(也就以意味着返回QuerySet是由一个个对象组成的).对于每一个QuerySet,它可以有零个，一个或多个过滤器(filter)。过滤器根据给定的参数"缩小查询结果的范围"。

在SQL方面，一个QuerySet等同于一个select语句，而一个过滤器是一个条件语句，如where或limit。可以使用模型的管理器获取QuerySet。每个Model至少有一个管理器，默认情况下称为objects。通过模型类直接访问它，就像这样
`Blog.objects`,我们可以通过Blog.objects.all()获取在包含数据库中所有Blob对象的QuerySet.

#### 使用过滤器检索特定的对象
要获取特定的对象,需要对初始的QuerySet添加过滤条件,下面是两种最常用的方法:
filter(**kwargs)
返回包含匹配(满足)给定查询参数的对象的新查询集
exclude(**kwargs)
返回包含不匹配(满足)给定查询参数的对象的新查询集

``` python
q1 = Entry.objects.filter(headline__startswith="What")
#等价于q1 =Entry.objects.all().filter(headline__startswith="What")
#作用在Entry.objects上的all()可以省略
q2 = q1.exclude(pub_date__gte=datetime.date.today())
q3 = q1.filter(pub_date__gte=datetime.date.today())
```
q1包含以“what”开头的标题所有Entry对象的集合。
q2是q1的子集，不过会排除pub_date是今天或将来的记录
q3也是q1的子集，不过仅选择q1中,pub_date今天或将来的记录。
q1不受到q2和q3的影响。
在这里还可以看到出现了__startswith,__gte(greater than,>)的字段,在django中称之为lookups.

#### Field lookups
这里介绍几个比较常用的lookups:
**iexact(case-insensitive)**
Blog.objects.get(name__iexact="beatles blog")
将匹配名字为,例如"Beatles Bl", "beatles blog", or even "BeAtlES blOG"的所有Blog
**contains**
Entry.objects.get(headline__contains='Lennon')
等价于:SELECT ... WHERE headline LIKE '%Lennon%';
**in**
Entry.objects.filter(headline__in=['Lennon','Apple','Banana'])
等价于:SELECT ... WHERE headline in ['Lennon','Apple','Banana'];
**django提供了一种强大而直观的方式来在"follow relationship"，它自动默默的处理sql中的JOIN,如果想要跨越Relationship，只需使用模型中相关字段的字段名称（用双下划线分隔），直到取到所需字段**
_对应小标题为:Lookups that span relationships_
Entry.objects.filter(blog__name='Beatles Blog')
查询所有的"关联的Blob的名字为Beatles Blog"的Entry对象.

#### 其他的特性
懒加载等


