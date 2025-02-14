from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
admin.site.register(Like)
