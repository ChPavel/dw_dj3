from django.core.management import BaseCommand
from bot.models import TgUser
from bot.tg.client import TgClient, logger
from bot.tg.schemas import Message
from todolist.goals.models import Goal, GoalCategory


class TgBotStatus:
    """Запоминает и хранит текущее состояния бота и id категории"""

    STOK = 0  # задач нет
    CAT_CHOICE = 1  # выбор категории
    GOAL_CREATE = 2  # создание цели

    def __init__(self, status_b=STOK, category_id=None):
        self.status_b = status_b
        self.category_id = category_id

    def set_status_b(self, status_b):
        """Хранит решаемую ботом задачу"""
        self.status_b = status_b

    def set_category_id(self, category_id):
        """Хранит id категории"""
        self.category_id = category_id


BOT_STATUS = TgBotStatus()


class Command(BaseCommand):
    """Основная логика работы бота"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **options):
        offset = 0

        logger.info('Bot start handling')
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        """Определяет авторизован ли пользователь"""
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if tg_user.user:
            self.handle_authorized_user(tg_user, msg)
        else:
            self.handle_unauthorized_user(tg_user, msg)

    def handle_authorized_user(self, tg_user: TgUser, msg: Message):
        """Обрабатывает запросы авторизованного пользователя"""
        if msg.text == '/goals':
            self.processing_request_goals(tg_user, msg)
        elif msg.text == '/create':
            self.processing_goal_creation(tg_user, msg)
        elif msg.text == '/cancel':
            self.cancellation_processing(msg)
        elif BOT_STATUS.status_b == TgBotStatus.CAT_CHOICE:
            self.checking_selected_category(msg)
        elif BOT_STATUS.status_b == TgBotStatus.GOAL_CREATE:
            self.create_goal(msg, tg_user)
        else:
            self.tg_client.send_message(chat_id=msg.chat.id, text=f'Unknown command {msg.text}')

    def handle_unauthorized_user(self, tg_user: TgUser, msg: Message):
        """Высылает верификационный код не авторизованному пользователю"""
        code = tg_user.generate_verification_code()
        tg_user.verification_code = code
        tg_user.save()

        self.tg_client.send_message(chat_id=msg.chat.id, text=f'Hello! Verification code: {code}')

    def processing_request_goals(self, tg_user: TgUser, msg: Message):
        """Выводит список целей пользователя из категорий на досках, где он является участником или владельцем"""
        qs = (
            Goal.objects.select_related('user')
            .filter(user=tg_user.user, category__is_deleted=False)
            .exclude(status=Goal.Status.archived)
        )

        goals = '\n'.join([f'# {goal.title}' for goal in qs])

        self.tg_client.send_message(chat_id=msg.chat.id, text='No goals' if not goals else goals)

    def processing_goal_creation(self, tg_user: TgUser, msg: Message):
        """Выводит список категорий пользователя с досок, где он является участником или владельцем и
        предлагает выбрать в которую внести следующую цель, переключая бота в статус выбора категории"""
        qs = GoalCategory.objects.select_related('user').filter(
            board__participants__user=tg_user.user, is_deleted=False
        )

        categories = '\n'.join([f'-> {cat.title}' for cat in qs])

        if not categories:
            self.tg_client.send_message(chat_id=msg.chat.id, text='No categories')
        self.tg_client.send_message(chat_id=msg.chat.id, text=f'Select a category \n{categories}')

        BOT_STATUS.set_status_b(TgBotStatus.CAT_CHOICE)

    def checking_selected_category(self, msg: Message):
        """Поверяет, что пользователь передал валидное значение категории и предлагает добавить новую цель в
        случае успешности проверки, переключая бота в статус создания цели и передавая ему id категории"""
        cat = GoalCategory.objects.filter(title=msg.text)
        if cat:
            self.tg_client.send_message(chat_id=msg.chat.id, text='Enter your new goal')
            BOT_STATUS.set_category_id(category_id=cat[0].id)
            BOT_STATUS.set_status_b(status_b=TgBotStatus.GOAL_CREATE)
        else:
            self.tg_client.send_message(chat_id=msg.chat.id, text=f'Category "{msg.text}" missing from your board')

    def create_goal(self, msg, tg_user):
        """Сохраняет цель в категорию с id, хранящимся у бота, переключая его в статус отсутствия задач"""
        cat = GoalCategory.objects.get(pk=BOT_STATUS.category_id)
        goal = Goal.objects.create(
            title=msg.text,
            category=cat,
            user=tg_user.user,
        )
        self.tg_client.send_message(chat_id=msg.chat.id, text=f'The goal {goal.title} was created successfully')
        BOT_STATUS.set_status_b(TgBotStatus.STOK)

    def cancellation_processing(self, msg: Message):
        """Обрабатывает команды отмены, переключая бота в статус отсутствия задач"""
        BOT_STATUS.set_status_b(TgBotStatus.STOK)
        self.tg_client.send_message(chat_id=msg.chat.id, text='Operation cancel')
