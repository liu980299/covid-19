# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2020-03-31 23:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_auto_20200401_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='risk',
            name='test',
            field=models.BooleanField(default=False),
        ),
    ]