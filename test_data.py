import os
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SurveyProject.settings')
django.setup()

from surveys.models import Survey, Question, AnswerOption, Poll, PollOption

def create_test_data():
    print("Начинаю генерацию тестовых данных...")
    
    # Очистка старых данных (опционально, раскомментируй если хочешь удалять старые при запуске)
    # Survey.objects.all().delete()
    # Poll.objects.all().delete()

    # ==========================
    # 1. СОЗДАНИЕ ОПРОСА
    # ==========================
    survey = Survey.objects.create(
        title="Исследование удовлетворенности IT-отдела",
        description="Пожалуйста, ответьте на несколько вопросов о вашей работе. Это поможет нам стать лучше.",
        is_active=True
    )
    print(f"✅ Создан опрос: {survey.title}")

    # Вопрос 1: Один вариант ответа (Radio)
    q1 = Question.objects.create(
        survey=survey,
        text="Как вы оцениваете условия работы в офисе?",
        question_type="single",
        order=1
    )
    AnswerOption.objects.create(question=q1, text="Полностью устраивают", order=1)
    AnswerOption.objects.create(question=q1, text="В основном устраивают, но есть мелкие недочеты", order=2)
    AnswerOption.objects.create(question=q1, text="Не устраивают", order=3)

    # Вопрос 2: Несколько вариантов ответа (Checkbox)
    q2 = Question.objects.create(
        survey=survey,
        text="Какие рабочие инструменты вы используете чаще всего?",
        question_type="multiple",
        order=2
    )
    AnswerOption.objects.create(question=q2, text="Slack", order=1)
    AnswerOption.objects.create(question=q2, text="Jira", order=2)
    AnswerOption.objects.create(question=q2, text="Figma", order=3)
    AnswerOption.objects.create(question=q2, text="GitLab", order=4)
    AnswerOption.objects.create(question=q2, text="Notion", order=5)

    # Вопрос 3: Текстовый ответ
    Question.objects.create(
        survey=survey,
        text="Какие у вас есть предложения по улучшению рабочих процессов?",
        question_type="text",
        order=3
    )

    # ==========================
    # 2. СОЗДАНИЕ ГОЛОСОВАНИЯ
    # ==========================
    poll = Poll.objects.create(
        title="Выбор темы для следующего хакатона",
        description="Голосуйте за тему, которая вам наиболее интересна для предстоящего корпоративного хакатона.",
        is_active=True
    )
    print(f"✅ Создано голосование: {poll.title}")

    PollOption.objects.create(poll=poll, text="Искусственный интеллект и машинное обучение", order=1)
    PollOption.objects.create(poll=poll, text="Внутренние инструменты для HR", order=2)
    PollOption.objects.create(poll=poll, text="Автоматизация тестирования", order=3)
    PollOption.objects.create(poll=poll, text="Улучшение мобильного приложения", order=4)

    print("\n🎉 Тестовые данные успешно созданы! Можешь проверить в админке или через API.")

if __name__ == '__main__':
    create_test_data()
