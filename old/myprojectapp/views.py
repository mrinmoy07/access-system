# from django.shortcuts import render

# # Create your views here.

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Face
# import face_recognition

# @csrf_exempt
# def face_registration(request):
#     if request.method == 'POST':
#         userid = request.POST.get('userid')
#         image = request.FILES['image']
#         # Assuming only one face in the image for registration
#         face_encoding = face_recognition.face_encodings(face_recognition.load_image_file(image))[0]
#         face_obj, created = Face.objects.get_or_create(userid=userid)
#         face_obj.face_enc = face_encoding
#         face_obj.save()
#         return JsonResponse({'message': 'Face registered successfully'})
#     return JsonResponse({'error': 'Invalid request method'})

# @csrf_exempt
# def match_face(request):
#     if request.method == 'POST':
#         matched_userids = []
#         images = request.FILES.getlist('images')
#         for image in images:
#             face_encodings = face_recognition.face_encodings(face_recognition.load_image_file(image))
#             for face_encoding in face_encodings:
#                 matched_faces = Face.objects.filter(face_enc=face_encoding)
#                 matched_userids.extend([str(face.userid) for face in matched_faces])
#         return JsonResponse({'matched_userids': matched_userids})
#     return JsonResponse({'error': 'Invalid request method'})
import base64
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Face, User
# import face_recognition

# @csrf_exempt
# def face_registration(request):
#     if request.method == 'POST':
#         full_name = request.POST.get('full_name')
#         employee_id = request.POST.get('employee_id')
#         access = request.POST.get('access')
#         image = request.FILES['image']
        
#         # Create or get the User
#         user, created = User.objects.get_or_create(employee_id=employee_id, defaults={
#             'full_name': full_name,
#             'access': access
#         })
        
#         # Assuming only one face in the image for registration
#         face_encoding = face_recognition.face_encodings(face_recognition.load_image_file(image))[0]
        
#         # Create or update the Face object
#         face_obj, created = Face.objects.update_or_create(user=user, defaults={'face_enc': face_encoding})
        
#         return JsonResponse({'message': 'Face registered successfully'})
#     return JsonResponse({'error': 'Invalid request method'})

# @csrf_exempt
# def match_face(request):
#     if request.method == 'POST':
#         matched_users = []
#         images = request.FILES.getlist('images')
#         for image in images:
#             face_encodings = face_recognition.face_encodings(face_recognition.load_image_file(image))
#             for face_encoding in face_encodings:
#                 # Query faces by encoding and get associated user ids
#                 matched_faces = Face.objects.filter(face_enc=face_encoding)
#                 matched_users.extend([{"user_id":str(face.user_id),"full_name":str(face.user.full_name),"employee_id":str(face.user.employee_id),"access":str(face.user.access)} for face in matched_faces])
#         return JsonResponse({'matched_userids': matched_users})
#     return JsonResponse({'error': 'Invalid request method'})




# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Face, User, UserEntryExit
# import face_recognition
# from django.shortcuts import get_object_or_404
# from django.core.serializers import serialize

# import numpy as np
# import io
# from PIL import Image
# @csrf_exempt
# def face_registration(request):
#     if request.method == 'POST':
#         body=request.body#.get("iamge data") 
#         full_name = request.POST.get('full_name')
#         employee_id = request.POST.get('employee_id')
#         access = request.POST.get('access')
        
#         image = request.FILES['image']          
#         if not image:
#             return JsonResponse({'error': 'No image provided'}, status=400) 
#         with open(image.name, 'wb+') as destination:
#             for chunk in image.chunks():
#                 destination.write(chunk)        
 
#         user, created = User.objects.get_or_create(employee_id=employee_id, defaults={
#             'full_name': full_name,
#             'access': access
#         })
        
#         # Assuming only one face in the image for registration
#         face_encoding = face_recognition.face_encodings(face_recognition.load_image_file(image.name))[0]
        
#         face_obj, created = Face.objects.update_or_create(user=user, defaults={'face_enc': face_encoding})
        
#         return JsonResponse({'success':True,'message': 'Face registered successfully'})
#     return JsonResponse({'success':True,'error': 'Invalid request method'})

# @csrf_exempt
# def match_face(request):
#     if request.method == 'POST':
#         matched_users = []
#         images = request.FILES.getlist('images')
#         door = request.POST.get('door')
#         entryexit = request.POST.get('entryexit')
        
#         for image in images:
#             face_encodings = face_recognition.face_encodings(face_recognition.load_image_file(image))
#             for face_encoding in face_encodings:

#                 # Query faces by encoding and get associated user ids
#                 matched_faces = Face.objects.filter(face_enc=face_encoding)
#                 for face in matched_faces:
#                     user = face.user
#                     matched_users.append({
#                         'user_id': str(user.id),
#                         'employee_id': user.employee_id,
#                         'full_name': user.full_name
#                     })
#                     UserEntryExit.objects.create(user=user, door=door, entryexit=entryexit)
                    
#         return JsonResponse({'matched_users': matched_users})
#     return JsonResponse({'error': 'Invalid request method'}, status=405)

# @csrf_exempt
# def list_entries(request):
#     if request.method == 'GET':
#         entries = UserEntryExit.objects.all()
#         data = serialize('json', entries)
#         return JsonResponse(data, safe=False)
#     return JsonResponse({'error': 'Invalid request method'}, status=405)


# @csrf_exempt
# def search_entries(request):
#     if request.method == 'GET':
#         employee_id = request.GET.get('employee_id')
        
#         if not employee_id:
#             return JsonResponse({'error': 'Employee ID is required'}, status=400)
        
#         entries = UserEntryExit.objects.filter(user__employee_id=employee_id)
        
#         data = serialize('json', entries)
#         return JsonResponse(data, safe=False)
#     return JsonResponse({'error': 'Invalid request method'}, status=405)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myprojectapp.models import User, Face, UserEntryExit
import face_recognition
from scipy.spatial.distance import cosine
from django.shortcuts import get_object_or_404
from django.core.serializers import serialize

import numpy as np
import io
from PIL import Image
from django.shortcuts import render
from .models import Schedule, Attendance

import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@csrf_exempt
def face_registration(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        employee_id = request.POST.get('employee_id')
        access = request.POST.get('access')
        
        image = request.FILES['image']
        if not image:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        with open(image.name, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        user, created = User.objects.get_or_create(employee_id=employee_id, defaults={
            'full_name': full_name,
            'access': access
        })
        
        image_path = image.name
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if len(face_encodings) > 0:
            face_encoding = face_encodings[0]
            face_obj, created = Face.objects.update_or_create(user=user, defaults={'face_enc': json.dumps(face_encoding.tolist())})
            logger.info(f"Face registered for user: {user.full_name} with employee ID: {user.employee_id}")
            return JsonResponse({'success': True, 'message': 'Face registered successfully'})
        else:
            logger.warning("No face found in the image during registration.")
            return JsonResponse({'error': 'No face found in the image'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def match_face(request):
    if request.method == 'POST':
        matched_users = []
        images = request.FILES.getlist('images')
        door = request.POST.get('door')
        entryexit = request.POST.get('entryexit')
        
        for image in images:
            image_path = image.name
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            for face_encoding in face_encodings:
                for face in Face.objects.all():
                    known_face_encoding = json.loads(face.face_enc)
                    
                    distance = face_recognition.face_distance([known_face_encoding], face_encoding)[0]
                    logger.info(f"Face distance: {distance} for user: {face.user.full_name}")
                    if distance < 0.4:  # Adjusted threshold for stricter matching
                        user = face.user
                        matched_users.append({
                            'user_id': str(user.id),
                            'employee_id': user.employee_id,
                            'full_name': user.full_name,
                            'access':user.access,
                        })
                        UserEntryExit.objects.create(user=user, door=door, entryexit=entryexit)
        
        if not matched_users:
            logger.info("No matching faces found.")
            return JsonResponse({'error': 'user not found'}, status=200)
        
        return JsonResponse({'matched_users': matched_users})
    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def list_entries(request):
    if request.method == 'GET':
        entries = UserEntryExit.objects.all()
        data = serialize('json', entries)
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def search_entries(request):
    if request.method == 'GET':
        employee_id = request.GET.get('employee_id')
        
        if not employee_id:
            return JsonResponse({'error': 'Employee ID is required'}, status=400)
        
        entries = UserEntryExit.objects.filter(user__employee_id=employee_id)
        
        data = serialize('json', entries)
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=405)















def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

def face_list(request):
    faces = Face.objects.all()
    return render(request, 'face_list.html', {'faces': faces})

def user_entry_exit_list(request):
    entries = UserEntryExit.objects.all()
    return render(request, 'user_entry_exit_list.html', {'entries': entries})





def schedule_list(request):
    schedules = Schedule.objects.all()
    return render(request, 'schedule_list.html', {'schedules': schedules})

def attendance_list(request):
    attendances = Attendance.objects.all()
    return render(request, 'attendance_list.html', {'attendances': attendances})
