from django.db import models

from core.models import User


class BaseModel(models.Model):
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата последнего обновления', auto_now=True)

    class Meta:
        abstract = True


class GoalCategory(BaseModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    title = models.CharField(verbose_name='Название', max_length=255)
    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)

    def __str__(self) -> str:
        return self.title


class Goal(BaseModel):
    class Status(models.IntegerChoices):
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В процессе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
        low = 1, 'Низкий'
        medium = 2, 'Средний'
        hight = 3, 'Высокий'
        critical = 4, 'Критичный'

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(GoalCategory, on_delete=models.PROTECT, related_name='goals')
    due_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='goals')
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(choices=Priority.choices, default=Priority.medium)

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    def __str__(self):
        return self.title
