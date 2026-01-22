from django.core.management.base import BaseCommand
from mailing.models import Mailing, Attempt
from mailing.utils import send_mailing


class Command(BaseCommand):
    help = 'Отправляет указанную рассылку по ID'

    def add_arguments(self, parser):
        parser.add_argument(
            'mailing_id',
            type=int,
            help='ID рассылки для отправки'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно отправить, игнорируя статус'
        )

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        force = options['force']

        # 1. Получаем рассылку
        try:
            mailing = Mailing.objects.get(id=mailing_id)
        except Mailing.DoesNotExist:
            self.stderr.write(f'Ошибка: рассылка с ID {mailing_id} не найдена.')
            return

        # 2. Проверяем статус (если не --force)
        if not force and mailing.status != 'Запущена':
            self.stderr.write(
                f'Ошибка: статус рассылки — "{mailing.status}". '
                'Используйте --force для отправки.'
            )
            return

        # 3. Начинаем отправку
        self.stdout.write(f'Отправка рассылки #{mailing_id}...')

        result = send_mailing(mailing_id)  # вызов вашей функции

        # 4. Выводим результат
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно: отправлено {result["sent"]} из {result["total"]} писем.'
                )
            )
        else:
            self.stderr.write(f'Ошибка отправки: {result["error"]}')

        # 5. Доп. статистика (если нужно)
        failed_count = Attempt.objects.filter(
            mailing=mailing,
            status='failed'
        ).count()
        if failed_count > 0:
            self.stdout.write(f'Неудачные попытки: {failed_count}')
