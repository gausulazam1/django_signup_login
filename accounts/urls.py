from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/otp/', views.verify_signup_otp, name='verify_signup_otp'),
    path('login/', views.login_view, name='login'),
    path('login/otp/', views.verify_login_otp, name='verify_login_otp'),
]
