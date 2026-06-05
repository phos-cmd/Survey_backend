from collections import Counter
import logging
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)

from .models import (
    Survey, Question, AnswerOption, UserResponse, UserAnswer,
    Poll, PollOption, Vote
)
from .serializers import (
    UserSerializer, RegisterSerializer,
    SurveyListSerializer, SurveyDetailSerializer,
    UserResponseSerializer,
    PollListSerializer, PollDetailSerializer,
    VoteSerializer
)


# ---- AUTH ----

class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Пользователь успешно зарегистрирован.", "username": user.username},
            status=status.HTTP_201_CREATED
        )


class UserMeView(generics.RetrieveAPIView):
    """Профиль текущего авторизованного пользователя."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---- SURVEYS ----

class SurveyViewSet(viewsets.ReadOnlyModelViewSet):
    """Опросы: список и детальный просмотр."""
    queryset = Survey.objects.filter(is_active=True).order_by('-created_at')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurveyDetailSerializer
        return SurveyListSerializer

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def submit(self, request, pk=None):
        """Отправить ответы на опрос и получить топ-3 навыков."""
        survey = self.get_object()
        
        if not survey.is_active:
            return Response(
                {"error": "Этот опрос больше не доступен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Валидация: проверяем, что есть хотя бы один ответ
        answers_data = serializer.validated_data['answers']
        if not answers_data:
            return Response(
                {"error": "Пожалуйста, ответьте хотя бы на один вопрос"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Create response record
                user_response = UserResponse.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    survey=survey,
                    session_key=request.session.session_key or ''
                )

                skill_counter = Counter()

                for answer_data in answers_data:
                    question_id = answer_data['question_id']
                    selected_ids = answer_data.get('selected_option_ids', [])
                    text_answer = answer_data.get('text_answer', '').strip()

                    try:
                        question = Question.objects.get(id=question_id, survey=survey)
                    except Question.DoesNotExist:
                        logger.warning(f"Question {question_id} not found in survey {survey.id}")
                        continue

                    user_answer = UserAnswer.objects.create(
                        response=user_response,
                        question=question,
                        text_answer=text_answer
                    )

                    if selected_ids:
                        options = AnswerOption.objects.filter(id__in=selected_ids, question=question)
                        user_answer.selected_options.set(options)
                        for opt in options:
                            if opt.skill_tag:
                                skill_counter[opt.skill_tag] += 1

        except Exception as e:
            logger.error(f"Error during survey submission: {str(e)}")
            return Response(
                {"error": "Ошибка при обработке ответов"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        top_skills = skill_counter.most_common(3)

        # Format top skills with emoji medals
        medals = ['🥇', '🥈', '🥉']
        result_skills = [
            {"rank": i + 1, "medal": medals[i], "skill": skill, "score": score}
            for i, (skill, score) in enumerate(top_skills)
        ]

        return Response({
            "message": "Ответы записаны!",
            "survey": survey.title,
            "top_skills": result_skills
        }, status=status.HTTP_200_OK)


# ---- POLLS ----

class PollViewSet(viewsets.ReadOnlyModelViewSet):
    """Голосования."""
    queryset = Poll.objects.all().order_by('-created_at')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PollDetailSerializer
        return PollListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        """Проголосовать в голосовании."""
        poll = self.get_object()

        if not poll.is_active:
            return Response({"error": "Голосование завершено."}, status=status.HTTP_400_BAD_REQUEST)

        if poll.ends_at and poll.ends_at < timezone.now():
            return Response({"error": "Время голосования истекло."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        option_id = serializer.validated_data['option_id']

        try:
            with transaction.atomic():
                # Проверяем еще раз внутри транзакции и создаем с блокировкой
                if Vote.objects.filter(poll=poll, user=request.user).exists():
                    return Response({"error": "Вы уже голосовали в этом опросе."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    option = PollOption.objects.get(id=option_id, poll=poll)
                except PollOption.DoesNotExist:
                    return Response({"error": "Вариант не найден."}, status=status.HTTP_404_NOT_FOUND)

                Vote.objects.create(user=request.user, poll=poll, option=option)

        except Exception as e:
            logger.error(f"Ошибка при голосовании: {str(e)}")
            return Response({"error": "Ошибка при обработке голоса."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return updated poll data
        poll_serializer = PollDetailSerializer(poll, context={'request': request})
        return Response({"message": "Голос принят!", "poll": poll_serializer.data})

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def result(self, request, pk=None):
        """Результаты голосования."""
        poll = self.get_object()
        serializer = PollDetailSerializer(poll, context={'request': request})
        return Response(serializer.data)
