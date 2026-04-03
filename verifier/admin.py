from django.contrib import admin
from .models import Entity, AttendanceLog # <--- Student ki jagah Entity kar diya

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    # Admin panel mein kaunsi fields nazar aayengi
    list_display = ('name', 'id_number', 'user_type', 'is_verified')
    list_filter = ('user_type', 'is_verified')
    search_fields = ('name', 'id_number')
@admin.register(AttendanceLog)
class AttendanceAdmin(admin.ModelAdmin):
    # Yeh columns Admin Panel mein nazar aayenge
    list_display = ('get_name', 'get_id', 'entry_time', 'date')
    # Side bar mein date filter lag jayega (Today, Past 7 days, etc.)
    list_filter = ('date', 'person__user_type')
    search_fields = ('person__name', 'person__id_number')

    # Helper functions taake Entity ka data yahan dikh sake
    def get_name(self, obj):
        return obj.person.name
    get_name.short_description = 'User Name'

    def get_id(self, obj):
        return obj.person.id_number
    get_id.short_description = 'ID / Roll Number'