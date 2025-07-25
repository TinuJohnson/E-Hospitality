from django import forms
from .models import Appointment, Doctor, Patient
from django.utils import timezone

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'symptoms',]  # exclude patient
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'symptoms': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)  # Accept patient from view
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.patient = patient  # Store it for use in save()

    def save(self, commit=True):
        appointment = super().save(commit=False)
        if self.patient:
            appointment.patient = self.patient
        if commit:
            appointment.save()
        return appointment

