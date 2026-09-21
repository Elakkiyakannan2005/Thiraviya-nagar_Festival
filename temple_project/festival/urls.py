from django.urls import path

from . import views

app_name = "festival"

urlpatterns = [
    path("", views.index, name="index"),
    path("donate/", views.donate, name="donate"),
    path("donation/<uuid:receipt_id>/receipt/", views.donation_receipt, name="donation_receipt"),
]
