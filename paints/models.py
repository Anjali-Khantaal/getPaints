# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save

# Create your models here.

# Carausel created here:
class Carousel(models.Model):
	image_link = models.TextField()
	image_title = models.CharField(max_length=64)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.image_title


class PaintingCategory(models.Model):
	category_name = models.CharField(max_length=64)
	category_code = models.CharField(max_length=64, unique=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return (self.category_code + " - " + self.category_name)


class Painting(models.Model):
	painting_name = models.CharField(max_length=128)
	belongs_to_category = models.ForeignKey('PaintingCategory', null=True)
	painting_code = models.CharField(max_length=64, unique=True)
	painting_size = models.CharField(max_length=32)
	painting_cost = models.PositiveIntegerField()
	painting_discounted_cost = models.PositiveIntegerField()
	painting_image_big = models.TextField()
	painting_image_small = models.TextField()
	artist_name = models.CharField(max_length=128)
	is_active = models.BooleanField(default=True)
	is_available = models.BooleanField(default=True)


	def __str__(self):
		return self.painting_name

# user info for signup created here
class User(models.Model):
	mobile = models.CharField(max_length=13)
	password_hash = models.TextField()
	email = models.CharField(max_length=512, unique=True)
	full_name = models.CharField(max_length=128)
	address = models.TextField(null=True, blank=True)
	registered_on = models.DateTimeField()
	is_blocked = models.BooleanField()
	email_verification_token = models.TextField()
	token_generated_at = models.DateTimeField()
	is_email_verified = models.BooleanField(default=False)

	def __str__(self):
		return self.mobile

class OtpSave(models.Model):
	mobile = models.CharField(max_length=13)
	otp = models.CharField(max_length=12)
	otp_for = models.CharField(max_length=38)
	saved_at = models.DateTimeField(null=True)

	def __str__(self):
		return self.mobile


class AllOrder(models.Model):
	order_number = models.CharField(max_length=512, null=True, blank=True)
	order_items = models.TextField()
	status =  models.CharField(max_length=120, default='received')
	order_total = models.CharField(max_length=10, null=True)
	payment_mode = models.CharField(max_length=64, null=True)
	user_name = models.CharField(max_length=256, null=True)
	logged_in_name = models.CharField(max_length=256, null=True)
	user_mobile = models.CharField(max_length=13, null=True)
	logged_in_mobile = models.CharField(max_length=13, null=True)
	user_email = models.CharField(max_length=256, null=True)
	logged_in_email = models.CharField(max_length=256, null=True)
	placed_at = models.DateTimeField()
	delivery_address = models.TextField(null=True, blank=True)
	expected_at = models.DateTimeField()
	rzp_payment_id = models.CharField(max_length=64, null=True)
	rzp_refund_id = models.CharField(max_length=64, null=True)

	def __str__ (self):
		return self.order_number


class OrderNumber(models.Model):
	code = models.CharField(max_length=256)
	order_number = models.CharField(max_length=256)

	def __str__ (self):
		return self.code





