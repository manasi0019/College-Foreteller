from re import U
from django.contrib import admin
from .models import UserInformation
# Register your models here.
@admin.register(UserInformation)
class UserInformationAdmin(admin.ModelAdmin):
    list_display = ['fname', 'username', 'mobile', 'email']