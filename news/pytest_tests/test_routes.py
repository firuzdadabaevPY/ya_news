import pytest

from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import News


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_for_args_news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
def test_availbility_for_comment_edit_and_delete(
    name, parametrized_client, expected_status, pk_for_args_comment
):
    url = reverse(name, args=pk_for_args_comment)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(client, name, pk_for_args_comment):
    login_url = reverse('users:login')
    url = reverse(name, args=pk_for_args_comment)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)

    assertRedirects(response, redirect_url)
