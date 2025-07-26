# hospital/models.py

from django.db import models
from django.contrib.auth.models import User
from datetime import time

# Patient Model


class Patient(models.Model):

    GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
    ('U', 'Unknown')
]
    BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('U', 'Unknown')
    
]
   
    name = models.CharField( max_length=50)
    password = models.CharField( max_length=50)
    bloodgroup = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        default='U'
    )
    email = models.EmailField(
        max_length=50,
        default='unknown@example.com'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='U'  # Simple single-char default
    )
    date_of_birth = models.DateField()
    contact_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    allergies = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} "

# Doctor Model
class Doctor(models.Model):
    username = models.CharField( max_length=50)
    fee = models.DecimalField(max_digits=8, decimal_places=2)  # Add this field
    password = models.CharField( max_length=50)
    name = models.CharField( max_length=50)
    specialty = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    available_days = models.JSONField()  # Example: ["Monday", "Wednesday", "Friday"]
    available_hours = models.JSONField()  # Example: ["9:00 AM - 1:00 PM"]

    def __str__(self):
        return f"Dr. {self.name}"


def default_appointment_time():
    return time(14, 30)


# Appointment Model
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField(default=default_appointment_time)
    symptoms = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    status_choices = [
        ('pending', 'Pending'),
        ('confirm', 'confirm'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    
    payment_status = models.BooleanField(default=False)  # Track payment status
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Appointment for {self.patient.name} with Dr. {self.doctor.user.name}"
    

class Admin(models.Model):
    username = models.CharField( max_length=50)
    password = models.CharField( max_length=50)

    def __str__(self):
        return self.username
    
class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='prescriptions'  
    )
    symptoms = models.TextField()
    diagnosis = models.TextField()
    medicines = models.TextField()
    advice = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    

    def __str__(self):
        return f"Prescription for {self.patient.name} by Dr. {self.doctor.name}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('created', 'Created'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]

    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.razorpay_order_id} - {self.get_status_display()}"


