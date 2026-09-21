from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("festival.urls")),
]

if settings.DEBUG:
    # django.contrib.staticfiles already auto-serves STATIC_URL when
    # DEBUG=True and `runserver` is used, so only MEDIA needs wiring here.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # This project has no external media host (S3/Cloudinary) configured,
    # so gallery photos/videos still need Django to serve them in
    # production too. Fine at this site's scale; swap for a real media
    # host + storage backend if traffic grows.
    urlpatterns += [
        path(
            "media/<path:path>",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

