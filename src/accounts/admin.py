from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


#on customise l'admin django pour afficher nos champs custom
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    #on ajoute nos champs role et is_verified dans le formulaire d'édition
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Infos Mosifra", {"fields": ("role", "is_verified")}),
    )
    #pareil pour le formulaire de création
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Infos Mosifra", {"fields": ("role",)}),
    )
    list_display = ("email", "username", "role", "is_staff", "is_superuser", "is_active")
    ordering = ("email",)
    search_fields = ("email", "username")
