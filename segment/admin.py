from django.contrib import admin
from segment.models import Tag
from segment.models import ImageType


class TagAdmin(admin.ModelAdmin):
    list_display =('name','image_type',)
    search_fields=('name',)

admin.site.register(Tag,TagAdmin)

class ImageTypeAdmin(admin.ModelAdmin):
    list_display =('name',)
    search_fields=('name',)

admin.site.register(ImageType,ImageTypeAdmin)


