from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('blog', blog_view, name='blog_view'),

    path('', main, name='index'),
    path('register', register_view),
    path('register_post', register_client, name='register_post'),
    path('login_post', login_client, name='login_post'),
    path('login', login_view, name='login'),
    path('test', template2_test, name = 'test'),
    path('logout', logout_post, name='logout_post'),
    #Client
    path('client_view', client_main_view, name='profile'),
    path('delete_client', delete_client, name='delete_client_post'),
    path('edit_client', edit_client, name='edit_client_post'),
    #Client.Appointments
    path('insert_appointment_post', new_appointment_post, name='new_appointment_post'),
    path('new_appointment', new_appointment_view, name='new_appointment'),
    path('appointments', all_appointments_view, name='client_appointments'),
    path('client_appointments', dummy),
    path('delete_appointment/<int:pk>', delete_appointment, name='delete_appointment'),
    path('edit_appointment/<int:pk>', edit_appointment_view, name='edit_appointment_view'),
    path('edit_appointment_post', edit_appointment_post, name='edit_appointment_post'),
    #
    #
    #Pets
    ##Pets.allergies
    path('insert_allergy_post', insert_allergy_post, name='insert_allergy_post'),
    path('delete_allergy_post', delete_allergy_post, name='delete_allergy_post'),
    
    ##
    path('insert_pet', insert_pet_view, name='insert_pet_view'),
    path('insert_pet_post', insert_pet_post, name='insert_pet_post'),
    path('client_pets', all_pets_view, name='client_pets'),
    path('edit_pet_view/<int:pk>', edit_pet_view, name='edit_pet_view'),
    path('delete_pet/<int:pk>', delete_pet_post),
    path('all', get_pets),
    #Pets


    ##DOCTORS
    path('doctors_view', all_doctors_view, name='doctors_view'),
    path('doctor_pet_search_view', doctor_pet_search, name='doctor_search_pet_view'),
    path('doctor_main_view', doctor_main_view, ),
    path('doctor_appointments_view', doctor_appointments_view, name='doctor_appointments_view'),
    path('doctor_appointment_view', doctor_appointment_view, name='doctor_appointment_view'),
    path('doctor_end_appointment_post', doctor_end_appointment_post, name='doctor_end_appointment_post'),
    path('doctor_pet_view/<int:pk>', doctor_pet_view, name='doctor_pet_view'),
    path('insert_pet_vaccine_post', insert_pet_vaccine_post, name='insert_pet_vaccine_post'),
    ##
    ##extras
    path('not_logged', not_logged_client),
    path('dummy', dummy)
    ##
]
