from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Recipient, Message, Mailing
from .forms import RecipientForm, MessageForm, MailingForm
from .utils import send_mailing


# === ПОЛУЧАТЕЛИ ===


@login_required
def recipient_list(request):
    recipients = Recipient.objects.all()
    return render(request, "mailing/recipient_list.html", {"recipients": recipients})


@login_required
def recipient_create(request):
    if request.method == "POST":
        form = RecipientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Получатель добавлен.")
            return redirect("mailing:recipient_list")
    else:
        form = RecipientForm()
    return render(request, "mailing/recipient_form.html", {"form": form})


@login_required
def recipient_update(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == "POST":
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные получателя обновлены.")
            return redirect("mailing:recipient_list")
    else:
        form = RecipientForm(instance=recipient)
    return render(request, "mailing/recipient_form.html", {"form": form})


@login_required
def recipient_delete(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    recipient.delete()
    messages.success(request, "Получатель удалён.")
    return redirect("mailing:recipient_list")


# === СООБЩЕНИЯ ===


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = cache.get("product_queryset")
        if not queryset:
            queryset = super().get_queryset()
            cache.set(
                "product_queryset", queryset, 60 * 15
            )  # Кешируем данные на 15 минут
        return queryset


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"

    def get_success_url(self):
        return reverse("mailing:message_list")

    def form_valid(self, form):
        messages.success(self.request, "Сообщение создано.")
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"

    def get_success_url(self):
        return reverse("mailing:message_list")

    def form_valid(self, form):
        messages.success(self.request, "Сообщение обновлено.")
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"

    def get_success_url(self):
        return reverse("mailing:message_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Сообщение удалено.")
        return super().delete(request, *args, **kwargs)


# === РАССЫЛКИ ===


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return Mailing.objects.filter(user=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Рассылка создана.")
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("mailing:mailing_list")

    def form_valid(self, form):
        # Запрет редактирования запущенных рассылок
        if form.instance.status == "Запущена":
            messages.error(self.request, "Нельзя редактировать запущенную рассылку.")
            return self.form_invalid(form)
        messages.success(self.request, "Рассылка обновлена.")
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"

    def get_success_url(self):
        return reverse("mailing:mailing_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Рассылка удалена.")
        return super().delete(request, *args, **kwargs)

@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    permission_required = "mailing.view_mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Автоматическое обновление статуса
        obj.update_status()
        return obj

    def has_permission(self):
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_superuser


# === ОТПРАВКА ПИСЕМ ===


@login_required
def send_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, user=request.user)

    # Проверка статуса: только 'Запущена' можно отправлять
    if mailing.status != "Запущена":
        messages.error(request, f"Рассылка не активна (статус: {mailing.status}).")
        return redirect("mailing:mailing_detail", pk=pk)

    result = send_mailing(pk)

    if result["success"]:
        messages.success(
            request, f'Отправлено {result["sent"]} из {result["total"]} писем.'
        )
    else:
        messages.error(request, result["error"])

    return redirect("mailing:mailing_detail", pk=pk)


# === ГЛАВНАЯ СТРАНИЦА ===


@login_required
def dashboard(request):
    user = request.user
    total_mailings = Mailing.objects.filter(user=user).count()

    active_mailings = Mailing.objects.filter(
        user=user,
        status="Запущена"
    ).count()

    total_recipients = Recipient.objects.filter(
        mailings__user=user
    ).distinct().count()

    latest_mailings = Mailing.objects.filter(
        user=user
    ).select_related('message').order_by('-created_at')[:10]

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "total_recipients": total_recipients,
        "latest_mailings": latest_mailings,  # передаём в шаблон
    }

    return render(request, "mailing/dashboard.html", context)
