from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
    
    def __str__(self):
        return self.name


class Area(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='areas')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        unique_together = ('city', 'name')  # prevent duplicate area names in the same city
    
    def __str__(self):
        return f"{self.name} ({self.city.name})"


class SubArea(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='subareas')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Sub-Area"
        verbose_name_plural = "Sub-Areas"
        unique_together = ('area', 'name')  # prevent duplicate subarea names in the same area

    def __str__(self):
        return f"{self.name} ({self.area.name} - {self.area.city.name})"
