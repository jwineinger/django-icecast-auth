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
    list_display = ('mount', 'user', 'start', 'end',)
    list_filter = ('mount', 'user')
    search_fields = ('user',)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []   
        if not request.user.is_superuser:
            self.exclude.append('password')
        return super(ListenerAdmin, self).get_form(request, obj, **kwargs)
admin.site.register(Listener, ListenerAdmin)
