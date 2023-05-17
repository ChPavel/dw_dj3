from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from core.models import User


@admin.register(User)
class CustomUserAdmin(
    UserAdmin
):  # CustomUserAdmin(UserAdmin) можно так PersonalAdmin(admin.ModelAdmin) но пароль в админке не поменять
    # наследование от UserAdmin, а не от admin.ModelAdmi позволяет не писать list_filter и search_fields
    """Класс настройки админпанели."""

    # exclude = ('password',) # У пользователя скрыт пароль.
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
    ]  # Отображение полей во вкладке Users.
    # list_filter = ['is_staff', 'is_active', 'is_superuser'] # Виджет с фильтрами по указанным полям.
    # search_fields = ('username', 'email', 'first_name', 'last_name')  # Поиск по указанным полям.
    readonly_fields = (
        'last_login',
        'date_joined',
    )  # Статичные поля, их нельзя поменять в админке.
    fieldsets = (  # можно настраивать так по разделам и конкретным полям
        (None, {'fields': ('password', 'username')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Разрешения', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.unregister(Group)  # убираем из админки закладку Группы
