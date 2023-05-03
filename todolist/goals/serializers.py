from datetime import date

from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import serializers

from core.serializers import ProfileSerializer
from todolist.goals.admin import GoalComment
from todolist.goals.models import GoalCategory, Goal


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')
        fields = '__all__'


class GoalCategorySerializer(GoalCategoryCreateSerializer):
    user = ProfileSerializer(read_only=True)


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ('id', 'created', 'updated', 'user')
        fields = '__all__'

    def validate_category(self, value: GoalCategory):
        if value.is_deleted:
            raise ValidationError('Category not found')
        if self.context['request'].user.id != value.user_id:
            raise PermissionDenied
        return value

    def validate_due_date(self, value: date | None) -> date:
        if value and value < timezone.now().date():
            raise ValidationError('Failed to set due date ib the past')
        return value


class GoalSerializer(GoalCreateSerializer):
    user = ProfileSerializer(read_only=True)


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'

    def validate_goal(self, value: Goal):
        if value.status == Goal.Status.archived:
            raise ValidationError('Goal not found')
        return value


class GoalCommentSerializer(GoalCommentCreateSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        read_only_fields = ('id', 'created', 'updated', 'user')
        fields = '__all__'
