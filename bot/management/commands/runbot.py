from django.core.management import BaseCommand
from bot.models import TgUser
from bot.tg.client import TgClient, logger
from bot.tg.schemas import Message
from todolist.goals.models import Goal, GoalCategory


class TgBotStatus:
    """Запоминает и хранит текущее состояния бота"""

    STOK = 0  # задач нет
    CAT_CHOICE = 1  # выбор категории
    GOAL_CREATE = 2  # создание цели

    def __init__(self, status_b=STOK, category_id=None):
        self.status_b = status_b
        self.category_id = category_id

    def set_status_b(self, status_b):
        self.status_b = status_b

    def set_category_id(self, category_id):
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
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if tg_user.user:
            self.handle_authorized_user(tg_user, msg)
        else:
            self.handle_unauthorized_user(tg_user, msg)

    def handle_authorized_user(self, tg_user: TgUser, msg: Message):
        if msg.text == '/goals':
            self.processing_request_goals(tg_user, msg)
        elif msg.text == '/create':
            self.processing_goal_creation(tg_user, msg)
        elif msg.text == '/':
            ...
        elif msg.text == '/':
            ...
        elif msg.text == '/':
            ...

    def handle_unauthorized_user(self, tg_user: TgUser, msg: Message):
        code = tg_user.generate_verification_code()
        tg_user.verification_code = code
        tg_user.save()

        self.tg_client.send_message(chat_id=msg.chat.id, text=f'Hello! Verification code: {code}')

    def processing_request_goals(self, tg_user: TgUser, msg: Message):
        qs = (
            Goal.objects.select_related('user')
            .filter(user=tg_user.user, category__is_deleted=False)
            .exclude(status=Goal.Status.archived)
        )

        goals = [f'{goal.id}) {goal.title}' for goal in qs]

        self.tg_client.send_message(chat_id=msg.chat.id, text='No goals' if not goals else '\n'.join(goals))

    def processing_goal_creation(self, tg_user: TgUser, msg: Message):
        qs = GoalCategory.objects.select_related('user').filter(
            board__participants__user=tg_user.user, user__goalcategory__is_deleted=False
        )

        categories = [f'{cat.id}) {cat.title}' for cat in qs]

        if not categories:
            self.tg_client.send_message(chat_id=msg.chat.id, text='No categories')
        self.tg_client.send_message(chat_id=msg.chat.id, text='Select a category' '\n'.join(categories))
