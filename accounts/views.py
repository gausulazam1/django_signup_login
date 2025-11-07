from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .forms import SignUpForm, LoginForm
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save user but inactive initially
            user = form.save(commit=False)
            user.is_active = False
            user.email = form.cleaned_data.get('email')
            user.save()

            # Store OTP and user id in session
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['user_id'] = user.id
            request.session['phone'] = form.cleaned_data.get('phone')

            # Send OTP on localhost (print in console)
            print(f"Signup OTP for user {user.username}: {otp}")

            return redirect('accounts:verify_signup_otp')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def verify_signup_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        user_id = request.session.get('user_id')

        if entered_otp == stored_otp and user_id:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            # Clear OTP session data
            request.session.pop('otp', None)
            request.session.pop('user_id', None)
            request.session.pop('phone', None)
            return render(request, 'accounts/signup_success.html')

        else:
            error = "Invalid OTP"
            return render(request, 'accounts/verify_signup_otp.html', {'error': error})

    return render(request, 'accounts/verify_signup_otp.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('identifier')
            password = form.cleaned_data.get('password')

            # Authenticate by username or email
            user = None
            if '@' in identifier:
                try:
                    user_obj = User.objects.get(email=identifier)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(request, username=identifier, password=password)

            if user is not None:
                # Generate OTP and store in session
                otp = generate_otp()
                request.session['login_otp'] = otp
                request.session['login_user_id'] = user.id
                print(f"Login OTP for user {user.username}: {otp}")

                return redirect('accounts:verify_login_otp')

            else:
                error = "Invalid credentials"
                return render(request, 'accounts/login.html', {'form': form, 'error': error})
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def verify_login_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('login_otp')
        user_id = request.session.get('login_user_id')

        if entered_otp == stored_otp and user_id:
            user = User.objects.get(id=user_id)
            # Log in the user
            login(request, user)

            # Clear login OTP session data
            request.session.pop('login_otp', None)
            request.session.pop('login_user_id', None)

            # For token generation, you can use REST framework JWT or default session token
            # Redirect to dashboard
            return redirect('dashboard')

        else:
            error = "Invalid OTP"
            return render(request, 'accounts/verify_login_otp.html', {'error': error})

    return render(request, 'accounts/verify_login_otp.html')
