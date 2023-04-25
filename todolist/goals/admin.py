from django.contrib import admin
from todolist.goals.models import GoalCategory, Goal, GoalComment


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title',)
    list_filter = ('is_deleted',)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'description')
    list_filter = ('status', 'priority')


@admin.register(GoalComment)
class GoalComment(admin.ModelAdmin):
    list_display = ('user', 'goal', 'text', 'created', 'updated')
    search_fields = ('text',)
    list_filter = ('created', 'updated')