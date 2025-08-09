from django.contrib import admin
from .models import Token, DataFile

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "created_at")
    search_fields = ("user__username", "key")

@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_by", "uploaded_at")
    search_fields = ("file", "uploaded_by__username")