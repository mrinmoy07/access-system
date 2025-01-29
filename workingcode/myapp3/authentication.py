# myapp3/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User

class EmployeeIDAuthentication(BaseAuthentication):
    def authenticate(self, request):
        employee_code = request.headers.get('Employee-ID')  # Expecting Employee ID in headers
        if not employee_code:
            return None

        try:
            user = User.objects.get(employee_code=employee_code)
        except User.DoesNotExist:
            raise AuthenticationFailed('No such user')

        return (user, None)  # Return user and None for the auth
