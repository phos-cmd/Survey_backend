from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Survey, Question, AnswerOption, UserResponse, UserAnswer, Poll, PollOption, Vote


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 3


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2
    inlines = []


@admin.register(Survey)
class SurveyAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active',)


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'order')
    search_fields = ('text',)
    list_filter = ('question_type',)


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'skill_tag', 'order')
    list_filter = ('question__survey',)


@admin.register(UserResponse)
class UserResponseAdmin(ModelAdmin):
    list_display = ('user', 'survey', 'completed_at')
    search_fields = ('user__username', 'survey__title')


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 3


@admin.register(Poll)
class PollAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'ends_at')
    search_fields = ('title',)
    list_filter = ('is_active',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'option', 'voted_at')
    list_filter = ('poll',)
