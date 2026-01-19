from django.db import models


class Specialist(models.Model):
    name = models.CharField(max_length=100,verbose_name="اسم التخصص") 
    
    class Meta:
        verbose_name = "التخصص"
        verbose_name_plural = "التخصصات"

    def __str__(self):
        return self.name

