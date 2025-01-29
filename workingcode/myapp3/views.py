from .models import Attendance, User, Face, EmployeeShiftAssignment, Guest
from .models import Shift
from .models import User
from .models import User, Face  # Assuming User and Face models are defined
from django.views.decorators.csrf import csrf_protect
from .models import User  # Ensure correct model import
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from .models import Guest
from .models import EmployeeShiftAssignment, Shift, User
from django.shortcuts import get_object_or_404
from .models import Face, User
from myapp3.models import User
#import cv2
import logging
import time
from concurrent.futures import ThreadPoolExecutor
import pytz
from PIL import Image, ExifTags
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from datetime import timedelta
from io import BytesIO
from PIL import Image, ImageEnhance, ImageOps
import calendar
import numpy as np
from django.views import View
from datetime import timedelta, datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.http import JsonResponse
from .models import User, Organization, Department
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from .models import Holiday
from django.utils import timezone
from datetime import datetime
from .models import Shift, EmployeeShiftAssignment
from rest_framework.response import Response
from rest_framework.views import APIView
import io
import face_recognition
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views.generic import TemplateView
from django.http import HttpResponse
import json

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class CreateOrganizationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_superuser:
            data = request.POST
            organization = Organization.objects.create(
                name=data['name'],
                address=data['address'],
                gst_no=data['gst_no'],
                no_of_employees=data['no_of_employees'],
                access_control=True if 'access_control' in data.keys(
                ) and data['access_control'] == "true" else False
            )
            return Response({"success": f"Organization '{organization.name}' created successfully."})
        return Response({"error": "Unauthorized: Only superusers can create organizations."})


class CreateOrganizationTemplateView(TemplateView):  # updating
    template_name = 'organization.html'

    def post(self, request):
        if request.user.is_superuser:
            data = request.POST
            organization = Organization.objects.create(
                name=data['name'],
                address=data['address'],
                gst_no=data['gst_no'],
                no_of_employees=data['no_of_employees'],
                access_control=True if 'access_control' in data.keys(
                ) and data['access_control'] == "true" else False
            )
            return HttpResponse(f"Organization '{organization.name}' created successfully.")
        return HttpResponse("Unauthorized: Only superusers can create organizations.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization  # Pass the model to access NAME_CHOICES
        return context


# class ListOrganizationView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         organizations = Organization.objects.all()
#         organization_data = [
#             {
#                 "id": organization.id,
#                 "name": organization.name,
#                 "address": organization.address,
#                 "gst_no": organization.gst_no,
#                 "no_of_employees": organization.no_of_employees,
#                 "access_control": organization.access_control
#             }
#             for organization in organizations
#         ]
#         return Response(organization_data)

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ListOrganizationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        # Get query parameters
        search_query = request.query_params.get('search', '')
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        # Get organizations and apply search if provided
        organizations = Organization.objects.all()
        if search_query:
            organizations = organizations.filter(name__icontains=search_query)

        # Apply pagination
        paginator = Paginator(organizations, page_size)
        current_page = paginator.get_page(page)

        # Format organization data
        organization_data = [
            {
                "id": organization.id,
                "name": organization.name,
                "address": organization.address,
                "gst_no": organization.gst_no,
                "no_of_employees": organization.no_of_employees,
                "access_control": organization.access_control
            }
            for organization in current_page
        ]

        response_data = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page),
            'results': organization_data
        }

        return Response(response_data)
class ListOrganizationTemplateView(TemplateView):  # updating
    template_name = 'organizations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizations'] = Organization.objects.all()
        return context





##For deleting org
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
from .models import Organization
class DeleteOrganizationTemplateView(View):
    @method_decorator(login_required)
    def post(self, request, organization_id):
        if request.user.is_superuser:
            organization = get_object_or_404(Organization, id=organization_id)
            organization_name = organization.name
            organization.delete()
            return HttpResponse(f"Organization '{organization_name}' deleted successfully.")
        return HttpResponse("Unauthorized: Only superusers can delete organizations.", status=403)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Organization

# Edit Organization API (only accessible by superadmins)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_organization(request, organization_id):
    if request.user.role != 'superadmin':
        return Response({"error": "Unauthorized: Only superadmins can edit organizations."}, status=status.HTTP_403_FORBIDDEN)

    try:
        organization = Organization.objects.get(id=organization_id)
    except Organization.DoesNotExist:
        return Response({"error": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data  # Expecting data in JSON format
    organization.name = data.get('name', organization.name)
    organization.address = data.get('address', organization.address)
    organization.gst_no = data.get('gst_no', organization.gst_no)
    organization.no_of_employees = data.get('no_of_employees', organization.no_of_employees)
    organization.access_control = data.get('access_control', organization.access_control)

    organization.save()
    return Response({"success": f"Organization '{organization.name}' updated successfully."}, status=status.HTTP_200_OK)


# Delete Organization API (only accessible by superadmins)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_organization(request, organization_id):
    if request.user.role != 'superadmin':
        return Response({"error": "Unauthorized: Only superadmins can delete organizations."}, status=status.HTTP_403_FORBIDDEN)

    try:
        organization = Organization.objects.get(id=organization_id)
    except Organization.DoesNotExist:
        return Response({"error": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

    organization.delete()
    return Response({"success": f"Organization '{organization.name}' deleted successfully."}, status=status.HTTP_200_OK)


#####Edit Organization 

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import Organization

# class EditOrganizationTemplateView(TemplateView):
#     template_name = 'edit_organization.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         organization_id = self.kwargs['organization_id']
#         context['organization'] = get_object_or_404(Organization, id=organization_id)
#         return context

#     def post(self, request, organization_id):
#         if request.user.is_superuser:
#             data = request.POST
#             organization = get_object_or_404(Organization, id=organization_id)
#             organization.name = data['name']
#             organization.address = data['address']
#             organization.gst_no = data['gst_no']
#             organization.no_of_employees = data['no_of_employees']
#             organization.access_control = True if 'access_control' in data.keys() and data['access_control'] == "true" else False
#             organization.save()
#             return HttpResponse(f"Organization '{organization.name}' updated successfully.")
#         return HttpResponse("Unauthorized: Only superusers can edit organizations.")
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import Organization

class EditOrganizationTemplateView(View):
    @method_decorator(login_required)
    def get(self, request, organization_id):
        if request.user.is_superuser:
            # Fetch the organization object based on the organization_id
            organization = get_object_or_404(Organization, id=organization_id)
            context = {
                'organization': organization,
                'name_choices': Organization.NAME_CHOICES,  # Pass NAME_CHOICES for the dropdown
            }
            return render(request, 'edit_organization.html', context)
        return HttpResponse("Unauthorized: Only superusers can edit organizations.", status=403)

    @method_decorator(login_required)
    def post(self, request, organization_id):
        if request.user.is_superuser:
            # Fetch the organization object based on the organization_id
            organization = get_object_or_404(Organization, id=organization_id)
            data = request.POST
            
            # Update the organization object with the new values
            organization.name = data['name']
            organization.address = data['address']
            organization.gst_no = data['gst_no']
            organization.no_of_employees = data['no_of_employees']
            
            # Handle the checkbox for access_control
            organization.access_control = 'access_control' in data

            # Save the updated organization object
            organization.save()
            
            # Display a success message
            messages.success(request, f"Organization '{organization.name}' updated successfully.")
            
            # Redirect to the list of organizations page
            return HttpResponseRedirect(reverse('list_organizations_template'))
        
        # Return an error response if the user is not a superuser
        return HttpResponse("Unauthorized: Only superusers can edit organizations.", status=403)





class CreateDepartmentView(APIView):
    # Ensure the user is authenticated and a superuser
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Manually extract and validate the incoming data
        name = request.POST.get('name')
        organization_id = request.POST.get('organization')
        integrate_with_ai_camera = request.POST.get(
            'integrate_with_ai_camera') == 'true'

        # Basic validation
        if not name:
            return Response({"error": "The name field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not organization_id:
            return Response({"error": "The organization field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({"error": "Organization does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the department
        department = Department.objects.create(
            name=name,
            organization=organization,
            integrate_with_ai_camera=integrate_with_ai_camera
        )

        return Response({"success": f"Department '{department.name}' created successfully."}, status=status.HTTP_201_CREATED)


class CreateDepartmentTemplateView(TemplateView):  # updating
    template_name = 'department.html'

    def post(self, request):
        # Manually extract and validate the incoming data
        name = request.POST.get('name')
        organization_id = request.POST.get('organization')
        integrate_with_ai_camera = request.POST.get(
            'integrate_with_ai_camera') == 'true'

        # Basic validation
        if not name:
            return HttpResponse("error: The name field is required.", status=status.HTTP_400_BAD_REQUEST)

        if not organization_id:
            return HttpResponse("error: The organization field is required.", status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return HttpResponse("error: Organization does not exist.", status=status.HTTP_400_BAD_REQUEST)

        # Create the department
        department = Department.objects.create(
            name=name,
            organization=organization,
            integrate_with_ai_camera=integrate_with_ai_camera
        )

        return HttpResponse(f"success: Department '{department.name}' created successfully.", status=status.HTTP_201_CREATED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizations'] = Organization.objects.all()
        return context


# class ListDepartmentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         departments = Department.objects.all()
#         department_data = [
#             {
#                 "id": department.id,
#                 "name": department.name,
#                 "organization": department.organization.name,
#                 "integrate_with_ai_camera": department.integrate_with_ai_camera
#             }
#             for department in departments
#         ]
#         return Response(department_data)

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.db.models import Q

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ListDepartmentView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        # Get query parameters
        search_query = request.query_params.get('search', '')
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        # Get departments and apply search if provided
        departments = Department.objects.all()
        if search_query:
            departments = departments.filter(
                Q(name__icontains=search_query) |
                Q(organization__name__icontains=search_query)
            )

        # Apply pagination
        paginator = Paginator(departments, page_size)
        current_page = paginator.get_page(page)

        # Format department data
        department_data = [
            {
                "id": department.id,
                "name": department.name,
                "organization": department.organization.name,
                "integrate_with_ai_camera": department.integrate_with_ai_camera
            }
            for department in current_page
        ]

        response_data = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page),
            'results': department_data
        }

        return Response(response_data)
class ListDepartmentTemplateView(TemplateView):  # updating
    template_name = 'departments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        return context














from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Department, Organization

# Edit Department API (only accessible by superadmins)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_department(request, department_id):
    # Check if the user is a superadmin
    if request.user.role != 'superadmin':
        return Response({"error": "Unauthorized: Only superadmins can edit departments."}, status=status.HTTP_403_FORBIDDEN)

    try:
        department = Department.objects.get(id=department_id)
    except Department.DoesNotExist:
        return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get data from request body (expecting JSON data)
    data = request.data
    department.name = data.get('name', department.name)
    department.integrate_with_ai_camera = data.get('integrate_with_ai_camera', department.integrate_with_ai_camera)

    # Update organization if provided
    if 'organization' in data:
        try:
            organization = Organization.objects.get(id=data['organization'])
            department.organization = organization
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

    department.save()
    return Response({"success": f"Department '{department.name}' updated successfully."}, status=status.HTTP_200_OK)


# Delete Department API (only accessible by superadmins)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_department(request, department_id):
    # Check if the user is a superadmin
    if request.user.role != 'superadmin':
        return Response({"error": "Unauthorized: Only superadmins can delete departments."}, status=status.HTTP_403_FORBIDDEN)

    try:
        department = Department.objects.get(id=department_id)
    except Department.DoesNotExist:
        return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

    department.delete()
    return Response({"success": f"Department '{department.name}' deleted successfully."}, status=status.HTTP_200_OK)

######
#####Delete department

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Department

class DeleteDepartmentTemplateView(View):
    @method_decorator(login_required)
    def post(self, request, department_id):
        if request.user.is_superuser:
            department = get_object_or_404(Department, id=department_id)
            department_name = department.name
            department.delete()
            return HttpResponse(f"Department '{department_name}' deleted successfully.")
        return HttpResponse("Unauthorized: Only superusers can delete departments.", status=403)


#####Edit Department


from django.views.generic import TemplateView
from .models import Department
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Department
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib import messages
from myapp3.models import Department, Organization
class EditDepartmentTemplateView(View):
    @method_decorator(login_required)
    def get(self, request, department_id):
        if request.user.is_superuser:
            # Fetch the department and list of organizations
            department = get_object_or_404(Department, id=department_id)
            organizations = Organization.objects.all()  # Pass this for the dropdown
            context = {
                'department': department,
                'organizations': organizations,
            }
            return render(request, 'edit_department.html', context)
        return HttpResponse("Unauthorized: Only superusers can edit departments.", status=403)

    @method_decorator(login_required)
    def post(self, request, department_id):
        if request.user.is_superuser:
            # Fetch the department
            department = get_object_or_404(Department, id=department_id)
            data = request.POST

            # Update the department fields
            department.name = data['name']
            department.organization_id = data['organization']
            department.integrate_with_ai_camera = 'integrate_with_ai_camera' in data

            # Save the updated department
            department.save()

            # Show success message
            messages.success(request, f"Department '{department.name}' updated successfully.")
            return HttpResponseRedirect(reverse('list_departments_template'))
        
        return HttpResponse("Unauthorized: Only superusers can edit departments.", status=403)

#####Password validation

import re

def validate_password(password):
    # Check for uppercase letter, lowercase letter, and special character
    if (any(char.islower() for char in password) and
        any(char.isupper() for char in password) and
        any(char in "!@#$%^&*()_+" for char in password)):
        return True
    return False


# class CreateUserBySuperuser(APIView):
#     permission_classes = [IsAuthenticated]
#     allowed_roles = ["hr", "accounts"]

#     def post(self, request):
#         if request.user.is_superuser:
#             name = request.POST.get('name')
#             role = request.POST.get('role')
#             organization_id = request.POST.get('organization')
#             department_id = request.POST.get('department')
#             designation = request.POST.get('designation')
#             blood_group = request.POST.get('blood_group')
#             emergency_contact = request.POST.get('emergency_contact')
#             photo = request.FILES.get('photo')
#             # Get password from request
#             password = request.POST.get('password')

#             if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact, photo, password]):
#                 return Response({"error": "All fields, including photo and password, are required."}, status=status.HTTP_400_BAD_REQUEST)

#             if role not in self.allowed_roles:
#                 return Response({"error": f"Role '{role}' is not allowed. Superuser can only assign roles: {', '.join(self.allowed_roles)}."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 user = User.objects.create(
#                     name=name,
#                     role=role,
#                     organization_id=organization_id,
#                     department_id=department_id,
#                     designation=designation,
#                     blood_group=blood_group,
#                     emergency_contact=emergency_contact,
#                     photo=photo,
#                     created_by=request.user
#                 )
#                 user.set_password(password)  # Set password
#                 user.save()

#                 image = face_recognition.load_image_file(photo)
#                 encodings = face_recognition.face_encodings(image)

#                 if encodings:
#                     Face.objects.create(
#                         user=user, face_enc=encodings[0].tolist())

#                 return Response({"success": f"User '{user.name}' created successfully with employee code {user.employee_code}."}, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({"error": "Unauthorized: Only superusers can create users."}, status=status.HTTP_403_FORBIDDEN)


import re
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

def validate_password(password):
    # Check for at least one lowercase letter, one uppercase letter, and one special character
    if (any(char.islower() for char in password) and
        any(char.isupper() for char in password) and
        any(char in "!@#$%^&*()_+" for char in password) and
        len(password) >= 8):  # Password length should be at least 8 characters for better security
        return True
    return False

class CreateUserBySuperuser(APIView):
    permission_classes = [IsAuthenticated]
    allowed_roles = ["hr", "accounts"]

    def post(self, request):
        if request.user.is_superuser:
            name = request.POST.get('name')
            role = request.POST.get('role')
            organization_id = request.POST.get('organization')
            department_id = request.POST.get('department')
            designation = request.POST.get('designation')
            blood_group = request.POST.get('blood_group')
            emergency_contact = request.POST.get('emergency_contact')
            photo = request.FILES.get('photo')
            # Get password from request
            password = request.POST.get('password')

            if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact, photo, password]):
                return Response({"error": "All fields, including photo and password, are required."}, status=status.HTTP_400_BAD_REQUEST)

            if role not in self.allowed_roles:
                return Response({"error": f"Role '{role}' is not allowed. Superuser can only assign roles: {', '.join(self.allowed_roles)}."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate the password
            validation_error = validate_password(password)
            if validation_error:
                logging.error(f"Password validation error: {validation_error}")
                return HttpResponse(f"error: {validation_error}", status=status.HTTP_400_BAD_REQUEST)
            # if not validate_password(password):
            #     return Response({"error": "Password must contain at least one uppercase letter, one lowercase letter, one special character, and be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.create(
                    name=name,
                    role=role,
                    organization_id=organization_id,
                    department_id=department_id,
                    designation=designation,
                    blood_group=blood_group,
                    emergency_contact=emergency_contact,
                    photo=photo,
                    created_by=request.user
                )
                user.set_password(password)  # Set password
                user.save()

                image = face_recognition.load_image_file(photo)
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    Face.objects.create(
                        user=user, face_enc=encodings[0].tolist())

                return Response({"success": f"User '{user.name}' created successfully with employee code {user.employee_code}."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"error": "Unauthorized: Only superusers can create users."}, status=status.HTTP_403_FORBIDDEN)

# class CreateUserBySuperuserTemplate(TemplateView):  # updating
#     template_name = 'user.html'
#     allowed_roles = ["hr", "accounts"]

#     def post(self, request):
#         if request.user.is_superuser:
#             name = request.POST.get('name')
#             role = request.POST.get('role')
#             organization_id = request.POST.get('organization')
#             department_id = request.POST.get('department')
#             designation = request.POST.get('designation')
#             blood_group = request.POST.get('blood_group')
#             emergency_contact = request.POST.get('emergency_contact')
#             photo = request.FILES.get('photo')
#             # Get password from request
#             password = request.POST.get('password')

#             print(request.FILES)

#             if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact, photo, password]):
#                 return HttpResponse("error: All fields, including photo and password, are required.", status=status.HTTP_400_BAD_REQUEST)

#             if role not in self.allowed_roles:
#                 return HttpResponse(f"error: Role '{role}' is not allowed. Superuser can only assign roles: {', '.join(self.allowed_roles)}.", status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 user = User.objects.create(
#                     name=name,
#                     role=role,
#                     organization_id=organization_id,
#                     department_id=department_id,
#                     designation=designation,
#                     blood_group=blood_group,
#                     emergency_contact=emergency_contact,
#                     photo=photo,
#                     created_by=request.user
#                 )
#                 user.set_password(password)  # Set password
#                 user.save()

#                 image = face_recognition.load_image_file(photo)
#                 encodings = face_recognition.face_encodings(image)

#                 if encodings:
#                     Face.objects.create(
#                         user=user, face_enc=encodings[0].tolist())

#                 return HttpResponse(f"success: User '{user.name}' created successfully with employee code {user.employee_code}.", status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return HttpResponse("error: Unauthorized: Only superusers can create users.", status=status.HTTP_403_FORBIDDEN)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = None
#         context['roles'] = self.allowed_roles
#         context['organizations'] = Organization.objects.all()
#         context['departments'] = Department.objects.all()
#         context['users'] = User.objects.all()
#         return context



# class CreateUserBySuperuserTemplate(TemplateView):
#     template_name = 'user.html'
#     allowed_roles = ["hr", "accounts"]

#     def post(self, request):
#         if request.user.is_superuser:
#             name = request.POST.get('name')
#             role = request.POST.get('role')
#             organization_id = request.POST.get('organization')
#             department_id = request.POST.get('department')
#             designation = request.POST.get('designation')
#             blood_group = request.POST.get('blood_group')
#             emergency_contact = request.POST.get('emergency_contact')
#             photo = request.FILES.get('photo')
#             password = request.POST.get('password')

#             # Check if password is valid
#             if not validate_password(password):
#                 return HttpResponse("error: Password must contain at least one uppercase letter, one lowercase letter, and one special character.", status=status.HTTP_400_BAD_REQUEST)

#             if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact, photo, password]):
#                 return HttpResponse("error: All fields, including photo and password, are required.", status=status.HTTP_400_BAD_REQUEST)

#             if role not in self.allowed_roles:
#                 return HttpResponse(f"error: Role '{role}' is not allowed. Superuser can only assign roles: {', '.join(self.allowed_roles)}.", status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 user = User.objects.create(
#                     name=name,
#                     role=role,
#                     organization_id=organization_id,
#                     department_id=department_id,
#                     designation=designation,
#                     blood_group=blood_group,
#                     emergency_contact=emergency_contact,
#                     photo=photo,
#                     created_by=request.user
#                 )
#                 user.set_password(password)  # Set password
#                 user.save()

#                 image = face_recognition.load_image_file(photo)
#                 encodings = face_recognition.face_encodings(image)

#                 if encodings:
#                     Face.objects.create(
#                         user=user, face_enc=encodings[0].tolist())

#                 return HttpResponse(f"success: User '{user.name}' created successfully with employee code {user.employee_code}.", status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return HttpResponse("error: Unauthorized: Only superusers can create users.", status=status.HTTP_403_FORBIDDEN)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = None
#         context['roles'] = self.allowed_roles
#         context['organizations'] = Organization.objects.all()
#         context['departments'] = Department.objects.all()
#         context['users'] = User.objects.all()
#         return context

# import logging  # Import logging module


# class CreateUserBySuperuserTemplate(TemplateView):
#     template_name = 'user.html'
#     allowed_roles = ["hr", "accounts"]

#     def post(self, request):
#         if request.user.is_superuser:
#             name = request.POST.get('name')
#             role = request.POST.get('role')
#             organization_id = request.POST.get('organization')
#             department_id = request.POST.get('department')
#             designation = request.POST.get('designation')
#             blood_group = request.POST.get('blood_group')
#             emergency_contact = request.POST.get('emergency_contact')
#             photo = request.FILES.get('photo')
#             password = request.POST.get('password')

#             # Check if password is valid
#             if not validate_password(password):
#                 return HttpResponse("error: Password must contain at least one uppercase letter, one lowercase letter, and one special character.", status=status.HTTP_400_BAD_REQUEST)

#             if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact, photo, password]):
#                 return HttpResponse("error: All fields, including photo and password, are required.", status=status.HTTP_400_BAD_REQUEST)

#             if role not in self.allowed_roles:
#                 return HttpResponse(f"error: Role '{role}' is not allowed. Superuser can only assign roles: {', '.join(self.allowed_roles)}.", status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 user = User.objects.create(
#                     name=name,
#                     role=role,
#                     organization_id=organization_id,
#                     department_id=department_id,
#                     designation=designation,
#                     blood_group=blood_group,
#                     emergency_contact=emergency_contact,
#                     photo=photo,
#                     created_by=request.user
#                 )
#                 user.set_password(password)  # Set password
#                 user.save()

#                 image = face_recognition.load_image_file(photo)
#                 encodings = face_recognition.face_encodings(image)

#                 if encodings:
#                     # Print and log face encoding
#                     face_encoding = encodings[0].tolist()
#                     print(f"Face encoding for user {user.name}: {face_encoding}")
#                     logging.info(f"Face encoding for user {user.name}: {face_encoding}")

#                     Face.objects.create(user=user, face_enc=face_encoding)
#                 else:
#                     print(f"No face encoding found for user {user.name}.")
#                     logging.warning(f"No face encoding found for user {user.name}.")

#                 return HttpResponse(f"success: User '{user.name}' created successfully with employee code {user.employee_code}.", status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 print(f"Error while creating user {name}: {e}")
#                 logging.error(f"Error while creating user {name}: {e}")
#                 return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return HttpResponse("error: Unauthorized: Only superusers can create users.", status=status.HTTP_403_FORBIDDEN)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = None
#         context['roles'] = self.allowed_roles
#         context['organizations'] = Organization.objects.all()
#         context['departments'] = Department.objects.all()
#         context['users'] = User.objects.all()
#         return context


import logging  # Import logging module
def validate_password(password):
    logging.info(f"Validating password: '{password}'")
    
    if len(password) < 8:
        logging.warning("Password validation failed: Length check")
        return False
    if not any(char.islower() for char in password):
        logging.warning("Password validation failed: Lowercase check")
        return False
    if not any(char.isupper() for char in password):
        logging.warning("Password validation failed: Uppercase check")
        return False
    if not any(char in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/`~" for char in password):
        logging.warning("Password validation failed: Special character check")
        return False
    
    logging.info("Password validation passed")
    return True

class CreateUserBySuperuserTemplate(TemplateView):
    template_name = 'user.html'
    allowed_roles = ["hr", "accounts"]

    def post(self, request):
        if request.user.is_superuser:
            name = request.POST.get('name')
            role = request.POST.get('role')
            organization_id = request.POST.get('organization')
            department_id = request.POST.get('department')
            designation = request.POST.get('designation')
            blood_group = request.POST.get('blood_group')
            emergency_contact = request.POST.get('emergency_contact')
            photo = request.FILES.get('photo')
            password = request.POST.get('password', '').strip()  # Trim leading/trailing spaces

            # Log the password received
            logging.info(f"Received password: '{password}'")

            # Validate password
            # Validate password
            validation_error = validate_password(password)
            if validation_error:
                logging.error(f"Password validation error: {validation_error}")
                return HttpResponse(f"error: {validation_error}", status=status.HTTP_400_BAD_REQUEST)

            # if not validate_password(password):
            #     return HttpResponse(
            #         "error: Password must contain at least one uppercase letter, one lowercase letter, and one special character.",
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
            

            # Ensure all fields are filled
            if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact, photo, password]):
                return HttpResponse("error: All fields, including photo and password, are required.", status=status.HTTP_400_BAD_REQUEST)

            # Check if role is allowed
            if role not in self.allowed_roles:
                return HttpResponse(f"error: Role '{role}' is not allowed. Allowed roles: {', '.join(self.allowed_roles)}.", status=status.HTTP_400_BAD_REQUEST)

            try:
                # Create the user
                user = User.objects.create(
                    name=name,
                    role=role,
                    organization_id=organization_id,
                    department_id=department_id,
                    designation=designation,
                    blood_group=blood_group,
                    emergency_contact=emergency_contact,
                    photo=photo,
                    created_by=request.user
                )
                user.set_password(password)  # Set the password securely
                user.save()

                # Process face encoding
                image = face_recognition.load_image_file(photo)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    face_encoding = encodings[0].tolist()
                    logging.info(f"Face encoding for user {user.name}: {face_encoding}")
                    Face.objects.create(user=user, face_enc=face_encoding)
                else:
                    logging.warning(f"No face encoding found for user {user.name}.")

                return HttpResponse(f"success: User '{user.name}' created successfully with employee code {user.employee_code}.", status=status.HTTP_201_CREATED)
            except Exception as e:
                logging.error(f"Error while creating user {name}: {e}")
                return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return HttpResponse("error: Unauthorized: Only superusers can create users.", status=status.HTTP_403_FORBIDDEN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = None
        context['roles'] = self.allowed_roles
        context['organizations'] = Organization.objects.all()
        context['departments'] = Department.objects.all()
        context['users'] = User.objects.all()
        return context




# import logging  # Import logging module
# def validate_password(password):
#     logging.info(f"Validating password: '{password}'")
    
#     if len(password) < 8:
#         logging.warning("Password validation failed: Length check")
#         return False
#     if not any(char.islower() for char in password):
#         logging.warning("Password validation failed: Lowercase check")
#         return False
#     if not any(char.isupper() for char in password):
#         logging.warning("Password validation failed: Uppercase check")
#         return False
#     if not any(char in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/`~" for char in password):
#         logging.warning("Password validation failed: Special character check")
#         return False
    
#     logging.info("Password validation passed")
#     return True

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_user_by_hr(request):
#     if request.user.role == 'hr':
#         name = request.data.get('name')
#         department_id = request.data.get('department')
#         organization_id = request.data.get('organization')
#         designation = request.data.get('designation')
#         blood_group = request.data.get('blood_group')
#         emergency_contact = request.data.get('emergency_contact')
#         role = request.data.get('role')
#         can_create_guest_pass = request.data.get(
#             'can_create_guest_pass', False)
#         photo = request.FILES.get('photo')
#         password = request.data.get('password')  # Get password from request

#         allowed_roles = ["front desk", "help Desk", "security", "others"]


#         # Validate password
#         validation_error = validate_password(password)
#         if validation_error:
#             logging.error(f"Password validation error: {validation_error}")
#             return HttpResponse(f"error: {validation_error}", status=status.HTTP_400_BAD_REQUEST)


#         if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role, photo, password]):
#             return Response({"error": "All fields, including photo and password, are required."}, status=status.HTTP_400_BAD_REQUEST)

#         if role not in allowed_roles:
#             return Response({"error": f"Role '{role}' is not allowed. Allowed roles are: {', '.join(allowed_roles)}."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.create(
#                 name=name,
#                 role=role,
#                 department_id=department_id,
#                 organization_id=organization_id,
#                 designation=designation,
#                 blood_group=blood_group,
#                 emergency_contact=emergency_contact,
#                 can_create_guest_pass=can_create_guest_pass,
#                 photo=photo,
#                 created_by=request.user
#             )
#             user.set_password(password)  # Set password
#             user.save()

#             image = face_recognition.load_image_file(photo)
#             encodings = face_recognition.face_encodings(image)

#             if encodings:
#                 Face.objects.create(user=user, face_enc=encodings[0].tolist())

#             return Response({"success": f"User {user.name} created successfully with employee code {user.employee_code}"}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     return Response({"error": "Unauthorized: Only HR can create users"}, status=status.HTTP_403_FORBIDDEN)
import logging
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password as django_validate_password

def validate_password(password):
    try:
        # First, use Django's password validators
        django_validate_password(password)
    except ValidationError as e:
        # Log Django validation errors
        logging.error(f"Django password validation failed: {e}")
        return str(e)  # Return the error message from Django validators
    
    # Now perform your custom validation
    logging.info(f"Validating password: '{password}'")
    
    if len(password) < 8:
        logging.warning("Password validation failed: Length check")
        return "Password must be at least 8 characters long."
    
    if not any(char.islower() for char in password):
        logging.warning("Password validation failed: Lowercase check")
        return "Password must contain at least one lowercase letter."
    
    if not any(char.isupper() for char in password):
        logging.warning("Password validation failed: Uppercase check")
        return "Password must contain at least one uppercase letter."
    
    if not any(char in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/`~" for char in password):
        logging.warning("Password validation failed: Special character check")
        return "Password must contain at least one special character."
    
    logging.info("Password validation passed")
    return None  # No error, password is valid

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user_by_hr(request):
    if request.user.role == 'hr':
        name = request.data.get('name')
        department_id = request.data.get('department')
        organization_id = request.data.get('organization')
        designation = request.data.get('designation')
        blood_group = request.data.get('blood_group')
        emergency_contact = request.data.get('emergency_contact')
        role = request.data.get('role')
        can_create_guest_pass = request.data.get('can_create_guest_pass', 'False')  # Default to 'False' if not provided
        photo = request.FILES.get('photo')
        password = request.data.get('password')  # Get password from request

        # Convert can_create_guest_pass to a boolean value
        can_create_guest_pass = str(can_create_guest_pass).lower() == 'true'

        allowed_roles = ["front desk", "help Desk", "security", "others"]

        # Normalize the role for comparison (strip and lower case)
        role = role.strip().lower()

        # Log the values for debugging
        logging.info(f"Received role: '{role}'")
        logging.info(f"Received can_create_guest_pass: {can_create_guest_pass}")
        logging.info(f"Received password: '{password}'")

        # Validate password
        validation_error = validate_password(password)
        if validation_error:  # Check if password is invalid
            logging.error(f"Password validation error: {validation_error}")
            return Response({"error": validation_error}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure all fields are provided
        if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role, photo, password]):
            return Response({"error": "All fields, including photo and password, are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate role
        if role not in [r.lower() for r in allowed_roles]:  # Normalize allowed roles as well
            return Response({"error": f"Role '{role}' is not allowed. Allowed roles are: {', '.join(allowed_roles)}."}, status=status.HTTP_400_BAD_REQUEST)

        # Restrict guest pass creation to "front desk" role
        if can_create_guest_pass and role != "front desk":
            logging.error(f"Guest pass creation not allowed for role '{role}'")
            return Response({"error": "Only users with the 'front desk' role can create guest passes."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the user
            user = User.objects.create(
                name=name,
                role=role,
                department_id=department_id,
                organization_id=organization_id,
                designation=designation,
                blood_group=blood_group,
                emergency_contact=emergency_contact,
                can_create_guest_pass=can_create_guest_pass,
                photo=photo,
                created_by=request.user
            )
            user.set_password(password)  # Set password securely
            user.save()

            # Process face recognition encoding
            image = face_recognition.load_image_file(photo)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                Face.objects.create(user=user, face_enc=encodings[0].tolist())

            return Response({"success": f"User {user.name} created successfully with employee code {user.employee_code}"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Unauthorized: Only HR can create users."}, status=status.HTTP_403_FORBIDDEN)

# class CreateUserHrTemplate(TemplateView):  # updating
#     template_name = 'create_user_by_hr.html'
#     allowed_roles = ["front desk", "help Desk", "security", "others"]

#     def post(self, request):
#         if request.user.role == 'hr':
#             name = request.POST.get('name')
#             department_id = request.POST.get('department')
#             organization_id = request.POST.get('organization')
#             designation = request.POST.get('designation')
#             blood_group = request.POST.get('blood_group')
#             emergency_contact = request.POST.get('emergency_contact')
#             role = request.POST.get('role')
#             can_create_guest_pass = True if request.POST.get(
#                 'can_create_guest_pass', 'false') == 'true' else False
#             photo = request.FILES.get('photo')
#             # Get password from request
#             password = request.POST.get('password')

#             if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role, photo, password]):
#                 return HttpResponse("error: All fields, including photo and password, are required.", status=status.HTTP_400_BAD_REQUEST)

#             if role not in self.allowed_roles:
#                 return HttpResponse(f"error: Role '{role}' is not allowed. Allowed roles are: {', '.join(self.allowed_roles)}.", status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 user = User.objects.create(
#                     name=name,
#                     role=role,
#                     department_id=department_id,
#                     organization_id=organization_id,
#                     designation=designation,
#                     blood_group=blood_group,
#                     emergency_contact=emergency_contact,
#                     can_create_guest_pass=can_create_guest_pass,
#                     photo=photo,
#                     created_by=request.user
#                 )
#                 user.set_password(password)  # Set password
#                 user.save()

#                 image = face_recognition.load_image_file(photo)
#                 encodings = face_recognition.face_encodings(image)

#                 if encodings:
#                     Face.objects.create(
#                         user=user, face_enc=encodings[0].tolist())

#                 return HttpResponse(f"success: User {user.name} created successfully with employee code {user.employee_code}", status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return HttpResponse("error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return HttpResponse("error: Unauthorized: Only HR can create users", status=status.HTTP_403_FORBIDDEN)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['roles'] = self.allowed_roles
#         context['organizations'] = Organization.objects.all()
#         context['departments'] = Department.objects.all()
#         context['users'] = User.objects.all()
#         return context






from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import face_recognition

# class CreateUserHrTemplate(TemplateView):
#     template_name = 'user.html'
#     allowed_roles = ["front desk", "help Desk", "security", "others","accounts"]

#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         if request.user.role != 'hr':
#             return HttpResponse("error: Unauthorized: Only HR can create users", status=status.HTTP_403_FORBIDDEN)

#         name = request.POST.get('name')
#         department_id = request.POST.get('department')
#         organization_id = request.POST.get('organization')
#         designation = request.POST.get('designation')
#         blood_group = request.POST.get('blood_group')
#         emergency_contact = request.POST.get('emergency_contact')
#         role = request.POST.get('role')
#         can_create_guest_pass = request.POST.get('can_create_guest_pass') == 'true'
#         photo = request.FILES.get('photo')
#         password = request.POST.get('password')

#         if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role, photo, password]):
#             return HttpResponse("error: All fields, including photo and password, are required.", status=status.HTTP_400_BAD_REQUEST)

#         if role not in self.allowed_roles:
#             return HttpResponse(f"error: Role '{role}' is not allowed. Allowed roles are: {', '.join(self.allowed_roles)}.", status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.create(
#                 name=name,
#                 role=role,
#                 department_id=department_id,
#                 organization_id=organization_id,
#                 designation=designation,
#                 blood_group=blood_group,
#                 emergency_contact=emergency_contact,
#                 can_create_guest_pass=can_create_guest_pass,
#                 photo=photo,
#                 created_by=request.user
#             )
#             user.set_password(password)
#             user.save()

#             image = face_recognition.load_image_file(photo)
#             encodings = face_recognition.face_encodings(image)

#             if encodings:
#                 Face.objects.create(user=user, face_enc=encodings[0].tolist())

#             return HttpResponse(f"success: User {user.name} created successfully with employee code {user.employee_code}", status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = None
#         context['roles'] = self.allowed_roles
#         context['organizations'] = Organization.objects.all()
#         context['departments'] = Department.objects.all()
#         context['users'] = User.objects.all()
#         return context







# class CreateUserHrTemplate(TemplateView):
#     template_name = 'user.html'
#     allowed_roles = ["front desk", "help Desk", "security", "others", "accounts"]

#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         if request.user.role != 'hr':
#             return HttpResponse("error: Unauthorized: Only HR can create users", status=status.HTTP_403_FORBIDDEN)

#         # Gather data from the request
#         name = request.POST.get('name')
#         department_id = request.POST.get('department')
#         organization_id = request.POST.get('organization')
#         designation = request.POST.get('designation')
#         blood_group = request.POST.get('blood_group')
#         emergency_contact = request.POST.get('emergency_contact')
#         role = request.POST.get('role')
#         photo = request.FILES.get('photo')
#         password = request.POST.get('password')

#         # Only allow 'can_create_guest_pass' if role is 'front desk'
#         can_create_guest_pass = request.POST.get('can_create_guest_pass') == 'true' if role == 'front desk' else False

#         # Ensure all required fields are filled
#         if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role, photo, password]):
#             return HttpResponse("error: All fields, including photo and password, are required.", status=status.HTTP_400_BAD_REQUEST)

#         if role not in self.allowed_roles:
#             return HttpResponse(f"error: Role '{role}' is not allowed. Allowed roles are: {', '.join(self.allowed_roles)}.", status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Create the user with the specified details
#             user = User.objects.create(
#                 name=name,
#                 role=role,
#                 department_id=department_id,
#                 organization_id=organization_id,
#                 designation=designation,
#                 blood_group=blood_group,
#                 emergency_contact=emergency_contact,
#                 can_create_guest_pass=can_create_guest_pass,
#                 photo=photo,
#                 created_by=request.user
#             )
#             user.set_password(password)
#             user.save()

#             # Create face encoding if available
#             image = face_recognition.load_image_file(photo)
#             encodings = face_recognition.face_encodings(image)
#             if encodings:
#                 Face.objects.create(user=user, face_enc=encodings[0].tolist())

#             return HttpResponse(f"success: User {user.name} created successfully with employee code {user.employee_code}", status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = None
#         context['roles'] = self.allowed_roles
#         context['organizations'] = Organization.objects.all()
#         context['departments'] = Department.objects.all()
#         context['users'] = User.objects.all()
#         return context







from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import status
import face_recognition
import re

def validate_password(password):
    # Check for uppercase letter, lowercase letter, and special character
    if (any(char.islower() for char in password) and
        any(char.isupper() for char in password) and
        any(char in "!@#$%^&*()_+" for char in password)):
        return True
    return False

class CreateUserHrTemplate(TemplateView):
    template_name = 'user.html'
    allowed_roles = ["front desk", "help desk", "security", "others"]

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.role != 'hr':
            return HttpResponse("error: Unauthorized: Only HR can create users", status=status.HTTP_403_FORBIDDEN)

        name = request.POST.get('name')
        department_id = request.POST.get('department')
        organization_id = request.POST.get('organization')
        designation = request.POST.get('designation')
        blood_group = request.POST.get('blood_group')
        emergency_contact = request.POST.get('emergency_contact')
        role = request.POST.get('role')
        can_create_guest_pass = request.POST.get('can_create_guest_pass') == 'true'
        photo = request.FILES.get('photo')
        password = request.POST.get('password')

        # Validate password
        validation_error = validate_password(password)
        if validation_error:
            logging.error(f"Password validation error: {validation_error}")
            return HttpResponse(f"error: {validation_error}", status=status.HTTP_400_BAD_REQUEST)

        # if not validate_password(password):
        #     return HttpResponse("error: Password must contain at least one uppercase letter, one lowercase letter, and one special character.", status=status.HTTP_400_BAD_REQUEST)

        # Check if all fields are provided
        if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role, photo, password]):
            return HttpResponse("error: All fields, including photo and password, are required.", status=status.HTTP_400_BAD_REQUEST)

        # Check if role is allowed
        if role not in self.allowed_roles:
            return HttpResponse(f"error: Role '{role}' is not allowed. Allowed roles are: {', '.join(self.allowed_roles)}.", status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create(
                name=name,
                role=role,
                department_id=department_id,
                organization_id=organization_id,
                designation=designation,
                blood_group=blood_group,
                emergency_contact=emergency_contact,
                can_create_guest_pass=can_create_guest_pass,
                photo=photo,
                created_by=request.user
            )
            user.set_password(password)  # Set the password
            user.save()

            # Process face recognition encoding
            image = face_recognition.load_image_file(photo)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                Face.objects.create(user=user, face_enc=encodings[0].tolist())

            return HttpResponse(f"success: User {user.name} created successfully with employee code {user.employee_code}", status=status.HTTP_201_CREATED)
        except Exception as e:
            return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = None
        context['roles'] = self.allowed_roles
        context['organizations'] = Organization.objects.all()
        context['departments'] = Department.objects.all()
        context['users'] = User.objects.all()
        context['can_create_guest_pass'] = True  # Add this to the context so it can be used in the template
        return context

# class UserListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if request.user.is_superuser or request.user.role == 'hr':
#             users = User.objects.all()
#             user_data = [
#                 {
#                     "id": user.id,
#                     "name": user.name,
#                     "role": user.role,
#                     "organization": user.organization_id,
#                     "department": user.department_id,
#                     "designation": user.designation,
#                     "blood_group": user.blood_group,
#                     "emergency_contact": user.emergency_contact,
#                     "employee_code": user.employee_code
#                 }
#                 for user in users
#             ]
#             return Response(user_data, status=status.HTTP_200_OK)
#         return Response({"error": "Unauthorized: Only superusers or HR can view users."}, status=status.HTTP_403_FORBIDDEN)
# class UserListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if request.user.is_superuser or request.user.role == 'hr':
#             # Get query parameters
#             search_query = request.query_params.get('search', '')
#             department_id = request.query_params.get('department')
#             organization_id = request.query_params.get('organization')

#             # Start with all users
#             users = User.objects.all()

#             # Apply filters if provided
#             if department_id:
#                 users = users.filter(department_id=department_id)
            
#             if organization_id:
#                 users = users.filter(organization_id=organization_id)

#             # Apply search across name
#             if search_query:
#                 users = users.filter(name__icontains=search_query)

#             user_data = [
#                 {
#                     "id": user.id,
#                     "name": user.name,
#                     "role": user.role,
#                     "organization": user.organization_id,
#                     "department": user.department_id,
#                     "designation": user.designation,
#                     "blood_group": user.blood_group,
#                     "emergency_contact": user.emergency_contact,
#                     "employee_code": user.employee_code
#                 }
#                 for user in users
#             ]
#             return Response(user_data, status=status.HTTP_200_OK)
            
#         return Response(
#             {"error": "Unauthorized: Only superusers or HR can view users."}, 
#             status=status.HTTP_403_FORBIDDEN
#         )

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        if request.user.is_superuser or request.user.role == 'hr':
            # Get query parameters
            search_query = request.query_params.get('search', '')
            department_id = request.query_params.get('department')
            organization_id = request.query_params.get('organization')
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 10)

            # Start with all users
            users = User.objects.all()

            # Apply filters
            if department_id:
                users = users.filter(department_id=department_id)
            if organization_id:
                users = users.filter(organization_id=organization_id)
            if search_query:
                users = users.filter(name__icontains=search_query)

            # Apply pagination
            paginator = Paginator(users, page_size)
            current_page = paginator.get_page(page)

            user_data = [
                {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role,
                    "organization": user.organization_id,
                    "department": user.department_id,
                    "designation": user.designation,
                    "blood_group": user.blood_group,
                    "emergency_contact": user.emergency_contact,
                    "employee_code": user.employee_code
                }
                for user in current_page
            ]

            response_data = {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': int(page),
                'results': user_data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(
            {"error": "Unauthorized: Only superusers or HR can view users."}, 
            status=status.HTTP_403_FORBIDDEN
        )

class UserListTemplateView(TemplateView):
    template_name = 'users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User, Organization, Department

class UserEditView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        # Check if the request user is allowed to edit users
        if request.user.is_superuser or request.user.role in ['hr', 'superadmin']:
            user = get_object_or_404(User, id=user_id)
            
            # Get data from request and update the user fields
            user.name = request.data.get('name', user.name)
            user.role = request.data.get('role', user.role)
            user.organization_id = request.data.get('organization', user.organization_id)
            user.department_id = request.data.get('department', user.department_id)
            user.designation = request.data.get('designation', user.designation)
            user.blood_group = request.data.get('blood_group', user.blood_group)
            user.emergency_contact = request.data.get('emergency_contact', user.emergency_contact)

            # If a new password is provided, update it
            password = request.data.get('password')
            if password:
                user.set_password(password)

            # If a photo is provided, update it
            if 'photo' in request.FILES:
                user.photo = request.FILES['photo']

            # Save the updated user
            user.save()
            return Response({"success": "User updated successfully."}, status=status.HTTP_200_OK)

        # If the user does not have permission, return a 403 error
        return Response({"error": "Unauthorized: Only superusers or HR can edit users."}, status=status.HTTP_403_FORBIDDEN)









# class UserEditTemplateView(TemplateView):
#     template_name = 'user.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user_id = self.kwargs.get('user_id')
#         context['user'] = get_object_or_404(User, id=user_id)
#         context['roles'] = ["hr", "accounts"] if self.request.user.role == 'superadmin' else ["front desk", "help Desk", "security", "others"]
#         context['organizations'] = Organization.objects.all()
#         context['departments'] = Department.objects.all()
#         return context



from django.shortcuts import redirect

# class UserEditTemplateView(View):
#     def get(self, request, user_id):
#         user = get_object_or_404(User, id=user_id)
        
#         # Check permissions
#         if not (request.user.is_superuser or request.user.role in ['hr', 'superadmin']):
#             return HttpResponse("error: Unauthorized: Only superusers or HR can edit users.", status=status.HTTP_403_FORBIDDEN)
        
#         roles = ["hr", "accounts"] if request.user.role == 'superadmin' else ["front desk", "help Desk", "security", "others"]
#         organizations = Organization.objects.all()
#         departments = Department.objects.all()

#         return render(request, 'user_edit.html', {
#             'user': user,
#             'roles': roles,
#             'organizations': organizations,
#             'departments': departments
#         })

#     def post(self, request, user_id):
#         user = get_object_or_404(User, id=user_id)

#         if request.user.is_superuser or request.user.role in ['hr', 'superadmin']:
#             # Update the user fields
#             user.name = request.POST.get('name', user.name)
#             user.role = request.POST.get('role', user.role)
#             user.organization_id = request.POST.get('organization', user.organization_id)
#             user.department_id = request.POST.get('department', user.department_id)
#             user.designation = request.POST.get('designation', user.designation)
#             user.blood_group = request.POST.get('blood_group', user.blood_group)
#             user.emergency_contact = request.POST.get('emergency_contact', user.emergency_contact)
            
#             # Update password if provided
#             password = request.POST.get('password')
#             if password:
#                 user.set_password(password)

#             # Update photo if provided
#             if 'photo' in request.FILES:
#                 user.photo = request.FILES['photo']

#             # Save user
#             user.save()
#             return HttpResponse("success: User updated successfully.", status=status.HTTP_200_OK)

#         return HttpResponse("error: Unauthorized: Only superusers or HR can edit users.", status=status.HTTP_403_FORBIDDEN)




class UserEditTemplateView(View):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # Check permissions
        if not (request.user.is_superuser or request.user.role in ['hr', 'superadmin']):
            return HttpResponse("error: Unauthorized: Only superusers or HR can edit users.", status=status.HTTP_403_FORBIDDEN)
        
        # HR cannot edit superadmin
        if request.user.role == 'hr' and user.is_superuser:
            return HttpResponse("error: Unauthorized: HR cannot edit superadmin.", status=status.HTTP_403_FORBIDDEN)

        roles = ["hr", "accounts"] if request.user.role == 'superadmin' else ["front desk", "help Desk", "security", "others"]
        organizations = Organization.objects.all()
        departments = Department.objects.all()

        return render(request, 'user_edit.html', {
            'user': user,
            'roles': roles,
            'organizations': organizations,
            'departments': departments
        })

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user.is_superuser or request.user.role in ['hr', 'superadmin']:
            # HR cannot update superadmin
            if request.user.role == 'hr' and user.is_superuser:
                return HttpResponse("error: Unauthorized: HR cannot edit superadmin.", status=status.HTTP_403_FORBIDDEN)

            # Update the user fields
            user.name = request.POST.get('name', user.name)
            user.role = request.POST.get('role', user.role)
            user.organization_id = request.POST.get('organization', user.organization_id)
            user.department_id = request.POST.get('department', user.department_id)
            user.designation = request.POST.get('designation', user.designation)
            user.blood_group = request.POST.get('blood_group', user.blood_group)
            user.emergency_contact = request.POST.get('emergency_contact', user.emergency_contact)

            # Update password if provided
            password = request.POST.get('password')
            if password:
                user.set_password(password)

            # Update photo if provided
            if 'photo' in request.FILES:
                user.photo = request.FILES['photo']

            # Save user
            user.save()
            return HttpResponse("success: User updated successfully.", status=status.HTTP_200_OK)

        return HttpResponse("error: Unauthorized: Only superusers or HR can edit users.", status=status.HTTP_403_FORBIDDEN)






class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        if request.user.is_superuser or request.user.role == 'hr':
            try:
                user = User.objects.get(id=user_id)
                user.delete()
                return Response({"success": f"User with ID {user_id} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Unauthorized: Only superusers or HR can delete users."}, status=status.HTTP_403_FORBIDDEN)


# @method_decorator(login_required, name='dispatch')
# class UserDeleteTemplateView(View):
#     def get(self, request, user_id):
#         if request.user.is_superuser or request.user.role == 'hr':
#             try:
#                 user = User.objects.get(id=user_id)
#                 user.delete()
#                 return HttpResponse(f"success: User with ID {user_id} deleted successfully.", status=status.HTTP_204_NO_CONTENT)
#             except User.DoesNotExist:
#                 return HttpResponse("error: User not found.", status=status.HTTP_404_NOT_FOUND)
#         return HttpResponse("error: Unauthorized: Only superusers or HR can delete users.", status=status.HTTP_403_FORBIDDEN)




from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# @method_decorator(login_required, name='dispatch')
# class UserDeleteTemplateView(View):
#     def get(self, request, user_id):
#         if request.user.is_superuser or request.user.role == 'hr':
#             try:
#                 user = User.objects.get(id=user_id)
#                 user.delete()
#                 return HttpResponse(f"success: User with ID {user_id} deleted successfully.", status=status.HTTP_200_OK)
#             except User.DoesNotExist:
#                 return HttpResponse("error: User not found.", status=status.HTTP_404_NOT_FOUND)
#         return HttpResponse("error: Unauthorized: Only superusers or HR can delete users.", status=status.HTTP_403_FORBIDDEN)




@method_decorator(login_required, name='dispatch')
class UserDeleteTemplateView(View):
    def get(self, request, user_id):
        if request.user.is_superuser or request.user.role == 'hr':
            try:
                user = User.objects.get(id=user_id)

                # HR cannot delete superadmin
                if request.user.role == 'hr' and user.is_superuser:
                    return HttpResponse("error: Unauthorized: HR cannot delete superadmin.", status=status.HTTP_403_FORBIDDEN)

                user.delete()
                return HttpResponse(f"success: User with ID {user_id} deleted successfully.", status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return HttpResponse("error: User not found.", status=status.HTTP_404_NOT_FOUND)

        return HttpResponse("error: Unauthorized: Only superusers or HR can delete users.", status=status.HTTP_403_FORBIDDEN)




# Old one


# class CreateUserBySuperuser(APIView):
#     permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

#     def post(self, request):
#         if request.user.is_superuser:  # Check if the user is a superuser
#             # Extract data from the request
#             name = request.data.get('name')
#             role = request.data.get('role')
#             organization_id = request.data.get('organization')
#             department_id = request.data.get('department')
#             designation = request.data.get('designation')
#             blood_group = request.data.get('blood_group')
#             emergency_contact = request.data.get('emergency_contact')
#             photo = request.FILES.get('photo')  # Get the photo from the request


#             # Allowed roles for the superuser
#             allowed_roles = ["hr", "accounts"]

#             # Validate required fields
#             if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact, photo]):
#                 return Response({"error": "All fields, including photo, are required."}, status=status.HTTP_400_BAD_REQUEST)
#              # Validate that the role is within the allowed roles for the superuser
#             if role not in allowed_roles:
#                 return Response({"error": f"Role '{role}' is not allowed. Superuser can only assign roles: {', '.join(allowed_roles)}."}, status=status.HTTP_400_BAD_REQUEST)
#             try:
#                 # Create the user
#                 user = User.objects.create(
#                     name=name,
#                     role=role,
#                     organization_id=organization_id,
#                     department_id=department_id,
#                     designation=designation,
#                     blood_group=blood_group,
#                     emergency_contact=emergency_contact,
#                     photo=photo,  # Save the photo
#                     created_by=request.user  # Superuser creating the user
#                 )
#                 # Process the photo to create face encoding
#                 image = face_recognition.load_image_file(photo)
#                 encodings = face_recognition.face_encodings(image)
#                 if encodings:
#                     # Save face encoding if detected
#                     Face.objects.create(user=user, face_enc=encodings[0].tolist())
#                 return Response({"success": f"User '{user.name}' created successfully with employee code {user.employee_code}."}, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response({"error": "Unauthorized: Only superusers can create users."}, status=status.HTTP_403_FORBIDDEN)
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Ensure only authenticated users can access
# def create_user_by_hr(request):
#     if request.user.role == 'hr':  # Check if the user is HR
#         # Extract data from request
#         name = request.data.get('name')
#         department_id = request.data.get('department')
#         organization_id = request.data.get('organization')
#         designation = request.data.get('designation')
#         blood_group = request.data.get('blood_group')
#         emergency_contact = request.data.get('emergency_contact')
#         role = request.data.get('role')  # Get the role from the request
#         can_create_guest_pass = request.data.get('can_create_guest_pass', False)  # New field for guest pass permission
#         photo = request.FILES.get('photo')  # Get the photo from the request
#         # List of roles that can be assigned by HR
#         allowed_roles = [ "front desk", "help Desk", "security", "others"]
#         # Check if all required fields are provided
#         if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role, photo]):
#             return Response({"error": "All fields, including photo, are required."}, status=status.HTTP_400_BAD_REQUEST)
#         # Validate the assigned role
#         if role not in allowed_roles:
#             return Response({"error": f"Role '{role}' is not allowed. Allowed roles are: {', '.join(allowed_roles)}."}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             # Create the user
#             user = User.objects.create(
#                 name=name,
#                 role=role,  # Assign the role provided in the request
#                 department_id=department_id,
#                 organization_id=organization_id,
#                 designation=designation,
#                 blood_group=blood_group,
#                 emergency_contact=emergency_contact,
#                 can_create_guest_pass=can_create_guest_pass,  # Set guest pass permission
#                 photo=photo,  # Save the photo
#                 created_by=request.user  # HR creating the user
#             )
#             # Process the photo to create face encoding
#             image = face_recognition.load_image_file(photo)
#             encodings = face_recognition.face_encodings(image)
#             if encodings:
#                 # Save face encoding if detected
#                 Face.objects.create(user=user, face_enc=encodings[0].tolist())
#             return Response({"success": f"User {user.name} created successfully with employee code {user.employee_code}"}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     return Response({"error": "Unauthorized: Only HR can create users"}, status=status.HTTP_403_FORBIDDEN)
# from .serial_control import open_door_async  # Import the async door control function


# Function to convert "HH:MM" format to timedelta
from .serial_control import open_door_async  # Import the async door control function
def time_spent_to_timedelta(time_str):
    if time_str == "00:00":
        return timedelta(0)
    hours, minutes = map(int, time_str.split(':'))
    return timedelta(hours=hours, minutes=minutes)

# class FaceMatchView(APIView):
#     permission_classes = [AllowAny]  # This allows access to everyone


#     def preprocess_image(self, photo):
#         preprocess_start = time.time() # start time of preprocessing
#         # Open the image using PIL
#         image = Image.open(photo)

#         # Enhance contrast (to improve face detection)
#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(2.0)  # Adjust the enhancement level as needed

#         # Convert to grayscale (optional, but can improve accuracy)
#         image = image.convert("L")

#         # Resize the image while maintaining aspect ratio
#         image.thumbnail((300, 300), Image.Resampling.LANCZOS)

#         # Convert the image back to a format compatible with face recognition
#         buffered = BytesIO()
#         image.save(buffered, format='JPEG')

#         preprocess_end = time.time() # end time for preprocessing
#         print(f"Image preprocessing took {preprocess_end - preprocess_start:.4f} seconds")
#         return face_recognition.load_image_file(BytesIO(buffered.getvalue()))


#     def post(self, request):
#         start_time = time.time()  # Overall process start time
#         photo = request.FILES.get('photo')  # Get the photo from the request

#         if not photo:
#             return Response({"error": "Photo is required for face matching."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Load the uploaded image
#             image_load_start = time.time()
#             # image = face_recognition.load_image_file(photo)
#             image = self.preprocess_image(photo)#preprocess the image before face encoding
#             encoding_start = time.time()  # Start time for encoding
#             uploaded_face_encodings = face_recognition.face_encodings(image)
#             encoding_end = time.time()  # End time for encoding

#             image_load_end = time.time()
#             # print(f"Image load and encoding took {image_load_end - image_load_start:.4f} seconds")
#             print(f"Image encoding took {encoding_end - encoding_start:.4f} seconds")
#             print(f"Total image processing (load + preprocess + encode) took {image_load_end - image_load_start:.4f} seconds")


#             if not uploaded_face_encodings:
#                 return Response({"error": "No face found in the uploaded photo."}, status=status.HTTP_400_BAD_REQUEST)

#             uploaded_face_encoding = uploaded_face_encodings[0]


#             # Step 2: Face matching process
#             match_start = time.time()
#             # Variables to track the closest match
#             closest_distance = float("inf")
#             matched_user = None
#             matched_guest = None

#             # Iterate over the stored face encodings to find a match
#             all_user_faces = Face.objects.filter(user__isnull=False)  # User faces
#             # all_faces = Face.objects.all()
#             for face in all_user_faces:
#             # for face in all_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))  # Convert stored encoding back to numpy array

#                 # Calculate face distance
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                 # Update if this is the closest match so far
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = face.user
#                     matched_guest = None


#             # Iterate over the stored guest face encodings
#             all_guest_faces = Face.objects.filter(guest__isnull=False)  # Guest faces
#             for face in all_guest_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = None
#                     matched_guest = face.guest

#             match_end = time.time()
#             print(f"Face matching process took {match_end - match_start:.4f} seconds")


#             # Step 3: Attendance update and door control
#             attendance_start = time.time()
#             # Set a threshold for what is considered a "match"
#             if closest_distance < 0.6:  # You can adjust this threshold as needed
#                 # Record attendance for the matched user
#                 now = timezone.now()
#                 attendance, created = Attendance.objects.get_or_create(
#                     user=matched_user,
#                     in_time__date=now.date(),  # Match based on today's date
#                     defaults={'in_time': now}
#                 )

#                 # If attendance record already exists, update the out_time
#                 if not created:
#                     attendance.out_time = now
#                     attendance.save()


#                 # Log time and open door asynchronously
#                 open_door_start = time.time()
#                 # Open the door asynchronously
#                 open_door_async()
#                 open_door_end = time.time()

#                 print(f"Attendance update took {open_door_start - attendance_start:.4f} seconds")
#                 print(f"Door opening command took {open_door_end - open_door_start:.4f} seconds")

#                 # Log total time taken
#                 total_time = time.time() - start_time
#                 print(f"Total process time: {total_time:.4f} seconds")

#                 return Response({"success": f"Match found: {matched_user.name}. Door is opening."}, status=status.HTTP_200_OK)

#                 # return Response({"success": f"Match found: {matched_user.name}"}, status=status.HTTP_200_OK)


#             # If no match is found within the threshold
#             return Response({"error": "No matching user found."}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             # Log any error time
#             error_time = time.time() - start_time
#             print(f"Error occurred after {error_time:.4f} seconds: {str(e)}")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######Updated
# class FaceMatchView(APIView):
#     permission_classes = [AllowAny]

#     def preprocess_image(self, photo):
#         preprocess_start = time.time()
#         image = Image.open(photo)

#         # Enhance contrast
#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(2.0)

#         # Convert to grayscale (optional)
#         image = image.convert("L")

#         # Resize image
#         image.thumbnail((300, 300), Image.Resampling.LANCZOS)

#         # Save to buffer
#         buffered = BytesIO()
#         image.save(buffered, format='JPEG')

#         preprocess_end = time.time()
#         print(
#             f"Image preprocessing took {preprocess_end - preprocess_start:.4f} seconds")
#         return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

#     def post(self, request):
#         start_time = time.time()
#         photo = request.FILES.get('photo')

#         if not photo:
#             return Response({"error": "Photo is required for face matching."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Preprocess and encode the uploaded image
#             image = self.preprocess_image(photo)
#             uploaded_face_encodings = face_recognition.face_encodings(image)

#             if not uploaded_face_encodings:
#                 return Response({"error": "No face found in the uploaded photo."}, status=status.HTTP_400_BAD_REQUEST)

#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Step 2: Face matching process
#             match_start = time.time()
#             closest_distance = float("inf")
#             matched_user = None
#             matched_guest = None

#             # Iterate over the stored user face encodings
#             all_user_faces = Face.objects.filter(
#                 user__isnull=False)  # User faces
#             for face in all_user_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))
#                 distance = face_recognition.face_distance(
#                     [stored_face_encoding], uploaded_face_encoding)[0]

#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = face.user
#                     matched_guest = None

#             # Iterate over the stored guest face encodings
#             all_guest_faces = Face.objects.filter(
#                 guest__isnull=False)  # Guest faces
#             for face in all_guest_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))
#                 distance = face_recognition.face_distance(
#                     [stored_face_encoding], uploaded_face_encoding)[0]

#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = None
#                     matched_guest = face.guest

#             match_end = time.time()
#             print(
#                 f"Face matching process took {match_end - match_start:.4f} seconds")

#             # Step 3: Attendance and response handling
#             attendance_start = time.time()

#             if closest_distance < 0.6:  # Adjust threshold as needed
#                 now = timezone.now()

#                 # If a user is matched, record user attendance
#                 if matched_user:
#                     attendance, created = Attendance.objects.get_or_create(
#                         user=matched_user,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()

#                     # Asynchronously open door
#                     open_door_async()
#                     total_time = time.time() - start_time
#                     print(f"Total process time: {total_time:.4f} seconds")
#                     return Response({"success": f"Match found: {matched_user.name}. Door is opening."}, status=status.HTTP_200_OK)

#                 # If a guest is matched, handle guest-specific actions and open the door
#                 if matched_guest:
#                     attendance, created = Attendance.objects.get_or_create(
#                         guest=matched_guest,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()

#                     # Asynchronously open door for the guest
#                     open_door_async()
#                     total_time = time.time() - start_time
#                     print(f"Total process time: {total_time:.4f} seconds")
#                     return Response({"success": f"Guest match found: {matched_guest.name}. Door is opening."}, status=status.HTTP_200_OK)

#             # If no match is found within the threshold
#             return Response({"error": "No matching user or guest found."}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             error_time = time.time() - start_time
#             print(f"Error occurred after {error_time:.4f} seconds: {str(e)}")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from PIL import Image, ImageEnhance
from io import BytesIO
import time
import face_recognition
import numpy as np
from django.utils import timezone

# class FaceMatchView(APIView):
#     permission_classes = [AllowAny]

#     def preprocess_image(self, photo):
#         preprocess_start = time.time()
#         image = Image.open(photo)

#         # Enhance contrast
#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(2.0)

#         # Convert to grayscale (optional)
#         image = image.convert("L")

#         # Resize image
#         image.thumbnail((300, 300), Image.Resampling.LANCZOS)

#         # Save to buffer
#         buffered = BytesIO()
#         image.save(buffered, format='JPEG')

#         preprocess_end = time.time()
#         print(f"Image preprocessing took {preprocess_end - preprocess_start:.4f} seconds")
#         return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

#     def post(self, request):
#         start_time = time.time()

#         # Handle multiple images in the request
#         photos = request.FILES.getlist('photos')
#         if not photos:
#             return Response({"error": "At least one photo is required for face matching."}, status=status.HTTP_400_BAD_REQUEST)

#         results = []  # To store results for each image
#         overall_bounding_boxes = []  # To store bounding boxes from all images
#         multiple_faces_detected = False

#         for photo in photos:
#             try:
#                 # Preprocess and encode the uploaded image
#                 image = self.preprocess_image(photo)
#                 uploaded_face_encodings = face_recognition.face_encodings(image)
#                 uploaded_face_locations = face_recognition.face_locations(image)

#                 # Extract bounding box coordinates in the required format
#                 bounding_boxes = [
#                     [(top, right), (bottom, left)]
#                     for top, right, bottom, left in uploaded_face_locations
#                 ]
#                 overall_bounding_boxes.extend(bounding_boxes)

#                 # Check for multiple faces in the current image
#                 if len(uploaded_face_encodings) > 1:
#                     multiple_faces_detected = True
#                     results.append({
#                         "photo_name": photo.name,
#                         "error": "Multiple faces detected in this image.",
#                         "bounding_boxes": bounding_boxes
#                     })
#                     continue

#                 if not uploaded_face_encodings:
#                     results.append({
#                         "photo_name": photo.name,
#                         "error": "No face found in the uploaded photo.",
#                     })
#                     continue

#             except Exception as e:
#                 results.append({
#                     "photo_name": photo.name,
#                     "error": f"Error processing image: {str(e)}"
#                 })

#         # Check if multiple faces are detected across any image or multiple images uploaded
#         if len(photos) > 1 or multiple_faces_detected:
#             return Response({
#                 "error": "Face matching cannot be performed because multiple images or faces were detected.",
#                 "bounding_boxes": overall_bounding_boxes
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # If only one image and one face are detected, proceed with matching
#         try:
#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Face matching process
#             closest_distance = float("inf")
#             matched_user = None
#             matched_guest = None

#             # Iterate over the stored user face encodings
#             all_user_faces = Face.objects.filter(user__isnull=False)  # User faces
#             for face in all_user_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = face.user
#                     matched_guest = None

#             # Iterate over the stored guest face encodings
#             all_guest_faces = Face.objects.filter(guest__isnull=False)  # Guest faces
#             for face in all_guest_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = None
#                     matched_guest = face.guest

#             # Handle match results
#             if closest_distance < 0.6:  # Adjust threshold as needed
#                 now = timezone.now()

#                 if matched_user:
#                     attendance, created = Attendance.objects.get_or_create(
#                         user=matched_user,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()

#                     open_door_async()
#                     return Response({
#                         "success": f"Match found: {matched_user.name}. Door is opening.",
#                         "bounding_boxes": overall_bounding_boxes
#                     }, status=status.HTTP_200_OK)

#                 if matched_guest:
#                     attendance, created = Attendance.objects.get_or_create(
#                         guest=matched_guest,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()

#                     open_door_async()
#                     return Response({
#                         "success": f"Guest match found: {matched_guest.name}. Door is opening.",
#                         "bounding_boxes": overall_bounding_boxes
#                     }, status=status.HTTP_200_OK)

#             return Response({
#                 "error": "No matching user or guest found.",
#                 "bounding_boxes": overall_bounding_boxes
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({"error": f"Error during matching: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class FaceMatchView(APIView):
#     permission_classes = [AllowAny]
#     _face_encodings_cache = None
#     _cache_timestamp = None
#     CACHE_DURATION = 300  # 5 minutes cache

#     @classmethod
#     def get_cached_encodings(cls):
#         now = time.time()
#         if (not cls._face_encodings_cache or 
#             not cls._cache_timestamp or 
#             now - cls._cache_timestamp > cls.CACHE_DURATION):
            
#             user_faces = Face.objects.filter(user__isnull=False).select_related('user')
#             guest_faces = Face.objects.filter(guest__isnull=False).select_related('guest')
            
#             cls._face_encodings_cache = {
#                 'users': [(face.user, np.array(eval(face.face_enc))) for face in user_faces],
#                 'guests': [(face.guest, np.array(eval(face.face_enc))) for face in guest_faces]
#             }
#             cls._cache_timestamp = now
#         return cls._face_encodings_cache

#     def preprocess_image(self, photo):
#         image = Image.open(photo)
#         image.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
#         # Enhance only if needed
#         extrema = image.convert("L").getextrema()
#         if (extrema[1] - extrema[0]) < 100:
#             enhancer = ImageEnhance.Contrast(image)
#             image = enhancer.enhance(1.5)
        
#         image = image.convert("L")
#         buffered = BytesIO()
#         image.save(buffered, format='JPEG', quality=85)
#         return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

#     def post(self, request):
#         start_time = time.time()
#         photos = request.FILES.getlist('photos')

#         if not photos:
#             return Response({"error": "Photo required"}, 
#                           status=status.HTTP_400_BAD_REQUEST)

#         # Process single photo
#         try:
#             photo = photos[0]
#             image = self.preprocess_image(photo)
#             face_locations = face_recognition.face_locations(image, model='hog')

#             if not face_locations:
#                 return Response({"error": "No face detected"}, 
#                               status=status.HTTP_400_BAD_REQUEST)

#             if len(face_locations) > 1:
#                 return Response({
#                     "error": "Multiple faces detected",
#                     "bounding_boxes": [
#                         [(top, right), (bottom, left)]
#                         for top, right, bottom, left in face_locations
#                     ]
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # Get face encoding and cached faces
#             face_encoding = face_recognition.face_encodings(image, face_locations)[0]
#             cached_faces = self.get_cached_encodings()

#             # Find best match
#             closest_match = None
#             closest_distance = float('inf')

#             # Check users
#             for user, stored_encoding in cached_faces['users']:
#                 distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     closest_match = ('user', user)

#             # Check guests
#             for guest, stored_encoding in cached_faces['guests']:
#                 distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     closest_match = ('guest', guest)

#             # Handle match results
#             if closest_distance < 0.46:
#                 now = timezone.now()
#                 match_type, matched_person = closest_match

#                 if match_type == 'user':
#                     attendance = Attendance.objects.update_or_create(
#                         user=matched_person,
#                         in_time__date=now.date(),
#                         defaults={'out_time': now}
#                     )
#                     open_door_async()
#                     print(f"Processing time: {time.time() - start_time:.3f}s")
#                     return Response({
#                         "success": f"Match found: {matched_person.name}",
#                         "bounding_boxes": [
#                             [(top, right), (bottom, left)]
#                             for top, right, bottom, left in face_locations
#                         ]
#                     }, status=status.HTTP_200_OK)
#                 else:
#                     attendance = Attendance.objects.update_or_create(
#                         guest=matched_person,
#                         in_time__date=now.date(),
#                         defaults={'out_time': now}
#                     )
#                     open_door_async()
#                     print(f"Processing time: {time.time() - start_time:.3f}s")
#                     return Response({
#                         "success": f"Guest match: {matched_person.name}",
#                         "bounding_boxes": [
#                             [(top, right), (bottom, left)]
#                             for top, right, bottom, left in face_locations
#                         ]
#                     }, status=status.HTTP_200_OK)

#             print(f"Processing time: {time.time() - start_time:.3f}s")
#             return Response({
#                 "error": "No match found",
#                 "bounding_boxes": [
#                     [(top, right), (bottom, left)]
#                     for top, right, bottom, left in face_locations
#                 ]
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             print(f"Error time: {time.time() - start_time:.3f}s")
#             return Response({"error": str(e)}, 
#                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
import time
import logging
import os
from datetime import datetime

# Set up logging
log_file_path = os.path.join(os.path.dirname(__file__), 'face_match_logs.txt')
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FaceMatchView(APIView):
    permission_classes = [AllowAny]
    _face_encodings_cache = None
    _cache_timestamp = None
    CACHE_DURATION = 300  # 5 minutes cache

    @classmethod
    def get_cached_encodings(cls):
        now = time.time()
        if (not cls._face_encodings_cache or 
            not cls._cache_timestamp or 
            now - cls._cache_timestamp > cls.CACHE_DURATION):
            
            start_time = time.time()
            user_faces = Face.objects.filter(user__isnull=False).select_related('user')
            guest_faces = Face.objects.filter(guest__isnull=False).select_related('guest')
            db_fetch_time = time.time() - start_time
            
            logging.info(f"Time to fetch faces from DB: {db_fetch_time:.3f}s")

            cls._face_encodings_cache = {
                'users': [(face.user, np.array(eval(face.face_enc))) for face in user_faces],
                'guests': [(face.guest, np.array(eval(face.face_enc))) for face in guest_faces]
            }
            cls._cache_timestamp = now
        return cls._face_encodings_cache

    def preprocess_image(self, photo):
        start_time = time.time()
        image = Image.open(photo)
        image.thumbnail((300, 300), Image.Resampling.LANCZOS)

        # Enhance only if needed
        extrema = image.convert("L").getextrema()
        if (extrema[1] - extrema[0]) < 100:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)

        image = image.convert("L")
        buffered = BytesIO()
        image.save(buffered, format='JPEG', quality=85)
        preprocess_time = time.time() - start_time

        logging.info(f"Time to preprocess image: {preprocess_time:.3f}s")
        return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

    def post(self, request):
        total_start_time = time.time()
        photos = request.FILES.getlist('photos')

        if not photos:
            logging.warning("No photos provided in request.")
            return Response({"error": "Photo required"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            step_start_time = time.time()
            photo = photos[0]
            image = self.preprocess_image(photo)
            face_locations = face_recognition.face_locations(image, model='hog')
            face_detection_time = time.time() - step_start_time
            logging.info(f"Time for face detection: {face_detection_time:.3f}s")

            if not face_locations:
                logging.info("No face detected in the image.")
                return Response({"error": "No face detected"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            if len(face_locations) > 1:
                logging.info("Multiple faces detected in the image.")
                return Response({
                    "error": "Multiple faces detected",
                    "bounding_boxes": [
                        [(top, right), (bottom, left)]
                        for top, right, bottom, left in face_locations
                    ]
                }, status=status.HTTP_400_BAD_REQUEST)

            step_start_time = time.time()
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
            encoding_time = time.time() - step_start_time
            logging.info(f"Time for face encoding: {encoding_time:.3f}s")

            step_start_time = time.time()
            cached_faces = self.get_cached_encodings()
            cache_retrieval_time = time.time() - step_start_time
            logging.info(f"Time to retrieve cached encodings: {cache_retrieval_time:.3f}s")

            step_start_time = time.time()
            closest_match = None
            closest_distance = float('inf')

            # Check users
            for user, stored_encoding in cached_faces['users']:
                distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                if distance < closest_distance:
                    closest_distance = distance
                    closest_match = ('user', user)

            # Check guests
            for guest, stored_encoding in cached_faces['guests']:
                distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                if distance < closest_distance:
                    closest_distance = distance
                    closest_match = ('guest', guest)
            
            matching_time = time.time() - step_start_time
            logging.info(f"Time for matching: {matching_time:.3f}s")

            if closest_distance < 0.46:
                now = timezone.now()
                match_type, matched_person = closest_match
                step_start_time = time.time()

                if match_type == 'user':
                    Attendance.objects.update_or_create(
                        user=matched_person,
                        in_time__date=now.date(),
                        defaults={'out_time': now}
                    )
                else:
                    Attendance.objects.update_or_create(
                        guest=matched_person,
                        in_time__date=now.date(),
                        defaults={'out_time': now}
                    )
                open_door_async()
                attendance_time = time.time() - step_start_time
                logging.info(f"Time to update attendance and open door: {attendance_time:.3f}s")

                total_time = time.time() - total_start_time
                logging.info(f"Total processing time: {total_time:.3f}s")
                return Response({
                    "success": f"Match found: {matched_person.name}",
                    "bounding_boxes": [
                        [(top, right), (bottom, left)]
                        for top, right, bottom, left in face_locations
                    ]
                }, status=status.HTTP_200_OK)

            logging.info("No match found for the face encoding.")
            return Response({
                "error": "No match found",
                "bounding_boxes": [
                    [(top, right), (bottom, left)]
                    for top, right, bottom, left in face_locations
                ]
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            return Response({"error": str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            total_time = time.time() - total_start_time
            logging.info(f"Total processing time: {total_time:.3f}s")

@csrf_exempt
def match_face2(request):
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

imgcount=0

# @csrf_exempt
# def match_face(request):
#     global imgcount
#     if request.method == 'POST':
        
#         start_time = time.time()
#         images = request.FILES.getlist('images')
#         door = request.POST.get('door')
#         entryexit = request.POST.get('entryexit')
#         matched_users = []

#         if not images:
#             return JsonResponse({"error": "Images are required for face matching."}, status=400)

#         def preprocess_image(photo):
#             """Preprocesses an image to enhance contrast, convert to grayscale, and resize."""
#             preprocess_start = time.time()
#             image = Image.open(photo)
#             image = image.rotate(270, expand=True)

#             # Enhance contrast
#             enhancer = ImageEnhance.Contrast(image)
#             image = enhancer.enhance(2.0)

#             # Convert to grayscale
#             image = image.convert("L")

#             # Resize image
#             image.thumbnail((300, 300), Image.Resampling.LANCZOS)

#             # Save to buffer
#             buffered = BytesIO()
#             image.save(buffered, format='JPEG')
#             image.save("a"+photo, format='JPEG')

#             preprocess_end = time.time()
#             print(f"Image preprocessing took {preprocess_end - preprocess_start:.4f} seconds")
#             return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

#         try:
            
#             print(f"facerecognition started")
#             for photo in images:
#                 print(f"Photo ")
#                 # Preprocess and encode the uploaded image

#                 image_path = str(imgcount)+photo.name
#                 imgcount=imgcount+1
#                 with open(image_path, 'wb+') as destination:
#                     for chunk in photo.chunks():
#                         destination.write(chunk)
#                 image = preprocess_image(image_path)
#                 uploaded_face_encodings = face_recognition.face_encodings(image)

#                 if not uploaded_face_encodings:
#                     print(f"no face in photo")
#                     continue

#                 uploaded_face_encoding = uploaded_face_encodings[0]

#                 # Face matching process
#                 closest_distance = float("inf")
#                 matched_user = None
#                 matched_guest = None

#                 # Iterate over the stored user face encodings
#                 all_user_faces = Face.objects.filter(user__isnull=False)
#                 for face in all_user_faces:
#                     stored_face_encoding = np.array(eval(face.face_enc))
#                     distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
#                     print(f"face found in Photo ")

#                     if distance < closest_distance:
#                         closest_distance = distance
#                         matched_user = face.user
#                         matched_guest = None

#                 # Iterate over the stored guest face encodings
#                 all_guest_faces = Face.objects.filter(guest__isnull=False)
#                 for face in all_guest_faces:
#                     stored_face_encoding = np.array(eval(face.face_enc))
#                     distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                     if distance < closest_distance:
#                         closest_distance = distance
#                         matched_user = None
#                         matched_guest = face.guest

#                 # Attendance and response handling
#                 if closest_distance < 0.6:  # Adjust threshold as needed
#                     now = timezone.now()
#                     if matched_user:
#                         print(f"no face recognised ")
#                         matched_users.append({
                            


#                             'user_id': str(matched_user.id),
#                             'employee_id': str(matched_user.employee_code,),
#                             'full_name':  matched_user.name ,
#                             'access':"",
#                         })
#                         # Record attendance
#                         Attendance.objects.get_or_create(
#                             user=matched_user,
#                             in_time__date=now.date(),
#                             defaults={'in_time': now}
#                         )

#                     elif matched_guest:
#                         matched_users.append({ 

#                             'user_id': str(matched_guest.id),
#                             'employee_id': str(0),
#                             'full_name':  matched_guest.name,
#                             'access':"",
#                         })
#                         # Record attendance
#                         Attendance.objects.get_or_create(
#                             guest=matched_guest,
#                             in_time__date=now.date(),
#                             defaults={'in_time': now}
#                         )

            
#             # Check if any users were matched
#             if not matched_users:
#                 print(f"no  recognised  face")
#                 return JsonResponse({'error': 'user not found'}, status=200)

#             total_time = time.time() - start_time
#             print(f"Total process time: {total_time:.4f} seconds")
#             print(f"sending data")
#             print(matched_users)
#             matched_users
#             return JsonResponse({'matched_users': matched_users}, status=200)

#         except Exception as e:
#             error_time = time.time() - start_time
#             print(f"Error occurred after {error_time:.4f} seconds: {str(e)}")
#             return JsonResponse({"error": str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=405)













###############Updated

# @csrf_exempt
# def match_face(request):
#     global imgcount
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=405)
    
#     def preprocess_image(photo):
#         """Preprocesses an image to enhance contrast, convert to grayscale, and resize."""
#         preprocess_start = time.time()
#         image = Image.open(photo)
#         image = image.rotate(270, expand=True)

#         # Enhance contrast
#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(2.0)

#         # Convert to grayscale
#         image = image.convert("L")

#         # Resize image
#         image.thumbnail((200, 200), Image.Resampling.LANCZOS)

#         # Save to buffer
#         buffered = BytesIO()
#         image.save(buffered, format='JPEG')

#         preprocess_end = time.time()
#         print(f"Image preprocessing took {preprocess_end - preprocess_start:.4f} seconds")
#         return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

#     start_time = time.time()
#     images = request.FILES.getlist('images')
#     matched_users = []

#     if not images:
#         return JsonResponse({"error": "Images are required for face matching."}, status=400)

#     try:
#         print("Face recognition started")
#         # Load all user and guest face encodings into memory once
#         user_faces = [(face.user, np.array(eval(face.face_enc))) for face in Face.objects.filter(user__isnull=False)]
#         guest_faces = [(face.guest, np.array(eval(face.face_enc))) for face in Face.objects.filter(guest__isnull=False)]

#         for photo in images:
#             # Preprocess the image
#             image = preprocess_image(photo)  # Call the nested preprocess function
            
#             # Perform face encoding on the preprocessed image
#             uploaded_face_encodings = face_recognition.face_encodings(image)

#             if not uploaded_face_encodings:
#                 continue  # Skip images with no detectable face

#             # Ensure only one face is processed per image
#             if len(uploaded_face_encodings) > 1:
#                 print("More than one face detected; skipping image.")
#                 continue

#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Initialize variables to track closest match
#             closest_distance = float("inf")
#             matched_user = None
#             matched_guest = None

#             # Match against user faces
#             for user, stored_face_encoding in user_faces:
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = user
#                     matched_guest = None  # Clear guest match if user is found

#             # Match against guest faces
#             for guest, stored_face_encoding in guest_faces:
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = None  # Clear user match if guest is found
#                     matched_guest = guest

#             # Attendance and response handling
#             if closest_distance < 0.6:  # Adjust threshold as needed
#                 now = timezone.now()
#                 if matched_user:
#                     matched_users.append({
#                         'user_id': str(matched_user.id),
#                         'employee_id': str(matched_user.employee_code),
#                         'full_name': matched_user.name,
#                         'access': ""
#                     })
#                     attendance, created = Attendance.objects.get_or_create(
#                         user=matched_user,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()
#                     open_door_async()

#                 elif matched_guest:
#                     matched_users.append({
#                         'user_id': str(matched_guest.id),
#                         'employee_id': str(0),
#                         'full_name': matched_guest.name,
#                         'access': ""
#                     })
#                     attendance, created = Attendance.objects.get_or_create(
#                         guest=matched_guest,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()
#                     open_door_async()

#         # Check if any users were matched
#         if not matched_users:
#             print("No recognized face")
#             return JsonResponse({'error': 'user not found'}, status=200)

#         total_time = time.time() - start_time
#         print(f"Total process time: {total_time:.4f} seconds")
#         return JsonResponse({'matched_users': matched_users}, status=200)

#     except Exception as e:
#         error_time = time.time() - start_time
#         print(f"Error occurred after {error_time:.4f} seconds: {str(e)}")
#         return JsonResponse({"error": str(e)}, status=500)










# @csrf_exempt
# def match_face(request):
#     global imgcount
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=405)
    
#     def preprocess_image(photo):
#         """Preprocesses an image to enhance contrast, convert to grayscale, and resize."""
#         preprocess_start = time.time()
#         image = Image.open(photo)
        
#         # Print original image dimensions
#         print(f"Original image dimensions: {image.size}")
        
#         image = image.rotate(270, expand=True)

#         # Enhance contrast
#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(2.0)

#         # Convert to grayscale
#         image = image.convert("L")

#         # Resize image
#         image.thumbnail((200, 200), Image.Resampling.LANCZOS)

#         # Print processed image dimensions
#         print(f"Processed image dimensions: {image.size}")

#         # Save to buffer
#         buffered = BytesIO()
#         image.save(buffered, format='JPEG')

#         preprocess_end = time.time()
#         print(f"Image preprocessing took {preprocess_end - preprocess_start:.4f} seconds")
#         return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

#     start_time = time.time()
#     images = request.FILES.getlist('images')
#     matched_users = []

#     if not images:
#         print("No photo uploaded")
#         return JsonResponse({"error": "Images are required for face matching."}, status=400)

#     print(f"{len(images)} photo(s) uploaded")

#     try:
#         print("Face recognition started")
#         # Load all user and guest face encodings into memory once
#         user_faces = [(face.user, np.array(eval(face.face_enc))) for face in Face.objects.filter(user__isnull=False)]
#         guest_faces = [(face.guest, np.array(eval(face.face_enc))) for face in Face.objects.filter(guest__isnull=False)]

#         for photo in images:
#             # Preprocess the image
#             image = preprocess_image(photo)  # Call the nested preprocess function
            
#             # Perform face encoding on the preprocessed image
#             uploaded_face_encodings = face_recognition.face_encodings(image)

#             if not uploaded_face_encodings:
#                 continue  # Skip images with no detectable face

#             # Ensure only one face is processed per image
#             if len(uploaded_face_encodings) > 1:
#                 print("More than one face detected; skipping image.")
#                 continue

#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Initialize variables to track closest match
#             closest_distance = float("inf")
#             matched_user = None
#             matched_guest = None

#             # Match against user faces
#             for user, stored_face_encoding in user_faces:
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = user
#                     matched_guest = None  # Clear guest match if user is found

#             # Match against guest faces
#             for guest, stored_face_encoding in guest_faces:
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = None  # Clear user match if guest is found
#                     matched_guest = guest

#             # Attendance and response handling
#             if closest_distance < 0.6:  # Adjust threshold as needed
#                 now = timezone.now()
#                 if matched_user:
#                     matched_users.append({
#                         'user_id': str(matched_user.id),
#                         'employee_id': str(matched_user.employee_code),
#                         'full_name': matched_user.name,
#                         'access': ""
#                     })
#                     attendance, created = Attendance.objects.get_or_create(
#                         user=matched_user,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()
#                     open_door_async()

#                 elif matched_guest:
#                     matched_users.append({
#                         'user_id': str(matched_guest.id),
#                         'employee_id': str(0),
#                         'full_name': matched_guest.name,
#                         'access': ""
#                     })
#                     attendance, created = Attendance.objects.get_or_create(
#                         guest=matched_guest,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()
#                     open_door_async()

#         # Check if any users were matched
#         if not matched_users:
#             print("No recognized face")
#             return JsonResponse({'error': 'user not found'}, status=200)

#         total_time = time.time() - start_time
#         print(f"Total process time: {total_time:.4f} seconds")
#         return JsonResponse({'matched_users': matched_users}, status=200)

#     except Exception as e:
#         error_time = time.time() - start_time
#         print(f"Error occurred after {error_time:.4f} seconds: {str(e)}")
#         return JsonResponse({"error": str(e)}, status=500)

###Update 8th Jan
@csrf_exempt
def match_face(request):
    global imgcount
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    def preprocess_image(photo):
        """Preprocesses an image to enhance contrast, convert to grayscale, and resize."""
        preprocess_start = time.time()
        image = Image.open(photo)

        # Print original image dimensions
        print(f"Original image dimensions: {image.size}")
        
        image = image.rotate(270, expand=True)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # Convert to grayscale
        image = image.convert("L")

        # Resize image
        image.thumbnail((200, 200), Image.Resampling.LANCZOS)

        # Print processed image dimensions
        print(f"Processed image dimensions: {image.size}")

        # Save to buffer
        buffered = BytesIO()
        image.save(buffered, format='JPEG')

        preprocess_end = time.time()
        print(f"Image preprocessing took {preprocess_end - preprocess_start:.4f} seconds")
        return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

    start_time = time.time()
    images = request.FILES.getlist('images')
    matched_users = []

    if not images:
        print("No photo uploaded")
        return JsonResponse({"error": "Images are required for face matching."}, status=400)

    print(f"{len(images)} photo(s) uploaded")

    try:
        print("Face recognition started")
        # Load all user and guest face encodings into memory once
        user_faces = [(face.user, np.array(eval(face.face_enc))) for face in Face.objects.filter(user__isnull=False)]
        guest_faces = [(face.guest, np.array(eval(face.face_enc))) for face in Face.objects.filter(guest__isnull=False)]

        for photo in images:
            # Preprocess the image
            image = preprocess_image(photo)  # Call the nested preprocess function
            
            # Perform face encoding on the preprocessed image
            uploaded_face_encodings = face_recognition.face_encodings(image)
            uploaded_face_locations = face_recognition.face_locations(image)

            # Extract bounding box coordinates in the required format
            bounding_boxes = [
                [(top, right), (bottom, left)]
                for top, right, bottom, left in uploaded_face_locations
            ]

            # Print the bounding box coordinates
            print("Bounding Box Coordinates: ", bounding_boxes)

            # Check if multiple faces are detected
            if len(uploaded_face_encodings) > 1:
                print("More than one face detected; skipping image.")
                
                # Send messages to the app indicating multiple faces were detected
                return JsonResponse({
                    'error': 'Multiple faces detected, please focus on one face.',
                    'messages': [
                        "Multiple faces detected. Please focus on one face.",
                        "Ensure that the face is centered in the frame.",
                        "We can only recognize one face at a time, please try again."
                    ]
                }, status=400)

            # If no faces detected, continue
            if not uploaded_face_encodings:
                continue  # Skip images with no detectable face

            uploaded_face_encoding = uploaded_face_encodings[0]

            # Initialize variables to track closest match
            closest_distance = float("inf")
            matched_user = None
            matched_guest = None

            # Match against user faces
            for user, stored_face_encoding in user_faces:
                distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
                if distance < closest_distance:
                    closest_distance = distance
                    matched_user = user
                    matched_guest = None  # Clear guest match if user is found

            # Match against guest faces
            for guest, stored_face_encoding in guest_faces:
                distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
                if distance < closest_distance:
                    closest_distance = distance
                    matched_user = None  # Clear user match if guest is found
                    matched_guest = guest

            # Attendance and response handling
            if closest_distance < 0.55:  # Adjust threshold as needed
                now = timezone.now()
                if matched_user:
                    matched_users.append({
                        'user_id': str(matched_user.id),
                        'employee_id': str(matched_user.employee_code),
                        'full_name': matched_user.name,
                        'access': "",
                        'bounding_boxes': bounding_boxes  # Add bounding boxes to response
                    })
                    attendance, created = Attendance.objects.get_or_create(
                        user=matched_user,
                        in_time__date=now.date(),
                        defaults={'in_time': now}
                    )
                    if not created:
                        attendance.out_time = now
                        attendance.save()
                    open_door_async()

                elif matched_guest:
                    matched_users.append({
                        'user_id': str(matched_guest.id),
                        'employee_id': str(0),
                        'full_name': matched_guest.name,
                        'access': "",
                        'bounding_boxes': bounding_boxes  # Add bounding boxes to response
                    })
                    attendance, created = Attendance.objects.get_or_create(
                        guest=matched_guest,
                        in_time__date=now.date(),
                        defaults={'in_time': now}
                    )
                    if not created:
                        attendance.out_time = now
                        attendance.save()
                    open_door_async()

        # Check if any users were matched
        if not matched_users:
            print("No recognized face")
            return JsonResponse({'error': 'user not found'}, status=200)

        total_time = time.time() - start_time
        print(f"Total process time: {total_time:.4f} seconds")
        return JsonResponse({'matched_users': matched_users}, status=200)

    except Exception as e:
        error_time = time.time() - start_time
        print(f"Error occurred after {error_time:.4f} seconds: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)




# # #########bounding box
# from PIL import Image, ImageDraw, ImageEnhance


# @csrf_exempt
# def match_face(request):
#     global imgcount
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

#     def preprocess_image(photo):
#         """Preprocesses an image to enhance contrast, convert to grayscale, and resize."""
#         preprocess_start = time.time()
#         image = Image.open(photo)

#         # Print original image dimensions
#         print(f"Original image dimensions: {image.size}")

#         # Resize to reduce dimensions while maintaining aspect ratio
#         reduced_size = (640, 640)  # Target dimensions
#         image.thumbnail(reduced_size, Image.Resampling.LANCZOS)

#         # Print dimensions after reduction
#         print(f"Reduced image dimensions: {image.size}")

#         # Rotate the image if needed
#         image = image.rotate(270, expand=True)

#         # Enhance contrast
#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(2.0)

#         # Convert to grayscale
#         image = image.convert("RGB")

#         # Detect faces in the image
#         image_np = np.array(image)
#         face_locations = face_recognition.face_locations(image_np)

#         # Draw bounding boxes around detected faces
#         draw = ImageDraw.Draw(image)
#         for (top, right, bottom, left) in face_locations:
#             draw.rectangle([left, top, right, bottom], outline="green", width=5)

#         # Print processed image dimensions
#         print(f"Processed image dimensions: {image.size}")

#         # Save to buffer
#         buffered = BytesIO()
#         image.save(buffered, format='JPEG')

#         preprocess_end = time.time()
#         print(f"Image preprocessing took {preprocess_end - preprocess_start:.4f} seconds")
#         return face_recognition.load_image_file(BytesIO(buffered.getvalue()))

#     start_time = time.time()
#     images = request.FILES.getlist('images')
#     matched_users = []

#     if not images:
#         print("No photo uploaded")
#         return JsonResponse({"error": "Images are required for face matching."}, status=400)

#     print(f"{len(images)} photo(s) uploaded")

#     try:
#         print("Face recognition started")
#         # Load all user and guest face encodings into memory once
#         user_faces = [(face.user, np.array(eval(face.face_enc))) for face in Face.objects.filter(user__isnull=False)]
#         guest_faces = [(face.guest, np.array(eval(face.face_enc))) for face in Face.objects.filter(guest__isnull=False)]

#         for photo in images:
#             # Preprocess the image and draw bounding box
#             image = preprocess_image(photo)  # Call the nested preprocess function

#             # Perform face encoding on the preprocessed image
#             encoding_start = time.time()
#             uploaded_face_encodings = face_recognition.face_encodings(image)
#             encoding_end = time.time()
#             print(f"Face encoding took {encoding_end - encoding_start:.4f} seconds")

#             if not uploaded_face_encodings:
#                 print("No face detected in the image.")
#                 continue  # Skip images with no detectable face

#             # Ensure only one face is processed per image
#             if len(uploaded_face_encodings) > 1:
#                 print("More than one face detected; skipping image.")
#                 continue

#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Initialize variables to track closest match
#             closest_distance = float("inf")
#             matched_user = None
#             matched_guest = None

#             # Match against user faces
#             matching_start = time.time()
#             for user, stored_face_encoding in user_faces:
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = user
#                     matched_guest = None  # Clear guest match if user is found

#             # Match against guest faces
#             for guest, stored_face_encoding in guest_faces:
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = None  # Clear user match if guest is found
#                     matched_guest = guest
#             matching_end = time.time()
#             print(f"Face matching took {matching_end - matching_start:.4f} seconds")

#             # Attendance and response handling
#             if closest_distance < 0.6:  # Adjust threshold as needed
#                 now = timezone.now()
#                 if matched_user:
#                     matched_users.append({
#                         'user_id': str(matched_user.id),
#                         'employee_id': str(matched_user.employee_code),
#                         'full_name': matched_user.name,
#                         'access': ""
#                     })
#                     attendance, created = Attendance.objects.get_or_create(
#                         user=matched_user,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()
#                     open_door_async()

#                 elif matched_guest:
#                     matched_users.append({
#                         'user_id': str(matched_guest.id),
#                         'employee_id': str(0),
#                         'full_name': matched_guest.name,
#                         'access': ""
#                     })
#                     attendance, created = Attendance.objects.get_or_create(
#                         guest=matched_guest,
#                         in_time__date=now.date(),
#                         defaults={'in_time': now}
#                     )
#                     if not created:
#                         attendance.out_time = now
#                         attendance.save()
#                     open_door_async()

#         # Check if any users were matched
#         if not matched_users:
#             print("No recognized face")
#             return JsonResponse({'error': 'user not found'}, status=200)

#         total_time = time.time() - start_time
#         print(f"Total process time: {total_time:.4f} seconds")
#         return JsonResponse({'matched_users': matched_users}, status=200)

#     except Exception as e:
#         error_time = time.time() - start_time
#         print(f"Error occurred after {error_time:.4f} seconds: {str(e)}")
#         return JsonResponse({"error": str(e)}, status=500)




from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from django.shortcuts import render
from django.utils import timezone
import calendar
from datetime import timedelta
from .models import Attendance, User

# Helper function to check user authorization based on role
def is_authorized_user(user):
    return user.is_authenticated and user.role in ['hr', 'superadmin', 'accounts']

# Utility function to get attendance reports
def get_attendance_report(period, year=None, month=None):
    if period == 'daily':
        return Attendance.generate_daily_report()
    elif period == 'weekly':
        start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
        return Attendance.generate_weekly_report(start_date=start_of_week)
    elif period == 'monthly':
        return Attendance.objects.filter(in_time__year=year, in_time__month=month)
    return Attendance.objects.all()

# Function to calculate monthly summary of attendances
def calculate_monthly_summary(attendances):
    total_ontime = attendances.filter(status='ontime').count()
    total_absent = attendances.filter(status='absent').count()
    total_late = attendances.filter(status='late').count()
    
    user_time_summary = {}
    guest_time_summary = {}

    for attendance in attendances:
        time_spent = time_spent_to_timedelta(attendance.time_spent)

        if attendance.user:
            user_time_summary[attendance.user] = user_time_summary.get(attendance.user, timedelta(0)) + time_spent
        elif attendance.guest:
            guest_time_summary[attendance.guest] = guest_time_summary.get(attendance.guest, timedelta(0)) + time_spent

    return {
        'total_ontime': total_ontime,
        'total_absent': total_absent,
        'total_late': total_late,
        'user_time_summary': user_time_summary,
        'guest_time_summary': guest_time_summary,
    }

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_authorized_user), name='dispatch')
class AttendanceReportView(View):
    def get(self, request):
        period = request.GET.get('period', 'daily')
        month = request.GET.get('month', None)
        year = request.GET.get('year', None)

        now = timezone.now()
        month = int(month) if month else now.month
        year = int(year) if year else now.year

        attendances = get_attendance_report(period, year=year, month=month)

        monthly_summary = {}
        guest_monthly_summary = {}
        if period == 'monthly':
            monthly_summary = calculate_monthly_summary(attendances)
            guest_monthly_summary = monthly_summary.get('guest_time_summary', {})

        user_attendance = attendances.filter(user__isnull=False).order_by('in_time')
        guest_attendance = attendances.filter(guest__isnull=False).order_by('in_time')

        month_name = calendar.month_name[month]

        context = {
            'attendances': attendances,
            'monthly_summary': monthly_summary,
            'user_attendance': user_attendance,
            'guest_attendance': guest_attendance,
            'guest_monthly_summary': guest_monthly_summary,
            'period': period,
            'month': month_name,
            'year': year,
        }

        return render(request, 'attendance_report.html', context)

# Attendance api


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import user_passes_test
# from django.utils import timezone
# from datetime import timedelta
# import calendar
# from .models import Attendance  # Replace with the actual import for Attendance model
#  # Replace with the actual utility function import


# # Helper function to check user authorization based on role
# def is_authorized_user(user):
#     return user.is_authenticated and user.role in ['hr', 'superadmin', 'accounts']


# # API View for Attendance Report
# class AttendanceReportAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @method_decorator(user_passes_test(is_authorized_user))
#     def get(self, request):
#         period = request.query_params.get('period', 'daily')
#         month = request.query_params.get('month', None)
#         year = request.query_params.get('year', None)

#         now = timezone.now()
#         month = int(month) if month else now.month
#         year = int(year) if year else now.year

#         attendances = get_attendance_report(period, year=year, month=month)

#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)
#             guest_monthly_summary = monthly_summary.get('guest_time_summary', {})
#         else:
#             monthly_summary = {}
#             guest_monthly_summary = {}

#         user_attendance = attendances.filter(user__isnull=False).order_by('in_time')
#         guest_attendance = attendances.filter(guest__isnull=False).order_by('in_time')

#         month_name = calendar.month_name[month]

#         data = {
#             'attendances': list(attendances.values()),  # Serialize attendance queryset
#             'monthly_summary': monthly_summary,
#             'user_attendance': list(user_attendance.values()),  # Serialize user attendance queryset
#             'guest_attendance': list(guest_attendance.values()),  # Serialize guest attendance queryset
#             'guest_monthly_summary': guest_monthly_summary,
#             'period': period,
#             'month': month_name,
#             'year': year,
#         }

#         return Response(data)


# # Utility function to get attendance reports
# def get_attendance_report(period, year=None, month=None):
#     if period == 'daily':
#         return Attendance.generate_daily_report()
#     elif period == 'weekly':
#         start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
#         return Attendance.generate_weekly_report(start_date=start_of_week)
#     elif period == 'monthly':
#         return Attendance.objects.filter(in_time__year=year, in_time__month=month)
#     return Attendance.objects.all()


# # Function to calculate monthly summary of attendances
# def calculate_monthly_summary(attendances):
#     total_ontime = attendances.filter(status='ontime').count()
#     total_absent = attendances.filter(status='absent').count()
#     total_late = attendances.filter(status='late').count()

#     user_time_summary = {}
#     guest_time_summary = {}

#     for attendance in attendances:
#         time_spent = time_spent_to_timedelta(attendance.time_spent)

#         if attendance.user:
#             user_time_summary[attendance.user] = user_time_summary.get(attendance.user, timedelta(0)) + time_spent
#         elif attendance.guest:
#             guest_time_summary[attendance.guest] = guest_time_summary.get(attendance.guest, timedelta(0)) + time_spent

#     return {
#         'total_ontime': total_ontime,
#         'total_absent': total_absent,
#         'total_late': total_late,
#         'user_time_summary': user_time_summary,
#         'guest_time_summary': guest_time_summary,
#     }

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.exceptions import PermissionDenied
# from django.utils import timezone
# from datetime import timedelta
# import calendar
# from .models import Attendance  # Replace with actual import


# # Helper function to check user authorization based on role
# def is_authorized_user(user):
#     return user.is_authenticated and user.role in ['hr', 'superadmin', 'accounts']


# # API View for Attendance Report
# class AttendanceReportAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Check user authorization
#         if not is_authorized_user(request.user):
#             raise PermissionDenied("You do not have permission to access this resource.")

#         # Extract query parameters
#         period = request.query_params.get('period', 'daily')
#         month = request.query_params.get('month', None)
#         year = request.query_params.get('year', None)

#         now = timezone.now()
#         month = int(month) if month else now.month
#         year = int(year) if year else now.year

#         # Fetch attendance data
#         attendances = get_attendance_report(period, year=year, month=month)

#         # Process monthly summary if required
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)
#             guest_monthly_summary = {
#                 str(guest): str(time) for guest, time in monthly_summary.get('guest_time_summary', {}).items()
#             }
#         else:
#             monthly_summary = {}
#             guest_monthly_summary = {}

#         # Prepare serialized data
#         user_attendance = list(attendances.filter(user__isnull=False).values())
#         guest_attendance = list(attendances.filter(guest__isnull=False).values())

#         month_name = calendar.month_name[month]

#         # Response data
#         data = {
#             'attendances': list(attendances.values()),  # Serialize attendance queryset
#             'monthly_summary': {
#                 'total_ontime': monthly_summary.get('total_ontime', 0),
#                 'total_absent': monthly_summary.get('total_absent', 0),
#                 'total_late': monthly_summary.get('total_late', 0),
#                 'user_time_summary': {
#                     str(user): str(time) for user, time in monthly_summary.get('user_time_summary', {}).items()
#                 },
#                 'guest_time_summary': guest_monthly_summary,
#             },
#             'user_attendance': user_attendance,
#             'guest_attendance': guest_attendance,
#             'period': period,
#             'month': month_name,
#             'year': year,
#         }

#         return Response(data)


# # Utility function to get attendance reports
# def get_attendance_report(period, year=None, month=None):
#     if period == 'daily':
#         return Attendance.generate_daily_report()
#     elif period == 'weekly':
#         start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
#         return Attendance.generate_weekly_report(start_date=start_of_week)
#     elif period == 'monthly':
#         return Attendance.objects.filter(in_time__year=year, in_time__month=month)
#     return Attendance.objects.all()


# # Function to calculate monthly summary of attendances
# def calculate_monthly_summary(attendances):
#     total_ontime = attendances.filter(status='ontime').count()
#     total_absent = attendances.filter(status='absent').count()
#     total_late = attendances.filter(status='late').count()

#     user_time_summary = {}
#     guest_time_summary = {}

#     for attendance in attendances:
#         time_spent = time_spent_to_timedelta(attendance.time_spent)

#         if attendance.user:
#             user_time_summary[attendance.user] = user_time_summary.get(attendance.user, timedelta(0)) + time_spent
#         elif attendance.guest:
#             guest_time_summary[attendance.guest] = guest_time_summary.get(attendance.guest, timedelta(0)) + time_spent

#     return {
#         'total_ontime': total_ontime,
#         'total_absent': total_absent,
#         'total_late': total_late,
#         'user_time_summary': user_time_summary,
#         'guest_time_summary': guest_time_summary,
#     }
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
import calendar
import pytz
from .models import Attendance  # Replace with actual import


# Helper function to convert datetime to IST
def convert_to_ist(dt):
    if dt and timezone.is_aware(dt):
        ist = pytz.timezone('Asia/Kolkata')
        return dt.astimezone(ist)
    return dt  # Return as is if it's not a datetime or already in the desired format


# Helper function to check user authorization based on role
def is_authorized_user(user):
    return user.is_authenticated and user.role in ['hr', 'superadmin', 'accounts']


# API View for Attendance Report
# class AttendanceReportAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Check user authorization
#         if not is_authorized_user(request.user):
#             raise PermissionDenied("You do not have permission to access this resource.")

#         # Extract query parameters
#         period = request.query_params.get('period', 'daily')
#         month = request.query_params.get('month', None)
#         year = request.query_params.get('year', None)

#         now = timezone.now()
#         month = int(month) if month else now.month
#         year = int(year) if year else now.year

#         # Fetch attendance data
#         attendances = get_attendance_report(period, year=year, month=month)

#         # Process monthly summary if required
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)
#             guest_monthly_summary = {
#                 str(guest): str(time) for guest, time in monthly_summary.get('guest_time_summary', {}).items()
#             }
#         else:
#             monthly_summary = {}
#             guest_monthly_summary = {}

#         # Prepare serialized data with IST conversion
#         user_attendance = [
#             {
#                 **entry,
#                 'in_time': convert_to_ist(entry['in_time']),
#                 'out_time': convert_to_ist(entry['out_time']),
#             }
#             for entry in attendances.filter(user__isnull=False).values()
#         ]
#         guest_attendance = [
#             {
#                 **entry,
#                 'in_time': convert_to_ist(entry['in_time']),
#                 'out_time': convert_to_ist(entry['out_time']),
#             }
#             for entry in attendances.filter(guest__isnull=False).values()
#         ]

#         month_name = calendar.month_name[month]

#         # Response data
#         data = {
#             'attendances': [
#                 {
#                     **entry,
#                     'in_time': convert_to_ist(entry['in_time']),
#                     'out_time': convert_to_ist(entry['out_time']),
#                 }
#                 for entry in attendances.values()
#             ],  # Serialize attendance queryset with IST
#             'monthly_summary': {
#                 'total_ontime': monthly_summary.get('total_ontime', 0),
#                 'total_absent': monthly_summary.get('total_absent', 0),
#                 'total_late': monthly_summary.get('total_late', 0),
#                 'user_time_summary': {
#                     str(user): str(time) for user, time in monthly_summary.get('user_time_summary', {}).items()
#                 },
#                 'guest_time_summary': guest_monthly_summary,
#             },
#             'user_attendance': user_attendance,
#             'guest_attendance': guest_attendance,
#             'period': period,
#             'month': month_name,
#             'year': year,
#         }

#         return Response(data)
# class AttendanceReportAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Check user authorization
#         if not is_authorized_user(request.user):
#             raise PermissionDenied("You do not have permission to access this resource.")

#         # Extract query parameters
#         period = request.query_params.get('period', 'daily')
#         month = request.query_params.get('month', None)
#         year = request.query_params.get('year', None)

#         now = timezone.now()
#         month = int(month) if month else now.month
#         year = int(year) if year else now.year

#         # Fetch attendance data
#         attendances = get_attendance_report(period, year=year, month=month)

#         # Process monthly summary if required
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)
#             guest_monthly_summary = {
#                 str(guest): str(time) for guest, time in monthly_summary.get('guest_time_summary', {}).items()
#             }
#         else:
#             monthly_summary = {}
#             guest_monthly_summary = {}

#         # Separate attendances for users and guests with IST conversion
#         user_attendance = [
#             {
#                 **entry,
#                 'in_time': convert_to_ist(entry['in_time']),
#                 'out_time': convert_to_ist(entry['out_time']),
#             }
#             for entry in attendances.filter(user__isnull=False).values()
#         ]
#         guest_attendance = [
#             {
#                 **entry,
#                 'in_time': convert_to_ist(entry['in_time']),
#                 'out_time': convert_to_ist(entry['out_time']),
#             }
#             for entry in attendances.filter(guest__isnull=False).values()
#         ]

#         month_name = calendar.month_name[month]

#         # Response data (remove or refine `attendances` key)
#         data = {
#             # Include only `user_attendance` and `guest_attendance` if needed
#             'user_attendance': user_attendance,
#             'guest_attendance': guest_attendance,
#             'monthly_summary': {
#                 'total_ontime': monthly_summary.get('total_ontime', 0),
#                 'total_absent': monthly_summary.get('total_absent', 0),
#                 'total_late': monthly_summary.get('total_late', 0),
#                 'user_time_summary': {
#                     str(user): str(time) for user, time in monthly_summary.get('user_time_summary', {}).items()
#                 },
#                 'guest_time_summary': guest_monthly_summary,
#             },
#             'period': period,
#             'month': month_name,
#             'year': year,
#         }

#         return Response(data)

##### separate attendance for user and guest
from django.db.models import Q

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserAttendanceReportAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        if not is_authorized_user(request.user):
            raise PermissionDenied()

        period = request.query_params.get('period', 'daily')
        month = request.query_params.get('month', None)
        year = request.query_params.get('year', None)
        search_query = request.query_params.get('search', '')
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        now = timezone.now()
        month = int(month) if month else now.month
        year = int(year) if year else now.year

        # Get base attendance data
        attendances = get_attendance_report(period, year=year, month=month)
        user_attendances = attendances.filter(user__isnull=False)

        # Apply search
        if search_query:
            user_attendances = user_attendances.filter(
                Q(user__name__icontains=search_query) |
                Q(user__employee_code__icontains=search_query)
            )

        # Calculate summary
        if period == 'monthly':
            monthly_summary = calculate_monthly_summary(user_attendances)
        else:
            monthly_summary = {}

        # Convert queryset to a list of dictionaries
        user_attendance_list = list(user_attendances.values())

        # Pagination
        paginator = Paginator(user_attendance_list, page_size)
        current_page = paginator.get_page(page)

        # Format attendance data
        user_attendance = [
            {
                **entry,
                'in_time': convert_to_ist(entry['in_time']),
                'out_time': convert_to_ist(entry['out_time']),
            }
            for entry in current_page.object_list
        ]

        response_data = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page),
            'user_attendance': user_attendance,
            'monthly_summary': {
                'total_ontime': monthly_summary.get('total_ontime', 0),
                'total_absent': monthly_summary.get('total_absent', 0),
                'total_late': monthly_summary.get('total_late', 0),
                'user_time_summary': {
                    str(user): str(time) for user, time in monthly_summary.get('user_time_summary', {}).items()
                }
            },
            'period': period,
            'month': calendar.month_name[month],
            'year': year,
        }

        return Response(response_data)


# class GuestAttendanceReportAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPagination

#     def get(self, request):
#         if not is_authorized_user(request.user):
#             raise PermissionDenied()

#         period = request.query_params.get('period', 'daily')
#         month = request.query_params.get('month', None)
#         year = request.query_params.get('year', None)
#         search_query = request.query_params.get('search', '')
#         page = request.query_params.get('page', 1)
#         page_size = request.query_params.get('page_size', 10)

#         now = timezone.now()
#         month = int(month) if month else now.month
#         year = int(year) if year else now.year

#         # Get base attendance data
#         attendances = get_attendance_report(period, year=year, month=month)
#         guest_attendances = attendances.filter(guest__isnull=False)

#         # Apply search
#         if search_query:
#             guest_attendances = guest_attendances.filter(
#                 Q(guest__name__icontains=search_query) |
#                 Q(guest__phone__icontains=search_query)
#             )

#         # Calculate summary
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(guest_attendances)
#             guest_monthly_summary = {
#                 str(guest): str(time) for guest, time in monthly_summary.get('guest_time_summary', {}).items()
#             }
#         else:
#             monthly_summary = {}
#             guest_monthly_summary = {}

#         # Pagination
#         paginator = Paginator(guest_attendances, page_size)
#         current_page = paginator.get_page(page)

#         # Format attendance data
#         guest_attendance = [
#             {
#                 **entry,
#                 'in_time': convert_to_ist(entry['in_time']),
#                 'out_time': convert_to_ist(entry['out_time']),
#             }
#             for entry in current_page.object_list.values()
#         ]

#         response_data = {
#             'count': paginator.count,
#             'total_pages': paginator.num_pages,
#             'current_page': int(page),
#             'guest_attendance': guest_attendance,
#             'monthly_summary': {
#                 'guest_time_summary': guest_monthly_summary
#             },
#             'period': period,
#             'month': calendar.month_name[month],
#             'year': year,
#         }

#         return Response(response_data)
class GuestAttendanceReportAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        if not is_authorized_user(request.user):
            raise PermissionDenied()

        period = request.query_params.get('period', 'daily')
        month = request.query_params.get('month', None)
        year = request.query_params.get('year', None)
        search_query = request.query_params.get('search', '')
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        now = timezone.now()
        month = int(month) if month else now.month
        year = int(year) if year else now.year

        # Get base attendance data
        attendances = get_attendance_report(period, year=year, month=month)
        guest_attendances = attendances.filter(guest__isnull=False)

        # Apply search
        if search_query:
            guest_attendances = guest_attendances.filter(
                Q(guest__name__icontains=search_query) |
                Q(guest__phone__icontains=search_query)
            )

        # Calculate summary
        if period == 'monthly':
            monthly_summary = calculate_monthly_summary(guest_attendances)
            guest_monthly_summary = {
                str(guest): str(time) for guest, time in monthly_summary.get('guest_time_summary', {}).items()
            }
        else:
            monthly_summary = {}
            guest_monthly_summary = {}

        # Convert queryset to a list of dictionaries
        guest_attendance_list = list(guest_attendances.values())

        # Pagination
        paginator = Paginator(guest_attendance_list, page_size)
        current_page = paginator.get_page(page)

        # Format attendance data
        guest_attendance = [
            {
                **entry,
                'in_time': convert_to_ist(entry['in_time']),
                'out_time': convert_to_ist(entry['out_time']),
            }
            for entry in current_page.object_list
        ]

        response_data = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page),
            'guest_attendance': guest_attendance,
            'monthly_summary': {
                'guest_time_summary': guest_monthly_summary
            },
            'period': period,
            'month': calendar.month_name[month],
            'year': year,
        }

        return Response(response_data)


# Utility function to get attendance reports
def get_attendance_report(period, year=None, month=None):
    if period == 'daily':
        return Attendance.generate_daily_report()
    elif period == 'weekly':
        start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
        return Attendance.generate_weekly_report(start_date=start_of_week)
    elif period == 'monthly':
        return Attendance.objects.filter(in_time__year=year, in_time__month=month)
    return Attendance.objects.all()


# Function to calculate monthly summary of attendances
def calculate_monthly_summary(attendances):
    total_ontime = attendances.filter(status='ontime').count()
    total_absent = attendances.filter(status='absent').count()
    total_late = attendances.filter(status='late').count()

    user_time_summary = {}
    guest_time_summary = {}

    for attendance in attendances:
        time_spent = time_spent_to_timedelta(attendance.time_spent)

        if attendance.user:
            user_time_summary[attendance.user] = user_time_summary.get(attendance.user, timedelta(0)) + time_spent
        elif attendance.guest:
            guest_time_summary[attendance.guest] = guest_time_summary.get(attendance.guest, timedelta(0)) + time_spent

    return {
        'total_ontime': total_ontime,
        'total_absent': total_absent,
        'total_late': total_late,
        'user_time_summary': user_time_summary,
        'guest_time_summary': guest_time_summary,
    }

# def get_attendance_report(period, year=None, month=None):
#     if period == 'daily':
#         return Attendance.generate_daily_report()
#     elif period == 'weekly':
#         start_date = timezone.now() - timedelta(days=timezone.now().weekday())
#         return Attendance.generate_weekly_report(start_date=start_date)
#     elif period == 'monthly':
#         return Attendance.objects.filter(in_time__year=year, in_time__month=month)
#     return Attendance.objects.all()  # Default to all records
    
    
    






###########comment out


# def get_attendance_report(period, year=None, month=None):
#     if period == 'daily':
#         # Use the class method to fetch today's records
#         return Attendance.generate_daily_report()

#     elif period == 'weekly':
#         # Use the class method to fetch the current week's records
#         start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
#         return Attendance.generate_weekly_report(start_date=start_of_week)

#     elif period == 'monthly':
#         # Use the existing filter to fetch records for the specified month and year
#         return Attendance.objects.filter(in_time__year=year, in_time__month=month)

#     # Default to all records if no period matches
#     return Attendance.objects.all()







# def get_attendance_report(period, year=None, month=None):
#     now = timezone.now()

#     if period == 'daily':
#         # Fetch today's attendance only
#         return Attendance.objects.filter(in_time__date=now.date())

#     elif period == 'weekly':
#         # Calculate the start and end of the current week
#         start_of_week = now.date() - timedelta(days=now.weekday())  # Monday
#         end_of_week = start_of_week + timedelta(days=6)  # Sunday
#         return Attendance.objects.filter(in_time__date__range=(start_of_week, end_of_week))

#     elif period == 'monthly' and year and month:
#         # Fetch all attendances in the specified month and year
#         return Attendance.objects.filter(in_time__year=year, in_time__month=month)

#     # Default to all records if no specific period matches
#     return Attendance.objects.all()


# def calculate_monthly_summary(attendances):
#     total_ontime = attendances.filter(status='ontime').count()
#     total_absent = attendances.filter(status='absent').count()
#     total_late = attendances.filter(status='late').count()
#     # Calculate total time spent
#     user_time_summary = {}
#     for attendance in attendances:
#         if attendance.user not in user_time_summary:
#             user_time_summary[attendance.user] = timedelta(0)  # Initialize time spent for the user
#         # Convert time_spent from string to timedelta before summing
#         user_time_summary[attendance.user] += time_spent_to_timedelta(attendance.time_spent)
#     return {
#         'total_ontime': total_ontime,
#         'total_absent': total_absent,
#         'total_late': total_late,
#         'user_time_summary': user_time_summary
#     }




############comment out

# def calculate_monthly_summary(attendances):
#     total_ontime = attendances.filter(status='ontime').count()
#     total_absent = attendances.filter(status='absent').count()
#     total_late = attendances.filter(status='late').count()

#     # Separate summaries for users and guests
#     user_time_summary = {}
#     guest_time_summary = {}

#     for attendance in attendances:
#         time_spent = time_spent_to_timedelta(attendance.time_spent)

#         if attendance.user:
#             if attendance.user not in user_time_summary:
#                 user_time_summary[attendance.user] = timedelta(0)
#             user_time_summary[attendance.user] += time_spent
#         elif attendance.guest:
#             if attendance.guest not in guest_time_summary:
#                 guest_time_summary[attendance.guest] = timedelta(0)
#             guest_time_summary[attendance.guest] += time_spent

#     return {
#         'total_ontime': total_ontime,
#         'total_absent': total_absent,
#         'total_late': total_late,
#         'user_time_summary': user_time_summary,
#         'guest_time_summary': guest_time_summary,
#     }


# def is_hr_authenticated_by_employee_code(request):
#     employee_code = request.headers.get("Employee-Code")
#     if employee_code:
#         try:
#             # Verify HR user based on employee_code
#             hr_user = User.objects.get(employee_code=employee_code, role='hr')
#             request.user = hr_user
#             return True
#         except User.DoesNotExist:
#             return False
#     return False


# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_passes_test(lambda user: user.is_staff or is_hr_authenticated_by_employee_code), name='dispatch')
# class AttendanceReportView(View):
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         # Set month and year for all periods if not provided
#         now = timezone.now()
#         if month is None or year is None:
#             month = now.month
#             year = now.year
#         else:
#             month = int(month)
#             year = int(year)

#         # Fetch attendances based on the period
#         attendances = get_attendance_report(period, year=year, month=month)

#         # Prepare monthly summary if needed
#         monthly_summary = {}
#         guest_monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)
#             guest_monthly_summary = monthly_summary.get(
#                 'guest_time_summary', {})

#         # Filter user and guest attendance based on the period
#         if period in ['daily', 'weekly', 'monthly']:
#             user_attendance = attendances.filter(
#                 user__isnull=False).order_by('in_time')
#             guest_attendance = attendances.filter(
#                 guest__isnull=False).order_by('in_time')

#         # Convert month number to month name
#         month_name = calendar.month_name[month]

#         context = {
#             'attendances': attendances,
#             'monthly_summary': monthly_summary,
#             'user_attendance': user_attendance,
#             'guest_attendance': guest_attendance,
#             'guest_monthly_summary': guest_monthly_summary,
#             'period': period,
#             'month': month_name,
#             'year': year,
#         }

#         return render(request, 'attendance_report.html', context)




# from django.utils.decorators import method_decorator
# from django.views import View
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from django.utils import timezone
# import calendar

# def is_authorized_user(request):
#     employee_code = request.headers.get("Employee-Code")
#     if employee_code:
#         try:
#             # Verify user based on employee_code and allowed roles
#             authorized_user = User.objects.get(
#                 employee_code=employee_code,
#                 role__in=['hr', 'superadmin', 'accounts']
#             )
#             request.user = authorized_user
#             return True
#         except User.DoesNotExist:
#             return False
#     return False





#######comment out

# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_passes_test(lambda user: user.is_staff or is_authorized_user(user)), name='dispatch')
# class AttendanceReportView(View):
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         # Set month and year for all periods if not provided
#         now = timezone.now()
#         if month is None or year is None:
#             month = now.month
#             year = now.year
#         else:
#             month = int(month)
#             year = int(year)

#         # Fetch attendances based on the period
#         attendances = get_attendance_report(period, year=year, month=month)

#         # Prepare monthly summary if needed
#         monthly_summary = {}
#         guest_monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)
#             guest_monthly_summary = monthly_summary.get('guest_time_summary', {})

#         # Filter user and guest attendance based on the period
#         if period in ['daily', 'weekly', 'monthly']:
#             user_attendance = attendances.filter(user__isnull=False).order_by('in_time')
#             guest_attendance = attendances.filter(guest__isnull=False).order_by('in_time')

#         # Convert month number to month name
#         month_name = calendar.month_name[month]

#         context = {
#             'attendances': attendances,
#             'monthly_summary': monthly_summary,
#             'user_attendance': user_attendance,
#             'guest_attendance': guest_attendance,
#             'guest_monthly_summary': guest_monthly_summary,
#             'period': period,
#             'month': month_name,
#             'year': year,
#         }

#         return render(request, 'attendance_report.html', context)




# @method_decorator(login_required, name='dispatch')
# class GuestAttendanceReportView(View):
#     @method_decorator(user_passes_test(lambda user: user.is_staff or is_hr_authenticated_by_employee_code,
#                                          login_url='/login/'), name='dispatch')
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         now = timezone.now()
#         if month is None or year is None:
#             month = now.month
#             year = now.year
#         else:
#             month = int(month)
#             year = int(year)

#         attendances = get_attendance_report(period, year=year, month=month)

#         # Debugging: Check how many attendances are fetched
#         print(f"Fetched {attendances.count()} attendances for period: {period}")

#         guest_attendance = attendances.filter(guest__isnull=False).order_by('in_time')

#         monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(guest_attendance)

#         month_name = calendar.month_name[month]

#         context = {
#             'guest_attendance': guest_attendance,
#             'monthly_summary': monthly_summary,
#             'period': period,
#             'month': month_name,
#             'year': year,
#         }

#         return render(request, 'guest_attendance_report.html', context)

# @method_decorator(login_required, name='dispatch')
# class UserAttendanceReportView(View):
#     @method_decorator(user_passes_test(lambda user: user.role in ['superadmin', 'hr', 'accounts'],
#                                          login_url='/login/'), name='dispatch')
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         now = timezone.now()
#         # today = timezone.now().date()

#         if month is None or year is None:
#             month = now.month
#             year = now.year
#         else:
#             month = int(month)
#             year = int(year)

#         attendances = get_attendance_report(period, year=year, month=month)
#         user_attendance = attendances.filter(user__isnull=False).order_by('in_time')

#         monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(user_attendance)

#         month_name = calendar.month_name[month]

#         # user_attendance = Attendance.objects.filter(user=request.user, in_time__date=today)

#         # Debugging: Check if user attendance records exist
#         context = {
#             'user_attendance': user_attendance,
#             'monthly_summary': monthly_summary,
#             'period': period,
#             'month': month_name,
#             'year': year,
#         }
#         return render(request, 'user_attendance_report.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_holiday_list(request):
    if request.user.role == 'hr':
        # Expecting a comma-separated string
        holiday_dates = request.data.get('holiday_dates')

        # Split the dates and validate
        date_list = [date.strip() for date in holiday_dates.split(',')]
        current_date = timezone.now()  # Get the current time in the timezone-aware format

        # Check for past dates and duplicates
        for date in date_list:
            # Convert each date to a timezone-aware datetime
            holiday_date = timezone.make_aware(
                datetime.strptime(date, '%Y-%m-%d'))
            if holiday_date < current_date:
                return Response({"error": "Past dates are not allowed."}, status=status.HTTP_400_BAD_REQUEST)

        if len(set(date_list)) < len(date_list):
            return Response({"error": "Duplicate dates are not allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the holiday list
        holiday = Holiday.objects.create(
            created_by=request.user,
            holiday_dates=holiday_dates,
        )
        return Response({"success": f"Holiday list created successfully with ID {holiday.id}"}, status=status.HTTP_201_CREATED)

    return Response({"error": "Unauthorized: Only HR can create holiday lists"}, status=status.HTTP_403_FORBIDDEN)

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes

@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def list_holidays(request):
    # Check permissions
    if not (request.user.is_superuser or request.user.role == 'hr'):
        return Response(
            {"error": "Unauthorized: Only HR and superadmin can view holiday lists"}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Get query parameters
    is_verified = request.query_params.get('verified')
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 10)

    # Get holidays
    holidays = Holiday.objects.all()

    # Filter by verification status
    if is_verified is not None:
        is_verified = is_verified.lower() == 'true'
        holidays = holidays.filter(is_verified=is_verified)

    # Apply pagination
    paginator = Paginator(holidays, page_size)
    current_page = paginator.get_page(page)

    # Format holiday data
    holiday_data = [
        {
            "id": holiday.id,
            "holiday_dates": holiday.holiday_dates,
            "created_by": holiday.created_by.name,
            "created_at": holiday.created_at,
            "is_verified": holiday.is_verified,
            # "verified_by": holiday.verified_by.name if holiday.verified_by else None,
            # "verified_at": holiday.verified_at
        }
        for holiday in current_page
    ]

    response_data = {
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'results': holiday_data
    }

    return Response(response_data, status=status.HTTP_200_OK)


# class CreateHolidayListTemplate(TemplateView):
#     template_name = 'create_holiday_list.html'

#     def post(self, request):
#         if request.user.role == 'hr':
#             holiday_dates = request.POST.getlist('holiday_dates', [])

#             date_list = [date.strip() for date in holiday_dates.split(',')]
#             current_date = timezone.now()

#             for date in date_list:
#                 holiday_date = timezone.make_aware(
#                     datetime.strptime(date, '%Y-%m-%d'))
#                 if holiday_date < current_date:
#                     return HttpResponse("error: Past dates are not allowed.", status=status.HTTP_400_BAD_REQUEST)

#             if len(set(date_list)) < len(date_list):
#                 return HttpResponse("error: Duplicate dates are not allowed.", status=status.HTTP_400_BAD_REQUEST)

#             holiday = Holiday.objects.create(
#                 created_by=request.user,
#                 holiday_dates=holiday_dates,
#             )
#             return HttpResponse(f"Success: Holiday list created successfully with ID {holiday.id}", status=status.HTTP_201_CREATED)

#         return HttpResponse("Unauthorized: Only HR can create holiday lists", status=status.HTTP_403_FORBIDDEN)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['holidays'] = Holiday.objects.all()
#         return context



from django.utils import timezone
from django.http import HttpResponse
from django.views.generic import TemplateView
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Holiday

# class CreateHolidayListTemplate(TemplateView):
#     template_name = 'holiday.html'

#     def post(self, request):
#         if request.user.role == 'hr':
#             # Retrieve the list of holiday dates
#             holiday_dates = request.POST.getlist('holiday_dates', [])  # Use getlist to retrieve an array

#             if not holiday_dates:
#                 return HttpResponse("No dates provided.", status=status.HTTP_400_BAD_REQUEST)

#             current_date = timezone.now()

#             # Validate each holiday date
#             for date in holiday_dates:
#                 try:
#                     holiday_date = timezone.make_aware(datetime.strptime(date, '%Y-%m-%d'))
#                 except ValueError:
#                     return HttpResponse(f"Invalid date format: {date}.", status=status.HTTP_400_BAD_REQUEST)

#                 if holiday_date < current_date:
#                     return HttpResponse("Error: Past dates are not allowed.", status=status.HTTP_400_BAD_REQUEST)

#             if len(set(holiday_dates)) < len(holiday_dates):
#                 return HttpResponse("Error: Duplicate dates are not allowed.", status=status.HTTP_400_BAD_REQUEST)

#             # Create the holiday list
#             holiday = Holiday.objects.create(
#                 created_by=request.user,
#                 holiday_dates=','.join(holiday_dates),  # Save dates as a comma-separated string
#             )
#             return HttpResponse(f"Success: Holiday list created successfully with ID {holiday.id}", status=status.HTTP_201_CREATED)

#         return HttpResponse("Unauthorized: Only HR can create holiday lists", status=status.HTTP_403_FORBIDDEN)

from django.utils import timezone
from datetime import datetime

# class CreateHolidayListTemplate(TemplateView):
#     template_name = 'holiday.html'

#     def post(self, request):
#         if request.user.role == 'hr':
#             # Retrieve the list of holiday dates
#             holiday_dates = request.POST.getlist('holiday_dates', [])  # Use getlist to retrieve an array

#             if not holiday_dates:
#                 return HttpResponse("No dates provided.", status=status.HTTP_400_BAD_REQUEST)

#             current_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

#             # Validate each holiday date
#             for date in holiday_dates:
#                 try:
#                     holiday_date = timezone.make_aware(datetime.strptime(date, '%Y-%m-%d'))
#                 except ValueError:
#                     return HttpResponse(f"Invalid date format: {date}.", status=status.HTTP_400_BAD_REQUEST)

#                 if holiday_date < current_date:
#                     return HttpResponse("Error: Past dates are not allowed.", status=status.HTTP_400_BAD_REQUEST)

#             if len(set(holiday_dates)) < len(holiday_dates):
#                 return HttpResponse("Error: Duplicate dates are not allowed.", status=status.HTTP_400_BAD_REQUEST)

#             # Create the holiday list
#             holiday = Holiday.objects.create(
#                 created_by=request.user,
#                 holiday_dates=','.join(holiday_dates),  # Save dates as a comma-separated string
#             )
#             return HttpResponse(f"Success: Holiday list created successfully with ID {holiday.id}", status=status.HTTP_201_CREATED)

#         return HttpResponse("Unauthorized: Only HR can create holiday lists", status=status.HTTP_403_FORBIDDEN)


from django.utils import timezone
from datetime import datetime

class CreateHolidayListTemplate(TemplateView):
    template_name = 'holiday.html'

    def post(self, request):
        if request.user.role == 'hr':
            # Retrieve the list of holiday dates
            holiday_dates = request.POST.getlist('holiday_dates[]')  # Use getlist to retrieve an array

            if not holiday_dates:
                return HttpResponse("No dates provided.", status=status.HTTP_400_BAD_REQUEST)

            current_date = timezone.now().date()  # Get only the current date part

            # Validate each holiday date
            for date in holiday_dates:
                try:
                    holiday_date = datetime.strptime(date, '%Y-%m-%d').date()  # Parse and get only date part
                except ValueError:
                    return HttpResponse(f"Invalid date format: {date}.", status=status.HTTP_400_BAD_REQUEST)

                # Allow only today or future dates
                if holiday_date < current_date:
                    return HttpResponse("Error: Past dates are not allowed.", status=status.HTTP_400_BAD_REQUEST)

            if len(set(holiday_dates)) < len(holiday_dates):
                return HttpResponse("Error: Duplicate dates are not allowed.", status=status.HTTP_400_BAD_REQUEST)

            # Create the holiday list
            holiday = Holiday.objects.create(
                created_by=request.user,
                holiday_dates=','.join(holiday_dates),  # Save dates as a comma-separated string
            )
            return HttpResponse(f"Success: Holiday list created successfully with ID {holiday.id}", status=status.HTTP_201_CREATED)

        return HttpResponse("Unauthorized: Only HR can create holiday lists", status=status.HTTP_403_FORBIDDEN)



@api_view(['POST'])
@permission_classes([IsAdminUser])  # Only admins can access this view
def verify_holiday(request, holiday_id):
    try:
        holiday = Holiday.objects.get(id=holiday_id)

        # Set the holiday as verified
        holiday.is_verified = True
        holiday.save()

        return Response({"success": f"Holiday List with ID {holiday_id} has been verified."}, status=status.HTTP_200_OK)
    except Holiday.DoesNotExist:
        return Response({"error": "Holiday list not found."}, status=status.HTTP_404_NOT_FOUND)


class VerifyHolidayTemplate(View):
    def get(self, request, holiday_id):
        try:
            holiday = Holiday.objects.get(id=holiday_id)
            holiday.is_verified = True
            holiday.save()
            return HttpResponse(f"success: Holiday List with ID {holiday_id} has been verified.", status=status.HTTP_200_OK)
        except Holiday.DoesNotExist:
            return HttpResponse("error: Holiday list not found.", status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_shift(request):
    if request.user.role == 'hr':  # Ensure only HR can create shifts
        shift_name = request.data.get('shift_name')
        shift_start_time = request.data.get('shift_start_time')
        shift_end_time = request.data.get('shift_end_time')

        # Calculate total work time and break time
        total_work_time = (datetime.strptime(
            shift_end_time, "%H:%M") - datetime.strptime(shift_start_time, "%H:%M"))
        total_break_time = total_work_time / 8  # Example logic; adjust as needed

        # Create the shift
        shift = Shift.objects.create(
            shift_name=shift_name,
            shift_start_time=shift_start_time,
            shift_end_time=shift_end_time,
            total_work_time=total_work_time,
            total_break_time=total_break_time,
            created_by=request.user,
        )
        return Response({"success": f"Shift '{shift}' created successfully."}, status=status.HTTP_201_CREATED)

    return Response({"error": "Unauthorized: Only HR can create shifts."}, status=status.HTTP_403_FORBIDDEN)


class CreateShiftTemplate(TemplateView):
    template_name = 'shift.html'

    def post(self, request):
        if request.user.role == 'hr':
            shift_name = request.POST.get('shift_name')
            shift_start_time = request.POST.get('shift_start_time')
            shift_end_time = request.POST.get('shift_end_time')

            total_work_time = (datetime.strptime(
                shift_end_time, "%H:%M") - datetime.strptime(shift_start_time, "%H:%M"))
            total_break_time = total_work_time / 8

            shift = Shift.objects.create(
                shift_name=shift_name,
                shift_start_time=shift_start_time,
                shift_end_time=shift_end_time,
                total_work_time=total_work_time,
                total_break_time=total_break_time,
                created_by=request.user,
            )
            return HttpResponse(f"success: Shift '{shift}' created successfully.", status=status.HTTP_201_CREATED)

        return HttpResponse("Unauthorized: Only HR can create shifts.", status=status.HTTP_403_FORBIDDEN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shifts'] = Shift.objects.all()
        return context


# @api_view(['POST'])
# # Ensure only authenticated users can access
# @permission_classes([IsAuthenticated])
# def assign_shift(request):
#     # HR should authenticate using their role
#     if request.user.role != 'hr':
#         # Check if the user is a superuser (Super Admin)
#         if not request.user.is_superuser:
#             return Response({"error": "Unauthorized: Only HR or Super Admin can assign shifts."}, status=status.HTTP_403_FORBIDDEN)

#     # Retrieve data from the request
#     # Employee ID for the shift assignment
#     employee_code = request.data.get('employee_id')
#     shift_id = request.data.get('shift_id')
#     weekly_holiday = request.data.get('weekly_holiday')  # Expecting a list of days
#     government_holiday_applicable = request.data.get(
#         'government_holiday_applicable', False)
#     earned_leave_qty = request.data.get('earned_leave_qty', 0)
#     paid_leave_qty = request.data.get('paid_leave_qty', 0)
#     casual_leave_qty = request.data.get('casual_leave_qty', 0)
#     applicable_from = request.data.get('applicable_from')

#     # Validate weekly_holiday to ensure it's a list
#     if not isinstance(weekly_holiday, list) or not all(isinstance(day, str) for day in weekly_holiday):
#         return Response({"error": "Weekly holiday must be a list of valid days."}, status=400)

#     # Fetch the User object based on employee_id
#     employee = get_object_or_404(User, employee_code=employee_code)

#     # Fetch the Shift object based on shift_id
#     shift = get_object_or_404(Shift, id=shift_id)

#     # Create the EmployeeShiftAssignment object, including applicable_from
#     shift_assignment = EmployeeShiftAssignment.objects.create(
#         employee=employee,
#         shift=shift,
#         assigned_by=request.user,  # Assuming the request user is making the assignment
#         applicable_from=applicable_from  # Ensure this is included here
#     )

#     # Set weekly holiday
#     shift_assignment.set_weekly_holiday(weekly_holiday)

#     # Additional fields
#     shift_assignment.government_holiday_applicable = government_holiday_applicable
#     shift_assignment.earned_leave_qty = earned_leave_qty
#     shift_assignment.paid_leave_qty = paid_leave_qty
#     shift_assignment.casual_leave_qty = casual_leave_qty

#     # Save the shift assignment after setting all fields
#     shift_assignment.save()

#     return Response({"success": "Shift assigned successfully"}, status=200)



# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def assign_shift(request):
#     # Ensure only authorized users (HR or Super Admin) can access
#     if request.user.role != 'hr':
#         if not request.user.is_superuser:
#             return Response({"error": "Unauthorized: Only HR or Super Admin can assign shifts."}, status=status.HTTP_403_FORBIDDEN)

#     # Retrieve data from the request
#     employee_code = request.data.get('employee_id')
#     shift_id = request.data.get('shift_id')
#     weekly_holiday = request.data.get('weekly_holiday', [])  # Expecting a list of days
#     government_holiday_applicable = request.data.get('government_holiday_applicable', False)
#     earned_leave_qty = request.data.get('earned_leave_qty', 0)
#     paid_leave_qty = request.data.get('paid_leave_qty', 0)
#     casual_leave_qty = request.data.get('casual_leave_qty', 0)
#     applicable_from = request.data.get('applicable_from')

#     # Validate weekly_holiday to ensure it's a list of valid days
#     valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
#     if not all(day in valid_days for day in weekly_holiday):
#         return Response({"error": "Weekly holiday must be a list of valid days."}, status=400)

#     # Fetch the User and Shift objects
#     employee = get_object_or_404(User, employee_code=employee_code)
#     shift = get_object_or_404(Shift, id=shift_id)

#     # Check if an assignment already exists for the employee
#     shift_assignment, created = EmployeeShiftAssignment.objects.update_or_create(
#         employee=employee,
#         defaults={
#             'shift': shift,
#             'assigned_by': request.user,
#             'applicable_from': applicable_from,
#             'government_holiday_applicable': government_holiday_applicable,
#             'earned_leave_qty': earned_leave_qty,
#             'paid_leave_qty': paid_leave_qty,
#             'casual_leave_qty': casual_leave_qty,
#         }
#     )

#     # Set weekly holidays
#     shift_assignment.set_weekly_holiday(weekly_holiday)

#     # Save the shift assignment after updating all fields
#     shift_assignment.save()

#     # Return appropriate response
#     if created:
#         return Response({"success": "Shift assigned successfully."}, status=200)
#     else:
#         return Response({"success": "Shift updated successfully."}, status=200)
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User, Shift, EmployeeShiftAssignment

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_shift(request):
    # Ensure only authorized users (HR or Super Admin) can access
    if request.user.role != 'hr':
        if not request.user.is_superuser:
            return Response({"error": "Unauthorized: Only HR or Super Admin can assign shifts."}, status=status.HTTP_403_FORBIDDEN)

    # Retrieve data from the request
    employee_code = request.data.get('employee_id')
    shift_id = request.data.get('shift_id')
    weekly_holiday = request.data.get('weekly_holiday', [])  # Expecting a list of days
    government_holiday_applicable = request.data.get('government_holiday_applicable', False)
    earned_leave_qty = request.data.get('earned_leave_qty', 0)
    paid_leave_qty = request.data.get('paid_leave_qty', 0)
    casual_leave_qty = request.data.get('casual_leave_qty', 0)
    applicable_from = request.data.get('applicable_from')

    # Validate weekly_holiday to ensure it's a list of valid days
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if not all(day in valid_days for day in weekly_holiday):
        return Response({"error": "Weekly holiday must be a list of valid days."}, status=400)

    # Validate 'applicable_from' date
    if applicable_from:
        try:
            applicable_from_date = datetime.strptime(applicable_from, "%Y-%m-%d").date()
            if applicable_from_date < datetime.now().date():
                return Response({"error": "'Applicable From' date cannot be a past date."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid date format for 'Applicable From'."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the User and Shift objects
    employee = get_object_or_404(User, employee_code=employee_code)
    shift = get_object_or_404(Shift, id=shift_id)

    # Check if an assignment already exists for the employee
    shift_assignment, created = EmployeeShiftAssignment.objects.update_or_create(
        employee=employee,
        defaults={
            'shift': shift,
            'assigned_by': request.user,
            'applicable_from': applicable_from,
            'government_holiday_applicable': government_holiday_applicable,
            'earned_leave_qty': earned_leave_qty,
            'paid_leave_qty': paid_leave_qty,
            'casual_leave_qty': casual_leave_qty,
        }
    )

    # Set weekly holidays
    shift_assignment.set_weekly_holiday(weekly_holiday)

    # Save the shift assignment after updating all fields
    shift_assignment.save()

    # Return appropriate response
    if created:
        return Response({"success": "Shift assigned successfully."}, status=200)
    else:
        return Response({"success": "Shift updated successfully."}, status=200)


# class AssignShiftTemplate(TemplateView):
#     template_name = 'shift_assignment.html'

#     def post(self, request):
#         if request.user.role == 'hr':
#             employee_code = request.POST.get('employee_id')
#             shift_id = request.POST.get('shift_id')
#             weekly_holiday = json.loads(request.POST.get('weekly_holiday'))
#             government_holiday_applicable = True if request.POST.get(
#                 'government_holiday_applicable', 'false') == "true" else False
#             earned_leave_qty = request.POST.get('earned_leave_qty', 0)
#             paid_leave_qty = request.POST.get('paid_leave_qty', 0)
#             casual_leave_qty = request.POST.get('casual_leave_qty', 0)
#             applicable_from = request.POST.get('applicable_from')

#             if not isinstance(weekly_holiday, list) or not all(isinstance(day, str) for day in weekly_holiday):
#                 return HttpResponse("error: Weekly holiday must be a list of valid days.", status=400)

#             employee = get_object_or_404(User, employee_code=employee_code)
#             shift = get_object_or_404(Shift, id=shift_id)

#             shift_assignment = EmployeeShiftAssignment.objects.create(
#                 employee=employee,
#                 shift=shift,
#                 assigned_by=request.user,
#                 applicable_from=applicable_from
#             )

#             shift_assignment.set_weekly_holiday(weekly_holiday)

#             shift_assignment.government_holiday_applicable = government_holiday_applicable
#             shift_assignment.earned_leave_qty = earned_leave_qty
#             shift_assignment.paid_leave_qty = paid_leave_qty
#             shift_assignment.casual_leave_qty = casual_leave_qty

#             shift_assignment.save()

#             return HttpResponse("success: Shift assigned successfully", status=200)

#         return HttpResponse("error: Unauthorized: Only HR can assign shifts.", status=403)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['employees'] = User.objects.all()
#         context['shifts'] = Shift.objects.all()
#         context['assignments'] = EmployeeShiftAssignment.objects.all()
#         return context




from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
import json

# class AssignShiftTemplate(TemplateView):
#     template_name = 'shift_assignment.html'

#     def post(self, request):
#         if request.user.role == 'hr':
#             employee_code = request.POST.get('employee_id')
#             shift_id = request.POST.get('shift_id')
#             # Retrieve multiple selected values for weekly holiday
#             weekly_holiday = request.POST.getlist('weekly_holiday')
#             government_holiday_applicable = request.POST.get(
#                 'government_holiday_applicable', 'false') == "true"
#             earned_leave_qty = request.POST.get('earned_leave_qty', 0)
#             paid_leave_qty = request.POST.get('paid_leave_qty', 0)
#             casual_leave_qty = request.POST.get('casual_leave_qty', 0)
#             applicable_from = request.POST.get('applicable_from')

#             if not all(day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] for day in weekly_holiday):
#                 return HttpResponse("error: Weekly holiday must be a list of valid days.", status=400)

#             employee = get_object_or_404(User, employee_code=employee_code)
#             shift = get_object_or_404(Shift, id=shift_id)

#             shift_assignment = EmployeeShiftAssignment.objects.create(
#                 employee=employee,
#                 shift=shift,
#                 assigned_by=request.user,
#                 applicable_from=applicable_from
#             )

#             shift_assignment.set_weekly_holiday(weekly_holiday)
#             shift_assignment.government_holiday_applicable = government_holiday_applicable
#             shift_assignment.earned_leave_qty = earned_leave_qty
#             shift_assignment.paid_leave_qty = paid_leave_qty
#             shift_assignment.casual_leave_qty = casual_leave_qty
#             shift_assignment.save()

#             return HttpResponse("success: Shift assigned successfully", status=200)

#         return HttpResponse("error: Unauthorized: Only HR can assign shifts.", status=403)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['employees'] = User.objects.all()
#         context['shifts'] = Shift.objects.all()
#         context['assignments'] = EmployeeShiftAssignment.objects.all()
#         return context

# class AssignShiftTemplate(TemplateView):
#     template_name = 'shift_assignment.html'

#     def post(self, request):
#         # Allow both 'hr' and 'superadmin' roles to assign shifts
#         if request.user.role in ['hr', 'superadmin']:
#             employee_code = request.POST.get('employee_id')
#             shift_id = request.POST.get('shift_id')
#             # Retrieve multiple selected values for weekly holiday
#             weekly_holiday = request.POST.getlist('weekly_holiday')
#             government_holiday_applicable = request.POST.get('government_holiday_applicable', 'false') == "true"
#             earned_leave_qty = request.POST.get('earned_leave_qty', 0)
#             paid_leave_qty = request.POST.get('paid_leave_qty', 0)
#             casual_leave_qty = request.POST.get('casual_leave_qty', 0)
#             applicable_from = request.POST.get('applicable_from')

#             # Validate weekly holidays are valid days
#             if not all(day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] for day in weekly_holiday):
#                 return HttpResponse("error: Weekly holiday must be a list of valid days.", status=400)

#             employee = get_object_or_404(User, employee_code=employee_code)
#             shift = get_object_or_404(Shift, id=shift_id)

#             # Create the shift assignment
#             shift_assignment = EmployeeShiftAssignment.objects.create(
#                 employee=employee,
#                 shift=shift,
#                 assigned_by=request.user,
#                 applicable_from=applicable_from
#             )

#             # Assign weekly holidays and other details
#             shift_assignment.set_weekly_holiday(weekly_holiday)
#             shift_assignment.government_holiday_applicable = government_holiday_applicable
#             shift_assignment.earned_leave_qty = earned_leave_qty
#             shift_assignment.paid_leave_qty = paid_leave_qty
#             shift_assignment.casual_leave_qty = casual_leave_qty
#             shift_assignment.save()

#             return HttpResponse("success: Shift assigned successfully", status=200)

#         return HttpResponse("error: Unauthorized: Only HR or Superadmin can assign shifts.", status=403)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['employees'] = User.objects.all()
#         context['shifts'] = Shift.objects.all()
#         context['assignments'] = EmployeeShiftAssignment.objects.all()
#         return context





#####Updated

# class AssignShiftTemplate(TemplateView):
#     template_name = 'shift_assignment.html'

#     def post(self, request):
#         # Allow both 'hr' and 'superadmin' roles to assign shifts
#         if request.user.role in ['hr', 'superadmin']:
#             employee_code = request.POST.get('employee_id')
#             shift_id = request.POST.get('shift_id')
#             weekly_holiday = request.POST.getlist('weekly_holiday')
#             government_holiday_applicable = request.POST.get('government_holiday_applicable', 'false') == "true"
#             earned_leave_qty = request.POST.get('earned_leave_qty', 0)
#             paid_leave_qty = request.POST.get('paid_leave_qty', 0)
#             casual_leave_qty = request.POST.get('casual_leave_qty', 0)
#             applicable_from = request.POST.get('applicable_from')

#             # Validate weekly holidays
#             if not all(day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] for day in weekly_holiday):
#                 return HttpResponse("error: Weekly holiday must be a list of valid days.", status=400)

#             employee = get_object_or_404(User, employee_code=employee_code)
#             shift = get_object_or_404(Shift, id=shift_id)

#             # Check if a shift assignment already exists for this employee
#             shift_assignment, created = EmployeeShiftAssignment.objects.update_or_create(
#                 employee=employee,
#                 defaults={
#                     'shift': shift,
#                     'assigned_by': request.user,
#                     'applicable_from': applicable_from,
#                     'government_holiday_applicable': government_holiday_applicable,
#                     'earned_leave_qty': earned_leave_qty,
#                     'paid_leave_qty': paid_leave_qty,
#                     'casual_leave_qty': casual_leave_qty
#                 }
#             )

#             # Update weekly holidays and other details
#             shift_assignment.set_weekly_holiday(weekly_holiday)
#             shift_assignment.save()

#             if created:
#                 message = "success: Shift assigned successfully"
#             else:
#                 message = "success: Shift updated successfully"

#             return HttpResponse(message, status=200)

#         return HttpResponse("error: Unauthorized: Only HR or Superadmin can assign shifts.", status=403)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['employees'] = User.objects.all()
#         context['shifts'] = Shift.objects.all()
#         context['assignments'] = EmployeeShiftAssignment.objects.all()
#         return context



from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from .models import User, Shift, EmployeeShiftAssignment

class AssignShiftTemplate(TemplateView):
    template_name = 'shift_assignment.html'

    def post(self, request):
        # Allow both 'hr' and 'superadmin' roles to assign shifts
        if request.user.role in ['hr', 'superadmin']:
            employee_code = request.POST.get('employee_id')
            shift_id = request.POST.get('shift_id')
            weekly_holiday = request.POST.getlist('weekly_holiday')
            government_holiday_applicable = request.POST.get('government_holiday_applicable', 'false') == "true"
            earned_leave_qty = request.POST.get('earned_leave_qty', 0)
            paid_leave_qty = request.POST.get('paid_leave_qty', 0)
            casual_leave_qty = request.POST.get('casual_leave_qty', 0)
            applicable_from = request.POST.get('applicable_from')

            # Validate weekly holidays
            if not all(day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] for day in weekly_holiday):
                return HttpResponse("error: Weekly holiday must be a list of valid days.", status=400)

            # Validate 'applicable_from' date
            if applicable_from:
                try:
                    applicable_from_date = datetime.strptime(applicable_from, "%Y-%m-%d").date()
                    if applicable_from_date < datetime.now().date():
                        return HttpResponse("error: 'Applicable From' date cannot be a past date.", status=400)
                except ValueError:
                    return HttpResponse("error: Invalid date format for 'Applicable From'.", status=400)

            employee = get_object_or_404(User, employee_code=employee_code)
            shift = get_object_or_404(Shift, id=shift_id)

            # Check if a shift assignment already exists for this employee
            shift_assignment, created = EmployeeShiftAssignment.objects.update_or_create(
                employee=employee,
                defaults={
                    'shift': shift,
                    'assigned_by': request.user,
                    'applicable_from': applicable_from,
                    'government_holiday_applicable': government_holiday_applicable,
                    'earned_leave_qty': earned_leave_qty,
                    'paid_leave_qty': paid_leave_qty,
                    'casual_leave_qty': casual_leave_qty
                }
            )

            # Update weekly holidays and other details
            shift_assignment.set_weekly_holiday(weekly_holiday)
            shift_assignment.save()

            if created:
                message = "success: Shift assigned successfully"
            else:
                message = "success: Shift updated successfully"

            return HttpResponse(message, status=200)

        return HttpResponse("error: Unauthorized: Only HR or Superadmin can assign shifts.", status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = User.objects.all()
        context['shifts'] = Shift.objects.all()
        context['assignments'] = EmployeeShiftAssignment.objects.all()
        return context



# class ShiftListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Retrieve all shifts
#         shifts = Shift.objects.all()

#         # Structure the shift data
#         shift_data = [
#             {
#                 "id": shift.id,
#                 "shift_name": shift.shift_name,
#                 "shift_start_time": shift.shift_start_time,
#                 "shift_end_time": shift.shift_end_time,
#                 "total_work_time": shift.total_work_time,
#                 "total_break_time": shift.total_break_time,
#                 "created_by": shift.created_by.id
#             }
#             for shift in shifts
#         ]

#         return Response(shift_data, status=status.HTTP_200_OK)
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ShiftListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        # Get query parameters
        search_query = request.query_params.get('search', '')
        start_time = request.query_params.get('start_time')
        work_time = request.query_params.get('work_time')
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        # Start with all shifts
        shifts = Shift.objects.all()

        # Apply search filter
        if search_query:
            shifts = shifts.filter(shift_name__icontains=search_query)

        # Filter by start time
        if start_time:
            try:
                time_obj = datetime.strptime(start_time, '%H:%M').time()
                shifts = shifts.filter(shift_start_time=time_obj)
            except ValueError:
                pass

        # Filter by work time
        if work_time:
            shifts = shifts.filter(total_work_time=work_time)

        # Apply pagination
        paginator = Paginator(shifts, page_size)
        current_page = paginator.get_page(page)

        # Structure the shift data without total_break_time
        shift_data = [
            {
                "id": shift.id,
                "shift_name": shift.shift_name,
                "shift_start_time": shift.shift_start_time,
                "shift_end_time": shift.shift_end_time,
                "total_work_time": shift.total_work_time,
                "created_by": shift.created_by.id
            }
            for shift in current_page
        ]

        response_data = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page),
            'results': shift_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class ShiftListTemplateView(TemplateView):
    template_name = 'shifts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shifts'] = Shift.objects.all()
        return context


class ShiftDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, shift_id):
        # Ensure only HR or superusers can delete shifts
        if not (request.user.role == 'hr' or request.user.is_superuser):
            return Response({"error": "Unauthorized: Only HR or Super Admin can delete shifts."}, status=status.HTTP_403_FORBIDDEN)

        # Get the shift to delete or return a 404 if not found
        shift = get_object_or_404(Shift, id=shift_id)

        # Delete the shift
        shift_name = shift.shift_name  # Save the shift name for the response
        shift.delete()

        return Response({"success": f"Shift '{shift_name}' deleted successfully."}, status=status.HTTP_200_OK)


class ShiftDeleteTemplateView(View):
    def get(self, request, shift_id):
        # Ensure only HR or superusers can delete shifts
        if not (request.user.role == 'hr' or request.user.is_superuser):
            return HttpResponse("error: Unauthorized: Only HR or Super Admin can delete shifts.", status=status.HTTP_403_FORBIDDEN)

        # Get the shift to delete or return a 404 if not found
        shift = get_object_or_404(Shift, id=shift_id)

        # Delete the shift
        shift_name = shift.shift_name  # Save the shift name for the response
        shift.delete()

        return HttpResponse(f"success: Shift '{shift_name}' deleted successfully.", status=status.HTTP_200_OK)


class ShiftAssignmentListTemplateView(TemplateView):
    template_name = 'shift_assignments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = EmployeeShiftAssignment.objects.all()
        return context


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_guest(request):
#     # Check if the user has permission to create guest passes
#     if not request.user.can_create_guest_pass:
#         return Response({"error": "You do not have permission to create guest passes."}, status=status.HTTP_403_FORBIDDEN)

#     # Extract data from request
#     name = request.data.get('name')
#     photo = request.FILES.get('photo')  # Handle file uploads
#     visit_date = request.data.get('visit_date')
#     start_time = request.data.get('start_time')
#     end_time = request.data.get('end_time')
#     organization_id = request.data.get('organization')
#     department_id = request.data.get('department')
#     person_to_meet = request.data.get('person_to_meet')

#     # Check required fields
#     if not all([name, visit_date, start_time, end_time, organization_id, department_id, photo]):
#         return Response({"error": "All fields except 'person_to_meet' are required."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         # Create the guest
#         guest = Guest.objects.create(
#             name=name,
#             photo=photo,
#             visit_date=visit_date,
#             start_time=start_time,
#             end_time=end_time,
#             organization_id=organization_id,
#             department_id=department_id,
#             person_to_meet=person_to_meet,
#             requested_by=request.user
#         )

#         # Process the photo to create face encoding
#         image = face_recognition.load_image_file(photo)
#         encodings = face_recognition.face_encodings(image)

#         if encodings:
#             # Save face encoding if detected, linking to the guest
#             Face.objects.create(guest=guest, face_enc=encodings[0].tolist())

#         return Response({"success": f"Guest '{guest.name}' created successfully."}, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import face_recognition

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_guest(request):
    # Check if the user has permission to create guest passes
    if not request.user.can_create_guest_pass:
        return Response({"error": "You do not have permission to create guest passes."}, status=status.HTTP_403_FORBIDDEN)

    # Extract data from request
    name = request.data.get('name')
    photo = request.FILES.get('photo')  # Handle file uploads
    visit_date = request.data.get('visit_date')
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')
    organization_id = request.data.get('organization')
    department_id = request.data.get('department')
    person_to_meet = request.data.get('person_to_meet')

    # Check required fields
    if not all([name, visit_date, start_time, end_time, organization_id, department_id, photo]):
        return Response({"error": "All fields except 'person_to_meet' are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if visit_date is today or in the future
    try:
        visit_date_obj = datetime.strptime(visit_date, "%Y-%m-%d").date()
        current_date = datetime.now().date()
        
        if visit_date_obj < current_date:
            return Response({"error": "Visit date cannot be in the past."}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"error": "Invalid date format for visit_date. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create the guest
        guest = Guest.objects.create(
            name=name,
            photo=photo,
            visit_date=visit_date,
            start_time=start_time,
            end_time=end_time,
            organization_id=organization_id,
            department_id=department_id,
            person_to_meet=person_to_meet,
            requested_by=request.user
        )

        # Process the photo to create face encoding
        image = face_recognition.load_image_file(photo)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            # Save face encoding if detected, linking to the guest
            Face.objects.create(guest=guest, face_enc=encodings[0].tolist())

        return Response({"success": f"Guest '{guest.name}' created successfully."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









# class CreateGuestTemplate(TemplateView):
#     template_name = 'guest.html'

#     def post(self, request):
#         if request.user.can_create_guest_pass:
#             name = request.POST.get('name')
#             photo = request.FILES.get('photo')
#             visit_date = request.POST.get('visit_date')
#             start_time = request.POST.get('start_time')
#             end_time = request.POST.get('end_time')
#             organization_id = request.POST.get('organization')
#             department_id = request.POST.get('department')
#             person_to_meet = request.POST.get('person_to_meet')

#             if not all([name, visit_date, start_time, end_time, organization_id, department_id, photo]):
#                 return HttpResponse({"error": "All fields except 'person_to_meet' are required."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 guest = Guest.objects.create(
#                     name=name,
#                     photo=photo,
#                     visit_date=visit_date,
#                     start_time=start_time,
#                     end_time=end_time,
#                     organization_id=organization_id,
#                     department_id=department_id,
#                     person_to_meet=person_to_meet,
#                     requested_by=request.user
#                 )

#                 image = face_recognition.load_image_file(photo)
#                 encodings = face_recognition.face_encodings(image)

#                 if encodings:
#                     Face.objects.create(
#                         guest=guest, face_enc=encodings[0].tolist())

#                 return HttpResponse(f"success: Guest '{guest.name}' created successfully.", status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return HttpResponse(f"error {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return HttpResponse("error: You do not have permission to create guest passes.", status=status.HTTP_403_FORBIDDEN)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['organizations'] = Organization.objects.all()
#         context['departments'] = Department.objects.all()
#         context['guests'] = Guest.objects.all()
#         return context






from django.utils import timezone
from datetime import datetime

class CreateGuestTemplate(TemplateView):
    template_name = 'guest.html'

    def post(self, request):
        if request.user.can_create_guest_pass:
            name = request.POST.get('name')
            photo = request.FILES.get('photo')
            visit_date = request.POST.get('visit_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            organization_id = request.POST.get('organization')
            department_id = request.POST.get('department')
            person_to_meet = request.POST.get('person_to_meet')

            # Ensure visit_date is not in the past
            today = timezone.now().date()
            if visit_date and datetime.strptime(visit_date, '%Y-%m-%d').date() < today:
                return HttpResponse("Error: Visit date cannot be in the past.", status=status.HTTP_400_BAD_REQUEST)

            if not all([name, visit_date, start_time, end_time, organization_id, department_id, photo]):
                return HttpResponse({"error": "All fields except 'person_to_meet' are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Create the guest
                guest = Guest.objects.create(
                    name=name,
                    photo=photo,
                    visit_date=visit_date,
                    start_time=start_time,
                    end_time=end_time,
                    organization_id=organization_id,
                    department_id=department_id,
                    person_to_meet=person_to_meet,
                    requested_by=request.user
                )

                # Process the photo to create face encoding
                image = face_recognition.load_image_file(photo)
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    Face.objects.create(guest=guest, face_enc=encodings[0].tolist())

                return HttpResponse(f"success: Guest '{guest.name}' created successfully.", status=status.HTTP_201_CREATED)
            except Exception as e:
                return HttpResponse(f"error {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return HttpResponse("error: You do not have permission to create guest passes.", status=status.HTTP_403_FORBIDDEN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizations'] = Organization.objects.all()
        context['departments'] = Department.objects.all()
        context['guests'] = Guest.objects.all()
        context['today'] = timezone.now().date()  # Pass today's date to the template
        return context













@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_guest(request, guest_id):
    try:
        # Fetch the guest request by ID
        guest = Guest.objects.get(id=guest_id)

        # Check if the user is a superuser or HR
        if request.user.is_superuser or request.user.role == 'hr':
            guest.is_approved = True  # Update approval status
            guest.approved_by = request.user  # Set who approved
            guest.approved_at = timezone.now()  # Set approval timestamp
            guest.save()  # Save the updated guest instance

            return Response({"success": f"Guest {guest.name} has been approved."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Unauthorized: You do not have permission to approve guest requests."}, status=status.HTTP_403_FORBIDDEN)
    except Guest.DoesNotExist:
        return Response({"error": "Guest not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApproveGuest(View):
    def get(self, request, guest_id):
        try:
            guest = Guest.objects.get(id=guest_id)

            if request.user.is_superuser or request.user.role == 'hr':
                guest.is_approved = True
                guest.approved_by = request.user
                guest.approved_at = timezone.now()
                guest.save()

                return HttpResponse(f"success: Guest {guest.name} has been approved.", status=status.HTTP_200_OK)
            else:
                return HttpResponse("error: Unauthorized: You do not have permission to approve guest requests.", status=status.HTTP_403_FORBIDDEN)
        except Guest.DoesNotExist:
            return HttpResponse("error: Guest not found.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class FaceMatchView(APIView):
#     permission_classes = [AllowAny]  # This allows access to everyone

#     def post(self, request):
#         photo = request.FILES.get('photo')  # Get the photo from the request

#         if not photo:
#             return Response({"error": "Photo is required for face matching."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Load the uploaded image
#             image = face_recognition.load_image_file(photo)
#             uploaded_face_encodings = face_recognition.face_encodings(image)

#             if not uploaded_face_encodings:
#                 return Response({"error": "No face found in the uploaded photo."}, status=status.HTTP_400_BAD_REQUEST)

#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Variables to track the closest match
#             closest_distance = float("inf")
#             matched_user = None

#             # Iterate over the stored face encodings to find a match
#             all_faces = Face.objects.all()
#             for face in all_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))  # Convert stored encoding back to numpy array

#                 # Calculate face distance
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                 # Update if this is the closest match so far
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = face.user

#             # Set a threshold for what is considered a "match"
#             if closest_distance < 0.6:  # You can adjust this threshold as needed
#                 # Record attendance for the matched user
#                 now = timezone.now()
#                 attendance, created = Attendance.objects.get_or_create(
#                     user=matched_user,
#                     in_time__date=now.date(),  # Match based on today's date
#                     defaults={'in_time': now}
#                 )

#                 # If attendance record already exists, update the out_time
#                 if not created:
#                     attendance.out_time = now
#                     attendance.save()

#                 return Response({"success": f"Match found: {matched_user.name}"}, status=status.HTTP_200_OK)

#             # If no match is found within the threshold
#             return Response({"error": "No matching user found."}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def get_attendance_report(period, year=None, month=None):
#     if period == 'daily':
#         return Attendance.generate_daily_report()
#     elif period == 'weekly':
#         start_date = timezone.now() - timedelta(days=timezone.now().weekday())
#         return Attendance.generate_weekly_report(start_date=start_date)
#     elif period == 'monthly':
#         return Attendance.objects.filter(in_time__year=year, in_time__month=month)
#     return Attendance.objects.all()  # Default to all records

# def calculate_monthly_summary(attendances):
#     total_present = attendances.filter(status='present').count()
#     total_absent = attendances.filter(status='absent').count()
#     total_late = attendances.filter(status='late').count()
#     return {
#         'total_present': total_present,
#         'total_absent': total_absent,
#         'total_late': total_late,
#     }

# def is_hr_authenticated_by_employee_code(request):
#     employee_code = request.headers.get("Employee-Code")
#     if employee_code:
#         try:
#             # Verify HR user based on employee_code
#             hr_user = User.objects.get(employee_code=employee_code, role='hr')
#             request.user = hr_user
#             return True
#         except User.DoesNotExist:
#             return False
#     return False

# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_passes_test(lambda user: user.is_staff or is_hr_authenticated_by_employee_code), name='dispatch')
# class AttendanceReportView(View):
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         # Automatically set month and year for monthly view
#         if period == 'monthly':
#             if month is None or year is None:
#                 month = timezone.now().month
#                 year = timezone.now().year
#             else:
#                 month = int(month)
#                 year = int(year)
#         else:
#             if month and year:
#                 month = int(month)
#                 year = int(year)

#         attendances = get_attendance_report(period, year=year, month=month)

#         monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)

#         context = {
#             'attendances': attendances,
#             'monthly_summary': monthly_summary,
#             'period': period,
#             'month': month,
#             'year': year,
#         }

#         return render(request, 'attendance_report.html', context)


# class FaceMatchView(APIView):
#     permission_classes = [AllowAny]  # This allows access to everyone

#     def post(self, request):
#         photo = request.FILES.get('photo')  # Get the photo from the request

#         if not photo:
#             return Response({"error": "Photo is required for face matching."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Load the uploaded image
#             image = face_recognition.load_image_file(photo)
#             uploaded_face_encodings = face_recognition.face_encodings(image)

#             if not uploaded_face_encodings:
#                 return Response({"error": "No face found in the uploaded photo."}, status=status.HTTP_400_BAD_REQUEST)

#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Variables to track the closest match
#             closest_distance = float("inf")
#             matched_user = None

#             # Iterate over the stored face encodings to find a match
#             all_faces = Face.objects.all()
#             for face in all_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))  # Convert stored encoding back to numpy array

#                 # Calculate face distance
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                 # Update if this is the closest match so far
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = face.user

#             # Set a threshold for what is considered a "match"
#             if closest_distance < 0.6:  # You can adjust this threshold as needed
#                 # Record attendance for the matched user
#                 now = timezone.now()
#                 attendance, created = Attendance.objects.get_or_create(
#                     user=matched_user,
#                     in_time__date=now.date(),  # Match based on today's date
#                     defaults={'in_time': now}
#                 )

#                 # If attendance record already exists, update the out_time
#                 if not created:
#                     attendance.out_time = now
#                     attendance.save()

#                 return Response({"success": f"Match found: {matched_user.name}"}, status=status.HTTP_200_OK)

#             # If no match is found within the threshold
#             return Response({"error": "No matching user found."}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def get_attendance_report(period, year=None, month=None):
#     if period == 'daily':
#         return Attendance.generate_daily_report()
#     elif period == 'weekly':
#         start_date = timezone.now() - timedelta(days=timezone.now().weekday())
#         return Attendance.generate_weekly_report(start_date=start_date)
#     elif period == 'monthly':
#         return Attendance.objects.filter(in_time__year=year, in_time__month=month)
#     return Attendance.objects.all()  # Default to all records

# def calculate_monthly_summary(attendances):
#     total_present = attendances.filter(status='present').count()
#     total_absent = attendances.filter(status='absent').count()
#     total_late = attendances.filter(status='late').count()

#     # Calculate total time spent
#     user_time_summary = {}
#     for attendance in attendances:
#         if attendance.user not in user_time_summary:
#             user_time_summary[attendance.user] = timedelta(0)
#         user_time_summary[attendance.user] += attendance.time_spent

#     return {
#         'total_present': total_present,
#         'total_absent': total_absent,
#         'total_late': total_late,
#         'user_time_summary': user_time_summary
#     }

# def is_hr_authenticated_by_employee_code(request):
#     employee_code = request.headers.get("Employee-Code")
#     if employee_code:
#         try:
#             # Verify HR user based on employee_code
#             hr_user = User.objects.get(employee_code=employee_code, role='hr')
#             request.user = hr_user
#             return True
#         except User.DoesNotExist:
#             return False
#     return False

# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_passes_test(lambda user: user.is_staff or is_hr_authenticated_by_employee_code), name='dispatch')
# class AttendanceReportView(View):
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         # Automatically set month and year for monthly view
#         if period == 'monthly':
#             if month is None or year is None:
#                 month = timezone.now().month
#                 year = timezone.now().year
#             else:
#                 month = int(month)
#                 year = int(year)
#         else:
#             if month and year:
#                 month = int(month)
#                 year = int(year)

#         attendances = get_attendance_report(period, year=year, month=month)

#         # for attendance in attendances:
#         #     if attendance.out_time and attendance.in_time:
#         #         time_spent_seconds = (attendance.out_time - attendance.in_time).total_seconds()
#         #         attendance.time_spent = time_spent_seconds / 3600  # Convert to hours


#         monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)

#         context = {
#             'attendances': attendances,
#             'monthly_summary': monthly_summary,
#             'period': period,
#             'month': month,
#             'year': year,
#         }

#         return render(request, 'attendance_report.html', context)


# # Function to convert "HH:MM" format to timedelta
# def time_spent_to_timedelta(time_str):
#     if time_str == "00:00":
#         return timedelta(0)
#     hours, minutes = map(int, time_str.split(':'))
#     return timedelta(hours=hours, minutes=minutes)

# class FaceMatchView(APIView):
#     permission_classes = [AllowAny]  # This allows access to everyone

#     def post(self, request):
#         photo = request.FILES.get('photo')  # Get the photo from the request

#         if not photo:
#             return Response({"error": "Photo is required for face matching."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Load the uploaded image
#             image = face_recognition.load_image_file(photo)
#             uploaded_face_encodings = face_recognition.face_encodings(image)

#             if not uploaded_face_encodings:
#                 return Response({"error": "No face found in the uploaded photo."}, status=status.HTTP_400_BAD_REQUEST)

#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Variables to track the closest match
#             closest_distance = float("inf")
#             matched_user = None

#             # Iterate over the stored face encodings to find a match
#             all_faces = Face.objects.all()
#             for face in all_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))  # Convert stored encoding back to numpy array

#                 # Calculate face distance
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                 # Update if this is the closest match so far
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = face.user

#             # Set a threshold for what is considered a "match"
#             if closest_distance < 0.6:  # You can adjust this threshold as needed
#                 # Record attendance for the matched user
#                 now = timezone.now()
#                 attendance, created = Attendance.objects.get_or_create(
#                     user=matched_user,
#                     in_time__date=now.date(),  # Match based on today's date
#                     defaults={'in_time': now}
#                 )

#                 # If attendance record already exists, update the out_time
#                 if not created:
#                     attendance.out_time = now
#                     attendance.save()

#                 return Response({"success": f"Match found: {matched_user.name}"}, status=status.HTTP_200_OK)

#             # If no match is found within the threshold
#             return Response({"error": "No matching user found."}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# def get_attendance_report(period, year=None, month=None):
#     if period == 'daily':
#         return Attendance.generate_daily_report()
#     elif period == 'weekly':
#         start_date = timezone.now() - timedelta(days=timezone.now().weekday())
#         return Attendance.generate_weekly_report(start_date=start_date)
#     elif period == 'monthly':
#         return Attendance.objects.filter(in_time__year=year, in_time__month=month)
#     return Attendance.objects.all()  # Default to all records

# def calculate_monthly_summary(attendances):
#     total_present = attendances.filter(status='present').count()
#     total_absent = attendances.filter(status='absent').count()
#     total_late = attendances.filter(status='late').count()

#     # Calculate total time spent
#     user_time_summary = {}
#     for attendance in attendances:
#         if attendance.user not in user_time_summary:
#             user_time_summary[attendance.user] = timedelta(0)  # Initialize time spent for the user

#         # Convert time_spent from string to timedelta before summing
#         user_time_summary[attendance.user] += time_spent_to_timedelta(attendance.time_spent)

#     return {
#         'total_present': total_present,
#         'total_absent': total_absent,
#         'total_late': total_late,
#         'user_time_summary': user_time_summary
#     }

# def is_hr_authenticated_by_employee_code(request):
#     employee_code = request.headers.get("Employee-Code")
#     if employee_code:
#         try:
#             # Verify HR user based on employee_code
#             hr_user = User.objects.get(employee_code=employee_code, role='hr')
#             request.user = hr_user
#             return True
#         except User.DoesNotExist:
#             return False
#     return False

# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_passes_test(lambda user: user.is_staff or is_hr_authenticated_by_employee_code), name='dispatch')
# class AttendanceReportView(View):
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         # Automatically set month and year for monthly view
#         if period == 'monthly':
#             if month is None or year is None:
#                 month = timezone.now().month
#                 year = timezone.now().year
#             else:
#                 month = int(month)
#                 year = int(year)
#         else:
#             if month and year:
#                 month = int(month)
#                 year = int(year)

#         attendances = get_attendance_report(period, year=year, month=month)

#         monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)

#         context = {
#             'attendances': attendances,
#             'monthly_summary': monthly_summary,
#             'period': period,
#             'month': month,
#             'year': year,
#         }

#         return render(request, 'attendance_report.html', context)


# class AttendanceReportView(View):
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         # Automatically set month and year for monthly view
#         if period == 'monthly':
#             if month is None or year is None:
#                 month = timezone.now().month
#                 year = timezone.now().year
#             else:
#                 month = int(month)
#                 year = int(year)
#         else:
#             if month and year:
#                 month = int(month)
#                 year = int(year)

#         attendances = get_attendance_report(period, year=year, month=month)

#         monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)

#         context = {
#             'attendances': attendances,
#             'monthly_summary': monthly_summary,
#             'period': period,
#             'month': month,
#             'year': year,
#         }

#         return render(request, 'attendance_report.html', context)


# class FaceMatchView(APIView):
#     permission_classes = [AllowAny]  # This allows access to everyone

#     def post(self, request):
#         photo = request.FILES.get('photo')  # Get the photo from the request

#         if not photo:
#             return Response({"error": "Photo is required for face matching."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Load the uploaded image
#             image = face_recognition.load_image_file(photo)
#             uploaded_face_encodings = face_recognition.face_encodings(image)

#             if not uploaded_face_encodings:
#                 return Response({"error": "No face found in the uploaded photo."}, status=status.HTTP_400_BAD_REQUEST)

#             uploaded_face_encoding = uploaded_face_encodings[0]

#             # Variables to track the closest match
#             closest_distance = float("inf")
#             matched_user = None

#             # Iterate over the stored face encodings to find a match
#             all_faces = Face.objects.all()
#             for face in all_faces:
#                 stored_face_encoding = np.array(eval(face.face_enc))  # Convert stored encoding back to numpy array

#                 # Calculate face distance
#                 distance = face_recognition.face_distance([stored_face_encoding], uploaded_face_encoding)[0]

#                 # Update if this is the closest match so far
#                 if distance < closest_distance:
#                     closest_distance = distance
#                     matched_user = face.user

#             # Set a threshold for what is considered a "match"
#             if closest_distance < 0.6:  # You can adjust this threshold as needed
#                 return Response({"success": f"Match found: {matched_user.name}"}, status=status.HTTP_200_OK)

#             # If no match is found within the threshold
#             return Response({"error": "No matching user found."}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CreateUserBySuperuser(APIView):
#     permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

#     def post(self, request):
#         if request.user.is_superuser:  # Check if the user is a superuser
#             # Extract data from the request
#             name = request.data.get('name')
#             role = request.data.get('role')
#             organization_id = request.data.get('organization')
#             department_id = request.data.get('department')
#             designation = request.data.get('designation')
#             blood_group = request.data.get('blood_group')
#             emergency_contact = request.data.get('emergency_contact')
#             photo = request.FILES.get('photo')  # Get the photo from the request

#             # Validate required fields
#             if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact, photo]):
#                 return Response({"error": "All fields, including photo, are required."}, status=status.HTTP_400_BAD_REQUEST)

#             # Optionally, you can add further validation here, e.g., check if organization and department exist

#             # Create the user
#             try:
#                 user = User.objects.create(
#                     name=name,
#                     role=role,
#                     organization_id=organization_id,
#                     department_id=department_id,
#                     designation=designation,
#                     blood_group=blood_group,
#                     emergency_contact=emergency_contact,
#                     photo=photo,  # Save the photo
#                     created_by=request.user  # Superuser creating the user
#                 )
#                 return Response({"success": f"User '{user.name}' created successfully with employee code {user.employee_code}."}, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({"error": "Unauthorized: Only superusers can create users."}, status=status.HTTP_403_FORBIDDEN)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Ensure only authenticated users can access
# def create_user_by_hr(request):
#     if request.user.role == 'hr':  # Check if the user is HR
#         # Extract data from request
#         name = request.data.get('name')
#         department_id = request.data.get('department')
#         organization_id = request.data.get('organization')
#         designation = request.data.get('designation')
#         blood_group = request.data.get('blood_group')
#         emergency_contact = request.data.get('emergency_contact')
#         role = request.data.get('role')  # Get the role from the request
#         can_create_guest_pass = request.data.get('can_create_guest_pass', False)  # New field for guest pass permission
#         photo = request.FILES.get('photo')  # Get the photo from the request

#         # List of roles that can be assigned by HR
#         allowed_roles = ["superadmin", "front desk", "help Desk", "security", "others"]

#         # Check if all required fields are provided
#         if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role, photo]):
#             return Response({"error": "All fields, including photo, are required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Validate the assigned role
#         if role not in allowed_roles:
#             return Response({"error": f"Role '{role}' is not allowed. Allowed roles are: {', '.join(allowed_roles)}."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.create(
#                 name=name,
#                 role=role,  # Assign the role provided in the request
#                 department_id=department_id,
#                 organization_id=organization_id,
#                 designation=designation,
#                 blood_group=blood_group,
#                 emergency_contact=emergency_contact,
#                 can_create_guest_pass=can_create_guest_pass,  # Set guest pass permission
#                 photo=photo,  # Save the photo
#                 created_by=request.user  # HR creating the user
#             )
#             return Response({"success": f"User {user.name} created successfully with employee code {user.employee_code}"}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     else:
#         return Response({"error": "Unauthorized: Only HR can create users"}, status=status.HTTP_403_FORBIDDEN)

# class CreateUserBySuperuser(APIView):
#     permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

#     def post(self, request):
#         if request.user.is_superuser:  # Check if the user is a superuser
#             # Extract data from the request
#             name = request.data.get('name')
#             role = request.data.get('role')
#             organization_id = request.data.get('organization')
#             department_id = request.data.get('department')
#             designation = request.data.get('designation')
#             blood_group = request.data.get('blood_group')
#             emergency_contact = request.data.get('emergency_contact')

#             # Validate required fields
#             if not all([name, role, organization_id, department_id, designation, blood_group, emergency_contact]):
#                 return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

#             # Optionally, you can add further validation here, e.g., check if organization and department exist

#             # Create the user
#             user = User.objects.create(
#                 name=name,
#                 role=role,
#                 organization_id=organization_id,
#                 department_id=department_id,
#                 designation=designation,
#                 blood_group=blood_group,
#                 emergency_contact=emergency_contact,
#                 created_by=request.user  # Superuser creating the user
#             )
#             return Response({"success": f"User '{user.name}' created successfully with employee code {user.employee_code}."}, status=status.HTTP_201_CREATED)

#         return Response({"error": "Unauthorized: Only superusers can create users."}, status=status.HTTP_403_FORBIDDEN)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Ensure only authenticated users can access
# def create_user_by_hr(request):
#     if request.user.role == 'hr':  # Check if the user is HR
#         # Extract data from request
#         name = request.data.get('name')
#         department_id = request.data.get('department')
#         organization_id = request.data.get('organization')
#         designation = request.data.get('designation')
#         blood_group = request.data.get('blood_group')
#         emergency_contact = request.data.get('emergency_contact')
#         role = request.data.get('role')  # Get the role from the request
#         can_create_guest_pass = request.data.get('can_create_guest_pass', False)  # New field for guest pass permission

#         # List of roles that can be assigned by HR
#         allowed_roles = ["superadmin", "front desk", "help Desk", "security", "others"]

#         # Check if all required fields are provided
#         if not all([name, department_id, organization_id, designation, blood_group, emergency_contact, role]):
#             return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Validate the assigned role
#         if role not in allowed_roles:
#             return Response({"error": f"Role '{role}' is not allowed. Allowed roles are: {', '.join(allowed_roles)}."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.create(
#                 name=name,
#                 role=role,  # Assign the role provided in the request
#                 department_id=department_id,
#                 organization_id=organization_id,
#                 designation=designation,
#                 blood_group=blood_group,
#                 emergency_contact=emergency_contact,
#                 can_create_guest_pass=can_create_guest_pass,  # Set guest pass permission
#                 created_by=request.user  # HR creating the user
#             )
#             return Response({"success": f"User {user.name} created successfully with employee code {user.employee_code}"}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     else:
#         return Response({"error": "Unauthorized: Only HR can create users"}, status=status.HTTP_403_FORBIDDEN)


# @api_view(['POST'])
# def assign_shift(request):
#     try:
#         # Retrieve data from the request
#         employee_code = request.data.get('employee_id')  # use 'employee_id' as it is sent in the request
#         shift_id = request.data.get('shift_id')
#         weekly_holiday = request.data.get('weekly_holiday')
#         government_holiday_applicable = request.data.get('government_holiday_applicable', False)
#         earned_leave_qty = request.data.get('earned_leave_qty', 0)
#         paid_leave_qty = request.data.get('paid_leave_qty', 0)
#         casual_leave_qty = request.data.get('casual_leave_qty', 0)
#         applicable_from = request.data.get('applicable_from')

#         # Fetch the User object based on employee_code
#         employee = get_object_or_404(User, employee_code=employee_code)

#         # Fetch the Shift object based on shift_id
#         shift = get_object_or_404(Shift, id=shift_id)

#         # Create the EmployeeShiftAssignment object
#         shift_assignment = EmployeeShiftAssignment.objects.create(
#             employee=employee,
#             shift=shift,
#             weekly_holiday=weekly_holiday,
#             government_holiday_applicable=government_holiday_applicable,
#             earned_leave_qty=earned_leave_qty,
#             paid_leave_qty=paid_leave_qty,
#             casual_leave_qty=casual_leave_qty,
#             applicable_from=applicable_from,
#             assigned_by=request.user  # Assuming the request user is making the assignment
#         )

#         return Response({"success": "Shift assigned successfully"}, status=200)

#     except Exception as e:
#         return Response({"error": str(e)}, status=400)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def assign_shift(request):
#     if request.user.role == 'hr':  # Ensure only HR can assign shifts
#         employee_id = request.data.get('employee_id')
#         shift_id = request.data.get('shift_id')
#         weekly_holiday = request.data.get('weekly_holiday')
#         government_holiday_applicable = request.data.get('government_holiday_applicable')
#         earned_leave_qty = request.data.get('earned_leave_qty')
#         paid_leave_qty = request.data.get('paid_leave_qty')
#         casual_leave_qty = request.data.get('casual_leave_qty')
#         applicable_from = request.data.get('applicable_from')

#         # Get employee and shift
#         employee = User.objects.get(id=employee_id)
#         shift = Shift.objects.get(id=shift_id)

#         # Create the assignment
#         assignment = EmployeeShiftAssignment.objects.create(
#             employee=employee,
#             shift=shift,
#             weekly_holiday=weekly_holiday,
#             government_holiday_applicable=government_holiday_applicable,
#             earned_leave_qty=earned_leave_qty,
#             paid_leave_qty=paid_leave_qty,
#             casual_leave_qty=casual_leave_qty,
#             applicable_from=applicable_from,
#             assigned_by=request.user,
#         )
#         return Response({"success": f"Shift '{shift}' assigned to '{employee}'."}, status=status.HTTP_201_CREATED)

#     return Response({"error": "Unauthorized: Only HR can assign shifts."}, status=status.HTTP_403_FORBIDDEN)

# @csrf_exempt
# def create_organization(request):
#     print("Request headers:", request.headers)  # Log request headers
#     print("Request user:", request.user)  # Log request user

#     if request.user.is_authenticated:
#         if request.user.is_superuser:
#             if request.method == 'POST':
#                 data = json.loads(request.body)
#                 organization = Organization.objects.create(
#                     name=data['name'],
#                     address=data['address'],
#                     gst_no=data['gst_no'],
#                     no_of_employees=data['no_of_employees'],
#                     access_control=data['access_control']
#                 )
#                 return JsonResponse({"success": f"Organization '{organization.name}' created successfully."})
#             return JsonResponse({"error": "Invalid request method."})
#         return JsonResponse({"error": "Unauthorized: Only superusers can create organizations."})
#     return JsonResponse({"error": "Unauthorized: User is not authenticated."})


# @csrf_exempt
# def create_department(request):
#     if request.user.is_superuser:  # Check if the user is a superuser
#         if request.method == 'POST':
#             data = json.loads(request.body)
#             organization = Organization.objects.get(id=data['organization'])
#             department = Department.objects.create(
#                 name=data['name'],
#                 organization=organization,
#                 integrate_with_ai_camera=data['integrate_with_ai_camera']
#             )
#             return JsonResponse({"success": f"Department '{department.name}' created successfully."})
#         return JsonResponse({"error": "Invalid request method."})
#     return JsonResponse({"error": "Unauthorized: Only superusers can create departments."})


# @csrf_exempt
# def create_user_by_superuser(request):
#     if request.user.is_superuser:  # Check if the user is a superuser
#         if request.method == 'POST':
#             data = json.loads(request.body)
#             user = User.objects.create(
#                 name=data['name'],
#                 role=Role.objects.get(id=data['role']),  # Role ID
#                 organization_id=data['organization'],  # Organization ID
#                 department_id=data['department'],  # Department ID
#                 designation=data['designation'],
#                 blood_group=data['blood_group'],
#                 emergency_contact=data['emergency_contact'],
#                 created_by=request.user  # Superuser creating the user
#             )
#             return JsonResponse({"success": f"User '{user.name}' created successfully with employee code {user.employee_code}."})
#     return JsonResponse({"error": "Unauthorized: Only superusers can create users."})

# def create_user_by_hr(request):
#     if request.user.role.name == 'HR':  # Check if the user is HR
#         name = request.POST.get('name')
#         department = request.POST.get('department')
#         organization = request.POST.get('organization')
#         designation = request.POST.get('designation')
#         blood_group = request.POST.get('blood_group')
#         emergency_contact = request.POST.get('emergency_contact')

#         # Assigning a default role (you can adjust it according to your needs)
#         role = Role.objects.get(name='Employee')

#         user = User.objects.create(
#             name=name,
#             role=role,
#             department_id=department,
#             organization_id=organization,
#             designation=designation,
#             blood_group=blood_group,
#             emergency_contact=emergency_contact,
#             created_by=request.user  # HR creating the user
#         )

#         return JsonResponse({"success": f"User {user.name} created successfully with employee code {user.employee_code}"})
#     else:
#         return JsonResponse({"error": "Unauthorized: Only HR can create users"})
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_guest(request):
#     # Check if the user has permission to create guest passes
#     if not request.user.can_create_guest_pass:
#         return Response({"error": "You do not have permission to create guest passes."}, status=status.HTTP_403_FORBIDDEN)

#     # Extract data from request
#     name = request.data.get('name')
#     photo = request.FILES.get('photo')  # Handle file uploads
#     visit_date = request.data.get('visit_date')
#     start_time = request.data.get('start_time')
#     end_time = request.data.get('end_time')
#     organization_id = request.data.get('organization')
#     department_id = request.data.get('department')
#     person_to_meet = request.data.get('person_to_meet')

#     # Check required fields
#     if not all([name, visit_date, start_time, end_time, organization_id, department_id]):
#         return Response({"error": "All fields except 'person_to_meet' are required."}, status=status.HTTP_400_BAD_REQUEST)

#     # Validate the date and time if needed
#     try:
#         # Here you might want to check if the organization and department exist
#         guest = Guest(
#             name=name,
#             photo=photo,
#             visit_date=visit_date,
#             start_time=start_time,
#             end_time=end_time,
#             organization_id=organization_id,
#             department_id=department_id,
#             person_to_meet=person_to_meet,
#             requested_by=request.user
#         )
#         guest.save()  # Save the guest instance
#         return Response({"success": f"Guest {guest.name} created successfully."}, status=status.HTTP_201_CREATED)
#     except ValidationError as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_passes_test(lambda user: user.is_staff or is_hr_authenticated_by_employee_code), name='dispatch')
# class AttendanceReportView(View):
#     def get(self, request):
#         period = request.GET.get('period', 'daily')
#         month = request.GET.get('month', None)
#         year = request.GET.get('year', None)

#         # Set month and year for all periods
#         if month is None or year is None:
#             now = timezone.now()
#             month = now.month
#             year = now.year
#         else:
#             month = int(month)
#             year = int(year)

#         # Fetch attendances based on the period
#         attendances = get_attendance_report(period, year=year, month=month)

#         # Prepare monthly summary if needed
#         monthly_summary = {}
#         guest_monthly_summary = {}
#         if period == 'monthly':
#             monthly_summary = calculate_monthly_summary(attendances)
#             guest_monthly_summary = monthly_summary['guest_time_summary']

#         # Fetch guest attendances
#         user_attendance = Attendance.objects.filter(user__isnull=False).order_by('in_time')
#         guest_attendance = Attendance.objects.filter(guest__isnull=False).order_by('in_time')

#         # guest_attendances = Attendance.objects.filter(guest__isnull=False)  # Add this line

#         # Convert month number to month name
#         month_name = calendar.month_name[month]

#         context = {
#             'attendances': attendances,
#             'monthly_summary': monthly_summary,
#             'user_attendance': user_attendance,
#             'guest_attendance': guest_attendance,
#             # 'guest_attendances': guest_attendances,  # Add this line
#             'guest_monthly_summary': guest_monthly_summary,
#             'period': period,
#             'month': month_name,  # Pass the month name to the template
#             'year': year,
#         }

#         return render(request, 'attendance_report.html', context)

 # Import your custom user model

# @csrf_exempt
# def login_view(request):
#     if request.method == 'POST':
#         employee_code = request.POST.get('employee_code')
#         password = request.POST.get('password')

#         # Authenticate using employee_code instead of username
#         try:
#             user = User.objects.get(employee_code=employee_code)  # Find user by employee_code
#             if user.check_password(password):  # Check if password is correct
#                 login(request, user)
#                 return JsonResponse({"success": True, "message": "Login successful", "redirect_url": reverse('home')})
#             else:
#                 return JsonResponse({"success": False, "message": "Invalid password"}, status=400)
#         except User.DoesNotExist:
#             return JsonResponse({"success": False, "message": "Invalid employee code"}, status=400)

#     return render(request, 'login.html')

# @login_required
# def home_view(request):
#     user = request.user
#     return render(request, 'home.html', {"user_name": user.full_name})

# def logout_view(request):
#     logout(request)
#     return redirect('login')


# @csrf_protect
# def login_view(request):
#     if request.method == 'POST':
#         employee_code = request.POST.get('employee_code')
#         password = request.POST.get('password')

#         try:
#             user = User.objects.get(employee_code=employee_code)
#             if user.check_password(password):
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 return JsonResponse({'error': 'Invalid password'}, status=400)
#         except User.DoesNotExist:
#             return JsonResponse({'error': 'Invalid employee code'}, status=400)

#     return render(request, 'login.html')


# def home_view(request):
#     if request.user.is_authenticated:
#         return render(request, 'home.html', {'user_name': request.user.name})
#     return redirect('login')


# def logout_view(request):
#     logout(request)
#     return redirect('login')


# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import requests
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseForbidden
import requests


from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import User
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import User
import requests


class PendingHolidayListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser or request.user.role == 'hr':
            pending_holidays = Holiday.objects.filter(is_verified=False)
            pending_data = [
                {
                    "id": holiday.id,
                    "holiday_dates": holiday.holiday_dates,
                    "created_by": holiday.created_by.id,
                    "is_verified": holiday.is_verified
                }
                for holiday in pending_holidays
            ]
            return Response(pending_data, status=status.HTTP_200_OK)
        return Response({"error": "Unauthorized: Only superusers or HR can view pending holidays."}, status=status.HTTP_403_FORBIDDEN)


class ApprovedHolidayListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser or request.user.role == 'hr':
            approved_holidays = Holiday.objects.filter(is_verified=True)
            approved_data = [
                {
                    "id": holiday.id,
                    "holiday_dates": holiday.holiday_dates,
                    "created_by": holiday.created_by.id,
                    "is_verified": holiday.is_verified
                }
                for holiday in approved_holidays
            ]
            return Response(approved_data, status=status.HTTP_200_OK)
        return Response({"error": "Unauthorized: Only superusers or HR can view approved holidays."}, status=status.HTTP_403_FORBIDDEN)


class ListHolidayTemplateView(TemplateView):
    template_name = 'holidays.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['holidays'] = Holiday.objects.all()
        return context


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_guests(request):
#     # Check if the user has permission to view the guest list
#     if not (request.user.can_create_guest_pass or request.user.is_superuser or request.user.role == 'hr'):
#         return Response({"error": "You do not have permission to view the guest list."}, status=status.HTTP_403_FORBIDDEN)

#     # Retrieve all guests
#     guests = Guest.objects.all()
#     guest_list = []

#     for guest in guests:
#         guest_list.append({
#             "id": guest.id,
#             "name": guest.name,
#             "visit_date": guest.visit_date,
#             "start_time": guest.start_time,
#             "end_time": guest.end_time,
#             "organization": guest.organization_id,  # Assuming this is an ID
#             "department": guest.department_id,        # Assuming this is an ID
#             "person_to_meet": guest.person_to_meet,
#             # Using 'name' attribute
#             "requested_by": guest.requested_by.name if guest.requested_by else None,
#             "is_approved": guest.is_approved,
#             # Using 'name' attribute
#             "approved_by": guest.approved_by.name if guest.approved_by else None,
#             "approved_at": guest.approved_at,
#         })

#     return Response(guest_list, status=status.HTTP_200_OK)
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_guests(request):
    # Check if the user has permission to view the guest list
    if not (request.user.can_create_guest_pass or request.user.is_superuser or request.user.role == 'hr'):
        return Response({"error": "You do not have permission to view the guest list."}, status=status.HTTP_403_FORBIDDEN)

    # Get query parameters
    approval_status = request.query_params.get('approved')
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 10)

    # Retrieve all guests
    guests = Guest.objects.all()

    # Filter by approval status if specified
    if approval_status is not None:
        is_approved = approval_status.lower() == 'true'
        guests = guests.filter(is_approved=is_approved)

    # Apply pagination
    paginator = Paginator(guests, page_size)
    current_page = paginator.get_page(page)

    guest_list = []
    for guest in current_page:
        guest_list.append({
            "id": guest.id,
            "name": guest.name,
            "visit_date": guest.visit_date,
            "start_time": guest.start_time,
            "end_time": guest.end_time,
            "organization": guest.organization_id,
            "department": guest.department_id,
            "person_to_meet": guest.person_to_meet,
            "requested_by": guest.requested_by.name if guest.requested_by else None,
            "is_approved": guest.is_approved,
            "approved_by": guest.approved_by.name if guest.approved_by else None,
            "approved_at": guest.approved_at,
        })

    response_data = {
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'results': guest_list
    }

    return Response(response_data, status=status.HTTP_200_OK)

class ListGuest(TemplateView):
    template_name = 'guests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guests'] = Guest.objects.all()
        return context


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_guest(request, guest_id):
    try:
        guest = Guest.objects.get(id=guest_id)

        # Check permissions: only HR or Super Admin can delete guests
        if not request.user.is_superuser and request.user.role != 'hr':
            return Response({"error": "Unauthorized: You do not have permission to delete guests."}, status=status.HTTP_403_FORBIDDEN)

        guest.delete()
        return Response({"success": f"Guest '{guest.name}' deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    except Guest.DoesNotExist:
        return Response({"error": "Guest not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.http import HttpResponse

class DeleteGuest(View):
    def get(self, request, guest_id):
        try:
            guest = Guest.objects.get(id=guest_id)

            # Check permissions: only HR or Super Admin can delete guests
            if not request.user.is_superuser and request.user.role != 'hr':
                return HttpResponse("error: Unauthorized: You do not have permission to delete guests.", status=status.HTTP_403_FORBIDDEN)

            guest.delete()
            return HttpResponse(f"success: Guest '{guest.name}' deleted successfully.", status=status.HTTP_200_OK)

        except Guest.DoesNotExist:
            return HttpResponse("error: Guest not found.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return HttpResponse(f"error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Lock

# Create Lock
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_lock(request):
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return Response({"error": "Unauthorized: Only Super Admin can create locks."}, status=status.HTTP_403_FORBIDDEN)
    
    name = request.data.get('name')
    com_port = request.data.get('com_port')
    if not name or not com_port:
        return Response({"error": "Name and COM port are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    lock = Lock.objects.create(name=name, com_port=com_port)
    return Response({"id": lock.id, "name": lock.name, "com_port": lock.com_port}, status=status.HTTP_201_CREATED)

# Edit Lock
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_lock(request, lock_id):
    try:
        lock = Lock.objects.get(id=lock_id)
        
        # Superadmin access check
        if not request.user.is_superuser and request.user.role != 'superadmin':
            return Response({"error": "Unauthorized: Only Super Admin can edit locks."}, status=status.HTTP_403_FORBIDDEN)
        
        lock.name = request.data.get('name', lock.name)
        lock.com_port = request.data.get('com_port', lock.com_port)
        lock.save()
        return Response({"id": lock.id, "name": lock.name, "com_port": lock.com_port}, status=status.HTTP_200_OK)
    
    except Lock.DoesNotExist:
        return Response({"error": "Lock not found."}, status=status.HTTP_404_NOT_FOUND)

# Delete Lock
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_lock(request, lock_id):
    try:
        lock = Lock.objects.get(id=lock_id)
        
        # Superadmin access check
        if not request.user.is_superuser and request.user.role != 'superadmin':
            return Response({"error": "Unauthorized: Only Super Admin can delete locks."}, status=status.HTTP_403_FORBIDDEN)
        
        lock.delete()
        return Response({"success": "Lock deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    except Lock.DoesNotExist:
        return Response({"error": "Lock not found."}, status=status.HTTP_404_NOT_FOUND)






from django.contrib import messages

@login_required
def manage_locks(request):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    # Fetch all locks to display in the template
    locks = Lock.objects.all()

    # Handle POST request for creating a new lock
    if request.method == 'POST':
        name = request.POST.get('name')
        com_port = request.POST.get('com_port')
        
        if name and com_port:
            # Create a new lock
            new_lock = Lock.objects.create(name=name, com_port=com_port)
            
            # Add success message using Django's messages framework
            messages.success(request, f"Lock '{new_lock.name}' created successfully.")
            
            # Redirect back to the manage_locks page
            return redirect('manage_locks_template')

    # Return the template with all locks if it's not a POST request
    return render(request, 'manage_locks.html', {'locks': locks})


@login_required
def edit_lock(request, lock_id):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    lock = get_object_or_404(Lock, id=lock_id)

    if request.method == 'POST':
        lock.name = request.POST.get('name')
        lock.com_port = request.POST.get('com_port')
        lock.save()
        messages.success(request, "Lock successfully updated.")
        return redirect('manage_locks_template')  # Redirect back to the manage locks page
    
    return render(request, 'edit_lock.html', {'lock': lock})


@login_required
def delete_lock(request, lock_id):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    lock = get_object_or_404(Lock, id=lock_id)

    if request.method == 'POST':
        lock.delete()
        messages.success(request, "Lock successfully deleted.")
        return redirect('manage_locks_template')  # Redirect to the correct URL name

    return render(request, 'confirm_delete_lock.html', {'lock': lock})


from .models import Camera, Lock

# Create Camera
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_camera(request):
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return Response({"error": "Unauthorized: Only Super Admin can create cameras."}, status=status.HTTP_403_FORBIDDEN)
    
    camera_id = request.data.get('camera_id')
    in_out = request.data.get('in_out')
    lock_id = request.data.get('lock_id')
    attendance = request.data.get('attendance', False)
    
    try:
        lock = Lock.objects.get(id=lock_id)
        camera = Camera.objects.create(camera_id=camera_id, in_out=in_out, lock=lock, attendance=attendance)
        return Response({"id": camera.id, "camera_id": camera.camera_id, "in_out": camera.in_out, "lock_id": camera.lock.id, "attendance": camera.attendance}, status=status.HTTP_201_CREATED)
    
    except Lock.DoesNotExist:
        return Response({"error": "Lock not found"}, status=status.HTTP_404_NOT_FOUND)

# Edit Camera
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_camera(request, camera_id):
    try:
        camera = Camera.objects.get(id=camera_id)
        
        if not request.user.is_superuser and request.user.role != 'superadmin':
            return Response({"error": "Unauthorized: Only Super Admin can edit cameras."}, status=status.HTTP_403_FORBIDDEN)
        
        camera.camera_id = request.data.get('camera_id', camera.camera_id)
        camera.in_out = request.data.get('in_out', camera.in_out)
        lock_id = request.data.get('lock_id', camera.lock.id)
        
        try:
            lock = Lock.objects.get(id=lock_id)
            camera.lock = lock
        except Lock.DoesNotExist:
            return Response({"error": "Lock not found"}, status=status.HTTP_404_NOT_FOUND)
        
        camera.attendance = request.data.get('attendance', camera.attendance)
        camera.save()
        return Response({"id": camera.id, "camera_id": camera.camera_id, "in_out": camera.in_out, "lock_id": camera.lock.id, "attendance": camera.attendance}, status=status.HTTP_200_OK)
    
    except Camera.DoesNotExist:
        return Response({"error": "Camera not found"}, status=status.HTTP_404_NOT_FOUND)

# Delete Camera
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_camera(request, camera_id):
    try:
        camera = Camera.objects.get(id=camera_id)
        
        if not request.user.is_superuser and request.user.role != 'superadmin':
            return Response({"error": "Unauthorized: Only Super Admin can delete cameras."}, status=status.HTTP_403_FORBIDDEN)
        
        camera.delete()
        return Response({"success": "Camera deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    except Camera.DoesNotExist:
        return Response({"error": "Camera not found"}, status=status.HTTP_404_NOT_FOUND)









from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Camera

@login_required
def manage_cameras(request):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    # Fetch all cameras to display in the template
    cameras = Camera.objects.all()

    # Handle POST request for creating a new camera
    if request.method == 'POST':
        camera_id = request.POST.get('camera_id')
        in_out = request.POST.get('in_out')
        lock_id = request.POST.get('lock_id')
        attendance = request.POST.get('attendance') == 'on'

        if camera_id and in_out and lock_id:
            try:
                lock = Lock.objects.get(id=lock_id)
                # Create a new camera
                new_camera = Camera.objects.create(
                    camera_id=camera_id,
                    in_out=in_out,
                    lock=lock,
                    attendance=attendance
                )
                messages.success(request, f"Camera '{new_camera.camera_id}' created successfully.")
                return redirect('manage_cameras_template')
            except Lock.DoesNotExist:
                messages.error(request, "Invalid Lock ID provided.")

    # Return the template with all cameras if it's not a POST request
    return render(request, 'manage_cameras.html', {'cameras': cameras})

@login_required
def edit_camera(request, camera_id):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    camera = get_object_or_404(Camera, id=camera_id)
    locks = Lock.objects.all()  # Fetch all locks for the dropdown menu

    if request.method == 'POST':
        camera.camera_id = request.POST.get('camera_id', camera.camera_id)
        camera.in_out = request.POST.get('in_out', camera.in_out)
        lock_id = request.POST.get('lock_id')
        attendance = request.POST.get('attendance') == 'on'

        try:
            lock = Lock.objects.get(id=lock_id)
            camera.lock = lock
        except Lock.DoesNotExist:
            messages.error(request, "Invalid Lock ID provided.")
            return redirect('edit_camera_template', camera_id=camera.id)

        camera.attendance = attendance
        camera.save()
        messages.success(request, "Camera successfully updated.")
        return redirect('manage_cameras_template')

    return render(request, 'edit_camera.html', {'camera': camera, 'locks': locks})


@login_required
def delete_camera(request, camera_id):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    camera = get_object_or_404(Camera, id=camera_id)

    if request.method == 'POST':
        camera.delete()
        messages.success(request, "Camera successfully deleted.")
        return redirect('manage_cameras_template')

    return render(request, 'confirm_delete_camera.html', {'camera': camera})




from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Lock, Camera  # assuming these models exist
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_locks(request):
    locks = Lock.objects.all()
    lock_data = [
        {
            "id": lock.id,
            "name": lock.name,
            "com_port": lock.com_port
        }
        for lock in locks
    ]
    return Response(lock_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cameras(request):
    cameras = Camera.objects.all()
    camera_data = [
        {
            "id": camera.id,
            "camera_id": camera.camera_id,
            "in_out": camera.in_out,
            "lock_id": camera.lock_id,
            "attendance": camera.attendance
        }
        for camera in cameras
    ]
    return Response(camera_data, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import JsonResponse
from .models import Camera, CameraSetup, Department
from django.core.exceptions import PermissionDenied
import json

# 1. List CameraSetups (only accessible by superadmin)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_camera_setups(request):
    if request.user.role == 'superadmin':
        camera_setups = CameraSetup.objects.all()
        setup_list = [
            {
                "id": setup.id,
                "name": setup.name,
                "camera_id": setup.camera.id,
                "camera_name": setup.camera.camera_id,
                "integrate_with_access_control": setup.integrate_with_access_control,
                "entry_exit": setup.entry_exit,
                "department_id": setup.department.id,
                "department_name": setup.department.name,
            }
            for setup in camera_setups
        ]
        return JsonResponse(setup_list, safe=False, status=status.HTTP_200_OK)
    return JsonResponse({"error": "Unauthorized: Only superadmin can list camera setups."}, status=status.HTTP_403_FORBIDDEN)

# 2. Create CameraSetup (only accessible by superadmin)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_camera_setup(request):
    if request.user.role == 'superadmin':
        data = request.data
        try:
            camera = Camera.objects.get(id=data.get("camera_id"))
            department = Department.objects.get(id=data.get("department_id"))

            camera_setup = CameraSetup.objects.create(
                camera=camera,
                name=data.get("name"),
                integrate_with_access_control=data.get("integrate_with_access_control"),
                entry_exit=data.get("entry_exit") if data.get("integrate_with_access_control") else None,
                department=department
            )
            return JsonResponse({"success": "Camera setup created successfully", "id": camera_setup.id}, status=status.HTTP_201_CREATED)
        except (Camera.DoesNotExist, Department.DoesNotExist):
            return JsonResponse({"error": "Invalid camera or department ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({"error": "Unauthorized: Only superadmin can create camera setups."}, status=status.HTTP_403_FORBIDDEN)

# 3. Edit CameraSetup (only accessible by superadmin)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_camera_setup(request, setup_id):
    if request.user.role == 'superadmin':
        try:
            camera_setup = CameraSetup.objects.get(id=setup_id)
            data = request.data

            camera = Camera.objects.get(id=data.get("camera_id"))
            department = Department.objects.get(id=data.get("department_id"))

            camera_setup.name = data.get("name", camera_setup.name)
            camera_setup.camera = camera
            camera_setup.integrate_with_access_control = data.get("integrate_with_access_control", camera_setup.integrate_with_access_control)
            camera_setup.entry_exit = data.get("entry_exit") if data.get("integrate_with_access_control") else None
            camera_setup.department = department
            camera_setup.save()

            return JsonResponse({"success": f"Camera setup '{camera_setup.name}' updated successfully."}, status=status.HTTP_200_OK)
        except CameraSetup.DoesNotExist:
            return JsonResponse({"error": "Camera setup not found."}, status=status.HTTP_404_NOT_FOUND)
        except (Camera.DoesNotExist, Department.DoesNotExist):
            return JsonResponse({"error": "Invalid camera or department ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({"error": "Unauthorized: Only superadmin can edit camera setups."}, status=status.HTTP_403_FORBIDDEN)

# 4. Delete CameraSetup (only accessible by superadmin)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_camera_setup(request, setup_id):
    if request.user.role == 'superadmin':
        try:
            camera_setup = CameraSetup.objects.get(id=setup_id)
            camera_setup.delete()
            return JsonResponse({"success": "Camera setup deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except CameraSetup.DoesNotExist:
            return JsonResponse({"error": "Camera setup not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({"error": "Unauthorized: Only superadmin can delete camera setups."}, status=status.HTTP_403_FORBIDDEN)












from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Camera, Department, CameraSetup
from django.contrib.auth.decorators import login_required

@login_required
def manage_camera_setups(request):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    cameras = Camera.objects.all()  # Fetch all cameras
    departments = Department.objects.all()  # Fetch all departments
    camera_setups = CameraSetup.objects.all()  # Fetch all existing camera setups

    # Handle POST request for creating a new camera setup
    if request.method == 'POST':
        camera_id = request.POST.get('camera_id')
        department_id = request.POST.get('department_id')
        integrate_with_access_control = request.POST.get('integrate_with_access_control') == 'on'
        entry_exit = request.POST.get('entry_exit') if integrate_with_access_control else None

        try:
            camera = Camera.objects.get(id=camera_id)
            department = Department.objects.get(id=department_id)

            # Create a new camera setup
            camera_setup = CameraSetup.objects.create(
                camera=camera,
                department=department,
                integrate_with_access_control=integrate_with_access_control,
                entry_exit=entry_exit
            )
            messages.success(request, f"Camera Setup '{camera_setup.camera.camera_id}' created successfully.")
            return redirect('manage_camera_setups_template')  # Redirect to refresh the page

        except Camera.DoesNotExist:
            messages.error(request, "Invalid Camera ID.")
        except Department.DoesNotExist:
            messages.error(request, "Invalid Department ID.")

    return render(request, 'manage_camera_setups.html', {
        'cameras': cameras,
        'departments': departments,
        'camera_setups': camera_setups
    })

@login_required
def edit_camera_setup(request, setup_id):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    camera_setup = get_object_or_404(CameraSetup, id=setup_id)
    cameras = Camera.objects.all()
    departments = Department.objects.all()

    if request.method == 'POST':
        camera_setup.name = request.POST.get('name', camera_setup.name)
        camera_id = request.POST.get('camera_id')
        department_id = request.POST.get('department_id')
        integrate_with_access_control = request.POST.get('integrate_with_access_control') == 'on'
        entry_exit = request.POST.get('entry_exit') if integrate_with_access_control else None

        try:
            camera = Camera.objects.get(id=camera_id)
            department = Department.objects.get(id=department_id)
            camera_setup.camera = camera
            camera_setup.department = department
        except (Camera.DoesNotExist, Department.DoesNotExist):
            messages.error(request, "Invalid Camera or Department ID provided.")
            return redirect('edit_camera_setup_template', setup_id=camera_setup.id)

        camera_setup.integrate_with_access_control = integrate_with_access_control
        camera_setup.entry_exit = entry_exit
        camera_setup.save()
        messages.success(request, f"Camera setup '{camera_setup.name}' updated successfully.")
        return redirect('manage_camera_setups_template')

    return render(request, 'edit_camera_setup.html', {'camera_setup': camera_setup, 'cameras': cameras, 'departments': departments})

@login_required
def delete_camera_setup(request, setup_id):
    # Restrict access to superadmins only
    if not request.user.is_superuser and request.user.role != 'superadmin':
        return JsonResponse({"error": "Unauthorized: Only Super Admin can access this page."}, status=403)

    camera_setup = get_object_or_404(CameraSetup, id=setup_id)

    if request.method == 'POST':
        camera_setup.delete()
        messages.success(request, f"Camera setup '{camera_setup.name}' deleted successfully.")
        return redirect('manage_camera_setups_template')

    return render(request, 'confirm_delete_camera_setup.html', {'camera_setup': camera_setup})




from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# @login_required
# def change_password(request):
#     if request.method == 'GET':
#         return render(request, 'change_password.html')

#     if request.method == 'POST':
#         employee_code = request.POST.get('employee_code')
#         current_password = request.POST.get('current_password')
#         new_password = request.POST.get('new_password')

#         user = request.user

#         if user.employee_code != employee_code:
#             return JsonResponse({"error": "Employee code does not match."}, status=400)

#         if not user.check_password(current_password):
#             return JsonResponse({"error": "Current password is incorrect."}, status=400)

#         if not validate_password(new_password):
#             return JsonResponse({"error": "Password must contain at least one uppercase letter, one lowercase letter, and one special character."}, status=400)

#         # Change the password and keep the user logged in
#         user.set_password(new_password)
#         user.save()
#         update_session_auth_hash(request, user)  # Keep the user logged in after password change

#         # Redirect to a success page
#         return redirect('password_change_success')



from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from django.shortcuts import render, redirect

@login_required
def change_password(request):
    if request.method == 'GET':
        return render(request, 'change_password.html')

    if request.method == 'POST':
        employee_code = request.POST.get('employee_code')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        user = request.user

        if user.employee_code != employee_code:
            return JsonResponse({"error": "Employee code does not match."}, status=400)

        if not user.check_password(current_password):
            return JsonResponse({"error": "Current password is incorrect."}, status=400)

        try:
            validate_password(new_password, user)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Change the password
        user.set_password(new_password)
        user.save()

        # Log out the user after changing the password
        logout(request)

        # Redirect to login page with a success message
        return redirect('login')


from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import logout

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_api(request):
    """
    API endpoint for changing the user's password.
    """
    employee_code = request.data.get('employee_code')
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    user = request.user

    if user.employee_code != employee_code:
        return Response({"error": "Employee code does not match."}, status=400)

    if not user.check_password(current_password):
        return Response({"error": "Current password is incorrect."}, status=400)

    try:
        validate_password(new_password, user)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    # Change the password
    user.set_password(new_password)
    user.save()

    # Log out the user programmatically
    logout(request)

    return Response({"message": "Password changed successfully. Please log in with your new password."}, status=200)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

# @api_view(['POST'])
# @permission_classes([AllowAny])  # Allows non-authenticated users to access this endpoint
# def login(request):
#     """
#     Login endpoint for generating an authentication token.
#     """
#     employee_code = request.data.get('employee_code')
#     password = request.data.get('password')
    
#     if not employee_code or not password:
#         return Response({"error": "Employee code and password are required."}, status=400)
    
#     user = authenticate(request, username=employee_code, password=password)
    
#     if user is not None:
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({"token": token.key})
#     else:
#         return Response({"error": "Invalid credentials."}, status=401)

# @api_view(['POST'])
# def logout(request):
#     """
#     Logout endpoint for invalidating the user's token.
#     """
#     if request.user.is_authenticated:
#         request.user.auth_token.delete()
#         return Response({"message": "Logged out successfully."})
#     else:
#         return Response({"error": "User is not authenticated."}, status=401)






from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

@csrf_protect
def login_view(request):
    """
    View for handling form-based login for browser access.
    """
    if request.method == 'POST':
        employee_code = request.POST.get('employee_code')
        password = request.POST.get('password')

        try:
            user = User.objects.get(employee_code=employee_code)
            if user.check_password(password):
                login(request, user)
                return redirect('home')  # Redirect to home for browser login
            else:
                return JsonResponse({'error': 'Invalid password'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid employee code'}, status=400)

    return render(request, 'login.html')


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    API endpoint for token-based login (Postman).
    """
    employee_code = request.data.get('employee_code')
    password = request.data.get('password')

    if not employee_code or not password:
        return Response({"error": "Employee code and password are required."}, status=400)

    user = authenticate(username=employee_code, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    else:
        return Response({"error": "Invalid credentials."}, status=401)


def home_view(request):
    """
    Home page view for authenticated users.
    """
    if request.user.is_authenticated:
        return render(request, 'home.html', {'user_name': request.user.name})
    return redirect('login')


def logout_view(request):
    """
    Logout view for browser-based sessions.
    """
    logout(request)
    return redirect('login')


@api_view(['POST'])
def api_logout(request):
    """
    API endpoint for token-based logout (Postman).
    """
    if request.user.is_authenticated:
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully."})
    else:
        return Response({"error": "User is not authenticated."}, status=401)



from django.shortcuts import render
from django.http import JsonResponse

def home_template_api(request):
    """
    API endpoint to provide the home.html template content.
    """
    context = {
        "user_name": request.user.name if request.user.is_authenticated else "Guest",
        "user_role": request.user.role if request.user.is_authenticated else None
    }

    # Render the template with the context
    html_content = render(request, 'home.html', context).content.decode('utf-8')

    return JsonResponse({
        "template": html_content
    })









###Security alert


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serial_control import send_command, emergency_active, set_emergency_status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def emergency_control(request):
    # Check if user is security
    if request.user.role != 'security':
        return Response({"error": "Only security personnel can access this feature"}, 
                      status=status.HTTP_403_FORBIDDEN)

    action = request.data.get('action')
    
    if action == 'activate':
        set_emergency_status(True)
        send_command('open')
        return Response({"status": "Emergency mode activated", "door": "open"}, 
                      status=status.HTTP_200_OK)
    
    elif action == 'deactivate':
        set_emergency_status(False)
        send_command('close')
        return Response({"status": "Emergency mode deactivated", "door": "closed"}, 
                      status=status.HTTP_200_OK)
    
    return Response({"error": "Invalid action. Use 'activate' or 'deactivate'"}, 
                  status=status.HTTP_400_BAD_REQUEST)