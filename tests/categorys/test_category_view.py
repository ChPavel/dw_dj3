import pytest
from django.urls import reverse
from rest_framework import status

from todolist.goals.models import BoardParticipant


@pytest.mark.django_db()
class TestCategoryRetrieveView:
    @pytest.fixture(autouse=True)
    def setup(self, board_participant):
        self.url = self.get_url(board_participant.board_id)

    @staticmethod
    def get_url(category_pk: int) -> str:
        return reverse('todolist.goals:goal_category', kwargs={'pk': category_pk})

    def test_auth_required(self, client):
        """Неавторизованный пользователь не может просматривать категории на доске."""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_retrieve_deleted_category(self, auth_client, goal_category):
        """Пользователь не может просматривать удалённые категории."""
        goal_category.is_deleted = True
        goal_category.save()

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_failed_to_retrieve_foreign_cdtegory(self, client, user_factory):
        """Пользователь не может просматривать категории досок, где он не является участником."""
        another_user = user_factory.create()
        client.force_login(another_user)

        response = client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND  # должно быть 403


@pytest.mark.django_db()
class TestCategoryDestroyView:
    @pytest.fixture(autouse=True)
    def setup(self, goal_category):
        self.url = self.get_url(goal_category.pk)

    @staticmethod
    def get_url(category_pk: int) -> str:
        return reverse('todolist.goals:goal_category', kwargs={'pk': category_pk})

    def test_auth_required(self, client):
        """Неавторизованный пользователь не может удалять категории."""
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_owner_failed_to_delete_category(self, client, user_factory, board, board_participant_factory):
        """Пользователь не являющийся владельцем или редактором доски, не может удалить категорию с неё."""
        another_user = user_factory.create()
        board_participant_factory.create(user=another_user, board=board, role=BoardParticipant.Role.reader)
        client.force_login(another_user)

        response = client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'role',
        [
            BoardParticipant.Role.owner,
            BoardParticipant.Role.writer,
        ],
        ids=['owner', 'writer'],
    )
    def test_not_owner_failed_to_delete_board(self, client, user_factory, board, board_participant_factory, role):
        """Пользователь являющийся владельцем или редактором доски, может удалить категорию с неё."""
        another_user = user_factory.create()
        board_participant_factory.create(user=another_user, board=board, role=role)
        client.force_login(another_user)

        response = client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
