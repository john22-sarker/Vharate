from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from locations.models import City, Area, SubArea


class Property(models.Model):
    # ======================
    # PROPERTY TYPE CHOICES
    # ======================
    APARTMENT = 'Apartment'
    FAMILY_HOUSE = 'Family House'
    BACHELOR_HOUSE = 'Bachelor House'

    PROPERTY_TYPE_CHOICES = [
        (APARTMENT, 'Apartment'),
        (FAMILY_HOUSE, 'Family House'),
        (BACHELOR_HOUSE, 'Bachelor House'),
    ]

    # ======================
    # BASIC INFO
    # ======================
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES
    )

    price = models.DecimalField(max_digits=12, decimal_places=2)

    # ======================
    # LOCATION
    # ======================
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        related_name='properties'
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        related_name='properties'
    )

    subarea = models.ForeignKey(
        SubArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties'
    )

    address = models.CharField(max_length=250, blank=True, null=True)

    # ======================
    # PROPERTY DETAILS
    # ======================
    rooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()

    size_sqft = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Size in square feet"
    )

    # ======================
    # CONTACT INFO
    # ======================
    contact_name = models.CharField(max_length=100, default="Unknown")
    contact_phone = models.CharField(max_length=20, default="0000000000")
    contact_email = models.EmailField(blank=True, null=True)
    contact_whatsapp = models.CharField(max_length=20, blank=True, null=True)

    # ======================
    # FACILITIES
    # ======================
    wifi_available = models.BooleanField(default=False)
    dog_allowed = models.BooleanField(default=False)
    smoking_allowed = models.BooleanField(default=False)
    garage_available = models.BooleanField(default=False)
    music_allowed = models.BooleanField(default=False)

    gate_close_time = models.TimeField(blank=True, null=True)

    # ======================
    # IMAGES
    # ======================
    main_image = models.ImageField(upload_to='property_images/')
    image_2 = models.ImageField(upload_to='property_images/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='property_images/', blank=True, null=True)
    image_4 = models.ImageField(upload_to='property_images/', blank=True, null=True)

    # ======================
    # META INFO
    # ======================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['area']),
            models.Index(fields=['price']),
            models.Index(fields=['property_type']),
        ]

    # ======================
    # SAVE METHOD (SLUG)
    # ======================
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Property.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # ======================
    # STRING REPRESENTATION
    # ======================
    def __str__(self):
        return f"{self.title} ({self.property_type})"