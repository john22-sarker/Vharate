from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import EmailOTP
from django.contrib.auth.models import User

from .forms import SignUpForm, ProfileUpdateForm
from .models import UserProfile
from properties.models import Property


# =====================================
# USER REGISTRATION
# =====================================
def signup_view(request):
    form = SignUpForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            # OTP create
            otp_obj, _ = EmailOTP.objects.get_or_create(user=user)
            otp_obj.generate_otp()

            # send email
            send_mail(
                'Verify your account',
                f'Your verification code is: {otp_obj.otp}',
                'your_email@gmail.com',
                [user.email],
                fail_silently=False,
            )

            return redirect('accounts:verify_code')

    return render(request, 'accounts/signup.html', {'form': form})

def verify_code_view(request):
    if request.method == 'POST':
        code = request.POST.get('otp')

        try:
            otp_obj = EmailOTP.objects.get(otp=code)

            user = otp_obj.user
            user.is_active = True
            user.save()

            otp_obj.delete()

            messages.success(request, "Account verified successfully!")
            return redirect('accounts:login')

        except EmailOTP.DoesNotExist:
            messages.error(request, "Invalid OTP")

    return render(request, 'accounts/verify_code.html')



# =====================================
# USER LOGIN (USERNAME OR EMAIL)
# =====================================
def login_view(request):
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        # allow login via email
        user_obj = User.objects.filter(email=username_input).first()
        username = user_obj.username if user_obj else username_input

        user = authenticate(request, username=username, password=password)

        if user:
            # 🔥 EMAIL VERIFICATION CHECK
            if not user.emailaddress_set.filter(verified=True).exists():
                messages.error(request, "Please verify your email before logging in.")
                return redirect('account_login')

            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('properties:home')
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'accounts/login.html')


# =====================================
# USER LOGOUT
# =====================================
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('properties:home')


# =====================================
# USER DASHBOARD
# =====================================
@login_required
def user_dashboard(request):

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # PROFILE FORM
    profile_form = ProfileUpdateForm(
        request.POST or None,
        instance=profile,
        user=request.user
    )

    # PASSWORD FORM
    password_form = PasswordChangeForm(
        user=request.user,
        data=request.POST or None
    )

    # USER PROPERTIES
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
