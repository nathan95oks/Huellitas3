from django.contrib import admin
from .models import User, Client, Doctor, Appointment, Pet, Vaccine, PetVaccine
# Register your models here.

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Pet)
admin.site.register(Vaccine)
admin.site.register(PetVaccine)