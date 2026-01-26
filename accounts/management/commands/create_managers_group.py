from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class Command(BaseCommand):
    help = 'Создаёт или обновляет группу "Менеджеры" с разрешениями на управление моделями рассылки'


    def add_arguments(self, parser):
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Удалить разрешения из группы вместо добавления'
        )
        parser.add_argument(
            '--app-label',
            type=str,
            default='mailing',
            help='Имя приложения (app_label) для поиска моделей'
        )

    def handle(self, *args, **options):
        group_name = 'Менеджеры'
        app_label = options['app_label']
        remove_mode = options['--remove']


        # Получаем или создаём группу
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" создана.'))
        else:
            self.stdout.write(f'Группа "{group_name}" найдена.')


        # Модели, для которых назначаем разрешения
        models = ['recipient', 'message', 'mailing']
        assigned_permissions = []

        for model_name in models:
            try:
                # Получаем ContentType для модели
                content_type = ContentType.objects.get(
                    app_label=app_label,
                    model=model_name
                )
                # Собираем разрешения: add, change, delete, view
                for action in ['add', 'change', 'delete', 'view']:
                    codename = f'{action}_{model_name}'
                    try:
                        permission = Permission.objects.get(
                            content_type=content_type,
                            codename=codename
                        )
                        assigned_permissions.append(permission)
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Разрешение {codename} не найдено для {app_label}.{model_name}.'
                            )
                        )
            except ContentType.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'Модель {model_name} не найдена в приложении {app_label}.'
                    )
                )

        # Применяем изменения
        if remove_mode:
            # Удаляем разрешения из группы
            group.permissions.remove(*assigned_permissions)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Разрешения удалены из группы "{group_name}".'
                )
            )
        else:
            # Добавляем разрешения в группу
            group.permissions.add(*assigned_permissions)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Разрешения назначены группе "{group_name}".'
                )
            )

        # Выводим итоговый список разрешений группы
        self.stdout.write('Текущие разрешения группы:')
        for perm in group.permissions.all():
            self.stdout.write(f'  {perm.codename}')
