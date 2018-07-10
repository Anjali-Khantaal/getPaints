# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-06-11 11:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('paints', '0003_painting_belongs_to_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtpSave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.PositiveIntegerField()),
                ('otp', models.PositiveIntegerField()),
                ('otp_for', models.CharField(max_length=38)),
                ('saved_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.PositiveIntegerField()),
                ('email', models.CharField(max_length=128, unique=True)),
                ('full_name', models.CharField(max_length=128)),
            ],
        ),
    ]