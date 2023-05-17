from typing import Callable
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture()
def category_create_data(faker) -> Callable:
    def _wrapper(**kwargs) -> dict:
        data = {'title': faker.sentence(2)}
        data |= kwargs
        return data

    return _wrapper


@pytest.mark.django_db()
class TestCategoryCreateView:
    url = reverse('todolist.goals:create_category')

    def test_auth_required(self, client, category_create_data):
        """Неавторизованный пользователь при создании категории получит ошибку авторизации."""
        response = client.post(self.url, data=category_create_data())

        assert response.status_code == status.HTTP_403_FORBIDDEN
