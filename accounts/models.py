from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('community', 'عضو مجتمع'),
        ('normal', 'مستخدم عادي'),
        ('doctors','أطباء'),
        ('clincs','عيادات')
    )

    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    full_name = models.CharField(max_length=255, verbose_name="الاسم الكامل")
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف")

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        verbose_name="نوع المستخدم"
    )

    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_staff = models.BooleanField(default=False, verbose_name="موظف")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الانضمام")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمين"

    def __str__(self):
        return self.full_name


class CommunityMember(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='community_profile',
        verbose_name="المستخدم"
    )

    community_name = models.CharField(max_length=255, verbose_name="اسم المجتمع")
    membership_number = models.CharField(max_length=100, verbose_name="رقم العضوية")
    
    class Meta:
        verbose_name = "عضو نقابة"
        verbose_name_plural = "أعضاء نقابة"

    def __str__(self):
        return f"{self.user.full_name} - {self.community_name}"


class NormalUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='normal_profile',
        verbose_name="المستخدم"
    )

    national_id = models.CharField(max_length=50, verbose_name="الرقم القومي")
    
    class Meta:
        verbose_name = "مستخدم عادي"
        verbose_name_plural = "المستخدمين العاديين"

    def __str__(self):
        return self.user.full_name
