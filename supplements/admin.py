from django.contrib import admin

from .models import ProteinPowder, Creatine, Brand


class ProteinPowderAdmin(admin.ModelAdmin):
    list_display = ["name", "weight", "brand", "type", "url"]


class CreatineAdmin(admin.ModelAdmin):
    list_display = ["name", "weight", "brand", "form", "type", "url"]


admin.site.register(ProteinPowder, ProteinPowderAdmin)
admin.site.register(Creatine, CreatineAdmin)
admin.site.register(Brand)
