from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Survey, Question, AnswerOption, Poll, PollOption, Vote


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        res = self.client.post('/api/auth/register/', {
            'username': 'testuser',
            'password': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', res.data)

    def test_register_password_mismatch(self):
        res = self.client.post('/api/auth/register/', {
            'username': 'user2',
            'password': 'abc123',
            'password2': 'xyz999',
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_and_get_tokens(self):
        User.objects.create_user(username='loginuser', password='pass12345')
        res = self.client.post('/api/auth/login/', {
            'username': 'loginuser',
            'password': 'pass12345',
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_me_authenticated(self):
        user = User.objects.create_user(username='meuser', password='pass12345')
        self.client.force_authenticate(user=user)
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'meuser')

    def test_me_unauthenticated(self):
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class SurveyAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.survey = Survey.objects.create(title='Тестовый опрос', is_active=True)
        q = Question.objects.create(survey=self.survey, text='Вопрос 1', question_type='single', order=1)
        self.opt1 = AnswerOption.objects.create(question=q, text='Вариант А', skill_tag='Python', order=1)
        self.opt2 = AnswerOption.objects.create(question=q, text='Вариант Б', skill_tag='Django', order=2)
        self.question = q

    def test_survey_list(self):
        res = self.client.get('/api/surveys/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_survey_detail(self):
        res = self.client.get(f'/api/surveys/{self.survey.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'Тестовый опрос')
        self.assertEqual(len(res.data['questions']), 1)

    def test_survey_submit(self):
        res = self.client.post(f'/api/surveys/{self.survey.id}/submit/', {
            'answers': [
                {'question_id': self.question.id, 'selected_option_ids': [self.opt1.id], 'text_answer': ''}
            ]
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('top_skills', res.data)

    def test_survey_submit_returns_top_skills(self):
        res = self.client.post(f'/api/surveys/{self.survey.id}/submit/', {
            'answers': [
                {'question_id': self.question.id, 'selected_option_ids': [self.opt1.id]}
            ]
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        skills = res.data['top_skills']
        self.assertIsInstance(skills, list)
        if skills:
            self.assertEqual(skills[0]['skill'], 'Python')


class PollAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='voter', password='pass12345')
        self.poll = Poll.objects.create(title='Тест голосование', is_active=True)
        self.opt1 = PollOption.objects.create(poll=self.poll, text='Вариант 1', order=1)
        self.opt2 = PollOption.objects.create(poll=self.poll, text='Вариант 2', order=2)

    def test_poll_list(self):
        res = self.client.get('/api/polls/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_poll_detail(self):
        res = self.client.get(f'/api/polls/{self.poll.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['options']), 2)

    def test_vote_requires_auth(self):
        res = self.client.post(f'/api/polls/{self.poll.id}/vote/', {'option_id': self.opt1.id})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vote_success(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(f'/api/polls/{self.poll.id}/vote/', {'option_id': self.opt1.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('message', res.data)

    def test_vote_duplicate_blocked(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(f'/api/polls/{self.poll.id}/vote/', {'option_id': self.opt1.id}, format='json')
        res = self.client.post(f'/api/polls/{self.poll.id}/vote/', {'option_id': self.opt2.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', res.data)

    def test_vote_inactive_poll(self):
        self.poll.is_active = False
        self.poll.save()
        self.client.force_authenticate(user=self.user)
        res = self.client.post(f'/api/polls/{self.poll.id}/vote/', {'option_id': self.opt1.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_poll_result(self):
        Vote.objects.create(user=self.user, poll=self.poll, option=self.opt1)
        res = self.client.get(f'/api/polls/{self.poll.id}/result/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['total_votes'], 1)
