from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import User




class LapCategory(models.Model):
    name = models.CharField(max_length=100,verbose_name="التخصص")

    class Meta:
        verbose_name = "القسم"
        verbose_name_plural = "الاقسام"
        
    def __str__(self):
        return self.name

class Labs(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='labs',
        verbose_name="المستخدم"
    )
    name = models.CharField(max_length=100,verbose_name="اسم المعمل")
    image = CloudinaryField('صورة')
    categories = models.ManyToManyField(LapCategory,related_name='labs',verbose_name="الاقسام")
    address = models.CharField(max_length=200,verbose_name="العنوان")
    phone = models.CharField(max_length=20,verbose_name="الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني" )
    rating = models.IntegerField(verbose_name="التقييم")

    class Meta:
        verbose_name = "المعمل"
        verbose_name_plural = "المعامل"


    def __str__(self):
        return self.name
