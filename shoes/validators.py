import phonenumbers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_file_extension(value, message='Unsupported file Type.'):
    import os
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.jpg', '.png', '.jpeg', '.webp']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_(message))


def validate_phone_number(value):
    try:
        x = phonenumbers.parse(value, None)
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError(_("Invalid phone number format, enter an E-164 or International formatted string"))
    else:
        if not phonenumbers.is_valid_number(x):
            raise ValidationError(_("Invalid phone number"))

def validate_password(value):
    if len(value) < 8:
            raise ValidationError(_("Password must be at least 8 characters long"))
    if value.isalpha():
        raise ValidationError(_("Password must contain at least a number"))