from django.core.validators import RegexValidator
from django.db import models
import uuid


class FestivalInfo(models.Model):
    """
    Singleton-style model holding the top-level festival details that
    used to be hardcoded in index.html (date, headline, etc).
    Editable from /admin/ without touching any code.
    """

    festival_name = models.CharField(max_length=150, default="Thiraviya Nagar Temple Festival")
    festival_date_text = models.CharField(
        max_length=150,
        blank=True,
        help_text="Shown as-is, e.g. 'January 14, 2027' or leave blank for "
        "'To be announced soon'.",
    )
    announcement = models.TextField(
        blank=True,
        help_text="Optional extra announcement line shown under the date.",
    )
    morning_program = models.CharField(
        max_length=255,
        blank=True,
        default="கோவில் பூஜை மற்றும் சிறப்பு வழிபாடுகள்",
    )
    afternoon_program = models.CharField(max_length=255, blank=True)
    evening_program = models.CharField(
        max_length=255,
        blank=True,
        default="கலாச்சார நிகழ்ச்சிகள் மற்றும் கலை நிகழ்வுகள்",
    )

    # Shown on the letterhead of donation receipts/bills.
    temple_address = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    pan_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional. Trust PAN, shown on receipts if you want donors to "
        "have it for their records.",
    )

    class Meta:
        verbose_name = "Festival Info"
        verbose_name_plural = "Festival Info"

    def __str__(self):
        return self.festival_name

    def save(self, *args, **kwargs):
        # Keep this a singleton: always overwrite row with pk=1.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class GalleryItem(models.Model):
    IMAGE = "image"
    VIDEO = "video"
    MEDIA_TYPE_CHOICES = [(IMAGE, "Image"), (VIDEO, "Video")]

    title = models.CharField(max_length=150)
    caption = models.CharField(max_length=200, blank=True)
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPE_CHOICES, default=IMAGE)
    media_file = models.FileField(upload_to="gallery/")
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class ScheduleItem(models.Model):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    TIME_CHOICES = [
        (MORNING, "காலை (Morning)"),
        (AFTERNOON, "மதியம் (Afternoon)"),
        (EVENING, "மாலை (Evening)"),
    ]

    time_slot = models.CharField(max_length=10, choices=TIME_CHOICES)
    description = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.get_time_slot_display()} - {self.description[:40]}"


mobile_validator = RegexValidator(
    regex=r"^[0-9]{10}$",
    message="Enter a valid 10-digit mobile number.",
)


class Donation(models.Model):
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=10, validators=[mobile_validator])
    address = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # Used to build the receipt/bill download URL. A UUID (rather than the
    # numeric id) keeps one donor's receipt link from being guessable by
    # incrementing someone else's.
    receipt_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # This project ships without a real payment gateway wired in, so every
    # donation is recorded as a "demo" pledge until a gateway (Razorpay/
    # Stripe/PayU etc.) is connected in views.py -> DonationCreateView.
    is_demo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - \u20b9{self.amount}"

    @property
    def receipt_number(self):
        """Human-friendly receipt number shown on the bill, e.g. TNF-000042."""
        return f"TNF-{self.pk:06d}" if self.pk else "TNF-PENDING"
