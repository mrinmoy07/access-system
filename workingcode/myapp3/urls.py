from django.urls import path
from django.shortcuts import render
from .views import DeleteGuest, ListGuest, ShiftDeleteTemplateView, ShiftAssignmentListTemplateView, ShiftListTemplateView, ListHolidayTemplateView, ListDepartmentTemplateView, ListOrganizationView, ListOrganizationTemplateView, UserEditTemplateView, CreateOrganizationView, CreateOrganizationTemplateView, CreateDepartmentView, CreateDepartmentTemplateView, CreateUserBySuperuser, CreateUserBySuperuserTemplate, create_user_by_hr, CreateUserHrTemplate, create_holiday_list, CreateHolidayListTemplate, verify_holiday, VerifyHolidayTemplate, create_shift, CreateShiftTemplate, assign_shift, AssignShiftTemplate, create_guest, CreateGuestTemplate, approve_guest, ApproveGuest, FaceMatchView, AttendanceReportView, login_view, home_view, logout_view, UserListView, UserDeleteView, PendingHolidayListView, ApprovedHolidayListView, ShiftListView, ShiftDeleteView, list_guests, delete_guest,UserListTemplateView,UserDeleteTemplateView,UserEditView


# GuestAttendanceReportView, UserAttendanceReportView
# create_organization
from .views import CustomAuthToken,UserEditTemplateView,DeleteOrganizationTemplateView, DeleteDepartmentTemplateView, EditOrganizationTemplateView, EditDepartmentTemplateView,manage_locks,EditOrganizationTemplateView,ListDepartmentView,UserAttendanceReportAPIView,GuestAttendanceReportAPIView
#AttendanceReportAPIView
from . import views
urlpatterns = [
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    # path('create-organization/', create_organization, name='create_organization'),
    path('api/organizations/', ListOrganizationView.as_view(), name='list_organizations'),  # For listing organizations
    path('api/organizations/create/', CreateOrganizationView.as_view(), name='create_organization'),
    path('organizations/', ListOrganizationTemplateView.as_view(), name='list_organizations_template'), # updating
    path('organizations/create/', CreateOrganizationTemplateView.as_view(), name='create_organization_template'), # updating
    path('organizations/delete/<int:organization_id>/', DeleteOrganizationTemplateView.as_view(), name='delete_organization_template'),
    path('organizations/edit/<int:organization_id>/', EditOrganizationTemplateView.as_view(), name='edit_organization_template'),



    path('api/departments/', ListDepartmentView.as_view(), name='list_departments'),  # For listing departments
    path('api/departments/create/', CreateDepartmentView.as_view(), name='create_department'),
    path('departments/', ListDepartmentTemplateView.as_view(), name='list_departments_template'), # updating
    path('departments/create/', CreateDepartmentTemplateView.as_view(), name='create_department_template'), # hupdating
    path('departments/delete/<int:department_id>/', DeleteDepartmentTemplateView.as_view(), name='delete_department_template'),
    path('departments/edit/<int:department_id>/', EditDepartmentTemplateView.as_view(), name='edit_department_template'),


    path('api/users/', UserListView.as_view(), name='user_list'),         # For listing users
    path('api/users/create/', CreateUserBySuperuser.as_view(), name='create_user'),
    path('api/users/create/hr/', create_user_by_hr, name='create_user_hr'),
    path('api/users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),  # For deleting a user by ID
    path('users/', UserListTemplateView.as_view(), name='user_list_template'), # updating
    path('users/create/', CreateUserBySuperuserTemplate.as_view(), name='create_user_template'), # updating
    path('users/create/hr/', CreateUserHrTemplate.as_view(), name='create_user_hr_template'),
    path('users/<int:user_id>/', UserEditTemplateView.as_view(), name='user'),  # For editing a user by ID
    path('users/<int:user_id>/delete/', UserDeleteTemplateView.as_view(), name='user_delete_template'),  # For deleting a user by ID

    path('api/holidays/create/', create_holiday_list, name='create_holiday'),
    path('api/holidays/<int:holiday_id>/verify/', verify_holiday, name='verify_holiday'),
    path('holidays/', ListHolidayTemplateView.as_view(), name='list_holidays_template'), # updating
    path('holidays/create/', CreateHolidayListTemplate.as_view(), name='create_holiday_template'), # updating
    path('holidays/<int:holiday_id>/verify/', VerifyHolidayTemplate.as_view(), name='verify_holiday_template'),
    path('api/holidays/', views.list_holidays, name='list_holidays'),

    path('api/shifts/', ShiftListView.as_view(), name='shift_list'), # updating
    path('api/shifts/create/', create_shift, name='create_shift'),
    path('api/shifts/<int:shift_id>/delete/', ShiftDeleteView.as_view(), name='shift_delete'),  # Shift deletion
    path('api/shifts/assignments/create', assign_shift, name='assign_shift'),
    path('shifts/', ShiftListTemplateView.as_view(), name='shift_list_template'), # updating
    path('shifts/create/', CreateShiftTemplate.as_view(), name='create_shift_template'), # hiupdating
    path('shifts/<int:shift_id>/delete/', ShiftDeleteTemplateView.as_view(), name='shift_delete_template'),  # Shift deletion
    path('shifts/assignments/', ShiftAssignmentListTemplateView.as_view(), name='shift_assignments_template'), # updating
    path('shifts/assignments/create/', AssignShiftTemplate.as_view(), name='assign_shift_template'), # updating

    path('api/guests/', list_guests, name='list_guests'),
    path('api/guesta/create/', create_guest, name='create_guest'),
    path('api/guests/<int:guest_id>/approve/', approve_guest, name='approve_guest'),
    path('api/guests/<int:guest_id>/delete/', delete_guest, name='delete_guest'),
    path('guests/', ListGuest.as_view(), name='list_guests_template'), # updating
    path('guests/create/', CreateGuestTemplate.as_view(), name='create_guest_template'), # updating
    path('guests/<int:guest_id>/approve/', ApproveGuest.as_view(), name='approve_guest_template'), #updating
    path('guests/<int:guest_id>/delete/', DeleteGuest.as_view(), name='delete_guest_template'), #updating

    path('face-match/', FaceMatchView.as_view(), name='face_match'),
    path('attendance-report/', AttendanceReportView.as_view(), name='attendance_report'),
    
    # path('guest-attendance-report/', GuestAttendanceReportView.as_view(), name='guest_attendance_report'),
    # path('user-attendance-report/', UserAttendanceReportView.as_view(), name='user_attendance_report'),
    # path('login/', login_view, name='login'),
    # path('home/', home_view, name='home'),
    # path('logout/', logout_view, name='logout'),
    path('holidays/pending/', PendingHolidayListView.as_view(), name='pending_holidays'),
    path('holidays/approved/', ApprovedHolidayListView.as_view(), name='approved_holidays'),
    path('shifts/', ShiftListView.as_view(), name='shift_list'),  # Shift listing
    path('shifts/<int:shift_id>/delete/', ShiftDeleteView.as_view(), name='shift_delete'),  # Shift deletion
    path('guests/', list_guests, name='list_guests'),
    path('guests/<int:guest_id>/', delete_guest, name='delete_guest'),
    path('api/user/<int:user_id>/edit/', UserEditView.as_view(), name='user_edit_api'),
    path('users/<int:user_id>/', UserEditTemplateView.as_view(), name='user_edit_template'),



    path('lock/create/', views.create_lock, name='create_lock'),
    path('lock/edit/<int:lock_id>/', views.edit_lock, name='edit_lock'),
    path('lock/delete/<int:lock_id>/', views.delete_lock, name='delete_lock'),
    
    path('camera/create/', views.create_camera, name='create_camera'),
    path('camera/edit/<int:camera_id>/', views.edit_camera, name='edit_camera'),
    path('camera/delete/<int:camera_id>/', views.delete_camera, name='delete_camera'),

    path('lock/list/', views.list_locks, name='list_locks'),
    path('camera/list/', views.list_cameras, name='list_cameras'),


    path('api/match-face/', views.match_face, name='match_face'),


    path('camera-setup/list/', views.list_camera_setups, name='list_camera_setups'),
    path('camera-setup/create/', views.create_camera_setup, name='create_camera_setup'),
    path('camera-setup/edit/<int:setup_id>/', views.edit_camera_setup, name='edit_camera_setup'),
    path('camera-setup/delete/<int:setup_id>/', views.delete_camera_setup, name='delete_camera_setup'),

    path('manage-locks/', manage_locks, name='manage_locks_template'),


    path('manage/cameras/', views.manage_cameras, name='manage_cameras_template'),
    path('manage/cameras/<int:camera_id>/edit/', views.edit_camera, name='edit_camera_template'),
    path('manage/cameras/<int:camera_id>/delete/', views.delete_camera, name='delete_camera_template'),




    path('camera_setups/manage/', views.manage_camera_setups, name='manage_camera_setups_template'),
    path('camera_setups/edit/<int:setup_id>/', views.edit_camera_setup, name='edit_camera_setup_template'),
    path('camera_setups/delete/<int:setup_id>/', views.delete_camera_setup, name='delete_camera_setup_template'),


    path('organizations/<int:organization_id>/edit/', EditOrganizationTemplateView.as_view(), name='edit_organization_template'),




    path('organization/edit/<int:organization_id>/', views.edit_organization, name='edit_organization'),
    path('organization/delete/<int:organization_id>/', views.delete_organization, name='delete_organization'),


    path('department/edit/<int:department_id>/', views.edit_department, name='edit_department'),
    path('department/delete/<int:department_id>/', views.delete_department, name='delete_department'),


    path('change-password/', views.change_password, name='change_password'),
    path('api/change-password/', views.change_password_api, name='change_password_api'),

    # path('api/login/', views.login, name='login'),
    # path('api/logout/', views.logout, name='logout'),



    path('login/', views.login_view, name='login'),  # Browser login
    path('api/login/', views.api_login, name='api_login'),  # API login (Postman)
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),  # Browser logout
    path('api/logout/', views.api_logout, name='api_logout'),  # API logout (Postman)

    path('password-change-success/', 
         lambda request: render(request, 'password_change_success.html'), name='password_change_success'),

    path('api/attendance/users/', UserAttendanceReportAPIView.as_view(), name='user-attendance-report'),
    path('api/attendance/guests/', GuestAttendanceReportAPIView.as_view(), name='guest-attendance-report'),

    path('api/home-template/', views.home_template_api, name='home_template_api'),

    path('api/emergency/', views.emergency_control, name='emergency-control'),

    

]
