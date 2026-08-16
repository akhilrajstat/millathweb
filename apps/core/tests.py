from django.test import TestCase, Client, override_settings
from django.urls import reverse


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
    }
)
class ComingSoonViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_coming_soon_default_page_loads(self):
        url = reverse("core:coming_soon_default")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "is coming soon")

    def test_coming_soon_digital_library(self):
        url = reverse("core:coming_soon", kwargs={"feature": "digital-library"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Digital Library")

    def test_coming_soon_fee_payment(self):
        url = reverse("core:coming_soon", kwargs={"feature": "fee-payment"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fee Payment")

    def test_coming_soon_attendance(self):
        url = reverse("core:coming_soon", kwargs={"feature": "attendance"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Attendance")

    def test_coming_soon_alumni_forum(self):
        url = reverse("core:coming_soon", kwargs={"feature": "alumni-forum"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alumni")

    def test_coming_soon_custom_feature_fallback(self):
        url = reverse("core:coming_soon", kwargs={"feature": "novel-feature-test"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Novel Feature Test")
