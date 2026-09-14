from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'department')
    search_fields = ('title', 'description')