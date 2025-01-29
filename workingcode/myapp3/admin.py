from django.contrib import admin
from .models import Department, Organization, User 

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'gst_no', 'no_of_employees', 'access_control')
    search_fields = ('name', 'address')

admin.site.register(Organization, OrganizationAdmin)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'integrate_with_ai_camera')  # Display fields in the admin list view
    search_fields = ('name',)  # Enable searching by department name

# Register the Department model
admin.site.register(Department, DepartmentAdmin)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User  # Make sure to import your custom User model

class UserAdmin(BaseUserAdmin):
    # Fields to be displayed in the list view
    list_display = (
        'employee_code', 'name', 'role', 'department', 'organization', 
        'designation', 'blood_group', 'emergency_contact', 'is_staff', 
        'is_superuser', 'created_by', 'date_joined','can_create_guest_pass'
    )

    # Fields to be used for search functionality
    search_fields = ('name', 'employee_code', 'role')

    # Fields to filter the list view
    list_filter = ('role', 'department', 'organization', 'is_staff', 'is_superuser')

    # Fields to be displayed in the detail view
    fieldsets = (
        (None, {'fields': ('employee_code', 'name', 'role', 'department', 'organization', 'designation')}),
        ('Contact Details', {'fields': ('blood_group', 'emergency_contact', 'photo')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'created_by')}),
        ('Other Information', {'fields': ('date_joined',)}),
    )

    # Optional: specify the ordering of the list view
    ordering = ('name',)

# Register the User model with the custom UserAdmin
admin.site.register(User, UserAdmin)



# myapp3/admin.py

from django.contrib import admin
from .models import Holiday

# class HolidayAdmin(admin.ModelAdmin):
#     list_display = ('created_by', 'holiday_dates', 'is_verified', 'created_at')  # Fields to display in the list view
#     search_fields = ('created_by__name',)  # Enable searching by HR's name
#     list_filter = ('is_verified',)  # Filter by verification status
#     ordering = ('-created_at',)  # Order by creation date (newest first)

# admin.site.register(Holiday, HolidayAdmin)

class HolidayAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'holiday_dates', 'is_verified', 'created_at')  # Fields to display in the list view
    search_fields = ('created_by__name',)  # Enable searching by HR's name
    list_filter = ('is_verified',)  # Filter by verification status
    ordering = ('-created_at',)  # Order by creation date (newest first)

    def save_model(self, request, obj, change):
        # Ensure only admins can set is_verified to True
        if obj.is_verified and not request.user.is_superuser:
            obj.is_verified = False  # Reset verification status if trying to set it as verified by non-admin
        super().save_model(request, obj, change)

admin.site.register(Holiday, HolidayAdmin)




from django.contrib import admin
from .models import Shift, EmployeeShiftAssignment
# Registering Shift model
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('shift_name', 'shift_start_time', 'shift_end_time', 'total_work_time', 'total_break_time', 'created_by', 'created_at')
    search_fields = ('shift_name', 'created_by__username')
    list_filter = ('created_at', 'created_by')
    ordering = ('-created_at',)

# Registering EmployeeShiftAssignment model
@admin.register(EmployeeShiftAssignment)
class EmployeeShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift', 'weekly_holiday', 'government_holiday_applicable', 'earned_leave_qty', 'paid_leave_qty', 'casual_leave_qty', 'applicable_from', 'assigned_by', 'created_at')
    search_fields = ('employee__username', 'shift__shift_name', 'assigned_by__username')
    list_filter = ('weekly_holiday', 'government_holiday_applicable', 'applicable_from', 'assigned_by')
    ordering = ('-created_at',)



from django.contrib import admin
from .models import Guest

class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'visit_date', 'start_time', 'end_time', 'organization', 'department', 'person_to_meet', 'requested_by', 'is_approved')
    search_fields = ('name', 'organization__name', 'department__name', 'person_to_meet', 'requested_by__name')
    list_filter = ('is_approved', 'organization', 'department')
    ordering = ('-visit_date',)
    fields = ('name', 'photo', 'visit_date', 'start_time', 'end_time', 'organization', 'department', 'person_to_meet', 'requested_by', 'is_approved', 'approved_by', 'approved_at')

admin.site.register(Guest, GuestAdmin)
