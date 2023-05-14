from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from rest_framework.filters import OrderingFilter, SearchFilter
from todolist.goals.filters import GoalDateFilter
from todolist.goals.models import GoalCategory, Goal, GoalComment, BoardParticipant, Board
from todolist.goals.permissions import GoalCommentPermission, GoalPermission, GoalCategoryPermission, BoardPermission
from todolist.goals.serializers import (
    GoalCategoryCreateSerializer,
    GoalCategorySerializer,
    GoalCreateSerializer,
    GoalSerializer,
    GoalCommentSerializer,
    GoalCommentCreateSerializer,
    BoardSerializer,
    BoardWithParticipantsSerializer,
)


class BoardCreateView(generics.CreateAPIView):
    """Вью создания доски"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer

    def perform_create(self, serializer: BoardSerializer) -> None:
        """Делаем текущего пользователя владельцем доски"""
        BoardParticipant.objects.create(user=self.request.user, board=serializer.save())


class BoardListView(generics.ListAPIView):
    """Вью отображения списка досок"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self) -> QuerySet[Board]:
        """Возвращает все доски кроме удалённых"""
        return Board.objects.filter(participants__user_id=self.request.user.id).exclude(is_deleted=True)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Вью детального отображения, изменения и удаления досок"""

    permission_classes = [BoardPermission]
    serializer_class = BoardWithParticipantsSerializer

    def get_queryset(self) -> QuerySet[Board]:
        """Возвращает все доски пользователя, где он является участником, кроме удалённых"""
        return Board.objects.filter(participants__user_id=self.request.user.id).exclude(is_deleted=True)

    def perform_destroy(self, instance: Board) -> None:
        """Удаление доски с обновлением статуса на удалённый (архивный), в том числе для категорий и целей на ней"""
        with transaction.atomic():
            Board.objects.filter(id=instance.id).update(is_deleted=True)
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)


class GoalCategoryCreateView(generics.CreateAPIView):
    """Вью создания категории"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(generics.ListAPIView):
    """Вью отображения списка категорий"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['board']
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self) -> QuerySet[GoalCategory]:
        """Возвращает все категории пользователя из досок, где он является участником, кроме удалённых"""
        return GoalCategory.objects.filter(board__participants__user=self.request.user).exclude(is_deleted=True)


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """Вью детального отображения, изменения и удаления категории"""

    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermission]

    def get_queryset(self) -> QuerySet[GoalCategory]:
        """Возвращает все категории пользователя из досок, где он является участником, кроме удалённых"""
        return GoalCategory.objects.filter(board__participants__user=self.request.user).exclude(is_deleted=True)

    def perform_destroy(self, instance: GoalCategory) -> None:
        """Обработка удаления категории"""
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted'])
            instance.goals.update(status=Goal.Status.archived)


class GoalCreateView(generics.CreateAPIView):
    """Вью создания цели"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """Вью отображения списка целей"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ('title', 'created')
    ordering = ['title']
    search_fields = ('title', 'description')

    def get_queryset(self) -> QuerySet[Goal]:
        """Возвращает все цели пользователя из категорий, где он является участником, кроме архивных"""
        return Goal.objects.filter(category__board__participants__user=self.request.user).exclude(
            status=Goal.Status.archived
        )


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    """Вью детального отображения, изменения и удаления цели"""

    permission_classes = [GoalPermission]
    serializer_class = GoalSerializer

    def get_queryset(self) -> QuerySet[Goal]:
        """Возвращает все цели пользователя из категорий, где он является участником, кроме архивных"""
        return Goal.objects.filter(category__board__participants__user=self.request.user).exclude(
            status=Goal.Status.archived
        )

    def perform_destroy(self, instance: Goal) -> None:
        """Обработка удаления цели"""
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))


class GoalCommentCreateView(generics.CreateAPIView):
    """Вью создания комментария"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer

    def create(self, request, *args, **kwargs):
        """Обработка создания комментария"""
        return super().create(request, args, kwargs)


class GoalCommentListView(generics.ListAPIView):
    """Вью отображения списка комментариев"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self) -> QuerySet[GoalComment]:
        """Возвращает все комментарии пользователя из цели, где он является участником"""
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user.id)


class GoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    """Вью детального отображения, изменения и удаления комментария"""

    permission_classes = [GoalCommentPermission]
    serializer_class = GoalCommentSerializer
    queryset = GoalComment.objects.select_related('user')
