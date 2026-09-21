import json

from django.db.models import Sum, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import DonationForm
from .models import FestivalInfo, GalleryItem, ScheduleItem


def index(request):
    """Render the temple festival landing page with all dynamic content."""

    info = FestivalInfo.load()

    schedule_items = ScheduleItem.objects.all()
    schedule_by_slot = {
        "morning": [s for s in schedule_items if s.time_slot == ScheduleItem.MORNING],
        "afternoon": [s for s in schedule_items if s.time_slot == ScheduleItem.AFTERNOON],
        "evening": [s for s in schedule_items if s.time_slot == ScheduleItem.EVENING],
    }

    gallery_items = GalleryItem.objects.filter(is_published=True)

    donation_totals = _donation_totals()

    context = {
        "info": info,
        "schedule_by_slot": schedule_by_slot,
        "gallery_items": gallery_items,
        "donation_form": DonationForm(),
        "total_raised": donation_totals["total"],
        "donor_count": donation_totals["count"],
    }
    return render(request, "festival/index.html", context)


def _donation_totals():
    from .models import Donation

    agg = Donation.objects.aggregate(total=Sum("amount"), count=Count("id"))
    return {
        "total": agg["total"] or 0,
        "count": agg["count"] or 0,
    }


@require_POST
def donate(request):
    """
    Handle the donation form submitted via fetch() as JSON or as a normal
    form POST (progressive enhancement -- works with JS on or off).
    """

    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({"ok": False, "message": "Invalid request."}, status=400)
        form = DonationForm(payload)
    else:
        form = DonationForm(request.POST)

    if form.is_valid():
        donation = form.save()
        totals = _donation_totals()
        message = (
            f"Thank you, {donation.name}! Your donation of \u20b9{donation.amount:,.0f} "
            "is recorded in this demo."
        )
        return JsonResponse(
            {
                "ok": True,
                "message": message,
                "total_raised": float(totals["total"]),
                "donor_count": totals["count"],
                "receipt_url": reverse(
                    "festival:donation_receipt", args=[str(donation.receipt_id)]
                ),
                "receipt_number": donation.receipt_number,
            }
        )

    # Flatten form errors into one readable message for the demo UI.
    first_error = next(iter(form.errors.values()))[0]
    return JsonResponse({"ok": False, "message": first_error}, status=400)


def donation_receipt(request, receipt_id):
    """Serve a single donation's bill/receipt as a downloadable PDF."""

    from .models import Donation
    from .receipts import generate_donation_receipt_pdf

    donation = get_object_or_404(Donation, receipt_id=receipt_id)
    info = FestivalInfo.load()

    pdf_buffer = generate_donation_receipt_pdf(donation, info)

    response = HttpResponse(pdf_buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="receipt-{donation.receipt_number}.pdf"'
    )
    return response
