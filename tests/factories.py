import factory
from django.utils import timezone
from pytest_factoryboy import register

from core.models import User
from todolist.goals.models import Board, BoardParticipant, GoalCategory


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._get_manager(model_class).create_user(*args, **kwargs)
        # можно User.objects.create_user(*args, **kwargs)


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)

    class Meta:
        abstract = True


@register
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(DatesFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


@register
class CategoryFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')
    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)

    class Meta:
        model = GoalCategory
