from django.urls import path
from . import views

urlpatterns = [
    # Main Root / Landing Page
    path('', views.report_problem_view, name='home'),

    # Staff routes
    path('staff/login/', views.login_view, name='login'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),

    # Intern routes
    path('intern/login/', views.intern_login_view, name='intern_login'),
    path('intern/dashboard/', views.intern_dashboard, name='intern_dashboard'),

    # Admin routes
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Ticketing / Problem Reporting
    path('report/', views.report_problem_view, name='report_problem'),
    path('report/success/', views.problem_success_view, name='problem_success'),

    # Ticket Status Update Route
    path('ticket/<int:ticket_id>/update/', views.update_ticket_status, name='update_ticket_status'),

    # New Filtered Ticket Views (Step 1)
    path('admin/tickets/pending/', views.admin_pending_tickets, name='admin_pending_tickets'),
    path('admin/tickets/resolved/', views.admin_resolved_tickets, name='admin_resolved_tickets'),

    # Staff Management Routes (Step 2)
    path('admin/staff/manage/', views.manage_staff_view, name='manage_staff'),
    path('admin/staff/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),

    # CSV Export Route
    path('admin/tickets/export/', views.export_tickets_csv, name='export_tickets_csv'),
]