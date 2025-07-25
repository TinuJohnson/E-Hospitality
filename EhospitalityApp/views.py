
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Admin, Patient,Doctor,Appointment,Prescription
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt 
from .forms import AppointmentForm
from django.shortcuts import render, redirect, get_object_or_404
import razorpay
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator


def user_selection(request):
    return render(request, 'user_selection.html',  {'MEDIA_URL': settings.MEDIA_URL})




def register_patient(request):
    if request.method == 'POST':
        # Get form data with defaults for optional fields
        name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '').strip()
        password1 = request.POST.get('password1', '').strip()
        email = request.POST.get('email', '').strip()
        gender = request.POST.get('gender', '').strip()
        bloodgroup = request.POST.get('bloodgroup', '').strip()
        date_of_birth = request.POST.get('date_of_birth')
        contact_number = request.POST.get('contact_number', '').strip()
        address = request.POST.get('address', '').strip()
        allergies = request.POST.get('allergies', '').strip()
        medical_history = request.POST.get('medical_history', '').strip()

    
        if not all([name, password, password1, email, date_of_birth, contact_number, address]):
            messages.error(request, "Please fill all required fields.")
            return redirect('register_patient')

 
        if password != password1:
            messages.error(request, "Passwords do not match.")
            return redirect('register_patient')
        
        
        if not contact_number.isdigit() or len(contact_number) < 10:
            messages.error(request, "Please enter a valid phone number.")
            return redirect('register_patient')

        try:
            
            patient = Patient(
                name=name,
                password=password,  
                email=email,
                gender=gender,
                bloodgroup=bloodgroup,
                date_of_birth=date_of_birth,
                contact_number=contact_number,
                address=address,
                allergies=allergies,
                medical_history=medical_history
            )
            
            patient.full_clean()
            patient.save()

            messages.success(request, "Registration successful! You can now login.")
            return redirect('login_patient')
            
       
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")

  
    context = {
        'gender_choices': Patient.GENDER_CHOICES,
        'bloodgroup_choices': Patient.BLOOD_GROUP_CHOICES ,
    }
    
    return render(request, 'patient/register_patient.html', context)


def login_patient(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        if not phone_number or not password:
            messages.error(request, "Both phone number and password are required.")
            return redirect('login_patient')
        
        try:
            patient = Patient.objects.get(contact_number=phone_number)
            
            if patient.password == password:  
                request.session['patient_id'] = patient.id
                request.session['patient_name'] = patient.name
                
                return redirect('home_patient')
            else:
                messages.error(request, "Invalid password.")
        except Patient.DoesNotExist:
            messages.error(request, "No account found with this phone number.")
        except Exception as e:
            messages.error(request, f"Login error: {str(e)}")
        
        return redirect('login_patient')
    
    return render(request, 'patient/login_patient.html')



def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "Both phone number and password are required.")
            return redirect('login_admin')
        
        try:
            admin = Admin.objects.get(username=username)
            
            if admin.password == password:  
                request.session['admin_id'] = admin.id
                request.session['admin_username'] = admin.username
                
                return redirect('home_admin')
            else:
                messages.error(request, "Invalid password.")
        except Patient.DoesNotExist:
            messages.error(request, "No account found with this phone number.")
        except Exception as e:
            messages.error(request, f"Login error: {str(e)}")
        
        return redirect('login_admin')
    
    return render(request, 'admin/login_admin.html')


def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "Both phone number and password are required.")
            return redirect('login_doctor')
        
        try:
            doctor = Doctor.objects.get(username=username)
            
            if doctor.password == password:  
                request.session['doctor'] = doctor.id
                request.session['doctor_username'] = doctor.username
                
                return redirect('home_doctor')
            else:
                messages.error(request, "Invalid password.")
        except Patient.DoesNotExist:
            messages.error(request, "No account found with this phone number.")
        except Exception as e:
            messages.error(request, f"Login error: {str(e)}")
        
        return redirect('login_doctor')
    
    return render(request, 'doctor/login_doctor.html')



def home_patient(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login_patient')
    
    doctors = Doctor.objects.all()
    appointments=Appointment.objects.filter(patient=patient_id)
    
    patient = Patient.objects.get(id=patient_id)
    return render(request, 'patient/home_patient.html', {'patient': patient , 'doctors':doctors , 'appointments':appointments})

def home_admin(request):
      return render(request, 'admin/home_admin.html')


def home_doctor(request):
    
    doctor_id = request.session.get('doctor')
    if not doctor_id:
        return redirect('login_doctor')
     
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    today = timezone.now().date()
   
    all_appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', '-appointment_time')
   
    paginator = Paginator(all_appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    todays_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).order_by('appointment_time')
    
    stats = {
        'total': all_appointments.count(),
        'completed': all_appointments.filter(status='completed').count(),
        'pending': all_appointments.filter(status='pending').count(),
        'confirmed': all_appointments.filter(status='confirm').count(),
        'canceled': all_appointments.filter(status='canceled').count(),
    }
    
    context = {
        'doctor': doctor,
        'appointments': page_obj,
        'todays_appointments': todays_appointments,
        'stats': stats,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'doctor/home_doctor.html', context)

def update_appointment_status(request, appointment_id, status):
    doctor_id = request.session.get('doctor')
   
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.doctor.id != doctor_id:
        return redirect('home_doctor')
    
    valid_statuses = [choice[0] for choice in Appointment.status_choices]
    if status in valid_statuses:
        appointment.status = status
        appointment.save()
    
    return redirect('home_doctor')

def delete_appointment_status(request, appointment_id, status):
    doctor_id = request.session.get('doctor')
   
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.doctor.id != doctor_id:
        return redirect('home_doctor')
    
    
    appointment.delete()
    
    return redirect('home_doctor')




client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_appointment(request):
    if not request.session.get('patient_id'):
        return redirect('login_patient')
    
    try:
        patient = Patient.objects.get(id=request.session['patient_id'])
    except Patient.DoesNotExist:
        return redirect('login_patient')
        
    if request.method == 'POST':
        form = AppointmentForm(request.POST, patient=patient)
        if form.is_valid():
            # Check if Razorpay client is properly initialized
            if not client:
                messages.error(request, "Payment system is not configured properly. Please contact administrator.")
                return render(request, 'patient/add_appoinment.html', {'form': form})
            
            appointment = form.save(commit=False)
            # Get fee from the selected doctor
            appointment.fee = appointment.doctor.fee  # Get fee from doctor model
            appointment.save()
            
            # Create Razorpay order
            try:
                amount = int(appointment.fee * 100)  # Convert to paise
                order_data = {
                    'amount': amount,
                    'currency': 'INR',
                    'receipt': f'appointment_{appointment.id}',
                    'payment_capture': 1
                }
                order = client.order.create(data=order_data)
                
                # Save Razorpay order ID
                appointment.razorpay_order_id = order['id']
                appointment.save()
                
                # Prepare payment context
                context = {
                    'appointment': appointment,
                    'razorpay_key': settings.RAZORPAY_KEY_ID,
                    'order_id': order['id'],
                    'amount': amount,
                    'patient_name': patient.name,
                    'patient_email': patient.email
                }
                
                
                return render(request, 'payment/payment.html', context)
            except Exception as e:
                print(f"Razorpay order creation failed: {str(e)}")
                appointment.delete()  # Clean up the appointment if payment order fails
                messages.error(request, "Failed to create payment order. Please try again.")
                return render(request, 'patient/add_appoinment.html', {'form': form})
    else:
        form = AppointmentForm(patient=patient)
    
    return render(request, 'patient/add_appoinment.html', {'form': form})

@csrf_exempt
def payment_handler(request):
    if request.method == 'POST':
        try:
            # Check if Razorpay client is properly initialized
            if not client:
                print("Razorpay client not initialized")
                return redirect('payment_failed')
            
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)
            
            # Update appointment payment status
            appointment = Appointment.objects.get(razorpay_order_id=order_id)
            appointment.payment_status = True
            appointment.razorpay_payment_id = payment_id  # Store payment ID for reference
            appointment.save()
            
            return redirect('appointment_success')
        except Exception as e:
            # Log the error for debugging
            print(f"Payment verification failed: {str(e)}")
            return redirect('payment_failed')
    
    return HttpResponse(status=400)


def view_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointment/view_appointment.html', {'appointment': appointment})

def update_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appoinment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointment/update_appointment.html', {'form': form})

def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appoinment_list')
    return render(request, 'appointment/confirm_delete.html', {'appointment': appointment})



def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-appointment_date')
    return render(request, 'admin/appoinment_list.html', {'appointments': appointments})

def list_prescription(request):
    prescriptions= Prescription.objects.all()
    context = {'prescriptions': prescriptions}
    return render(request, 'admin/prescription_list.html' , context)

def list_patient(request):
    patients = Patient.objects.all()
    context = {'patients': patients}
    return render(request, 'admin/patient_list.html', context)

def list_doctor(request):
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render(request, 'admin/doctor_list.html', context)

def delete_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.delete()
    return redirect('list_doctor')  

def patient_prescriptions(request):
    
    patient_id = request.session.get('patient_id')
    patient = Patient.objects.get(id=patient_id)
    prescriptions = Prescription.objects.filter(
        patient = Patient.objects.get(id=patient_id)
    ).select_related('doctor', 'appointment').order_by('-date')
    
    return render(request, 'patient/patient_prescriptions.html', {
        'prescriptions': prescriptions,
        'patient':patient
    })




def logout(request):
    return render(request, 'user_selection')



def patient_appointment(request):
    patient_id = request.session.get('patient_id')
    appointments=Appointment.objects.filter(patient=patient_id)
    patient = Patient.objects.get(id=patient_id)
    return render(request, 'patient/patient_appointment.html', { 'patient':patient, 'appointments':appointments})

def list_doctor_patient(request):
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render(request, 'patient/doctor_list.html', context)

def view_appointment_patient(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'patient/view_appointment.html', {'appointment': appointment})

def update_appointment_patient(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('patient_appointment')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'patient/update_appointment.html', {'form': form})

def delete_appointment_patient(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('patient_appointment')
    return render(request, 'patient/delete_appointment.html', {'appointment': appointment})



def add_doctor(request):
    
    if request.method == 'POST':
        try:
           
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            specialty = request.POST.get('specialty')
            contact_number = request.POST.get('contact_number')
            fee = request.POST.get('consultation_fee')
            available_days = request.POST.getlist('available_days')
            available_hours = request.POST.get('available_hours')
           
            doctor = Doctor(
                username=username,
                password=password,  
                name=name,
                fee=fee,
                specialty=specialty,
                contact_number=contact_number,
                available_days=available_days,
                available_hours=available_hours
            )
            doctor.save()
            
            
            return redirect('home_admin')
        
        except Exception as e:
            messages.error(request, f'Error adding doctor: {str(e)}')
   
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    common_hours = [
        '9:00 AM - 1:00 PM',
        '2:00 PM - 6:00 PM',
        '9:00 AM - 5:00 PM',
        'Emergency Only'
    ]
    
    context = {
        'days_of_week': days_of_week,
        'common_hours': common_hours
    }
    return render(request, 'admin/add_doctor.html', context)



@csrf_exempt
def create_prescription(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        doctor = appointment.doctor

        symptoms = request.POST.get('symptoms')
        diagnosis = request.POST.get('diagnosis')
        medicines = request.POST.get('medicines')
        advice = request.POST.get('advice')

        Prescription.objects.create(
            patient=appointment.patient,
            doctor=doctor,
            appointment=appointment,
            symptoms=symptoms,
            diagnosis=diagnosis,
            medicines=medicines,
            advice=advice
        )

        return redirect('home_doctor') 

    return redirect('home_doctor')

def education_static(request):
    return render(request, 'patient/health_education_resource.html')






# import stripe
# from django.conf import settings
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import Patient, Appointment
# from .forms import AppointmentForm

# stripe.api_key = settings.STRIPE_SECRET_KEY

# def create_appointment(request):
#     if not request.session.get('patient_id'):
#         return redirect('login_patient')
    
#     try:
#         patient = Patient.objects.get(id=request.session['patient_id'])
#     except Patient.DoesNotExist:
#         return redirect('login_patient')
        
#     if request.method == 'POST':
#         form = AppointmentForm(request.POST, patient=patient)
#         if form.is_valid():
#             appointment = form.save(commit=False)
#             appointment.patient = patient
#             appointment.fee = appointment.doctor.fee
            
#             try:
#                 # Create Stripe Payment Intent
#                 payment_intent = stripe.PaymentIntent.create(
#                     amount=int(appointment.fee * 100),  # Convert to cents/paisa
#                     currency='inr',
#                     payment_method_types=['card'],
#                     metadata={
#                         'patient_id': patient.id,
#                         'doctor_id': appointment.doctor.id,
#                         'appointment_type': 'consultation'
#                     },
#                     description=f"Appointment with Dr. {appointment.doctor.name}"
#                 )
                
#                 # Save appointment with pending status
#                 appointment.status = 'pending_payment'
#                 appointment.stripe_payment_intent_id = payment_intent.id
#                 appointment.save()
                
#                 # Return JSON response for AJAX handling
#                 if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                     return JsonResponse({
#                         'success': True,
#                         'redirect_url': reverse('payment_page', kwargs={'appointment_id': appointment.id})
#                     })
#                 else:
#                     return redirect('payment_page', appointment_id=appointment.id)
                
#             except stripe.error.StripeError as e:
#                 error_msg = f"Payment error: {str(e)}"
#             except Exception as e:
#                 error_msg = f"An error occurred: {str(e)}"
            
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({'success': False, 'error': error_msg}, status=400)
#             else:
#                 messages.error(request, error_msg)
    
#     else:
#         form = AppointmentForm(patient=patient)
    
#     return render(request, 'patient/add_appoinment.html', {'form': form})



# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError as e:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return HttpResponse(status=400)

#     if event['type'] == 'payment_intent.succeeded':
#         payment_intent = event['data']['object']
#         appointment = Appointment.objects.get(
#             stripe_payment_intent_id=payment_intent.id
#         )
#         appointment.status = 'confirmed'
#         appointment.payment_status = True
#         appointment.save()

#     return HttpResponse(status=200)
# def payment_page(request, appointment_id):
#     try:
#         appointment = Appointment.objects.get(id=appointment_id)
#         patient = Patient.objects.get(id=request.session['patient_id'])
        
#         # Retrieve the PaymentIntent
#         payment_intent = stripe.PaymentIntent.retrieve(appointment.stripe_payment_intent_id)
        
#         return render(request, 'payment/payment.html', {
#             'client_secret': payment_intent.client_secret,
#             'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
#             'appointment': appointment,
#             'patient': patient
#         })
#     except Exception as e:
#         messages.error(request, f"Error loading payment page: {str(e)}")
#         return redirect('create_appointment')
            