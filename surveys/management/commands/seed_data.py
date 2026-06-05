"""
Команда для заполнения базы данных тестовыми данными.
Запуск: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from surveys.models import Survey, Question, AnswerOption, Poll, PollOption


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми опросами и голосованиями'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Заполняем базу данных...')

        # ---- SURVEY ----
        if not Survey.objects.exists():
            survey = Survey.objects.create(
                title='Определи свои IT-навыки',
                description='Пройдите опрос и узнайте свои топ-3 сильных стороны в IT',
                is_active=True
            )

            q1 = Question.objects.create(
                survey=survey, text='Что вам больше нравится делать?',
                question_type='single', order=1
            )
            AnswerOption.objects.bulk_create([
                AnswerOption(question=q1, text='Писать код и алгоритмы', skill_tag='Backend', order=1),
                AnswerOption(question=q1, text='Создавать красивые интерфейсы', skill_tag='Frontend', order=2),
                AnswerOption(question=q1, text='Анализировать данные', skill_tag='Data Science', order=3),
                AnswerOption(question=q1, text='Настраивать серверы и CI/CD', skill_tag='DevOps', order=4),
            ])

            q2 = Question.objects.create(
                survey=survey, text='Какой язык программирования предпочитаете?',
                question_type='single', order=2
            )
            AnswerOption.objects.bulk_create([
                AnswerOption(question=q2, text='Python', skill_tag='Backend', order=1),
                AnswerOption(question=q2, text='JavaScript / TypeScript', skill_tag='Frontend', order=2),
                AnswerOption(question=q2, text='SQL / R', skill_tag='Data Science', order=3),
                AnswerOption(question=q2, text='Bash / Go / Rust', skill_tag='DevOps', order=4),
            ])

            q3 = Question.objects.create(
                survey=survey, text='Как вы решаете сложную задачу?',
                question_type='multiple', order=3
            )
            AnswerOption.objects.bulk_create([
                AnswerOption(question=q3, text='Разбиваю на подзадачи и пишу алгоритм', skill_tag='Backend', order=1),
                AnswerOption(question=q3, text='Ищу UX-решение для пользователя', skill_tag='Frontend', order=2),
                AnswerOption(question=q3, text='Строю модель и анализирую данные', skill_tag='Data Science', order=3),
                AnswerOption(question=q3, text='Автоматизирую процесс', skill_tag='DevOps', order=4),
            ])

            self.stdout.write(self.style.SUCCESS('✅ Опрос создан'))

        # ---- POLLS ----
        if not Poll.objects.exists():
            poll1 = Poll.objects.create(
                title='Какой фреймворк лучше для бэкенда?',
                description='Выберите свой любимый Python веб-фреймворк',
                is_active=True
            )
            PollOption.objects.bulk_create([
                PollOption(poll=poll1, text='Django',   order=1),
                PollOption(poll=poll1, text='FastAPI',  order=2),
                PollOption(poll=poll1, text='Flask',    order=3),
                PollOption(poll=poll1, text='Другой',   order=4),
            ])

            poll2 = Poll.objects.create(
                title='Светлая или тёмная тема?',
                description='Какую тему вы используете в редакторе кода?',
                is_active=False
            )
            PollOption.objects.bulk_create([
                PollOption(poll=poll2, text='🌙 Тёмная тема', order=1),
                PollOption(poll=poll2, text='☀️ Светлая тема', order=2),
                PollOption(poll=poll2, text='🔄 Зависит от настроения', order=3),
            ])

            self.stdout.write(self.style.SUCCESS('✅ Голосования созданы'))

        # ---- ADMIN USER ----
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✅ Суперпользователь: admin / admin123'))

        self.stdout.write(self.style.SUCCESS('🎉 База данных заполнена!'))
