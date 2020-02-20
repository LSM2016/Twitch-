from django.contrib import admin
from .models import Channel, Clip, Cursor, HighlightClip

# Register your models here.
admin.site.register(Channel)
admin.site.register(Cursor)
admin.site.register(HighlightClip)

@admin.register(Clip)
class ClipAdmin(admin.ModelAdmin):
    list_display = ('title','views','created_at')
    search_fields = ('title','created_at')