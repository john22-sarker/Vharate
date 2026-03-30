from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # 🔹 USER INFO
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)

    # 🔹 PROFILE PHOTO
    photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.username} Profile"


# ============================
# AUTO CREATE PROFILE
# ============================
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            full_name=instance.username
        )
    else:
        # 🔥 Ensure profile always exists
        UserProfile.objects.get_or_create(user=instance)