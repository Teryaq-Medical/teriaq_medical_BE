from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from rest_framework.authtoken.models import Token

try:
    admin.site.unregister(Token)
except admin.sites.NotRegistered:
    pass


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)

# 1. Form for adding users (Password Hashing only, Signal handles Token)
class UserCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, 
        label="كلمة المرور",
        help_text="يتم تشفير كلمة المرور وتوليد التوكين تلقائياً عند الحفظ."
    )

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number', 'user_type', 'password', 'is_active', 'is_staff', 'is_superuser')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# 2. User Admin Configuration
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'user_type', 'phone_number', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_superuser')
    search_fields = ('email', 'full_name', 'phone_number')
    
    # Read-only fields in the edit page
    readonly_fields = ('date_joined', 'display_token')

    def display_token(self, obj):
        # We try to get the token; if it's missing, we create it on the fly
        token, created = Token.objects.get_or_create(user=obj)
        return mark_safe(f'<strong style="color: #e67e22; font-family: monospace;">{token.key}</strong>')
    
    display_token.short_description = "رمز التحقق (Token)"

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return UserCreationForm
        return super().get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ('email', 'full_name', 'phone_number', 'user_type', 'password', 'is_active', 'is_staff', 'is_superuser')
        
        return (
            'email', 'full_name', 'phone_number', 'user_type', 
            'is_active', 'is_staff', 'is_superuser', 'date_joined', 
        )
