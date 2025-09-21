from django.contrib import admin
from django.urls import path
from .api_reqs import *

urlpatterns = [
    ##USER
    path('get_users', get_users_api),
    path('delete_user', delete_user_api),

    path('insert_client', register_client_api),
    path('login_post', login_client_api),
    #Client
    path('get_clients', get_clients_api),
    path('delete_client/<int:pk>', delete_client_api),
    path('edit_user', edit_user),
    #Client.Appointments
    path('insert_appointment', insert_appointment_api),
    path('get_appointments', get_appointments_api),
    path('client_appointments', dummy),
    path('delete_appointment/<int:pk>', delete_appointment_api),

    ##Doctor
    path('insert_doctor', register_doctor_api),
    path('get_doctors', get_doctors_api),
    #
    #
    #Pets
    ##Pets.allergies
    path('insert_allergy/<int:pk>', insert_allergy_api),
    path('get_allergies/<int:pk>', get_allergies_api),
    
    ##
    path('insert_pet', insert_pet_api),
    path('get_pets', get_pets_api),
    path('delete_pet/<int:pk>', delete_pet_api),
    path('edit_pet_base_api/<int:pk>', edit_pet_base_api),
    #Pets

    ##extras
    path('not_logged', dummy),
    path('dummy', dummy)
    ##
]
