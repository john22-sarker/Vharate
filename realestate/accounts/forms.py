from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile


# ============================
# SIGNUP FORM
# ============================
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'full_name',
            'phone_number',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')

        if commit:
            user.save()

            # ✅ Safe profile create/update
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.full_name = self.cleaned_data.get('full_name')
            profile.phone_number = self.cleaned_data.get('phone_number')
            profile.save()

        return user


# ============================
# PROFILE UPDATE FORM (NO PHOTO)
# ============================
class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        # ❌ photo removed (manual upload handle korba)
        fields = ['full_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # 🔹 email initial value
        if user:
            self.fields['email'].initial = user.email

    def save(self, user=None, commit=True):
        profile = super().save(commit=False)

        # 🔹 update user email
        if user:
            user.email = self.cleaned_data.get('email')
            user.save()

        if commit:
            profile.save()

        return profile