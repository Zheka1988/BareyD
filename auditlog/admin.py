from django.contrib import admin
from auditlog.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_repr', 'short_details', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('object_repr', 'details', 'user__username', 'user__first_name', 'user__last_name')
    search_help_text = 'Поиск по: имя пользователя, имя, фамилия, объект, детали'
    date_hierarchy = 'timestamp'
    readonly_fields = (
        'user', 'action', 'model_name', 'object_id',
        'object_repr', 'details', 'ip_address', 'timestamp',
    )

    @admin.display(description='Детали')
    def short_details(self, obj):
        if obj.details:
            return obj.details[:80] + ('...' if len(obj.details) > 80 else '')
        return '-'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
