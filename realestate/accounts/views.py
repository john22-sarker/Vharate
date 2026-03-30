from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .forms import SignUpForm, ProfileUpdateForm
from .models import UserProfile, EmailOTP
from properties.models import Property


# =============================
# USER REGISTRATION
# =============================

def signup_view(request):
    form = SignUpForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        otp_obj, _ = EmailOTP.objects.get_or_create(user=user)
        otp_obj.generate_otp()

        request.session['otp'] = str(otp_obj.otp)
        request.session['otp_user'] = user.id
        request.session['otp_time'] = timezone.now().isoformat()

        return redirect('accounts:verify_code')

    return render(request, 'accounts/signup.html', {'form': form})


# =============================
# VERIFY OTP (SIGNUP)
# =============================

def verify_code_view(request):
    otp = request.session.get('otp')
    user_id = request.session.get('otp_user')
    otp_time = request.session.get('otp_time')

    if not otp or not user_id or not otp_time:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect('accounts:signup')

    if timezone.now() > timezone.datetime.fromisoformat(otp_time) + timedelta(minutes=5):
        messages.error(request, "OTP expired.")
        return redirect('accounts:signup')

    if request.method == 'POST':
        code = request.POST.get('otp')

        if not code:
            messages.error(request, "Enter OTP.")
            return redirect('accounts:verify_code')

        if code == otp:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()

            request.session.flush()

            messages.success(request, "Account verified!")
            return redirect('accounts:login')

        else:
            messages.error(request, "Invalid OTP.")

    return render(request, 'accounts/verify_code.html')


# =============================
# LOGIN
# =============================

def login_view(request):
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email=username_input).first()
        username = user_obj.username if user_obj else username_input

        user = authenticate(request, username=username, password=password)

        if user:
            if not user.is_active:
                messages.error(request, "Verify your account first.")
                return redirect('accounts:verify_code')

            login(request, user)
            return redirect('properties:home')

        messages.error(request, "Invalid credentials.")

    return render(request, 'accounts/login.html')


# =============================
# LOGOUT
# =============================

def logout_view(request):
    logout(request)
    return redirect('properties:home')


# =============================
# FORGOT PASSWORD
# =============================

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            otp_obj, _ = EmailOTP.objects.get_or_create(user=user)
            otp_obj.generate_otp()

            request.session['reset_user'] = user.id
            request.session['reset_otp'] = str(otp_obj.otp)
            request.session['reset_otp_time'] = timezone.now().isoformat()

            return redirect('accounts:verify_reset_otp')

        messages.error(request, "Email not found.")

    return render(request, 'accounts/forgot_password.html')


# =============================
# VERIFY RESET OTP
# =============================

def verify_reset_otp_view(request):
    otp = request.session.get('reset_otp')
    user_id = request.session.get('reset_user')
    otp_time = request.session.get('reset_otp_time')

    if not otp or not user_id or not otp_time:
        messages.error(request, "Session expired.")
        return redirect('accounts:forgot_password')

    if timezone.now() > timezone.datetime.fromisoformat(otp_time) + timedelta(minutes=5):
        messages.error(request, "OTP expired.")
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        code = request.POST.get('otp')

        if not code:
            messages.error(request, "Enter OTP.")
            return redirect('accounts:verify_reset_otp')

        if code == otp:
            request.session['otp_verified'] = True
            return redirect('accounts:reset_password')

        else:
            messages.error(request, "Invalid OTP.")

    return render(request, 'accounts/verify_reset_otp.html')


# =============================
# RESET PASSWORD
# =============================

def reset_password_view(request):
    user_id = request.session.get('reset_user')
    verified = request.session.get('otp_verified')

    if not user_id or not verified:
        return redirect('accounts:forgot_password')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password == confirm:
            user.set_password(password)
            user.save()

            request.session.flush()
            messages.success(request, "Password reset successful!")
            return redirect('accounts:login')

        messages.error(request, "Passwords do not match.")

    return render(request, 'accounts/reset_password.html')


# =============================
# USER DASHBOARD
# =============================

@login_required
def user_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    profile_form = ProfileUpdateForm(
        request.POST or None,
        instance=profile,
        user=request.user
    )

    password_form = PasswordChangeForm(
        user=request.user,
        data=request.POST or None
    )

    properties = Property.objects.filter(owner=request.user).order_by('-created_at')

    if request.method == 'POST':

        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save(user=request.user)
                messages.success(request, "Profile updated!")
            else:
                messages.error(request, "Update failed!")
            return redirect('accounts:user_dashboard')

        if 'update_photo' in request.POST:
            photo = request.FILES.get('photo')
            if photo:
                profile.photo = photo
                profile.save()
                messages.success(request, "Photo updated!")
            else:
                messages.error(request, "No file selected!")
            return redirect('accounts:user_dashboard')

        if 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed!")
            else:
                messages.error(request, "Fix errors!")
            return redirect('accounts:user_dashboard')

    context = {
        'profile': profile,
        'profile_update_form': profile_form,
        'password_form': password_form,
        'properties': properties,
    }

    return render(request, 'accounts/dashboard.html', context)


# =============================
# PROPERTY ACTIONS
# =============================

@login_required
def delete_property(request, id):
    property_obj = get_object_or_404(Property, id=id, owner=request.user)

    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, "Property deleted!")

    return redirect('accounts:user_dashboard')


@login_required
def toggle_property(request, id):
    property_obj = get_object_or_404(Property, id=id, owner=request.user)

    if request.method == 'POST':
        property_obj.is_published = not property_obj.is_published
        property_obj.save()

        if property_obj.is_published:
            messages.success(request, "Property activated!")
        else:
            messages.success(request, "Property deactivated!")

    return redirect('accounts:user_dashboard')


@login_required
def edit_property_redirect(request, id):
    property_obj = get_object_or_404(Property, id=id, owner=request.user)
    return redirect('properties:property_edit', id=property_obj.id)
