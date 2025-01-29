# myapp/validators.py
import re
from django.core.exceptions import ValidationError

class ComplexPasswordValidator:
    def __init__(self):
        self.uppercase_regex = r'[A-Z]'  # At least one uppercase letter
        self.lowercase_regex = r'[a-z]'  # At least one lowercase letter
        self.special_char_regex = r'[!@#$%^&*()_+\-=\[\]{}|;:\'",<>\./?]'  # At least one special character
        self.alphanumeric_regex = r'[0-9]'  # At least one number
        self.min_length = 8  # Minimum password length

    def validate(self, password, user=None):
        # Check if password has at least one uppercase letter
        if not re.search(self.uppercase_regex, password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        # Check if password has at least one lowercase letter
        if not re.search(self.lowercase_regex, password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        # Check if password has at least one special character
        if not re.search(self.special_char_regex, password):
            raise ValidationError("Password must contain at least one special character.")
        
        # Check if password has at least one numeric character
        if not re.search(self.alphanumeric_regex, password):
            raise ValidationError("Password must contain at least one numeric character.")
        
        # Check if password meets the minimum length requirement
        if len(password) < self.min_length:
            raise ValidationError(f"Password must be at least {self.min_length} characters long.")

    def get_help_text(self):
        return (
            f"Your password must contain at least one uppercase letter, "
            f"one lowercase letter, one special character, one numeric character, "
            f"and be at least {self.min_length} characters long."
        )
