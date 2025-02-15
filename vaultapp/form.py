from django import forms
from .models import Letter
from django.utils import timezone
import pytz

class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = ['recipient_email', 'content', 'send_date', 'title', 'is_public']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define the Nepal time zone (NPT)
        nepal_timezone = pytz.timezone('Asia/Kathmandu')
        
        # Get the current time in UTC and convert it to Nepal Standard Time (NPT)
        local_time_npt = timezone.now().astimezone(nepal_timezone)
        
        # Set the default send_date to the current NPT time
        self.fields['send_date'].initial = local_time_npt
        
        # Set widget for send_date as a datetime-local input
        self.fields['send_date'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'min': local_time_npt.strftime('%Y-%m-%dT%H:%M'),  # Ensure it's in NPT time
        })
        
        # Make title optional and hide it initially
        self.fields['title'].required = False
