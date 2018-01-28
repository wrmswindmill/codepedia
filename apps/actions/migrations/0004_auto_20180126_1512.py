# Generated by Django 2.0.1 on 2018-01-26 15:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0005_issueanswer_content'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('actions', '0003_auto_20180126_1355'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueCommentVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.IssueComment', verbose_name='issue评论')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': 'Issue评论点赞',
                'verbose_name_plural': 'Issue评论点赞',
                'db_table': 'Vote_Issue_Comment',
            },
        ),
        migrations.CreateModel(
            name='IssueVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.Issue', verbose_name='issue')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '问题点赞',
                'verbose_name_plural': '问题点赞',
                'db_table': 'Vote_Issue',
            },
        ),
        migrations.AlterField(
            model_name='annotationcommentvote',
            name='value',
            field=models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型'),
        ),
        migrations.AlterField(
            model_name='annotationvote',
            name='value',
            field=models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型'),
        ),
        migrations.AlterField(
            model_name='answercommentvote',
            name='value',
            field=models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型'),
        ),
        migrations.AlterField(
            model_name='answervote',
            name='value',
            field=models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型'),
        ),
        migrations.AlterField(
            model_name='articlecommentvote',
            name='value',
            field=models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型'),
        ),
        migrations.AlterField(
            model_name='articlevote',
            name='value',
            field=models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型'),
        ),
        migrations.AlterField(
            model_name='questioncommentvote',
            name='value',
            field=models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型'),
        ),
        migrations.AlterField(
            model_name='questionvote',
            name='value',
            field=models.IntegerField(choices=[(1, '点赞'), (-1, '点踩')], default=0, verbose_name='点赞类型'),
        ),
    ]
