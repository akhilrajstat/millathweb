"""
apps/accounts/management/commands/create_groups.py
====================================================
Management command that idempotently creates Django Groups matching
each role defined in UserRole.

Usage
-----
    python manage.py create_groups

Safe to run multiple times — uses get_or_create so existing groups
are not duplicated or altered.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.models import UserRole


class Command(BaseCommand):
    help = "Creates Django Groups for every UserRole if they do not already exist."

    # Map role label → group name (labels come from UserRole.choices).
    # Adding a new role to UserRole automatically picks it up here.
    GROUP_NAMES = [label for _, label in UserRole.choices]

    def handle(self, *args, **options):
        created_count = 0

        for group_name in self.GROUP_NAMES:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  [CREATED] Group: '{group_name}'")
                )
            else:
                self.stdout.write(f"  [EXISTS]  Group: '{group_name}'")

        summary = (
            f"\nDone. {created_count} group(s) created, "
            f"{len(self.GROUP_NAMES) - created_count} already existed."
        )
        self.stdout.write(self.style.SUCCESS(summary))
