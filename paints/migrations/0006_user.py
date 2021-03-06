# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-03 09:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paints', '0005_auto_20180703_0947'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(max_length=13)),
                ('password_hash', models.TextField()),
                ('email', models.CharField(max_length=128, unique=True)),
                ('full_name', models.CharField(max_length=128)),
                ('address', models.TextField(null=True)),
                ('registered_on', models.DateTimeField()),
                ('is_blocked', models.BooleanField()),
                ('email_verification_token', models.TextField()),
                ('token_generated_at', models.DateTimeField()),
                ('is_email_verified', models.BooleanField(default=False)),
            ],
        ),
    ]
