# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import render_to_string
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import *
from django.utils import timezone
import random
import requests
import hashlib
from datetime import timedelta
import json
import string
import razorpay
# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import sendgrid
import os
from sendgrid.helpers.mail import *

# request.seesion keys:
	# cart, order_number, user_datails, user_pre_sign_up_details,

# Create your views here.
def index(request):
	# if order number in session, then delete it
	if "order_number" in request.session:
		del request.session["order_number"]

	# Check whether cart exists
	if "cart" not in request.session:
		request.session["cart"] = {}

	carousels = Carousel.objects.filter(is_active=True)
	painting_categories = PaintingCategory.objects.filter(is_active=True)
	paintings = Painting.objects.filter(is_active=True)

	# TODO: Is cart already present in session?

	output_di = {}
	for painting in paintings:
		if painting.belongs_to_category.is_active and painting.is_active:
			di = {}
			di["painting_name"] = painting.painting_name
			di["painting_code"] = painting.painting_code
			di["painting_size"] = painting.painting_size
			di["painting_cost"] = painting.painting_cost
			di["painting_discounted_cost"] = painting.painting_discounted_cost
			di["image_big"] = painting.painting_image_big
			di["image_small"] = painting.painting_image_small
			di["artist_name"] = painting.artist_name
			di["is_available"] = painting.is_available
			if painting.belongs_to_category.category_name not in output_di.keys():
				output_di[painting.belongs_to_category.category_name] = [di]
			else:
				output_di[painting.belongs_to_category.category_name].append(di)
	return render(request, 'paints/index.html',
		{'carousels': carousels, 'paintings': output_di})


def add_to_cart(request):
	painting_code = request.POST["painting_code"]
	painting = Painting.objects.get(painting_code=painting_code)

	# Check whether cart exists
	if "cart" not in request.session:
		request.session["cart"] = {}

	user_cart = request.session["cart"]

	# Check whether item already in cart
	if painting.painting_code in user_cart.keys():
		response_di = {}
		response_di["status"] = "failed"
		response_di["message"] = "You already have this painting in your cart. Please checkout!"
		response_di["data"] = painting_code;
		return JsonResponse(response_di)

	# If everything is fine
	di = {}
	di["painting_name"] = painting.painting_name
	di["painting_code"] = painting.painting_code
	di["painting_size"] = painting.painting_size
	di["painting_cost"] = painting.painting_cost
	di["painting_discounted_cost"] = painting.painting_discounted_cost
	di["image_big"] = painting.painting_image_big
	di["image_small"] = painting.painting_image_small
	di["artist_name"] = painting.artist_name

	# TODO: Calculate number of items in cart and cart total

	user_cart[painting.painting_code] = di
	request.session["cart"] = user_cart
	
	html_content = render_to_string(
		"paints/base_cart_extension.html",
		context={}, request=request, using=None)

	response_di = {}
	response_di["status"] = "ok"
	response_di["message"] = "Painting successfully added to your cart!"
	# TODO: Send number of items and cart total as data dictionary
	response_di["data"] = {"painting_code": painting_code,
		"html_content": html_content};

	return JsonResponse(response_di)


def remove_from_cart(request):
	painting_code = request.POST["painting_code"]
	painting = Painting.objects.get(painting_code=painting_code)

	user_cart = request.session["cart"]

	# if painting is not there in the cart
	if painting.painting_code not in user_cart.keys():
		response_di = {}
		response_di["status"] = "failed"
		response_di["message"] = "Item has not been added to the cart"
		response_di["data"] = None
		return JsonResponse(response_di)

	# if everything is fine
	del user_cart[painting.painting_code]

	# update cart in session
	request.session["cart"] = user_cart

	# calculate cart total
	cart_total = calculate_cart_total(request)
	cart_saving = calculate_cart_saving(request)
	cart_length = len(user_cart)

	# preparing html for response
	html_content = render_to_string(
		"paints/checkout_extension_1.html",
		context={"user_cart": user_cart, "cart_total": cart_total, "cart_saving": cart_saving,
			'cart_length': cart_length},
		request=request, using=None)

	response_di = {}
	response_di["status"] = "ok"
	response_di["message"] = "Painting successfully removed from your cart!"
	response_di["data"] = {"html": html_content}
	return JsonResponse(response_di)

def contact(request):
	return render(request, 'paints/contact.html', {})

def about_us(request):
	return render(request, 'paints/about_us.html', {})

def category(request, category_name):
	paintings = Painting.objects.filter(is_active=True,
		belongs_to_category__category_name=category_name)
	on_success_param = "category/" + category_name
	return render(request, 'paints/category.html',
		{'paintings': paintings, 'category_name': category_name,
		'on_success_param': on_success_param})

def checkout(request):
	user_cart = request.session["cart"]
	cart_total = calculate_cart_total(request)
	cart_saving = calculate_cart_saving(request)
	cart_length = len(user_cart)
	on_success_param = "checkout/"
	return render(request, 'paints/checkout.html', {'user_cart': user_cart,
		'cart_total': cart_total, "cart_saving": cart_saving,
		'cart_length': cart_length})

def calculate_cart_total(request):
	user_cart = request.session["cart"]
	cart_total = 0.0
	for key, val in user_cart.items():
		cart_total += val["painting_cost"]
	if (cart_total == 0.0):
		return HttpResponseRedirect('/')
	else:
		return cart_total

def calculate_cart_saving(request):
	user_cart = request.session["cart"]
	cart_saving = 0.0
	for key, val in user_cart.items():
		cart_saving += (int(val["painting_cost"]) - int(val["painting_discounted_cost"]))
	return cart_saving



def signup(request):
	on_success_param = request.GET.get('onSuccessPage')
	if 'user_datails' in request.session:
		if on_success_param:   #understand this
			return HttpResponseRedirect('/' + on_success_param + '/')
		return HttpResponseRedirect('/')
	return render(request, 'paints/signup.html', {'on_success_param': on_success_param})

def validate_signup(request):
	"""
	!!! EXCLUSIVELY FOR WEB SESSIONS !!!
	This will take care of signup by new users.
	"""
	mobile = request.POST["mobile"]
	email = request.POST["email"]
	print email
	name = request.POST["name"]

	#check if email is already registered
	try:
		emailmatch = User.objects.get(email = email)
		return JsonResponse({'status': 'failed', 'message': 'email already exist', 'data': None})
	except:
		pass

	#check if mobile is alredy registered
	try:
		mobmatch = User.objects.get(mobile = mobile)
		return JsonResponse({'status': 'failed', 'message': 'mobile number already registered', 'data': None})
	except User.DoesNotExist:
		#for unregistered mobile number, send an otp and then store it
		try:
			otp_check = OtpSave.objects.get(mobile=mobile)
			otp = str(random.randint(100000,999999))
			otp_check.otp = otp
			otp_check.otp_for = "signup"
			otp_check.saved_at = timezone.now()
			otp_check.save()

		except OtpSave.DoesNotExist:
			otp = str(random.randint(100000, 999999))
			OtpSave.objects.create(mobile=mobile, otp=otp, otp_for='signup',saved_at=timezone.now())

		#storing users input in session:
		session_di = {}
		session_di['name'] = name
		session_di['email'] = email
		session_di['mobile'] = mobile
		request.session['user_pre_sign_up_details'] = session_di
		print session_di

		#send otp as sms
		message_send_url = "https://control.msg91.com/api/sendhttp.php?"
		message_send_url += "authkey=219509AvHigpCGp5b1a3795&mobiles=91"
		message_send_url += str(mobile)
		message_send_url += "&message=Your%20getPaints%20Signup%20OTP%20is%3A%20"
		message_send_url += otp
		message_send_url += "&sender=PAINTS&route=4&country=0&campaign=signupweb"
		#req = requests.get(message_send_url)
		print otp
		return JsonResponse({'status':'ok', 'message':'OTP Sent!', 'data':None})

	return JsonResponse({'status':'ok', 'message':'', 'data':None})


def otp_verify(request):
	if "user_pre_sign_up_details" not in request.session:
		return HttpResponseRedirect("/")
	on_success_param = request.GET.get('onSuccessPage') #understand this
	if 'user_datails' in request.session:
		if on_success_param:   #understand this
			return HttpResponseRedirect('/' + on_success_param + '/')   #understand this
		return HttpResponseRedirect('/')
	return render(request, 'paints/otp_verify.html', {'on_success_param': on_success_param})




def web_complete_signup(request):
	"""
	!!! EXCLUSIVELY FOR WEB USERS !!!
	This will take care of verfication of OTP for new users.
	"""
	otp = request.POST["otp"]
	password = request.POST["password"]
	try:
		name = request.session["user_pre_sign_up_details"]["name"]
		email = request.session["user_pre_sign_up_details"]["email"]
		mobile = request.session["user_pre_sign_up_details"]["mobile"]
	except:
		return JsonResponse({"status": "failed",
			"message": "Something went wrong. Please startover!"})

	#Check if OTP is stored in database and is not expired
	try:
		otpmatch = OtpSave.objects.get(mobile=mobile, otp_for="signup")
		otp_in_db = otpmatch.otp
		if otp_in_db == otp:
			if (otpmatch.saved_at + timedelta(minutes=10)) > timezone.now():
				#create new user and return response
				password_hash = str(hashlib.sha512(
					str(password).encode('utf-8')).hexdigest())
				#storing token for email verification
				salt = str(random.randint(100000, 999999))
				decoded_str = mobile + salt
				encoded_str = str(hashlib.sha224(str(
					decoded_str).encode('utf-8')).hexdigest()).lower()
				try:
					check_user = User.objects.get(mobile=mobile)
					return JsonResponse({"status": "failed",
						"message": "You're already registered. Please login!",
						"data": None})
				except:
					pass
				try:
					check_user = User.objects.get(email=email)
					return JsonResponse({"status": "failed",
						"message": "Email already registered. Please login!",
						"data": None})
				except:
					pass
				storage_item = User.objects.create(full_name=name,
					mobile=mobile, password_hash=password_hash,
					email=email, registered_on=timezone.now(),
					is_email_verified=False,
					email_verification_token=encoded_str,
					token_generated_at=timezone.now(),
					is_blocked=False)
			else:
				return JsonResponse({"status": "failed",
					"message": "OTP Expired! Please go to previous step or startover.",
					"data": None}, status=200)
		else:
			return JsonResponse({"status": "failed",
				"message": "Wrong OTP!",
				"data": None}, status=200)
	except OtpSave.DoesNotExist:
		return JsonResponse({"status": "failed",
			"message": "Please signup first!",
			"data": None}, status=200)
	"""
	If everything went correct so far, delete the supporting session key
	"user_pre_signup_details" after storing its details into persistent
	session key
	"""
	del request.session["user_pre_sign_up_details"]

	data = {}
	data["name"] = storage_item.full_name
	data["mobile"] = storage_item.mobile
	data["address"] = None
	data["email"] = storage_item.email

	#sending email for verification
	request.session["user_details"] = data
	print settings.SENDGRID_API_KEY
	sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
	from_email = Email("anjalikhantaal06@gmail.com")
	to_email = Email(storage_item.email)
	subject = "Confirm Your Email"
	content = Content("text/html", render_to_string("paints/email_verification.html", 
		context={"token": storage_item.email_verification_token}))
	mail = Mail(from_email, subject, to_email, content)
	response = sg.client.mail.send.post(request_body=mail.get())
	print response.status_code
	print response.body
	print response.headers

	return JsonResponse({"status": "ok", "message": "",
		"data": None}, status=200)


def email_verification(request, token):
	try:
		user = User.objects.get(email_verification_token=token)
		user.is_email_verified = True
		user.save()
		return render(request, "paints/email_verified.html", {"user_name": user.full_name,
			"verification_complete": True})
	except:
		return render(request, "paints/email_verified.html", {"verification_complete": False})
		return HttpResponseRedirect("/")



def login(request):
	on_success_param = request.GET.get('onSuccessPage')
	password_changed = request.GET.get('passwordChanged')
	login = request.GET.get('login')
	if "user_details" in request.session:
		if on_success_param:
			return HttpResponseRedirect("/" + on_success_param + "/")
		return HttpResponseRedirect("/")
	return render(request, "paints/login.html",
		{"password_changed": password_changed, "login": login})

def validate_login(request):
	"""
	!!! EXCLUSIVELY FOR WEB SESSIONS !!!
	This will take care of new login. By new login, we mean the passwords of
	customers will be hashed before saving it into DB. Apart from this, it will
	also function as a view for login for old users.
	"""
	mobile = request.POST['mobile']

	if len(mobile) != 10 or not mobile.isdigit():
		return JsonResponse({'status': 'failed', 'message': 'Please enter a valid 10 digit mobile number','data': None})

	password = request.POST['password']
	''' Begin reCAPTCHA validation '''
	recaptcha_response = request.POST['g-recaptcha-response']
	url = 'https://www.google.com/recaptcha/api/siteverify'
	values = {
		'secret': "6LeGd2IUAAAAAK_I_GschxfIYRJ4F5xOvVXeYYXY",
		'response': recaptcha_response
	}
	data = values
	req = requests.post(url, data)
	result = json.loads(req.text)
	if not result['success']:
		return JsonResponse({"status": "failed",
			"message": "re-CAPTACHA verification failed",
			"data": None})
	''' End reCAPTCHA validation '''
	password_hash = str(hashlib.sha512(
		str(password).encode('utf-8')).hexdigest())

	#Check if mobile is registered
	try:
		mobmatch = User.objects.get(mobile=mobile)
		if password_hash != mobmatch.password_hash:
			return JsonResponse({'status': 'failed', 'message': 'Incorrect Credentials!', 'data': None})
	except User.DoesNotExist:
		return JsonResponse({'status': 'failed', 'message': 'Not registered! Please create an account.',
			'data': None})
	#Check for users being blocked
	if mobmatch.is_blocked:
		return JsonResponse({'status': 'failed', 'message': 'You are blocked by getPaints',
				'data': None})
	else:
		data = {}
		data['name'] = mobmatch.full_name
		data['mobile'] = mobmatch.mobile
		request.session["user_details"] = data
		return JsonResponse({"status": "ok", "message": "",
			"data": None}, status=200)


def logout(request):
	del request.session["user_details"]
	return HttpResponseRedirect("/")


def mobile_check(request):
	return render(request, "paints/mobile_check.html")


def validate_mobile_check(request):
	mobile = request.POST["mobile"]
	''' Begin reCAPTCHA validation '''
	recaptcha_response = request.POST['g-recaptcha-response']
	url = 'https://www.google.com/recaptcha/api/siteverify'
	values = {
		'secret': "6LeGd2IUAAAAAK_I_GschxfIYRJ4F5xOvVXeYYXY",
		'response': recaptcha_response
	}
	data = values
	req = requests.post(url, data)
	result = json.loads(req.text)
	if not result['success']:
		return JsonResponse({"status": "failed",
			"message": "re-CAPTACHA verification failed",
			"data": None})
	''' End reCAPTCHA validation '''
	# Check if mobile number is already registered
	try:
		mobmatch = User.objects.get(mobile=mobile)
		if mobmatch.mobile == mobile:
			#for registered mobile number, send an otp and then store it
			try:
				otp_check = OtpSave.objects.get(mobile=mobile)
				otp = str(random.randint(100000,999999))
				otp_check.otp = otp
				otp_check.otp_for = "reset"
				otp_check.saved_at = timezone.now()
				otp_check.save()

			except OtpSave.DoesNotExist:
				otp = str(random.randint(100000, 999999))
				OtpSave.objects.create(mobile=mobile, otp=otp, otp_for='reset',saved_at=timezone.now())

			#storing users input in session:
			session_di = {}
			session_di['mobile'] = mobile
			request.session['user_pre_sign_up_details'] = session_di

			#send otp as sms
			message_send_url = "https://control.msg91.com/api/sendhttp.php?"
			message_send_url += "authkey=219509AvHigpCGp5b1a3795&mobiles=91"
			message_send_url += str(mobile)
			message_send_url += "&message=Your%20getPaints%20Signup%20OTP%20is%3A%20"
			message_send_url += otp
			message_send_url += "&sender=PAINTS&route=4&country=0&campaign=signupweb"
			print otp
			#req = requests.get(message_send_url)
			return JsonResponse({'status':'ok', 'message':'OTP Sent!', 'data':None})

		return JsonResponse({'status':'ok', 'message':'', 'data':None})
	#if mobile number is not registered
	except User.DoesNotExist:
		return JsonResponse({'status':'failed', 'message': 'This mobile number is not registered. Please enter a registered mobile number or sign up',
			'data': None})


def forgot_password_reset(request):
	on_success_param = request.GET.get('onSuccessPage')
	if "user_details" in request.session:
		if on_success_param:
			return HttpResponseRedirect("/" + on_success_param + "/")
		return HttpResponseRedirect("/")
	return render(request, "paints/forgot_password_reset.html", {'on_success_param': on_success_param})

def validate_forgot_password_reset(request):
	otp = request.POST["otp"]
	password = request.POST["password"]
	confirm_password = request.POST["confirm_password"]
	#Check if OTP is stored in database and is not expired
	try:
		otpmatch = OtpSave.objects.get(otp=otp, otp_for="reset")
		otp_in_db = otpmatch.otp
		if otp_in_db == otp:
			if (otpmatch.saved_at + timedelta(minutes=10)) > timezone.now():
				if password == confirm_password:
					#create new password and return response
					password_hash = str(hashlib.sha512(
						str(password).encode('utf-8')).hexdigest())
					#update in models.py
					user_in_db = User.objects.get(mobile=otpmatch.mobile)
					user_in_db.password_hash = password_hash
					user_in_db.save()
				else:
					return JsonResponse({"status":"failed", "message": "Password does not match. Please try again!", "data": None})
			else:
				return JsonResponse({"status": "failed",
					"message": "OTP Expired! Please go to previous step or startover.",
					"data": None}, status=200)
		else:
			return JsonResponse({"status": "failed",
				"message": "Wrong OTP!",
				"data": None}, status=200)
	except:
		pass
	return JsonResponse({"status": "ok", "message": "",
		"data": None}, status=200)


def order_placed(request):
	user_cart = request.session["cart"]
	cart_total = calculate_cart_total(request)
	cart_total_in_paisa = cart_total * 100
	full_name = request.POST["name"]
	contact = request.POST["contact"]
	email = request.POST["email"]
	address = (request.POST["add_line1"] + request.POST["add_line2"] + request.POST["add_line3"] 
				+ request.POST["city"] + request.POST["state"] + request.POST["pin"])
	logged_in_name = request.session["user_details"]["name"]
	logged_in_mobile = request.session["user_details"]["mobile"]
	logged_in_email = request.session["user_details"]["email"]
	# picking and saving order number
	on_object = OrderNumber.objects.get(code="1")
	order_number = on_object.order_number
	on_object.order_number = str(int(order_number) + 1)
	on_object.save()

	# handling ordered items
	order_items = json.dumps(user_cart)

	# save order number to session
	request.session["order_number"] = order_number

	# saving details to AllOrder model
	AllOrder.objects.create(order_number=order_number,
		order_items=order_items, status="received",
		order_total=cart_total,payment_mode="online payment",
		user_name=full_name,logged_in_name=logged_in_name,
		user_mobile=contact,logged_in_mobile=logged_in_mobile,
		user_email=email,logged_in_email=logged_in_email,placed_at=timezone.now(),
		delivery_address=address,expected_at=(timezone.now() + timedelta(days=5)))

	return JsonResponse({"status": "ok", "message": "order has been placed",
		"data": {"full_name": full_name, "contact": contact, "email": email,
					"cart_total_in_paisa": cart_total_in_paisa, "order_number": order_number,
					"logged_in_mobile": logged_in_mobile }})



def order_completed(request):
	# don't open this page if no order number in session
	print request.session["order_number"]
	if "order_number" not in request.session:
		return HttpResponseRedirect('/')
	else:
		# copy order number from session to a variable and pass it in context
		order_number = request.session["order_number"]
		# delete all stuff from session along with order number
		del request.session["cart"]
		del request.session["order_number"]

	return render(request, "paints/order_completed.html")








