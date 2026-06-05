from django.db import models
from django.contrib.auth.models import User


class Survey(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название опроса")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ('single', 'Один вариант'),
        ('multiple', 'Несколько вариантов'),
        ('text', 'Текстовый ответ'),
    ]
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=1000, verbose_name="Текст вопроса")
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return f"{self.survey.title}: {self.text[:50]}"


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=500, verbose_name="Вариант ответа")
    skill_tag = models.CharField(max_length=100, blank=True, verbose_name="Тег навыка")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

    def __str__(self):
        return self.text


class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Прохождение опроса"
        verbose_name_plural = "Прохождения опросов"

    def __str__(self):
        return f"Response to {self.survey.title}"


class UserAnswer(models.Model):
    response = models.ForeignKey(UserResponse, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(AnswerOption, blank=True)
    text_answer = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"

    def __str__(self):
        return f"Ответ на {self.question.text[:30]} - {self.response.survey.title}"


# ---- POLLS ----

class Poll(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название голосования")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания")

    class Meta:
        verbose_name = "Голосование"
        verbose_name_plural = "Голосования"

    def __str__(self):
        return self.title


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=500, verbose_name="Вариант")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Вариант голосования"
        verbose_name_plural = "Варианты голосования"

    def __str__(self):
        return self.text

    @property
    def vote_count(self):
        return self.votes.count()


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, related_name='votes', on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')
        indexes = [
            models.Index(fields=['poll', 'user']),
            models.Index(fields=['poll']),
        ]
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"

    def __str__(self):
        return f"{self.user} voted in {self.poll.title}"

# Модели для приложения "surveys". Эти классы описывают структуру данных для опросов, вопросов, ответов и голосований.

# Survey: Описывает опрос, включая его название, описание и статус активности.
# Question: Описывает вопрос, связанный с опросом. Может быть нескольких типов (один вариант, несколько вариантов, текст).
# AnswerOption: Варианты ответов для вопросов с выбором.
# UserResponse: Хранит информацию о прохождении опроса пользователем.
# UserAnswer: Хранит ответы пользователя на вопросы.
# Poll: Описывает голосование, включая дату окончания.
# PollOption: Варианты для голосования.
# Vote: Хранит информацию о голосах пользователей.
