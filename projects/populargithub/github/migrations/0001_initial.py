# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GitHubRequestCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('query', models.CharField(max_length=255)),
                ('ETag', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(default=None, null=True)),
                ('completed_at', models.DateTimeField(default=None, null=True)),
                ('success', models.NullBooleanField(default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PullRequest',
            fields=[
                ('number', models.IntegerField(serialize=False, primary_key=True)),
                ('state', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('closed_at', models.DateTimeField(null=True)),
                ('merged_at', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RateLimit',
            fields=[
                ('type', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('limit', models.IntegerField()),
                ('remaining', models.IntegerField()),
                ('reset', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('full_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('html_url', models.CharField(max_length=255)),
                ('stargazer_count', models.IntegerField(null=True)),
                ('fork_count', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('login', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='repo',
            field=models.ForeignKey(to='github.Repo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='user',
            field=models.ForeignKey(to='github.User'),
            preserve_default=True,
        ),
    ]
