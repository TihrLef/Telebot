from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import MyUserCreationForm, MyUserChangeForm
from .models import User

class MyUserAdmin(UserAdmin):
    add_form = MyUserCreationForm
    form = MyUserChangeForm
    model = User
    add_fieldsets = (
        (None, {"fields": ("username", 
                           "password", 
                           "password2", 
                           "telegram_id")}),)
    list_display = ["username", "telegram_id"]

admin.site.register(User, MyUserAdmin)