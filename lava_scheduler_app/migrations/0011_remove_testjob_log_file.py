# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-11 12:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lava_scheduler_app', '0010_auto_20151103_1136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testjob',
            name='log_file',
        ),
    ]
