from django.contrib import admin
from django.db.models import Count, Max, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from pypdf import PdfWriter

from .models import Donation, FestivalInfo, GalleryItem, ScheduleItem
from .receipts import generate_donation_receipt_pdf


@admin.register(FestivalInfo)
class FestivalInfoAdmin(admin.ModelAdmin):
    list_display = ("festival_name", "festival_date_text")
    fieldsets = (
        ("Festival details", {
            "fields": ("festival_name", "festival_date_text", "announcement"),
        }),
        ("Schedule", {
            "fields": ("morning_program", "afternoon_program", "evening_program"),
        }),
        ("Receipt letterhead", {
            "fields": ("temple_address", "contact_phone", "contact_email", "pan_number"),
            "description": "Shown at the top of every donation receipt/bill.",
        }),
    )

    def has_add_permission(self, request):
        # Singleton: only one row should ever exist.
        return not FestivalInfo.objects.exists()


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "order", "is_published")
    list_editable = ("order", "is_published")
    list_filter = ("media_type", "is_published")


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ("time_slot", "description", "order")
    list_editable = ("order",)
    list_filter = ("time_slot",)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    change_list_template = "admin/festival/donation/change_list.html"

    list_display = (
        "name",
        "mobile",
        "amount_display",
        "created_at",
        "is_demo",
        "receipt_link",
    )
    list_filter = ("is_demo", "created_at")
    search_fields = ("name", "mobile", "address")
    readonly_fields = ("created_at", "receipt_id", "receipt_number", "receipt_link")
    date_hierarchy = "created_at"
    actions = ["download_receipts_pdf"]

    fieldsets = (
        ("Donor details", {
            "fields": ("name", "mobile", "address"),
        }),
        ("Donation", {
            "fields": ("amount", "is_demo", "created_at"),
        }),
        ("Receipt", {
            "fields": ("receipt_number", "receipt_link"),
        }),
    )

    @admin.display(description="Amount", ordering="amount")
    def amount_display(self, obj):
        return f"\u20b9{obj.amount:,.2f}"

    @admin.display(description="Receipt")
    def receipt_link(self, obj):
        if not obj.pk:
            return "-"
        url = reverse("festival:donation_receipt", args=[str(obj.receipt_id)])
        return format_html('<a href="{}" target="_blank">View / Download</a>', url)

    @admin.action(description="Download bill (PDF) for selected donations")
    def download_receipts_pdf(self, request, queryset):
        info = FestivalInfo.load()
        writer = PdfWriter()

        for donation in queryset.order_by("created_at"):
            buffer = generate_donation_receipt_pdf(donation, info)
            writer.append(buffer)

        output = HttpResponse(content_type="application/pdf")
        output["Content-Disposition"] = 'attachment; filename="donation-receipts.pdf"'
        writer.write(output)
        writer.close()
        return output

    # ---- Custom "Donors summary" page, linked from the change list ----

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "donors-summary/",
                self.admin_site.admin_view(self.donors_summary_view),
                name="festival_donation_donors_summary",
            ),
        ]
        return custom_urls + urls

    def donors_summary_view(self, request):
        donors = (
            Donation.objects.values("name", "mobile")
            .annotate(
                total_donated=Sum("amount"),
                donation_count=Count("id"),
                last_donation=Max("created_at"),
            )
            .order_by("-total_donated")
        )

        context = {
            **self.admin_site.each_context(request),
            "title": "Donors summary",
            "donors": donors,
            "opts": self.model._meta,
        }
        return render(request, "admin/festival/donors_summary.html", context)
