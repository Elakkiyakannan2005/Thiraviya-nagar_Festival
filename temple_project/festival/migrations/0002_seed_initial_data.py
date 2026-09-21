import shutil
from pathlib import Path

from django.conf import settings
from django.db import migrations


# Source assets are the ones shipped inside festival/static/festival/media/
# (copied there from the original static site). This migration copies them
# into MEDIA_ROOT/gallery/ once, and creates the matching DB rows, so the
# gallery works out of the box after `migrate` -- no manual admin work
# needed for the demo content. Real content can be edited/replaced anytime
# from /admin/.
ASSET_SOURCE_DIR = Path(__file__).resolve().parent.parent / "static" / "festival" / "media"

GALLERY_SEED = [
    # (source filename, title, caption, media_type, order)
    ("amman.png", "Sri Muppudathi Amman", "Temple sanctum decorated for the festival", "image", 1),
    ("amman_kovil.mp4", "Amman Kovil", "A glimpse inside the temple", "video", 2),
    ("sudalai.png", "Sudalai Madan", "Our guardian deity, adorned with garlands", "image", 3),
    ("pongal.mp4", "Pongal Celebrations", "Community Pongal being prepared", "video", 4),
]

SCHEDULE_SEED = [
    ("morning", "கோவில் பூஜை மற்றும் சிறப்பு வழிபாடுகள்", 1),
    ("afternoon", "அன்னதானம் மற்றும் சமூக உணவு", 2),
    ("evening", "கலாச்சார நிகழ்ச்சிகள் மற்றும் கலை நிகழ்வுகள்", 3),
]


def seed_data(apps, schema_editor):
    FestivalInfo = apps.get_model("festival", "FestivalInfo")
    ScheduleItem = apps.get_model("festival", "ScheduleItem")
    GalleryItem = apps.get_model("festival", "GalleryItem")

    FestivalInfo.objects.get_or_create(
        pk=1,
        defaults={
            "festival_name": "Thiraviya Nagar Temple Festival",
            "festival_date_text": "",
            "announcement": "",
        },
    )

    if not ScheduleItem.objects.exists():
        for time_slot, description, order in SCHEDULE_SEED:
            ScheduleItem.objects.create(time_slot=time_slot, description=description, order=order)

    if not GalleryItem.objects.exists():
        gallery_dir = Path(settings.MEDIA_ROOT) / "gallery"
        gallery_dir.mkdir(parents=True, exist_ok=True)

        for filename, title, caption, media_type, order in GALLERY_SEED:
            source_path = ASSET_SOURCE_DIR / filename
            if not source_path.exists():
                # Asset not bundled (e.g. trimmed deployment) - skip quietly.
                continue

            dest_path = gallery_dir / filename
            if not dest_path.exists():
                shutil.copyfile(source_path, dest_path)

            GalleryItem.objects.create(
                title=title,
                caption=caption,
                media_type=media_type,
                media_file=f"gallery/{filename}",
                order=order,
                is_published=True,
            )


def unseed_data(apps, schema_editor):
    FestivalInfo = apps.get_model("festival", "FestivalInfo")
    ScheduleItem = apps.get_model("festival", "ScheduleItem")
    GalleryItem = apps.get_model("festival", "GalleryItem")

    ScheduleItem.objects.all().delete()
    GalleryItem.objects.all().delete()
    FestivalInfo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("festival", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
