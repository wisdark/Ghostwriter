# Standard Libraries
import logging
from datetime import date, timedelta

# Django Imports
from django.conf import settings
from django.db.models import Q
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

# Ghostwriter Libraries
from ghostwriter.factories import (
    GroupFactory,
    ProjectAssignmentFactory,
    ProjectFactory,
    ProjectObjectiveFactory,
    ReportFactory,
    ReportFindingLinkFactory,
    UserFactory,
)
from ghostwriter.home.templatetags import custom_tags

logging.disable(logging.CRITICAL)

PASSWORD = "SuperNaturalReporting!"


# Tests related to custom template tags and filters


class TemplateTagTests(TestCase):
    """Collection of tests for custom template tags."""

    @classmethod
    def setUpTestData(cls):
        cls.group_1 = GroupFactory(name="Group 1")
        cls.group_2 = GroupFactory(name="Group 2")
        cls.user = UserFactory(password=PASSWORD, groups=(cls.group_1,))
        cls.project = ProjectFactory()
        cls.report = ReportFactory(project=cls.project)
        cls.assignment = ProjectAssignmentFactory(project=cls.project, operator=cls.user)

        cls.Objective = ProjectObjectiveFactory._meta.model
        cls.objective = ProjectObjectiveFactory(project=cls.project, complete=False)
        cls.complete_objective = ProjectObjectiveFactory(project=cls.project, complete=True)
        cls.objectives = cls.Objective.objects.filter(project=cls.project)

        cls.num_of_findings = 3
        ReportFindingLinkFactory.create_batch(
            cls.num_of_findings, report=cls.report, assigned_to=cls.user
        )

        cls.uri = reverse("home:dashboard")

    def setUp(self):
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )

    def test_tags(self):
        result = custom_tags.has_group(self.user, "Group 1")
        self.assertTrue(result)
        result = custom_tags.has_group(self.user, "Group 2")
        self.assertFalse(result)

        result = custom_tags.get_groups(self.user)
        self.assertEqual(result, "Group 1")

        response = self.client_auth.get(self.uri)
        request = response.wsgi_request
        result = custom_tags.count_assignments(request)
        self.assertEqual(result, self.num_of_findings)

        result = custom_tags.get_reports(request)
        self.assertEqual(len(result), 1)

        result = custom_tags.settings_value("DATE_FORMAT")
        self.assertEqual(result, settings.DATE_FORMAT)

        result = custom_tags.count_incomplete_objectives(self.objectives)
        self.assertEqual(result, 1)

        example_html = "<body><p>Example HTML</p><br /><br /><p></p></body>"
        result = custom_tags.strip_empty_tags(example_html)
        # The tag uses BS4's `prettify()` method to format the HTML, so there are newlines and indentations
        self.assertEqual(result, "<html>\n <body>\n  <p>\n   Example HTML\n  </p>\n </body>\n</html>")


class DashboardTests(TestCase):
    """Collection of tests for :view:`home.dashboard`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)

        cls.Project = ProjectFactory._meta.model
        cls.ProjectAssignment = ProjectAssignmentFactory._meta.model
        cls.ReportFindingLink = ReportFindingLinkFactory._meta.model

        cls.current_project = ProjectFactory(
            start_date=date.today() - timedelta(days=14),
            end_date=date.today(),
            complete=True
        )
        cls.future_project = ProjectFactory(
            start_date=date.today() + timedelta(days=14),
            end_date=date.today() + timedelta(days=28),
            complete=False
        )
        ProjectAssignmentFactory(
            project=cls.current_project,
            operator=cls.user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14),
        )
        ProjectAssignmentFactory(
            project=cls.future_project,
            operator=cls.user,
            start_date=date.today() + timedelta(days=14),
            end_date=date.today() + timedelta(days=28),
        )

        cls.report = ReportFactory(project=cls.current_project)
        ReportFindingLinkFactory.create_batch(3, report=cls.report, assigned_to=cls.user)

        cls.user_tasks = (
            cls.ReportFindingLink.objects.select_related("report", "report__project")
            .filter(
                Q(assigned_to=cls.user) & Q(report__complete=False) & Q(complete=False)
            )
            .order_by("report__project__end_date")[:10]
        )
        cls.user_projects = cls.ProjectAssignment.objects.select_related(
            "project", "project__client", "role"
        ).filter(Q(operator=cls.user))
        cls.active_projects = cls.ProjectAssignment.objects.select_related(
            "project", "project__client", "role"
        ).filter(Q(operator=cls.user) & Q(project__complete=False))

        cls.uri = reverse("home:dashboard")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )

    def test_view_uri_exists_at_desired_location(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_uses_correct_template(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_custom_context_exists(self):
        response = self.client_auth.get(self.uri)
        self.assertIn("user_projects", response.context)
        self.assertIn("active_projects", response.context)
        self.assertIn("recent_tasks", response.context)
        self.assertIn("user_tasks", response.context)
        self.assertEqual(len(response.context["user_projects"]), 2)
        self.assertEqual(response.context["user_projects"][0], self.user_projects[0])
        self.assertEqual(len(response.context["active_projects"]), 1)
        self.assertEqual(
            response.context["active_projects"][0], self.active_projects[0]
        )
        self.assertEqual(len(response.context["user_tasks"]), 3)


class ManagementTests(TestCase):
    """Collection of tests for :view:`home.Management`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.staff_user = UserFactory(password=PASSWORD, is_staff=True)

        cls.uri = reverse("home:management")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_staff = Client()
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )
        self.assertTrue(
            self.client_staff.login(username=self.staff_user.username, password=PASSWORD)
        )

    def test_view_uri_exists_at_desired_location(self):
        response = self.client_staff.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_permissions(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)

        response = self.client_staff.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client_staff.get(self.uri)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/management.html")

    def test_custom_context_exists(self):
        response = self.client_staff.get(self.uri)
        self.assertIn("timezone", response.context)


class UpdateSessionTests(TestCase):
    """Collection of tests for :view:`home.update_session`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.uri = reverse("home:ajax_update_session")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_auth.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_sticky_sidebar_value(self):
        self.client_auth.post(self.uri, {"session_data": "sidebar"})
        session = self.client_auth.session
        self.assertEqual(session["sidebar"]["sticky"], True)

        self.client_auth.post(self.uri, {"session_data": "sidebar"})
        session = self.client_auth.session
        self.assertEqual(session["sidebar"]["sticky"], False)

    def test_invalid_get_method(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 405)


class TestAWSConnectionTests(TestCase):
    """Collection of tests for :view:`home.TestAWSConnection`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.staff_user = UserFactory(password=PASSWORD, is_staff=True)

        cls.uri = reverse("home:ajax_test_aws")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_staff = Client()
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )
        self.assertTrue(
            self.client_staff.login(username=self.staff_user.username, password=PASSWORD)
        )

    def test_view_uri_post(self):
        response = self.client_staff.post(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_requires_staff(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)


class TestDOConnectionTests(TestCase):
    """Collection of tests for :view:`home.TestDOConnection`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.staff_user = UserFactory(password=PASSWORD, is_staff=True)

        cls.uri = reverse("home:ajax_test_do")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_staff = Client()
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )
        self.assertTrue(
            self.client_staff.login(username=self.staff_user.username, password=PASSWORD)
        )

    def test_view_uri_post(self):
        response = self.client_staff.post(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_requires_staff(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)


class TestNamecheapConnectionTests(TestCase):
    """Collection of tests for :view:`home.TestNamecheapConnection`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.staff_user = UserFactory(password=PASSWORD, is_staff=True)

        cls.uri = reverse("home:ajax_test_namecheap")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_staff = Client()
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )
        self.assertTrue(
            self.client_staff.login(username=self.staff_user.username, password=PASSWORD)
        )

    def test_view_uri_post(self):
        response = self.client_staff.post(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_requires_staff(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)


class TestSlackConnectionTests(TestCase):
    """Collection of tests for :view:`home.TestSlackConnection`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.staff_user = UserFactory(password=PASSWORD, is_staff=True)

        cls.uri = reverse("home:ajax_test_slack")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_staff = Client()
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )
        self.assertTrue(
            self.client_staff.login(username=self.staff_user.username, password=PASSWORD)
        )

    def test_view_uri_post(self):
        response = self.client_staff.post(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_requires_staff(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)


class TestVirusTotalConnectionTests(TestCase):
    """Collection of tests for :view:`home.TestSlackConnection`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.staff_user = UserFactory(password=PASSWORD, is_staff=True)

        cls.uri = reverse("home:ajax_test_virustotal")

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.client_staff = Client()
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )
        self.assertTrue(
            self.client_staff.login(username=self.staff_user.username, password=PASSWORD)
        )

    def test_view_uri_post(self):
        response = self.client_staff.post(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_view_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)

    def test_view_requires_staff(self):
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 302)


class ProtectedServeTest(TestCase):
    """Collection of tests for :view:`home.protected_serve`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password=PASSWORD)
        cls.staff_user = UserFactory(password=PASSWORD, is_staff=True)

        cls.uri = "/media/templates"

    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.assertTrue(
            self.client_auth.login(username=self.user.username, password=PASSWORD)
        )

    @override_settings(DEBUG=True)
    def test_view_uri(self):
        assert settings.DEBUG
        response = self.client_auth.get(self.uri)
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "ghostwriter.home.views.protected_serve", status_code=404)

    def test_view_uri_requires_login(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 302)
