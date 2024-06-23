from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy as _

# def limit_validator(min_value, max_value):
#     if (value.size > self.max_size) or (self.min_size > value.size):
#         return False
#     return True

            
class SizeValidator(BaseValidator):

    def __init__(self, max_size, min_size=0):
        self.max_size=max_size
        self.min_size=min_size

    def __call__(self, value):
        if (value.size > self.max_size) or (self.min_size > value.size):
            raise ValidationError(_(f"Size {value!s} incorrect"))
