from django import forms
from .models import Property
from locations.models import City, Area, SubArea


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'price',
            'city', 'area', 'subarea', 'address',
            'rooms', 'bathrooms', 'size_sqft',
            'contact_name', 'contact_phone', 'contact_email', 'contact_whatsapp',
            'wifi_available', 'dog_allowed', 'smoking_allowed', 'gate_close_time',
            'garage_available', 'music_allowed',
            'main_image', 'image_2', 'image_3', 'image_4'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),

            'city': forms.Select(attrs={'class': 'form-select', 'id': 'id_city'}),
            'area': forms.Select(attrs={'class': 'form-select', 'id': 'id_area'}),
            'subarea': forms.Select(attrs={'class': 'form-select', 'id': 'id_subarea'}),

            'address': forms.TextInput(attrs={'class': 'form-control'}),

            'rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'size_sqft': forms.NumberInput(attrs={'class': 'form-control'}),

            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_whatsapp': forms.TextInput(attrs={'class': 'form-control'}),

            'gate_close_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    # =====================================
    # INIT METHOD (AUTO FILL + DROPDOWNS)
    # =====================================
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # 👈 important
        super().__init__(*args, **kwargs)

        # =========================
        # AUTO FILL FROM USER PROFILE
        # =========================
        if self.user:
            try:
                profile = self.user.profile

                self.fields['contact_name'].initial = profile.full_name
                self.fields['contact_phone'].initial = profile.phone_number
                self.fields['contact_email'].initial = self.user.email

            except Exception:
                pass

        # =========================
        # DEPENDENT DROPDOWNS
        # =========================

        # Initially
        self.fields['city'].queryset = City.objects.all()
        self.fields['area'].queryset = Area.objects.none()
        self.fields['subarea'].queryset = SubArea.objects.none()

        # ---- CITY → AREA ----
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['area'].queryset = Area.objects.filter(city_id=city_id)
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.city:
            self.fields['area'].queryset = Area.objects.filter(city=self.instance.city)

        # ---- AREA → SUBAREA ----
        if 'area' in self.data:
            try:
                area_id = int(self.data.get('area'))
                self.fields['subarea'].queryset = SubArea.objects.filter(area_id=area_id)
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.area:
            self.fields['subarea'].queryset = SubArea.objects.filter(area=self.instance.area)