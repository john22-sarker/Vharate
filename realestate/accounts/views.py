from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import SignUpForm, ProfileUpdateForm
from .models import UserProfile, EmailOTP
from properties.models import Property


# =====================================
# USER REGISTRATION
# =====================================
def signup_view(request):
    form = SignUpForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            otp_obj, _ = EmailOTP.objects.get_or_create(user=user)
            otp_obj.generate_otp()

            print("OTP CODE:", otp_obj.otp)

            # session এ store
            request.session['otp'] = otp_obj.otp
            request.session['otp_user'] = user.id

            return redirect('accounts:verify_code')

        messages.error(request, "Please fix the errors below.")

    return render(request, 'accounts/signup.html', {'form': form})


# =====================================
# VERIFY OTP (SIGNUP)
# =====================================
def verify_code_view(request):
    otp = request.session.get('otp')
    user_id = request.session.get('otp_user')

    if not otp or not user_id:
        messages.error(request, "Session expired. Try again.")
        return redirect('accounts:signup')

    if request.method == 'POST':
        code = request.POST.get('otp')

        if not code:
            messages.error(request, "Please enter OTP.")
            return redirect('accounts:verify_code')

        if code == str(otp):
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()

                # cleanup
                request.session.pop('otp', None)
                request.session.pop('otp_user', None)

                messages.success(request, "Account verified successfully!")
                return redirect('accounts:login')

            except User.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Invalid OTP.")

    return render(request, 'accounts/verify_code.html', {
        'otp': otp   # ⚠️ only for testing
    })


# =====================================
# LOGIN
# =====================================
def login_view(request):
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email=username_input).first()
        username = user_obj.username if user_obj else username_input

        user = authenticate(request, username=username, password=password)

        if user:
            if not user.is_active:
                messages.error(request, "Please verify your account first.")
                return redirect('accounts:verify_code')

            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('properties:home')

        messages.error(request, "Invalid credentials.")

    return render(request, 'accounts/login.html')


# =====================================
# LOGOUT
# =====================================
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('properties:home')


# =====================================
# FORGOT PASSWORD (STEP 1)
# =====================================
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()

        if user:
            otp_obj, _ = EmailOTP.objects.get_or_create(user=user)
            otp_obj.generate_otp()

            print("RESET OTP:", otp_obj.otp)

            request.session['reset_user'] = user.id
            request.session['reset_otp'] = otp_obj.otp

            return redirect('accounts:verify_reset_otp')

        messages.error(request, "Email not found.")

    return render(request, 'accounts/forgot_password.html')


# =====================================
# VERIFY RESET OTP (STEP 2)
# =====================================
def verify_reset_otp_view(request):
    otp = request.session.get('reset_otp')
    user_id = request.session.get('reset_user')

    if not otp or not user_id:
        messages.error(request, "Session expired.")
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        code = request.POST.get('otp')

        if code == str(otp):
            request.session['otp_verified'] = True
            return redirect('accounts:reset_password')

        messages.error(request, "Invalid OTP.")

    return render(request, 'accounts/verify_reset_otp.html', {
        'otp': otp   # ⚠️ testing only
    })


# =====================================
# RESET PASSWORD (STEP 3)
# =====================================
def reset_password_view(request):
    user_id = request.session.get('reset_user')
    verified = request.session.get('otp_verified')

    if not user_id or not verified:
        return redirect('accounts:forgot_password')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('accounts:forgot_password')

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


# =====================================
# USER DASHBOARD
# =====================================
@login_required
def user_dashboard(request):

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # ✅ PROFILE FORM (NO FILES HERE)
    profile_form = ProfileUpdateForm(
        request.POST or None,
        instance=profile,
        user=request.user
    )

    # ✅ PASSWORD FORM
    password_form = PasswordChangeForm(
        user=request.user,
        data=request.POST or None
    )

    # ✅ USER PROPERTIES
    properties = Property.objects.filter(
        owner=request.user
    ).order_by('-created_at')

    # =====================================
    # HANDLE POST REQUESTS
    # =====================================
    if request.method == 'POST':

        print("\n====== DEBUG ======")
        print("POST:", request.POST)
        print("FILES:", request.FILES)

        # ---------- PROFILE UPDATE ----------
        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save(user=request.user)
                messages.success(request, "Profile updated successfully!")
            else:
                print("PROFILE ERRORS:", profile_form.errors)
                messages.error(request, "Profile update failed!")

            return redirect('accounts:user_dashboard')

        # ---------- PHOTO UPDATE ----------
        if 'update_photo' in request.POST:
            photo = request.FILES.get('photo')

            if photo:
                profile.photo = photo
                profile.save()
                print("SAVED:", profile.photo.path)
                messages.success(request, "Profile photo updated!")
            else:
                print("NO FILE RECEIVED")
                messages.error(request, "No file selected!")

            return redirect('accounts:user_dashboard')

        # ---------- PASSWORD CHANGE ----------
        if 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully!")
            else:
                print("PASSWORD ERRORS:", password_form.errors)
                messages.error(request, "Fix password errors!")

            return redirect('accounts:user_dashboard')

    # =====================================
    # CONTEXT
    # =====================================
    context = {
        'profile': profile,
        'profile_update_form': profile_form,
        'password_form': password_form,

        'properties': properties,
        'total_properties': properties.count(),
        'active_properties': properties.filter(is_published=True).count(),
        'inactive_properties': properties.filter(is_published=False).count(),
    }

    return render(request, 'accounts/dashboard.html', context)


# =====================================
# DELETE PROPERTY
# =====================================
@login_required
def delete_property(request, id):
    property = get_object_or_404(Property, id=id, owner=request.user)

    if request.method == 'POST':
        property.delete()
        messages.success(request, "Property deleted successfully!")

    return redirect('accounts:user_dashboard')


# =====================================
# TOGGLE ACTIVE / DEACTIVE
# =====================================
@login_required
def toggle_property(request, id):
    property = get_object_or_404(Property, id=id, owner=request.user)

    if request.method == 'POST':
        property.is_published = not property.is_published
        property.save()

        if property.is_published:
            messages.success(request, "Property activated!")
        else:
            messages.success(request, "Property deactivated!")

    return redirect('accounts:user_dashboard')


# =====================================
# EDIT REDIRECT
# =====================================
@login_required
def edit_property_redirect(request, id):
    property = get_object_or_404(Property, id=id, owner=request.user)
    return redirect('properties:property_edit', id=property.id)
