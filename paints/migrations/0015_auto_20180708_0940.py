# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-08 09:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paints', '0014_auto_20180708_0939'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PlaceOrder',
            new_name='AllOrder',
        ),
        migrations.RenameModel(
            old_name='Order',
            new_name='OrderNumber',
        ),
    ]