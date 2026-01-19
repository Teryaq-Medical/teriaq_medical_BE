from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import User
from specialists.models import Specialist


class Hospital(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='hospital',verbose_name="المستخدم")
    name = models.CharField(max_length=100,verbose_name="اسم المعمل")
    image = CloudinaryField('صورة')
    specialist = models.ManyToManyField(Specialist,related_name='hospital',verbose_name="المستشفى")
    address = models.CharField(max_length=200,verbose_name="العنوان")
    phone = models.CharField(max_length=20,verbose_name="الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني" )
    rating = models.IntegerField(verbose_name="التقييم")

    class Meta:
        verbose_name = "مستشفي"
        verbose_name_plural = "مستشفيات"


    def __str__(self):
        return self.name
