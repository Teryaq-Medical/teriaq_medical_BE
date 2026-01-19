from django.db import models
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField
from specialists.models import Specialist
from accounts.models import User


class Clincs(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='clinics',
        verbose_name=_("المستخدم")
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم العيادة")
    )

    image = CloudinaryField(
        ("الصورة")
    )

    Specialist = models.ManyToManyField(
        Specialist,
        related_name='clincs',
        verbose_name=_("التخصصات")
    )

    class Meta:
        verbose_name = _("عيادة")
        verbose_name_plural = _("العيادات")

    def __str__(self):
        return self.name
