import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("festival", "0002_seed_initial_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="festivalinfo",
            name="temple_address",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="festivalinfo",
            name="contact_phone",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="festivalinfo",
            name="contact_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="festivalinfo",
            name="pan_number",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="donation",
            name="receipt_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
