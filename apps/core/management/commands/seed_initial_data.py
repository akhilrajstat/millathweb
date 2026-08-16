"""
apps/core/management/commands/seed_initial_data.py
==================================================
Idempotent data seeder for Millath College of Teacher Education.
Populates official institutional SiteSettings and the six core B.Ed degree
specializations sourced from the college's existing establishment records.

Usage:
    python manage.py seed_initial_data

===============================================================================
REFERENCE STAFF ROSTER (15 Verified Staff Members from Official College Records):
===============================================================================
1.  Saritha K.R          — Administrative Officer
2.  Bindu kumari C.S     — Assistant Professor
3.  Suba Basheer         — Assistant Professor
4.  Shemi Mole A         — Assistant Professor
5.  USHA K               — Assistant Professor
6.  Sharanya M           — Assistant Professor
7.  Saju Illias          — Assistant Professor
8.  Deepthy C            — Assistant Professor
9.  RAJANI R             — Assistant Professor
10. Neenu Thomas         — Assistant Professor
11. Sini R               — Librarian
12. BINU.P               — Technical Assistant
13. AKSHAYA S R          — Assistant Professor
14. Akhilnath.K          — Librarian
15. Rajesh Balakrishnan  — Assistant Professor
===============================================================================
NOTE FOR OFFICE STAFF / ADMINISTRATORS:
Exact designations, subject specializations, and qualifications beyond "Assistant
Professor" were not confirmed from the source records. Office staff must verify
and fill in the exact designation, subject specialization, and qualifications
for each person via the Django admin panel when creating or updating their
FacultyProfile records. Do not fabricate degrees or specializations for any of them.
===============================================================================
"""

from django.core.management.base import BaseCommand
from apps.core.models import SiteSettings
from apps.programs.models import Program


class Command(BaseCommand):
    help = "Seeds official institutional content for Millath College of Teacher Education (Idempotent)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("-> Starting initial data seeding for Millath College..."))

        # ---------------------------------------------------------------------
        # 1. SiteSettings (Singleton)
        # ---------------------------------------------------------------------
        # Address note: "Sooranadu, Kollam, Kerala, India" is a verified base location.
        # Exact postal door/pincode to be finalized by the college office via admin.
        # Phone and email are intentionally left blank as requested until provided.
        settings_obj = SiteSettings.get_solo()
        settings_obj.college_name = "Millath College of Teacher Education"
        settings_obj.tagline = "Shaping Future Educators with Excellence & Values"
        settings_obj.address = "Sooranadu, Kollam, Kerala, India"
        # If logo points to a non-existent media file, reset it so the static fallback is used
        if settings_obj.logo:
            try:
                if not settings_obj.logo.storage.exists(settings_obj.logo.name):
                    settings_obj.logo = None
            except Exception:
                settings_obj.logo = None
        settings_obj.footer_text = "© Millath College of Teacher Education. Affiliated to University of Kerala. NCTE Approved."
        settings_obj.save()

        self.stdout.write(
            self.style.SUCCESS(f"  [OK] SiteSettings updated: '{settings_obj.college_name}'")
        )

        # ---------------------------------------------------------------------
        # 2. Academic Programs (6 B.Ed Specializations)
        # ---------------------------------------------------------------------
        specializations = [
            "English",
            "Mathematics",
            "Physical Science",
            "Natural Science",
            "Social Science",
            "Commerce",
        ]

        generic_description = (
            "<p>The Bachelor of Education (B.Ed) is a two-year professional degree program "
            "affiliated to the University of Kerala and recognised by the National Council for "
            "Teacher Education (NCTE). The curriculum encompasses foundational theoretical perspectives, "
            "subject-specific pedagogical methodologies, hands-on teaching internships, and digital "
            "classroom innovations.</p>"
            "<p class='text-muted small'><em>[Content to be finalized by college office: detailed syllabus and course modules]</em></p>"
        )

        generic_eligibility = (
            "Candidates should possess a Bachelor's Degree (B.A./B.Sc./B.Com) or Master's Degree "
            "in the relevant discipline with minimum 50% marks (or equivalent CGPA) from a recognised university, "
            "subject to relaxation norms for reserved categories as mandated by the University of Kerala and Government of Kerala.\n\n"
            "[Content to be finalized by college office: category-wise reservation percentage and admission quota details]"
        )

        created_count = 0
        updated_count = 0

        for subject in specializations:
            prog_name = f"B.Ed - {subject}"
            prog, created = Program.objects.update_or_create(
                name=prog_name,
                defaults={
                    "duration": "2 Years",
                    "description": generic_description,
                    "eligibility": generic_eligibility,
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  + [CREATED] Program: {prog_name}"))
            else:
                updated_count += 1
                self.stdout.write(f"  ~ [UPDATED] Program: {prog_name}")

        # ---------------------------------------------------------------------
        # 3. Default Super Admin User
        # ---------------------------------------------------------------------
        from apps.accounts.models import User, UserRole
        from django.contrib.auth.models import Group

        admin_user, admin_created = User.objects.get_or_create(
            username="collegeadmin",
            defaults={
                "email": "millathcollege669@yahoo.com",
                "first_name": "saritha",
                "last_name": "admin",
                "role": UserRole.SUPER_ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "is_approved": True,
            },
        )
        admin_user.set_password("Saritha@6123")
        admin_user.email = "millathcollege669@yahoo.com"
        admin_user.first_name = "saritha"
        admin_user.last_name = "admin"
        admin_user.role = UserRole.SUPER_ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.is_approved = True
        admin_user.save()

        super_group = Group.objects.filter(name="Super Admin").first()
        if super_group:
            admin_user.groups.add(super_group)

        self.stdout.write(
            self.style.SUCCESS(
                f"  [OK] Default Super Admin 'collegeadmin' verified and active."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeeding complete! Site settings configured, {created_count} program(s) created, "
                f"{updated_count} updated, and superadmin verified."
            )
        )

