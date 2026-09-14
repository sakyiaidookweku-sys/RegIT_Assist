import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.core.mail import send_mail
from .models import Ticket

# Main / Ticketing Views
@csrf_exempt
def report_problem_view(request):
    if request.method == 'POST':
        reporter_name = request.POST.get('reporter_name')
        staff_id = request.POST.get('staff_id')
        corporate_email = request.POST.get('corporate_email')
        district = request.POST.get('district', 'General')
        department = request.POST.get('department', 'General')
        category = request.POST.get('category', 'General')
        description = request.POST.get('description')
        
        # Ensure title is never None by safely fallback-stringing category and district
        title = f"{category} Issue - {district}"
        
        ticket = Ticket.objects.create(
            reporter_name=reporter_name,
            staff_id=staff_id,
            corporate_email=corporate_email,
            district=district,
            department=department,
            category=category,
            title=title,
            description=description,
            priority='Medium'
        )
        
        # Send email notification to console/user
        if corporate_email:
            subject = f"Ticket Received: #{ticket.id} - {title}"
            message = (
                f"Hello {reporter_name},\n\n"
                f"Your support ticket has been successfully received by the RegIT Assist team.\n\n"
                f"Details:\n"
                f"- Ticket ID: #{ticket.id}\n"
                f"- Category: {category}\n"
                f"- Status: {ticket.status}\n\n"
                f"We will review your issue shortly.\n\n"
                f"Best regards,\nRegIT Assist Support Team"
            )
            send_mail(subject, message, None, [corporate_email], fail_silently=True)

        return redirect('problem_success')
        
    return render(request, 'support_app/report_problem.html')

def problem_success_view(request):
    return render(request, 'support_app/problem_success.html')

# Staff Views
def login_view(request):
    error_message = None
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        user = authenticate(request, username=username_input, password=password_input)
        if user is not None:
            login(request, user)
            return redirect('staff_dashboard')
        else:
            error_message = "Invalid username or password."
            
    return render(request, 'support_app/login.html', {'error': error_message})

@login_required(login_url='login')
def staff_dashboard(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    context = {
        'tickets': tickets,
    }
    return render(request, 'support_app/dashboards/staff_dash.html', context)

# Intern Views
def intern_login_view(request):
    error_message = None
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        user = authenticate(request, username=username_input, password=password_input)
        if user is not None:
            login(request, user)
            return redirect('intern_dashboard')
        else:
            error_message = "Invalid username or password."
            
    return render(request, 'support_app/intern_login.html', {'error': error_message})

@login_required(login_url='intern_login')
def intern_dashboard(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    context = {
        'tickets': tickets,
    }
    return render(request, 'support_app/dashboards/intern_dash.html', context)

# Admin Views
def admin_login_view(request):
    error_message = None
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        user = authenticate(request, username=username_input, password=password_input)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error_message = "Invalid admin credentials or insufficient privileges."
            
    return render(request, 'support_app/admin_login.html', {'error': error_message})

@login_required(login_url='admin_login')
def admin_dashboard(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    
    # Get search and filter parameters from the GET request
    search_query = request.GET.get('q', '')
    priority_filter = request.GET.get('priority', '')
    
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) |
            Q(reporter_name__icontains=search_query) |
            Q(staff_id__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)

    context = {
        'tickets': tickets,
        'search_query': search_query,
        'priority_filter': priority_filter,
    }
    return render(request, 'support_app/dashboards/admin_dash.html', context)

# Ticket Status Update View
@login_required
def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            if new_status in ['Pending', 'In Progress', 'Resolved']:
                ticket.status = new_status
                ticket.save()
        except Ticket.DoesNotExist:
            pass
            
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('staff_dashboard')
        
    return redirect('staff_dashboard')

# Filtered Admin Views for Stat Cards
@login_required(login_url='admin_login')
def admin_pending_tickets(request):
    """View listing all pending or in-progress tickets for admins."""
    if not request.user.is_staff:
        return redirect('admin_dashboard')
    
    tickets = Ticket.objects.filter(status__in=['Pending', 'Open', 'In Progress']).order_by('-created_at')
    return render(request, 'support_app/dashboards/admin_pending.html', {'tickets': tickets})

@login_required(login_url='admin_login')
def admin_resolved_tickets(request):
    """View listing all resolved tickets for admins."""
    if not request.user.is_staff:
        return redirect('admin_dashboard')
    
    tickets = Ticket.objects.filter(status='Resolved').order_by('-created_at')
    return render(request, 'support_app/dashboards/admin_resolved.html', {'tickets': tickets})

# Staff & User Management Views
@login_required(login_url='admin_login')
def manage_staff_view(request):
    """View for admins to see and manage support staff and intern accounts."""
    if not request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Assuming standard Django User model is used for staff/interns
    from django.contrib.auth.models import User
    staff_members = User.objects.all().order_by('-date_joined')
    
    context = {
        'staff_members': staff_members,
    }
    return render(request, 'support_app/dashboards/manage_staff.html', context)

@login_required(login_url='admin_login')
def toggle_user_status(request, user_id):
    """Activate or deactivate a staff/intern account."""
    if not request.user.is_staff:
        return redirect('admin_dashboard')
    
    from django.contrib.auth.models import User
    target_user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from deactivating themselves
    if target_user != request.user:
        target_user.is_active = not target_user.is_active
        target_user.save()
        
    return redirect('manage_staff')

# CSV Export View
@login_required(login_url='admin_login')
def export_tickets_csv(request):
    """Export all tickets as a downloadable CSV file."""
    if not request.user.is_staff:
        return redirect('admin_dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="regit_assist_tickets.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Reporter Name', 'Staff ID', 'District', 'Department', 'Category', 'Priority', 'Status', 'Created At'])

    tickets = Ticket.objects.all().order_by('-created_at')
    for ticket in tickets:
        writer.writerow([
            ticket.id,
            ticket.title,
            ticket.reporter_name,
            ticket.staff_id,
            ticket.district,
            ticket.department,
            ticket.category,
            ticket.priority,
            ticket.status,
            ticket.created_at
        ])

    return response

import os
from google import genai
from django.http import JsonResponse

def chat_api(request):
    if request.method == "POST":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return JsonResponse({"error": "GEMINI_API_KEY is not configured."}, status=500)

        user_message = request.POST.get("message", "")
        if not user_message:
            return JsonResponse({"error": "Message parameter is required."}, status=400)

        try:
            client = genai.Client(api_key=api_key)
            
            # Use a standard Gemini Flash model identifier
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=user_message,
            )
            
            return JsonResponse({"reply": response.text})
            
        except Exception as e:
            return JsonResponse({"error": f"API call failed: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)