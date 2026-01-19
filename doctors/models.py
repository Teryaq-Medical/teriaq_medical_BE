from django.db import models
from specialists.models import Specialist
from cloudinary.models import CloudinaryField
from accounts.models import User

class Doctors(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctors',
        verbose_name="المستخدم"
    )
    name = models.CharField(max_length=50, verbose_name="الاسم")
    age = models.IntegerField(verbose_name="العمر")
    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        related_name='doctors',
        verbose_name="التخصص"
    )
    phone_number = models.IntegerField(verbose_name="رقم الهاتف")
    address = models.CharField(max_length=200, verbose_name="العنوان")
    license = CloudinaryField('رخصة العمل')
    doctor_image = CloudinaryField('صورة الطبيب')
    
    class Meta:
        verbose_name = "طبيب"
        verbose_name_plural = " الأطباء"
    
    def __str__(self):
        return self.name
