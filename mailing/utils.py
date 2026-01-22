from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import Attempt, Mailing


def send_mailing(mailing_id):
    mailing = get_object_or_404(Mailing, id=mailing_id)
    mailing.update_status()  # актуализируем статус

    if mailing.status != "Запущена":
        return {
            "success": False,
            "error": "Рассылка не активна (не в периоде отправки).",
        }

    success_count = 0
    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            Attempt.objects.create(
                mailing=mailing, status="Успешно", server_response=None
            )
            success_count += 1
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing, status="Не успешно", server_response=str(e)
            )

    return {"success": True, "sent": success_count, "total": mailing.recipients.count()}
