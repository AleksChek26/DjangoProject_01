from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = (
        'Добавляет пользователей в группу "Менеджеры". '
        'Можно указать несколько username через пробел.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'usernames',
            nargs='+',  # Позволяет передать несколько аргументов
            help='Список username пользователей для добавления в группу'
        )
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Удалить пользователей из группы вместо добавления'
        )

    def handle(self, *args, **options):
        group_name = 'Менеджеры'
        usernames = options['usernames']
        remove = options['--remove']

        # Получаем группу
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise CommandError(f'Группа "{group_name}" не найдена. Создайте её сначала.')

        success_count = 0
        not_found = []
        already_in_group = []
        not_in_group = []

        for username in usernames:
            try:
                user = User.objects.get(username=username)

                if remove:
                    if user in group.user_set.all():
                        group.user_set.remove(user)
                        self.stdout.write(
                            f'Пользователь {username} удалён из группы.'
                        )
                        success_count += 1
                    else:
                        not_in_group.append(username)
                else:
                    if user not in group.user_set.all():
                        group.user_set.add(user)
                        self.stdout.write(
                            f'Пользователь {username} добавлен в группу.'
                        )
                        success_count += 1
                    else:
                        already_in_group.append(username)

            except User.DoesNotExist:
                not_found.append(username)

        # Итоговые сообщения
        if success_count > 0:
            self.stdout.write(self.style.SUCCESS(
                f'Успешно обработано: {success_count} пользователей.'
            ))

        if not_found:
            self.stderr.write(f'Не найдены пользователи: {", ".join(not_found)}')

        if already_in_group and not remove:
            self.stdout.write(f'Уже в группе: {", ".join(already_in_group)}')

        if not_in_group and remove:
            self.stdout.write(f'Не были в группе: {", ".join(not_in_group)}')
