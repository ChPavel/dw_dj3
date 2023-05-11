from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from todolist.goals.models import Goal


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **options):
        offset = 0

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
            qs = (
                Goal.objects.select_related('user')
                .filter(user=tg_user.user, category__is_deleted=False)
                .exclude(status=Goal.Status.archived)
            )

            goals = [f'{goal.id}) {goal.title}' for goal in qs]

            self.tg_client.send_message(chat_id=msg.chat.id, text='No goals' if not goals else '\n'.join(goals))

    def handle_unauthorized_user(self, tg_user: TgUser, msg: Message):
        code = tg_user.generate_verification_code()
        tg_user.verification_code = code
        tg_user.save()

        self.tg_client.send_message(chat_id=msg.chat.id, text=f'Hello! Verification code: {code}')
