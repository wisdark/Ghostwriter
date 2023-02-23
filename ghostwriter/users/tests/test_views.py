# Standard Libraries
import logging
from base64 import b64decode

# Django Imports
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

# Ghostwriter Libraries
from ghostwriter.factories import UserFactory

logging.disable(logging.CRITICAL)

PASSWORD = "SuperNaturalReporting!"


class UserDetailViewTests(TestCase):
    """Collection of tests for :view:`users.UserDetailView`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.uri = reverse("users:user_detail", kwargs={"username": cls.user.username})

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(self.client_auth.login(username=self.user.username, password=PASSWORD))

    def test_view_uri_exists_at_desired_location(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_uses_correct_template(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")


class UserUpdateViewTests(TestCase):
    """Collection of tests for :view:`users.UserUpdateView`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.other_user = UserFactory(password=PASSWORD)
        cls.uri = reverse("users:user_update", kwargs={"username": cls.user.username})
        cls.success_uri = reverse("users:user_detail", kwargs={"username": cls.user.username})

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(self.client_auth.login(username=self.user.username, password=PASSWORD))
        self.other_client_auth = Client()
        self.other_client_auth.login(username=self.other_user.username, password=PASSWORD)
        self.assertTrue(self.other_client_auth.login(username=self.other_user.username, password=PASSWORD))

    def test_view_uri_exists_at_desired_location(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_uses_correct_template(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile_form.html")

    def test_view_blocks_improper_access(self):
        response = self.other_client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_successfull_redirect(self):
        response = self.client_auth.post(
            self.uri,
            {
                "name": self.user.name,
                "email": self.user.email,
                "timezone": self.user.timezone,
                "phone": self.user.phone,
            },
        )
        self.assertRedirects(response, self.success_uri)


class UserProfileUpdateViewTests(TestCase):
    """Collection of tests for :view:`users.UserProfileUpdateView`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.other_user = UserFactory(password=PASSWORD)
        cls.uri = reverse("users:userprofile_update", kwargs={"username": cls.user.username})
        cls.redirect_uri = reverse("users:redirect")
        cls.success_uri = reverse("users:user_detail", kwargs={"username": cls.user.username})

        image_data = b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        image_file = ContentFile(image_data, "fake.png")
        cls.uploaded_image_file = SimpleUploadedFile(image_file.name, image_file.read(), content_type="image/png")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(self.client_auth.login(username=self.user.username, password=PASSWORD))
        self.other_client_auth = Client()
        self.other_client_auth.login(username=self.other_user.username, password=PASSWORD)
        self.assertTrue(self.other_client_auth.login(username=self.other_user.username, password=PASSWORD))

    def test_view_uri_exists_at_desired_location(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_uses_correct_template(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile_form.html")

    def test_view_blocks_improper_access(self):
        response = self.other_client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_successfull_redirect(self):
        response = self.client_auth.post(self.uri, {"avatar": self.uploaded_image_file})
        self.assertRedirects(response, self.success_uri)


class UserRedirectViewTests(TestCase):
    """Collection of tests for :view:`users.UserRedirectView`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.uri = reverse("users:redirect")
        cls.redirect_uri = reverse("users:user_detail", kwargs={"username": cls.user.username})

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(self.client_auth.login(username=self.user.username, password=PASSWORD))

    def test_view_uri_exists_at_desired_location(self):
        response = self.client_auth.get(self.uri)
        self.assertRedirects(response, self.redirect_uri)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)


class GhostwriterPasswordChangeViewTests(TestCase):
    """Collection of tests for :view:`users.GhostwriterPasswordChangeView`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.uri = reverse("account_change_password")
        cls.success_uri = reverse("users:user_detail", kwargs={"username": cls.user.username})

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(self.client_auth.login(username=self.user.username, password=PASSWORD))

    def test_view_uri_exists_at_desired_location(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_successfull_redirect(self):
        response = self.client_auth.post(
            self.uri,
            {"oldpassword": PASSWORD, "password1": "IxIGx58vy79hS&sju#Ea", "password2": "IxIGx58vy79hS&sju#Ea"},
        )
        self.assertRedirects(response, self.success_uri)
        self.user.password = PASSWORD
        self.user.save()


class UserLoginViewTests(TestCase):
    """Collection of tests for :view:`allauth.Login`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.uri = reverse("account_login")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(self.client_auth.login(username=self.user.username, password=PASSWORD))

    def test_view_uri_exists_at_desired_location(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_authenticated(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

    def test_valid_credentials(self):
        response = self.client.post(self.uri, {"login": self.user.username, "password": PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, "account/messages/logged_in.txt")

    def test_invalid_credentials(self):
        response = self.client.post(self.uri, {"login": self.user.username, "password": "invalid"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")
