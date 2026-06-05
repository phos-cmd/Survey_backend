from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Survey, Question, AnswerOption, UserResponse, UserAnswer,
    Poll, PollOption, Vote
)


# ---- AUTH ----

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, label="Подтвердите пароль")

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


# ---- SURVEYS ----

class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ('id', 'text', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'order', 'options')


class SurveyListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'created_at', 'is_active', 'question_count')

    def get_question_count(self, obj):
        return obj.questions.count()


class SurveyDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'created_at', 'is_active', 'questions')


class UserAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
    text_answer = serializers.CharField(required=False, default='', allow_blank=True)


class UserResponseSerializer(serializers.Serializer):
    answers = UserAnswerSerializer(many=True)


# ---- POLLS ----

class PollOptionSerializer(serializers.ModelSerializer):
    vote_count = serializers.IntegerField(read_only=True)
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = PollOption
        fields = ('id', 'text', 'order', 'vote_count', 'percentage')

    def get_percentage(self, obj):
        total = self.context.get('total_votes', 0)
        if total == 0:
            return 0
        return round((obj.vote_count / total) * 100, 1)


class PollListSerializer(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ('id', 'title', 'description', 'created_at', 'is_active', 'ends_at', 'total_votes')

    def get_total_votes(self, obj):
        return Vote.objects.filter(poll=obj).count()


class PollDetailSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    user_voted = serializers.SerializerMethodField()
    user_vote_option_id = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ('id', 'title', 'description', 'created_at', 'is_active', 'ends_at',
                  'options', 'total_votes', 'user_voted', 'user_vote_option_id')

    def get_total_votes(self, obj):
        return Vote.objects.filter(poll=obj).count()

    def get_options(self, obj):
        total = self.get_total_votes(obj)
        opts = obj.options.all()
        return PollOptionSerializer(opts, many=True, context={'total_votes': total}).data

    def get_user_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Vote.objects.filter(poll=obj, user=request.user).exists()
        return False

    def get_user_vote_option_id(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = Vote.objects.filter(poll=obj, user=request.user).first()
            return vote.option_id if vote else None
        return None


class VoteSerializer(serializers.Serializer):
    option_id = serializers.IntegerField()
