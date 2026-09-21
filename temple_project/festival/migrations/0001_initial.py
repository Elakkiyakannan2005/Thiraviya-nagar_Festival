import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FestivalInfo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("festival_name", models.CharField(default="Thiraviya Nagar Temple Festival", max_length=150)),
                ("festival_date_text", models.CharField(blank=True, max_length=150)),
                ("announcement", models.TextField(blank=True)),
                ("morning_program", models.CharField(blank=True, default="கோவில் பூஜை மற்றும் சிறப்பு வழிபாடுகள்", max_length=255)),
                ("afternoon_program", models.CharField(blank=True, max_length=255)),
                ("evening_program", models.CharField(blank=True, default="கலாச்சார நிகழ்ச்சிகள் மற்றும் கலை நிகழ்வுகள்", max_length=255)),
            ],
            options={
                "verbose_name": "Festival Info",
                "verbose_name_plural": "Festival Info",
            },
        ),
        migrations.CreateModel(
            name="GalleryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                ("caption", models.CharField(blank=True, max_length=200)),
                ("media_type", models.CharField(choices=[("image", "Image"), ("video", "Video")], default="image", max_length=5)),
                ("media_file", models.FileField(upload_to="gallery/")),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="ScheduleItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("time_slot", models.CharField(choices=[("morning", "காலை (Morning)"), ("afternoon", "மதியம் (Afternoon)"), ("evening", "மாலை (Evening)")], max_length=10)),
                ("description", models.CharField(max_length=255)),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Donation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("mobile", models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message="Enter a valid 10-digit mobile number.", regex="^[0-9]{10}$")])),
                ("address", models.TextField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_demo", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
