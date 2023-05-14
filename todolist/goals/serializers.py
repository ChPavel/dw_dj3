from datetime import date
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import serializers
from rest_framework.request import Request
from core.models import User
from core.serializers import ProfileSerializer
from todolist.goals.admin import GoalComment
from todolist.goals.models import GoalCategory, Goal, Board, BoardParticipant


class BoardSerializer(serializers.ModelSerializer):
    """Сериализатор создания доски"""

    class Meta:
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'


class BoardParticipantSerializer(serializers.ModelSerializer):
    """Сериалайзер участника доски для сериализатора изменения доски"""

    role = serializers.ChoiceField(required=True, choices=BoardParticipant.editable_roles)
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')

    def validate_user(self, user: User) -> User:
        """Проверка чтобы пользователь не менял свой статус владельца"""
        if self.context['request'].user == user:
            raise ValidationError('Failed to change your role')
        return user


class BoardWithParticipantsSerializer(BoardSerializer):
    """Сериализатор детального отображения, изменения, удаления, доски"""

    participants = BoardParticipantSerializer(many=True)

    def update(self, instance: Board, validated_data: dict) -> Board:
        """Работа с участниками доски (добавления, удаления, изменения участникам уровня доступа)"""
        requests: Request = self.context['request']
        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=requests.user).delete()
            BoardParticipant.objects.bulk_create(
                [
                    BoardParticipant(user=participant['user'], role=participant['role'], board=instance)
                    for participant in validated_data.get('participants', [])
                ],
                ignore_conflicts=True,
            )

            if title := validated_data.get('title'):
                instance.title = title
            instance.save()

        return instance


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания категории"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')
        fields = '__all__'

    def validate_board(self, board: Board) -> Board:
        """Проверка, что доска не удалена и запрос на создание категории на ней от владельца или редактора"""
        if board.is_deleted:
            raise ValidationError('Board is deleted')

        if not BoardParticipant.objects.filter(
            board_id=board.id,
            user_id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ).exists():
            raise PermissionDenied

        return board


class GoalCategorySerializer(GoalCategoryCreateSerializer):
    """Сериализатор для детального отображения, изменения и удаления категории"""

    user = ProfileSerializer(read_only=True)


class GoalCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания цели"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ('id', 'created', 'updated', 'user')
        fields = '__all__'

    def validate_category(self, cat: GoalCategory):
        """Проверка, что категория не удалена и запрос на создание цели в ней от владельца или редактора"""
        if cat.is_deleted:
            raise ValidationError('Category not found')
        if not BoardParticipant.objects.filter(
            board_id=cat.board.id,
            user_id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ).exists():
            raise PermissionDenied
        return cat

    def validate_due_date(self, value: date | None) -> date | None:
        """Проверка на недопустимость создания цели с дедлайном задним числом"""
        if value and value < timezone.now().date():
            raise ValidationError('Failed to set due date ib the past')
        return value


class GoalSerializer(GoalCreateSerializer):
    """Сериализатор для детального отображения, изменения и удаления цели"""

    user = ProfileSerializer(read_only=True)


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'

    def validate_goal(self, goal: Goal):
        """Проверка, что цель не удалена и запрос на создание комментария в ней от владельца или редактора"""
        if goal.status == Goal.Status.archived:
            raise ValidationError('Goal not found')
        if not BoardParticipant.objects.filter(
            board_id=goal.category.board.id,
            user_id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ).exists():
            raise PermissionDenied
        return goal


class GoalCommentSerializer(GoalCommentCreateSerializer):
    """Сериализатор для детального отображения, изменения и удаления комментария"""

    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        read_only_fields = ('id', 'created', 'updated', 'user')
        fields = '__all__'
