from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(client, pk_for_args_news, comment_data):
    url = reverse('news:detail', args=pk_for_args_news)
    response = client.post(url, comment_data)

    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, news, author, pk_for_args_news, comment_data
):
    url = reverse('news:detail', args=pk_for_args_news)
    response = author_client.post(url, comment_data)

    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1

    comment = Comment.objects.get()
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, pk_for_args_news):
    url = reverse('news:detail', args=pk_for_args_news)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, bad_words_data)

    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment, news):
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.delete(url)

    url_to_comments = reverse('news:detail', args=(news.id,))
    url_to_comments = f'{url_to_comments}#comments'
    assertRedirects(response, url_to_comments)

    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, pk_for_args_comment, pk_for_args_news):
    url = reverse('news:edit', args=pk_for_args_comment)
    data = {'text': 'It is edited comment'}

    assert Comment.objects.get().text == 'Текст комментария'

    response = author_client.post(url, data)
    comment = Comment.objects.get()

    url_to_comments = reverse('news:detail', args=pk_for_args_news)
    url_to_comments = f'{url_to_comments}#comments'

    assertRedirects(response, url_to_comments)
    assert comment.text == data['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client, pk_for_args_comment, pk_for_args_news
):
    url = reverse('news:edit', args=pk_for_args_comment)
    data = {'text': 'It is edited comment'}
    response = not_author_client.post(url, data=data)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment = Comment.objects.get()

    assert comment.text == 'Текст комментария'
