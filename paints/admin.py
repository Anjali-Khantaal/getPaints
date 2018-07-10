# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Carousel)
admin.site.register(PaintingCategory)
admin.site.register(Painting)
admin.site.register(User)
admin.site.register(OtpSave)
admin.site.register(AllOrder)
admin.site.register(OrderNumber)
