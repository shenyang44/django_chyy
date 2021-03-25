from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question
from django.urls import reverse

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_q(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_q(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_q = Question(pub_date=time)
        self.assertIs(old_q.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_q(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_q = Question(pub_date=time)
        self.assertIs(recent_q.was_published_recently(), True)

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date = time)


class QuestionIndexViewTests(TestCase):
    def test_no_q(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_list'], [])

    def test_past_q(self):
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_list'],
            ['<Question: Past question.>']
        )

    def test_future_q(self):
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_list'], [])

    def test_future_and_past_q(self):
        create_question(question_text='Past question.', days=-30)
        create_question(question_text='Future', days=30)
        response=self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        create_question(question_text='Past 1', days = -30)
        create_question(question_text='Past 2', days = -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_list'],
            ['<Question: Past 2>', '<Question: Past 1>']
        )

class QuestionDetailViewTests(TestCase):
    def test_future_q(self):
        future_q = create_question(question_text='Future question.', days=5)
        url= reverse('polls:detail', args=(future_q.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_q(self):
        past_q = create_question(question_text='Past question.', days=-5)
        url = reverse('polls:detail', args = (past_q.id,))
        response = self.client.get(url)
        self.assertContains(response, past_q.question_text)

