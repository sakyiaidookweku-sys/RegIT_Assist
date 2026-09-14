from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        # If your model has other fields like 'title' or 'priority', add them here along with 'issue_description'
        fields = ['issue_description']  # Expand this list if your Ticket model has more fields (e.g., ['title', 'issue_description'])
        widgets = {
            'issue_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your software, hardware, or network issue...',
                'rows': 4
            })
        }