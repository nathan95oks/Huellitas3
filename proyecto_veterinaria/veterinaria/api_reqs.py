from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
current_user: User = None
current_client: Client = None
INVALID = JsonResponse({'res': 'INVALID'})
OK = JsonResponse( {'res': 'OK'} )
DUMMY = JsonResponse({'res': 'NOT IMPLEMENTED'})
def is_it_of( current: models.Model, target: models.Model, key: 'str' ):
    try:
        found = current.objects.get( **{key: target} )
        return found 
    except current.DoesNotExist:
        return None  

##
def dummy(req):
    return DUMMY


def not_logged_client(req):
    return HttpResponse('Debe haber iniciado sesion')
##
def is_already_registered( email ):
    matches = User.objects.filter( email=email )
    return len(matches) > 0
    
## USERS GENERAL
def get_users_api(req):
    return JsonResponse( [ user.json() for user in User.objects.all() ], safe=False )

@csrf_exempt
def delete_user_api(req: HttpRequest):
    if req.method != 'POST':
        return INVALID
    pk = req.POST['pk']
    try:
        user = User.objects.get( pk = pk )
        user.delete()
        return OK
    except User.DoesNotExist:
        return INVALID

##

@csrf_exempt
def login_client_api(req: HttpRequest):
    global current_user, current_client
    email = req.POST['email']
    password = req.POST['password']

    users = User.objects.filter( email=email, password=password)
    if users.exists():
        current_user = users.first()
        current_client = Client.objects.filter(user=current_user).first()
        return OK
    else:
        return INVALID

@csrf_exempt
def register_client_api(req: HttpRequest):
    name = req.POST['name']
    email = req.POST['email']
    contact_number = req.POST['contact_number']
    password= req.POST['password']

    if is_already_registered(email):
        return INVALID
    
    user = User(name=name, email=email, contact_number=contact_number, password=password, type=USER_TYPE.CLIENT)
    user.save()
    
    client = Client(user=user)
    client.save()

    return OK



##DOCTOR
@csrf_exempt
def register_doctor_api(req: HttpRequest):
    if req.method=='GET':
        return INVALID
    
    name = req.POST['name']
    email = req.POST['email']
    contact_number = req.POST['contact_number']
    password= req.POST['password']
    
    if is_already_registered( email ):
        return INVALID

    user = User(name=name, email=email, contact_number=contact_number, password=password, type=USER_TYPE.DOCTOR)
    user.save()
    
    doctor = Doctor(user=user)
    doctor.save()

    return OK

@csrf_exempt
def get_doctors_api(req):
    return JsonResponse( [doctor.json() for doctor in Doctor.objects.all()], safe=False  )


##CLIENT
def get_clients_api(req):
    return JsonResponse( [client.json() for client in Client.objects.all()], safe=False )

@csrf_exempt
def delete_client_api(req, pk):
    print(f'{pk = }')
    if req.method == 'POST':
        user =  User.objects.get( pk = pk, type=USER_TYPE.CLIENT )
        user.delete()
        return OK
    else:
        return INVALID 


@csrf_exempt
def insert_appointment_api(req: HttpRequest):
    if current_user and current_user.type == USER_TYPE.CLIENT:
        date = req.POST['datetime']
        doctor = None
        if 'doc_pk' in req.POST:
            pk = req.POST['doc_pk']
            try:
                doc_user = User.objects.get( pk = pk )
                doctor = Doctor.objects.get( user = doc_user )
            except Doctor.DoesNotExist:
                print('does not exists')
                return INVALID

        date = datetime.fromisoformat( date )
        appointment = Appointment(datetime=date, client=current_client, doctor=doctor)
        appointment.save( )
        return OK
    else:
        return INVALID

def get_appointments_api(req:HttpRequest):
    if current_user and current_user.type == USER_TYPE.CLIENT:
        appointments = Appointment.objects.filter( client = current_client )
        return JsonResponse( [ a.json() for a in appointments ], safe=False )
    else:
        return INVALID
    
@csrf_exempt
def delete_appointment_api(req: HttpRequest, pk):
    if  current_user:
        try:
            appointment = Appointment.objects.get( pk = pk, client = current_client )
            appointment.delete()
            return OK
        except Appointment.DoesNotExist:
            return INVALID
    else:
        return INVALID
    


## PETS
@csrf_exempt
def get_pets_api(req):
    if not current_client or req.method!='GET':
        return INVALID
    return JsonResponse( [pet.json() for pet in (Pet.objects.filter( client=current_client  ))], safe=False )

@csrf_exempt
def delete_pet_api(req: HttpRequest, pk):
    if not current_client or req.method != 'POST':
        return INVALID
    pet = Pet.objects.get( pk=pk, client=current_client )
    pet.delete()
    return OK
@csrf_exempt
def edit_user(req: HttpRequest):
    pk = req.POST['pk']
    user = User.objects.get( pk = pk )
    for K, V in req.POST.items():
        if K != 'PK':
            setattr( user, K, V )
    user.save()
    return OK

@csrf_exempt
def edit_pet_base_api(req: HttpRequest, pk):
    if not current_user and req.method != 'POST':
        return INVALID
    try:
        pet = Pet.objects.get( pk = pk, client = current_client ) 
        for key, val in req.POST.items():
            if key == 'pk':
                continue
            setattr( pet, key, val )
        pet.save()
        return OK
    except Pet.DoesNotExist:
        return INVALID 

@csrf_exempt
def insert_pet_api(req: HttpRequest):
    if not current_user or req.method != 'POST':
        return INVALID

    name = req.POST['name']
    age = int( req.POST['age'] )
    breed = req.POST['breed']

    target_client = current_client
    if 'user_id' in req.POST:
        try:
            user = User.objects.get( pk = int(req.POST['user_id']) )
            target_client = Client.objects.get( user = user )
        except:
            return INVALID
        

    pet = Pet(name = name, age = age, breed = breed, client = target_client)
    pet.save()
    return OK

##PET.ALLERGY
def get_allergies_api(req: HttpResponse, pk: int):
    try:
        pet_target = Pet.objects.get( pk = pk )
        return JsonResponse( 
            [allergy.json() for allergy in PetAllergy.objects.filter( pet=pet_target )], safe=False
        )
    except Pet.DoesNotExist:
        return INVALID

@csrf_exempt
def insert_allergy_api(req: HttpRequest, pk):
    try:
        pet = Pet.objects.get( pk= pk )
        if pet.client.pk != current_client.pk:
            return INVALID
        
        name = req.POST['name']
        description = req.POST['description']
        allergy = PetAllergy( name = name, description = description, pet = pet )
        allergy.save()
        return OK
    except Pet.DoesNotExist:
        return INVALID
##
##
'''
##


##PETS

def all_pets_get_api(req: HttpRequest):
    if not current_user:
        return 
    client_pets = Pet.objects.filter( client=current_client )
    return render( req, 'pet/pets.html', {'pets': client_pets} )

@csrf_exempt
def new_pet_post(req:HttpRequest):
    name = req.POST['name']
    age = int( req.POST['age'] )
    breed = req.POST['breed']

    if not current_user and current_user.type != USER_TYPE.CLIENT:
        return HttpResponse('NO CURRENT USER LOGGED')
    else:
        pet = Pet(name = name, age = age, breed = breed, client = current_client)
        pet.save()
        return redirect( client_main_view )
    pass

def edit_pet_view(req: HttpRequest, pk: int):
    if not current_user:
        return redirect( login_view )
    pet = Pet.objects.get( pk = pk )
    return render( req, 'pet/edit_pet.html', {'pet':pet, 'allergies': PetAllergy.objects.filter(pet = pet)} )

def delete_pet_post(req: HttpRequest, pk: int):
    if req.method != 'POST':
        return redirect( dummy, msg='INVALID URL' )
    pet = Pet.objects.get( pk=pk )
    pet.delete()
    return redirect( all_pets_view )

def new_allergy_post(req: HttpRequest, pk):
    name = req.POST['name']
    description = req.POST['description']
    pet = Pet.objects.get( pk= pk )
    allergy = PetAllergy( name = name, description = description, pet = pet )
    allergy.save()
    return redirect( edit_pet_view, pk=pk )

def delete_allergy_post(req, pk, mk):
    allergy = PetAllergy.objects.get(pk=pk)
    allergy.delete()
    return redirect( edit_pet_view, pk=mk )
 

'''
##