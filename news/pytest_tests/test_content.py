from django.urls import reverse

from news.forms import CommentForm

HOME_URL = 'news:home'


def test_news_count(client, ten_news_count):
    url = reverse(HOME_URL)
    response = client.get(url)

    object_list = response.context['object_list']

    assert object_list.count() == ten_news_count


def test_ten_news_order(ten_news_count, client):
    url = reverse(HOME_URL)
    response = client.get(url)

    object_list = response.context['object_list']
    all_date = [news.date for news in object_list]
    sorted_dates = sorted(all_date, reverse=True)

    assert object_list.count() == ten_news_count
    assert all_date == sorted_dates


def test_ten_comment_order(client, ten_comments, pk_for_args_news):
    url = reverse('news:detail', args=pk_for_args_news)
    response = client.get(url)

    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)

    assert all_comments.count() == 10
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, pk_for_args_news):
    url = reverse('news:detail', args=pk_for_args_news)
    response = client.get(url)

    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, pk_for_args_news):
    url = reverse('news:detail', args=pk_for_args_news)
    response = author_client.get(url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
