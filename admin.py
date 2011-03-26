from django.contrib import admin
from models import Mount, Authorization, Listener

class MountAdmin(admin.ModelAdmin):
    list_display = ('name', )
admin.site.register(Mount, MountAdmin)

class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ('mount', 'user', 'password', 'start', 'end',)
    list_filter = ('mount',)
    search_fields = ('user',)
admin.site.register(Authorization, AuthorizationAdmin)

class ListenerAdmin(admin.ModelAdmin):
    list_display = ('mount', 'user', 'password', 'start', 'end',)
    list_filter = ('mount',)
    search_fields = ('user',)
admin.site.register(Listener, ListenerAdmin)
