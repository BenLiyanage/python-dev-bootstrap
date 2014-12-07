# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('github', '0004_auto_20141119_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='githubrequestcache',
            name='processed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
