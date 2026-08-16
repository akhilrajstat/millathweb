"""
apps/core/views.py
==================
Public website core views: Homepage, About Us, and Contact Us.
"""

from django.views.generic import TemplateView
from apps.core.models import HomePageBanner
from apps.programs.models import Program
from apps.notices.models import Notice
from apps.gallery.models import GalleryImage


class HomeView(TemplateView):
    """
    Homepage view rendering hero banners, latest programs, recent notices,
    and photo gallery highlights.
    """

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["banners"] = HomePageBanner.objects.filter(is_active=True).order_by("display_order", "-id")
        context["programs"] = Program.objects.filter(is_active=True).order_by("name")[:6]
        context["notices"] = Notice.objects.filter(is_active=True).order_by("-publish_date", "-id")[:3]
        context["gallery_images"] = GalleryImage.objects.all().order_by("display_order", "-upload_date")[:8]
        return context


class AboutView(TemplateView):
    """
    About Us page presenting the institution history, vision, mission, and leadership.
    """

    template_name = "about.html"


class ContactView(TemplateView):
    """
    Contact Us page rendering contact info and a simple enquiry form.
    """

    template_name = "contact.html"


class ComingSoonView(TemplateView):
    """
    Graceful Coming Soon view for planned institutional modules and services.
    Accepts a feature slug via URL parameter (e.g. 'digital-library') or query parameter.
    """

    template_name = "coming_soon.html"

    FEATURE_METADATA = {
        "digital-library": {
            "title": "Digital Library & E-Resource Portal",
            "category": "Academic Resources",
            "description": "We are currently digitizing thousands of teacher education journals, reference volumes, research archives, and audio-visual pedagogical assets.",
            "icon": "bi-book-half",
            "eta": "Phase 2 Academic Rollout",
        },
        "fee-payment": {
            "title": "Online Fee Payment Portal",
            "category": "Student Services & Accounts",
            "description": "A secure integrated payment gateway for semester tuition fees, receipt generation, and scholarship reconciliations is being configured.",
            "icon": "bi-credit-card-2-front",
            "eta": "Next Financial Quarter",
        },
        "fee-management": {
            "title": "Fee Management & Accounts Ledger",
            "category": "Institutional Finance",
            "description": "Comprehensive fee scheduling, fee structure configurations, and ledger analytics for administrative staff are undergoing final integration.",
            "icon": "bi-cash-coin",
            "eta": "Next Financial Quarter",
        },
        "attendance": {
            "title": "Smart Attendance Tracking System",
            "category": "Academic Administration",
            "description": "Digital period-wise student attendance logging, monthly percentage calculations, and university compliance reports are under active development.",
            "icon": "bi-calendar-check",
            "eta": "Upcoming Academic Term",
        },
        "attendance-tracker": {
            "title": "Student Attendance Portal",
            "category": "Academic Administration",
            "description": "Track your semester attendance percentages, leave requests, and NCTE mandatory practicum hour logs digitally.",
            "icon": "bi-calendar-check",
            "eta": "Upcoming Academic Term",
        },
        "attendance-analytics": {
            "title": "Institutional Attendance Analytics",
            "category": "Executive Reporting",
            "description": "College-wide attendance dashboards, department-wise compliance heatmaps, and University of Kerala semester eligibility reports.",
            "icon": "bi-bar-chart-line-fill",
            "eta": "Upcoming Academic Term",
        },
        "alumni-forum": {
            "title": "Alumni Association & Network",
            "category": "Institutional Community",
            "description": "An exclusive interactive network uniting Millath College educators across Kerala and worldwide for mentorship, school placements, and reunions.",
            "icon": "bi-mortarboard",
            "eta": "Annual Alumni Meet Rollout",
        },
        "student-forum": {
            "title": "Student Activity Corner & Clubs",
            "category": "Campus Life & Extracurriculars",
            "description": "A dedicated digital hub for collegiate literary, cultural, nature, micro-teaching, and community outreach clubs.",
            "icon": "bi-people-fill",
            "eta": "Upcoming Semester",
        },
        "student-activities": {
            "title": "Student Activity Corner & Clubs",
            "category": "Campus Life & Extracurriculars",
            "description": "A dedicated digital hub for collegiate literary, cultural, nature, micro-teaching, and community outreach clubs.",
            "icon": "bi-stars",
            "eta": "Upcoming Semester",
        },
        "payroll-system": {
            "title": "Staff Payroll & Salary Statements",
            "category": "Human Resources",
            "description": "Self-service digital monthly pay slips, provident fund records, and institutional benefits portal for faculty and staff members.",
            "icon": "bi-wallet2",
            "eta": "Next Administrative Release",
        },
        "payroll-management": {
            "title": "Staff Payroll & HR Ledger",
            "category": "Human Resources Administration",
            "description": "Administrative salary disbursements, allowance configurations, tax deductions, and compliance records.",
            "icon": "bi-cash-stack",
            "eta": "Next Administrative Release",
        },
        "mobile-app": {
            "title": "Millath ERP Mobile App",
            "category": "Mobile Technology",
            "description": "Dedicated Android & iOS mobile applications with push notifications for notices, coursework submissions, and academic alerts.",
            "icon": "bi-phone",
            "eta": "App Store & Play Store Release",
        },
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get("feature") or self.request.GET.get("feature", "planned-feature")
        slug = slug.strip().lower()

        meta = self.FEATURE_METADATA.get(slug)
        if meta:
            context["feature_name"] = meta["title"]
            context["feature_category"] = meta.get("category", "Planned Module")
            context["feature_desc"] = meta.get("description")
            context["feature_icon"] = meta.get("icon", "bi-stars")
            context["feature_eta"] = meta.get("eta", "Coming Soon")
        else:
            clean_title = slug.replace("-", " ").replace("_", " ").title()
            context["feature_name"] = clean_title
            context["feature_category"] = "Institutional Module"
            context["feature_desc"] = (
                f"The {clean_title} module is currently under active development as part "
                "of the Millath College digital transformation roadmap."
            )
            context["feature_icon"] = "bi-stars"
            context["feature_eta"] = "Coming Soon"

        context["feature_slug"] = slug
        return context
