from typing import Any
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.request import Request
from todolist.goals.models import Goal, GoalCategory, GoalComment, Board, BoardParticipant


class BoardPermission(IsAuthenticated):
    """Проверка прав доступа к доскe"""

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: Board) -> bool:
        _filters: dict[str, Any] = {'user_id': request.user.id, 'board_id': obj.id}
        if request.method not in SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return BoardParticipant.objects.filter(**_filters).exists()

    # Вариант:
    #     if request.method in SAFE_METHODS:
    #         return BoardParticipant.objects.filter(
    #             user_id=request.user.id, board_id=obj.id
    #         )
    #     else:
    #         return BoardParticipant.objects.filter(
    #             user_id=request.user.id, board_id=obj.id, role=BoardParticipant.Role.owner
    #         )


class GoalCategoryPermission(IsAuthenticated):
    """Проверка прав доступа к категории"""

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: GoalCategory) -> bool:
        _filters: dict[str, Any] = {'user_id': request.user.id, 'board_id': obj.board_id}
        if request.method not in SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalPermission(IsAuthenticated):
    """Проверка прав доступа к цели"""

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: Goal) -> bool:
        _filters: dict[str, Any] = {'user_id': request.user.id, 'board_id': obj.category.board_id}
        if request.method not in SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCommentPermission(IsAuthenticated):
    """Проверка прав доступа к коментарию"""

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: GoalComment) -> bool:
        _filters: dict[str, Any] = {'user_id': request.user.id, 'board_id': obj.goal.category.board_id}
        if request.method not in SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()
