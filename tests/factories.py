import factory
from tests.async_factory import AsyncFactory
from app.users.models import User
from app.projects.models import Project
from app.tasks.models import Task


class UserFactory(AsyncFactory):
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Sequence(lambda n: f"User {n}")
    hashed_pass = "<test>"

    class Meta:
        model = User


class ProjectFactory(AsyncFactory):
    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker("sentence")
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Project


class TaskFactory(AsyncFactory):
    name = factory.Sequence(lambda n: f"Task {n}")
    description = factory.Faker("sentence")
    owner = factory.SubFactory(UserFactory)
    project = None  # you’ll set it in the test if you want

    class Meta:
        model = Task
