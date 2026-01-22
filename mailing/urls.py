from django.urls import path
from . import views

app_name = "mailing"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("recipients/", views.recipient_list, name="recipient_list"),
    path("recipients/create/", views.recipient_create, name="recipient_create"),
    path(
        "recipients/<int:pk>/update/", views.recipient_update, name="recipient_update"
    ),
    path(
        "recipients/<int:pk>/delete/", views.recipient_delete, name="recipient_delete"
    ),
    path("messages/", views.MessageListView.as_view(), name="message_list"),
    path("messages/create/", views.MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/<int:pk>/update/",
        views.MessageUpdateView.as_view(),
        name="message_update",
    ),
    path(
        "messages/<int:pk>/delete/",
        views.MessageDeleteView.as_view(),
        name="message_delete",
    ),
    path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", views.MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"
    ),
    path(
        "mailings/<int:pk>/update/",
        views.MailingUpdateView.as_view(),
        name="mailing_update",
    ),
    path(
        "mailings/<int:pk>/delete/",
        views.MailingDeleteView.as_view(),
        name="mailing_delete",
    ),
    path("mailings/<int:pk>/send/", views.send_mailing_view, name="send_mailing"),
]
