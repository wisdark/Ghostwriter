# Standard Libraries
import logging
from datetime import timedelta

# Django Imports
from django.test import TestCase

# Ghostwriter Libraries
from ghostwriter.factories import (
    ClientContactFactory,
    ClientFactory,
    ClientNoteFactory,
    ProjectAssignmentFactory,
    ProjectFactory,
    ProjectNoteFactory,
    ProjectObjectiveFactory,
    ProjectScopeFactory,
    ProjectTargetFactory,
    UserFactory,
)
from ghostwriter.rolodex.forms_client import (
    ClientContactForm,
    ClientContactFormSet,
    ClientForm,
    ClientNoteForm,
)
from ghostwriter.rolodex.forms_project import (
    ProjectAssignmentForm,
    ProjectAssignmentFormSet,
    ProjectForm,
    ProjectNoteForm,
    ProjectObjectiveForm,
    ProjectObjectiveFormSet,
    ProjectScopeForm,
    ProjectScopeFormSet,
    ProjectTargetForm,
    ProjectTargetFormSet,
)

logging.disable(logging.CRITICAL)


def instantiate_formset(formset_class, data, instance=None, initial=None):
    prefix = formset_class().prefix
    formset_data = {}
    for i, form_data in enumerate(data):
        for name, value in form_data.items():
            if name.endswith("_id"):
                name = name.replace("_id", "")
            if isinstance(value, list):
                for j, inner in enumerate(value):
                    formset_data["{}-{}-{}_{}".format(prefix, i, name, j)] = inner
            else:
                formset_data["{}-{}-{}".format(prefix, i, name)] = value
    formset_data["{}-TOTAL_FORMS".format(prefix)] = len(data)
    formset_data["{}-INITIAL_FORMS".format(prefix)] = 0

    if instance:
        return formset_class(formset_data, instance=instance, initial=initial)
    else:
        return formset_class(formset_data, initial=initial)


class ClientContactFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ClientContactForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.contact = ClientContactFactory()

    def setUp(self):
        pass

    def form_data(
        self,
        name=None,
        email=None,
        job_title=None,
        phone=None,
        note=None,
        client_id=None,
        timezone=None,
        **kwargs,
    ):
        return ClientContactForm(
            data={
                "name": name,
                "email": email,
                "job_title": job_title,
                "phone": phone,
                "note": note,
                "client": client_id,
                "timezone": timezone,
            },
        )

    def test_valid_data(self):
        form = self.form_data(**self.contact.__dict__)
        self.assertTrue(form.is_valid())


class ClientContactFormSetTests(TestCase):
    """Collection of tests for :form:`rolodex.ClientContactFormSet`."""

    @classmethod
    def setUpTestData(cls):
        cls.org = ClientFactory()
        cls.contact_1 = ClientContactFactory(client=cls.org)
        cls.contact_2 = ClientContactFactory(client=cls.org)
        cls.to_be_deleted = ClientContactFactory(client=cls.org)

    def form_data(self, data, **kwargs):
        return instantiate_formset(ClientContactFormSet, data=data, instance=self.org)

    def test_valid_data(self):
        data = [self.contact_1.__dict__, self.contact_2.__dict__]
        form = self.form_data(data)
        self.assertTrue(form.is_valid())

    def test_duplicate_contacts(self):
        contact_1 = self.contact_1.__dict__.copy()
        contact_2 = self.contact_2.__dict__.copy()
        contact_2["name"] = contact_1["name"]

        data = [contact_1, contact_2]
        form = self.form_data(data)
        errors = form.errors[1]["name"].as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "duplicate")

    def test_incomplete_contact_form_name(self):
        contact_1 = self.contact_1.__dict__.copy()
        contact_2 = self.contact_2.__dict__.copy()
        contact_1["name"] = ""

        data = [contact_1, contact_2]
        form = self.form_data(data)
        errors = form.errors[0]["name"].as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "required")

    def test_incomplete_contact_form_job_title(self):
        contact_1 = self.contact_1.__dict__.copy()
        contact_2 = self.contact_2.__dict__.copy()
        contact_1["job_title"] = ""

        data = [contact_1, contact_2]
        form = self.form_data(data)
        errors = form.errors[0]["job_title"].as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "incomplete")

    def test_incomplete_contact_form_email(self):
        contact_1 = self.contact_1.__dict__.copy()
        contact_2 = self.contact_2.__dict__.copy()
        contact_1["email"] = ""

        data = [contact_1, contact_2]
        form = self.form_data(data)
        errors = form.errors[0]["email"].as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "incomplete")

    def test_invalid_email_address(self):
        contact_1 = self.contact_1.__dict__.copy()
        contact_2 = self.contact_2.__dict__.copy()
        contact_1["email"] = "foo#bar"

        data = [contact_1, contact_2]
        form = self.form_data(data)
        errors = form.errors[0]["email"].as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "invalid")

    def test_contact_delete(self):
        contact_1 = self.contact_1.__dict__.copy()
        contact_2 = self.contact_2.__dict__.copy()
        contact_1["name"] = ""
        contact_1["email"] = "foo#bar"
        contact_1["DELETE"] = True

        data = [contact_1, contact_2]
        form = self.form_data(data)
        self.assertTrue(form.is_valid())


class ClientFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ClientForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.org = ClientFactory()
        cls.client_dict = cls.org.__dict__

    def setUp(self):
        pass

    def form_data(
        self,
        name=None,
        short_name=None,
        codename=None,
        note=None,
        timezone=None,
        address=None,
        **kwargs,
    ):
        return ClientForm(
            data={
                "name": name,
                "short_name": short_name,
                "codename": codename,
                "note": note,
                "timezone": timezone,
                "address": address,
            },
        )

    def test_valid_data(self):
        client = self.client_dict.copy()
        client["name"] = "New Client"

        form = self.form_data(**client)
        self.assertTrue(form.is_valid())

    def test_duplicate_client(self):
        client = self.client_dict.copy()

        form = self.form_data(**client)
        self.assertFalse(form.is_valid())


class ClientNoteFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ClientNoteForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.note = ClientNoteFactory()
        cls.note_dict = cls.note.__dict__

    def setUp(self):
        pass

    def form_data(
        self,
        note=None,
        **kwargs,
    ):
        return ClientNoteForm(
            data={
                "note": note,
            },
        )

    def test_valid_data(self):
        note = self.note_dict.copy()

        form = self.form_data(**note)
        self.assertTrue(form.is_valid())

    def test_blank_note(self):
        note = self.note_dict.copy()
        note["note"] = ""

        form = self.form_data(**note)
        errors = form["note"].errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "required")


class ProjectNoteFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectNoteForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.note = ProjectNoteFactory()
        cls.note_dict = cls.note.__dict__

    def setUp(self):
        pass

    def form_data(
        self,
        note=None,
        **kwargs,
    ):
        return ProjectNoteForm(
            data={
                "note": note,
            },
        )

    def test_valid_data(self):
        note = self.note_dict.copy()

        form = self.form_data(**note)
        self.assertTrue(form.is_valid())

    def test_blank_note(self):
        note = self.note_dict.copy()
        note["note"] = ""

        form = self.form_data(**note)
        errors = form["note"].errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "required")


class ProjectAssignmentFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectAssignmentForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.assignment = ProjectAssignmentFactory()
        cls.assignment_dict = cls.assignment.__dict__
        cls.new_assignee = UserFactory()

    def setUp(self):
        pass

    def form_data(
        self,
        operator=None,
        start_date=None,
        end_date=None,
        note=None,
        project_id=None,
        **kwargs,
    ):
        return ProjectAssignmentForm(
            data={
                "operator": operator,
                "start_date": start_date,
                "end_date": end_date,
                "project": project_id,
                "note": note,
            },
        )

    def test_valid_data(self):
        assignment = self.assignment_dict.copy()
        assignment["operator"] = self.new_assignee

        form = self.form_data(**assignment)
        self.assertTrue(form.is_valid())


class ProjectObjectiveFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectObjectiveForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.objective = ProjectObjectiveFactory()
        cls.objective_dict = cls.objective.__dict__

    def setUp(self):
        pass

    def form_data(
        self,
        deadline=None,
        objective=None,
        complete=None,
        status_id=None,
        description=None,
        priority_id=None,
        **kwargs,
    ):
        return ProjectObjectiveForm(
            data={
                "deadline": deadline,
                "objective": objective,
                "complete": complete,
                "status": status_id,
                "description": description,
                "priority": priority_id,
            },
        )

    def test_valid_data(self):
        objective = self.objective_dict.copy()

        form = self.form_data(**objective)
        self.assertTrue(form.is_valid())


class ProjectScopeFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectScopeForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.scope = ProjectScopeFactory()
        cls.scope_dict = cls.scope.__dict__

    def setUp(self):
        pass

    def form_data(
        self,
        name=None,
        scope=None,
        description=None,
        disallowed=None,
        requires_caution=None,
        **kwargs,
    ):
        return ProjectScopeForm(
            data={
                "name": name,
                "scope": scope,
                "description": description,
                "disallowed": disallowed,
                "requires_caution": requires_caution,
            },
        )

    def test_valid_data(self):
        scope = self.scope_dict.copy()

        form = self.form_data(**scope)
        self.assertTrue(form.is_valid())


class ProjectTargetFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectTargetForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.target = ProjectTargetFactory()
        cls.target_dict = cls.target.__dict__

    def setUp(self):
        pass

    def form_data(
        self,
        ip_address=None,
        hostname=None,
        note=None,
        **kwargs,
    ):
        return ProjectTargetForm(
            data={
                "ip_address": ip_address,
                "hostname": hostname,
                "note": note,
            },
        )

    def test_valid_data(self):
        target = self.target_dict.copy()

        form = self.form_data(**target)
        self.assertTrue(form.is_valid())


class ProjectFormTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectForm`."""

    @classmethod
    def setUpTestData(cls):
        cls.project = ProjectFactory()
        cls.project_dict = cls.project.__dict__

    def setUp(self):
        pass

    def form_data(
        self,
        start_date=None,
        end_date=None,
        project_type_id=None,
        client_id=None,
        codename=None,
        update_checkouts=None,
        slack_channel=None,
        note=None,
        timezone=None,
        **kwargs,
    ):
        return ProjectForm(
            data={
                "start_date": start_date,
                "end_date": end_date,
                "project_type": project_type_id,
                "client": client_id,
                "codename": codename,
                "update_checkouts": update_checkouts,
                "slack_channel": slack_channel,
                "note": note,
                "timezone": timezone,
            },
        )

    def test_valid_data(self):
        project = self.project_dict.copy()

        form = self.form_data(**project)
        self.assertTrue(form.is_valid())

    def test_invalid_dates(self):
        project = self.project_dict.copy()
        project["start_date"] = self.project.end_date
        project["end_date"] = self.project.start_date

        form = self.form_data(**project)
        errors = form.errors["end_date"].as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "invalid_date")

    def test_invalid_slack_channel(self):
        project = self.project_dict.copy()
        project["slack_channel"] = "NoHash"

        form = self.form_data(**project)
        errors = form.errors["slack_channel"].as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "invalid_channel")


class ProjectAssignmentFormSetTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectAssignmentFormSet`."""

    @classmethod
    def setUpTestData(cls):
        cls.project = ProjectFactory()
        cls.project_dict = cls.project.__dict__
        cls.assignment_1 = ProjectAssignmentFactory(project=cls.project)
        cls.assignment_2 = ProjectAssignmentFactory(project=cls.project)
        cls.to_be_deleted = ProjectAssignmentFactory(project=cls.project)
        cls.new_assignee = UserFactory()

    def form_data(self, data, **kwargs):
        return instantiate_formset(
            ProjectAssignmentFormSet, data=data, instance=self.project
        )

    def test_valid_data(self):
        to_be_deleted = self.to_be_deleted.__dict__
        to_be_deleted["operator"] = None
        to_be_deleted["DELETE"] = True

        data = [self.assignment_1.__dict__, self.assignment_2.__dict__, to_be_deleted]
        form = self.form_data(data)
        self.assertTrue(form.is_valid())

    def test_duplicate_assignees(self):
        assignment_1 = self.assignment_1.__dict__.copy()
        assignment_2 = self.assignment_2.__dict__.copy()
        assignment_1["operator"] = self.new_assignee
        assignment_2["operator"] = self.new_assignee

        data = [assignment_1, assignment_2]
        form = self.form_data(data)
        errors = form.errors[1]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["operator"].as_data()[0].code, "duplicate")

    def test_invalid_start_date(self):
        assignment_1 = self.assignment_1.__dict__.copy()
        assignment_2 = self.assignment_2.__dict__.copy()

        assignment_1["start_date"] = self.project.start_date - timedelta(days=1)

        data = [assignment_1, assignment_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["start_date"].as_data()[0].code, "invalid_date")

    def test_invalid_end_date(self):
        assignment_1 = self.assignment_1.__dict__.copy()
        assignment_2 = self.assignment_2.__dict__.copy()

        assignment_1["end_date"] = self.project.end_date + timedelta(days=1)

        data = [assignment_1, assignment_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["end_date"].as_data()[0].code, "invalid_date")

    def test_incomplete_form(self):
        assignment_1 = self.assignment_1.__dict__.copy()
        assignment_2 = self.assignment_2.__dict__.copy()

        assignment_1["start_date"] = None
        assignment_1["end_date"] = None
        assignment_1["role"] = None

        data = [assignment_1, assignment_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 3)
        self.assertEqual(errors["start_date"].as_data()[0].code, "incomplete")
        self.assertEqual(errors["end_date"].as_data()[0].code, "incomplete")
        self.assertEqual(errors["role"].as_data()[0].code, "incomplete")

    def test_blank_form(self):
        assignment_1 = self.assignment_1.__dict__.copy()
        assignment_2 = self.assignment_2.__dict__.copy()

        assignment_1["operator"] = None
        assignment_1["start_date"] = None
        assignment_1["end_date"] = None
        assignment_1["role"] = None

        data = [assignment_1, assignment_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["note"].as_data()[0].code, "incomplete")

    def test_missing_operator(self):
        assignment_1 = self.assignment_1.__dict__.copy()
        assignment_2 = self.assignment_2.__dict__.copy()

        assignment_1["operator"] = None

        data = [assignment_1, assignment_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["operator"].as_data()[0].code, "incomplete")


class ProjectObjectiveFormSetTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectObjectiveFormSet`."""

    @classmethod
    def setUpTestData(cls):
        cls.project = ProjectFactory()
        cls.project_dict = cls.project.__dict__
        cls.objective_1 = ProjectObjectiveFactory(
            project=cls.project, deadline=cls.project.end_date
        )
        cls.objective_2 = ProjectObjectiveFactory(
            project=cls.project, deadline=cls.project.end_date
        )
        cls.to_be_deleted = ProjectObjectiveFactory(project=cls.project)

    def form_data(self, data, **kwargs):
        return instantiate_formset(
            ProjectObjectiveFormSet, data=data, instance=self.project
        )

    def test_valid_data(self):
        to_be_deleted = self.to_be_deleted.__dict__
        to_be_deleted["objective"] = None
        to_be_deleted["DELETE"] = True

        data = [self.objective_1.__dict__, self.objective_2.__dict__, to_be_deleted]
        form = self.form_data(data)
        self.assertTrue(form.is_valid())

    def test_duplicate_objectives(self):
        objective_1 = self.objective_1.__dict__.copy()
        objective_2 = self.objective_2.__dict__.copy()
        objective_1["objective"] = "Duplicate Objective"
        objective_2["objective"] = "Duplicate Objective"

        data = [objective_1, objective_2]
        form = self.form_data(data)
        errors = form.errors[1]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["objective"].as_data()[0].code, "duplicate")

    def test_missing_objective(self):
        objective_1 = self.objective_1.__dict__.copy()
        objective_2 = self.objective_2.__dict__.copy()
        objective_1["objective"] = None

        data = [objective_1, objective_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["objective"].as_data()[0].code, "incomplete")

    def test_missing_deadline(self):
        objective_1 = self.objective_1.__dict__.copy()
        objective_2 = self.objective_2.__dict__.copy()
        objective_1["deadline"] = None

        data = [objective_1, objective_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["deadline"].as_data()[0].code, "incomplete")

    def test_missing_objective_with_description(self):
        objective_1 = self.objective_1.__dict__.copy()
        objective_2 = self.objective_2.__dict__.copy()
        objective_1["objective"] = None
        objective_1["deadline"] = None

        data = [objective_1, objective_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["description"].as_data()[0].code, "incomplete")

    def test_invalid_early_deadline(self):
        objective_1 = self.objective_1.__dict__.copy()
        objective_2 = self.objective_2.__dict__.copy()
        objective_1["deadline"] = self.project.start_date - timedelta(days=1)

        data = [objective_1, objective_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["deadline"].as_data()[0].code, "invalid_date")

    def test_invalid_late_deadline(self):
        objective_1 = self.objective_1.__dict__.copy()
        objective_2 = self.objective_2.__dict__.copy()
        objective_1["deadline"] = self.project.end_date + timedelta(days=1)

        data = [objective_1, objective_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["deadline"].as_data()[0].code, "invalid_date")


class ProjectScopeFormSetTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectScopeInlineFormSet`."""

    @classmethod
    def setUpTestData(cls):
        cls.project = ProjectFactory()
        cls.project_dict = cls.project.__dict__
        cls.scope_1 = ProjectScopeFactory(project=cls.project)
        cls.scope_2 = ProjectScopeFactory(project=cls.project)
        cls.to_be_deleted = ProjectScopeFactory(project=cls.project)

    def form_data(self, data, **kwargs):
        return instantiate_formset(ProjectScopeFormSet, data=data, instance=self.project)

    def test_valid_data(self):
        to_be_deleted = self.to_be_deleted.__dict__
        to_be_deleted["name"] = None
        to_be_deleted["DELETE"] = True

        data = [self.scope_1.__dict__, self.scope_2.__dict__, to_be_deleted]
        form = self.form_data(data)
        self.assertTrue(form.is_valid())

    def test_duplicate_names(self):
        scope_1 = self.scope_1.__dict__.copy()
        scope_2 = self.scope_2.__dict__.copy()
        scope_1["name"] = "Duplicate Name"
        scope_2["name"] = "duplicate name"

        data = [scope_1, scope_2]
        form = self.form_data(data)
        errors = form.errors[1]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["name"].as_data()[0].code, "duplicate")

    def test_missing_scope(self):
        scope_1 = self.scope_1.__dict__.copy()
        scope_2 = self.scope_2.__dict__.copy()
        scope_1["scope"] = None

        data = [scope_1, scope_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["scope"].as_data()[0].code, "incomplete")

    def test_missing_name(self):
        scope_1 = self.scope_1.__dict__.copy()
        scope_2 = self.scope_2.__dict__.copy()
        scope_1["name"] = None

        data = [scope_1, scope_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["name"].as_data()[0].code, "incomplete")


class ProjectTargetFormSetTests(TestCase):
    """Collection of tests for :form:`rolodex.ProjectTargetInlineFormSet`."""

    @classmethod
    def setUpTestData(cls):
        cls.project = ProjectFactory()
        cls.project_dict = cls.project.__dict__
        cls.target_1 = ProjectTargetFactory(project=cls.project)
        cls.target_2 = ProjectTargetFactory(project=cls.project)
        cls.to_be_deleted = ProjectTargetFactory(project=cls.project)

    def form_data(self, data, **kwargs):
        return instantiate_formset(ProjectTargetFormSet, data=data, instance=self.project)

    def test_valid_data(self):
        target_1 = self.target_1.__dict__
        target_1["hostname"] = None

        target_2 = self.target_2.__dict__
        target_2["ip_address"] = None

        to_be_deleted = self.to_be_deleted.__dict__
        to_be_deleted["hostname"] = None
        to_be_deleted["ip_address"] = None
        to_be_deleted["DELETE"] = True

        data = [target_1, target_2, to_be_deleted]
        form = self.form_data(data)
        self.assertTrue(form.is_valid())

    def test_duplicate_hostnames(self):
        target_1 = self.target_1.__dict__.copy()
        target_2 = self.target_2.__dict__.copy()
        target_1["hostname"] = "Duplicate Name"
        target_2["hostname"] = "duplicate name"

        data = [target_1, target_2]
        form = self.form_data(data)
        errors = form.errors[1]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["hostname"].as_data()[0].code, "duplicate")

    def test_duplicate_addresses(self):
        target_1 = self.target_1.__dict__.copy()
        target_2 = self.target_2.__dict__.copy()
        target_1["ip_address"] = "1.1.1.1"
        target_2["ip_address"] = "1.1.1.1"

        data = [target_1, target_2]
        form = self.form_data(data)
        errors = form.errors[1]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["ip_address"].as_data()[0].code, "duplicate")

    def test_incomplete_form(self):
        target_1 = self.target_1.__dict__.copy()
        target_2 = self.target_2.__dict__.copy()
        target_1["hostname"] = None
        target_1["ip_address"] = None
        target_1["note"] = "Only a note"

        data = [target_1, target_2]
        form = self.form_data(data)
        errors = form.errors[0]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors["note"].as_data()[0].code, "incomplete")
