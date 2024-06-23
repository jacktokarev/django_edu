from django.db import models
from django.contrib.auth.models import User
from .validators import SizeValidator


def get_user_avatar_path(instance: "Profile", filename: str) -> str:
    return f"myauth/users/user_{instance.user.pk!s}/avatars/{filename!s}"


class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        null=True, blank=True,
        upload_to=get_user_avatar_path,
        validators=[SizeValidator(51200)],
    )
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
