# hospital/urls.py

from django.urls import path
from . import views




urlpatterns = [
  path('', views.user_selection, name='user_selection'),
  path('register/patient/', views.register_patient, name='register_patient'),
  path('login/patient/', views.login_patient,name='login_patient'),
  path('home/patient/',views.home_patient,name='home_patient'),
  path('login/admin/',views.admin_login, name='login_admin'),
  path('home/admin/',views.home_admin,name='home_admin'),
  path('home/adddoctor/',views.add_doctor,name='add_doctor'),
  path('doctor/delete/<int:pk>/', views.delete_doctor, name='delete_doctor'),

  path('login/doctor/',views.doctor_login,name='login_doctor'),
  path('home/doctor/',views.home_doctor,name='home_doctor'),
  path('home/list_doctors/',views.list_doctor,name='list_doctor'),
  path('home/listpatient/',views.list_patient,name='list_patient'),
  path('home/listprescription/',views.list_prescription,name='list_prescription'),
  path('appointments/new/', views.create_appointment, name='create_appointment'),
  path('appoinment/list',views.appointment_list,name='appoinment_list'),
  path('appointment/<int:pk>/', views.view_appointment, name='view_appointment'),
  path('appointment/<int:pk>/edit/', views.update_appointment, name='update_appointment'),
  path('appointment/<int:pk>/delete/', views.delete_appointment, name='delete_appointment'),
  path('patient/appointment/',views.patient_appointment,name='patient_appointment'),
  path('patient/doctors/',views.list_doctor_patient,name='doctor_patient'),
  path('patient/appointment/<int:pk>',views.view_appointment_patient,name='appointment_list_patient'),
  path('patient/appointment/<int:pk>/edit/',views.update_appointment_patient,name='appointment_update_patient'),
  path('patient/appointment/<int:pk>/delete',views.delete_appointment_patient,name='appointment_delete_patient'),
  path('appointments/<int:appointment_id>/update-status/<str:status>/',views.update_appointment_status, name='update_appointment_status'),
  path('appointments/<int:appointment_id>/update-status/<str:status>/',views.delete_appointment_status, name='delete_appointment_status'),
  path('payment-handler/', views.payment_handler, name='payment_handler'),
  path('prescription/create/<int:appointment_id>/', views.create_prescription, name='create_prescription'),
  path('patient/presciption/',views.patient_prescriptions,name='patient_prescriptions')




 
 

]
