from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .session_handle import _Session
import logging

logger = logging.getLogger(__name__)

current_user: User = None
current_client: Client = None
session = _Session.empty(  )
_DEBUG = False


##
def dummy(req, msg='DUMMY'):
    print(f"dummy called with msg={msg}")
    logger.debug(f"dummy view accessed with msg={msg}")
    return render( req, 'main/t2.html' )


def template2_test(req):
    print("template2_test called")
    logger.info("template2_test view accessed")
    return render(req, 'temp/test.html' )

def not_logged_client(req):
    print("not_logged_client called")
    logger.warning("not_logged_client accessed")
    return HttpResponse('Debe haber iniciado sesion')
##

##STATIC

def  blog_view(req):
    print("blog_view called")
    logger.info("blog_view accessed")
    return render( req, 'static_tmp/blog.html', {**session.get_context()} )

@csrf_exempt
def get_pets(req):
    print("get_pets called")
    logger.info("get_pets accessed")
    return JsonResponse( {idx:pet.json() for idx, pet in enumerate(Pet.objects.filter(  ))}, safe=False )

def get_model_or_none( T: models.Model ,**kwargs ):
    print(f"get_model_or_none called for {T} with {kwargs}")
    logger.debug(f"get_model_or_none: {T}, {kwargs}")
    try:
        found = T.objects.get( **kwargs )
    except T.DoesNotExist as e:
        found = None
        if _DEBUG:
            print("Exception in get_model_or_none")
            logger.error("Exception in get_model_or_none", exc_info=True)
            raise e
    return found  

def user_login( email, password ):
    print(f"user_login called with email={email}")
    logger.info(f"user_login attempt for {email}")
    global current_client, current_user
    user: User = get_model_or_none( User, email=email)
    if not user:
        print("user not found")
        logger.warning("user_login: user not found")
    if not user or not user.check_password( password ):
        print("user_login failed password check")
        logger.warning("user_login: password check failed")
        return None, None
    if user:
        print(f"user found: {user}")
        logger.info(f"user_login: user found {user}")
        if user.type == USER_TYPE.CLIENT:
            sub_user = get_model_or_none( Client, user = user )
        elif user.type == USER_TYPE.DOCTOR:
            sub_user = get_model_or_none( Doctor, user = user )
        elif user.type == USER_TYPE.RECEPTIONIST:
            sub_user = None
        print(f"Setting session for user {user} and sub_user {sub_user}")
        logger.debug(f"Setting session for user {user.pk} and sub_user {getattr(sub_user, 'pk', None)}")
        session.set( user, sub_user )
        current_user = session.user
        current_client = session.sub_user
    return user, sub_user


def login_user(req: HttpRequest):
    print("login_user called")
    logger.info("login_user accessed")
    f1, f2  = user_login( req.POST['email'], req.POST['password'] )
    if session.is_client_logged():
        print("redirecting to main (client)")
        return redirect( main )
    elif session.is_doctor_logged():
        print("redirecting to doctor_main_view")
        return redirect( doctor_main_view )
    else:
        print("redirecting to register_view")
        return redirect( register_view ) 

@csrf_exempt
def login_client(req: HttpRequest):
    print("login_client called")
    logger.info("login_client accessed")
    user_login( req.POST['email'], req.POST['password'] )
    if session.is_logged():
        print("login_client: session is logged, redirecting to main")
        return redirect( main )
    else:
        print("login_client: session not logged, redirecting to register_view")
        return redirect( register_view )

    # print(req.POST)
    # email = req.POST['email']
    # password = req.POST['password']

    # users = User.objects.filter( email=email, password=password)
    # if users.exists():
    #     current_user = users.first()

    #     current_client = Client.objects.filter(user=current_user).first()
        
    #     return redirect(main)
    # else:
    #     return redirect(login_view)


def login_view(req:HttpRequest):
    return render(req, 'auth/auth.html', session.get_context())

def logout_post(req):
    print("logout_post called")
    logger.info("logout_post accessed")
    global current_user, current_client
    current_client = None
    current_user = None

    session.log_out()
    print("session logged out")
    logger.info("session logged out")
    return redirect( main )

def register_view(req: HttpRequest):
    print("register_view called")
    logger.info("register_view accessed")
    return render( req, 'login/register.html' )

def main(req: HttpRequest):
    print("main called")
    logger.info("main view accessed")
    return render(req, 'home/index.html', session.get_context())

@csrf_exempt
def register_client(req: HttpRequest):
    print("register_client called")
    logger.info("register_client accessed")
    name = req.POST['name']
    email = req.POST['email']
    contact_number = req.POST['contact_number']
    password= req.POST['password']

    try:
        _user = User.objects.get( email=email )
        print("User already exists, redirecting to login_view")
        logger.warning("register_client: user already exists")
        return redirect( login_view )
    except User.DoesNotExist:
        print("User does not exist, creating new user")
        logger.info("register_client: creating new user")

        type = USER_TYPE.CLIENT
        
        user = User(name=name, email=email, contact_number=contact_number, password=password, type=type)
        user.save()
        
        client = Client(user=user)
        client.save()

        print("New client registered")
        logger.info("New client registered")
        return redirect(  login_view )

##CLIENT

def new_appointment_view(req: HttpRequest):
    print("new_appointment_view called")
    logger.info("new_appointment_view accessed")
    if not session.is_client_logged_prop:
        print("User not logged as client, redirecting to login_view")
        return redirect( login_view )
    client_pets = Pet.objects.filter( client = session.sub_user )
    if not client_pets.exists():
        print("No pets found for client, redirecting to insert_pet_view")
        return redirect( insert_pet_view )
    print(f"Rendering new_appointment_view for client {session.sub_user.pk}")
    return render(req, 'client/appointments/new_appointment.html', {**session.get_context(), 
                                                                    'doctors': Doctor.objects.all(),
                                                                    'pets': client_pets})


def new_appointment_post(req: HttpRequest):
    print("new_appointment_post called")
    logger.info("new_appointment_post accessed")
    if session.is_client_logged():
        date = req.POST['datetime']
        pk = req.POST['doc_pk']
        pet_pk = req.POST['pet_pk']
        print(f"Creating appointment for doctor {pk} and pet {pet_pk} at {date}")
        doctor = Doctor.objects.get( pk = pk )
        pet = Pet.objects.get( pk = pet_pk )
        date = datetime.fromisoformat( date )
        client_details = req.POST['client_details']
        appointment = Appointment(datetime=date, pet = pet, client=current_client, doctor=doctor,
                                  client_details=client_details)
        appointment.save( )
        print("Appointment saved")
        logger.info("Appointment saved")
        return redirect( all_appointments_view )
    else:
        print("User not logged as client, redirecting to login_view")
        return redirect( login_view )

def all_appointments_view(req:HttpRequest):
    print("all_appointments_view called")
    logger.info("all_appointments_view accessed")
    if session.is_client_logged():
        appointments = Appointment.objects.filter( client = session.sub_user )
        print(f"Found {appointments.count()} appointments for client")
        return render( req, 'client/appointments/all_appointments.html', 
                      {**session.get_context(),
                          'appointments': 
                       [(appo.fmtdate, appo) for appo in  appointments]} )
    else:
        print("User not logged as client, redirecting to login_view")
        return redirect( login_view )
    

def delete_appointment(req: HttpRequest, pk):
    print(f"delete_appointment called for pk={pk}")
    logger.info(f"delete_appointment accessed for pk={pk}")
    appointment = Appointment.objects.get( pk = pk )
    appointment.delete()
    print("Appointment deleted")
    logger.info("Appointment deleted")
    if session.is_client_logged_prop:
        return redirect( all_appointments_view )
    else:
        return redirect( doctor_appointments_view )

def edit_appointment_view(req, pk):
    if not session.is_client_logged_prop:
        return redirect( login_view )
    
    appointment = get_model_or_none( Appointment, pk = pk, client = session.sub_user )
    client_pets = Pet.objects.filter( client = session.sub_user )
    if not appointment:
        return redirect( all_appointments_view )
    
    return render( req, 'client/appointments/edit_appointment.html', {
        **session.get_context(),
        'appointment': appointment,
        'doctors': Doctor.objects.all(),
        'pets': client_pets
    } )

def edit_appointment_post(req:HttpRequest):
    print("edit_appointment_post called")
    logger.info("edit_appointment_post accessed")
    if session.is_client_logged():
        date = req.POST['datetime']
        pk = req.POST['doc_pk']
        pet_pk = req.POST['pet_pk']
        print(f"Editing appointment for doctor {pk} and pet {pet_pk} at {date}")
        doctor = Doctor.objects.get( pk = pk )
        pet = Pet.objects.get( pk = pet_pk )
        date = datetime.fromisoformat( date )
        client_details = req.POST['client_details']
        appo_pk = req.POST['appo_pk']
        appointment: Appointment = get_model_or_none( Appointment, pk = appo_pk )

        appointment.doctor = doctor
        appointment.pet = pet 
        appointment.client_details = client_details
        appointment.datetime = date 

        appointment.save( )
        print("Appointment updated")
        logger.info("Appointment updated")
        return redirect( all_appointments_view )
    else:
        print("User not logged as client, redirecting to login_view")
        return redirect( login_view ) 

##
def client_main_view(req:HttpRequest):
    if session.is_logged():
        return render(req, 'client/profile.html', { **session.get_context() })
    else:
        return redirect( login_view )

def delete_client(req: HttpRequest):
    global current_user, current_client
    if not session.is_logged() or req.method != 'POST':
        return redirect( login_view )
    
    pk = int(req.POST['pk'])
    if session.user.pk != pk:
        return redirect( client_main_view )
    
    session.user.delete()
    current_client = None
    current_user = None
    session.log_out(  )

    return redirect( login_view )

def edit_client(req: HttpRequest):
    pk = int(req.POST['pk'])
    if session.user.pk != pk:
        return redirect( login_view )
    if 'email' in req.POST:
        try:
            found = User.objects.get( email = req.POST['email'] )
            if found.pk != session.user.pk:
                return redirect( client_main_view )
        except User.DoesNotExist:
            pass
        
    user = session.user
    for K, V in req.POST.items():
        if K != 'pk':
            setattr( user, K, V )
    user.save()
    return redirect( client_main_view )
##


##PETS
def insert_pet_view(req: HttpRequest):
    return render(req, 'pet/insert_pet.html', {**session.get_context()})

def all_pets_view(req: HttpRequest):
    if not session.is_logged():
        return redirect( login_view )
    client_pets = Pet.objects.filter( client = session.sub_user )
    return render( req, 'pet/all_pets.html', {**session.get_context(), 'pets': client_pets} )


@csrf_exempt
def insert_pet_post(req:HttpRequest):
    print("insert_pet_post called")
    logger.info("insert_pet_post accessed")
    if req.method != 'POST':
        print("Invalid method for insert_pet_post")
        logger.warning("insert_pet_post: invalid method")
        return HttpResponse('asd')
    
    cpk = int(req.POST['pk'])
    name = req.POST['name']
    age = int( req.POST['age'] )
    breed = req.POST['breed']

    print(f"Inserting pet: {name}, age: {age}, breed: {breed}, client pk: {cpk}")
    logger.debug(f"Inserting pet: {name}, age: {age}, breed: {breed}, client pk: {cpk}")

    if not session.is_client_logged():
        print("User not logged as client, redirecting to login_view")
        return redirect( login_view )
    
    elif (cpk != session.user.pk):
        print( f'{cpk  }')
        print( f'{ session.user.pk }' )
        print( f'{ session.user.pk == cpk }' )
        print( f'{ type(session.user.pk)   }' )
        logger.warning("insert_pet_post: client pk mismatch")
        return redirect( login_view )
    else:
        pet = Pet(name = name, age = age, breed = breed, client = session.sub_user)
        pet.save()
        print("Pet saved")
        logger.info("Pet saved")
        return redirect( all_pets_view )
    

def edit_pet_view(req: HttpRequest, pk: int):
    if not session.is_logged():
        return redirect( login_view )
    pet = Pet.objects.get( pk = pk )
    return render( req, 'pet/pet.html', {**session.get_context(), 'pet':pet, 
                                         'allergies': PetAllergy.objects.filter(pet = pet),
                                         'appointments': Appointment.objects.filter( pet = pet ),
                                         'vaccines': PetVaccine.objects.filter( pet = pet )})

def delete_pet_post(req: HttpRequest, pk: int):
    print(f"delete_pet_post called for pk={pk}")
    logger.info(f"delete_pet_post accessed for pk={pk}")
    if req.method != 'POST':
        print("Invalid method for delete_pet_post")
        logger.warning("delete_pet_post: invalid method")
        return redirect( dummy, msg='INVALID URL' )
    pet = Pet.objects.get( pk=pk )
    pet.delete()
    print("Pet deleted")
    logger.info("Pet deleted")
    return redirect( all_pets_view )

def insert_allergy_post(req: HttpRequest):
    print("insert_allergy_post called")
    logger.info("insert_allergy_post accessed")
    name = req.POST['name']
    description = req.POST['description']
    pk = int( req.POST['pk'] )
    pet = Pet.objects.get( pk= pk )
    allergy = PetAllergy( name = name, description = description, pet = pet )
    allergy.save()
    print("Allergy saved")
    logger.info("Allergy saved")
    return redirect( edit_pet_view, pk=pk )

def delete_allergy_post(req: HttpRequest):
    print("delete_allergy_post called")
    logger.info("delete_allergy_post accessed")
    pk = int( req.POST['pk'] )
    mk = int( req.POST['mpk'] )
    allergy = PetAllergy.objects.get(pk=pk)
    allergy.delete()
    print("Allergy deleted")
    logger.info("Allergy deleted")
    return redirect( edit_pet_view, pk=mk )
 ######


 ## DOCTOR
def doctor_pet_search(req):
    print("doctor_pet_search called")
    logger.info("doctor_pet_search accessed")
    if req.method == 'POST':
        pname = req.POST['name']
        print(f"Searching for pet with name: {pname}")
        pets = Pet.objects.filter( name = pname )
    else:
        pets = None
    return render( req, 'temp/doctor/pet/doctor_pet_search.html', {**session.get_context(), 'pets': pets} )

def doctor_main_view(req: HttpRequest):
    print("doctor_main_view called")
    logger.info("doctor_main_view accessed")
    return redirect( main )

def doctor_appointments_view(req: HttpRequest):
    print("doctor_appointments_view called")
    logger.info("doctor_appointments_view accessed")
    if not session.is_doctor_logged_prop:
        print("User not logged as doctor, redirecting to login_view")
        return redirect( login_view )
    
    appointments = Appointment.objects.filter( doctor = session.sub_user )
    print(f"Found {appointments.count()} appointments for doctor")
    return render(req, 'temp/doctor/doctor_appointments.html', {  **session.get_context(), 'appointments': 
                       [(appo.datetime.strftime("%d/%m/%Y, %H:%M:%S"), appo) for appo in  appointments] } )
    
def doctor_appointment_view(req: HttpRequest):
    print("doctor_appointment_view called")
    logger.info("doctor_appointment_view accessed")
    if not session.is_doctor_logged_prop:
        print("User not logged as doctor, redirecting to login_view")
        return redirect( login_view )
    appo_pk = req.POST['appo_pk']
    appointment = get_model_or_none( Appointment, doctor = session.sub_user, pk = appo_pk )
    print(f"Viewing appointment {appo_pk}")
    return render( req, 'temp/doctor/doctor_appointment_view.html', {**session.get_context(), 'appointment': appointment} )

def doctor_end_appointment_post(req: HttpRequest):
    print("doctor_end_appointment_post called")
    logger.info("doctor_end_appointment_post accessed")
    if not session.is_doctor_logged():
        print("User not logged as doctor, redirecting to login_view")
        return redirect( login_view )

    appo_pk = req.POST['appo_pk']
    appointment: Appointment = get_model_or_none( Appointment, pk = appo_pk, doctor = session.sub_user )
    if not appointment:
        print("Appointment not found, redirecting to doctor_appointments_view")
        return redirect( doctor_appointments_view )
    
    appointment.status = APPOINTMENT_STATUS.INACTIVE
    appointment.doctor_details = req.POST['details']
    print(f'Appointment ended with details: {req.POST["details"]}')
    logger.info(f'Appointment ended with details: {req.POST["details"]}')

    appointment.save()
    print("Appointment status updated to INACTIVE")
    logger.info("Appointment status updated to INACTIVE")

    return redirect( doctor_appointments_view )


def doctor_pet_view(req, pk: int):
    if not session.is_doctor_logged_prop:
        return redirect( login_view )
    pet = get_model_or_none( Pet, pk = pk )
    if not pet:
        return redirect( doctor_appointments_view )
    
    return render( req, 'temp/doctor/pet/doctor_pet_view.html', 
                  {**session.get_context(), 'pet': pet,
                   'vaccines': PetVaccine.objects.filter( pet = pet ),
                   'allergies': PetAllergy.objects.filter( pet = pet ),
                   'appointments': Appointment.objects.filter( pet = pet ),
                   'avl_vaccines': Vaccine.objects.all()} )

def insert_pet_vaccine_post(req):
    print("insert_pet_vaccine_post called")
    logger.info("insert_pet_vaccine_post accessed")
    pet_pk = int( req.POST['pet_pk'] )
    vaccine_pk = int( req.POST['vaccine_pk'] )
    dosis = req.POST['dosis'] 

    pet = get_model_or_none( Pet, pk = pet_pk )
    vaccine = get_model_or_none( Vaccine, pk = vaccine_pk )

    if (not pet) or (not vaccine):
        print("Pet or vaccine not found, redirecting to doctor_appointments_view")
        logger.warning("insert_pet_vaccine_post: pet or vaccine not found")
        return redirect( doctor_appointments_view ) 

    date = datetime.fromisoformat(req.POST['date'])
    dosis = int( dosis )

    pet_vaccine = PetVaccine( pet = pet, vaccine = vaccine, date = date, dosis = dosis )
    pet_vaccine.save(  )
    print("Pet vaccine saved")
    logger.info("Pet vaccine saved")
    return redirect( doctor_pet_view, pk = pet_pk )

##DOCTORS - IND
def all_doctors_view(req: HttpRequest):
    return render( req, 'doctor/all_doctors.html', {**session.get_context(), 'doctors': Doctor.objects.all()} )

##