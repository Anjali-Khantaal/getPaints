from django.conf.urls import url
from . import views
from django.contrib.auth.views  import password_reset, password_reset_done

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add_to_cart/$', views.add_to_cart, name='add_to_cart'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^about_us', views.about_us, name='about_us'),
    url(r'^category/(?P<category_name>.+)/$', views.category, name='category'),
    url(r'^checkout', views.checkout, name='checkout'),
    url(r'^remove_from_cart', views.remove_from_cart, name='remove_from_cart'),
    url(r'^otp_verify', views.otp_verify, name='otp_verify'),
    url(r'^signup', views.signup, name='signup'),
    url(r'^validate_signup', views.validate_signup, name='validate_signup'),
    url(r'^web_complete_signup', views.web_complete_signup, name='web_complete_signup'),
    url(r'^login', views.login, name='login'),
    url(r'^validate_login', views.validate_login, name='validate_login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^mobile_check', views.mobile_check, name='mobile_check'),
    url(r'^validate_mobile_check', views.validate_mobile_check, name='validate_mobile_check'),
    url(r'^forgot_password_reset', views.forgot_password_reset, name='forgot_password_reset'),
    url(r'^validate_forgot_password_reset', views.validate_forgot_password_reset, name='validate_forgot_password_reset'),
    url(r'^order_placed', views.order_placed, name='order_placed'),
    url(r'^order_completed', views.order_completed, name='order_completed'),
    url(r'^email_verification/(?P<token>.+)/$', views.email_verification, name='email_verification'),
]
