from os import name
from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group, Permission


class Command(BaseCommand):

    def handle(self, *args, **options) -> str | None:
        user = User.objects.get(pk=3)
        group, created = Group.objects.get_or_create(
            name="profile_manager",
        )
        permissions_profile = Permission.objects.get(
            codename="view_profile",
        )
        permission_logentry = Permission.objects.get(
            codename="view_logentry",
        )
        # полномочия группы
        group.permissions.add(permissions_profile)
        # добавление пользователя в группу
        user.groups.add(group)
        # личные полномочия пользователя
        user.user_permissions.add(permission_logentry)

        group.save()
        user.save()
