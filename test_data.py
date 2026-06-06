import os
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SurveyProject.settings')
django.setup()

from surveys.models import Survey, Question, AnswerOption, Poll, PollOption

def create_test_data():
    print("Начинаю расширенную генерацию тестовых данных...")
    
    # Очистка старых данных (опционально, раскомментируй если хочешь удалять старые при запуске)
    # Survey.objects.all().delete()
    # Poll.objects.all().delete()

    # ==========================
    # 1. ОПРОСЫ (Surveys)
    # ==========================
    
    # --- Опрос 1: IT Отдел ---
    survey1 = Survey.objects.create(
        title="Исследование удовлетворенности IT-отдела",
        description="Пожалуйста, ответьте на несколько вопросов о вашей работе. Это поможет нам стать лучше.",
        is_active=True
    )
    print(f"✅ Создан опрос: {survey1.title}")

    q1_1 = Question.objects.create(survey=survey1, text="Как вы оцениваете условия работы в офисе?", question_type="single", order=1)
    AnswerOption.objects.create(question=q1_1, text="Полностью устраивают", order=1)
    AnswerOption.objects.create(question=q1_1, text="В основном устраивают, но есть недочеты", order=2)
    AnswerOption.objects.create(question=q1_1, text="Не устраивают", order=3)

    q1_2 = Question.objects.create(survey=survey1, text="Какие рабочие инструменты вы используете чаще всего?", question_type="multiple", order=2)
    for i, tool in enumerate(["Slack", "Jira", "Figma", "GitLab", "Notion", "Trello"], 1):
        AnswerOption.objects.create(question=q1_2, text=tool, order=i)

    Question.objects.create(survey=survey1, text="Ваши предложения по улучшению процессов?", question_type="text", order=3)

    # --- Опрос 2: Продуктовый дизайн ---
    survey2 = Survey.objects.create(
        title="Оценка нового дизайна приложения",
        description="Мы недавно выкатили новый интерфейс. Поделитесь своим мнением!",
        is_active=True
    )
    print(f"✅ Создан опрос: {survey2.title}")

    q2_1 = Question.objects.create(survey=survey2, text="Стало ли удобнее пользоваться меню?", question_type="single", order=1)
    AnswerOption.objects.create(question=q2_1, text="Да, намного удобнее", order=1)
    AnswerOption.objects.create(question=q2_1, text="Осталось так же", order=2)
    AnswerOption.objects.create(question=q2_1, text="Стало хуже и непонятнее", order=3)

    q2_2 = Question.objects.create(survey=survey2, text="Какие новые фичи вы заметили?", question_type="multiple", order=2)
    for i, feat in enumerate(["Темная тема", "Быстрый поиск", "Новые иконки", "Анимации переходов"], 1):
        AnswerOption.objects.create(question=q2_2, text=feat, order=i)

    Question.objects.create(survey=survey2, text="Чего вам не хватает в новом дизайне?", question_type="text", order=3)

    # --- Опрос 3: Клиентский (Неактивный для проверки) ---
    survey3 = Survey.objects.create(
        title="Обратная связь после покупки товара",
        description="Оцените качество обслуживания в нашем магазине.",
        is_active=False
    )
    print(f"✅ Создан опрос: {survey3.title} (Неактивный статус)")

    q3_1 = Question.objects.create(survey=survey3, text="Оцените скорость доставки (1-5)", question_type="single", order=1)
    for i in range(1, 6):
        AnswerOption.objects.create(question=q3_1, text=f"{i} звезд", order=i)

    # ==========================
    # 2. ГОЛОСОВАНИЯ (Polls)
    # ==========================

    # --- Голосование 1 ---
    poll1 = Poll.objects.create(
        title="Выбор темы для следующего хакатона",
        description="Голосуйте за тему, которая вам наиболее интересна для предстоящего корпоративного хакатона.",
        is_active=True
    )
    print(f"✅ Создано голосование: {poll1.title}")

    for i, opt in enumerate(["Искусственный интеллект и ML", "Внутренние инструменты HR", "Автоматизация тестирования", "Улучшение мобайла"], 1):
        PollOption.objects.create(poll=poll1, text=opt, order=i)

    # --- Голосование 2 ---
    poll2 = Poll.objects.create(
        title="Формат корпоратива 2026",
        description="Как будем праздновать день рождения компании?",
        is_active=True
    )
    print(f"✅ Создано голосование: {poll2.title}")

    for i, opt in enumerate(["Выезд на природу с палатками", "Ресторан в центре города", "Квест-комната + бар", "Онлайн вечеринка в Discord"], 1):
        PollOption.objects.create(poll=poll2, text=opt, order=i)

    # --- Голосование 3 (Неактивное) ---
    poll3 = Poll.objects.create(
        title="Лучший язык программирования (Архив)",
        description="Опрос завершен. Спасибо всем за участие.",
        is_active=False
    )
    print(f"✅ Создано голосование: {poll3.title} (Неактивный статус)")

    for i, opt in enumerate(["Python", "JavaScript", "Go", "Rust", "C++"], 1):
        PollOption.objects.create(poll=poll3, text=opt, order=i)

    print("\n🎉 Генерация расширенных тестовых данных успешно завершена! Можно проверять.")

if __name__ == '__main__':
    create_test_data()
