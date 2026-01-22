from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Создаёт группу «Менеджеры» и назначает базовые разрешения'


    def handle(self, *args, **options):
        # Название группы
        group_name = 'Менеджеры'


        # Получаем или создаём группу
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" создана.'))
        else:
            self.stdout.write(f'Группа "{group_name}" уже существует.')


        # Список моделей, для которых назначаем разрешения
        # Замените your_app на реальное имя вашего приложения
        models = [
            'recipient',
            'message',
            'mailing',
        ]

        # Собираем разрешения
        permissions_to_assign = []
        for model_name in models:
            try:
                content_type = ContentType.objects.get(
                    app_label='accounts',
                    model=model_name
                )
                # Добавляем разрешения: add, change, delete
                for perm_codename in ['add', 'change', 'delete']:
                    perm_name = f'{perm_codename}_{model_name}'
                    try:
                        permission = Permission.objects.get(
                            content_type=content_type,
                            codename=perm_name
                )
                        permissions_to_assign.append(permission)
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Разрешение {perm_name} не найдено.'
                            )
                        )
            except ContentType.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Модель {model_name} не найдена в приложении your_app.'
                    )
                )

        # Назначаем разрешения группе
        if permissions_to_assign:
            group.permissions.set(permissions_to_assign)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Назначено {len(permissions_to_assign)} разрешений группе "{group_name}".'
                )
            )
        else:
            self.stdout.write(f'Не найдено разрешений для назначения.')
